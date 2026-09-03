"""One-shot qualification of the fixed S2-KF PCM scale."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2ke_auditory_holdout_fixtures import FIXTURE_ROLES, GEOMETRY_BLOCKED, SCALE_DENOMINATOR, SCALE_NUMERATOR, S2KE_PLAN_SCHEMA
from tools._s2ke_auditory_holdout_measurement import READY, materialize_start_gate_with_plan, validate_start_gate
from tools import _s2ke_auditory_holdout_runner as runner
from tools._s2ke_auditory_holdout_result_verifier import verify_result


QUALIFICATION_ID = "s2kf-qualification-20260903-01"
WORKSPACE = Path(__file__).resolve().parents[1]
CONTRACT_PATH = WORKSPACE / "docs" / "S2KF_AUDITIVE_PCM_UNIFORME_SKALIERUNG.md"
PRODUCT_PATHS = tuple(WORKSPACE / relative for relative in runner.SOURCE_PATHS) + (CONTRACT_PATH,)


def _digest(value: object) -> str:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    return hashlib.sha256(data).hexdigest()


class S2KFQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hashes_before = {str(path.relative_to(WORKSPACE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in PRODUCT_PATHS}
        cls.preflight, cls.pcm_plan = materialize_start_gate_with_plan(build_s2jw_default_live_profile())

    @classmethod
    def tearDownClass(cls) -> None:
        hashes_after = {str(path.relative_to(WORKSPACE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in PRODUCT_PATHS}
        report_dir = WORKSPACE / "reports" / "s2kf" / QUALIFICATION_ID
        report_dir.mkdir(parents=True, exist_ok=False)
        payload = {
            "schema": "s2kf.qualification-evidence.v1",
            "qualification_id": QUALIFICATION_ID,
            "test_count": 12,
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

    def test_01_new_fixture_version_binds_exact_uniform_scale(self) -> None:
        self.assertEqual(S2KE_PLAN_SCHEMA, "s2kf.auditory-pcm-plan.v2")
        self.assertEqual((SCALE_NUMERATOR, SCALE_DENOMINATOR), (24, 25))
        self.assertEqual(self.pcm_plan.payload_without_digest()["uniform_scale"], [24, 25])

    def test_02_coefficients_follow_the_bound_binary64_then_float32_order(self) -> None:
        plan = self.pcm_plan
        scale = 24.0 / 25.0
        expected = (
            struct.unpack("<f", struct.pack("<f", ((33.0 / 2000.0) * scale) / plan.m_u))[0],
            struct.unpack("<f", struct.pack("<f", ((1.0 / 100.0) * scale) / plan.m_v))[0],
            struct.unpack("<f", struct.pack("<f", ((1.0 / 200.0) * scale) / plan.m_v))[0],
        )
        self.assertEqual((plan.alpha_u, plan.alpha_hv, plan.alpha_bv), expected)

    def test_03_sample_gate_is_bound_before_receptor_and_memory_use(self) -> None:
        extrema = {role: (minimum, maximum) for role, minimum, maximum in self.pcm_plan.sample_extrema}
        self.assertEqual(set(extrema), {"T_PLUS", "T_MINUS", "H_AUDIO", "N_AUDIO"})
        if self.pcm_plan.samples_valid:
            self.assertTrue(all(-1.0 <= minimum <= maximum <= 1.0 for minimum, maximum in extrema.values()))
        else:
            self.assertEqual(self.preflight["status"], GEOMETRY_BLOCKED)
            self.assertEqual(self.preflight["reason"], "PCM_SAMPLE_BOUND_EXCEEDED")

    def test_04_real_start_gate_is_digest_valid_and_single_pass(self) -> None:
        self.assertIs(validate_start_gate(self.preflight), self.preflight)
        self.assertEqual((self.preflight["basis_evaluations"], self.preflight["coefficient_sets"], self.preflight["memory_calls"]), (2, 1, 0))

    def test_05_real_distance_intervals_are_enforced_when_samples_pass(self) -> None:
        if self.preflight["status"] == READY:
            distance = self.preflight["distances"]
            self.assertTrue(0.02010 <= distance["holdout_plus"] <= 0.02120)
            self.assertTrue(0.02010 <= distance["holdout_minus"] <= 0.02120)
            self.assertTrue(0.00900 <= distance["training_pair"] <= 0.01020)
            self.assertLessEqual(distance["holdout_adaptive"], 0.01850)
            self.assertTrue(0.02900 <= distance["negative_plus"] <= 0.03150)
            self.assertTrue(0.02010 <= distance["negative_minus"] <= 0.02120)
            self.assertGreaterEqual(distance["negative_adaptive"], 0.02700)
        else:
            self.assertIn(self.preflight["reason"], {"PCM_SAMPLE_BOUND_EXCEEDED", "MEASURED_DISTANCE_GATE_FAILED"})

    def test_06_all_six_actual_adaptive_updates_are_pre_memory(self) -> None:
        if self.preflight["status"] == READY:
            updates = self.preflight["adaptive_updates"]
            self.assertEqual([item["update_index"] for item in updates], list(range(1, 7)))
            self.assertTrue(all(item["pre_distance"] <= 0.02 for item in updates))
        self.assertEqual(self.preflight["memory_calls"], 0)

    def test_07_visual_control_and_distractors_are_measured_not_inferred(self) -> None:
        if self.preflight["status"] == READY:
            self.assertIsInstance(self.preflight["shared_visual_values_digest"], str)
            self.assertEqual(set(self.preflight["fixture_digests"]), set(FIXTURE_ROLES))
            self.assertEqual(len(self.preflight["distractor_distances"]), 9)
            self.assertTrue(all(min(item["plus"], item["minus"], item["adaptive"]) > 0.02 for item in self.preflight["distractor_distances"]))

    def test_08_overlap_remains_diagnostic(self) -> None:
        self.assertEqual(len(self.pcm_plan.overlap_channels), 48)
        self.assertGreaterEqual(self.pcm_plan.overlap_l1_contribution, 0.0)
        self.assertNotIn("overlap_l1_contribution", self.preflight.get("distances", {}))

    def test_09_no_raw_payload_is_persisted(self) -> None:
        forbidden = {"samples", "pixels", "frame", "image", "raw", "raw_bytes"}
        def walk(value: object) -> bool:
            if isinstance(value, dict):
                return any(str(key).lower() in forbidden or walk(item) for key, item in value.items())
            if isinstance(value, list):
                return any(walk(item) for item in value)
            return False
        self.assertFalse(walk(self.preflight))

    def test_10_runner_gate_and_full_run_remain_closed(self) -> None:
        self.assertIs(runner.MAIN_EXECUTION_ENABLED, False)
        self.assertIsNone(runner.AUTHORIZED_RUN_ID)
        self.assertEqual(len(runner.EXPECTED_OPERATION_ROLES), 157)
        with self.assertRaises(runner.S2KERunnerError):
            runner.run_main_once(Path(tempfile.gettempdir()), WORKSPACE, "s2kf-main-locked")

    def test_11_verifier_accepts_only_the_actual_pre_memory_terminal_form(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            status = self.preflight["status"]
            payload = {"schema": runner.S2KE_RESULT_SCHEMA, "run_id": "s2kf-neutral-record", "technical_status": status if status == GEOMETRY_BLOCKED else "NOT_EVALUABLE", "source_hashes": runner.source_hashes(WORKSPACE), "plan": runner._plan(), "preflight": self.preflight, "completed_operation_count": 0, "memory_calls": 0}
            path.write_text(json.dumps(runner._seal(payload), ensure_ascii=True, separators=(",", ":"), sort_keys=True) + "\n", encoding="ascii")
            finding = verify_result(path.resolve(), WORKSPACE)
            self.assertEqual(finding.operation_count, 0)
            self.assertIn(finding.status, {GEOMETRY_BLOCKED, "NOT_EVALUABLE"})

    def test_12_product_sources_and_gate_remain_unchanged(self) -> None:
        current = {str(path.relative_to(WORKSPACE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in PRODUCT_PATHS}
        self.assertEqual(self.hashes_before, current)
        self.assertFalse(runner.MAIN_EXECUTION_ENABLED)


if __name__ == "__main__":
    unittest.main()
