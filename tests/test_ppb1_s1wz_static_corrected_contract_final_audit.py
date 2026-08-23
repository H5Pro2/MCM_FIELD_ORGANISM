from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    ROOT
    / "docs"
    / "S1WZ_PPB1_STATISCHER_KORRIGIERTER_VERTRAGSABSCHLUSSAUDIT_V1.json"
)
EXPECTED_AUDIT_DIGEST = (
    "22b6972bd5f3b9c25f3aef28293aae4e4b4b7288de4b6736e5d876b33d4f9059"
)


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


class PPB1S1WZStaticCorrectedContractFinalAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        payload = load_audit()
        observed = payload.pop("audit_digest")
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, observed)
        self.assertEqual(observed, hashlib.sha256(encoded).hexdigest())

    def test_s1ww_s1wx_and_s1wy_canonical_digests_are_bound(self) -> None:
        self.assertEqual(
            {
                "s1ww": "d37006947a0b71be113519b4204b742b9c459a2cdc2e0bb755f4888f0f9143da",
                "s1wx": "604b9b52d32dcd5b0bf5e00c91d043f459c22e122eb1f52300826fd33bbed0fd",
                "s1wy": "3a37d4dfaf83661cf93ff6328be73fc65b159455112426c3878c934c3a1dc6c9",
            },
            load_audit()["canonical_digests"],
        )

    def test_all_twenty_checks_pass_without_remaining_blocker(self) -> None:
        audit = load_audit()
        self.assertEqual(20, audit["positive_check_count"])
        self.assertEqual(0, audit["negative_check_count"])
        self.assertEqual(20, len(audit["checks"]))
        self.assertTrue(all(audit["checks"].values()))
        self.assertEqual(4, audit["closed_blocker_count"])
        self.assertEqual(0, audit["remaining_blocker_count"])

    def test_reachability_checks_pass_for_both_modalities(self) -> None:
        checks = load_audit()["checks"]
        for role in (
            "auditory_threshold_inside_existing_corridor",
            "visual_threshold_inside_existing_corridor",
            "auditory_five_probe_relations_reachable",
            "visual_five_probe_relations_reachable",
            "all_zero_formation_target_is_dimension_independent_and_bounded",
        ):
            self.assertTrue(checks[role], role)

    def test_baseline_behavior_metadata_and_no_memory_are_noncircular(self) -> None:
        checks = load_audit()["checks"]
        for role in (
            "behavioral_explanation_uses_only_decision_and_distance",
            "behavioral_and_metadata_roles_are_disjoint",
            "one_baseline_must_explain_all_ten_without_cell_mixing",
            "no_memory_null_roles_and_zero_budget_are_complete",
            "no_memory_fabricated_digest_is_forbidden",
        ):
            self.assertTrue(checks[role], role)

    def test_aggregation_matrix_and_decision_precedence_are_complete(self) -> None:
        checks = load_audit()["checks"]
        for role in (
            "all_of_aggregation_requires_both_modalities_and_ten_cells",
            "wrong_present_cell_and_missing_cell_have_distinct_decisions",
            "sixty_cell_matrix_arithmetic_is_complete_and_unexecuted",
            "method_invalidity_precedes_function_and_explanation",
        ):
            self.assertTrue(checks[role], role)

    def test_no_fixture_formation_probe_baseline_matrix_or_field_execution_occurred(self) -> None:
        audit = load_audit()
        for role in (
            "fixture_implementation_count",
            "formation_execution_count",
            "probe_execution_count",
            "baseline_execution_count",
            "matrix_execution_count",
            "field_effect_count",
        ):
            self.assertEqual(0, audit[role], role)

    def test_decision_allows_only_later_static_fixture_materialization(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "PASS_CORRECTED_COMPLETE_FUNCTION_CONTRACT_READY_FOR_STATIC_FIXTURE_MATERIALIZATION",
            audit["decision"],
        )
        self.assertEqual(
            "FINITE_TECHNICAL_MEMORY_FUNCTION_SPECIFICATION_NO_FUNCTION_RESULT_OR_MCM_MEMORY_CLAIM",
            audit["claim_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
