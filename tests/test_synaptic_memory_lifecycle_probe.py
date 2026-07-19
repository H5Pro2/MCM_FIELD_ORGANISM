from __future__ import annotations

import unittest

from mcm_field_organism import (
    LocalSynapticMemoryConfig,
    controlled_memory_lifecycle_world,
    run_synaptic_memory_lifecycle_probe,
    synaptic_memory_lifecycle_probe_public_roles,
)


class SynapticMemoryLifecycleProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = LocalSynapticMemoryConfig(
            flexible_rate=0.5,
            stabilization_rate=0.25,
            release_rate=0.2,
            local_budget=0.8,
        )

    def test_world_has_build_interruption_and_rebinding_phases(self) -> None:
        world = controlled_memory_lifecycle_world()

        self.assertEqual(16.0, world.duration_seconds)
        self.assertEqual(4, sum(item.phase_id.startswith("build.") for item in world.phases))
        self.assertEqual(
            8,
            sum(item.phase_id.startswith("interrupt.") for item in world.phases),
        )
        self.assertEqual(
            4,
            sum(item.phase_id.startswith("rebind.") for item in world.phases),
        )

    def test_candidate_builds_but_does_not_fully_release_old_relations(self) -> None:
        result = run_synaptic_memory_lifecycle_probe(self.config)

        self.assertEqual(16, result.phase_count)
        self.assertGreater(result.built_relation_count, 0)
        self.assertGreater(result.candidate_build_l1, 0.0)
        self.assertGreater(result.candidate_after_interruption_l1, 0.0)
        self.assertFalse(result.candidate_old_relations_exactly_resolved)
        self.assertFalse(result.candidate_complete_lifecycle)

    def test_reexposure_changes_both_candidate_and_two_stage_baseline(self) -> None:
        result = run_synaptic_memory_lifecycle_probe(self.config)

        self.assertGreater(result.candidate_rebinding_change_l1, 0.0)
        self.assertGreater(result.two_stage_rebinding_change_l1, 0.0)
        self.assertFalse(result.two_stage_old_relations_exactly_resolved)
        self.assertLessEqual(
            result.candidate_max_local_budget_use,
            self.config.local_budget + 1e-12,
        )

    def test_probe_is_exactly_reproducible_and_passive(self) -> None:
        first = run_synaptic_memory_lifecycle_probe(self.config)
        second = run_synaptic_memory_lifecycle_probe(self.config)

        self.assertEqual(first, second)
        self.assertFalse(first.raw_sensor_payload_retained)
        self.assertFalse(first.writes_back)

    def test_public_result_contains_no_semantics_or_runtime_writeback(self) -> None:
        roles = set(synaptic_memory_lifecycle_probe_public_roles())
        self.assertTrue(
            {
                "label",
                "meaning",
                "class_id",
                "reward",
                "runtime_memory",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
