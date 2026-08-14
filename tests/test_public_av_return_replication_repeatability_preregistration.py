from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_preregistration import (
    PublicAVReturnReplicationRepeatabilityPreregistrationError,
    public_av_return_replication_repeatability_preregistration,
    public_av_return_replication_repeatability_preregistration_json_value,
    public_av_return_replication_repeatability_preregistration_public_roles,
)


class PublicAVReturnReplicationRepeatabilityPreregistrationTests(unittest.TestCase):
    def test_preregisters_three_independent_repeats_without_releasing_run(self) -> None:
        plan = public_av_return_replication_repeatability_preregistration()
        self.assertEqual(3, plan.independent_repeat_count)
        self.assertEqual((1, 2, 3), plan.repeat_index_set)
        self.assertFalse(plan.runner_implementation_allowed)
        self.assertFalse(plan.repeatability_run_allowed)

    def test_all_four_causal_contrasts_are_bound_to_fixed_arm_pairs(self) -> None:
        plan = public_av_return_replication_repeatability_preregistration()
        self.assertEqual(4, len(plan.contrast_roles))
        by_id = {item.contrast_id: item for item in plan.contrast_roles}
        self.assertEqual(
            ("return.continued.full_state", "return.fresh_stage_two"),
            (by_id["full_state_vs_fresh_stage_two"].left_arm_id, by_id["full_state_vs_fresh_stage_two"].right_arm_id),
        )
        self.assertEqual(
            ("control.activation_only_carry", "control.afterimage_only_carry"),
            (
                by_id["activation_only_vs_afterimage_only"].left_arm_id,
                by_id["activation_only_vs_afterimage_only"].right_arm_id,
            ),
        )
        self.assertEqual(
            ("return.continued.full_state", "control.stage_two_order_permuted"),
            (
                by_id["full_state_vs_permuted_stage_two"].left_arm_id,
                by_id["full_state_vs_permuted_stage_two"].right_arm_id,
            ),
        )
        self.assertEqual(
            ("return.continued.full_state", "control.stage_two_sequence_withheld"),
            (
                by_id["full_state_vs_withheld_stage_two"].left_arm_id,
                by_id["full_state_vs_withheld_stage_two"].right_arm_id,
            ),
        )

    def test_identical_contract_parameters_and_stability_roles_are_required(self) -> None:
        plan = public_av_return_replication_repeatability_preregistration()
        for role in (
            "same_source_contract",
            "same_permutation_contract_digest",
            "same_component_intervention_contract",
            "same_runner_wiring_contract",
            "same_field_parameters",
        ):
            self.assertIn(role, plan.contract_parameters_required_identical)
        for role in (
            "cross_repeat_activation_linf_min_max_range",
            "cross_repeat_afterimage_linf_min_max_range",
            "cross_repeat_digest_equality_pattern_consistency",
        ):
            self.assertIn(role, plan.stability_measurements)

    def test_release_threshold_and_claim_flags_are_constructively_blocked(self) -> None:
        plan = public_av_return_replication_repeatability_preregistration()
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityPreregistrationError, "cannot release"):
            replace(plan, repeatability_run_allowed=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityPreregistrationError, "cannot release"):
            replace(plan, memory_threshold_defined=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityPreregistrationError, "cannot release"):
            replace(plan, organization_claim_allowed=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityPreregistrationError, "exactly three"):
            replace(plan, independent_repeat_count=2)

    def test_json_and_public_roles_exclude_claim_scores(self) -> None:
        plan = public_av_return_replication_repeatability_preregistration()
        encoded = repr(public_av_return_replication_repeatability_preregistration_json_value(plan))
        self.assertIn("full_state_vs_fresh_stage_two", encoded)
        forbidden = {
            "memory_score",
            "organization_score",
            "meaning",
            "label",
            "reward",
            "success_threshold",
            "target_topology",
        }
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_repeatability_preregistration_public_roles()))


if __name__ == "__main__":
    unittest.main()
