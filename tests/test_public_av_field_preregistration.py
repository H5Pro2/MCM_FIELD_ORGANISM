from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_field_preregistration import (
    PublicAVFieldPreregistrationError,
    public_av_field_preregistration_public_roles,
    public_av_passive_field_preregistration,
)


class PublicAVFieldPreregistrationTests(unittest.TestCase):
    def test_plan_fixes_joint_single_modality_and_partition_controls(self) -> None:
        plan = public_av_passive_field_preregistration()

        self.assertTrue(plan.preregistration_complete)
        self.assertEqual(6, len(plan.arms))
        self.assertIn("joint.coarse", {arm.arm_id for arm in plan.arms})
        self.assertIn("auditory_only.fine", {arm.arm_id for arm in plan.arms})
        self.assertIn("visual_only.fine", {arm.arm_id for arm in plan.arms})
        self.assertNotIn(
            "auditory_visual.withheld_control",
            {arm.arm_id for arm in plan.arms},
        )
        self.assertTrue(all(arm.fresh_field_required for arm in plan.arms))

    def test_plan_does_not_release_implementation_field_or_claims(self) -> None:
        plan = public_av_passive_field_preregistration()

        self.assertFalse(plan.field_runner_implementation_allowed)
        self.assertFalse(plan.field_run_allowed)
        self.assertFalse(plan.memory_claim_allowed)
        self.assertFalse(plan.meaning_claim_allowed)
        self.assertFalse(plan.organization_claim_allowed)
        self.assertFalse(plan.ai_claim_allowed)

    def test_release_flag_is_rejected(self) -> None:
        plan = public_av_passive_field_preregistration()

        with self.assertRaisesRegex(PublicAVFieldPreregistrationError, "cannot release"):
            replace(plan, field_run_allowed=True)

    def test_public_roles_exclude_content_programming(self) -> None:
        forbidden = {
            "label",
            "meaning",
            "reward",
            "target_topology",
            "desired_response",
            "receptor_values",
            "raw_audio",
            "raw_video",
        }
        self.assertTrue(
            forbidden.isdisjoint(public_av_field_preregistration_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
