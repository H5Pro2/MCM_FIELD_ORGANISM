from __future__ import annotations

import unittest

from mcm_field_organism.mcm_f3_k2b_run import (
    mcm_f3_k2b_preregistration,
    mcm_f3_k2b_run_public_roles,
)


class MCMF3K2BRunTests(unittest.TestCase):
    def test_preregistration_fixes_models_thresholds_and_nonclaims(self) -> None:
        plan = mcm_f3_k2b_preregistration()

        self.assertEqual(("f3-candidate", "linear-coupled-field"), plan.model_ids)
        self.assertEqual(5, plan.checkpoint_count)
        self.assertEqual(0.05, plan.functional_loss_limit)
        self.assertEqual(0.50, plan.competitive_advantage_factor)
        self.assertEqual(4, plan.refinement)
        self.assertFalse(plan.memory_claim_allowed)
        self.assertFalse(plan.ai_claim_allowed)

    def test_public_surface_has_no_content_roles(self) -> None:
        roles = set(mcm_f3_k2b_run_public_roles())

        self.assertTrue(
            {"labels", "meaning", "pixels", "raw_samples", "reward"}.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
