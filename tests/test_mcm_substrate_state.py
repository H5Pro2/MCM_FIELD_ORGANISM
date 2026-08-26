from __future__ import annotations

import unittest

from mcm_field_organism import (
    MCMSubstrateArmContract,
    MCMSubstrateMass,
    MCMSubstrateState,
    MCMSubstrateStateError,
    ReceptorContactFrame,
    ReceptorDockAnatomy,
    build_shared_mcm_field,
    build_uniform_mcm_substrate,
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
    mcm_substrate_state_public_roles,
)


def frame(modality: str) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality,
        geometry_id=f"{modality}.geometry.v1",
        snapshot_id=f"{modality}.snapshot.0",
        clock_id=f"{modality}.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=(f"{modality}.carrier.0",),
        values=(0.0,),
    )


def layer():
    return build_shared_mcm_field(
        (frame("auditory"), frame("visual")),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,),),
            ),
            "visual": ReceptorDockAnatomy(
                "visual",
                "dock.visual",
                ((1,),),
            ),
        },
        sample_offsets=((-1,), (1,)),
    ).layer


class MCMSubstrateStateTests(unittest.TestCase):
    def test_uniform_reference_uses_the_existing_connected_field_edges(self) -> None:
        current_layer = layer()
        arm = MCMSubstrateArmContract("p0.null", 0.0, -0.5, 0.0)

        state = build_uniform_mcm_substrate(current_layer, arm)

        self.assertEqual(
            ((current_layer.neurons[0].neuron_id, current_layer.neurons[1].neuron_id),),
            mcm_substrate_edge_inventory(current_layer),
        )
        self.assertEqual(
            mcm_substrate_edge_inventory_digest(current_layer),
            state.edge_inventory_digest,
        )
        self.assertEqual((0.5, 0.5), tuple(item.mass for item in state.masses))
        self.assertEqual(1.0, state.total_mass)

    def test_arm_contract_rejects_invalid_or_extended_first_corridor_values(self) -> None:
        for values in (
            ("p0.null", -0.1, 0.0, 0.0, 1.0),
            ("p0.null", 0.0, -0.5001, 0.0, 1.0),
            ("p0.null", 0.0, 0.5001, 0.0, 1.0),
            ("p0.null", 0.0, 0.0, -0.1, 1.0),
            ("p0.null", 0.0, 0.0, 0.0, 2.0),
            ("p0.null", True, 0.0, 0.0, 1.0),
        ):
            with self.subTest(values=values):
                with self.assertRaises(MCMSubstrateStateError):
                    MCMSubstrateArmContract(*values)

    def test_state_rejects_duplicate_missing_or_wrong_total_mass(self) -> None:
        current_layer = layer()
        arm = MCMSubstrateArmContract("p0.null", 0.0, 0.0, 0.0)
        digest = mcm_substrate_edge_inventory_digest(current_layer)
        first = current_layer.neurons[0].neuron_id

        with self.assertRaisesRegex(MCMSubstrateStateError, "unique"):
            MCMSubstrateState(
                arm,
                (MCMSubstrateMass(first, 0.5), MCMSubstrateMass(first, 0.5)),
                digest,
            )
        with self.assertRaisesRegex(MCMSubstrateStateError, "total mass"):
            MCMSubstrateState(
                arm,
                (MCMSubstrateMass(first, 0.5),),
                digest,
            )

    def test_public_contract_contains_no_perception_or_history_roles(self) -> None:
        self.assertTrue(
            {
                "perception",
                "sample",
                "world_contact",
                "meaning",
                "reward",
                "memory",
                "topology",
                "history",
                "reader",
            }.isdisjoint(mcm_substrate_state_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
