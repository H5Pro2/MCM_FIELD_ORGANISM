from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    ROOT
    / "docs"
    / "S1WX_PPB1_STATISCHER_VOLLSTAENDIGKEITS_FAIRNESS_UND_NICHTZIRKULARITAETSAUDIT_V1.json"
)
EXPECTED_AUDIT_DIGEST = (
    "604b9b52d32dcd5b0bf5e00c91d043f459c22e122eb1f52300826fd33bbed0fd"
)


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


class PPB1S1WXStaticCompletenessFairnessAuditTests(unittest.TestCase):
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

    def test_s1ww_source_and_canonical_digests_are_bound(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "d37006947a0b71be113519b4204b742b9c459a2cdc2e0bb755f4888f0f9143da",
            audit["s1ww_contract_canonical_digest"],
        )
        self.assertEqual(
            "ec2471b2708bb328b73c5bcbd6a97f692606ddf005267f0bcc51817f012fa36e",
            audit["s1ww_contract_file_digest"],
        )

    def test_twelve_checks_pass_and_four_fail_closed(self) -> None:
        audit = load_audit()
        self.assertEqual(12, audit["positive_check_count"])
        self.assertEqual(4, audit["negative_check_count"])
        self.assertEqual(16, len(audit["checks"]))
        self.assertEqual(12, sum(audit["checks"].values()))

    def test_exact_four_correction_blockers_are_bound(self) -> None:
        audit = load_audit()
        self.assertEqual(4, audit["blocker_count"])
        self.assertEqual(
            {
                "S1WX_THRESHOLD_REACHABILITY_UNBOUND",
                "S1WX_BASELINE_EXPLANATION_OUTPUT_SET_AMBIGUOUS",
                "S1WX_NO_MEMORY_STATE_DIGEST_ROLE_UNDEFINED",
                "S1WX_MODALITY_AGGREGATION_UNBOUND",
            },
            {blocker["blocker_id"] for blocker in audit["blockers"]},
        )

    def test_existing_formation_probe_fairness_and_claim_checks_remain_valid(self) -> None:
        checks = load_audit()["checks"]
        for role in (
            "formation_stabilization_and_evidence_roles_are_complete",
            "every_probe_arm_starts_from_exact_frozen_prestate",
            "three_positive_and_two_negative_expectations_are_prebound",
            "candidate_and_five_required_baselines_are_present",
            "formation_gap_probe_and_information_boundaries_are_fair",
            "probe_and_bank_immutability_are_complete",
            "claim_boundary_blocks_current_and_mcm_specific_claims",
        ):
            self.assertTrue(checks[role], role)

    def test_reachability_explanation_no_state_and_aggregation_are_not_assumed(self) -> None:
        checks = load_audit()["checks"]
        for role in (
            "probe_distance_classes_are_reachable_for_every_admissible_config",
            "baseline_explanation_compares_behavior_not_private_metadata",
            "no_memory_observed_state_digest_semantics_are_defined",
            "aggregate_pass_requires_both_modalities_and_all_probe_classes",
        ):
            self.assertFalse(checks[role], role)

    def test_no_formation_probe_baseline_matrix_or_field_execution_occurred(self) -> None:
        audit = load_audit()
        for role in (
            "formation_execution_count",
            "probe_execution_count",
            "baseline_execution_count",
            "matrix_execution_count",
            "field_effect_count",
        ):
            self.assertEqual(0, audit[role], role)

    def test_decision_requires_static_correction_without_result(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "BLOCKED_STATIC_CONTRACT_CORRECTION_REQUIRED_NO_EXECUTION",
            audit["decision"],
        )
        self.assertEqual(
            "NO_TECHNICAL_FUNCTION_OR_MCM_MEMORY_RESULT",
            audit["claim_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
