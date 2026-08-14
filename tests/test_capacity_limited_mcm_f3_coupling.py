from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    DistributedReceptorContact,
    MCMSubstrateArmContract,
    MCMSubstrateMass,
    MCMSubstrateState,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDockAnatomy,
    build_shared_mcm_field,
    build_uniform_mcm_substrate,
    compute_mcm_f3_coupling,
    mcm_substrate_edge_inventory_digest,
    receptor_projection_baseline,
)
from mcm_field_organism.capacity_limited_mcm_f3_coupling import (
    MCMCapacityLimitedCouplingContract,
    MCMCapacityLimitedCouplingError,
    compute_capacity_limited_mcm_f3_coupling,
)


def _frame(modality: str, value: float) -> ReceptorContactFrame:
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


def _layer(
    first_value: float,
    second_value: float,
    *,
    reverse_declaration: bool = False,
):
    auditory = _frame("auditory", first_value)
    visual = _frame("visual", second_value)
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
        CommonFieldTime("organism.w7g", 0, 1),
        (
            DistributedReceptorContact("dock.auditory", auditory),
            DistributedReceptorContact("dock.visual", visual),
        ),
    )
    return field.advance(distribution, receptor_projection_baseline).layer


def _substrate(layer, arm, masses: tuple[float, float]):
    return MCMSubstrateState(
        arm=arm,
        masses=tuple(
            MCMSubstrateMass(neuron.neuron_id, mass)
            for neuron, mass in zip(layer.neurons, masses, strict=True)
        ),
        edge_inventory_digest=mcm_substrate_edge_inventory_digest(layer),
    )


class CapacityLimitedMCMF3CouplingTests(unittest.TestCase):
    def test_null_arm_returns_zero_and_preserves_inputs(self) -> None:
        layer = _layer(-0.5, 0.5)
        substrate = build_uniform_mcm_substrate(
            layer,
            MCMSubstrateArmContract("p0.null", 0.0, 0.5, 2.0),
        )
        layer_digest = layer.digest()
        substrate_digest = substrate.digest()

        result = compute_capacity_limited_mcm_f3_coupling(
            layer,
            substrate,
            MCMCapacityLimitedCouplingContract(0.75),
        )

        self.assertEqual((0.0, 0.0), result.mass_rate)
        self.assertEqual((0.0, 0.0), result.activation_backreaction)
        self.assertEqual(0.0, result.edge_rates[0].first_to_second)
        self.assertEqual(0.0, result.edge_rates[0].second_to_first)
        self.assertEqual(layer_digest, layer.digest())
        self.assertEqual(substrate_digest, substrate.digest())

    def test_full_target_blocks_inflow_and_can_only_release_mass(self) -> None:
        layer = _layer(-0.5, 0.5)
        substrate = _substrate(
            layer,
            MCMSubstrateArmContract("w7g.active", 1.0, 0.5, 1.0),
            (0.25, 0.75),
        )

        result = compute_capacity_limited_mcm_f3_coupling(
            layer,
            substrate,
            MCMCapacityLimitedCouplingContract(0.75),
        )

        edge = result.edge_rates[0]
        self.assertEqual(0.0, edge.first_to_second)
        self.assertGreater(edge.second_to_first, 0.0)
        self.assertGreater(result.mass_rate[0], 0.0)
        self.assertLess(result.mass_rate[1], 0.0)

    def test_empty_source_cannot_release_mass_and_can_only_receive(self) -> None:
        layer = _layer(-0.5, 0.5)
        substrate = _substrate(
            layer,
            MCMSubstrateArmContract("w7g.active", 1.0, 0.5, 1.0),
            (0.0, 1.0),
        )

        result = compute_capacity_limited_mcm_f3_coupling(
            layer,
            substrate,
            MCMCapacityLimitedCouplingContract(1.0),
        )

        edge = result.edge_rates[0]
        self.assertEqual(0.0, edge.first_to_second)
        self.assertGreaterEqual(edge.second_to_first, 0.0)
        self.assertGreaterEqual(result.mass_rate[0], 0.0)
        self.assertLessEqual(result.mass_rate[1], 0.0)

    def test_exact_delta_matches_the_w7f_bilinear_term(self) -> None:
        layer = _layer(-0.4, 0.7)
        arm = MCMSubstrateArmContract("w7g.active", 0.8, 0.3, 1.25)
        substrate = _substrate(layer, arm, (0.4, 0.6))
        capacity = 0.8

        baseline = compute_mcm_f3_coupling(layer, substrate)
        result = compute_capacity_limited_mcm_f3_coupling(
            layer,
            substrate,
            MCMCapacityLimitedCouplingContract(capacity),
        )

        first_activation, second_activation = (
            neuron.activation for neuron in layer.neurons
        )
        delta_s = second_activation - first_activation
        expected_delta_j = (
            -2.0
            * arm.lambda_sm_per_second
            * arm.kappa
            * delta_s
            * 0.4
            * 0.6
            / capacity
        )
        actual_delta_j = (
            result.edge_rates[0].net_first_to_second
            + baseline.mass_rate[0]
        )
        self.assertAlmostEqual(expected_delta_j, actual_delta_j, places=15)

    def test_kappa_zero_is_exactly_the_existing_passive_diffusion(self) -> None:
        layer = _layer(-0.5, 0.5)
        arm = MCMSubstrateArmContract("w7g.kappa-null", 0.7, 0.0, 1.1)
        substrate = _substrate(layer, arm, (0.35, 0.65))

        baseline = compute_mcm_f3_coupling(layer, substrate)
        result = compute_capacity_limited_mcm_f3_coupling(
            layer,
            substrate,
            MCMCapacityLimitedCouplingContract(0.8),
        )

        self.assertAlmostEqual(baseline.mass_rate[0], result.mass_rate[0])
        self.assertAlmostEqual(baseline.mass_rate[1], result.mass_rate[1])
        self.assertAlmostEqual(
            baseline.activation_backreaction[0],
            result.activation_backreaction[0],
        )
        self.assertAlmostEqual(
            baseline.activation_backreaction[1],
            result.activation_backreaction[1],
        )

    def test_eta_zero_removes_only_the_tied_backreaction(self) -> None:
        layer = _layer(-0.5, 0.5)
        active = _substrate(
            layer,
            MCMSubstrateArmContract("w7g.active", 1.0, 0.5, 1.0),
            (0.4, 0.6),
        )
        eta_null = _substrate(
            layer,
            MCMSubstrateArmContract("w7g.eta-null", 1.0, 0.5, 0.0),
            (0.4, 0.6),
        )
        contract = MCMCapacityLimitedCouplingContract(0.8)

        active_result = compute_capacity_limited_mcm_f3_coupling(
            layer, active, contract
        )
        null_result = compute_capacity_limited_mcm_f3_coupling(
            layer, eta_null, contract
        )

        self.assertEqual(active_result.mass_rate, null_result.mass_rate)
        self.assertEqual((0.0, 0.0), null_result.activation_backreaction)

    def test_edge_booking_conserves_total_mass_rate(self) -> None:
        layer = _layer(-0.75, 0.25)
        substrate = _substrate(
            layer,
            MCMSubstrateArmContract("w7g.active", 0.9, -0.4, 1.0),
            (0.3, 0.7),
        )

        result = compute_capacity_limited_mcm_f3_coupling(
            layer,
            substrate,
            MCMCapacityLimitedCouplingContract(0.85),
        )

        self.assertEqual(0.0, sum(result.mass_rate))
        self.assertEqual(
            -result.edge_rates[0].net_first_to_second,
            result.mass_rate[0],
        )
        self.assertEqual(
            result.edge_rates[0].net_first_to_second,
            result.mass_rate[1],
        )

    def test_declaration_order_cannot_change_the_result(self) -> None:
        first_layer = _layer(-0.5, 0.5)
        reversed_layer = _layer(-0.5, 0.5, reverse_declaration=True)
        arm = MCMSubstrateArmContract("w7g.active", 0.75, -0.25, 1.5)
        contract = MCMCapacityLimitedCouplingContract(0.8)

        first = compute_capacity_limited_mcm_f3_coupling(
            first_layer,
            _substrate(first_layer, arm, (0.4, 0.6)),
            contract,
        )
        reversed_result = compute_capacity_limited_mcm_f3_coupling(
            reversed_layer,
            _substrate(reversed_layer, arm, (0.4, 0.6)),
            contract,
        )

        self.assertEqual(first, reversed_result)

    def test_capacity_contract_rejects_invalid_corridors(self) -> None:
        layer = _layer(-0.5, 0.5)
        arm = MCMSubstrateArmContract("w7g.active", 1.0, 0.5, 1.0)
        uniform = build_uniform_mcm_substrate(layer, arm)

        with self.assertRaisesRegex(
            MCMCapacityLimitedCouplingError,
            "exceed the homogeneous mean",
        ):
            compute_capacity_limited_mcm_f3_coupling(
                layer,
                uniform,
                MCMCapacityLimitedCouplingContract(0.5),
            )
        with self.assertRaisesRegex(
            MCMCapacityLimitedCouplingError,
            "cannot exceed the declared total",
        ):
            compute_capacity_limited_mcm_f3_coupling(
                layer,
                uniform,
                MCMCapacityLimitedCouplingContract(1.1),
            )
        overfilled = _substrate(layer, arm, (0.2, 0.8))
        with self.assertRaisesRegex(
            MCMCapacityLimitedCouplingError,
            "mass exceeds",
        ):
            compute_capacity_limited_mcm_f3_coupling(
                layer,
                overfilled,
                MCMCapacityLimitedCouplingContract(0.7),
            )

    def test_module_is_not_reexported_from_current_api(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "compute_capacity_limited_mcm_f3_coupling")
        )


if __name__ == "__main__":
    unittest.main()
