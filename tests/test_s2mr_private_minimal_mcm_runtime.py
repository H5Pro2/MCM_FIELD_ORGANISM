"""Focused neutral composition qualification for the private S2-MR runtime."""

from __future__ import annotations

from dataclasses import dataclass, FrozenInstanceError
import hashlib
import json
import unittest

from tools import _s2lm_private_role_free_stream_processor as stream
from tools import _s2mr_private_minimal_mcm_runtime as runtime
from tools._s2kq_private_partial_cue_retrieval_336 import (
    PartialCueContextHypothesis336V1,
)
from tools._s2kz_private_auditory_partial_cue_retrieval_336 import (
    AuditoryPartialCueHypothesis48V1,
)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class _Token:
    name: str
    digest: str


def _visual_hypothesis(*, area: str = "A_RECENT") -> PartialCueContextHypothesis336V1:
    temporary = PartialCueContextHypothesis336V1(
        area,
        (_sha("visual-slot"),),
        _sha("visual-values"),
        (32, 33),
        (0.25, 0.75),
        _sha("visual-cue"),
        _sha("visual-mask"),
        _sha("memory-state"),
        32,
        288,
        "",
    )
    return PartialCueContextHypothesis336V1(
        temporary.area,
        temporary.provenance_slot_digests,
        temporary.candidate_values_digest,
        temporary.masked_positions,
        temporary.proposed_values,
        temporary.cue_digest,
        temporary.mask_plan_digest,
        temporary.state_digest,
        temporary.observed_value_count,
        temporary.field_contact_count,
        _digest(temporary.payload_without_digest()),
    )


def _auditory_hypothesis(*, area: str = "B_STABLE_AUDITORY") -> AuditoryPartialCueHypothesis48V1:
    temporary = AuditoryPartialCueHypothesis48V1(
        area,
        (_sha("auditory-slot"),),
        _sha("auditory-values"),
        (24, 25),
        (0.125, 0.625),
        _sha("auditory-cue"),
        _sha("auditory-band-plan"),
        _sha("memory-state"),
        24,
        288,
        48,
        "",
    )
    return AuditoryPartialCueHypothesis48V1(
        temporary.area,
        temporary.provenance_slot_digests,
        temporary.candidate_values_digest,
        temporary.masked_bands,
        temporary.proposed_values,
        temporary.cue_digest,
        temporary.band_plan_digest,
        temporary.state_digest,
        temporary.observed_value_count,
        temporary.visual_value_count,
        temporary.field_contact_count,
        _digest(temporary.payload_without_digest()),
    )


def _initial_state() -> stream.PerceptionStreamStateV1:
    field = _Token("field-0", _sha("field-0"))
    memory = _Token("memory-0", _sha("memory-0"))
    return stream.initial_perception_stream_state(
        stream_id="s2mr-neutral-stream",
        field_state=field,
        field_state_digest=field.digest,
        memory_state=memory,
        memory_state_digest=memory.digest,
    )


def _event(ordinal: int, event_type: str) -> stream.PerceptionStreamEvent336V1:
    perception_digest = _sha(f"perception-{ordinal}-{event_type}")
    return stream.build_perception_stream_event(
        event_id=f"s2mr-neutral-event-{ordinal:03d}",
        ordinal=ordinal,
        event_type=event_type,
        source_digest=_sha(f"source-{ordinal}"),
        perception_digest=perception_digest,
        field_projection_digest=perception_digest,
        operation_projection_digest=perception_digest,
        field_payload=_Token(f"field-input-{ordinal}", perception_digest),
        operation_payload=_Token(f"operation-input-{ordinal}", perception_digest),
    )


class _Adapters:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int, str]] = []
        self.fail: set[str] = set()
        self.decision = "ABSTAIN_NO_CONTEXT"
        self.primary_hypothesis: runtime.RuntimeHypothesis336V1 | None = None
        self.baseline_hypothesis: runtime.RuntimeHypothesis336V1 | None = None

    def field(self, state: _Token, event: stream.PerceptionStreamEvent336V1):
        self.calls.append(("FIELD", event.ordinal, event.perception_digest))
        if "FIELD" in self.fail:
            raise RuntimeError("neutral field failure")
        post = _Token(f"field-{event.ordinal}", _sha(f"field-{event.ordinal}"))
        return stream.StreamBranchResultV1(
            "FIELD",
            event.field_projection_digest,
            state.digest,
            post,
            post.digest,
            _sha(f"field-receipt-{event.ordinal}"),
        )

    def memory(self, state: _Token, event: stream.PerceptionStreamEvent336V1):
        self.calls.append(("MEMORY", event.ordinal, event.perception_digest))
        if "MEMORY" in self.fail:
            raise RuntimeError("neutral memory failure")
        post = _Token(f"memory-{event.ordinal}", _sha(f"memory-{event.ordinal}"))
        return stream.StreamBranchResultV1(
            "MEMORY",
            event.operation_projection_digest,
            state.digest,
            post,
            post.digest,
            _sha(f"memory-receipt-{event.ordinal}"),
        )

    def _scan(self, role: str, state: _Token, event: stream.PerceptionStreamEvent336V1):
        self.calls.append((role, event.ordinal, event.perception_digest))
        if role in self.fail:
            raise RuntimeError("neutral scan failure")
        hypothesis = (
            self.primary_hypothesis if role == "PRIMARY" else self.baseline_hypothesis
        )
        return stream.StreamScanResultV1(
            role,
            event.operation_projection_digest,
            state.digest,
            state.digest,
            self.decision,
            None if hypothesis is None else hypothesis.hypothesis_digest,
            _sha(f"{role.lower()}-receipt-{event.ordinal}"),
            hypothesis,
        )

    def visual_scan(self, state, event):
        return self._scan("PRIMARY", state, event)

    def visual_baseline(self, state, event):
        return self._scan("DIRECT_BASELINE", state, event)

    def auditory_scan(self, state, event):
        return self._scan("PRIMARY", state, event)

    def auditory_baseline(self, state, event):
        return self._scan("DIRECT_BASELINE", state, event)

    def processor(self) -> stream.RoleFreePerceptionStreamProcessor:
        return stream.RoleFreePerceptionStreamProcessor(
            field_adapter=self.field,
            memory_adapter=self.memory,
            visual_scan=self.visual_scan,
            visual_baseline=self.visual_baseline,
            auditory_scan=self.auditory_scan,
            auditory_baseline=self.auditory_baseline,
        )


def _runtime(*, max_events: int = 8, adapters: _Adapters | None = None):
    adapters = adapters or _Adapters()
    config = runtime.build_minimal_runtime_config(
        runtime_id="s2mr-neutral-runtime",
        max_event_count=max_events,
        source_binding_digest=_sha("neutral-source-binding"),
        component_binding_digest=_sha("qualified-components"),
    )
    subject = runtime.MinimalMCMRuntime336(
        config=config,
        processor=adapters.processor(),
        initial_state=_initial_state(),
    )
    return subject, adapters


class S2MRMinimalRuntimeTests(unittest.TestCase):
    def test_01_initial_snapshot_is_bound_immutable_and_closable(self) -> None:
        subject, _ = _runtime()
        before = subject.snapshot()
        self.assertEqual(("OPEN", 1, 0), (before.status, before.next_ordinal, before.processed_event_count))
        self.assertEqual(before.snapshot_digest, _digest(before.payload_without_digest()))
        with self.assertRaises(FrozenInstanceError):
            before.status = "CLOSED"
        after = subject.close()
        self.assertEqual("CLOSED", after.status)
        self.assertNotEqual(before.snapshot_digest, after.snapshot_digest)

    def test_02_complete_av_routes_one_field_contact_and_atomic_formation(self) -> None:
        subject, adapters = _runtime()
        result = subject.process_once(_event(1, "COMPLETE_AV_PERCEPTION"))
        self.assertEqual(["FIELD", "MEMORY"], [item[0] for item in adapters.calls])
        self.assertEqual("FIELD_CONTACT_RECORDED", result.perception_status)
        self.assertEqual("FORMATION_COMMITTED", result.memory_status)
        self.assertEqual("NOT_REQUESTED", result.context_status)
        self.assertIsNotNone(result.field_receipt_digest)
        self.assertIsNotNone(result.memory_receipt_digest)

    def test_03_visual_cue_publishes_only_the_exact_visual_hypothesis_type(self) -> None:
        adapters = _Adapters()
        adapters.decision = "ADMIT_SINGLE_CONTEXT"
        adapters.primary_hypothesis = _visual_hypothesis()
        adapters.baseline_hypothesis = _visual_hypothesis()
        subject, _ = _runtime(adapters=adapters)
        before = subject.snapshot()
        result = subject.process_once(_event(1, "PARTIAL_VISUAL_CUE"))
        self.assertEqual("CONTEXT_CANDIDATE_AVAILABLE", result.context_status)
        self.assertIs(type(result.hypothesis), PartialCueContextHypothesis336V1)
        self.assertEqual(before.memory_state_digest, subject.snapshot().memory_state_digest)

    def test_04_auditory_cue_publishes_only_the_exact_auditory_hypothesis_type(self) -> None:
        adapters = _Adapters()
        adapters.decision = "ADMIT_SINGLE_CONTEXT"
        adapters.primary_hypothesis = _auditory_hypothesis()
        adapters.baseline_hypothesis = _auditory_hypothesis()
        subject, _ = _runtime(adapters=adapters)
        before = subject.snapshot()
        result = subject.process_once(_event(1, "PARTIAL_AUDITORY_CUE"))
        self.assertEqual("CONTEXT_CANDIDATE_AVAILABLE", result.context_status)
        self.assertIs(type(result.hypothesis), AuditoryPartialCueHypothesis48V1)
        self.assertEqual(before.memory_state_digest, subject.snapshot().memory_state_digest)

    def test_05_all_bound_abstentions_remain_hypothesis_free(self) -> None:
        decisions = (
            "ABSTAIN_INTERNAL_AMBIGUITY",
            "ABSTAIN_INTERNAL_CONFLICT",
            "ABSTAIN_AMBIGUOUS_CONTEXT",
            "ABSTAIN_NO_CONTEXT",
            "ABSTAIN_NO_APPLICABLE_CONTEXT",
        )
        for decision in decisions:
            with self.subTest(decision=decision):
                adapters = _Adapters()
                adapters.decision = decision
                subject, _ = _runtime(adapters=adapters)
                result = subject.process_once(_event(1, "PARTIAL_VISUAL_CUE"))
                self.assertEqual(decision, result.context_status)
                self.assertIsNone(result.hypothesis)

    def test_06_primary_and_baseline_receive_the_same_read_only_memory_state(self) -> None:
        subject, adapters = _runtime()
        before = subject.snapshot()
        result = subject.process_once(_event(1, "PARTIAL_AUDITORY_CUE"))
        self.assertEqual(["FIELD", "PRIMARY", "DIRECT_BASELINE"], [item[0] for item in adapters.calls])
        self.assertEqual("READ_ONLY_UNCHANGED", result.memory_status)
        self.assertEqual(before.memory_state_digest, subject.snapshot().memory_state_digest)
        self.assertEqual(2, subject.snapshot().scan_attempt_count)

    def test_07_baseline_decision_mismatch_fails_closed_without_hypothesis(self) -> None:
        adapters = _Adapters()
        original = adapters.visual_baseline

        def mismatch(state, event):
            value = original(state, event)
            return stream.StreamScanResultV1(
                value.scan_role,
                value.input_digest,
                value.prestate_digest,
                value.poststate_digest,
                "ABSTAIN_NO_APPLICABLE_CONTEXT",
                None,
                value.receipt_digest,
            )

        processor = stream.RoleFreePerceptionStreamProcessor(
            field_adapter=adapters.field,
            memory_adapter=adapters.memory,
            visual_scan=adapters.visual_scan,
            visual_baseline=mismatch,
            auditory_scan=adapters.auditory_scan,
            auditory_baseline=adapters.auditory_baseline,
        )
        config = runtime.build_minimal_runtime_config(
            runtime_id="s2mr-mismatch-runtime",
            max_event_count=2,
            source_binding_digest=_sha("source"),
            component_binding_digest=_sha("components"),
        )
        subject = runtime.MinimalMCMRuntime336(config=config, processor=processor, initial_state=_initial_state())
        result = subject.process_once(_event(1, "PARTIAL_VISUAL_CUE"))
        self.assertEqual("SCAN_FAILED", result.context_status)
        self.assertIsNone(result.hypothesis)
        self.assertIn("SCAN_BASELINE_DECISION_MISMATCH", result.error_codes)

    def test_08_baseline_hypothesis_mismatch_fails_closed(self) -> None:
        adapters = _Adapters()
        adapters.decision = "ADMIT_SINGLE_CONTEXT"
        adapters.primary_hypothesis = _visual_hypothesis(area="A_RECENT")
        adapters.baseline_hypothesis = _visual_hypothesis(area="B_STABLE")
        subject, _ = _runtime(adapters=adapters)
        result = subject.process_once(_event(1, "PARTIAL_VISUAL_CUE"))
        self.assertEqual("SCAN_FAILED", result.context_status)
        self.assertIsNone(result.hypothesis)
        self.assertIn("SCAN_BASELINE_HYPOTHESIS_MISMATCH", result.error_codes)

    def test_09_wrong_hypothesis_modality_is_rejected_without_fallback(self) -> None:
        adapters = _Adapters()
        adapters.decision = "ADMIT_SINGLE_CONTEXT"
        adapters.primary_hypothesis = _auditory_hypothesis()
        adapters.baseline_hypothesis = _auditory_hypothesis()
        subject, _ = _runtime(adapters=adapters)
        result = subject.process_once(_event(1, "PARTIAL_VISUAL_CUE"))
        self.assertEqual("SCAN_FAILED", result.context_status)
        self.assertIsNone(result.hypothesis)
        self.assertIn("SCAN_HYPOTHESIS_INVALID", result.error_codes)

    def test_10_field_failure_does_not_suppress_memory_formation(self) -> None:
        adapters = _Adapters()
        adapters.fail.add("FIELD")
        subject, _ = _runtime(adapters=adapters)
        before = subject.snapshot()
        result = subject.process_once(_event(1, "COMPLETE_AV_PERCEPTION"))
        after = subject.snapshot()
        self.assertEqual("FIELD_CONTACT_FAILED", result.perception_status)
        self.assertEqual("FORMATION_COMMITTED", result.memory_status)
        self.assertEqual(before.field_state_digest, after.field_state_digest)
        self.assertNotEqual(before.memory_state_digest, after.memory_state_digest)

    def test_11_memory_failure_does_not_rollback_field_contact(self) -> None:
        adapters = _Adapters()
        adapters.fail.add("MEMORY")
        subject, _ = _runtime(adapters=adapters)
        before = subject.snapshot()
        result = subject.process_once(_event(1, "COMPLETE_AV_PERCEPTION"))
        after = subject.snapshot()
        self.assertEqual("FIELD_CONTACT_RECORDED", result.perception_status)
        self.assertEqual("FORMATION_FAILED", result.memory_status)
        self.assertNotEqual(before.field_state_digest, after.field_state_digest)
        self.assertEqual(before.memory_state_digest, after.memory_state_digest)

    def test_12_scan_failure_does_not_rollback_field_or_change_memory(self) -> None:
        adapters = _Adapters()
        adapters.fail.add("PRIMARY")
        subject, _ = _runtime(adapters=adapters)
        before = subject.snapshot()
        result = subject.process_once(_event(1, "PARTIAL_VISUAL_CUE"))
        after = subject.snapshot()
        self.assertEqual("FIELD_CONTACT_RECORDED", result.perception_status)
        self.assertEqual("SCAN_FAILED", result.context_status)
        self.assertNotEqual(before.field_state_digest, after.field_state_digest)
        self.assertEqual(before.memory_state_digest, after.memory_state_digest)
        self.assertIsNone(result.hypothesis)

    def test_13_each_event_gets_fresh_authority_and_runtime_stays_open(self) -> None:
        subject, _ = _runtime(max_events=3)
        first = subject.process_once(_event(1, "COMPLETE_AV_PERCEPTION"))
        second = subject.process_once(_event(2, "PARTIAL_VISUAL_CUE"))
        third = subject.process_once(_event(3, "PARTIAL_AUDITORY_CUE"))
        snapshot = subject.snapshot()
        self.assertEqual("OPEN", snapshot.status)
        self.assertEqual((4, 3, 3, 1, 4), (
            snapshot.next_ordinal,
            snapshot.processed_event_count,
            snapshot.field_attempt_count,
            snapshot.memory_formation_attempt_count,
            snapshot.scan_attempt_count,
        ))
        self.assertEqual(first.poststate_digest, second.prestate_digest)
        self.assertEqual(second.poststate_digest, third.prestate_digest)

    def test_14_budget_and_closed_runtime_reject_before_branch_calls(self) -> None:
        subject, adapters = _runtime(max_events=1)
        subject.process_once(_event(1, "COMPLETE_AV_PERCEPTION"))
        call_count = len(adapters.calls)
        with self.assertRaises(runtime.S2MRRuntimeError):
            subject.process_once(_event(2, "COMPLETE_AV_PERCEPTION"))
        self.assertEqual(call_count, len(adapters.calls))
        subject.close()
        with self.assertRaises(runtime.S2MRRuntimeError):
            subject.process_once(_event(2, "COMPLETE_AV_PERCEPTION"))

    def test_15_wrong_ordinal_and_noncanonical_event_reject_before_adapters(self) -> None:
        subject, adapters = _runtime()
        with self.assertRaises(runtime.S2MRRuntimeError):
            subject.process_once(_event(2, "COMPLETE_AV_PERCEPTION"))
        valid = _event(1, "COMPLETE_AV_PERCEPTION")
        invalid = stream.PerceptionStreamEvent336V1(
            valid.event_id,
            valid.ordinal,
            valid.event_type,
            valid.source_digest,
            valid.perception_digest,
            valid.field_projection_digest,
            valid.operation_projection_digest,
            valid.field_payload,
            valid.operation_payload,
            _sha("tampered-event"),
        )
        with self.assertRaises(runtime.S2MRRuntimeError):
            subject.process_once(invalid)
        self.assertEqual([], adapters.calls)

    def test_16_step_is_compact_digest_bound_and_contains_no_research_roles(self) -> None:
        subject, adapters = _runtime()
        result = subject.process_once(_event(1, "PARTIAL_VISUAL_CUE"))
        payload = result.payload_without_digest()
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
        self.assertEqual(result.step_digest, _digest(payload))
        self.assertLess(len(encoded), runtime.MAX_STEP_BYTES)
        self.assertEqual(subject.snapshot().snapshot_digest, result.poststate_digest)
        self.assertEqual(
            {adapters.calls[0][2]},
            {item[2] for item in adapters.calls},
        )
        for forbidden in ("TARGET", "DISTRACTOR", "HOLDOUT", "FAMILY", "RGB8", "PCM_F32LE"):
            self.assertNotIn(forbidden, encoded.decode("ascii"))


if __name__ == "__main__":
    unittest.main()
