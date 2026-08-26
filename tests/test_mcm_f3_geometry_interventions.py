from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism import (
    MCMSubstrateArmContract,
    MCMSubstrateMass,
    MCMSubstrateState,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    activate_mcm_f3_field,
    build_shared_mcm_field,
)
from mcm_field_organism.mcm_f3_geometry_interventions import (
    mcm_f3_geometry_contract,
    neutralize_mcm_f3_local_mask_balanced,
    permute_mcm_f3_mass_by_geometry,
)


def field():
    frame = ReceptorContactFrame(
        "visual", "visual.fixture", "fixture.0", "fixture.clock", 0, 1,
        tuple(f"carrier.{i}" for i in range(8)), (0.0,) * 8,
    )
    base = build_shared_mcm_field(
        (frame,),
        {"visual": ReceptorDockAnatomy(
            "visual", "dock.visual", tuple((row, column) for row in range(2) for column in range(4))
        )},
        sample_offsets=((-1, 0), (0, -1), (0, 1), (1, 0)),
    )
    active = activate_mcm_f3_field(base, MCMSubstrateArmContract("p1.active", 1.0, 0.5, 1.0))
    masses = tuple(
        MCMSubstrateMass(item.neuron_id, value)
        for item, value in zip(active.substrate.masses, (0.05, 0.10, 0.15, 0.20, 0.05, 0.10, 0.15, 0.20), strict=True)
    )
    return replace(active, substrate=MCMSubstrateState(
        active.substrate.arm, masses, active.substrate.edge_inventory_digest
    ))


class MCMF3GeometryInterventionTests(unittest.TestCase):
    def test_row_reflection_is_value_independent_involutive_and_budget_exact(self) -> None:
        original = field()
        contract = mcm_f3_geometry_contract(original)
        once = permute_mcm_f3_mass_by_geometry(original, contract)
        twice = permute_mcm_f3_mass_by_geometry(once, contract)

        self.assertEqual(original.substrate.masses, twice.substrate.masses)
        self.assertEqual(
            sorted(item.mass for item in original.substrate.masses),
            sorted(item.mass for item in once.substrate.masses),
        )
        self.assertAlmostEqual(original.substrate.total_mass, once.substrate.total_mass)

    def test_balanced_half_neutralization_preserves_total_and_other_state(self) -> None:
        original = field()
        contract = mcm_f3_geometry_contract(original)
        left = neutralize_mcm_f3_local_mask_balanced(original, contract, target_mask="left")
        right = neutralize_mcm_f3_local_mask_balanced(original, contract, target_mask="right")
        neutral = 1.0 / len(original.substrate.masses)

        self.assertEqual(original.layer, left.layer)
        self.assertAlmostEqual(1.0, left.substrate.total_mass)
        self.assertAlmostEqual(1.0, right.substrate.total_mass)
        left_mass = {item.neuron_id: item.mass for item in left.substrate.masses}
        right_mass = {item.neuron_id: item.mass for item in right.substrate.masses}
        self.assertTrue(all(left_mass[item] == neutral for item in contract.left_mask_neuron_ids))
        self.assertTrue(all(right_mass[item] == neutral for item in contract.right_mask_neuron_ids))
        self.assertNotEqual(left.substrate.masses, right.substrate.masses)


if __name__ == "__main__":
    unittest.main()
