from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism.mcm_f3_geometry_run import (
    _normalized_controls,
    mcm_f3_geometry_preregistration,
    mcm_f3_geometry_run_public_roles,
)


class MCMF3GeometryRunTests(unittest.TestCase):
    def test_preregistration_binds_geometry_and_nonclaims(self) -> None:
        plan = mcm_f3_geometry_preregistration()

        self.assertEqual(84, plan.reflection_pair_count)
        self.assertEqual(36, plan.mask_size)
        self.assertEqual(4, plan.refinement)
        self.assertEqual(6, len(plan.arm_suffixes))
        self.assertFalse(plan.memory_claim_allowed)
        self.assertFalse(plan.ai_claim_allowed)

    def test_result_surface_has_no_labels_or_raw_media(self) -> None:
        roles = set(mcm_f3_geometry_run_public_roles())

        self.assertTrue({"labels", "meaning", "pixels", "raw_samples", "reward"}.isdisjoint(roles))

    def test_observer_controls_are_native_json_booleans(self) -> None:
        controls = _normalized_controls((("numpy", np.bool_(True)), ("native", False)))

        self.assertEqual((("numpy", True), ("native", False)), controls)
        self.assertTrue(all(type(value) is bool for _, value in controls))


if __name__ == "__main__":
    unittest.main()
