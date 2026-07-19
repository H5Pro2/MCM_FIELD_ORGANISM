from __future__ import annotations

import unittest

from mcm_field_organism import (
    instantaneous_field_flow_null_probe_public_roles,
    run_instantaneous_field_flow_null_probe,
)


class InstantaneousFieldFlowNullProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = run_instantaneous_field_flow_null_probe()

    def test_directed_edge_flow_is_antisymmetric(self) -> None:
        self.assertLessEqual(self.result.edge_antisymmetry_error, 1e-12)

    def test_local_divergence_is_the_existing_diffusion_generator(self) -> None:
        self.assertLessEqual(self.result.generator_identity_error, 1e-12)
        self.assertLessEqual(self.result.total_divergence_error, 1e-12)
        self.assertTrue(
            any(
                abs(node.local_divergence) > 1e-6
                for node in self.result.observation.nodes
            )
        )

    def test_public_prior_field_samples_reconstruct_the_same_flow(self) -> None:
        self.assertLessEqual(self.result.perception_identity_error, 1e-12)

    def test_observation_order_and_matched_fast_state_add_no_flow_information(
        self,
    ) -> None:
        self.assertTrue(self.result.order_invariant)
        self.assertTrue(self.result.fast_matched_full_states_distinct)
        self.assertTrue(self.result.fast_matched_flow_equal)

    def test_observer_does_not_modify_or_extend_the_runtime(self) -> None:
        self.assertTrue(self.result.observer_preserved_source_digest)
        self.assertFalse(self.result.observer_writeback_performed)
        self.assertFalse(self.result.accumulation_performed)
        self.assertFalse(self.result.new_runtime_state_added)
        self.assertFalse(self.result.runtime_candidate_released)

    def test_public_roles_contain_no_memory_or_accumulator(self) -> None:
        forbidden = {
            "memory",
            "history",
            "accumulator",
            "integrated_flow",
            "medium_state",
            "topology",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                instantaneous_field_flow_null_probe_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
