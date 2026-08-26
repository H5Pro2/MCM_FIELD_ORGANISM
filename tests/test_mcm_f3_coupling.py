from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    DistributedReceptorContact,
    MCMF3CouplingError,
    MCMSubstrateArmContract,
    MCMSubstrateMass,
    MCMSubstrateState,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDockAnatomy,
    build_shared_mcm_field,
    build_uniform_mcm_substrate,
    compute_mcm_f3_coupling,
    mcm_f3_coupling_public_roles,
    mcm_substrate_edge_inventory_digest,
    receptor_projection_baseline,
)


def frame(modality: str, value: float) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality,
        geometry_id=f"{modality}.geometry.v1",
        snapshot_id=f"{modality}.snapshot.0",
        clock_id=f"{modality}.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=(f"{modality}.carrier.0",),
        values=(value,),
    )


def layer_with_activation(
    auditory_value: float,
    visual_value: float,
    *,
    reverse_declaration: bool = False,
):
    auditory = frame("auditory", auditory_value)
    visual = frame("visual", visual_value)
    reference = (visual, auditory) if reverse_declaration else (auditory, visual)
    field = build_shared_mcm_field(
        reference,
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
    )
    distribution = ReceptorDistribution(
        CommonFieldTime("organism.f3", 0, 1),
        (
            DistributedReceptorContact("dock.auditory", auditory),
            DistributedReceptorContact("dock.visual", visual),
        ),
    )
    return field.advance(distribution, receptor_projection_baseline).layer


def line_layer(values: tuple[float, ...]):
    auditory = ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.geometry.line.v1",
        snapshot_id="auditory.snapshot.line.0",
        clock_id="auditory.source",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=tuple(f"auditory.carrier.{index}" for index in range(len(values))),
        values=values,
    )
    field = build_shared_mcm_field(
        (auditory,),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                tuple((index,) for index in range(len(values))),
            ),
        },
        sample_offsets=((-1,), (1,)),
    )
    distribution = ReceptorDistribution(
        CommonFieldTime("organism.f3", 0, 1),
        (DistributedReceptorContact("dock.auditory", auditory),),
    )
    return field.advance(distribution, receptor_projection_baseline).layer


def uniform_substrate(layer, arm):
    return build_uniform_mcm_substrate(layer, arm)


def nonuniform_substrate(layer, arm, first_mass: float):
    neuron_ids = tuple(neuron.neuron_id for neuron in layer.neurons)
    return MCMSubstrateState(
        arm=arm,
        masses=(
            MCMSubstrateMass(neuron_ids[0], first_mass),
            MCMSubstrateMass(neuron_ids[1], 1.0 - first_mass),
        ),
        edge_inventory_digest=mcm_substrate_edge_inventory_digest(layer),
    )


class MCMF3CouplingTests(unittest.TestCase):
    def test_null_arm_returns_exact_zero_without_changing_inputs(self) -> None:
        layer = layer_with_activation(-0.5, 0.5)
        substrate = uniform_substrate(
            layer,
            MCMSubstrateArmContract("p0.null", 0.0, 0.5, 2.0),
        )
        layer_digest = layer.digest()
        substrate_digest = substrate.digest()

        result = compute_mcm_f3_coupling(layer, substrate)

        self.assertEqual((0.0, 0.0), result.mass_rate)
        self.assertEqual((0.0, 0.0), result.activation_backreaction)
        self.assertEqual(layer_digest, layer.digest())
        self.assertEqual(substrate_digest, substrate.digest())

    def test_uniform_mass_and_activation_gradient_create_tied_c_and_r(self) -> None:
        layer = layer_with_activation(-0.5, 0.5)
        substrate = uniform_substrate(
            layer,
            MCMSubstrateArmContract("p1.active", 1.0, 0.5, 2.0),
        )

        result = compute_mcm_f3_coupling(layer, substrate)

        self.assertEqual((-0.5, 0.5), result.mass_rate)
        self.assertEqual((0.75, -0.75), result.activation_backreaction)
        self.assertEqual(0.0, sum(result.mass_rate))

    def test_eta_ablation_removes_only_backreaction(self) -> None:
        layer = layer_with_activation(-0.5, 0.5)
        active = uniform_substrate(
            layer,
            MCMSubstrateArmContract("p1.active", 1.0, 0.5, 2.0),
        )
        eta_null = uniform_substrate(
            layer,
            MCMSubstrateArmContract("b.eta-null", 1.0, 0.5, 0.0),
        )

        active_result = compute_mcm_f3_coupling(layer, active)
        null_result = compute_mcm_f3_coupling(layer, eta_null)

        self.assertEqual(active_result.mass_rate, null_result.mass_rate)
        self.assertEqual((0.0, 0.0), null_result.activation_backreaction)

    def test_kappa_ablation_leaves_only_neutral_mass_diffusion(self) -> None:
        layer = layer_with_activation(-0.5, 0.5)
        substrate = nonuniform_substrate(
            layer,
            MCMSubstrateArmContract("b.kappa-null", 1.0, 0.0, 1.0),
            0.75,
        )

        result = compute_mcm_f3_coupling(layer, substrate)

        self.assertEqual((-0.5, 0.5), result.mass_rate)
        self.assertEqual((0.375, -0.375), result.activation_backreaction)

    def test_constant_activation_and_uniform_mass_are_an_exact_rest_state(self) -> None:
        layer = layer_with_activation(0.25, 0.25)
        substrate = uniform_substrate(
            layer,
            MCMSubstrateArmContract("p1.active", 1.0, 0.5, 2.0),
        )

        result = compute_mcm_f3_coupling(layer, substrate)

        self.assertEqual((0.0, 0.0), result.mass_rate)
        self.assertEqual((0.0, 0.0), result.activation_backreaction)

    def test_activation_boundary_envelope_blocks_only_r(self) -> None:
        layer = layer_with_activation(-1.0, 1.0)
        substrate = uniform_substrate(
            layer,
            MCMSubstrateArmContract("p1.active", 1.0, 0.5, 3.0),
        )

        result = compute_mcm_f3_coupling(layer, substrate)

        self.assertEqual((-1.0, 1.0), result.mass_rate)
        self.assertEqual((0.0, 0.0), result.activation_backreaction)

    def test_declaration_order_cannot_change_the_canonical_result(self) -> None:
        first_layer = layer_with_activation(-0.5, 0.5)
        reversed_layer = layer_with_activation(
            -0.5,
            0.5,
            reverse_declaration=True,
        )
        arm = MCMSubstrateArmContract("p1.active", 0.75, -0.25, 1.5)

        first = compute_mcm_f3_coupling(
            first_layer,
            uniform_substrate(first_layer, arm),
        )
        reversed_result = compute_mcm_f3_coupling(
            reversed_layer,
            uniform_substrate(reversed_layer, arm),
        )

        self.assertEqual(first, reversed_result)

    def test_kappa_sign_reverses_uniform_mass_gradient_transport(self) -> None:
        layer = layer_with_activation(-0.5, 0.5)
        positive = uniform_substrate(
            layer,
            MCMSubstrateArmContract("b.sign-positive", 1.0, 0.5, 1.0),
        )
        negative = uniform_substrate(
            layer,
            MCMSubstrateArmContract("b.sign-negative", 1.0, -0.5, 1.0),
        )

        positive_result = compute_mcm_f3_coupling(layer, positive)
        negative_result = compute_mcm_f3_coupling(layer, negative)

        self.assertEqual(
            positive_result.mass_rate,
            tuple(-value for value in negative_result.mass_rate),
        )
        self.assertEqual(
            positive_result.activation_backreaction,
            tuple(-value for value in negative_result.activation_backreaction),
        )

    def test_multinode_edge_booking_conserves_total_mass_rate(self) -> None:
        layer = line_layer((-0.75, -0.1, 0.4, 0.9))
        arm = MCMSubstrateArmContract("p1.active", 0.8, 0.4, 1.2)
        substrate = MCMSubstrateState(
            arm=arm,
            masses=tuple(
                MCMSubstrateMass(neuron.neuron_id, mass)
                for neuron, mass in zip(
                    layer.neurons,
                    (0.1, 0.2, 0.3, 0.4),
                    strict=True,
                )
            ),
            edge_inventory_digest=mcm_substrate_edge_inventory_digest(layer),
        )

        result = compute_mcm_f3_coupling(layer, substrate)

        self.assertAlmostEqual(0.0, sum(result.mass_rate), places=15)
        self.assertTrue(any(value != 0.0 for value in result.mass_rate))
        self.assertEqual(
            tuple(neuron.neuron_id for neuron in layer.neurons),
            result.neuron_ids,
        )

    def test_mismatched_substrate_identity_or_edges_are_rejected(self) -> None:
        layer = layer_with_activation(-0.5, 0.5)
        arm = MCMSubstrateArmContract("p1.active", 1.0, 0.5, 1.0)
        valid = uniform_substrate(layer, arm)
        wrong_ids = MCMSubstrateState(
            arm=arm,
            masses=(
                MCMSubstrateMass("wrong.a", 0.5),
                MCMSubstrateMass("wrong.b", 0.5),
            ),
            edge_inventory_digest=valid.edge_inventory_digest,
        )
        wrong_edges = MCMSubstrateState(
            arm=arm,
            masses=valid.masses,
            edge_inventory_digest="0" * 64,
        )

        with self.assertRaisesRegex(MCMF3CouplingError, "every field neuron"):
            compute_mcm_f3_coupling(layer, wrong_ids)
        with self.assertRaisesRegex(MCMF3CouplingError, "edge inventory"):
            compute_mcm_f3_coupling(layer, wrong_edges)

    def test_public_result_contract_contains_no_world_or_history_roles(self) -> None:
        self.assertTrue(
            {
                "world",
                "contact",
                "snapshot",
                "history",
                "phase",
                "meaning",
                "reward",
                "memory",
                "reader",
                "topology",
            }.isdisjoint(mcm_f3_coupling_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
