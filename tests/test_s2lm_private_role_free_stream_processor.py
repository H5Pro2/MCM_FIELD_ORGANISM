"""Neutral contract tests for the private S2-LM stream processor."""

from __future__ import annotations

from dataclasses import dataclass, FrozenInstanceError
import hashlib
import json
from pathlib import Path
import unittest

from tools import _s2lm_private_role_free_stream_processor as stream
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools import _s2jw_profiled_memory_coordinator as memory
from tools._s2lj_coherent_av_fixtures import S2LJSourceStream


ROOT = Path(__file__).resolve().parents[1]


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True)
class _Token:
    name: str
    digest: str


def _initial_state() -> stream.PerceptionStreamStateV1:
    field = _Token("field-0", _sha("field-0"))
    stored = _Token("memory-0", _sha("memory-0"))
    return stream.initial_perception_stream_state(
        stream_id="s2lm-neutral-stream",
        field_state=field,
        field_state_digest=field.digest,
        memory_state=stored,
        memory_state_digest=stored.digest,
    )


def _event(ordinal: int, event_type: str) -> stream.PerceptionStreamEvent336V1:
    bound = _sha(f"perception-{ordinal}-{event_type}")
    return stream.build_perception_stream_event(
        event_id=f"s2lm-neutral-event-{ordinal:03d}",
        ordinal=ordinal,
        event_type=event_type,
        source_digest=_sha(f"source-{ordinal}"),
        perception_digest=bound,
        field_projection_digest=bound,
        operation_projection_digest=bound,
        field_payload=_Token(f"field-input-{ordinal}", bound),
        operation_payload=_Token(f"operation-input-{ordinal}", bound),
    )


class _Adapters:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.fail: set[str] = set()

    def field(self, state: _Token, event) -> stream.StreamBranchResultV1:
        self.calls.append("FIELD")
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

    def memory(self, state: _Token, event) -> stream.StreamBranchResultV1:
        self.calls.append("MEMORY")
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

    def _scan(self, role: str, state: _Token, event) -> stream.StreamScanResultV1:
        self.calls.append(role)
        if role in self.fail:
            raise RuntimeError("neutral scan failure")
        return stream.StreamScanResultV1(
            role,
            event.operation_projection_digest,
            state.digest,
            state.digest,
            "ABSTAIN_NO_CONTEXT",
            None,
            _sha(f"{role.lower()}-receipt-{event.ordinal}"),
        )

    def visual_scan(self, state, event):
        return self._scan("PRIMARY", state, event)

    def visual_baseline(self, state, event):
        return self._scan("DIRECT_BASELINE", state, event)

    def auditory_scan(self, state, event):
        return self._scan("PRIMARY", state, event)

    def auditory_baseline(self, state, event):
        return self._scan("DIRECT_BASELINE", state, event)

    def processor(self, memory_adapter=None) -> stream.RoleFreePerceptionStreamProcessor:
        return stream.RoleFreePerceptionStreamProcessor(
            field_adapter=self.field,
            memory_adapter=memory_adapter or self.memory,
            visual_scan=self.visual_scan,
            visual_baseline=self.visual_baseline,
            auditory_scan=self.auditory_scan,
            auditory_baseline=self.auditory_baseline,
        )


def _run(event_type: str, *, failures: tuple[str, ...] = ()):
    state = _initial_state()
    event = _event(1, event_type)
    adapters = _Adapters()
    adapters.fail.update(failures)
    owner = stream.PerceptionEventOwner("s2lm-neutral-owner-001", state.state_digest, event.event_digest)
    result = adapters.processor().process_once(state=state, event=event, owner=owner)
    return state, event, adapters, owner, result


class S2LMRoleFreeStreamTests(unittest.TestCase):
    def test_01_event_stream_and_owner_snapshots_are_immutable(self) -> None:
        state = _initial_state()
        event = _event(1, "COMPLETE_AV_PERCEPTION")
        owner = stream.PerceptionEventOwner("s2lm-neutral-owner-001", state.state_digest, event.event_digest)
        with self.assertRaises(FrozenInstanceError):
            state.status = "CLOSED"
        with self.assertRaises(FrozenInstanceError):
            event.ordinal = 2
        with self.assertRaises(FrozenInstanceError):
            owner.snapshot().status = "FAILED"

    def test_02_complete_av_routes_one_field_and_one_memory_formation(self) -> None:
        _, _, adapters, _, result = _run("COMPLETE_AV_PERCEPTION")
        self.assertEqual(["FIELD", "MEMORY"], adapters.calls)
        self.assertIsNotNone(result.field_result)
        self.assertIsNotNone(result.memory_result)
        self.assertIsNone(result.primary_scan)
        self.assertEqual((1, 1, 0), (
            result.poststate.field_attempt_count,
            result.poststate.memory_formation_attempt_count,
            result.poststate.scan_attempt_count,
        ))

    def test_03_visual_cue_routes_field_and_two_read_only_scans(self) -> None:
        before, _, adapters, _, result = _run("PARTIAL_VISUAL_CUE")
        self.assertEqual(["FIELD", "PRIMARY", "DIRECT_BASELINE"], adapters.calls)
        self.assertIsNone(result.memory_result)
        self.assertEqual(before.memory_state_digest, result.poststate.memory_state_digest)
        self.assertEqual(2, result.poststate.scan_attempt_count)

    def test_04_auditory_cue_routes_field_and_two_read_only_scans(self) -> None:
        before, _, adapters, _, result = _run("PARTIAL_AUDITORY_CUE")
        self.assertEqual(["FIELD", "PRIMARY", "DIRECT_BASELINE"], adapters.calls)
        self.assertIsNone(result.memory_result)
        self.assertEqual(before.memory_state_digest, result.poststate.memory_state_digest)
        self.assertEqual(2, result.poststate.scan_attempt_count)

    def test_05_field_failure_does_not_suppress_or_rollback_memory(self) -> None:
        before, _, adapters, owner, result = _run(
            "COMPLETE_AV_PERCEPTION", failures=("FIELD",)
        )
        self.assertEqual(["FIELD", "MEMORY"], adapters.calls)
        self.assertEqual(before.field_state_digest, result.poststate.field_state_digest)
        self.assertNotEqual(before.memory_state_digest, result.poststate.memory_state_digest)
        self.assertEqual(("FIELD_BRANCH_FAILED",), result.error_codes)
        self.assertEqual("FAILED", owner.snapshot().status)

    def test_06_memory_failure_does_not_rollback_valid_field_contact(self) -> None:
        before, _, adapters, owner, result = _run(
            "COMPLETE_AV_PERCEPTION", failures=("MEMORY",)
        )
        self.assertEqual(["FIELD", "MEMORY"], adapters.calls)
        self.assertNotEqual(before.field_state_digest, result.poststate.field_state_digest)
        self.assertEqual(before.memory_state_digest, result.poststate.memory_state_digest)
        self.assertEqual(("MEMORY_BRANCH_FAILED",), result.error_codes)
        self.assertEqual("FAILED", owner.snapshot().status)

    def test_07_scan_failure_does_not_rollback_field_or_mutate_memory(self) -> None:
        before, _, adapters, _, result = _run(
            "PARTIAL_VISUAL_CUE", failures=("PRIMARY",)
        )
        self.assertEqual(["FIELD", "PRIMARY", "DIRECT_BASELINE"], adapters.calls)
        self.assertNotEqual(before.field_state_digest, result.poststate.field_state_digest)
        self.assertEqual(before.memory_state_digest, result.poststate.memory_state_digest)
        self.assertIsNone(result.primary_scan)
        self.assertIsNotNone(result.baseline_scan)
        self.assertEqual(("PRIMARY_SCAN_FAILED",), result.error_codes)

    def test_08_consumed_event_owner_does_not_close_stream_and_cannot_repeat(self) -> None:
        state, event, adapters, owner, result = _run("COMPLETE_AV_PERCEPTION")
        self.assertEqual("CONSUMED", owner.snapshot().status)
        self.assertEqual("OPEN", result.poststate.status)
        with self.assertRaises(stream.S2LMStreamError):
            adapters.processor().process_once(state=state, event=event, owner=owner)

    def test_09_next_event_uses_a_fresh_owner_on_the_open_stream(self) -> None:
        _, _, adapters, _, first = _run("COMPLETE_AV_PERCEPTION")
        second_event = _event(2, "PARTIAL_VISUAL_CUE")
        owner = stream.PerceptionEventOwner(
            "s2lm-neutral-owner-002", first.poststate.state_digest, second_event.event_digest
        )
        second = adapters.processor().process_once(
            state=first.poststate, event=second_event, owner=owner
        )
        self.assertEqual(3, second.poststate.next_ordinal)
        self.assertEqual("OPEN", second.poststate.status)
        self.assertEqual("CONSUMED", owner.snapshot().status)

    def test_10_projection_mismatch_stops_before_any_adapter(self) -> None:
        with self.assertRaises(stream.S2LMStreamError):
            stream.build_perception_stream_event(
                event_id="s2lm-neutral-event-001",
                ordinal=1,
                event_type="COMPLETE_AV_PERCEPTION",
                source_digest=_sha("source"),
                perception_digest=_sha("perception"),
                field_projection_digest=_sha("field"),
                operation_projection_digest=_sha("memory"),
                field_payload=_Token("field", _sha("field")),
                operation_payload=_Token("memory", _sha("memory")),
            )

    def test_11_existing_atomic_s2jw_adapter_handles_one_neutral_event(self) -> None:
        profile = build_s2jw_default_live_profile()
        config = memory.build_s2jv_coordinator_config(
            tspm_config=profile.tspm_config,
            b4_capacity=profile.b4_capacity,
            ledger_limits=build_s2jv_ledger_limits(profile),
        )
        source_stream = S2LJSourceStream(profile, mode="QUALIFICATION")
        pair, _ = source_stream.materialize_next_formation()
        initial_memory = memory.initial_s2jv_composite_state(config)
        field = _Token("field-0", _sha("field-0"))
        state = stream.initial_perception_stream_state(
            stream_id="s2lm-adapter-stream",
            field_state=field,
            field_state_digest=field.digest,
            memory_state=initial_memory,
            memory_state_digest=initial_memory.state_digest,
        )
        event = stream.build_perception_stream_event(
            event_id="s2lm-adapter-event-001",
            ordinal=1,
            event_type="COMPLETE_AV_PERCEPTION",
            source_digest=_sha("adapter-source"),
            perception_digest=pair.pairing_digest,
            field_projection_digest=pair.pairing_digest,
            operation_projection_digest=pair.pairing_digest,
            field_payload=pair,
            operation_payload=pair,
        )
        owner = stream.PerceptionEventOwner(
            "s2lm-adapter-owner-001", state.state_digest, event.event_digest
        )
        adapters = _Adapters()
        result = adapters.processor(
            memory_adapter=stream.build_s2jw_memory_adapter(config)
        ).process_once(state=state, event=event, owner=owner)
        self.assertEqual(1, result.poststate.memory_state.generation)
        self.assertEqual("CONSUMED", result.owner_poststate.status)

    def test_12_result_is_bounded_role_free_and_digest_bound(self) -> None:
        _, _, _, _, result = _run("PARTIAL_AUDITORY_CUE")
        payload = result.payload_without_digest()
        self.assertEqual(result.result_digest, stream._digest(payload))
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
        self.assertLess(len(encoded), 32_768)
        for forbidden in ("TARGET", "DISTRACTOR", "POSITIVE", "NEGATIVE"):
            self.assertNotIn(forbidden, encoded.decode("ascii"))


if __name__ == "__main__":
    unittest.main()
