from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_two_stage_return_preregistration import (
    PublicAVTwoStageReturnPreregistrationError,
    public_av_two_stage_return_preregistration,
    public_av_two_stage_return_preregistration_json_value,
    public_av_two_stage_return_preregistration_public_roles,
)


class PublicAVTwoStageReturnPreregistrationTests(unittest.TestCase):
    def test_plan_fixes_two_arms_same_sequence_and_intermediate_interval(self) -> None:
        plan = public_av_two_stage_return_preregistration()

        self.assertTrue(plan.preregistration_complete)
        self.assertEqual(500_000_000, plan.stage_duration_ticks)
        self.assertEqual(
            {"continued_field", "fresh_stage_two_baseline"},
            {arm.arm_id for arm in plan.arms},
        )
        for arm in plan.arms:
            self.assertEqual(arm.stage_one_sequence_id, arm.stage_two_sequence_id)
            self.assertEqual(100_000_000, arm.intermediate_interval_ticks)
            self.assertEqual("no_input_gap.step_time_only", arm.resolution_phase)

    def test_state_takeover_and_fresh_baseline_are_disjoint(self) -> None:
        plan = public_av_two_stage_return_preregistration()
        by_id = {arm.arm_id: arm for arm in plan.arms}

        self.assertTrue(by_id["continued_field"].carry_field_state_to_stage_two)
        self.assertFalse(by_id["continued_field"].fresh_field_before_stage_two)
        self.assertFalse(by_id["fresh_stage_two_baseline"].carry_field_state_to_stage_two)
        self.assertTrue(by_id["fresh_stage_two_baseline"].fresh_field_before_stage_two)

    def test_plan_does_not_release_runner_field_thresholds_or_claims(self) -> None:
        plan = public_av_two_stage_return_preregistration()

        self.assertFalse(plan.runner_implementation_allowed)
        self.assertFalse(plan.field_run_allowed)
        self.assertFalse(plan.memory_threshold_defined)
        self.assertFalse(plan.organization_threshold_defined)
        self.assertFalse(plan.memory_claim_allowed)
        self.assertFalse(plan.meaning_claim_allowed)
        self.assertFalse(plan.organization_claim_allowed)
        self.assertFalse(plan.ai_claim_allowed)

    def test_release_flag_is_rejected(self) -> None:
        plan = public_av_two_stage_return_preregistration()

        with self.assertRaisesRegex(
            PublicAVTwoStageReturnPreregistrationError,
            "cannot release",
        ):
            replace(plan, field_run_allowed=True)

    def test_forbidden_measurement_is_rejected(self) -> None:
        plan = public_av_two_stage_return_preregistration()

        with self.assertRaisesRegex(
            PublicAVTwoStageReturnPreregistrationError,
            "forbidden",
        ):
            replace(plan, measured_roles=plan.measured_roles + ("memory_score",))

    def test_json_and_public_roles_exclude_payloads_labels_and_claim_scores(self) -> None:
        plan = public_av_two_stage_return_preregistration()
        payload = public_av_two_stage_return_preregistration_json_value(plan)
        encoded = repr(payload)

        self.assertIn("continued_field", encoded)
        self.assertNotIn("raw_samples", encoded)
        self.assertNotIn("pixels", encoded)
        forbidden = {
            "raw_samples",
            "pixels",
            "metadata",
            "label",
            "reward",
            "target_topology",
            "memory_score",
            "organization_score",
        }
        self.assertTrue(
            forbidden.isdisjoint(public_av_two_stage_return_preregistration_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
