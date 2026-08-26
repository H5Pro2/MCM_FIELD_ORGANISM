from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from threading import Event, Thread
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_active_batch_formation_consumer as consumer
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    bind_ppb1_active_receptor_batch,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism._ppb1_reference import initial_ppb1_bank_state
from mcm_field_organism.browser_receptor_bridge import BrowserReceptorSequenceBatch
from mcm_field_organism.browser_world_contract import (
    BrowserWorldContract,
    BrowserWorldPhase,
)
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
)
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


ROOT = Path(__file__).resolve().parents[1]


def _parameters() -> PPB1ProfileParameters:
    return PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )


def _world_contract() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="synthetic.browser.world.v1",
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=100.0,
        phases=(
            BrowserWorldPhase("rest.before", 10, "static", 0.0),
            BrowserWorldPhase("change", 10, "moving", 0.2),
            BrowserWorldPhase("rest.after", 10, "static", 0.0),
        ),
    )


def _sequence(config, field_offset: int) -> ReceptorTimeSequence:
    timed_frames = tuple(
        OrganismTimedReceptorFrame(
            ReceptorContactFrame(
                config.modality_id,
                config.geometry_id,
                f"synthetic.{config.modality_id}.{index}",
                f"source.{config.modality_id}",
                index * 10,
                (index + 1) * 10,
                config.carrier_ids,
                tuple(
                    (index + carrier) / 100.0
                    for carrier in range(len(config.carrier_ids))
                ),
            ),
            CommonFieldTime(
                "field.synthetic",
                field_offset + index * 20,
                field_offset + (index + 1) * 20,
            ),
        )
        for index in range(2)
    )
    return ReceptorTimeSequence(
        config.modality_id,
        config.geometry_id,
        "field.synthetic",
        timed_frames,
    )


def _fixture():
    contract = _world_contract()
    profile = bind_ppb1_receptor_profile("browser", _parameters())
    auditory = _sequence(profile.auditory_config, 0)
    visual = _sequence(profile.visual_config, 10)
    batch = BrowserReceptorSequenceBatch(
        contract.contract_id,
        contract.digest(),
        (auditory, visual),
    )
    envelope = bind_ppb1_active_receptor_batch(
        "binding.synthetic.v1",
        contract,
        batch,
        profile,
    )
    auditory_state = initial_ppb1_bank_state(profile.auditory_config)
    visual_state = initial_ppb1_bank_state(profile.visual_config)
    owner = consumer.prepare_ppb1_active_batch_formation_consumer_owner(
        "owner.synthetic.v1",
        "authorization.synthetic.v1",
        "consumption.synthetic.v1",
        envelope.envelope_digest,
        profile.digest(),
        auditory_state.digest(),
        visual_state.digest(),
    )
    return owner, envelope, profile, auditory_state, visual_state


def _consume(values):
    owner, envelope, profile, auditory, visual = values
    return owner.consume_once(envelope, profile, auditory, visual)


class S2ARPrivateActiveBatchFormationConsumerTests(unittest.TestCase):
    def test_success_consumes_once_and_returns_complete_two_modality_result(
        self,
    ) -> None:
        values = _fixture()
        result = _consume(values)
        snapshot = values[0].snapshot()

        self.assertEqual("CONSUMED", snapshot.status)
        self.assertEqual((1, 1, 1), (
            snapshot.attempt_count,
            snapshot.use_count,
            snapshot.generation,
        ))
        self.assertEqual(
            result.formation_result_digest,
            snapshot.committed_result_digest,
        )
        self.assertEqual(4, len(result.ordered_step_receipts))
        self.assertEqual(2, result.auditory_poststate.accepted_step_count)
        self.assertEqual(2, result.visual_poststate.accepted_step_count)

    def test_wrong_preflight_input_leaves_authorized_owner_unchanged(self) -> None:
        owner, envelope, profile, auditory, visual = _fixture()
        before = owner.snapshot()
        with self.assertRaises(consumer.PPB1ActiveBatchFormationError) as caught:
            owner.consume_once(envelope, profile, visual, auditory)
        self.assertEqual(
            consumer.PPB1_ACTIVE_BATCH_FORMATION_PREFLIGHT_REJECTED,
            caught.exception.code,
        )
        self.assertEqual(before, owner.snapshot())

    def test_corrected_call_after_preflight_rejection_succeeds_once(self) -> None:
        values = _fixture()
        owner, envelope, profile, auditory, visual = values
        with self.assertRaises(consumer.PPB1ActiveBatchFormationError):
            owner.consume_once(envelope, profile, visual, auditory)
        result = _consume(values)
        self.assertEqual("CONSUMED", result.authorization_poststate.status)

    def test_second_call_after_consumed_rejects_before_lifecycle(self) -> None:
        values = _fixture()
        _consume(values)
        with patch.object(
            consumer,
            "advance_s1wq_perceptual_state",
        ) as advance:
            with self.assertRaises(consumer.PPB1ActiveBatchFormationError) as caught:
                _consume(values)
        self.assertEqual(
            consumer.PPB1_ACTIVE_BATCH_FORMATION_OWNER_TERMINAL,
            caught.exception.code,
        )
        advance.assert_not_called()

    def test_attempt_failure_commits_failed_without_result(self) -> None:
        values = _fixture()
        with patch.object(
            consumer,
            "advance_s1wq_perceptual_state",
            side_effect=RuntimeError("synthetic failure"),
        ):
            with self.assertRaises(consumer.PPB1ActiveBatchFormationError) as caught:
                _consume(values)
        snapshot = values[0].snapshot()
        self.assertEqual(
            consumer.PPB1_ACTIVE_BATCH_FORMATION_ATTEMPT_FAILED,
            caught.exception.code,
        )
        self.assertEqual("FAILED", snapshot.status)
        self.assertEqual((1, 0, 1), (
            snapshot.attempt_count,
            snapshot.use_count,
            snapshot.generation,
        ))
        self.assertIsNone(snapshot.committed_result_digest)

    def test_second_call_after_failed_rejects_before_lifecycle(self) -> None:
        values = _fixture()
        with patch.object(
            consumer,
            "advance_s1wq_perceptual_state",
            side_effect=RuntimeError("synthetic failure"),
        ):
            with self.assertRaises(consumer.PPB1ActiveBatchFormationError):
                _consume(values)
        with patch.object(
            consumer,
            "advance_s1wq_perceptual_state",
        ) as advance:
            with self.assertRaises(consumer.PPB1ActiveBatchFormationError) as caught:
                _consume(values)
        self.assertEqual(
            consumer.PPB1_ACTIVE_BATCH_FORMATION_OWNER_TERMINAL,
            caught.exception.code,
        )
        advance.assert_not_called()

    def test_concurrent_second_call_is_busy_without_extra_lifecycle_call(self) -> None:
        values = _fixture()
        entered = Event()
        release = Event()
        original = consumer.advance_s1wq_perceptual_state
        call_count = 0
        first_result: list[object] = []

        def blocking_advance(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                entered.set()
                self.assertTrue(release.wait(timeout=2.0))
            return original(*args, **kwargs)

        def first_call() -> None:
            try:
                first_result.append(_consume(values))
            except Exception as exc:  # pragma: no cover - assertion captures it
                first_result.append(exc)

        with patch.object(
            consumer,
            "advance_s1wq_perceptual_state",
            side_effect=blocking_advance,
        ):
            thread = Thread(target=first_call)
            thread.start()
            self.assertTrue(entered.wait(timeout=2.0))
            with self.assertRaises(consumer.PPB1ActiveBatchFormationError) as caught:
                _consume(values)
            self.assertEqual(1, call_count)
            release.set()
            thread.join(timeout=2.0)

        self.assertFalse(thread.is_alive())
        self.assertEqual(
            consumer.PPB1_ACTIVE_BATCH_FORMATION_OWNER_BUSY,
            caught.exception.code,
        )
        self.assertEqual(1, len(first_result))
        self.assertIsInstance(
            first_result[0],
            consumer.PPB1ActiveBatchFormationResult,
        )

    def test_owner_snapshot_is_frozen_and_contains_no_bank_or_frame_values(
        self,
    ) -> None:
        snapshot = _fixture()[0].snapshot()
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            snapshot.status = "FAILED"  # type: ignore[misc]
        names = {item.name for item in fields(snapshot)}
        self.assertTrue(
            names.isdisjoint({"bank", "slots", "frames", "values", "poststate"})
        )

    def test_public_api_snapshot_and_field_boundaries_remain_unchanged(self) -> None:
        private_names = {
            "PPB1ActiveBatchFormationConsumerOwner",
            "PPB1ActiveBatchFormationOwnerSnapshot",
            "PPB1ActiveBatchFormationStepReceipt",
            "PPB1ActiveBatchFormationResult",
            "prepare_ppb1_active_batch_formation_consumer_owner",
        }
        self.assertTrue(private_names.isdisjoint(mcm_field_organism.__all__))
        self.assertTrue(private_names.isdisjoint(ROOT_LAZY_EXPORTS))
        self.assertTrue(private_names.isdisjoint(current_api.__all__))
        self.assertTrue(
            private_names.isdisjoint(
                {item.name for item in fields(SharedMCMFieldSnapshot)}
            )
        )
        source = (
            ROOT
            / "mcm_field_organism"
            / "_ppb1_active_batch_formation_consumer.py"
        ).read_text(encoding="ascii")
        for forbidden in (
            "SharedMCMField",
            "current_api",
            "root_lazy_exports",
            "probe_s1wu_perceptual_state",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
