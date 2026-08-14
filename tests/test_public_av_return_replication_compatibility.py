from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_compatibility import (
    PublicAVReturnReplicationCompatibilityError,
    audit_public_av_return_replication_compatibility,
    public_av_return_replication_compatibility_json_value,
    public_av_return_replication_compatibility_public_roles,
)


class PublicAVReturnReplicationCompatibilityTests(unittest.TestCase):
    def test_existing_full_fresh_and_withheld_paths_are_supported(self) -> None:
        audit = audit_public_av_return_replication_compatibility()
        by_id = {arm.arm_id: arm for arm in audit.arms}
        self.assertTrue(by_id["return.continued.full_state"].existing_runtime_supports_arm)
        self.assertTrue(by_id["return.fresh_stage_two"].existing_runtime_supports_arm)
        self.assertTrue(by_id["control.stage_two_sequence_withheld"].existing_runtime_supports_arm)
        self.assertEqual(
            "contact_free_field_step.stage_two_horizon",
            by_id["control.stage_two_sequence_withheld"].runtime_path,
        )

    def test_component_interventions_are_validated_observer_contracts(self) -> None:
        audit = audit_public_av_return_replication_compatibility()
        by_id = {arm.arm_id: arm for arm in audit.arms}
        self.assertTrue(audit.component_state_interventions_supported)
        self.assertTrue(by_id["control.activation_only_carry"].existing_runtime_supports_arm)
        self.assertEqual(
            "component_intervention.reset_afterimage_preserve_activation",
            by_id["control.activation_only_carry"].runtime_path,
        )
        self.assertTrue(by_id["control.afterimage_only_carry"].existing_runtime_supports_arm)
        self.assertEqual(
            "component_intervention.reset_activation_preserve_afterimage",
            by_id["control.afterimage_only_carry"].runtime_path,
        )
        self.assertFalse(by_id["control.activation_only_carry"].special_state_rule_required)
        self.assertFalse(by_id["control.afterimage_only_carry"].special_state_rule_required)

    def test_permuted_sequence_uses_fully_specified_contract(self) -> None:
        audit = audit_public_av_return_replication_compatibility()
        arm = next(item for item in audit.arms if item.arm_id == "control.stage_two_order_permuted")
        self.assertTrue(audit.permuted_stage_two_contract_complete)
        self.assertTrue(arm.existing_runtime_supports_arm)
        self.assertTrue(arm.sequence_transform_fully_specified)
        self.assertEqual("permutation_contract.reverse_rank_stage_two", arm.runtime_path)
        self.assertIsNone(arm.blocker)

    def test_positive_structural_audit_releases_runner_implementation_not_run(self) -> None:
        audit = audit_public_av_return_replication_compatibility()
        self.assertTrue(audit.all_preregistered_arms_supported)
        self.assertTrue(audit.runner_implementation_allowed)
        self.assertFalse(audit.replication_run_allowed)
        with self.assertRaisesRegex(PublicAVReturnReplicationCompatibilityError, "cannot release"):
            replace(audit, replication_run_allowed=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationCompatibilityError, "must follow"):
            replace(audit, runner_implementation_allowed=False)

    def test_json_and_roles_exclude_payloads_and_claim_scores(self) -> None:
        audit = audit_public_av_return_replication_compatibility()
        encoded = repr(public_av_return_replication_compatibility_json_value(audit))
        self.assertIn("activation_only_carry", encoded)
        forbidden = {"samples", "pixels", "label", "reward", "memory_score", "organization_score"}
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_compatibility_public_roles()))


if __name__ == "__main__":
    unittest.main()
