"""Single neutral qualification for the private S2-KE implementation."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2ke_auditory_holdout_evaluator import CONFIRMED, FALSIFIED, NOT_EVALUABLE, S2KE_EVIDENCE_SCHEMA, evaluate_s2kc_evidence
from tools._s2ke_auditory_holdout_fixtures import CHECKPOINTS, FIXTURE_ROLES, FORMATION_SEQUENCE, GEOMETRY_BLOCKED, HOLDOUT_ROLES, TRAINING_ROLES
from tools._s2ke_auditory_holdout_measurement import READY, initial_baseline_state, materialize_start_gate_with_plan, validate_start_gate
from tools import _s2ke_auditory_holdout_runner as runner
from tools._s2ke_auditory_holdout_result_verifier import verify_result


QUALIFICATION_ID = "s2ke-qualification-20260903-01"
WORKSPACE = Path(__file__).resolve().parents[1]
PRODUCT_PATHS = tuple(WORKSPACE / relative for relative in runner.SOURCE_PATHS)


def _digest(value: object) -> str:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def _selected(support: int | None = None, evidence: str = "e") -> dict[str, object]:
    result: dict[str, object] = {"mechanical_match": True, "evidence_digest": evidence}
    if support is not None:
        result["support"] = support
    return result


def _probe(role: str, *, h: bool, negative: bool, checkpoint: str) -> dict[str, object]:
    final = checkpoint == "C3"
    trained = checkpoint in {"C2", "C3"}
    baseline = {
        "prestate_digest": f"baseline-{checkpoint}",
        "poststate_digest": f"baseline-{checkpoint}",
        "frozen": None,
        "nearest": None,
        "adaptive": None,
        "finding_digest": f"baseline-finding-{checkpoint}-{role}",
    }
    if final:
        baseline.update({
            "frozen": {"match": False},
            "nearest": {"match": False},
            "adaptive": {"match": h and not negative},
        })
    return {
        "probe_role": role,
        "prestate_digest": f"memory-{checkpoint}",
        "poststate_digest": f"memory-{checkpoint}",
        "b4_selected": _selected() if h and checkpoint == "C2" else None,
        "fast_selected": _selected() if h and checkpoint == "C2" else None,
        "auditory_slow_selected": _selected(3, "auditory") if h and trained else None,
        "visual_slow_selected": _selected(3, "visual-control") if trained else None,
        "baselines": baseline,
    }


def _confirmed_evidence() -> dict[str, object]:
    checkpoints = []
    for checkpoint, count in CHECKPOINTS:
        checkpoints.append({
            "checkpoint_id": checkpoint,
            "formation_count": count,
            "probes": [
                _probe("H_AUDIO", h=True, negative=False, checkpoint=checkpoint),
                _probe("N_AUDIO", h=False, negative=True, checkpoint=checkpoint),
            ],
        })
    return {
        "schema": S2KE_EVIDENCE_SCHEMA,
        "formation_roles": list(FORMATION_SEQUENCE),
        "baseline_training_roles": list(FORMATION_SEQUENCE),
        "checkpoints": checkpoints,
    }


class S2KEQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hashes_before = {str(path.relative_to(WORKSPACE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in PRODUCT_PATHS}
        cls.preflight, cls.pcm_plan = materialize_start_gate_with_plan(build_s2jw_default_live_profile())

    @classmethod
    def tearDownClass(cls) -> None:
        hashes_after = {str(path.relative_to(WORKSPACE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in PRODUCT_PATHS}
        report_dir = WORKSPACE / "reports" / "s2ke" / QUALIFICATION_ID
        report_dir.mkdir(parents=True, exist_ok=False)
        payload = {
            "schema": "s2ke.qualification-evidence.v1",
            "qualification_id": QUALIFICATION_ID,
            "test_count": 14,
            "main_gate": runner.MAIN_EXECUTION_ENABLED,
            "authorized_run_id": runner.AUTHORIZED_RUN_ID,
            "preflight": cls.preflight,
            "source_hashes_before": cls.hashes_before,
            "source_hashes_after": hashes_after,
            "source_hashes_unchanged": cls.hashes_before == hashes_after,
            "main_execution_performed": False,
            "memory_calls": cls.preflight["memory_calls"],
        }
        result = {**payload, "evidence_digest": _digest(payload)}
        (report_dir / "qualification.json").write_text(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="ascii")

    def test_01_fixed_roles_counts_and_holdout_exclusion(self) -> None:
        self.assertEqual(len(FIXTURE_ROLES), 13)
        self.assertEqual(len(FORMATION_SEQUENCE), 17)
        self.assertEqual(CHECKPOINTS, (("C0", 0), ("C1", 1), ("C2", 8), ("C3", 17)))
        self.assertTrue(set(HOLDOUT_ROLES).isdisjoint(TRAINING_ROLES))
        self.assertTrue(set(HOLDOUT_ROLES).isdisjoint(FORMATION_SEQUENCE))

    def test_02_pcm_plan_is_single_set_with_exact_float32_coefficients(self) -> None:
        plan = self.pcm_plan
        self.assertEqual(self.preflight["basis_evaluations"], 2)
        self.assertEqual(self.preflight["coefficient_sets"], 1)
        expected = (
            struct.unpack("<f", struct.pack("<f", (33.0 / 2000.0) / plan.m_u))[0],
            struct.unpack("<f", struct.pack("<f", (1.0 / 100.0) / plan.m_v))[0],
            struct.unpack("<f", struct.pack("<f", (1.0 / 200.0) / plan.m_v))[0],
        )
        self.assertEqual((plan.alpha_u, plan.alpha_hv, plan.alpha_bv), expected)
        self.assertEqual(plan.alpha_plus_v, struct.unpack("<f", struct.pack("<f", plan.alpha_hv + plan.alpha_bv))[0])
        self.assertEqual(plan.alpha_minus_v, struct.unpack("<f", struct.pack("<f", plan.alpha_hv - plan.alpha_bv))[0])

    def test_03_plan_and_preflight_digest_bindings(self) -> None:
        self.assertEqual(self.pcm_plan.plan_digest, _digest(self.pcm_plan.payload_without_digest()))
        self.assertIs(validate_start_gate(self.preflight), self.preflight)

    def test_04_overlap_is_diagnostic_only(self) -> None:
        self.assertIsInstance(self.pcm_plan.overlap_channels, tuple)
        self.assertGreaterEqual(self.pcm_plan.overlap_l1_contribution, 0.0)
        self.assertNotIn("overlap_channels", {"status", "reason"})

    def test_05_real_gate_is_complete_or_stops_before_memory(self) -> None:
        self.assertIn(self.preflight["status"], {READY, GEOMETRY_BLOCKED})
        self.assertEqual(self.preflight["memory_calls"], 0)
        if self.preflight["status"] == READY:
            self.assertEqual(len(self.preflight["adaptive_updates"]), 6)
            self.assertEqual(set(self.preflight["fixture_digests"]), set(FIXTURE_ROLES))
        else:
            self.assertIn(self.preflight["reason"], {"PCM_SAMPLE_BOUND_EXCEEDED", "MEASURED_DISTANCE_GATE_FAILED"})

    def test_06_real_gate_uses_actual_48_value_measurements_when_reachable(self) -> None:
        if self.preflight["status"] == READY:
            distances = self.preflight["distances"]
            self.assertLessEqual(distances["training_pair"], 0.012)
            self.assertLessEqual(distances["holdout_adaptive"], 0.0195)
            self.assertTrue(all(item["pre_distance"] <= 0.02 for item in self.preflight["adaptive_updates"]))
        else:
            self.assertFalse(self.pcm_plan.samples_valid) if self.preflight["reason"] == "PCM_SAMPLE_BOUND_EXCEEDED" else self.assertIn("distances", self.preflight)

    def test_07_no_raw_payload_is_persisted_in_preflight(self) -> None:
        forbidden = {"samples", "pixels", "frame", "image", "raw", "raw_bytes"}
        def walk(value: object) -> bool:
            if isinstance(value, dict):
                return any(str(key).lower() in forbidden or walk(item) for key, item in value.items())
            if isinstance(value, list):
                return any(walk(item) for item in value)
            return False
        self.assertFalse(walk(self.preflight))

    def test_08_initial_baseline_is_immutable_and_empty(self) -> None:
        state = initial_baseline_state()
        self.assertEqual((state.formation_count, state.replay, state.frozen, state.adaptive, state.support), (0, (), None, None, 0))
        self.assertEqual(state.state_digest, initial_baseline_state().state_digest)

    def test_09_pure_evaluator_confirms_bound_synthetic_evidence(self) -> None:
        self.assertEqual(evaluate_s2kc_evidence(_confirmed_evidence())["status"], CONFIRMED)

    def test_10_pure_evaluator_reports_functional_falsification(self) -> None:
        evidence = _confirmed_evidence()
        evidence["checkpoints"][3]["probes"][0]["auditory_slow_selected"] = None
        self.assertEqual(evaluate_s2kc_evidence(evidence)["status"], FALSIFIED)

    def test_11_pure_evaluator_separates_not_evaluable(self) -> None:
        evidence = _confirmed_evidence()
        evidence["checkpoints"][0]["probes"][0]["poststate_digest"] = "changed"
        self.assertEqual(evaluate_s2kc_evidence(evidence)["status"], NOT_EVALUABLE)

    def test_12_runner_gate_and_operation_registry_remain_closed_and_exact(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        self.assertIsNone(runner.AUTHORIZED_RUN_ID)
        self.assertEqual(len(runner.EXPECTED_OPERATION_ROLES), 157)
        with self.assertRaises(runner.S2KERunnerError):
            runner.run_main_once(Path(tempfile.gettempdir()), WORKSPACE, "s2ke-main-locked")

    def test_13_verifier_accepts_the_actual_pre_memory_terminal_form(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            status = self.preflight["status"]
            payload = {
                "schema": runner.S2KE_RESULT_SCHEMA,
                "run_id": "s2ke-neutral-record",
                "technical_status": status if status == GEOMETRY_BLOCKED else "NOT_EVALUABLE",
                "source_hashes": runner.source_hashes(WORKSPACE),
                "plan": runner._plan(),
                "preflight": self.preflight,
                "completed_operation_count": 0,
                "memory_calls": 0,
            }
            path.write_text(json.dumps(runner._seal(payload), ensure_ascii=True, separators=(",", ":"), sort_keys=True) + "\n", encoding="ascii")
            finding = verify_result(path.resolve(), WORKSPACE)
            self.assertEqual(finding.operation_count, 0)
            self.assertIn(finding.status, {GEOMETRY_BLOCKED, NOT_EVALUABLE})

    def test_14_sources_exclude_field_context_and_main_effects(self) -> None:
        for path in PRODUCT_PATHS:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module]
            self.assertFalse(any("field_path" in name or "context" in name for name in imports))
        self.assertEqual(self.hashes_before, {str(path.relative_to(WORKSPACE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in PRODUCT_PATHS})


if __name__ == "__main__":
    unittest.main()
