from __future__ import annotations

import unittest

from mcm_field_organism.controlled_audio_video_test_world import (
    controlled_reentry_world_family,
    run_controlled_test_world,
)
from mcm_field_organism.local_synaptic_memory_candidate import (
    LocalSynapticMemoryConfig,
    advance_local_synaptic_memory,
    initialize_local_synaptic_memory,
    local_relation_evidence,
    local_synaptic_memory_candidate_public_roles,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)


def evidence(values: tuple[float, ...]):
    return {
        f"relation.source.{index}.to.target.0": (
            f"source.{index}",
            "target.0",
            value,
        )
        for index, value in enumerate(values)
    }


class LocalSynapticMemoryCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = LocalSynapticMemoryConfig(
            flexible_rate=0.5,
            stabilization_rate=0.25,
            release_rate=0.2,
            local_budget=0.8,
        )

    def test_exact_zero_evidence_cannot_create_a_relation(self) -> None:
        input_evidence = evidence((0.0, 0.0))
        state = initialize_local_synaptic_memory(input_evidence)

        for _ in range(20):
            state = advance_local_synaptic_memory(
                state,
                input_evidence,
                self.config,
            )

        self.assertTrue(
            all(
                relation.flexible == 0.0 and relation.stabilized == 0.0
                for relation in state.relations
            )
        )

    def test_repeated_local_coactivity_builds_flexible_and_stable_efficacy(self) -> None:
        input_evidence = evidence((0.8, 0.0))
        state = initialize_local_synaptic_memory(input_evidence)

        for _ in range(12):
            state = advance_local_synaptic_memory(
                state,
                input_evidence,
                self.config,
            )

        self.assertGreater(state.relations[0].flexible, 0.79)
        self.assertGreater(state.relations[0].stabilized, 0.0)
        self.assertEqual(0.0, state.relations[1].stabilized)

    def test_absent_coactivity_releases_but_does_not_instantly_erase(self) -> None:
        contact = evidence((0.8,))
        quiet = evidence((0.0,))
        state = initialize_local_synaptic_memory(contact)
        for _ in range(12):
            state = advance_local_synaptic_memory(state, contact, self.config)
        carried = state.relations[0].stabilized

        state = advance_local_synaptic_memory(state, quiet, self.config)

        self.assertLess(state.relations[0].stabilized, carried)
        self.assertGreater(state.relations[0].stabilized, 0.0)

    def test_local_homeostasis_bounds_competing_relations(self) -> None:
        input_evidence = evidence((1.0, 1.0, 1.0))
        state = initialize_local_synaptic_memory(input_evidence)
        for _ in range(40):
            state = advance_local_synaptic_memory(
                state,
                input_evidence,
                self.config,
            )

        self.assertLessEqual(
            sum(abs(item.stabilized) for item in state.relations),
            self.config.local_budget + 1e-12,
        )
        self.assertTrue(all(item.stabilized > 0.0 for item in state.relations))

    def test_real_test_world_field_can_supply_only_local_evidence(self) -> None:
        world, _ = controlled_reentry_world_family()
        result = run_controlled_test_world(
            world,
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
        )

        observed = local_relation_evidence(result.field_run.field)
        state = initialize_local_synaptic_memory(observed)

        self.assertTrue(observed)
        self.assertEqual(len(observed), len(state.relations))
        self.assertTrue(any(abs(item[2]) > 0.0 for item in observed.values()))
        self.assertTrue(
            all(
                relation.source_neuron_id != relation.target_neuron_id
                for relation in state.relations
            )
        )

    def test_public_contract_contains_no_semantics_or_reward(self) -> None:
        roles = set(local_synaptic_memory_candidate_public_roles())
        self.assertTrue(
            {
                "label",
                "meaning",
                "object_id",
                "class_id",
                "reward",
                "winner",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
