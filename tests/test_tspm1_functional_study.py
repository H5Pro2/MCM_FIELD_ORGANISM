"""Eight miniature qualification tests; never execute an H1-H7 cell."""

from __future__ import annotations

import argparse
import ast
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from copy import deepcopy
import inspect
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from mcm_field_organism import _tspm1_private as tspm
from mcm_field_organism import _tspm1_s2dr_private_comparison as c
from tools import _tspm1_functional_study as local


def mini_source(profile, config, index, pair, *, probe=False):
    streams = tuple(c._sequence(modality, value, index, "unit-mini", "probe" if probe else "formation")
                    for modality, value in zip((profile.auditory_config, profile.visual_config), pair, strict=True))
    world = c._world()
    batch = c.BrowserReceptorSequenceBatch(world.contract_id, world.digest(), streams)
    envelope = c.bind_ppb1_active_receptor_batch(f"unit.binding.{index}", world, batch, profile)
    args = (config, envelope, envelope.auditory_stream.timed_frames[0], envelope.visual_stream.timed_frames[0])
    return tspm.bind_tspm1_probe(*args) if probe else tspm.bind_tspm1_exposure(*args)


def miniature(start):
    profile, config = c._runtime_tspm_config()
    state = tspm.initial_tspm1_composite_state(config)
    initial = c._canonical(state)
    events = []
    for index, pair in enumerate(((0.11, 0.23), (0.13, 0.25)), 1):
        exposure = mini_source(profile, config, index, pair)
        before = state
        owner = tspm.TSPM1CoordinatorOwner(f"unit.owner.{index}", f"unit.authorization.{index}",
            f"unit.consume.{index}", config.config_binding_digest, state.composite_state_digest, exposure.exposure_digest)
        step = owner.consume_once(config, state, exposure)
        state = step.poststate
        events.append(c._canonical({"prestate": before, "exposure_digest": exposure.exposure_digest,
                                   "step": step, "owner": owner.snapshot()}))
    before_probe = c._canonical(state)
    finding = tspm.probe_tspm1_read_only(config, state, mini_source(profile, config, 3, (0.12, 0.24), probe=True))
    return {"cell_id": start["cell_id"], "owner_id": start["owner_id"],
            "consumption_id": start["consumption_id"], "events": events,
            "findings": [c._canonical(finding)], "initial": initial,
            "before_probe": before_probe, "after_probe": c._canonical(state)}


def expected_unit(cell_id="unit.mini", formations=2, probes=1):
    return [{"cell_id": cell_id, "formation_count": formations, "probe_count": probes,
             "plan": {"scope": "QUALIFICATION_ONLY", "pairs": [[0.11, 0.23], [0.13, 0.25]]}}]


def empty_packet(start):
    return {"cell_id": start["cell_id"], "owner_id": start["owner_id"],
            "consumption_id": start["consumption_id"], "events": [], "findings": []}


class FunctionalStudyTests(unittest.TestCase):
    def setUp(self):
        self.notes = []
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        # Guard every registered cell/state entry for all eight tests, even negative tests.
        self.guards = [self.stack.enter_context(patch.object(c, name, side_effect=AssertionError("H1-H7 execution forbidden")))
                       for name in ("initial_s2dr_arm_state", "advance_s2dr_arm", "probe_s2dr_arm")]
        self.guards.append(self.stack.enter_context(patch.object(c.S2DRCellOwner, "consume_once",
                                                               side_effect=AssertionError("cell execution forbidden"))))
        self.temp = self.stack.enter_context(tempfile.TemporaryDirectory(prefix="tspm1-qualification-"))

    def tearDown(self):
        self.assertEqual([0, 0, 0, 0], [guard.call_count for guard in self.guards])
        self.notes.append({"registered_cell_and_state_calls": [guard.call_count for guard in self.guards]})

    def log(self, run_id, expected=None):
        return local._AttemptLog(self.temp, run_id, "eight-focused-tests-only", {"sources": []},
                                 expected or expected_unit(), scope="QUALIFICATION")

    def test_01_real_formation_precedes_probe_and_recording(self):
        log = self.log("unit.first")
        packet = log.record_cell(miniature)
        self.assertEqual(2, len(packet["events"]))
        self.assertEqual(packet["initial"], packet["events"][0]["prestate"])
        self.assertEqual(packet["events"][0]["step"]["poststate"], packet["events"][1]["prestate"])
        self.assertTrue(packet["findings"][0]["fast_recognized"])
        self.assertNotEqual(packet["initial"], packet["before_probe"])
        result = log.finish({"kind": "TECHNICAL_MINIATURE_ONLY"})
        self.assertEqual((1, 2, 1), tuple(result["payload"][k] for k in ("cell_count", "formation_count", "probe_count")))
        self.assertEqual("COMPLETE", local.verify_result(log.directory)["recording_status"])
        self.notes.append({"actual_miniature": packet, "recording": result})

    def test_02_fresh_state_and_read_only_probe(self):
        profile, config = c._runtime_tspm_config()
        fresh = tspm.initial_tspm1_composite_state(config)
        fresh_before = c._canonical(fresh)
        no_match = tspm.probe_tspm1_read_only(config, fresh, mini_source(profile, config, 1, (0.12, 0.24), probe=True))
        self.assertFalse(no_match.fast_recognized)
        first = miniature({"cell_id": "unit.a", "owner_id": "unit.a", "consumption_id": "unit.a"})
        second = miniature({"cell_id": "unit.b", "owner_id": "unit.b", "consumption_id": "unit.b"})
        self.assertEqual(fresh_before, first["initial"])
        self.assertEqual(first["initial"], second["initial"])
        self.assertEqual(first["before_probe"], first["after_probe"])
        self.assertEqual(second["before_probe"], second["after_probe"])
        self.assertEqual(fresh_before, c._canonical(fresh))
        self.notes.append({"fresh_probe": c._canonical(no_match), "first": first, "second": second})

    def test_03_neutral_scoring_and_simpler_equal_utility(self):
        finding = {"recognized": True, "selected_auditory_values": [0.1] * 8,
                   "selected_visual_values": [0.3] * 18}
        positive = c._score_functional_probe(finding, True, (0.0, 0.2))
        self.assertTrue(positive["functional_correct"])
        self.assertEqual(26, positive["evaluation_terms"])
        self.assertFalse(c._score_functional_probe(finding, False, None)["functional_correct"])
        negative = {"recognized": False, "selected_auditory_values": None, "selected_visual_values": None}
        self.assertTrue(c._score_functional_probe(negative, False, None)["functional_correct"])
        self.assertFalse(c._score_functional_probe(negative, True, (0.0, 0.2))["functional_correct"])
        row = {"probe_metrics": [{"probe_key": "unit.probe", **positive}], "ax_preserved": True,
               "observed_capture_latency_rank": 1, "total_formation_write_words": 100}
        groups = c._engineering_groups({"TSPM1": deepcopy(row), "B2": deepcopy(row), "R0": deepcopy(row)})
        self.assertEqual(1, len(groups))
        self.assertEqual(("B2",), groups[0]["equally_preferred"])
        different = deepcopy(row)
        different["probe_metrics"][0]["functional_correct"] = False
        self.assertEqual(2, len(c._engineering_groups({"TSPM1": row, "B2": different})))
        self.notes.append({"positive": positive, "engineering_groups": groups})

    def test_04_full_r0_projection_rejects_changed_identity(self):
        # Two one-observation DTOs only; no matrix, native state or fabricated attestation.
        finding = {key: None for key in ("checkpoint", "pair_id", "recognized", "context_source",
            "fast_recognized", "auditory_fast_distance", "visual_fast_distance", "auditory_slow_status",
            "visual_slow_status", "auditory_selected_slot_id", "visual_selected_slot_id",
            "auditory_selected_prototype_digest", "visual_selected_prototype_digest", "auditory_slow_distance",
            "visual_slow_distance", "selected_av_payload_digest")}
        finding["observation"] = {key: None for key in c._ee_contract()["source_and_receipt_contract"]["r0_observation_projection_fields"]}
        original = SimpleNamespace(poststate_payload={"bank": "unit.bank", "config": "unit.config", "slot": "unit.slot"},
            event_payloads=({"event": "UNIT_ONLY", "consolidation_status": "UNIT_ONLY"},), finding_payloads=(finding,))
        self.assertTrue(c._r0_pair_equal(original, deepcopy(original)))
        for identity in ("bank", "config", "slot"):
            changed = deepcopy(original)
            changed.poststate_payload[identity] = "unit.foreign"
            self.assertFalse(c._r0_pair_equal(original, changed))
        changed = deepcopy(original)
        changed.finding_payloads[0]["observation"]["native_recognized"] = True
        self.assertFalse(c._r0_pair_equal(original, changed))
        self.notes.append({"projection": c._exact_reduction_projection(original),
                           "rejected": ["bank", "config", "slot", "observation"]})

    def test_05_budget_includes_validation_terms(self):
        # Registry metadata only. No H1-H7 cell/result or functional state is built.
        config, fixtures, arms, plans, _ = c.build_s2dr_registry()
        arm, plan, fixture = arms[0], plans[0], fixtures[0]
        identity = c._file_identity(Path(c.__file__))
        line = inspect.getsourcelines(c._score_functional_probe)[1]
        distances = [{"cell_id": plan.cell_id, "phase": "PROBE", "operation_index": 1,
            "ordinal": index, "dimension": 18, "purpose": "FUNCTIONAL" if index == 1 else "VALIDATION",
            "source_path": identity["repository_relative_path"], "source_blob": identity["git_blob"],
            "operand_digests": ["a" * 64, "b" * 64], "callsite": ["_score_functional_probe", line]}
            for index in range(1, 14)]
        cost = {"cell_id": plan.cell_id, "phase": "PROBE", "operation_index": 1,
            "distance_evidence": distances, "write_evidence": [], "functional_terms": 18,
            "validation_terms": 216, "total_distance_terms": 234, "functional_write_words": 0,
            "ppb_call_evidence": [], "native_prestate_payload": [], "native_poststate_payload": [],
            "native_event": None, "prestate_payload": [], "poststate_payload": [],
            "prestate_digest": c._digest([]), "poststate_digest": c._digest([])}
        cost["cost_digest"] = c._digest(cost)
        c.validate_s2dr_cell_result(config, fixture, arm, plan, None, operation_cost=cost)
        cost["distance_evidence"].append({**distances[-1], "ordinal": 14, "dimension": 8})
        cost.update(validation_terms=224, total_distance_terms=242)
        cost["cost_digest"] = c._digest({k: v for k, v in cost.items() if k != "cost_digest"})
        with self.assertRaises(c.S2DRError) as caught:
            c.validate_s2dr_cell_result(config, fixture, arm, plan, None, operation_cost=cost)
        self.assertEqual(c.S2DR_RESOURCE_OR_OPERATION_LIMIT_EXCEEDED, caught.exception.code)
        self.notes.append({"scope": "UNIT_COST_EVIDENCE_NOT_MEASURED_MODEL_COST", "accepted": 234,
                           "rejected": cost, "error_code": caught.exception.code})

    def test_06_missing_corrupt_and_flush_failed_recording(self):
        log = self.log("unit.complete", expected_unit(formations=0, probes=0))
        log.record_cell(empty_packet)
        log.finish({"kind": "RECORDING_ONLY"})
        terminal = log.directory / "terminal.json"
        # Mutations affect only isolated temporary qualification files.
        terminal.rename(log.directory / "terminal.withheld")
        self.assertEqual("NOT_EVALUABLE", local.verify_result(log.directory)["recording_status"])
        (log.directory / "terminal.withheld").rename(terminal)
        (log.directory / "cell-001.json").write_bytes(b'{"incomplete":')
        self.assertEqual("NOT_EVALUABLE", local.verify_result(log.directory)["recording_status"])
        failed = self.log("unit.flush", expected_unit(formations=0, probes=0))
        failed.record_cell(empty_packet)
        original = local.os.fsync
        calls = []
        def fail_first(handle):
            calls.append(handle)
            if len(calls) == 1:
                raise OSError("injected qualification flush failure")
            return original(handle)
        with patch.object(local.os, "fsync", side_effect=fail_first):
            with self.assertRaises(OSError):
                failed.finish({"kind": "RECORDING_ONLY"})
        self.assertFalse((failed.directory / "terminal.json").exists())
        self.assertEqual("NOT_EVALUABLE", local.verify_result(failed.directory)["recording_status"])
        self.notes.append({"injected_only": True, "failure": local._read(failed.directory / "failure.json", "failure")})

    def test_07_one_use_and_error_without_retry(self):
        log = self.log("unit.once", expected_unit(formations=0, probes=0))
        calls = []
        def fail(start):
            calls.append(start)
            raise RuntimeError("deliberate miniature failure")
        with self.assertRaises(RuntimeError):
            log.record_cell(fail)
        with self.assertRaises(local.RecordingError):
            log.record_cell(fail)
        with self.assertRaises(FileExistsError):
            self.log("unit.once", expected_unit(formations=0, probes=0))
        self.assertEqual(1, len(calls))
        self.assertEqual("FAILED", log.status)
        self.assertEqual("NOT_EVALUABLE", local.verify_result(log.directory)["recording_status"])
        self.notes.append({"producer_calls": len(calls), "failure": local._read(log.directory / "failure.json", "failure")})

    def test_08_old_gate_and_platform_isolation(self):
        self.assertIs(c._EXECUTION_RELEASE_ENABLED, False)
        self.assertIs(local._FUNCTIONAL_STUDY_RELEASE_ENABLED, False)
        with self.assertRaises(c.S2DRError):
            c._S2EFAttempt(None, None, None)
        with self.assertRaises(c.S2DRError):
            c.compare_s2dr_results(None, (), (), "a" * 64)
        with self.assertRaises(local.RecordingError):
            local.run_study_once("unit.forbidden", "qualification-not-matrix")
        tree = ast.parse(Path(local.__file__).read_text(encoding="utf-8"))
        forbidden = {"_S2EFAttempt", "_DurableStudyStore", "_build_s2ef_execution_plan", "_source_manifest"}
        calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and isinstance(n.func.value, ast.Name) and n.func.value.id == "comparison"}
        self.assertFalse(calls & forbidden)
        self.assertFalse(any(name.startswith(("tools._s2", "mcm_field_organism._s2")) for name in sys.modules))
        before = ast.parse(c._git("show", "HEAD:mcm_field_organism/_tspm1_s2dr_private_comparison.py"))
        after = ast.parse(Path(c.__file__).read_text(encoding="utf-8"))
        allowed = {"_per_arm_metrics", "compare_s2dr_results"}
        old = {n.name: ast.dump(n, include_attributes=False) for n in before.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        new = {n.name: ast.dump(n, include_attributes=False) for n in after.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        self.assertEqual([], [name for name in old if name not in allowed and old[name] != new.get(name)])
        old_constants = [ast.dump(n, include_attributes=False) for n in before.body if isinstance(n, (ast.Assign, ast.AnnAssign))]
        new_constants = [ast.dump(n, include_attributes=False) for n in after.body if isinstance(n, (ast.Assign, ast.AnnAssign))]
        self.assertEqual(old_constants, new_constants)
        self.notes.append({"both_gates_locked": True, "old_definitions_unchanged_except": sorted(allowed),
                           "baseline_parameter_fixture_constants_unchanged": True})


class _RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def startTest(self, test):
        self.test_started = time.perf_counter()
        super().startTest(test)

    def stopTest(self, test):
        failures = [text for case, text in self.failures + self.errors if case is test]
        self.records.append({"id": test.id(), "status": "FAIL" if failures else "PASS",
            "elapsed_seconds": time.perf_counter() - self.test_started,
            "errors": failures, "evidence": getattr(test, "notes", [])})
        super().stopTest(test)


def run_recorded(directory):
    """Exactly one explicitly selected eight-test suite, with fail-fast recording."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    source = local._source_manifest()
    local._write_new(directory / "sources.json", local._seal("qualification_sources", source))
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FunctionalStudyTests)
    if suite.countTestCases() != 8:
        raise RuntimeError("exactly eight qualification tests required")
    transcript = directory / "output.txt"
    with transcript.open("x", encoding="utf-8", newline="\n") as stream:
        with redirect_stdout(stream), redirect_stderr(stream):
            result = unittest.TextTestRunner(stream=stream, verbosity=2, failfast=True,
                                             resultclass=_RecordedResult).run(suite)
        stream.flush()
        local.os.fsync(stream.fileno())
    local._check_sources(source)
    exit_code = 0 if result.wasSuccessful() and result.testsRun == 8 else 1
    payload = {"scope": "EIGHT_FOCUSED_TESTS_ONLY", "expected_tests": 8, "tests_run": result.testsRun,
        "exit_code": exit_code, "terminal": "OK" if exit_code == 0 else "STOPPED",
        "test_records": result.records, "failures": len(result.failures), "errors": len(result.errors),
        "source_manifest_digest": local._read(directory / "sources.json", "qualification_sources")["digest"],
        "transcript_sha256": local._sha(transcript.read_bytes()),
        "matrix_executed": False, "representation_quality": "NOT_TESTED"}
    report = local._seal("qualification_result", payload)
    local._publish(directory / "result.json", report)
    local._require(local._read(directory / "result.json", "qualification_result") == report, "qualification publication differs")
    print(f"{result.testsRun}/8 tests; exit_code={exit_code}; result={directory / 'result.json'}")
    return exit_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record-dir", type=Path, required=True)
    raise SystemExit(run_recorded(parser.parse_args().record_dir))
