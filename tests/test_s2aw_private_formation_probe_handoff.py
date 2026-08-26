from __future__ import annotations

from dataclasses import fields, replace
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
import mcm_field_organism._ppb1_active_batch_formation_probe_handoff as handoff
from mcm_field_organism._ppb1_active_batch_formation_consumer import (
    prepare_ppb1_active_batch_formation_consumer_owner,
)
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


def _contract() -> BrowserWorldContract:
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


def _sequence(
    config,
    *,
    phase: str,
    count: int,
    source_start: int,
    field_start: int,
    field_stride: int,
    values: float,
) -> ReceptorTimeSequence:
    frames = tuple(
        OrganismTimedReceptorFrame(
            ReceptorContactFrame(
                config.modality_id,
                config.geometry_id,
                f"synthetic.{phase}.{config.modality_id}.{index}",
                f"source.{config.modality_id}",
                source_start + index * 10,
                source_start + (index + 1) * 10,
                config.carrier_ids,
                tuple(values for _ in config.carrier_ids),
            ),
            CommonFieldTime(
                "field.synthetic",
                field_start + index * field_stride,
                field_start + index * field_stride + 10,
            ),
        )
        for index in range(count)
    )
    return ReceptorTimeSequence(
        config.modality_id,
        config.geometry_id,
        "field.synthetic",
        frames,
    )


def _envelope(
    contract,
    profile,
    *,
    phase: str,
    count: int,
    source_start: int,
    field_end_before: int,
    values: float,
):
    auditory_field_start = field_end_before
    visual_field_start = field_end_before + 10
    stride = 20 if count > 1 else 10
    auditory = _sequence(
        profile.auditory_config,
        phase=phase,
        count=count,
        source_start=source_start,
        field_start=auditory_field_start,
        field_stride=stride,
        values=values,
    )
    visual = _sequence(
        profile.visual_config,
        phase=phase,
        count=count,
        source_start=source_start,
        field_start=visual_field_start,
        field_stride=stride,
        values=values,
    )
    batch = BrowserReceptorSequenceBatch(
        contract.contract_id,
        contract.digest(),
        (auditory, visual),
    )
    return bind_ppb1_active_receptor_batch(
        f"binding.synthetic.{phase}.v1",
        contract,
        batch,
        profile,
    )


def _fixture(
    *,
    formation_count: int = 3,
    probe_count: int = 1,
    probe_source_start: int | None = None,
    probe_values: float = 0.0,
):
    contract = _contract()
    profile = bind_ppb1_receptor_profile("browser", _parameters())
    formation = _envelope(
        contract,
        profile,
        phase=f"formation.{formation_count}",
        count=formation_count,
        source_start=0,
        field_end_before=0,
        values=0.0,
    )
    auditory = initial_ppb1_bank_state(profile.auditory_config)
    visual = initial_ppb1_bank_state(profile.visual_config)
    owner = prepare_ppb1_active_batch_formation_consumer_owner(
        f"owner.synthetic.{formation_count}",
        f"authorization.synthetic.{formation_count}",
        f"consumption.synthetic.{formation_count}",
        formation.envelope_digest,
        profile.digest(),
        auditory.digest(),
        visual.digest(),
    )
    result = owner.consume_once(formation, profile, auditory, visual)
    formation_field_end = max(
        item.field_window_end_tick
        for stream in (formation.auditory_stream, formation.visual_stream)
        for item in stream.timed_frames
    )
    probe = _envelope(
        contract,
        profile,
        phase=f"probe.{formation_count}.{probe_count}.{probe_values}",
        count=probe_count,
        source_start=(
            formation_count * 10
            if probe_source_start is None
            else probe_source_start
        ),
        field_end_before=formation_field_end,
        values=probe_values,
    )
    return result, formation, profile, probe


def _run(values):
    return handoff.probe_ppb1_active_batch_formation_result_read_only(
        "handoff.synthetic.v1",
        *values,
        "probe.synthetic.auditory",
        "probe.synthetic.visual",
    )


class S2AWPrivateFormationProbeHandoffTests(unittest.TestCase):
    def test_valid_positive_handoff_returns_two_read_only_recognitions(self) -> None:
        values = _fixture()
        before = (
            values[0].auditory_poststate.digest(),
            values[0].visual_poststate.digest(),
        )
        result = _run(values)
        self.assertTrue(result.auditory_finding.recognized)
        self.assertTrue(result.visual_finding.recognized)
        self.assertEqual(
            before,
            (
                result.auditory_postprobe_state_digest,
                result.visual_postprobe_state_digest,
            ),
        )

    def test_valid_negative_handoff_returns_two_nonrecognitions(self) -> None:
        result = _run(_fixture(probe_values=0.5))
        self.assertFalse(result.auditory_finding.recognized)
        self.assertFalse(result.visual_finding.recognized)
        self.assertGreater(result.auditory_finding.match_distance, 0.02)
        self.assertGreater(result.visual_finding.match_distance, 0.01)

    def test_wrong_formation_envelope_or_profile_rejects_before_probe(self) -> None:
        values = _fixture()
        wrong_profile = bind_ppb1_receptor_profile("controlled", _parameters())
        with patch.object(handoff, "probe_s1wu_perceptual_state") as probe:
            with self.assertRaises(
                handoff.PPB1ActiveBatchFormationProbeHandoffError
            ):
                _run((values[0], values[3], values[2], values[3]))
            with self.assertRaises(
                handoff.PPB1ActiveBatchFormationProbeHandoffError
            ):
                _run((values[0], values[1], wrong_profile, values[3]))
        probe.assert_not_called()

    def test_unstabilized_formation_rejects_before_probe(self) -> None:
        values = _fixture(formation_count=2)
        with patch.object(handoff, "probe_s1wu_perceptual_state") as probe:
            with self.assertRaises(
                handoff.PPB1ActiveBatchFormationProbeHandoffError
            ) as caught:
                _run(values)
        self.assertEqual(
            handoff.PPB1_FORMATION_PROBE_HANDOFF_STABILIZATION_REQUIRED,
            caught.exception.code,
        )
        probe.assert_not_called()

    def test_overlapping_or_nonlater_probe_rejects_before_probe(self) -> None:
        values = _fixture(probe_source_start=20)
        with patch.object(handoff, "probe_s1wu_perceptual_state") as probe:
            with self.assertRaises(
                handoff.PPB1ActiveBatchFormationProbeHandoffError
            ) as caught:
                _run(values)
        self.assertEqual(
            handoff.PPB1_FORMATION_PROBE_HANDOFF_PARTITION_MISMATCH,
            caught.exception.code,
        )
        probe.assert_not_called()

    def test_multiframe_probe_stream_rejects_before_probe(self) -> None:
        values = _fixture(probe_count=2)
        with patch.object(handoff, "probe_s1wu_perceptual_state") as probe:
            with self.assertRaises(
                handoff.PPB1ActiveBatchFormationProbeHandoffError
            ):
                _run(values)
        probe.assert_not_called()

    def test_second_probe_failure_returns_no_result_and_preserves_states(self) -> None:
        values = _fixture()
        original = handoff.probe_s1wu_perceptual_state
        calls = 0
        before = (
            values[0].auditory_poststate.digest(),
            values[0].visual_poststate.digest(),
        )

        def fail_second(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("synthetic second-probe failure")
            return original(*args, **kwargs)

        with patch.object(
            handoff,
            "probe_s1wu_perceptual_state",
            side_effect=fail_second,
        ):
            with self.assertRaises(
                handoff.PPB1ActiveBatchFormationProbeHandoffError
            ) as caught:
                _run(values)
        self.assertEqual(
            handoff.PPB1_FORMATION_PROBE_HANDOFF_ATOMIC_RESULT_REQUIRED,
            caught.exception.code,
        )
        self.assertEqual(2, calls)
        self.assertEqual(
            before,
            (
                values[0].auditory_poststate.digest(),
                values[0].visual_poststate.digest(),
            ),
        )

    def test_result_finding_partition_and_source_tampering_fail_closed(self) -> None:
        result = _run(_fixture())
        with self.assertRaises(
            handoff.PPB1ActiveBatchFormationProbeHandoffError
        ):
            replace(result, formation_to_probe_partition_digest="0" * 64)
        with self.assertRaises(Exception):
            replace(result.auditory_finding, recognized=False)
        with self.assertRaises(
            handoff.PPB1ActiveBatchFormationProbeHandoffError
        ):
            replace(result, formation_envelope_digest="0" * 64)

    def test_public_api_snapshot_and_field_boundaries_remain_unchanged(self) -> None:
        private_names = {
            "PPB1ActiveBatchFormationProbeHandoffError",
            "PPB1ActiveBatchFormationProbeResult",
            "probe_ppb1_active_batch_formation_result_read_only",
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
            / "_ppb1_active_batch_formation_probe_handoff.py"
        ).read_text(encoding="ascii")
        for forbidden in (
            "SharedMCMField",
            "current_api",
            "root_lazy_exports",
            "advance_s1wq_perceptual_state",
            "advance_ppb1_bank",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
