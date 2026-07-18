from __future__ import annotations

import unittest

from mcm_field_organism import (
    centered_first_temporal_moment,
    run_temporal_directed_moment_audit,
    temporal_directed_moment_audit_public_roles,
    temporal_moment_collision_paths,
)


class TemporalDirectedMomentAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = run_temporal_directed_moment_audit()

    def test_directed_moment_is_refinement_invariant_for_constant_path(self) -> None:
        self.assertTrue(self.result.representation_invariance_rechecked)
        self.assertAlmostEqual(0.0, self.result.dense_constant_moment)
        self.assertAlmostEqual(0.0, self.result.sparse_constant_moment)

    def test_directed_moment_distinguishes_time_reversal(self) -> None:
        self.assertTrue(self.result.reversal_paths_distinguished)
        self.assertTrue(self.result.reversal_antisymmetry_observed)
        self.assertAlmostEqual(
            self.result.reversal_first_moment,
            -self.result.reversal_second_moment,
        )

    def test_directed_moment_still_has_an_order_collision(self) -> None:
        self.assertTrue(self.result.collision_paths_distinct)
        self.assertTrue(self.result.collision_moments_equal)
        self.assertAlmostEqual(
            self.result.collision_first_moment,
            self.result.collision_second_moment,
        )

    def test_observer_is_fixed_width_but_not_unique(self) -> None:
        self.assertEqual(1, self.result.observer_width)
        self.assertTrue(self.result.observer_width_fixed)
        self.assertFalse(self.result.unique_order_encoding_proven)

    def test_no_field_effect_or_runtime_is_released(self) -> None:
        self.assertFalse(self.result.field_effect_performed)
        self.assertFalse(self.result.runtime_candidate_released)

    def test_public_collision_paths_reproduce_the_equal_moment(self) -> None:
        paths = temporal_moment_collision_paths()
        self.assertAlmostEqual(
            centered_first_temporal_moment(paths.first),
            centered_first_temporal_moment(paths.second),
        )

    def test_public_roles_add_no_field_state_or_selection(self) -> None:
        forbidden = {
            "activation",
            "afterimage",
            "selected_representation",
            "storage_policy",
            "memory",
            "topology",
            "weight",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                temporal_directed_moment_audit_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
