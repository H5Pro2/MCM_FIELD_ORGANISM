from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / (
    "S1XE_PPB1_STATISCHER_PRIVATER_MATRIXRUNNER_RECEIPT_UND_"
    "ENTSCHEIDUNGSVERTRAG_V1.json"
)
EXPECTED_CONTRACT_DIGEST = (
    "eb501a103ec40dc9234e946553afb554279089ed2381a03011daa91f9db7731c"
)


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def canonical_json_digest(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class PPB1S1XEStaticMatrixRunnerReceiptDecisionContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_contract(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(
            EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest()
        )

    def test_parent_and_three_prior_contract_digests_are_exact(self) -> None:
        contract = load_contract()
        expected = {
            "parent_s1xd_audit_digest": (
                "docs/S1XD_PPB1_STATISCHER_QUELL_DIGEST_EXPORT_UND_"
                "NICHTAUSFUEHRUNGSAUDIT_V1.json"
            ),
            "s1ww_complete_function_contract": (
                "docs/S1WW_PPB1_VOLLSTAENDIGER_BILDUNGS_UND_PROBE_"
                "FUNKTIONSVERTRAG_V1.json"
            ),
            "s1wy_correction_contract": (
                "docs/S1WY_PPB1_KORREKTURVERTRAG_SCHWELLE_BASELINE_"
                "NULLROLLE_AGGREGATION_V1.json"
            ),
            "s1xa_materialization_contract": (
                "docs/S1XA_PPB1_STATISCHER_FIXTURE_UND_60_ZELLEN_"
                "MATRIXMATERIALISIERUNGSVERTRAG_V1.json"
            ),
        }
        self.assertEqual(
            canonical_json_digest(ROOT / expected["parent_s1xd_audit_digest"]),
            contract["parent_s1xd_audit_digest"],
        )
        for role in (
            "s1ww_complete_function_contract",
            "s1wy_correction_contract",
            "s1xa_materialization_contract",
        ):
            self.assertEqual(
                canonical_json_digest(ROOT / expected[role]),
                contract["bound_contract_digests"][role],
            )

        implementation = contract["bound_implementation"]
        for role, relative in (
            ("s1xc_source_digest", "mcm_field_organism/_ppb1_s1xc_fixture_registry.py"),
            ("s1wu_source_digest", "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py"),
        ):
            self.assertEqual(
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                implementation[role],
            )

    def test_formation_template_cannot_bypass_real_candidate_formation(self) -> None:
        correction = load_contract()["formation_bypass_correction"]
        self.assertTrue(correction["materialized_candidate_prestate_is_expected_template_only"])
        self.assertFalse(correction["template_is_candidate_formation_result"])
        self.assertTrue(correction["candidate_formation_must_execute_before_probe"])
        self.assertEqual(6, correction["total_candidate_formation_calls"])
        self.assertEqual(
            ["CREATED", "MATCHED", "MATCHED"],
            correction["required_terminal_event_sequence"],
        )

    def test_runner_phase_order_stops_before_decision_until_receipts_complete(self) -> None:
        phases = load_contract()["runner_phase_order"]
        self.assertEqual(9, len(phases))
        self.assertLess(
            phases.index("R6_VERIFY_COMPLETE_ORDERED_RECEIPT_SET"),
            phases.index("R7_APPLY_DECISION_PRECEDENCE"),
        )

    def test_allowed_call_counts_are_exact_and_finite(self) -> None:
        calls = load_contract()["allowed_private_calls"]
        self.assertEqual(1, calls["materializer"]["exact_call_count"])
        self.assertEqual(2, calls["candidate_formation"]["exact_initial_call_count"])
        self.assertEqual(6, calls["candidate_formation"]["exact_advance_call_count"])
        self.assertEqual(10, calls["candidate_probe"]["exact_call_count"])
        self.assertEqual(50, calls["baseline_probe"]["exact_call_count"])

    def test_sixty_cell_order_and_independent_prestates_are_bound(self) -> None:
        cells = load_contract()["cell_execution_binding"]
        self.assertEqual((2, 6, 5, 60, 10, 50), (
            len(cells["ordered_modality_ids"]),
            len(cells["ordered_system_ids"]),
            len(cells["ordered_probe_classes"]),
            cells["cell_count"],
            cells["candidate_cell_count"],
            cells["baseline_cell_count"],
        ))
        self.assertTrue(
            cells[
                "every_candidate_cell_uses_value_equal_copy_of_verified_formed_state"
            ]
        )
        self.assertFalse(cells["candidate_copy_may_be_reconstructed_from_summary"])
        self.assertFalse(cells["duplicate_missing_reordered_or_retried_cell_allowed"])

    def test_cell_and_matrix_receipt_roles_are_complete(self) -> None:
        contract = load_contract()
        self.assertEqual(19, len(contract["cell_receipt_roles"]))
        self.assertEqual(15, len(contract["matrix_receipt_roles"]))
        self.assertIn("STATE_UNCHANGED", contract["cell_receipt_roles"])
        self.assertIn("FINAL_DECISION", contract["matrix_receipt_roles"])

    def test_candidate_pass_requires_all_ten_cells_and_both_formations(self) -> None:
        required = load_contract()["candidate_function_decision"]["pass_requires"]
        self.assertIn("BOTH_FORMATIONS_MATCH_EXPECTED_TEMPLATE", required)
        self.assertIn("ALL_TEN_CANDIDATE_CELLS_EXIST_EXACTLY_ONCE", required)
        self.assertIn("ALL_TEN_CANDIDATE_PROBES_PRESERVE_STATE_AND_IDENTITY", required)

    def test_baseline_explanation_is_same_system_all_ten_behavioral_outputs(self) -> None:
        baseline = load_contract()["baseline_explanation_decision"]
        self.assertEqual(["RECOGNIZED", "NEAREST_DISTANCE_OR_NULL"], baseline["behavioral_roles"])
        self.assertTrue(baseline["one_baseline_must_match_all_ten_candidate_cells"])
        self.assertFalse(baseline["mixing_baselines_across_cells_allowed"])
        self.assertEqual(4, len(baseline["expected_explaining_baselines"]))
        self.assertFalse(baseline["no_memory_expected_to_explain"])

    def test_method_invalid_precedes_all_function_decisions(self) -> None:
        contract = load_contract()
        self.assertEqual(
            "METHOD_INVALID_STOP_WITHOUT_FUNCTION_DECISION",
            contract["decision_precedence"][0],
        )
        self.assertEqual(11, len(contract["method_invalid_conditions"]))
        self.assertFalse(contract["atomic_failure_rules"]["partial_matrix_receipt_allowed"])
        self.assertFalse(
            contract["atomic_failure_rules"][
                "failure_returns_function_or_baseline_decision"
            ]
        )

    def test_claim_boundary_keeps_result_and_capability_unproven(self) -> None:
        boundary = load_contract()["claim_boundary"]
        self.assertTrue(all(not value for value in boundary.values()))

    def test_no_execution_or_implementation_is_authorized(self) -> None:
        contract = load_contract()
        self.assertEqual(60, contract["planned_matrix_cell_count"])
        self.assertEqual(0, contract["executed_matrix_cell_count"])
        self.assertEqual(8, len(contract["current_prohibitions"]))
        self.assertIn("NO_RUNNER_RECEIPT_OR_DECISION_CODE", contract["current_prohibitions"])


if __name__ == "__main__":
    unittest.main()
