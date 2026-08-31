"""One-shot neutral qualification for the private S2-HU run envelope."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from tools import _s2hu_private_append_only_recorder as recording
from tools import _s2hu_private_fixture_registry as fixtures
from tools import _s2hu_private_result_verifier as verifier
from tools import _s2hu_private_runner as runner


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2hv-neutral-qualification-20260831-01"


def _expected_output(case_id: str) -> tuple[float, ...]:
    return dict(verifier.EXPECTED_CASE_VALUES)[case_id]


def _neutral_result(index: int, operation_id: str) -> dict[str, object]:
    return {
        "schema": "s2hv.neutral-artifact.v1",
        "operation_id": operation_id,
        "neutral_qualification": True,
        "ordinal": index,
    }


def _complete_neutral_recording(output_root: Path, run_id: str) -> Path:
    plan, registry = runner.materialize_execution_plan(
        WORKSPACE_ROOT, run_id, f"{run_id}-owner"
    )
    reserved = recording.AppendOnlyRunRecorder.reserve(output_root, plan, registry)
    if type(reserved) is recording.StartBlocked:
        raise AssertionError("neutral qualification reservation was blocked")
    recorder = reserved
    evaluation_root = verifier.expected_evaluation_root(WORKSPACE_ROOT)
    expected = dict(verifier.EXPECTED_CASE_VALUES)
    case_by_operation = {
        39: "c01",
        43: "c02",
        47: "c03",
        51: "c04",
    }
    evaluation_by_operation = {
        54: "c01",
        55: "c02",
        56: "c03",
        57: "c04",
    }
    case_evidence: dict[str, dict[str, object]] = {}
    for index in range(2, 61):
        row = recorder.current_row()
        external = evaluation_root["seal_digest"] if index == 53 else None
        recorder.start(
            row.operation_id,
            {"neutral_qualification": True, "ordinal": index},
            external_parent_digest=external,
        )
        result = _neutral_result(index, row.operation_id)
        if index == 2:
            result = {
                "execution_plan": plan.payload(),
                "registry_source_digest": registry.source_digest,
                "registry_bundle_digest": registry.bundle_digest,
                "execution_fixture_digest": fixtures.EXECUTION_FIXTURE_DIGEST,
            }
        elif index in (16, 32):
            state_digest = fixtures.canonical_digest(["neutral-state", index])
            result = {
                **result,
                "prestate_digest": state_digest,
                "poststate_digest": state_digest,
            }
        elif index in case_by_operation:
            case_id = case_by_operation[index]
            output = expected[case_id]
            result = {
                "schema": "s2hu.case-evidence.v1",
                "case_id": case_id,
                "consumer_output": output,
                "baseline_output": output,
                "consumer_read_only": True,
                "baseline_read_only": True,
            }
            case_evidence[case_id] = result
        elif index in (37, 38, 41, 42, 45, 46, 49, 50):
            state_digest = fixtures.canonical_digest(["neutral-arm-state", index])
            result = {
                **result,
                "prestate_digest": state_digest,
                "poststate_digest": state_digest,
            }
        elif index == 52:
            result = {
                "schema": "s2hu.execution-evidence-package.v1",
                "execution_plan_digest": plan.plan_digest,
                "evaluation_plan_digest": None,
            }
        elif index == 53:
            result = {
                "schema": "s2hu.evaluation-run-binding.v1",
                "evaluation_plan_digest": evaluation_root["seal_digest"],
                "binding_digest": fixtures.canonical_digest(
                    ["neutral-evaluation", evaluation_root["seal_digest"]]
                ),
            }
        elif index in evaluation_by_operation:
            case_id = evaluation_by_operation[index]
            output = tuple(case_evidence[case_id]["consumer_output"])
            result = {
                "schema": "s2hu.evaluation-finding.v1",
                "case_id": case_id,
                "expected_values_digest": fixtures.canonical_digest(
                    list(expected[case_id])
                ),
                "consumer_matches_expected": output == expected[case_id],
                "baseline_matches_expected": output == expected[case_id],
                "consumer_equals_baseline": True,
                "visible_values_unchanged": True,
                "read_only": True,
            }
        elif index == 58:
            result = {
                "schema": "s2hu.aggregate-finding.v1",
                "all_expected": True,
                "baseline_explains": True,
                "all_read_only": True,
            }
        elif index == 59:
            result = {
                "schema": "s2hu.terminal-finding.v1",
                "status": "COMPLETING",
                "functional_status": "NEUTRAL_QUALIFICATION_ONLY",
            }
        elif index == 60:
            result = {
                "schema": "s2hu.completion-marker.v1",
                "status": "COMPLETE",
                "operation_count": 60,
                "event_count": 120,
            }
        recorder.finish(row.operation_id, {"result": result})
    if recorder.state != "COMPLETE" or recorder.event_count != 120:
        raise AssertionError("neutral recording did not close completely")
    return recorder.run_directory


def _canonical_write(path: Path, payload: object) -> None:
    encoded = recording.canonical_bytes(payload)
    path.write_bytes(encoded)


class _ForeignPathLike(os.PathLike[str]):
    def __init__(self, path: Path) -> None:
        self._path = path

    def __fspath__(self) -> str:
        return str(self._path)


class S2HVNeutralTechnicalQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="s2hv-")
        cls.root = Path(cls._temporary.name).resolve()
        cls.valid_run = _complete_neutral_recording(
            cls.root, "s2hv-neutral-complete-01"
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def _copy_valid(self, suffix: str) -> Path:
        target = self.root / f"copy-{suffix}"
        shutil.copytree(self.valid_run, target)
        return target

    def test_01_registry_is_exactly_sixty_operations_and_120_events(self) -> None:
        registry = fixtures.load_operation_registry(WORKSPACE_ROOT)
        self.assertEqual(60, len(registry.rows))
        self.assertEqual(
            tuple(f"hs-op-{index:03d}" for index in range(1, 61)),
            tuple(row.operation_id for row in registry.rows),
        )
        self.assertEqual(120, 2 * len(registry.rows))

    def test_02_closed_runner_gate_blocks_main_without_execution(self) -> None:
        runner.MAIN_EXECUTION_ENABLED = False
        with mock.patch.object(runner, "_execute") as execute:
            with self.assertRaises(runner.S2HURunnerError):
                runner.run_main_once(
                    self.root,
                    WORKSPACE_ROOT,
                    "s2hv-gate-closed-01",
                    "s2hv-gate-closed-owner",
                    object(),
                )
        execute.assert_not_called()
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)

    def test_03_gate_returns_to_false_on_invalid_opened_boundary(self) -> None:
        runner.MAIN_EXECUTION_ENABLED = True
        with mock.patch.object(runner, "_execute") as execute:
            with self.assertRaises(runner.S2HURunnerError):
                runner.run_main_once(
                    "not-a-path",  # type: ignore[arg-type]
                    WORKSPACE_ROOT,
                    "s2hv-gate-invalid-01",
                    "s2hv-gate-invalid-owner",
                    object(),
                )
        execute.assert_not_called()
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)

    def test_04_windows_path_owner_and_source_bindings_are_strict(self) -> None:
        plan, registry = runner.materialize_execution_plan(
            WORKSPACE_ROOT,
            "s2hv-path-valid-01",
            "s2hv-path-valid-owner",
        )
        self.assertIsInstance(self.root, Path)
        accepted = recording.AppendOnlyRunRecorder.reserve(self.root, plan, registry)
        self.assertIs(type(accepted), recording.AppendOnlyRunRecorder)
        blocked_string = recording.AppendOnlyRunRecorder.reserve(  # type: ignore[arg-type]
            str(self.root), plan, registry
        )
        blocked_foreign = recording.AppendOnlyRunRecorder.reserve(  # type: ignore[arg-type]
            _ForeignPathLike(self.root), plan, registry
        )
        self.assertIs(type(blocked_string), recording.StartBlocked)
        self.assertIs(type(blocked_foreign), recording.StartBlocked)
        with self.assertRaises(recording.S2HURecordingError):
            recording.ExecutionPlan.build(
                "s2hv-owner-invalid-01",
                "INVALID OWNER",
                registry,
                plan.source_digests,
            )

    def test_05_append_only_complete_record_has_paired_events_and_marker(self) -> None:
        lines = (self.valid_run / "journal/operations.jsonl").read_text(
            encoding="ascii"
        ).splitlines()
        events = tuple(json.loads(line) for line in lines)
        self.assertEqual(120, len(events))
        self.assertEqual(
            tuple("START" if index % 2 == 0 else "RESULT" for index in range(120)),
            tuple(event["phase"] for event in events),
        )
        marker = json.loads(
            (self.valid_run / "terminal/complete/COMPLETE").read_text(
                encoding="ascii"
            )
        )
        self.assertEqual("COMPLETE", marker["artifact"]["result"]["status"])

    def test_06_independent_verifier_accepts_neutral_complete_recording(self) -> None:
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, self.valid_run)
        self.assertEqual("RECORDING_COMPLETE", finding.status, finding.errors)
        self.assertEqual((60, 120), (finding.operation_count, finding.event_count))

    def test_07_missing_receipt_is_rejected(self) -> None:
        target = self._copy_valid("missing")
        (target / "receipts/hs-op-010.json").unlink()
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, target)
        self.assertEqual("NOT_EVALUABLE", finding.status)
        self.assertTrue(any("missing" in item for item in finding.errors))

    def test_08_swapped_receipts_are_rejected(self) -> None:
        target = self._copy_valid("swapped")
        first = target / "receipts/hs-op-010.json"
        second = target / "receipts/hs-op-011.json"
        first_bytes, second_bytes = first.read_bytes(), second.read_bytes()
        first.write_bytes(second_bytes)
        second.write_bytes(first_bytes)
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, target)
        self.assertEqual("NOT_EVALUABLE", finding.status)
        self.assertTrue(any("binding differs" in item for item in finding.errors))

    def test_09_manipulated_receipt_digest_is_rejected(self) -> None:
        target = self._copy_valid("digest")
        path = target / "receipts/hs-op-012.json"
        payload = json.loads(path.read_text(encoding="ascii"))
        payload["artifact"]["result"]["ordinal"] = 999
        _canonical_write(path, payload)
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, target)
        self.assertEqual("NOT_EVALUABLE", finding.status)
        self.assertTrue(any("binding differs" in item for item in finding.errors))

    def test_10_execution_and_evaluation_roots_first_join_at_operation_53(self) -> None:
        execution = json.loads(
            (self.valid_run / "evidence/execution.json").read_text(encoding="ascii")
        )["artifact"]["result"]
        evaluation = json.loads(
            (self.valid_run / "evaluation/binding.json").read_text(encoding="ascii")
        )["artifact"]["result"]
        self.assertIsNone(execution["evaluation_plan_digest"])
        self.assertEqual(
            verifier.expected_evaluation_root(WORKSPACE_ROOT)["seal_digest"],
            evaluation["evaluation_plan_digest"],
        )

    def test_11_complete_and_not_evaluable_are_exclusive(self) -> None:
        target = self._copy_valid("exclusive")
        failure = target / "terminal/failure/NOT_EVALUABLE"
        _canonical_write(failure, {"status": "NOT_EVALUABLE"})
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, target)
        self.assertEqual("NOT_EVALUABLE", finding.status)
        self.assertTrue(any("coexist" in item for item in finding.errors))

    def test_12_registered_failure_closes_as_not_evaluable(self) -> None:
        plan, registry = runner.materialize_execution_plan(
            WORKSPACE_ROOT,
            "s2hv-neutral-failure-01",
            "s2hv-neutral-failure-owner",
        )
        reserved = recording.AppendOnlyRunRecorder.reserve(self.root, plan, registry)
        self.assertIs(type(reserved), recording.AppendOnlyRunRecorder)
        reserved.fail("HS-E006", "hs-op-002")
        self.assertEqual("NOT_EVALUABLE", reserved.state)
        self.assertFalse((reserved.run_directory / "terminal/complete/COMPLETE").exists())
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, reserved.run_directory)
        self.assertEqual("NOT_EVALUABLE", finding.status)
        self.assertEqual((), finding.errors)

    def test_13_run_directory_reuse_and_overwrite_are_blocked(self) -> None:
        plan, registry = runner.materialize_execution_plan(
            WORKSPACE_ROOT,
            "s2hv-neutral-reuse-01",
            "s2hv-neutral-reuse-owner",
        )
        first = recording.AppendOnlyRunRecorder.reserve(self.root, plan, registry)
        second = recording.AppendOnlyRunRecorder.reserve(self.root, plan, registry)
        self.assertIs(type(first), recording.AppendOnlyRunRecorder)
        self.assertIs(type(second), recording.StartBlocked)
        row = first.current_row()
        first.start(row.operation_id, {"neutral": True})
        target = first.run_directory / row.target_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("occupied", encoding="ascii")
        with self.assertRaises(recording.S2HURecordingError):
            first.finish(row.operation_id, {"result": {"neutral": True}})

    def test_14_source_digest_and_manifest_manipulation_is_rejected(self) -> None:
        target = self._copy_valid("source")
        path = target / "manifest.json"
        payload = json.loads(path.read_text(encoding="ascii"))
        payload["artifact"]["result"]["execution_plan"]["source_digests"][0][1] = "0" * 64
        _canonical_write(path, payload)
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, target)
        self.assertEqual("NOT_EVALUABLE", finding.status)
        self.assertTrue(any("source digest differs" in item for item in finding.errors))


if __name__ == "__main__":
    unittest.main()
