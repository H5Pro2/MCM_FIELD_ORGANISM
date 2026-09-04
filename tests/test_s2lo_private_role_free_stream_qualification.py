"""Neutral qualification for the bounded private S2-LO stream shell."""

from __future__ import annotations

from dataclasses import dataclass, FrozenInstanceError
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools import _s2lm_private_role_free_stream_processor as stream
from tools import _s2lo_private_role_free_stream_runner as runner
from tools import _s2lo_private_role_free_stream_verifier as verifier
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools import _s2jw_profiled_memory_coordinator as memory
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as auditory_scan


ROOT = Path(__file__).resolve().parents[1]


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True)
class _Token:
    digest: str


@dataclass(frozen=True, slots=True)
class _Hypothesis:
    hypothesis_digest: str


def _fake_state() -> stream.PerceptionStreamStateV1:
    field = _Token(_sha("field-zero"))
    stored = _Token(_sha("memory-zero"))
    return stream.initial_perception_stream_state(
        stream_id="s2lo-neutral-fake-stream",
        field_state=field,
        field_state_digest=field.digest,
        memory_state=stored,
        memory_state_digest=stored.digest,
    )


def _fake_event(event_type: str) -> stream.PerceptionStreamEvent336V1:
    bound = _sha(f"bound-{event_type}")
    return stream.build_perception_stream_event(
        event_id="s2lo-neutral-fake-event",
        ordinal=1,
        event_type=event_type,
        source_digest=_sha("source"),
        perception_digest=bound,
        field_projection_digest=bound,
        operation_projection_digest=bound,
        field_payload=_Token(bound),
        operation_payload=_Token(bound),
    )


class _FakeAdapters:
    def __init__(self, failures: tuple[str, ...] = (), *, hypothesis: bool = False) -> None:
        self.failures = set(failures)
        self.calls: list[str] = []
        self.hypothesis = hypothesis

    def field(self, state: _Token, event) -> stream.StreamBranchResultV1:
        self.calls.append("FIELD")
        if "FIELD" in self.failures:
            raise RuntimeError("neutral field failure")
        post = _Token(_sha("field-one"))
        return stream.StreamBranchResultV1(
            "FIELD", event.field_projection_digest, state.digest, post, post.digest, _sha("field-receipt")
        )

    def memory(self, state: _Token, event) -> stream.StreamBranchResultV1:
        self.calls.append("MEMORY")
        if "MEMORY" in self.failures:
            raise RuntimeError("neutral memory failure")
        post = _Token(_sha("memory-one"))
        return stream.StreamBranchResultV1(
            "MEMORY", event.operation_projection_digest, state.digest, post, post.digest, _sha("memory-receipt")
        )

    def _scan(self, role: str, state: _Token, event) -> stream.StreamScanResultV1:
        self.calls.append(role)
        if role in self.failures:
            raise RuntimeError("neutral scan failure")
        hypothesis = _Hypothesis(_sha(f"hypothesis-{role}")) if self.hypothesis else None
        return stream.StreamScanResultV1(
            role,
            event.operation_projection_digest,
            state.digest,
            state.digest,
            "ADMIT_SINGLE_CONTEXT" if hypothesis else "ABSTAIN_NO_CONTEXT",
            None if hypothesis is None else hypothesis.hypothesis_digest,
            _sha(f"receipt-{role}"),
            hypothesis,
        )

    def primary(self, state, event):
        return self._scan("PRIMARY", state, event)

    def baseline(self, state, event):
        return self._scan("DIRECT_BASELINE", state, event)

    def processor(self) -> stream.RoleFreePerceptionStreamProcessor:
        return stream.RoleFreePerceptionStreamProcessor(
            field_adapter=self.field,
            memory_adapter=self.memory,
            visual_scan=self.primary,
            visual_baseline=self.baseline,
            auditory_scan=self.primary,
            auditory_baseline=self.baseline,
        )


class S2LOQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = runner.neutral_qualification_record(ROOT)

    def test_01_main_specs_are_fixed_neutral_and_complete(self) -> None:
        specs = runner.MAIN_EVENT_SPECS
        self.assertEqual(18, len(specs))
        self.assertEqual(tuple(f"e{index:02d}" for index in range(1, 19)), tuple(item.event_code for item in specs))
        self.assertEqual(16, sum(item.event_type == "COMPLETE_AV_PERCEPTION" for item in specs))
        self.assertEqual(1, sum(item.event_type == "PARTIAL_AUDITORY_CUE" for item in specs))
        self.assertEqual(1, sum(item.event_type == "PARTIAL_VISUAL_CUE" for item in specs))
        serialized = json.dumps([item.payload_without_digest() for item in specs], sort_keys=True)
        for forbidden in ("TARGET", "DISTRACTOR", "POSITIVE", "NEGATIVE"):
            self.assertNotIn(forbidden, serialized)

    def test_02_specs_and_field_state_are_immutable(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            runner.MAIN_EVENT_SPECS[0].ordinal = 2
        profile = build_s2jw_default_live_profile()
        config = memory.build_s2jv_coordinator_config(
            tspm_config=profile.tspm_config,
            b4_capacity=profile.b4_capacity,
            ledger_limits=build_s2jv_ledger_limits(profile),
        )
        source = runner.S2LOSourceStream(profile, mode="QUALIFICATION")
        value = source.materialize_next(
            config_digest=config.config_digest,
            band_plan=auditory_scan.build_auditory_band_plan_48(),
        )
        field = runner.initial_s2lo_field_state(value.field_input)
        with self.assertRaises(FrozenInstanceError):
            field.step_count = 1

    def test_03_real_neutral_source_has_exact_receptor_dimensions(self) -> None:
        profile = build_s2jw_default_live_profile()
        config = memory.build_s2jv_coordinator_config(
            tspm_config=profile.tspm_config,
            b4_capacity=profile.b4_capacity,
            ledger_limits=build_s2jv_ledger_limits(profile),
        )
        source = runner.S2LOSourceStream(profile, mode="QUALIFICATION")
        value = source.materialize_next(
            config_digest=config.config_digest,
            band_plan=auditory_scan.build_auditory_band_plan_48(),
        )
        pair = value.operation_payload
        self.assertEqual(48, len(pair.auditory.timed_frame.frame.values))
        self.assertEqual(288, len(pair.visual.timed_frame.frame.values))
        self.assertEqual(2, len(value.field_input.timed_frames))
        self.assertEqual(value.perception_digest, value.field_input.perception_digest)

    def test_04_neutral_record_routes_all_three_event_forms(self) -> None:
        events = self.record["execution"]["events"]
        self.assertEqual(
            ["COMPLETE_AV_PERCEPTION", "PARTIAL_AUDITORY_CUE", "PARTIAL_VISUAL_CUE"],
            [item["event_type"] for item in events],
        )
        self.assertEqual(["CONSUMED"] * 3, [item["owner_status"] for item in events])
        self.assertTrue(all(item["error_codes"] == [] for item in events))

    def test_05_neutral_field_memory_and_scan_counters_are_exact(self) -> None:
        counters = self.record["execution"]["counters"]
        self.assertEqual(
            (3, 3, 1, 4, "OPEN"),
            (
                counters["event_count"],
                counters["field_attempt_count"],
                counters["memory_formation_attempt_count"],
                counters["scan_attempt_count"],
                counters["stream_status"],
            ),
        )
        self.assertNotEqual(counters["final_field_digest"], _sha("field-zero"))

    def test_06_real_neutral_cues_are_read_only_and_both_scans_run(self) -> None:
        events = self.record["execution"]["events"]
        final_memory = self.record["execution"]["counters"]["final_memory_digest"]
        for event in events[1:]:
            self.assertIsNone(event["memory_receipt_digest"])
            self.assertEqual("PRIMARY", event["primary_scan"]["scan_role"])
            self.assertEqual("DIRECT_BASELINE", event["baseline_scan"]["scan_role"])
            for scan in (event["primary_scan"], event["baseline_scan"]):
                self.assertEqual(final_memory, scan["prestate_digest"])
                self.assertEqual(final_memory, scan["poststate_digest"])

    def test_07_scan_hypothesis_is_transparently_carried_once(self) -> None:
        state = _fake_state()
        event = _fake_event("PARTIAL_VISUAL_CUE")
        adapters = _FakeAdapters(hypothesis=True)
        owner = stream.PerceptionEventOwner("s2lo-neutral-fake-owner", state.state_digest, event.event_digest)
        result = adapters.processor().process_once(state=state, event=event, owner=owner)
        self.assertIsNotNone(result.primary_scan.hypothesis)
        self.assertEqual(result.primary_scan.hypothesis_digest, result.primary_scan.hypothesis.hypothesis_digest)
        self.assertEqual(["FIELD", "PRIMARY", "DIRECT_BASELINE"], adapters.calls)

    def test_08_field_failure_does_not_suppress_memory(self) -> None:
        state = _fake_state()
        event = _fake_event("COMPLETE_AV_PERCEPTION")
        adapters = _FakeAdapters(("FIELD",))
        owner = stream.PerceptionEventOwner("s2lo-neutral-fake-owner", state.state_digest, event.event_digest)
        result = adapters.processor().process_once(state=state, event=event, owner=owner)
        self.assertEqual(["FIELD", "MEMORY"], adapters.calls)
        self.assertEqual(state.field_state_digest, result.poststate.field_state_digest)
        self.assertNotEqual(state.memory_state_digest, result.poststate.memory_state_digest)

    def test_09_memory_or_scan_failure_does_not_rollback_field(self) -> None:
        for event_type, failure in (
            ("COMPLETE_AV_PERCEPTION", "MEMORY"),
            ("PARTIAL_AUDITORY_CUE", "PRIMARY"),
        ):
            state = _fake_state()
            event = _fake_event(event_type)
            adapters = _FakeAdapters((failure,))
            owner = stream.PerceptionEventOwner("s2lo-neutral-fake-owner", state.state_digest, event.event_digest)
            result = adapters.processor().process_once(state=state, event=event, owner=owner)
            self.assertNotEqual(state.field_state_digest, result.poststate.field_state_digest)
            if event_type != "COMPLETE_AV_PERCEPTION":
                self.assertEqual(state.memory_state_digest, result.poststate.memory_state_digest)

    def test_10_main_gate_is_closed_without_output(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            with self.assertRaises(runner.S2LOError):
                runner.run_main_once(workspace_root=ROOT, output_root=root, run_id=runner.AUTHORIZED_RUN_ID)
            self.assertEqual([], list(root.iterdir()))

    def test_11_atomic_result_is_written_once_and_verifies_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            result_path = runner.write_result_once(root, "s2lo-neutral-qualification", self.record)
            before = hashlib.sha256(result_path.read_bytes()).hexdigest()
            result = verifier.verify_result_file(result_path, ROOT, expected_mode="QUALIFICATION")
            after = hashlib.sha256(result_path.read_bytes()).hexdigest()
            self.assertEqual("RECORDING_COMPLETE", result["verification_status"])
            self.assertEqual(before, after)
            with self.assertRaises(FileExistsError):
                runner.write_result_once(root, "s2lo-neutral-qualification", self.record)

    def test_12_verifier_rejects_tampering_and_raw_payload_keys(self) -> None:
        for mutation in ("digest", "raw"):
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                changed = json.loads(json.dumps(self.record))
                if mutation == "digest":
                    changed["execution"]["events"][0]["source_digest"] = _sha("changed")
                else:
                    changed["execution"]["raw_bytes"] = [1]
                changed_payload = dict(changed)
                changed_payload.pop("record_digest", None)
                changed["record_digest"] = runner._digest(changed_payload)
                run_dir = root / f"s2lo-neutral-{mutation}"
                run_dir.mkdir()
                path = run_dir / "result.json"
                path.write_bytes(runner._canonical_bytes(changed, newline=True))
                with self.assertRaises(verifier.S2LOVerificationError):
                    verifier.verify_result_file(path, ROOT, expected_mode="QUALIFICATION")


if __name__ == "__main__":
    unittest.main()
