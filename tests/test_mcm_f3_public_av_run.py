from __future__ import annotations

import unittest

from mcm_field_organism.mcm_f3_public_av_run import (
    mcm_f3_public_av_run_public_roles,
    nasa_mcm_f3_preregistration,
)


class MCMF3PublicAVRunTests(unittest.TestCase):
    def test_preregistration_binds_source_parameters_arms_and_nonclaims(self) -> None:
        plan = nasa_mcm_f3_preregistration()

        self.assertEqual((0, 500_000_000), (plan.start_tick, plan.end_tick))
        self.assertEqual((41, 15), (plan.expected_auditory_frames, plan.expected_visual_frames))
        self.assertEqual((1.0, 0.5), (plan.response_time_seconds, plan.afterimage_time_constant_seconds))
        self.assertEqual((1.0, 0.5, 1.0), (
            plan.active_arm.lambda_sm_per_second,
            plan.active_arm.kappa,
            plan.active_arm.eta,
        ))
        self.assertEqual(7, len(plan.arm_keys))
        self.assertIn("b.kappa-inverted", plan.arm_keys)
        self.assertFalse(plan.dissipation_enabled)
        self.assertFalse(plan.memory_claim_allowed)
        self.assertFalse(plan.ai_claim_allowed)

    def test_public_result_roles_exclude_raw_media_and_meaning(self) -> None:
        roles = set(mcm_f3_public_av_run_public_roles())

        self.assertNotIn("raw_samples", roles)
        self.assertNotIn("pixels", roles)
        self.assertNotIn("labels", roles)
        self.assertNotIn("meaning", roles)


if __name__ == "__main__":
    unittest.main()
