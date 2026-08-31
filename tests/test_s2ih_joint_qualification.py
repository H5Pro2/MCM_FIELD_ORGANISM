"""One-shot joint qualification of current S2-IC and the S2-IG run envelope."""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from tests import test_s2id_private_two_area_conflict_signal as s2id
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2ig_private_append_only_recorder as recording
from tools import _s2ig_private_fixture_registry as fixtures
from tools import _s2ig_private_result_verifier as verifier
from tools import _s2ig_private_runner as runner


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2ih-joint-qualification-20260831-01"


def _separate_signal_probe(label: str) -> probe_contract.MaskedVisualProbe:
    values = tuple(
        s2id.VISIBLE_VALUE if index in probe_contract.VISIBLE_POSITIONS else None
        for index in range(18)
    )
    return probe_contract.MaskedVisualProbe.build(values, s2id._digest(label))


def _context_wrapper(
    case_plan_digest: str,
    function_probe_digest: str,
) -> runner.ContextRetrievalProbe:
    payload = {
        "schema": "s2if.context-retrieval-probe.v1",
        "case_plan_digest": case_plan_digest,
        "role": "CONTEXT_RETRIEVAL_PROBE",
        "probe_id": "s2ih.context-probe",
        "source_id": "s2ih.context-source",
        "source_digest": s2id._digest("context-source"),
        "receptor_receipt_digest": s2id._digest("context-receipt"),
        "config_digest": s2id._digest("shared-config"),
        "auditory_values_digest": s2id._digest("context-auditory"),
        "visual_values_digest": s2id._digest("context-visual"),
        "av_values_digest": s2id._digest("context-av"),
        "function_probe_digest": function_probe_digest,
        "value_dimension": 26,
        "window_start_tick": 10,
        "window_end_tick": 11,
    }
    return runner.ContextRetrievalProbe(
        case_plan_digest,
        payload["probe_id"],
        payload["source_id"],
        payload["source_digest"],
        payload["receptor_receipt_digest"],
        payload["config_digest"],
        payload["auditory_values_digest"],
        payload["visual_values_digest"],
        payload["av_values_digest"],
        function_probe_digest,
        10,
        11,
        fixtures.canonical_digest(payload),
    )


def _signal_wrapper(
    case_plan_digest: str,
    probe: probe_contract.MaskedVisualProbe,
    *,
    source_suffix: str = "primary",
) -> runner.MaskedSignalProbe:
    payload = {
        "schema": "s2if.masked-signal-probe.v1",
        "case_plan_digest": case_plan_digest,
        "role": "MASKED_SIGNAL_PROBE",
        "probe_id": f"s2ih.signal-probe.{source_suffix}",
        "source_id": f"s2ih.signal-source.{source_suffix}",
        "source_digest": s2id._digest(f"signal-source-{source_suffix}"),
        "receptor_receipt_digest": s2id._digest(f"signal-receipt-{source_suffix}"),
        "config_digest": s2id._digest("shared-config"),
        "visual_values_digest": s2id._digest(f"signal-visual-{source_suffix}"),
        "visible_values_digest": s2id._digest(f"signal-visible-{source_suffix}"),
        "mask_digest": signal_contract.mask_digest_for(probe),
        "masked_visual_probe_digest": probe.probe_digest,
        "visible_positions": fixtures.VISIBLE_POSITIONS,
        "masked_positions": fixtures.MASKED_POSITIONS,
        "value_dimension": 18,
        "window_start_tick": 20,
        "window_end_tick": 21,
    }
    return runner.MaskedSignalProbe(
        case_plan_digest,
        payload["probe_id"],
        payload["source_id"],
        payload["source_digest"],
        payload["receptor_receipt_digest"],
        payload["config_digest"],
        payload["visual_values_digest"],
        payload["visible_values_digest"],
        payload["mask_digest"],
        probe.probe_digest,
        fixtures.VISIBLE_POSITIONS,
        fixtures.MASKED_POSITIONS,
        20,
        21,
        fixtures.canonical_digest(payload),
    )


def _dual_fixture() -> tuple[object, ...]:
    context_probe = s2id._probe()
    signal_probe = _separate_signal_probe("separate-signal-probe")
    bundle = s2id._bundle("x", "y", context_probe)
    signal_input = signal_contract.TwoAreaConflictSignalInput.build(
        "s2ih-signal-input", "SIGNAL", signal_probe, bundle
    )
    baseline_input = signal_contract.TwoAreaConflictSignalInput.build(
        "s2ih-baseline-input", "DIRECT_BASELINE", signal_probe, bundle
    )
    case_plan_digest = s2id._digest("joint-case-plan")
    context_wrapper = _context_wrapper(case_plan_digest, context_probe.probe_digest)
    signal_wrapper = _signal_wrapper(case_plan_digest, signal_probe)
    return (
        context_probe,
        signal_probe,
        bundle,
        signal_input,
        baseline_input,
        context_wrapper,
        signal_wrapper,
    )


def _neutral_result(index: int, operation_id: str) -> dict[str, object]:
    return {
        "schema": "s2ih.neutral-artifact.v1",
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
    for index in range(2, fixtures.SUCCESS_OPERATION_COUNT + 1):
        row = recorder.current_row()
        external = evaluation_root["seal_digest"] if index == 172 else None
        recorder.start(
            row.operation_id,
            {"neutral_qualification": True, "ordinal": index},
            external_parent_digest=external,
        )
        result = _neutral_result(index, row.operation_id)
        if index == 2:
            result = {
                "execution_plan": plan.payload(),
                "registry_bundle_digest": registry.bundle_digest,
                "execution_fixture_digest": fixtures.EXECUTION_FIXTURE_DIGEST,
            }
        elif index in case_evidence_ops:
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


class S2IHJointQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temporary = tempfile.TemporaryDirectory(prefix="s2ih-")
        cls.root = Path(cls._temporary.name).resolve()
        cls.valid_run = _complete_neutral_recording(
            cls.root, "s2ih-neutral-complete-01"
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def _copy_valid(self, suffix: str) -> Path:
        target = self.root / f"copy-{suffix}"
        shutil.copytree(self.valid_run, target)
        return target

    def test_15_distinct_retrieval_and_signal_probes_bind_without_digest_equality(self) -> None:
        (
            context_probe,
            signal_probe,
            bundle,
            signal_input,
            baseline_input,
            context_wrapper,
            signal_wrapper,
        ) = _dual_fixture()
        binding, ledger = runner.bind_dual_probe_case(
            context_wrapper, signal_wrapper, bundle, signal_input, baseline_input
        )
        self.assertNotEqual(context_probe.probe_digest, signal_probe.probe_digest)
        self.assertEqual(bundle.probe_digest, binding.context_function_probe_digest)
        self.assertEqual(signal_probe.probe_digest, binding.masked_visual_probe_digest)
        self.assertEqual(0, ledger["storage_or_learning_call_count"])

    def test_16_swapped_case_plan_and_probe_relations_fail_closed(self) -> None:
        values = _dual_fixture()
        bundle, signal_input, baseline_input = values[2], values[3], values[4]
        context_wrapper, signal_wrapper = values[5], values[6]
        foreign_plan = s2id._digest("foreign-case-plan")
        foreign_signal = _signal_wrapper(
            foreign_plan, values[1], source_suffix="foreign-plan"
        )
        with self.assertRaises(runner.S2IGRunnerError):
            runner.bind_dual_probe_case(
                context_wrapper, foreign_signal, bundle, signal_input, baseline_input
            )
        foreign_probe = _separate_signal_probe("foreign-native-probe")
        foreign_wrapper = _signal_wrapper(
            context_wrapper.case_plan_digest, foreign_probe, source_suffix="foreign-probe"
        )
        with self.assertRaises(runner.S2IGRunnerError):
            runner.bind_dual_probe_case(
                context_wrapper, foreign_wrapper, bundle, signal_input, baseline_input
            )

    def test_17_owner_is_atomic_and_rejects_a_foreign_pairing(self) -> None:
        values = _dual_fixture()
        binding, _ = runner.bind_dual_probe_case(
            values[5], values[6], values[2], values[3], values[4]
        )
        foreign = replace(
            binding,
            dual_probe_binding_digest=s2id._digest("foreign-binding"),
        )
        owner = runner.DualProbeCaseOwner("s2ih-dual-owner", binding)
        with self.assertRaises(runner.S2IGRunnerError):
            owner.commit(foreign, s2id._digest("signal"), s2id._digest("baseline"))
        self.assertEqual("FAILED", owner.state)
        self.assertIsNone(owner.poststate.signal_result_digest)
        with self.assertRaises(runner.S2IGRunnerError):
            owner.commit(binding, s2id._digest("signal"), s2id._digest("baseline"))

    def test_18_candidates_remain_bound_to_retrieval_and_status_to_signal_probe(self) -> None:
        values = _dual_fixture()
        bundle = values[2]
        first_binding, _ = runner.bind_dual_probe_case(
            values[5], values[6], bundle, values[3], values[4]
        )
        alternate_probe = _separate_signal_probe("alternate-signal-probe")
        alternate_signal = signal_contract.TwoAreaConflictSignalInput.build(
            "s2ih-alternate-signal", "SIGNAL", alternate_probe, bundle
        )
        alternate_baseline = signal_contract.TwoAreaConflictSignalInput.build(
            "s2ih-alternate-baseline", "DIRECT_BASELINE", alternate_probe, bundle
        )
        alternate_wrapper = _signal_wrapper(
            values[5].case_plan_digest, alternate_probe, source_suffix="alternate"
        )
        second_binding, _ = runner.bind_dual_probe_case(
            values[5], alternate_wrapper, bundle, alternate_signal, alternate_baseline
        )
        self.assertEqual(first_binding.two_area_bundle_digest, second_binding.two_area_bundle_digest)
        self.assertEqual(first_binding.context_function_probe_digest, second_binding.context_function_probe_digest)
        self.assertNotEqual(first_binding.masked_visual_probe_digest, second_binding.masked_visual_probe_digest)

    def test_19_registry_gate_and_complete_neutral_recording_are_valid(self) -> None:
        self.assertEqual(183, len(fixtures.REGISTRY.rows))
        self.assertEqual(366, 2 * len(fixtures.REGISTRY.rows))
        runner.MAIN_EXECUTION_ENABLED = False
        with mock.patch.object(runner, "_execute") as execute:
            with self.assertRaises(runner.S2IGRunnerError):
                runner.run_main_once(
                    self.root,
                    WORKSPACE_ROOT,
                    "s2ih-gate-closed-01",
                    "s2ih-gate-closed-owner",
                    object(),
                )
        execute.assert_not_called()
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        finding = verifier.verify_run_read_only(WORKSPACE_ROOT, self.valid_run)
        self.assertEqual("RECORDING_COMPLETE", finding.status, finding.errors)
        self.assertEqual((183, 366), (finding.operation_count, finding.event_count))

    def test_20_event_and_receipt_manipulations_are_rejected(self) -> None:
        missing_event = self._copy_valid("missing-event")
        journal = missing_event / "journal/operations.jsonl"
        lines = journal.read_bytes().splitlines(keepends=True)
        journal.write_bytes(b"".join(lines[:-1]))
        self.assertEqual(
            "NOT_EVALUABLE",
            verifier.verify_run_read_only(WORKSPACE_ROOT, missing_event).status,
        )

        swapped_event = self._copy_valid("swapped-event")
        journal = swapped_event / "journal/operations.jsonl"
        lines = journal.read_bytes().splitlines(keepends=True)
        lines[20], lines[21] = lines[21], lines[20]
        journal.write_bytes(b"".join(lines))
        self.assertEqual(
            "NOT_EVALUABLE",
            verifier.verify_run_read_only(WORKSPACE_ROOT, swapped_event).status,
        )

        missing_receipt = self._copy_valid("missing-receipt")
        (missing_receipt / "receipts/ie-op-010.json").unlink()
        self.assertEqual(
            "NOT_EVALUABLE",
            verifier.verify_run_read_only(WORKSPACE_ROOT, missing_receipt).status,
        )

        swapped_receipt = self._copy_valid("swapped-receipt")
        first = swapped_receipt / "receipts/ie-op-010.json"
        second = swapped_receipt / "receipts/ie-op-011.json"
        first_bytes, second_bytes = first.read_bytes(), second.read_bytes()
        first.write_bytes(second_bytes)
        second.write_bytes(first_bytes)
        self.assertEqual(
            "NOT_EVALUABLE",
            verifier.verify_run_read_only(WORKSPACE_ROOT, swapped_receipt).status,
        )

        manipulated = self._copy_valid("manipulated-receipt")
        path = manipulated / "receipts/ie-op-012.json"
        payload = json.loads(path.read_text(encoding="ascii"))
        payload["artifact"]["result"]["ordinal"] = 999
        _canonical_write(path, payload)
        self.assertEqual(
            "NOT_EVALUABLE",
            verifier.verify_run_read_only(WORKSPACE_ROOT, manipulated).status,
        )

    def test_21_complete_and_not_evaluable_are_exclusive(self) -> None:
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
            "s2ih-neutral-failure-01",
            "s2ih-neutral-failure-owner",
        )
        reserved = recording.AppendOnlyRunRecorder.reserve(self.root, plan, registry)
        self.assertIs(type(reserved), recording.AppendOnlyRunRecorder)
        reserved.fail("IG-E002", "ie-op-002")
        self.assertEqual("NOT_EVALUABLE", reserved.state)
        self.assertFalse((reserved.run_directory / "terminal/complete/COMPLETE").exists())
        failure = verifier.verify_run_read_only(WORKSPACE_ROOT, reserved.run_directory)
        self.assertEqual("NOT_EVALUABLE", failure.status)
        self.assertEqual((), failure.errors)


def load_tests(
    loader: unittest.TestLoader,
    tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(s2id.S2IDPrivateTwoAreaConflictSignalTests))
    suite.addTests(loader.loadTestsFromTestCase(S2IHJointQualificationTests))
    return suite


if __name__ == "__main__":
    unittest.main()
