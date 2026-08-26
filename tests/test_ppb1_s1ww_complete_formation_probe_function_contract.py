from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "S1WW_PPB1_VOLLSTAENDIGER_BILDUNGS_UND_PROBE_FUNKTIONSVERTRAG_V1.json"
)
EXPECTED_CONTRACT_DIGEST = (
    "d37006947a0b71be113519b4204b742b9c459a2cdc2e0bb755f4888f0f9143da"
)


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class PPB1S1WWCompleteFormationProbeFunctionContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        payload = load_contract()
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(
            EXPECTED_CONTRACT_DIGEST,
            hashlib.sha256(encoded).hexdigest(),
        )

    def test_parent_chain_and_static_scope_are_exact(self) -> None:
        contract = load_contract()
        self.assertEqual(
            "99195245b2062fc472a59b90acb2421e82f583542094244666c118292b4bca7e",
            contract["parent_s1wv_audit_digest"],
        )
        self.assertEqual(
            "1e47680f9c340149c99e0fb182fc1f25d475b773ce34b37a9d2103fad05303ef",
            contract["bound_s1wu_source_digest"],
        )
        self.assertEqual(
            "STATIC_COMPLETE_FUNCTION_AND_FALSIFICATION_CONTRACT_NO_IMPLEMENTATION_OR_EXECUTION",
            contract["scope"],
        )

    def test_phase_order_and_formation_are_fully_bound(self) -> None:
        contract = load_contract()
        self.assertEqual(7, len(contract["phase_order"]))
        formation = contract["formation_contract"]
        self.assertEqual(
            "EXACT_BOUND_CONFIG_STABLE_AFTER",
            formation["formation_exposure_count"],
        )
        self.assertEqual(
            "PERCEPTUAL_STATE_STABILIZED",
            formation["required_terminal_event"],
        )
        self.assertTrue(formation["exactly_one_target_slot_required"])
        self.assertFalse(formation["raw_audio_or_video_allowed"])
        self.assertFalse(formation["semantic_or_object_role_allowed"])

    def test_evidence_and_frozen_probe_prestate_are_digest_exact(self) -> None:
        contract = load_contract()
        evidence = contract["stabilized_evidence_binding"]
        self.assertEqual(12, len(evidence["required_roles"]))
        self.assertFalse(evidence["raw_history_payload_in_evidence_allowed"])
        self.assertFalse(evidence["prototype_values_in_evidence_allowed"])
        frozen = contract["frozen_probe_prestate"]
        self.assertTrue(frozen["same_prestate_digest_for_every_probe_arm"])
        self.assertTrue(frozen["same_state_identity_digest_for_every_probe_arm"])
        self.assertFalse(frozen["clone_or_reconstruction_from_summary_allowed"])
        self.assertFalse(frozen["intervening_write_or_lifecycle_step_allowed"])

    def test_three_positive_and_two_negative_probe_classes_are_prebound(self) -> None:
        probes = load_contract()["probe_classes"]
        self.assertEqual(5, len(probes))
        self.assertEqual(
            [True, True, True, False, False],
            [probe["expected_recognized"] for probe in probes],
        )
        self.assertEqual(
            {
                "P_EXACT_POSITIVE",
                "P_NEAR_POSITIVE",
                "P_BOUNDARY_POSITIVE",
                "N_NEAR_NEGATIVE",
                "N_DISTINCT_NEGATIVE",
            },
            {probe["probe_class"] for probe in probes},
        )

    def test_probe_is_independent_read_only_and_all_deltas_are_zero(self) -> None:
        contract = load_contract()
        probe = contract["probe_contract"]
        self.assertEqual("PRIVATE_S1WU_READ_ONLY_ONLY", probe["probe_path"])
        self.assertTrue(probe["one_independent_probe_arm_per_probe_class"])
        self.assertFalse(probe["raw_formation_history_access_allowed"])
        self.assertFalse(probe["poststate_allowed"])
        self.assertFalse(probe["advance_call_allowed"])
        invariants = contract["immutability_requirements"]
        self.assertTrue(invariants["bank_state_digest_before_equals_after_each_probe"])
        self.assertTrue(invariants["state_identity_digest_before_equals_after_each_probe"])
        for role, value in invariants.items():
            if role.endswith("_count") or role.endswith("_delta"):
                self.assertEqual(0, value, role)

    def test_candidate_and_five_required_baselines_are_present(self) -> None:
        contract = load_contract()
        self.assertEqual(6, len(contract["systems_under_comparison"]))
        self.assertEqual(
            {
                "NO_MEMORY",
                "RAW_HISTORY_OR_REPLAY_ACCESS",
                "SIMPLE_STATIC_PROTOTYPE_BANK",
                "REVERBERATION_OR_MOVING_STATE",
                "SIMPLE_LAST_FORMATION_VECTOR_DISTANCE",
            },
            {
                baseline["baseline_id"]
                for baseline in contract["baseline_contracts"]
            },
        )

    def test_fairness_binds_histories_probes_metric_threshold_and_budgets(self) -> None:
        fairness = load_contract()["fairness_binding"]
        for role in (
            "same_modality_specific_formation_sequence",
            "same_gap_and_probe_frames",
            "same_probe_class_order_independence",
            "same_normalized_l1_metric_where_distance_is_used",
            "same_match_threshold_where_threshold_is_used",
            "same_read_only_probe_constraint",
            "storage_budget_must_be_reported_not_hidden",
            "replay_is_upper_information_control_not_equal_storage_claim",
        ):
            self.assertTrue(fairness[role], role)
        self.assertEqual(7, len(fairness["same_output_decision_roles"]))

    def test_minimum_matrix_is_sixty_cells_with_zero_execution(self) -> None:
        matrix = load_contract()["minimum_static_matrix"]
        self.assertEqual(
            (2, 6, 5, 60, 0),
            (
                matrix["modality_count"],
                matrix["system_count"],
                matrix["probe_class_count"],
                matrix["planned_cell_count"],
                matrix["execution_count"],
            ),
        )

    def test_success_and_failure_are_complete_and_mutually_decidable(self) -> None:
        contract = load_contract()
        success = contract["technical_function_success"]
        failure = contract["technical_function_failure"]
        self.assertEqual(6, len(success["required"]))
        self.assertEqual(6, len(failure["any_condition"]))
        self.assertEqual("TECHNICAL_MEMORY_FUNCTION_PASS", success["allowed_decision"])
        self.assertEqual("TECHNICAL_MEMORY_FUNCTION_FAIL", failure["required_decision"])

    def test_baseline_explanation_and_invalidity_are_separate_decisions(self) -> None:
        contract = load_contract()
        explanation = contract["baseline_explanation_decision"]
        self.assertFalse(
            explanation["unexplained_engineering_difference_is_mcm_specific_memory_claim"]
        )
        self.assertFalse(
            explanation["baseline_explanation_changes_candidate_function_pass"]
        )
        self.assertEqual(10, len(contract["method_invalid_conditions"]))
        self.assertEqual(
            "METHOD_INVALID_STOP_WITHOUT_FUNCTION_DECISION",
            contract["decision_precedence"][0],
        )

    def test_claims_implementation_execution_and_integration_remain_blocked(self) -> None:
        contract = load_contract()
        claims = contract["claim_boundary"]
        self.assertTrue(claims["technical_memory_function_is_testable"])
        self.assertFalse(claims["technical_memory_function_is_currently_demonstrated"])
        self.assertFalse(claims["independent_mcm_memory_is_demonstrated"])
        self.assertFalse(claims["field_causation_or_field_memory_claim_allowed"])
        self.assertEqual(7, len(contract["current_prohibitions"]))


if __name__ == "__main__":
    unittest.main()
