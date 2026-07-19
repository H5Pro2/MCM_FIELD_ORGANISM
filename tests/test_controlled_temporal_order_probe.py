from __future__ import annotations

import unittest

from mcm_field_organism import (
    controlled_temporal_order_probe_public_roles,
    run_controlled_temporal_order_probe,
)


class ControlledTemporalOrderProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_controlled_temporal_order_probe()

    def test_branches_use_the_same_two_world_phases_in_reverse_order(self) -> None:
        self.assertEqual(2, self.result.phase_count_per_branch)
        self.assertTrue(self.result.same_phase_multiset)

    def test_order_is_visible_but_reaches_every_local_relation(self) -> None:
        self.assertEqual(290, self.result.directed_relation_count)
        self.assertEqual(145, self.result.independent_local_pair_count)
        self.assertEqual(290, self.result.forward_nonzero_relation_count)
        self.assertEqual(290, self.result.reverse_nonzero_relation_count)
        self.assertTrue(self.result.every_local_relation_affected)
        self.assertFalse(self.result.selective_relation_source_shown)

    def test_most_signs_reverse_but_field_history_breaks_exact_reversal(self) -> None:
        self.assertEqual(250, self.result.opposed_sign_relation_count)
        self.assertEqual(40, self.result.same_sign_relation_count)
        self.assertTrue(self.result.reciprocal_antisymmetry_exact)
        self.assertFalse(self.result.exact_time_reversal_antisymmetry)
        self.assertGreater(self.result.reversal_relative_residual, 0.0)

    def test_measurement_is_exactly_reproducible(self) -> None:
        self.assertEqual(self.result, run_controlled_temporal_order_probe())

    def test_probe_is_only_a_fixed_passive_one_step_reader(self) -> None:
        self.assertEqual(1, self.result.observer_width)
        self.assertTrue(self.result.observer_is_fixed_one_step_reader)
        self.assertFalse(self.result.raw_sensor_payload_retained)
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.releases_memory_candidate)

    def test_public_result_has_no_semantics_selection_or_runtime_memory(self) -> None:
        forbidden = {
            "meaning",
            "label",
            "class_id",
            "reward",
            "winner",
            "threshold",
            "runtime_memory",
            "target_topology",
        }
        self.assertTrue(
            forbidden.isdisjoint(controlled_temporal_order_probe_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
