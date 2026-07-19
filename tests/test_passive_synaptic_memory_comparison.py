from __future__ import annotations

import unittest

from mcm_field_organism.local_synaptic_memory_candidate import (
    LocalSynapticMemoryConfig,
)
from mcm_field_organism.passive_synaptic_memory_comparison import (
    passive_synaptic_memory_comparison_public_roles,
    run_passive_synaptic_memory_comparison,
)


class PassiveSynapticMemoryComparisonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = LocalSynapticMemoryConfig(
            flexible_rate=0.5,
            stabilization_rate=0.25,
            release_rate=0.2,
            local_budget=0.8,
        )

    def test_common_prefix_and_common_probe_are_exact_controls(self) -> None:
        result = run_passive_synaptic_memory_comparison(self.config)

        self.assertEqual(0.0, result.common_prefix_max_error)
        self.assertGreater(result.history_evidence_l1, 0.0)
        self.assertEqual(0.0, result.null_baseline_l1)
        self.assertEqual(0.0, result.instantaneous_baseline_l1)
        self.assertEqual(0.0, result.fixed_baseline_l1)

    def test_candidate_and_leaky_baseline_both_retain_history(self) -> None:
        result = run_passive_synaptic_memory_comparison(self.config)

        self.assertGreater(result.leaky_baseline_l1, 0.0)
        self.assertGreater(result.two_stage_leaky_baseline_l1, 0.0)
        self.assertGreater(result.candidate_flexible_l1, 0.0)
        self.assertGreater(result.candidate_stabilized_l1, 0.0)
        self.assertFalse(result.raw_sensor_payload_retained)
        self.assertFalse(result.writes_back)

    def test_comparison_is_exactly_reproducible(self) -> None:
        first = run_passive_synaptic_memory_comparison(self.config)
        second = run_passive_synaptic_memory_comparison(self.config)

        self.assertEqual(first, second)

    def test_public_result_has_no_semantic_or_runtime_memory_role(self) -> None:
        roles = set(passive_synaptic_memory_comparison_public_roles())
        self.assertTrue(
            {
                "label",
                "meaning",
                "object_id",
                "class_id",
                "reward",
                "runtime_writeback",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
