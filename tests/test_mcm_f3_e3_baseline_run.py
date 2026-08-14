from __future__ import annotations

import unittest

from mcm_field_organism.mcm_f3_e3_baseline_run import (
    mcm_f3_e3_baseline_run_public_roles,
    mcm_f3_e3_preregistration,
)


class MCMF3E3BaselineRunTests(unittest.TestCase):
    def test_preregistration_fixes_budget_and_threshold(self) -> None:
        plan = mcm_f3_e3_preregistration()

        self.assertEqual(3, len(plan.baseline_ids))
        self.assertEqual(4, len(plan.intervention_ids))
        self.assertEqual(0.05, plan.relative_residual_limit)
        self.assertEqual(4, plan.refinement)
        self.assertFalse(plan.memory_claim_allowed)
        self.assertFalse(plan.ai_claim_allowed)

    def test_public_result_surface_contains_no_content_roles(self) -> None:
        roles = set(mcm_f3_e3_baseline_run_public_roles())

        self.assertTrue(
            {"labels", "meaning", "pixels", "raw_samples", "reward"}.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
