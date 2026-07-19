from __future__ import annotations

import unittest

from mcm_field_organism import (
    field_passivity_null_probe_public_roles,
    run_field_passivity_null_probe,
)


class FieldPassivityNullProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = run_field_passivity_null_probe()

    def test_contact_free_field_is_quadratically_dissipative(self) -> None:
        observation = self.result.contact_free
        self.assertTrue(self.result.contact_free_storage_nonincreasing)
        self.assertEqual(0.0, observation.receptor_supply_rate)
        self.assertGreater(observation.neighbor_dissipation_rate, 0.0)
        self.assertLessEqual(observation.storage_rate, 0.0)
        self.assertLessEqual(observation.maximum_generator_eigenvalue, 1e-12)

    def test_receptor_driven_balance_closes_exactly(self) -> None:
        observation = self.result.receptor_driven
        self.assertTrue(self.result.receptor_balance_closed)
        self.assertLessEqual(observation.balance_error, 1e-12)
        self.assertGreater(observation.receptor_dissipation_rate, 0.0)
        self.assertLessEqual(
            observation.storage_rate,
            observation.receptor_supply_rate + 1e-12,
        )

    def test_observer_preserves_field_and_distributions(self) -> None:
        self.assertTrue(self.result.field_digest_preserved)
        self.assertTrue(self.result.distribution_digests_preserved)
        self.assertFalse(self.result.observer_writeback_performed)

    def test_balance_adds_no_accumulator_or_runtime_state(self) -> None:
        self.assertFalse(self.result.accumulation_performed)
        self.assertFalse(self.result.new_runtime_state_added)
        self.assertFalse(self.result.runtime_candidate_released)

    def test_quadratic_storage_is_not_claimed_as_physical_energy(self) -> None:
        self.assertFalse(self.result.physical_energy_claimed)
        self.assertGreater(self.result.contact_free.quadratic_storage, 0.0)

    def test_public_roles_contain_no_material_or_memory_state(self) -> None:
        forbidden = {
            "memory",
            "history",
            "material_state",
            "medium_state",
            "work_accumulator",
            "topology",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(field_passivity_null_probe_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
