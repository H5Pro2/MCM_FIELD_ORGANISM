from __future__ import annotations

import unittest

from mcm_field_organism import (
    abu_interaction_ground_null_public_roles,
    run_abu_interaction_ground_null,
)


class ABUInteractionGroundNullTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_abu_interaction_ground_null()

    def test_histories_reach_the_field_before_constructive_alignment(self) -> None:
        self.assertTrue(self.result.histories_distinct_before_alignment)
        self.assertGreater(self.result.u_effect_at_b_before_alignment, 0.0)
        self.assertEqual(
            {"Y00", "Y10", "Y01", "Y11", "Z00", "Z10", "Z01", "Z11"},
            {item.branch_id for item in self.result.branches},
        )

    def test_primary_and_u_interaction_residuals_are_zero(self) -> None:
        self.assertEqual(0.0, self.result.interaction_ab_max)
        self.assertEqual(0.0, self.result.interaction_ub_max)
        self.assertEqual((0.0,) * 8, self.result.interaction_ab)
        self.assertEqual((0.0,) * 8, self.result.interaction_ub)
        self.assertTrue(self.result.probe_responses_equal_after_matching)

    def test_solution_challenges_leave_no_hidden_a_effect(self) -> None:
        self.assertEqual({"D0", "D1"}, {item.challenge_id for item in self.result.solutions})
        self.assertTrue(all(item.response_max_error == 0.0 for item in self.result.solutions))

    def test_rebinding_branches_leave_no_hidden_a_effect(self) -> None:
        self.assertEqual({"D0", "D1"}, {item.challenge_id for item in self.result.rebindings})
        self.assertTrue(all(item.response_max_error == 0.0 for item in self.result.rebindings))

    def test_neutral_runtime_and_execution_controls_close(self) -> None:
        self.assertTrue(self.result.neutral_baseline_rebuild_exact)
        self.assertLessEqual(self.result.coarse_fine_max_error, 1e-12)
        self.assertLessEqual(self.result.reflection_max_error, 1e-12)
        self.assertLessEqual(self.result.translation_max_error, 1e-12)
        self.assertLessEqual(self.result.neuron_order_max_error, 1e-12)
        self.assertTrue(self.result.branch_order_exact)
        self.assertTrue(self.result.snapshot_resume_exact)

    def test_probe_adds_no_runtime_mechanism(self) -> None:
        self.assertFalse(self.result.observer_writeback_performed)
        self.assertFalse(self.result.persistent_state_added)
        self.assertFalse(self.result.runtime_candidate_released)

    def test_result_is_reproducible(self) -> None:
        self.assertEqual(
            "1c24ff931aa3cf53452612b2895602acd5f615a2a84403237c9f58d8bc5da249",
            self.result.digest(),
        )
        self.assertEqual(self.result.digest(), run_abu_interaction_ground_null().digest())

    def test_public_roles_do_not_expose_an_organization_mechanism(self) -> None:
        forbidden = {
            "capacity",
            "edge",
            "partner",
            "weight",
            "learning_rate",
            "threshold",
            "winner",
            "semantic_label",
            "meaning",
        }
        self.assertTrue(forbidden.isdisjoint(abu_interaction_ground_null_public_roles()))


if __name__ == "__main__":
    unittest.main()
