"""One-shot neutral qualification for the private S2-KB implementation."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_read_only as read_only
from tools import _s2kb_withheld_variant_runner as runner
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools._s2kb_withheld_variant_evaluator import (
    CONFIRMED,
    FALSIFIED,
    NOT_EVALUABLE,
    S2KB_EVIDENCE_SCHEMA,
    evaluate_s2ka_evidence,
)
from tools._s2kb_withheld_variant_fixtures import (
    CHECKPOINTS,
    FIXTURE_RECIPE_DIGEST,
    FIXTURE_ROLES,
    FORMATION_SEQUENCE,
    HOLDOUT_ROLES,
    S2KBFixtureError,
    S2KBFixtureStream,
    assert_training_role,
)
from tools._s2kb_withheld_variant_measurement import (
    AUDITORY_THRESHOLD,
    VISUAL_THRESHOLD,
    advance_baselines,
    initial_baseline_state,
    materialize_preflight,
    probe_baselines,
    validate_preflight_payload,
)
from tools._s2kb_withheld_variant_result_verifier import (
    S2KBVerificationError,
    verify_result,
)


QUALIFICATION_ID = "s2kb-qualification-20260902-01"
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


def _selected() -> dict[str, object]:
    return {"evidence_digest": "a" * 64, "mechanical_match": True}


def _baseline(match: bool | None) -> dict[str, object] | None:
    return None if match is None else {"match": match}


def _probe(role: str, memory: tuple[bool, bool, bool, bool], baseline: tuple[bool | None, bool | None, bool | None]) -> dict[str, object]:
    digest = f"state-{role.lower()}"
    baseline_digest = f"baseline-{role.lower()}"
    return {
        "probe_role": role,
        "prestate_digest": digest,
        "poststate_digest": digest,
        "b4_selected": _selected() if memory[0] else None,
        "fast_selected": _selected() if memory[1] else None,
        "auditory_slow_selected": _selected() if memory[2] else None,
        "visual_slow_selected": _selected() if memory[3] else None,
        "baselines": {
            "baseline_prestate_digest": baseline_digest,
            "baseline_poststate_digest": baseline_digest,
            "frozen_first": _baseline(baseline[0]),
            "replay_nearest": _baseline(baseline[1]),
            "adaptive_prototype": _baseline(baseline[2]),
        },
    }


def _synthetic_evidence() -> dict[str, object]:
    h_memory = {
        "C0": (False, False, False, False),
        "C1": (True, True, False, False),
        "C2": (True, True, True, True),
        "C3": (False, False, True, True),
    }
    h_baseline = {
        "C0": (None, None, None),
        "C1": (None, False, None),
        "C2": (False, False, True),
        "C3": (False, False, True),
    }
    n_baseline = {
        "C0": (None, None, None),
        "C1": (None, False, None),
        "C2": (False, False, False),
        "C3": (False, False, False),
    }
    return {
        "schema": S2KB_EVIDENCE_SCHEMA,
        "formation_roles": list(FORMATION_SEQUENCE),
        "baseline_training_roles": list(FORMATION_SEQUENCE),
        "initial_state_digest": "initial-memory",
        "initial_baseline_digest": "initial-baseline",
        "formation_evidence": [
            {"formation_index": index, "training_role": role}
            for index, role in enumerate(FORMATION_SEQUENCE, 1)
        ],
        "checkpoints": [
            {
                "checkpoint_id": checkpoint,
                "formation_count": count,
                "probes": [
                    _probe("H1", h_memory[checkpoint], h_baseline[checkpoint]),
                    _probe("N0", (False, False, False, False), n_baseline[checkpoint]),
                ],
            }
            for checkpoint, count in CHECKPOINTS
        ],
        "final_state": {},
        "final_baseline_state_digest": "final-baseline",
    }


class S2KBQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = build_s2jw_default_live_profile()
        stream = S2KBFixtureStream(cls.profile, "s2kb-qualification-clock")
        cls.fixtures = tuple(stream.materialize(role, index) for index, role in enumerate(FIXTURE_ROLES))
        cls.by_role = {item.role: item for item in cls.fixtures}
        cls.preflight = materialize_preflight(cls.fixtures)

    def _write_valid_result(self, directory: Path) -> Path:
        operations = runner._OperationChain([])
        for role in runner.EXPECTED_OPERATION_ROLES:
            operations.append(role, {"qualification": QUALIFICATION_ID})
        evidence = _synthetic_evidence()
        evaluation = evaluate_s2ka_evidence(evidence)
        payload = {
            "schema": runner.S2KB_RESULT_SCHEMA,
            "run_id": QUALIFICATION_ID,
            "technical_status": "RECORDING_COMPLETE",
            "source_hashes": runner.source_hashes(WORKSPACE_ROOT),
            "fixture_recipe_digest": FIXTURE_RECIPE_DIGEST,
            "preflight": self.preflight,
            "plan": runner._plan(),
            "operations": operations.records,
            "evidence": evidence,
            "functional_evaluation": evaluation,
            "last_operation_digest": operations.previous_digest,
        }
        path = directory / "result.json"
        runner._atomic_write(path, runner._seal(payload))
        return path

    def test_01_bound_fixture_inventory_and_streaming_shape(self) -> None:
        self.assertEqual(tuple(self.by_role), FIXTURE_ROLES)
        self.assertEqual(len(set(item.fixture_digest for item in self.fixtures)), 13)
        for item in self.fixtures:
            self.assertEqual(len(item.pair.auditory.timed_frame.frame.values), 48)
            self.assertEqual(len(item.pair.visual.timed_frame.frame.values), 288)
            self.assertFalse(hasattr(item, "image"))
            self.assertFalse(hasattr(item, "pcm"))

    def test_02_actual_receptor_preflight_and_all_distances(self) -> None:
        self.assertIs(validate_preflight_payload(self.preflight), self.preflight)
        self.assertEqual(len(self.preflight["pairwise_distances"]), 78)
        self.assertLessEqual(self.preflight["holdout_adaptive_distances"]["visual"], VISUAL_THRESHOLD)
        self.assertGreater(self.preflight["holdout_static_distances"]["visual"], VISUAL_THRESHOLD)
        self.assertLessEqual(self.preflight["holdout_adaptive_distances"]["auditory"], AUDITORY_THRESHOLD)

    def test_03_holdouts_are_excluded_from_all_training_roles(self) -> None:
        self.assertFalse(set(HOLDOUT_ROLES) & set(FORMATION_SEQUENCE))
        for role in HOLDOUT_ROLES:
            with self.assertRaises(S2KBFixtureError):
                assert_training_role(role)

    def test_04_independent_baselines_shift_without_holdout_training(self) -> None:
        state = initial_baseline_state()
        for role in FORMATION_SEQUENCE[:8]:
            state = advance_baselines(state, self.by_role[role])
        h1 = probe_baselines(state, self.by_role["H1"])
        n0 = probe_baselines(state, self.by_role["N0"])
        self.assertFalse(h1["frozen_first"]["match"])
        self.assertFalse(h1["replay_nearest"]["match"])
        self.assertTrue(h1["adaptive_prototype"]["match"])
        self.assertFalse(n0["adaptive_prototype"]["match"])
        self.assertEqual(state.adaptive_support, 3)

    def test_05_small_real_memory_path_is_atomic_and_read_only(self) -> None:
        limits = build_s2jv_ledger_limits(self.profile)
        config = coordinator.build_s2jv_coordinator_config(
            tspm_config=self.profile.tspm_config,
            b4_capacity=self.profile.b4_capacity,
            ledger_limits=limits,
        )
        state = coordinator.initial_s2jv_composite_state(config)
        stream = S2KBFixtureStream(self.profile, "s2kb-neutral-memory-clock")
        fixture = stream.materialize("D1", 0)
        source = coordinator.bind_s2jv_coordinator_input(config=config, source=fixture.pair)
        owner = coordinator.S2JVFormationOwner(
            "s2kb-neutral-owner", "s2kb-neutral-authorization",
            "s2kb-neutral-consumption", config.config_digest,
            state.state_digest, source.input_digest,
        )
        result = coordinator.advance_s2jv_atomic(config=config, prestate=state, source=source, owner=owner)
        probe = coordinator.bind_s2jv_probe(config=config, source=fixture.pair)
        finding = read_only.probe_s2jv_composite_read_only(config=config, state=result.poststate, probe=probe)
        self.assertEqual(finding.prestate_digest, finding.poststate_digest)
        self.assertEqual(result.poststate.generation, 1)

    def test_06_pure_evaluator_accepts_complete_synthetic_evidence(self) -> None:
        result = evaluate_s2ka_evidence(_synthetic_evidence())
        self.assertEqual(result["status"], CONFIRMED)
        self.assertTrue(all(result["claims"].values()))

    def test_07_functional_deviation_is_falsified_not_technical(self) -> None:
        evidence = _synthetic_evidence()
        evidence["checkpoints"][3]["probes"][0]["visual_slow_selected"] = None
        result = evaluate_s2ka_evidence(evidence)
        self.assertEqual(result["status"], FALSIFIED)
        self.assertFalse(result["claims"]["final_holdout_is_slow_only"])

    def test_08_method_break_is_not_evaluable(self) -> None:
        evidence = _synthetic_evidence()
        evidence["formation_roles"][0] = "H1"
        result = evaluate_s2ka_evidence(evidence)
        self.assertEqual(result["status"], NOT_EVALUABLE)

    def test_09_gate_is_closed_and_registry_is_exact(self) -> None:
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)
        self.assertIsNone(runner.AUTHORIZED_RUN_ID)
        self.assertEqual(len(runner.EXPECTED_OPERATION_ROLES), 157)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(runner.S2KBRunnerError):
                runner.run_main_once(Path(temporary).resolve(), WORKSPACE_ROOT, "s2kb-blocked-run")

    def test_10_atomic_result_write_rejects_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary).resolve() / "result.json"
            runner._atomic_write(path, {"qualification": QUALIFICATION_ID})
            with self.assertRaises(runner.S2KBRunnerError):
                runner._atomic_write(path, {"qualification": QUALIFICATION_ID})

    def test_11_independent_verifier_accepts_complete_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = self._write_valid_result(Path(temporary).resolve())
            finding = verify_result(path, WORKSPACE_ROOT)
            self.assertEqual(finding.status, "RECORDING_COMPLETE")
            self.assertEqual(finding.operation_count, 157)
            self.assertEqual(finding.functional_status, CONFIRMED)

    def test_12_verifier_rejects_operation_and_preflight_tampering(self) -> None:
        for mutation in ("operation", "preflight"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                path = self._write_valid_result(Path(temporary).resolve())
                value = json.loads(path.read_text(encoding="ascii"))
                if mutation == "operation":
                    value["operations"][1]["role"] = "ALTERED"
                else:
                    value["preflight"]["preflight_raw_bytes"] += 1
                payload = dict(value)
                payload.pop("record_digest")
                value["record_digest"] = runner._digest(payload)
                path.write_bytes(runner._json_bytes(value))
                with self.assertRaises(S2KBVerificationError):
                    verify_result(path, WORKSPACE_ROOT)

    def test_13_verifier_rejects_source_and_raw_payload_tampering(self) -> None:
        for mutation in ("source", "raw"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                path = self._write_valid_result(Path(temporary).resolve())
                value = json.loads(path.read_text(encoding="ascii"))
                if mutation == "source":
                    key = next(iter(value["source_hashes"]))
                    value["source_hashes"][key] = "0" * 64
                else:
                    value["evidence"]["raw_bytes"] = [1, 2, 3]
                payload = dict(value)
                payload.pop("record_digest")
                value["record_digest"] = runner._digest(payload)
                path.write_bytes(runner._json_bytes(value))
                with self.assertRaises(S2KBVerificationError):
                    verify_result(path, WORKSPACE_ROOT)

    def test_14_failure_record_is_not_evaluable_and_gate_stays_closed(self) -> None:
        payload = {
            "schema": runner.S2KB_RESULT_SCHEMA,
            "run_id": QUALIFICATION_ID,
            "technical_status": "NOT_EVALUABLE",
            "error_type": "NeutralFailure",
            "completed_operation_count": 4,
            "source_hashes": runner.source_hashes(WORKSPACE_ROOT),
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary).resolve() / "result.json"
            runner._atomic_write(path, runner._seal(payload))
            finding = verify_result(path, WORKSPACE_ROOT)
        self.assertEqual(finding.status, "NOT_EVALUABLE")
        self.assertIsNone(finding.functional_status)
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)


if __name__ == "__main__":
    unittest.main()
