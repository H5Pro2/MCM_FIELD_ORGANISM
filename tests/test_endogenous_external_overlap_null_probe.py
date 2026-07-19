from __future__ import annotations

import unittest

from mcm_field_organism import (
    endogenous_external_overlap_null_probe_public_roles,
    run_endogenous_external_overlap_null_probe,
)


class EndogenousExternalOverlapNullProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_endogenous_external_overlap_null_probe()

    def test_both_causes_remain_nonzero_after_existing_field_dynamics(self) -> None:
        self.assertTrue(self.result.external_cause_preserved)
        self.assertTrue(self.result.endogenous_cause_preserved)
        self.assertGreater(self.result.external_signature.activation_l2, 0.0)
        self.assertGreater(self.result.endogenous_signature.activation_l2, 0.0)
        self.assertGreater(self.result.external_signature.afterimage_l2, 0.0)
        self.assertGreater(self.result.endogenous_signature.afterimage_l2, 0.0)

    def test_cause_signatures_remain_distinct(self) -> None:
        self.assertTrue(self.result.cause_signatures_distinct)
        self.assertNotEqual(
            self.result.external_signature.activation,
            self.result.endogenous_signature.activation,
        )
        self.assertNotEqual(
            self.result.external_signature.afterimage,
            self.result.endogenous_signature.afterimage,
        )

    def test_joint_field_is_exact_sum_of_the_two_controlled_causes(self) -> None:
        self.assertTrue(self.result.exact_linear_superposition)
        self.assertLessEqual(
            self.result.maximum_activation_superposition_error,
            1e-12,
        )
        self.assertLessEqual(
            self.result.maximum_afterimage_superposition_error,
            1e-12,
        )

    def test_probe_preserves_sources_and_performs_no_writeback(self) -> None:
        self.assertTrue(self.result.source_states_preserved)
        self.assertFalse(self.result.observer_writeback_performed)

    def test_probe_adds_no_memory_material_motion_or_runtime_candidate(self) -> None:
        self.assertFalse(self.result.memory_state_added)
        self.assertFalse(self.result.material_motion_added)
        self.assertFalse(self.result.runtime_candidate_released)

    def test_public_roles_contain_no_development_or_semantic_mechanism(self) -> None:
        forbidden = {
            "meaning",
            "mood",
            "learning_rate",
            "memory_write",
            "material_velocity",
            "winner",
            "reward",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                endogenous_external_overlap_null_probe_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
