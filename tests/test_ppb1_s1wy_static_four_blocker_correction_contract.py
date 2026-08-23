from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "docs"
    / "S1WY_PPB1_KORREKTURVERTRAG_SCHWELLE_BASELINE_NULLROLLE_AGGREGATION_V1.json"
)
EXPECTED_CONTRACT_DIGEST = (
    "3a37d4dfaf83661cf93ff6328be73fc65b159455112426c3878c934c3a1dc6c9"
)


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class PPB1S1WYStaticFourBlockerCorrectionContractTests(unittest.TestCase):
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

    def test_parent_chain_scope_and_exact_four_blockers_are_bound(self) -> None:
        contract = load_contract()
        self.assertEqual(
            "604b9b52d32dcd5b0bf5e00c91d043f459c22e122eb1f52300826fd33bbed0fd",
            contract["parent_s1wx_audit_digest"],
        )
        self.assertEqual(
            "d37006947a0b71be113519b4204b742b9c459a2cdc2e0bb755f4888f0f9143da",
            contract["parent_s1ww_contract_digest"],
        )
        self.assertEqual(
            "STATIC_FOUR_BLOCKER_CORRECTION_ONLY_NO_IMPLEMENTATION_OR_EXECUTION",
            contract["scope"],
        )
        self.assertEqual(4, len(contract["corrected_blocker_ids"]))

    def test_zero_target_and_two_inner_thresholds_are_exact(self) -> None:
        reachability = load_contract()["threshold_and_probe_reachability_override"]
        self.assertEqual(
            "ALL_ZERO_NORMALIZED_REDUCED_VECTOR_IN_BOUND_MODALITY_DIMENSION",
            reachability["formation_target"],
        )
        modalities = {item["modality_id"]: item for item in reachability["modalities"]}
        self.assertEqual(0.2, modalities["AUDITORY"]["match_threshold"])
        self.assertEqual(0.1, modalities["VISUAL"]["match_threshold"])
        self.assertFalse(reachability["formation_variation_allowed"])
        self.assertTrue(reachability["all_values_within_normalized_range"])

    def test_all_probe_distances_are_reachable_and_masks_follow_thresholds(self) -> None:
        reachability = load_contract()["threshold_and_probe_reachability_override"]
        for modality in reachability["modalities"]:
            values = list(modality["probe_component_values"].values())
            distances = list(modality["expected_normalized_l1_distances"].values())
            self.assertEqual(values, distances)
            self.assertTrue(all(0.0 <= value <= 1.0 for value in values))
            threshold = modality["match_threshold"]
            self.assertEqual(
                modality["expected_recognition_mask"],
                [distance <= threshold for distance in distances],
            )

    def test_behavioral_explanation_uses_only_decision_and_distance(self) -> None:
        explanation = load_contract()["baseline_explanation_override"]
        self.assertEqual(
            ["RECOGNIZED", "NEAREST_DISTANCE_OR_NULL"],
            explanation["behavioral_explanation_roles"],
        )
        self.assertEqual(1e-12, explanation["distance_comparison_absolute_tolerance"])
        self.assertFalse(explanation["metadata_equality_required_for_behavioral_explanation"])
        self.assertFalse(explanation["baseline_explanation_may_mix_different_baselines_across_cells"])

    def test_metadata_and_resources_are_reported_but_not_behavior(self) -> None:
        explanation = load_contract()["baseline_explanation_override"]
        self.assertEqual(8, len(explanation["metadata_roles_reported_separately"]))
        self.assertFalse(explanation["resource_superiority_is_behavioral_difference"])
        self.assertFalse(explanation["different_private_identity_is_behavioral_difference"])

    def test_no_memory_has_canonical_nullable_zero_storage_roles(self) -> None:
        no_memory = load_contract()["no_memory_null_role_override"]
        self.assertFalse(no_memory["observed_state_present"])
        for role in (
            "observed_state_digest_before",
            "observed_state_digest_after",
            "state_identity_digest",
            "state_provenance_digest",
            "nearest_distance",
        ):
            self.assertIsNone(no_memory[role], role)
        self.assertEqual(0, no_memory["storage_role_count"])
        self.assertEqual(0, no_memory["stored_scalar_value_count"])
        self.assertFalse(no_memory["recognized"])
        self.assertFalse(no_memory["fabricated_empty_state_digest_allowed"])

    def test_aggregation_requires_all_ten_candidate_cells(self) -> None:
        aggregation = load_contract()["modality_aggregation_override"]
        self.assertEqual(["AUDITORY", "VISUAL"], aggregation["required_modality_ids"])
        self.assertEqual(5, len(aggregation["required_probe_classes_per_modality"]))
        self.assertEqual(10, aggregation["required_candidate_cell_count"])
        self.assertFalse(aggregation["one_modality_may_substitute_for_the_other"])
        self.assertFalse(aggregation["partial_modality_pass_allowed"])

    def test_matrix_counts_and_decision_precedence_remain_unchanged(self) -> None:
        contract = load_contract()
        matrix = contract["unchanged_matrix_binding"]
        self.assertEqual((60, 10, 50, 0), (
            matrix["planned_cell_count"],
            matrix["candidate_cell_count"],
            matrix["baseline_cell_count"],
            matrix["execution_count"],
        ))
        self.assertEqual(
            "METHOD_INVALID_STOP_WITHOUT_FUNCTION_DECISION",
            contract["decision_precedence"][0],
        )

    def test_function_is_finite_but_unexecuted_and_claims_remain_blocked(self) -> None:
        contract = load_contract()
        claims = contract["claim_boundary"]
        self.assertTrue(claims["technical_memory_function_is_now_finitely_specified"])
        self.assertFalse(claims["technical_memory_function_is_demonstrated"])
        self.assertFalse(claims["independent_mcm_memory_is_demonstrated"])
        self.assertFalse(claims["baseline_nonexplanation_is_mcm_specific_memory_claim"])
        self.assertEqual(7, len(contract["current_prohibitions"]))


if __name__ == "__main__":
    unittest.main()
