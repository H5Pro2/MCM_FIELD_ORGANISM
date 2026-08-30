"""One-shot neutral S2-GV qualification for the private S2-GT run envelope."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from tools import _s2fs_b4_tspm1_private_coordinator as coordinator
from tools import _s2gb_private_perceptual_context_bundle as context_bundle
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_direct_mask_fill_baseline as direct_baseline
from tools import _s2gk_private_masked_visual_completion_evaluator as evaluator
from tools import _s2gk_private_masked_visual_context_consumer as consumer
from tools import _s2gt_private_append_only_recorder as recording
from tools import _s2gt_private_fixture_registry as fixtures
from tools import _s2gt_private_result_verifier as verifier
from tools import _s2gt_private_runner as runner


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2gv-private-run-envelope-qualification-20260830-01"


class _GenericPathLike(os.PathLike[str]):
    def __init__(self, value: str) -> None:
        self.value = value

    def __fspath__(self) -> str:
        return self.value


def _plan(run_id: str) -> tuple[recording.ExecutionPlan, fixtures.RegistryBundle]:
    return runner.materialize_execution_plan(
        WORKSPACE_ROOT,
        run_id,
        "s2gv-neutral-owner",
    )


def _reserve(root: Path, run_id: str) -> recording.AppendOnlyRunRecorder:
    plan, registry = _plan(run_id)
    result = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
    if type(result) is recording.StartBlocked:
        raise AssertionError("neutral reservation was unexpectedly blocked")
    return result


def _complete_neutral_recorder(root: Path, run_id: str) -> recording.AppendOnlyRunRecorder:
    recorder = _reserve(root, run_id)
    while recorder.next_operation_index <= fixtures.SUCCESS_OPERATION_COUNT:
        row = recorder._row()
        operation_id = row["operation_id"]
        recorder.start(
            operation_id,
            {
                "qualification_id": QUALIFICATION_ID,
                "neutral_operation": operation_id,
            },
        )
        recorder.finish(
            operation_id,
            {
                "qualification_id": QUALIFICATION_ID,
                "neutral_result": operation_id,
            },
        )
    return recorder


def _complete_neutral(root: Path, run_id: str) -> Path:
    return _complete_neutral_recorder(root, run_id).run_directory


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class S2GVPrivateRunEnvelopeQualification(unittest.TestCase):
    def test_01_main_gate_closed_and_run_rejected(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        with self.assertRaisesRegex(runner.S2GTRunnerError, "not authorized"):
            runner.run_main_once(
                WORKSPACE_ROOT,
                WORKSPACE_ROOT,
                "s2gv-rejected-main-run",
                "s2gv-neutral-owner",
                runner.build_evaluation_plan_seal(),
            )

    def test_02_registry_counts_are_exact(self) -> None:
        registry = fixtures.load_bound_registries(WORKSPACE_ROOT)
        self.assertEqual(len(registry.operation_rows), 139)
        self.assertEqual(fixtures.SUCCESS_EVENT_COUNT, 278)
        self.assertEqual(len(registry.failure_path_rows), 140)
        self.assertEqual(len(registry.error_code_rows), 16)

    def test_03_windows_path_subclasses_are_accepted(self) -> None:
        self.assertIsInstance(WORKSPACE_ROOT, Path)
        registry = fixtures.load_bound_registries(WORKSPACE_ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan, _ = _plan("s2gv-windows-path")
            recorder = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
            self.assertIsInstance(recorder, recording.AppendOnlyRunRecorder)
            finding = verifier.verify_run_read_only(WORKSPACE_ROOT, recorder.run_directory)
            self.assertNotIn("absolute pathlib.Path inputs required", finding.errors)

    def test_04_string_and_generic_pathlike_are_rejected(self) -> None:
        with self.assertRaises(fixtures.S2GTRegistryError):
            fixtures.load_bound_registries(str(WORKSPACE_ROOT))  # type: ignore[arg-type]
        generic = _GenericPathLike(str(WORKSPACE_ROOT))
        with self.assertRaises(fixtures.S2GTRegistryError):
            fixtures.load_bound_registries(generic)  # type: ignore[arg-type]
        plan, registry = _plan("s2gv-pathlike-reject")
        self.assertIsInstance(recording.AppendOnlyRunRecorder.reserve(str(WORKSPACE_ROOT), plan, registry), recording.StartBlocked)  # type: ignore[arg-type]
        self.assertIsInstance(recording.AppendOnlyRunRecorder.reserve(generic, plan, registry), recording.StartBlocked)  # type: ignore[arg-type]
        finding = verifier.verify_run_read_only(str(WORKSPACE_ROOT), str(WORKSPACE_ROOT))  # type: ignore[arg-type]
        self.assertEqual(finding.status, "NOT_EVALUABLE")

    def test_05_start_blocked_creates_no_run_directory(self) -> None:
        plan, registry = _plan("s2gv-relative-block")
        relative = Path("s2gv-relative-output-must-not-exist")
        self.assertFalse(relative.exists())
        finding = recording.AppendOnlyRunRecorder.reserve(relative, plan, registry)
        self.assertIsInstance(finding, recording.StartBlocked)
        self.assertFalse(relative.exists())

    def test_06_exclusive_reservation_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            recorder = _reserve(Path(temporary), "s2gv-exclusive-reservation")
            self.assertEqual(recorder.state, "ACTIVE")
            self.assertEqual(recorder.next_operation_index, 2)
            self.assertEqual(recorder.event_count, 2)
            self.assertTrue((recorder.run_directory / "manifest.json").is_file())
            self.assertTrue((recorder.run_directory / "reservation.json").is_file())

    def test_07_registry_order_and_event_pairing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            recorder = _reserve(Path(temporary), "s2gv-order-pairing")
            with self.assertRaises(recording.S2GTRecordingError):
                recorder.start("op-0003", {})
            recorder.start("op-0002", {"neutral": True})
            recorder.finish("op-0002", {"neutral": True})
            events = [json.loads(line) for line in (recorder.run_directory / "journal/operations.jsonl").read_text(encoding="ascii").splitlines()]
            self.assertEqual([(item["operation_id"], item["phase"]) for item in events], [("op-0001", "START"), ("op-0001", "RESULT"), ("op-0002", "START"), ("op-0002", "RESULT")])

    def test_08_reuse_and_overwrite_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plan, registry = _plan("s2gv-no-reuse")
            first = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
            self.assertIsInstance(first, recording.AppendOnlyRunRecorder)
            manifest_digest = _sha256(first.run_directory / "manifest.json")
            second = recording.AppendOnlyRunRecorder.reserve(root, plan, registry)
            self.assertIsInstance(second, recording.StartBlocked)
            self.assertEqual(_sha256(first.run_directory / "manifest.json"), manifest_digest)

    def test_09_complete_neutral_139_operation_recording(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _complete_neutral(Path(temporary), "s2gv-neutral-complete")
            events = (directory / "journal/operations.jsonl").read_text(encoding="ascii").splitlines()
            self.assertEqual(len(events), 278)
            self.assertTrue((directory / "terminal/complete/COMPLETE").is_file())

    def test_10_independent_verifier_accepts_complete_recording(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _complete_neutral(Path(temporary), "s2gv-verifier-complete")
            finding = verifier.verify_run_read_only(WORKSPACE_ROOT, directory)
            self.assertEqual(finding.status, "RECORDING_COMPLETE")
            self.assertEqual((finding.operation_count, finding.event_count), (139, 278))
            self.assertEqual(finding.errors, ())

    def test_11_journal_manipulation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _complete_neutral(Path(temporary), "s2gv-tamper-journal")
            journal = directory / "journal/operations.jsonl"
            journal.write_bytes(journal.read_bytes() + b"{}\n")
            self.assertEqual(verifier.verify_run_read_only(WORKSPACE_ROOT, directory).status, "NOT_EVALUABLE")

    def test_12_artifact_manipulation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _complete_neutral(Path(temporary), "s2gv-tamper-artifact")
            artifact = directory / "receipts/op-0002.json"
            artifact.write_bytes(artifact.read_bytes() + b" ")
            self.assertEqual(verifier.verify_run_read_only(WORKSPACE_ROOT, directory).status, "NOT_EVALUABLE")

    def test_13_manifest_manipulation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _complete_neutral(Path(temporary), "s2gv-tamper-manifest")
            manifest = directory / "manifest.json"
            payload = json.loads(manifest.read_text(encoding="ascii"))
            payload["operation_count"] = 138
            manifest.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="ascii")
            self.assertEqual(verifier.verify_run_read_only(WORKSPACE_ROOT, directory).status, "NOT_EVALUABLE")

    def test_14_reservation_manipulation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _complete_neutral(Path(temporary), "s2gv-tamper-reservation")
            reservation = directory / "reservation.json"
            payload = json.loads(reservation.read_text(encoding="ascii"))
            payload["owner_id"] = "s2gv-foreign-owner"
            reservation.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="ascii")
            self.assertEqual(verifier.verify_run_read_only(WORKSPACE_ROOT, directory).status, "NOT_EVALUABLE")

    def test_15_terminal_manipulation_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = _complete_neutral(Path(temporary), "s2gv-tamper-terminal")
            (directory / "terminal/complete/COMPLETE").unlink()
            self.assertEqual(verifier.verify_run_read_only(WORKSPACE_ROOT, directory).status, "NOT_EVALUABLE")

    def test_16_one_neutral_failure_path_closes_not_evaluable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            recorder = _reserve(Path(temporary), "s2gv-neutral-failure")
            recorder.start("op-0002", {"neutral": True})
            recorder.fail("E009", "op-0002")
            self.assertEqual(recorder.state, "NOT_EVALUABLE")
            self.assertEqual(recorder.event_count, 10)
            self.assertTrue((recorder.run_directory / "terminal/failure/NOT_EVALUABLE").is_file())

    def test_17_terminal_completion_blocks_further_operations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            recorder = _complete_neutral_recorder(Path(temporary), "s2gv-terminal-block")
            self.assertTrue((recorder.run_directory / "terminal/complete/COMPLETE").is_file())
            with self.assertRaisesRegex(recording.S2GTRecordingError, "E014"):
                recorder.start("op-0139", {"forbidden": True})

    def test_18_resource_limit_excess_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            recorder = _reserve(Path(temporary), "s2gv-resource-limit")
            recorder.start("op-0002", {"neutral": True})
            with self.assertRaisesRegex(recording.S2GTRecordingError, "E008"):
                recorder.finish("op-0002", {"oversized": "x" * 5_000})
            recorder.fail("E008", "op-0002")
            self.assertEqual(recorder.state, "NOT_EVALUABLE")

    def test_19_small_real_receptor_and_formation_path(self) -> None:
        runtime = runner._runtime()
        prestate = coordinator.initial_composite_state(runtime.coordinator_config)
        source = runner._analyze(runtime, "s2gv.neutral.source.01", "A1", "Q1", 0, 1, "FORMATION")
        result = runner._formation(runtime, prestate, source, "neutral.01")
        self.assertEqual(result.poststate.generation, 1)
        self.assertNotEqual(result.poststate.state_digest, prestate.state_digest)

    def test_20_read_only_projection_consumer_baseline_and_evaluator(self) -> None:
        runtime = runner._runtime()
        prestate = coordinator.initial_composite_state(runtime.coordinator_config)
        formation = runner._analyze(runtime, "s2gv.neutral.source.02", "A1", "Q1", 0, 1, "FORMATION")
        state = runner._formation(runtime, prestate, formation, "neutral.02").poststate
        probe_source = runner._analyze(runtime, "s2gv.neutral.probe.01", "A2", "Q2", 1, 2, "READ_ONLY")
        before = state.state_digest
        finding = runner._probe(runtime, state, probe_source)
        binding = runner._projection_binding(runtime, state, probe_source)
        sequence = context_bundle.ValidatedB4ShortSequenceEvidence.build("NOT_REQUESTED", finding.b4_recent.observed_state_digest, finding.probe_digest)
        bundle = context_bundle.project_perceptual_context_bundle(binding, finding, sequence)
        projection = two_area.project_two_area_context(bundle)
        masked = runner._masked_probe(probe_source)
        current = consumer.current_perception_only(masked)
        use_binding = consumer.ContextUseBinding.build(masked, projection)
        completed = consumer.complete_with_named_b_stable(masked, projection, use_binding)
        direct = direct_baseline.direct_b_stable_mask_fill(masked, projection, use_binding)
        target = evaluator.MaskedVisualTargetFixture.build(fixtures.VISUAL_BY_ID["A2"].values)
        evaluation = evaluator.evaluate_completion_case("ABSENT_CONTEXT", target, current, completed, direct)
        self.assertEqual(evaluation.status, "S2GJ_CONTROL_VALID")
        self.assertEqual(state.state_digest, before)
        self.assertEqual((finding.prestate_digest, finding.poststate_digest), (before, before))
        self.assertEqual((projection.prestate_digest, projection.poststate_digest), (before, before))


if __name__ == "__main__":
    unittest.main()
