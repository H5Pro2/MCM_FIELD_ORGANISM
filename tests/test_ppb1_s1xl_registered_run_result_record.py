from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "docs/S1XL_PPB1_EINMALIGER_PRIVATER_REGISTRIERTER_60_ZELLEN_LAUF_V1.json"
EXPECTED_RESULT_DIGEST = (
    "67dd6f3cbf2644b2cebc651646129bf9e1e590f718a68b5f666cda9d19076bec"
)


def load_result():
    return json.loads(RESULT_PATH.read_text(encoding="utf-8"))


def canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class PPB1S1XLRegisteredRunResultRecordTests(unittest.TestCase):
    def test_result_record_is_canonical_and_digest_bound(self) -> None:
        self.assertEqual(EXPECTED_RESULT_DIGEST, canonical_digest(load_result()))

    def test_parent_preflight_and_sources_remain_exact(self) -> None:
        result = load_result()
        parent = json.loads(
            (ROOT / "docs/S1XK_PPB1_STATISCHER_REGISTRIERTER_AUSFUEHRUNGS_GO_NO_GO_UND_AUTORISIERUNGSPREFLIGHT_V1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(result["parent_s1xk_preflight_digest"], canonical_digest(parent))
        paths = {
            "s1xi_source": "mcm_field_organism/_ppb1_s1xi_private_full_runner.py",
            "s1xc_fixture_registry": "mcm_field_organism/_ppb1_s1xc_fixture_registry.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "s1xf_miniature_runner": "mcm_field_organism/_ppb1_s1xf_private_miniature_runner.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                result["bound_source_digests_verified_immediately_before_run"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_execution_scope_is_single_private_and_retry_free(self) -> None:
        scope = load_result()["execution_scope"]
        self.assertEqual(1, scope["process_count"])
        self.assertEqual(1, scope["registered_runner_call_count"])
        self.assertEqual(0, scope["retry_count"])
        self.assertEqual(60, scope["registered_matrix_cell_count"])
        self.assertFalse(scope["source_file_modified"])
        self.assertTrue(scope["registered_lock_reset_in_finally"])
        self.assertFalse(scope["substitute_runner_called"])

    def test_both_formations_match_and_matrix_identity_is_exact(self) -> None:
        result = load_result()
        self.assertTrue(result["formation_receipts"]["auditory"]["template_match"])
        self.assertTrue(result["formation_receipts"]["visual"]["template_match"])
        matrix = result["matrix_receipt"]
        self.assertTrue(matrix["method_valid"])
        self.assertEqual(60, matrix["ordered_cell_receipt_count"])
        self.assertEqual(
            "c854345e708175ef4473b1044d3ab1cd40f48c39c0676789523fd8a52297e2ce",
            matrix["matrix_receipt_digest"],
        )

    def test_bound_function_decision_is_fail_at_nine_of_ten(self) -> None:
        matrix = load_result()["matrix_receipt"]
        self.assertEqual(9, matrix["candidate_pass_cell_count"])
        self.assertEqual(
            "TECHNICAL_MEMORY_FUNCTION_FAIL", matrix["technical_function_decision"]
        )
        self.assertIsNone(matrix["baseline_explanation_decision"])
        self.assertEqual("TECHNICAL_MEMORY_FUNCTION_FAIL", matrix["final_decision"])

    def test_one_auditory_boundary_mismatch_is_preserved(self) -> None:
        mismatch = load_result()["observed_candidate_mismatch"]
        self.assertEqual(1, mismatch["mismatch_count"])
        self.assertEqual("s1xa.auditory.ppb1.boundary-positive", mismatch["cell_id"])
        self.assertTrue(mismatch["expected_recognized"])
        self.assertFalse(mismatch["observed_recognized"])
        self.assertEqual(0.2, mismatch["expected_distance"])
        self.assertEqual(0.20000000000000004, mismatch["observed_distance"])
        self.assertTrue(mismatch["state_unchanged"])

    def test_baseline_map_and_interpretation_remain_narrow(self) -> None:
        result = load_result()
        self.assertEqual(
            {
                "no-memory": False,
                "replay": True,
                "static-prototype": True,
                "moving-state": True,
                "last-vector-distance": True,
            },
            result["matrix_receipt"]["baseline_explanation_by_system"],
        )
        self.assertEqual(
            "BOUND_TECHNICAL_FUNCTION_FAIL_NO_MEMORY_CAPABILITY_OR_MCM_SPECIFIC_CLAIM",
            result["result_interpretation"],
        )
        self.assertFalse(result["rerun_allowed"])


if __name__ == "__main__":
    unittest.main()
