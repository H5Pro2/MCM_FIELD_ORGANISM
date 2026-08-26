from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_preregistration import (
    PublicAVReturnReplicationPreregistrationError,
    public_av_return_replication_preregistration,
    public_av_return_replication_preregistration_json_value,
    public_av_return_replication_preregistration_public_roles,
)


class PublicAVReturnReplicationPreregistrationTests(unittest.TestCase):
    def test_six_causal_replication_arms_are_fixed(self) -> None:
        plan = public_av_return_replication_preregistration()
        self.assertEqual(6, len(plan.arms))
        self.assertEqual(
            {
                "return.continued.full_state",
                "return.fresh_stage_two",
                "control.activation_only_carry",
                "control.afterimage_only_carry",
                "control.stage_two_order_permuted",
                "control.stage_two_sequence_withheld",
            },
            {arm.arm_id for arm in plan.arms},
        )

    def test_causal_roles_separate_residual_afterimage_and_sequence_return(self) -> None:
        plan = public_av_return_replication_preregistration()
        roles = {arm.causal_contrast_role for arm in plan.arms}
        self.assertIn("linear_residual_counterbaseline", roles)
        self.assertIn("afterimage_counterbaseline", roles)
        self.assertIn("sequence_order_counterbaseline", roles)
        self.assertIn("no_world_return_counterbaseline", roles)
        self.assertIn("separate_linear_activation_residual_from_afterimage_trace", plan.causal_questions)
        self.assertIn("separate_stage_two_world_contact_from_contact_free_continuation", plan.causal_questions)

    def test_preregistration_does_not_release_runs_thresholds_or_claims(self) -> None:
        plan = public_av_return_replication_preregistration()
        self.assertTrue(plan.preregistration_complete)
        self.assertFalse(plan.replication_run_allowed)
        self.assertFalse(plan.runner_implementation_allowed)
        self.assertFalse(plan.memory_threshold_defined)
        self.assertFalse(plan.organization_threshold_defined)
        self.assertFalse(plan.positive_effect_required)
        with self.assertRaisesRegex(PublicAVReturnReplicationPreregistrationError, "cannot release"):
            replace(plan, replication_run_allowed=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationPreregistrationError, "cannot release"):
            replace(plan, memory_claim_allowed=True)

    def test_no_claim_measurement_or_positive_outcome_is_encoded(self) -> None:
        plan = public_av_return_replication_preregistration()
        forbidden = {
            "label",
            "meaning",
            "reward",
            "target_topology",
            "desired_response",
            "memory_score",
            "organization_score",
            "success_threshold",
        }
        self.assertTrue(forbidden.isdisjoint(plan.measured_roles))
        self.assertIn("no_positive_minimum_difference", plan.required_invariants)
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_preregistration_public_roles()))

    def test_json_keeps_withheld_stage_two_as_no_sequence_not_zero_contact_claim(self) -> None:
        encoded = public_av_return_replication_preregistration_json_value(
            public_av_return_replication_preregistration()
        )
        arms = {arm["arm_id"]: arm for arm in encoded["arms"]}
        self.assertEqual(
            "none.no-stage-two-receptor-sequence",
            arms["control.stage_two_sequence_withheld"]["stage_two_sequence_id"],
        )
        self.assertEqual(
            "carry_full_state_without_stage_two_receptors",
            arms["control.stage_two_sequence_withheld"]["stage_two_state_mode"],
        )


if __name__ == "__main__":
    unittest.main()
