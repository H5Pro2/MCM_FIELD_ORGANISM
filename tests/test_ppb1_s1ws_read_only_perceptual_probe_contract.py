from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "docs" / "S1WS_PPB1_READ_ONLY_PERZEPTIVER_PROBEVERTRAG_V1.json"
)
EXPECTED_CONTRACT_DIGEST = (
    "909d3dc3d01ec3b94b53f0c770e615364e08ecb0b91f3aaefc72daf3aa834559"
)


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class PPB1S1WSReadOnlyPerceptualProbeContractTests(unittest.TestCase):
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

    def test_parent_sources_and_static_scope_are_exact(self) -> None:
        contract = load_contract()
        self.assertEqual(
            "dcaec4ee7ecb7e959412b34f96e17364f311c6d266e762eb231c6a0b1e81c676",
            contract["parent_s1wr_audit_digest"],
        )
        self.assertEqual(
            "7b21391ee86ce597c9434d46fe3d76cf3d8dbe8a65f2da49555ad2b26a203954",
            contract["bound_s1wq_source_digest"],
        )
        self.assertEqual(
            "STATIC_READ_ONLY_PROBE_CONTRACT_NO_IMPLEMENTATION_OR_EXECUTION",
            contract["scope"],
        )

    def test_probe_input_is_reduced_later_and_bank_bound(self) -> None:
        probe = load_contract()["probe_input"]
        self.assertEqual(13, len(probe["required_roles"]))
        self.assertTrue(probe["same_bank_binding_required"])
        self.assertTrue(probe["same_modality_geometry_and_carrier_order_required"])
        self.assertTrue(
            probe["probe_must_be_causally_later_than_committed_bank_contact"]
        )
        self.assertFalse(probe["raw_audio_or_video_allowed"])
        self.assertFalse(probe["semantic_or_object_role_allowed"])

    def test_only_stabilized_occupied_slots_are_eligible(self) -> None:
        eligible = load_contract()["eligible_private_state"]
        self.assertEqual("OCCUPIED_AND_STABILIZED_ONLY", eligible["slot_policy"])
        self.assertFalse(eligible["unstabilized_slot_eligible"])
        self.assertFalse(eligible["free_slot_eligible"])
        self.assertFalse(eligible["probe_may_expire_or_replace_slot"])
        self.assertFalse(eligible["probe_may_change_slot_eligibility"])

    def test_comparison_uses_existing_metric_and_deterministic_tie_break(self) -> None:
        comparison = load_contract()["comparison_rule"]
        self.assertEqual(
            "EXISTING_DIMENSION_NORMALIZED_L1_DISTANCE",
            comparison["metric_family"],
        )
        self.assertEqual(
            ["LOWEST_DISTANCE", "LEXICOGRAPHIC_SLOT_ID"],
            comparison["tie_break_order"],
        )
        self.assertTrue(comparison["same_state_and_probe_must_be_deterministic"])
        self.assertFalse(comparison["metric_or_threshold_update_allowed"])

    def test_finding_contains_no_poststate_values_semantics_or_field_effect(self) -> None:
        finding = load_contract()["read_only_finding"]
        self.assertEqual(14, len(finding["required_roles"]))
        self.assertFalse(finding["poststate_role_allowed"])
        self.assertFalse(finding["prototype_values_in_finding_allowed"])
        self.assertFalse(finding["semantic_label_in_finding_allowed"])
        self.assertFalse(finding["field_effect_in_finding_allowed"])

    def test_all_state_and_effect_deltas_are_zero(self) -> None:
        invariants = load_contract()["read_only_invariants"]
        self.assertTrue(invariants["bank_state_digest_before_equals_after"])
        self.assertTrue(invariants["state_identity_digest_before_equals_after"])
        for role, value in invariants.items():
            if role.endswith("_count") or role.endswith("_delta"):
                self.assertEqual(0, value, role)

    def test_fail_closed_rules_cover_identity_history_write_and_output(self) -> None:
        rules = load_contract()["fail_closed_rules"]
        self.assertEqual(6, len(rules))
        conditions = {rule["condition"] for rule in rules}
        self.assertTrue(
            {
                "BANK_CONFIG_STATE_OR_IDENTITY_DIGEST_MISMATCH",
                "PROBE_IS_NOT_CAUSALLY_LATER_THAN_COMMITTED_BANK_CONTACT",
                "ANY_STATE_OR_LIFECYCLE_VALUE_CHANGES",
                "ANY_ADVANCE_FILE_FIELD_SEMANTIC_OR_PRODUCTION_PATH_IS_REACHED",
            }.issubset(conditions)
        )

    def test_falsification_requires_determinism_boundary_and_no_hidden_write(self) -> None:
        requirements = set(load_contract()["later_falsification_requirements"])
        self.assertEqual(8, len(requirements))
        self.assertTrue(
            {
                "IDENTICAL_STATE_AND_PROBE_MUST_RETURN_IDENTICAL_FINDING",
                "DISTANCE_AT_THRESHOLD_MUST_RECOGNIZE",
                "DISTANCE_ABOVE_THRESHOLD_MUST_NOT_RECOGNIZE",
                "REPEATED_PROBE_MUST_NOT_ACCUMULATE_SUPPORT_OR_DELAY_EXPIRY",
                "ANY_HIDDEN_WRITE_OR_ADVANCE_CALL_STOPS_THE_PROBE_BRANCH",
            }.issubset(requirements)
        )

    def test_implementation_execution_integration_and_claims_remain_blocked(self) -> None:
        prohibitions = set(load_contract()["current_prohibitions"])
        self.assertEqual(9, len(prohibitions))
        self.assertTrue(
            {
                "NO_PROBE_IMPLEMENTATION",
                "NO_PROBE_OR_STATE_FUNCTION_EXECUTION",
                "NO_STATE_MUTATION",
                "NO_FIELD_SNAPSHOT_CHANGE",
                "NO_PUBLIC_API_OR_PRODUCTION_PATH",
                "NO_FIELD_FEEDBACK",
                "NO_SEMANTIC_LABEL_OR_WORD",
                "NO_REAL_FIELD_OR_MEDIA_RUN",
                "NO_MEMORY_FUNCTION_OR_CAPABILITY_CLAIM",
            }.issubset(prohibitions)
        )


if __name__ == "__main__":
    unittest.main()
