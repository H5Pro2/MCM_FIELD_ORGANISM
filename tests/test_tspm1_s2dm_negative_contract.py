from __future__ import annotations

from dataclasses import fields, replace
import unittest
from unittest.mock import patch

import mcm_field_organism._tspm1_private as tspm1
from mcm_field_organism._ppb1_reference import PPB1StepResult
from tests.test_tspm1_s2dh_private_fast_core import (
    advance,
    config_for,
    envelope_for,
    exposures,
    profile,
)


FOREIGN_DIGEST = "f" * 64
MALFORMED_DIGEST = "e" * 64


def unsafe_clone(value, **changes):
    clone = object.__new__(type(value))
    for field in fields(value):
        object.__setattr__(
            clone,
            field.name,
            changes.get(field.name, getattr(value, field.name)),
        )
    return clone


def eligible_fixture():
    bound_profile = profile()
    config = config_for(bound_profile)
    envelope = envelope_for(
        bound_profile,
        ((0.1, 0.1), (0.1, 0.1)),
        suffix="s2dm.eligible",
    )
    source = exposures(config, envelope)
    initial = tspm1.initial_tspm1_composite_state(config)
    _, created = advance(config, initial, source[0], 0)
    return config, source, created.poststate


def owner_for(config, state, exposure, suffix: str):
    return tspm1.TSPM1CoordinatorOwner(
        f"tspm1.owner.s2dm.{suffix}",
        f"tspm1.authorization.s2dm.{suffix}",
        f"tspm1.consumption.s2dm.{suffix}",
        config.config_binding_digest,
        state.composite_state_digest,
        exposure.exposure_digest,
    )


class TSPM1S2DMNegativeContractTests(unittest.TestCase):
    def assert_terminal_failure(
        self,
        owner,
        action,
        retry,
        expected_inner_code: str,
    ) -> None:
        with self.assertRaises(tspm1.TSPM1Error) as caught:
            action()
        self.assertEqual(tspm1.TSPM1_ATTEMPT_FAILED, caught.exception.code)
        snapshot = owner.snapshot()
        self.assertEqual("FAILED", snapshot.status)
        self.assertEqual((1, 0, 1), (
            snapshot.attempt_count,
            snapshot.use_count,
            snapshot.generation,
        ))
        self.assertEqual(expected_inner_code, snapshot.failure_code)
        self.assertIsNone(snapshot.committed_result_digest)
        with self.assertRaises(tspm1.TSPM1Error) as terminal:
            retry()
        self.assertEqual(tspm1.TSPM1_OWNER_TERMINAL, terminal.exception.code)

    def test_p01_wrong_exposure_type_precedes_invalid_composite(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        envelope = envelope_for(bound_profile, ((0.1, 0.1),), suffix="s2dm.p01")
        exposure = exposures(config, envelope)[0]
        state = tspm1.initial_tspm1_composite_state(config)
        malformed = unsafe_clone(state, composite_state_digest=MALFORMED_DIGEST)
        owner = tspm1.TSPM1CoordinatorOwner(
            "tspm1.owner.s2dm.p01",
            "tspm1.authorization.s2dm.p01",
            "tspm1.consumption.s2dm.p01",
            config.config_binding_digest,
            malformed.composite_state_digest,
            exposure.exposure_digest,
        )
        invalid_exposure = object()

        self.assert_terminal_failure(
            owner,
            lambda: owner.consume_once(config, malformed, invalid_exposure),
            lambda: owner.consume_once(config, malformed, invalid_exposure),
            tspm1.TSPM1_INVALID_TYPE_OR_SCHEMA,
        )

    def test_p02_owner_authorization_precedes_invalid_composite(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        envelope = envelope_for(bound_profile, ((0.1, 0.1),), suffix="s2dm.p02")
        exposure = exposures(config, envelope)[0]
        state = tspm1.initial_tspm1_composite_state(config)
        malformed = unsafe_clone(state, composite_state_digest=MALFORMED_DIGEST)
        owner = tspm1.TSPM1CoordinatorOwner(
            "tspm1.owner.s2dm.p02",
            "tspm1.authorization.s2dm.p02",
            "tspm1.consumption.s2dm.p02",
            config.config_binding_digest,
            FOREIGN_DIGEST,
            exposure.exposure_digest,
        )

        self.assert_terminal_failure(
            owner,
            lambda: owner.consume_once(config, malformed, exposure),
            lambda: owner.consume_once(config, malformed, exposure),
            tspm1.TSPM1_OWNER_AUTHORIZATION_MISMATCH,
        )

    def test_p03_owner_authorization_precedes_source_provenance(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        first = envelope_for(bound_profile, ((0.1, 0.1),), suffix="s2dm.p03.a")
        second = envelope_for(
            bound_profile,
            ((0.2, 0.2),),
            start_index=1,
            suffix="s2dm.p03.b",
        )
        exposure = exposures(config, first)[0]
        malformed = unsafe_clone(
            exposure,
            auditory=second.auditory_stream.timed_frames[0],
        )
        state = tspm1.initial_tspm1_composite_state(config)
        owner = tspm1.TSPM1CoordinatorOwner(
            "tspm1.owner.s2dm.p03",
            "tspm1.authorization.s2dm.p03",
            "tspm1.consumption.s2dm.p03",
            config.config_binding_digest,
            state.composite_state_digest,
            FOREIGN_DIGEST,
        )

        self.assert_terminal_failure(
            owner,
            lambda: owner.consume_once(config, state, malformed),
            lambda: owner.consume_once(config, state, malformed),
            tspm1.TSPM1_OWNER_AUTHORIZATION_MISMATCH,
        )

    def test_p04_wrong_probe_type_precedes_invalid_composite(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        state = tspm1.initial_tspm1_composite_state(config)
        malformed = unsafe_clone(state, composite_state_digest=MALFORMED_DIGEST)

        with self.assertRaises(tspm1.TSPM1Error) as caught:
            tspm1.probe_tspm1_read_only(config, malformed, object())
        self.assertEqual(tspm1.TSPM1_INVALID_TYPE_OR_SCHEMA, caught.exception.code)

    def test_r05_updated_candidate_rejects_conflict_flag(self) -> None:
        config, source, state = eligible_fixture()
        candidate = tspm1.advance_tspm1_fast(config, state.fast_state, source[1])
        self.assertEqual("FAST_UPDATED", candidate.primary_event)

        with self.assertRaises(tspm1.TSPM1Error) as caught:
            tspm1._make_candidate(
                candidate.poststate,
                candidate.primary_event,
                True,
                candidate.expired_slot_digests,
                candidate.replaced_slot_digest,
                candidate.selected_slot_id,
                candidate.auditory_match_distance,
                candidate.visual_match_distance,
                candidate.consolidation_eligible,
            )
        self.assertEqual(tspm1.TSPM1_ATOMIC_RESULT_REQUIRED, caught.exception.code)

    def test_r06_candidate_rejects_support_eligibility_mismatch(self) -> None:
        config, source, state = eligible_fixture()
        candidate = tspm1.advance_tspm1_fast(config, state.fast_state, source[1])
        forged = tspm1._make_candidate(
            candidate.poststate,
            candidate.primary_event,
            candidate.partial_association_conflict,
            candidate.expired_slot_digests,
            candidate.replaced_slot_digest,
            candidate.selected_slot_id,
            candidate.auditory_match_distance,
            candidate.visual_match_distance,
            False,
        )
        owner = owner_for(config, state, source[1], "r06")
        with patch.object(tspm1, "advance_tspm1_fast", return_value=forged), patch.object(
            tspm1,
            "advance_ppb1_bank",
        ) as ppb_step:
            self.assert_terminal_failure(
                owner,
                lambda: owner.consume_once(config, state, source[1]),
                lambda: owner.consume_once(config, state, source[1]),
                tspm1.TSPM1_ATOMIC_RESULT_REQUIRED,
            )
        self.assertEqual(0, ppb_step.call_count)

    def test_r07_candidate_rejects_nonminimal_lru_slot(self) -> None:
        bound_profile = profile()
        config = config_for(
            bound_profile,
            capacity=2,
            threshold=0.1,
            expire_after=20,
        )
        envelope = envelope_for(
            bound_profile,
            ((0.0, 0.0), (0.5, 0.5), (0.9, 0.9)),
            suffix="s2dm.r07",
        )
        source = exposures(config, envelope)
        state = tspm1.initial_tspm1_composite_state(config)
        for index in range(2):
            _, result = advance(config, state, source[index], index)
            state = result.poststate
        candidate = tspm1.advance_tspm1_fast(config, state.fast_state, source[2])
        other_slot_id = next(
            slot.slot_id
            for slot in state.fast_state.slots
            if slot.slot_id != candidate.selected_slot_id
        )
        forged = tspm1._make_candidate(
            candidate.poststate,
            candidate.primary_event,
            candidate.partial_association_conflict,
            candidate.expired_slot_digests,
            candidate.replaced_slot_digest,
            other_slot_id,
            candidate.auditory_match_distance,
            candidate.visual_match_distance,
            candidate.consolidation_eligible,
        )
        owner = owner_for(config, state, source[2], "r07")
        with patch.object(tspm1, "advance_tspm1_fast", return_value=forged), patch.object(
            tspm1,
            "advance_ppb1_bank",
        ) as ppb_step:
            self.assert_terminal_failure(
                owner,
                lambda: owner.consume_once(config, state, source[2]),
                lambda: owner.consume_once(config, state, source[2]),
                tspm1.TSPM1_ATOMIC_RESULT_REQUIRED,
            )
        self.assertEqual(0, ppb_step.call_count)

    def test_r08_committed_receipt_rejects_created_event(self) -> None:
        config, source, state = eligible_fixture()
        _, result = advance(config, state, source[1], 1)
        receipt = result.receipt
        payload = receipt.payload_without_digest()
        payload["primary_event"] = "FAST_CREATED"

        with self.assertRaises(tspm1.TSPM1Error) as caught:
            replace(
                receipt,
                primary_event="FAST_CREATED",
                receipt_digest=tspm1._digest(payload),
            )
        self.assertEqual(tspm1.TSPM1_ATOMIC_RESULT_REQUIRED, caught.exception.code)

    def test_r09_ineligible_receipt_rejects_ppb_roles(self) -> None:
        config, source, state = eligible_fixture()
        _, result = advance(config, state, source[1], 1)
        receipt = result.receipt
        payload = receipt.payload_without_digest()
        payload["consolidation_status"] = "NOT_ELIGIBLE"

        with self.assertRaises(tspm1.TSPM1Error) as caught:
            replace(
                receipt,
                consolidation_status="NOT_ELIGIBLE",
                receipt_digest=tspm1._digest(payload),
            )
        self.assertEqual(tspm1.TSPM1_ATOMIC_RESULT_REQUIRED, caught.exception.code)

    def test_r10_slow_context_requires_two_positive_slow_findings(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        envelope = envelope_for(
            bound_profile,
            ((0.1, 0.1),) * 5,
            suffix="s2dm.r10",
        )
        source = exposures(config, envelope)
        state = tspm1.initial_tspm1_composite_state(config)
        for index in range(4):
            _, result = advance(config, state, source[index], index)
            state = result.poststate
        probe = tspm1.bind_tspm1_probe(
            config,
            envelope,
            envelope.auditory_stream.timed_frames[4],
            envelope.visual_stream.timed_frames[4],
        )
        finding = tspm1.probe_tspm1_read_only(config, state, probe)
        self.assertEqual("SLOW_PPB1_CONTEXT", finding.context_source)
        payload = finding.payload_without_digest()
        payload["visual_slow_status"] = "SLOW_NOT_RECOGNIZED"

        with self.assertRaises(tspm1.TSPM1Error) as caught:
            replace(
                finding,
                visual_slow_status="SLOW_NOT_RECOGNIZED",
                finding_digest=tspm1._digest(payload),
            )
        self.assertEqual(tspm1.TSPM1_ATOMIC_RESULT_REQUIRED, caught.exception.code)

    def test_r11_fast_context_requires_positive_fast_finding(self) -> None:
        bound_profile = profile()
        config = config_for(bound_profile)
        envelope = envelope_for(bound_profile, ((0.1, 0.1),), suffix="s2dm.r11")
        state = tspm1.initial_tspm1_composite_state(config)
        probe = tspm1.bind_tspm1_probe(
            config,
            envelope,
            envelope.auditory_stream.timed_frames[0],
            envelope.visual_stream.timed_frames[0],
        )
        finding = tspm1.probe_tspm1_read_only(config, state, probe)
        payload = finding.payload_without_digest()
        payload["context_source"] = "FAST_ASSOCIATIVE_CONTEXT"

        with self.assertRaises(tspm1.TSPM1Error) as caught:
            replace(
                finding,
                context_source="FAST_ASSOCIATIVE_CONTEXT",
                finding_digest=tspm1._digest(payload),
            )
        self.assertEqual(tspm1.TSPM1_ATOMIC_RESULT_REQUIRED, caught.exception.code)

    def test_r12_step_result_rejects_owner_receipt_source_mismatch(self) -> None:
        config, source, state = eligible_fixture()
        _, result = advance(config, state, source[1], 1)
        base_owner = result.owner_poststate
        owner_projection = base_owner.result_projection_payload()
        owner_projection["authorized_exposure_digest"] = FOREIGN_DIGEST
        result_payload = {
            "schema_version": tspm1.TSPM1_SCHEMA_VERSION,
            "poststate_digest": result.poststate.composite_state_digest,
            "receipt_digest": result.receipt.receipt_digest,
            "owner_poststate_projection": owner_projection,
        }
        result_digest = tspm1._digest(result_payload)
        owner_payload = base_owner.payload_without_digest()
        owner_payload["authorized_exposure_digest"] = FOREIGN_DIGEST
        owner_payload["committed_result_digest"] = result_digest
        forged_owner = tspm1.TSPM1CoordinatorOwnerSnapshot(
            owner_id=base_owner.owner_id,
            authorization_id=base_owner.authorization_id,
            consumption_id=base_owner.consumption_id,
            authorized_config_binding_digest=(
                base_owner.authorized_config_binding_digest
            ),
            authorized_composite_prestate_digest=(
                base_owner.authorized_composite_prestate_digest
            ),
            authorized_exposure_digest=FOREIGN_DIGEST,
            status=base_owner.status,
            attempt_count=base_owner.attempt_count,
            use_count=base_owner.use_count,
            generation=base_owner.generation,
            committed_result_digest=result_digest,
            failure_code=None,
            failure_digest=None,
            owner_state_digest=tspm1._digest(owner_payload),
        )

        with self.assertRaises(tspm1.TSPM1Error) as caught:
            tspm1.TSPM1StepResult(
                result.poststate,
                result.receipt,
                forged_owner,
                result_digest,
            )
        self.assertEqual(tspm1.TSPM1_ATOMIC_RESULT_REQUIRED, caught.exception.code)

    def test_b13_rejects_auditory_ppb_config_digest_atomically(self) -> None:
        config, source, state = eligible_fixture()
        owner = owner_for(config, state, source[1], "b13")
        real_advance = tspm1.advance_ppb1_bank
        calls = []

        def malformed_auditory(ppb_config, ppb_state, frame):
            calls.append(frame.modality_id)
            result = real_advance(ppb_config, ppb_state, frame)
            if frame.modality_id == "auditory":
                readout = replace(result.readout, config_digest=FOREIGN_DIGEST)
                return PPB1StepResult(result.poststate, readout)
            return result

        with patch.object(tspm1, "advance_ppb1_bank", side_effect=malformed_auditory):
            self.assert_terminal_failure(
                owner,
                lambda: owner.consume_once(config, state, source[1]),
                lambda: owner.consume_once(config, state, source[1]),
                tspm1.TSPM1_ATOMIC_RESULT_REQUIRED,
            )
        self.assertEqual(["auditory", "visual"], calls)

    def test_b14_rejects_auditory_ppb_input_digest_atomically(self) -> None:
        config, source, state = eligible_fixture()
        owner = owner_for(config, state, source[1], "b14")
        real_advance = tspm1.advance_ppb1_bank
        calls = []

        def malformed_auditory(ppb_config, ppb_state, frame):
            calls.append(frame.modality_id)
            result = real_advance(ppb_config, ppb_state, frame)
            if frame.modality_id == "auditory":
                readout = replace(result.readout, input_digest=FOREIGN_DIGEST)
                return PPB1StepResult(result.poststate, readout)
            return result

        with patch.object(tspm1, "advance_ppb1_bank", side_effect=malformed_auditory):
            self.assert_terminal_failure(
                owner,
                lambda: owner.consume_once(config, state, source[1]),
                lambda: owner.consume_once(config, state, source[1]),
                tspm1.TSPM1_ATOMIC_RESULT_REQUIRED,
            )
        self.assertEqual(["auditory", "visual"], calls)

    def test_b15_rejects_visual_ppb_prestate_digest_atomically(self) -> None:
        config, source, state = eligible_fixture()
        owner = owner_for(config, state, source[1], "b15")
        real_advance = tspm1.advance_ppb1_bank
        calls = []

        def malformed_visual(ppb_config, ppb_state, frame):
            calls.append(frame.modality_id)
            result = real_advance(ppb_config, ppb_state, frame)
            if frame.modality_id == "visual":
                readout = replace(result.readout, prestate_digest=FOREIGN_DIGEST)
                return PPB1StepResult(result.poststate, readout)
            return result

        with patch.object(tspm1, "advance_ppb1_bank", side_effect=malformed_visual):
            self.assert_terminal_failure(
                owner,
                lambda: owner.consume_once(config, state, source[1]),
                lambda: owner.consume_once(config, state, source[1]),
                tspm1.TSPM1_ATOMIC_RESULT_REQUIRED,
            )
        self.assertEqual(["auditory", "visual"], calls)

    def test_a16_second_ppb_failure_publishes_nothing_and_blocks_retry(self) -> None:
        config, source, state = eligible_fixture()
        owner = owner_for(config, state, source[1], "a16")
        real_advance = tspm1.advance_ppb1_bank
        calls = []

        def fail_visual(ppb_config, ppb_state, frame):
            calls.append(frame.modality_id)
            if frame.modality_id == "visual":
                raise RuntimeError("bound synthetic visual failure")
            return real_advance(ppb_config, ppb_state, frame)

        with patch.object(tspm1, "advance_ppb1_bank", side_effect=fail_visual):
            self.assert_terminal_failure(
                owner,
                lambda: owner.consume_once(config, state, source[1]),
                lambda: owner.consume_once(config, state, source[1]),
                tspm1.TSPM1_ATOMIC_RESULT_REQUIRED,
            )
        self.assertEqual(["auditory", "visual"], calls)


if __name__ == "__main__":
    unittest.main()
