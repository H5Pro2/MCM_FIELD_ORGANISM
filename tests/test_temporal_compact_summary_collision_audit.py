from __future__ import annotations

import unittest

from mcm_field_organism import (
    compact_temporal_summary,
    run_temporal_compact_summary_collision_audit,
    temporal_adversarial_paths,
    temporal_compact_summary_collision_audit_public_roles,
)


class TemporalCompactSummaryCollisionAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = run_temporal_compact_summary_collision_audit()

    def test_paths_are_distinct_exact_time_reversals(self) -> None:
        self.assertTrue(self.result.paths_are_exact_time_reversals)
        self.assertTrue(self.result.supported_paths_distinct)
        self.assertEqual(
            self.result.first_supported_path[0].contact,
            self.result.reversed_supported_path[0].contact,
        )
        self.assertEqual(
            self.result.first_supported_path[-1].contact,
            self.result.reversed_supported_path[-1].contact,
        )

    def test_fixed_summary_bundle_collides(self) -> None:
        self.assertEqual(
            self.result.first_summary,
            self.result.reversed_summary,
        )
        self.assertTrue(self.result.summaries_equal)
        self.assertTrue(self.result.summary_width_fixed)
        self.assertEqual(13, self.result.summary_width)

    def test_collision_includes_variation_and_neighbor_statistics(self) -> None:
        summary = self.result.first_summary
        self.assertEqual(6, summary.segment_count)
        self.assertEqual(6, summary.total_duration)
        self.assertAlmostEqual(0.5, summary.duration_weighted_mean)
        self.assertAlmostEqual(2.0, summary.total_variation)
        self.assertAlmostEqual(1.0, summary.positive_variation)
        self.assertAlmostEqual(1.0, summary.negative_variation)
        self.assertAlmostEqual(1.06, summary.adjacent_product_sum)
        self.assertEqual(4, summary.turning_count)

    def test_summary_still_passes_registered_refinement_control(self) -> None:
        self.assertTrue(self.result.representation_invariance_rechecked)

    def test_observer_does_not_claim_general_impossibility_or_runtime(self) -> None:
        self.assertFalse(self.result.all_compact_representations_falsified)
        self.assertFalse(self.result.field_effect_performed)
        self.assertFalse(self.result.runtime_candidate_released)

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
                temporal_compact_summary_collision_audit_public_roles()
            )
        )

    def test_public_observers_are_deterministic(self) -> None:
        paths = temporal_adversarial_paths()
        self.assertEqual(
            compact_temporal_summary(paths.first),
            compact_temporal_summary(paths.first),
        )


if __name__ == "__main__":
    unittest.main()
