"""One-shot neutral qualification of S2-IN lifecycle and current S2-IC/ParentSetV1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from tests import test_s2id_private_two_area_conflict_signal as s2id
from tests import test_s2ih_joint_qualification as s2ih
from tests import test_s2il_joint_qualification as s2il
from tools import _s2ig_private_append_only_recorder as recording
from tools import _s2ig_private_fixture_registry as fixtures
from tools import _s2ig_private_result_verifier as verifier
from tools import _s2ig_private_runner as runner


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2io-joint-qualification-20260901-01"


def _neutral_result(index: int, operation_id: str) -> dict[str, object]:
    return {
        "schema": "s2io.neutral-artifact.v1",
        "operation_id": operation_id,
        "neutral_qualification": True,
        "ordinal": index,
    }


def _complete_neutral_recording(output_root: Path, run_id: str) -> Path:
    plan, registry = runner.materialize_execution_plan(
        WORKSPACE_ROOT, run_id, f"{run_id}-owner"
    )
    reserved = recording.AppendOnlyRunRecorder.reserve(output_root, plan, registry)
    if type(reserved) is not recording.AppendOnlyRunRecorder:
        raise AssertionError("neutral qualification reservation was rejected")
    recorder = reserved
    if (
        recorder.state != "ACTIVE"
        or recorder.next_operation_index != 3
        or recorder.event_count != 4
    ):
        raise AssertionError("atomic bootstrap did not publish an active recorder")
    evaluation_root = verifier.expected_evaluation_root(WORKSPACE_ROOT)
    expected = dict(verifier.EXPECTED_STATUSES)
    case_evidence_ops = {
        121 + 7 * index: case_id
        for index, (case_id, _) in enumerate(verifier.EXPECTED_STATUSES)
    }
    evaluation_ops = {
        173 + index: case_id
        for index, (case_id, _) in enumerate(verifier.EXPECTED_STATUSES)
    }
    observed: dict[str, str] = {}
    for index in range(3, fixtures.SUCCESS_OPERATION_COUNT + 1):
        row = recorder.current_row()
        external = evaluation_root["seal_digest"] if index == 172 else None
        recorder.start(
            row.operation_id,
            {"neutral_qualification": True, "ordinal": index},
            external_parent_digest=external,
        )
        result = _neutral_result(index, row.operation_id)
        if index in case_evidence_ops:
            case_id = case_evidence_ops[index]
            status = expected[case_id]
            context_digest = s2id._digest(f"{case_id}-context-probe")
            signal_digest = s2id._digest(f"{case_id}-signal-probe")
            observed[case_id] = status
            result = {
                "schema": "s2if.case-evidence.v1",
                "case_id": case_id,
                "context_function_probe_digest": context_digest,
                "masked_visual_probe_digest": signal_digest,
                "bundle_context_probe_digest": context_digest,
                "signal_status": status,
                "baseline_status": status,
                "read_only": True,
            }
        elif index == 171:
            result = {
                "schema": "s2ie.execution-evidence-package.v1",
                "execution_plan_digest": plan.plan_digest,
                "evaluation_plan_digest": None,
            }
        elif index == 172:
            result = {
                "schema": "s2ie.evaluation-run-binding.v1",
                "evaluation_plan_digest": evaluation_root["seal_digest"],
            }
        elif index in evaluation_ops:
            case_id = evaluation_ops[index]
            status = observed[case_id]
            result = {
                "schema": "s2ie.evaluation-finding.v1",
                "case_id": case_id,
                "expected_status": expected[case_id],
                "observed_status": status,
                "status_matches": status == expected[case_id],
            }
        elif index == 183:
            result = {
                "schema": "s2ie.completion-marker.v1",
                "status": "COMPLETE",
                "operation_count": fixtures.SUCCESS_OPERATION_COUNT,
                "event_count": fixtures.SUCCESS_EVENT_COUNT,
            }
        recorder.finish(row.operation_id, {"result": result})
    if recorder.state != "COMPLETE" or recorder.event_count != fixtures.SUCCESS_EVENT_COUNT:
        raise AssertionError("neutral recording did not close completely")
    return recorder.run_directory


def _canonical_write(path: Path, payload: object) -> None:
    path.write_bytes(recording.canonical_bytes(payload))


class S2IOJointQualificationTests(s2il.S2ILJointQualificationTests):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="s2io-")
        cls.root = Path(cls._temporary.name).resolve()
        cls.valid_run = _complete_neutral_recording(
            cls.root, "s2io-neutral-complete-01"
        )

    def test_19_registry_gate_and_complete_neutral_recording_are_valid(self) -> None:
        self.assertEqual((183, 366), (len(fixtures.REGISTRY.rows), fixtures.SUCCESS_EVENT_COUNT))
        runner.MAIN_EXECUTION_ENABLED = False
        with mock.patch.object(runner, "_execute") as execute:
            with self.assertRaises(runner.S2IGRunnerError):
                runner.run_main_once(
                    self.root,
                    WORKSPACE_ROOT,
                    "s2io-gate-closed-01",
                    "s2io-gate-closed-owner",
                    object(),
                )
        execute.assert_not_called()
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, self.valid_run)
        self.assertEqual("RECORDING_COMPLETE", finding.status, finding.errors)
        self.assertEqual((183, 366), (finding.operation_count, finding.event_count))

    def test_21_complete_and_post_bootstrap_not_evaluable_are_exclusive(self) -> None:
        coexist = self._copy_valid("terminal-coexist")
        _canonical_write(
            coexist / "terminal/failure/NOT_EVALUABLE",
            {"status": "NOT_EVALUABLE"},
        )
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, coexist)
        self.assertEqual("NOT_EVALUABLE", finding.status)
        self.assertTrue(any("coexist" in item for item in finding.errors))

        plan, registry = runner.materialize_execution_plan(
            WORKSPACE_ROOT,
            "s2io-neutral-failure-01",
            "s2io-neutral-failure-owner",
        )
        reserved = recording.AppendOnlyRunRecorder.reserve(self.root, plan, registry)
        self.assertIs(type(reserved), recording.AppendOnlyRunRecorder)
        self.assertEqual(("ACTIVE", 3, 4), (
            reserved.state,
            reserved.next_operation_index,
            reserved.event_count,
        ))
        reserved.fail("IG-E002", "ie-op-003")
        self.assertEqual("NOT_EVALUABLE", reserved.state)
        self.assertTrue((reserved.run_directory / "reservation.json").is_file())
        self.assertTrue((reserved.run_directory / "manifest.json").is_file())
        self.assertFalse((reserved.run_directory / "terminal/complete/COMPLETE").exists())
        failure = verifier.verify_run_read_only(WORKSPACE_ROOT, reserved.run_directory)
        self.assertEqual("NOT_EVALUABLE", failure.status)
        self.assertEqual((), failure.errors)
        self.assertEqual((3, 10), (failure.operation_count, failure.event_count))
        self.assertLessEqual(failure.byte_count, recording.EARLIEST_POST_RESERVATION_FAILURE_MAX_BYTES)

    def _assert_start_rejected(
        self,
        output_root: Path,
        plan: recording.ExecutionPlan,
        outcome: recording.AppendOnlyRunRecorder | recording.StartRejected,
    ) -> None:
        self.assertIs(type(outcome), recording.StartRejected)
        payload = outcome.payload()
        finding = verifier.verify_lifecycle_read_only(WORKSPACE_ROOT, output_root, payload)
        self.assertEqual("START_REJECTED", finding.status, finding.errors)
        self.assertEqual((0, 0), (finding.operation_count, finding.event_count))
        self.assertFalse(payload["publication_performed"])
        self.assertIsNone(payload["reservation_digest"])
        if payload["target_preexisted"] is False:
            self.assertFalse((output_root / plan.run_id).exists())

    def test_30_each_bootstrap_partial_failure_is_start_rejected(self) -> None:
        def materialize(case: str) -> tuple[Path, recording.ExecutionPlan, fixtures.RegistryBundle]:
            root = (self.root / f"bootstrap-{case}").resolve()
            root.mkdir()
            plan, registry = runner.materialize_execution_plan(
                WORKSPACE_ROOT, f"s2io-bootstrap-{case}", f"s2io-bootstrap-{case}-owner"
            )
            return root, plan, registry

        root, plan, registry = materialize("invalid-path")
        outcome = recording.AppendOnlyRunRecorder.reserve("not-a-path", plan, registry)  # type: ignore[arg-type]
        self._assert_start_rejected(root, plan, outcome)

        root, plan, registry = materialize("target-exists")
        (root / plan.run_id).mkdir()
        outcome = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
        self._assert_start_rejected(root, plan, outcome)

        root, plan, registry = materialize("staging-exists")
        staging = root / ".s2im-bootstrap" / f"{plan.run_id}.{plan.plan_digest[:16]}.pending"
        staging.mkdir(parents=True)
        outcome = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
        self._assert_start_rejected(root, plan, outcome)

        root, plan, registry = materialize("directory")
        original_mkdir = Path.mkdir

        def fail_journal(path: Path, *args: object, **kwargs: object) -> None:
            if path.name == "journal":
                raise PermissionError("neutral injected bootstrap directory failure")
            original_mkdir(path, *args, **kwargs)

        with mock.patch.object(Path, "mkdir", new=fail_journal):
            outcome = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
        self._assert_start_rejected(root, plan, outcome)

        for method_name, fail_call in (("start", 1), ("finish", 1), ("start", 2), ("finish", 2)):
            case = f"{method_name}-{fail_call}"
            root, plan, registry = materialize(case)
            original = getattr(recording.AppendOnlyRunRecorder, method_name)
            calls = 0

            def injected(instance: recording.AppendOnlyRunRecorder, *args: object, **kwargs: object) -> object:
                nonlocal calls
                calls += 1
                if calls == fail_call:
                    raise recording.S2IGRecordingError("IG-E010", "neutral injected bootstrap failure")
                return original(instance, *args, **kwargs)

            with mock.patch.object(recording.AppendOnlyRunRecorder, method_name, new=injected):
                outcome = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
            self._assert_start_rejected(root, plan, outcome)

        root, plan, registry = materialize("publish")
        with mock.patch.object(Path, "rename", side_effect=PermissionError("neutral publish failure")):
            outcome = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
        self._assert_start_rejected(root, plan, outcome)

    def test_31_full_bootstrap_is_atomic_bounded_and_activates_at_operation_three(self) -> None:
        root = (self.root / "bootstrap-complete").resolve()
        root.mkdir()
        plan, registry = runner.materialize_execution_plan(
            WORKSPACE_ROOT, "s2io-bootstrap-complete", "s2io-bootstrap-complete-owner"
        )
        outcome = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
        self.assertIs(type(outcome), recording.AppendOnlyRunRecorder)
        recorder = outcome
        self.assertEqual(("ACTIVE", 3, 4), (
            recorder.state,
            recorder.next_operation_index,
            recorder.event_count,
        ))
        self.assertTrue((recorder.run_directory / "reservation.json").is_file())
        self.assertTrue((recorder.run_directory / "manifest.json").is_file())
        events = tuple(
            json.loads(line)
            for line in (recorder.run_directory / "journal/operations.jsonl")
            .read_text(encoding="ascii")
            .splitlines()
        )
        self.assertEqual(
            ("ie-op-001", "ie-op-001", "ie-op-002", "ie-op-002"),
            tuple(item["operation_id"] for item in events),
        )
        prior = "0" * 64
        for index, event in enumerate(events, 1):
            self.assertEqual(index, event["event_index"])
            self.assertEqual(prior, event["previous_event_digest"])
            prior = event["event_digest"]
        bootstrap_bytes = sum(
            path.stat().st_size
            for path in (
                recorder.run_directory / "reservation.json",
                recorder.run_directory / "manifest.json",
                recorder.run_directory / "journal/operations.jsonl",
            )
        )
        self.assertEqual(recorder.byte_count, bootstrap_bytes)
        self.assertLessEqual(bootstrap_bytes, recording.ATOMIC_BOOTSTRAP_MAX_BYTES)

    def test_32_start_rejected_lifecycle_mutations_are_invalid(self) -> None:
        root = (self.root / "lifecycle-invalid").resolve()
        root.mkdir()
        plan, registry = runner.materialize_execution_plan(
            WORKSPACE_ROOT, "s2io-lifecycle-invalid", "s2io-lifecycle-invalid-owner"
        )
        (root / plan.run_id).mkdir()
        outcome = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
        self.assertIs(type(outcome), recording.StartRejected)
        payload = outcome.payload()
        changed = dict(payload)
        changed["publication_performed"] = True
        self.assertEqual(
            "LIFECYCLE_INVALID",
            verifier.verify_lifecycle_read_only(WORKSPACE_ROOT, root, changed).status,
        )
        self.assertEqual(
            "LIFECYCLE_INVALID",
            verifier.verify_lifecycle_read_only(WORKSPACE_ROOT, root, object()).status,
        )

    def test_33_append_only_reuse_is_rejected_without_changing_complete_run(self) -> None:
        before = {
            str(path.relative_to(self.valid_run)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.valid_run.rglob("*")
            if path.is_file()
        }
        plan, registry = runner.materialize_execution_plan(
            WORKSPACE_ROOT,
            "s2io-neutral-complete-01",
            "s2io-neutral-complete-01-owner",
        )
        outcome = recording.AppendOnlyRunRecorder.reserve(self.root, plan, registry)
        self.assertIs(type(outcome), recording.StartRejected)
        self.assertTrue(outcome.target_preexisted)
        after = {
            str(path.relative_to(self.valid_run)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.valid_run.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_34_lifecycle_bounds_and_registry_remain_exact(self) -> None:
        self.assertEqual(11_264, recording.ATOMIC_BOOTSTRAP_MAX_BYTES)
        self.assertEqual(22_528, recording.EARLIEST_POST_RESERVATION_FAILURE_MAX_BYTES)
        self.assertEqual(recording.ATOMIC_BOOTSTRAP_MAX_BYTES, verifier.ATOMIC_BOOTSTRAP_MAX_BYTES)
        self.assertEqual(
            recording.EARLIEST_POST_RESERVATION_FAILURE_MAX_BYTES,
            verifier.EARLIEST_POST_RESERVATION_FAILURE_MAX_BYTES,
        )
        self.assertEqual((183, 366), (len(fixtures.REGISTRY.rows), fixtures.SUCCESS_EVENT_COUNT))
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(s2id.S2IDPrivateTwoAreaConflictSignalTests))
    suite.addTests(loader.loadTestsFromTestCase(S2IOJointQualificationTests))
    return suite


if __name__ == "__main__":
    unittest.main()
