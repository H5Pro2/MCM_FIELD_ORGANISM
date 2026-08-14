from __future__ import annotations

import math
import unittest

import numpy as np

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1EdgeBinding,
    E1LocalEdgePlasticityContract,
    E1LocalEdgePlasticityState,
    build_neutral_e1_state,
)
from mcm_field_organism.e1_weighted_field_adapter import (
    E1WeightedEdgeRate,
    E1WeightedFieldAdapterError,
    E1WeightedFieldAdapterResult,
    build_e1_weighted_diffusion_generator,
    compute_e1_weighted_edge_rates,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_e1_local_edge_plasticity import contract, layer


def bound_state() -> tuple[object, E1LocalEdgePlasticityState]:
    current = layer((-1.0, 0.0, 1.0))
    neutral = build_neutral_e1_state(current, contract())
    state = E1LocalEdgePlasticityState(
        neutral.contract,
        (
            E1EdgeBinding(*neutral.edges[0], 0.5),
            E1EdgeBinding(*neutral.edges[1], 1.0),
        ),
        neutral.edge_inventory_digest,
    )
    return current, state


class E1WeightedFieldAdapterTests(unittest.TestCase):
    def test_active_adapter_uses_the_bound_rate_formula(self) -> None:
        current, state = bound_state()
        config = NeutralLocalFieldSubstrateConfig(0.5)

        result = compute_e1_weighted_edge_rates(
            current, state, config, backreaction_enabled=True
        )

        self.assertEqual(2.0, result.base_rate_per_second)
        self.assertEqual(
            (2.25, 2.5),
            tuple(item.rate_per_second for item in result.edge_rates),
        )
        self.assertTrue(result.backreaction_enabled)

    def test_ablation_keeps_the_same_state_and_returns_exact_base_rate(self) -> None:
        current, state = bound_state()
        config = NeutralLocalFieldSubstrateConfig(0.5)
        before = state.edge_bindings

        result = compute_e1_weighted_edge_rates(
            current, state, config, backreaction_enabled=False
        )

        self.assertEqual((2.0, 2.0), tuple(x.rate_per_second for x in result.edge_rates))
        self.assertEqual(before, state.edge_bindings)
        self.assertFalse(result.backreaction_enabled)

    def test_zero_binding_and_zero_gain_are_exactly_neutral(self) -> None:
        current = layer()
        config = NeutralLocalFieldSubstrateConfig(0.25)
        zero_binding = build_neutral_e1_state(current, contract())
        zero_gain_contract = E1LocalEdgePlasticityContract(
            E1_CONTRACT_ID, 1.0, 2.0, 0.5, 0.0
        )
        zero_gain = E1LocalEdgePlasticityState(
            zero_gain_contract,
            (
                E1EdgeBinding(*zero_binding.edges[0], 0.5),
                E1EdgeBinding(*zero_binding.edges[1], 1.0),
            ),
            zero_binding.edge_inventory_digest,
        )

        for state in (zero_binding, zero_gain):
            active = compute_e1_weighted_edge_rates(
                current, state, config, backreaction_enabled=True
            )
            ablated = compute_e1_weighted_edge_rates(
                current, state, config, backreaction_enabled=False
            )
            self.assertEqual(
                tuple(x.rate_per_second for x in ablated.edge_rates),
                tuple(x.rate_per_second for x in active.edge_rates),
            )

    def test_first_corridor_rate_bound_is_attained_but_not_exceeded(self) -> None:
        current = layer()
        neutral = build_neutral_e1_state(current, contract())
        maximum_gain_contract = E1LocalEdgePlasticityContract(
            E1_CONTRACT_ID, 1.0, 2.0, 0.5, 1.0
        )
        maximum = E1LocalEdgePlasticityState(
            maximum_gain_contract,
            (
                E1EdgeBinding(*neutral.edges[0], 2.0),
                E1EdgeBinding(*neutral.edges[1], 0.0),
            ),
            neutral.edge_inventory_digest,
        )

        result = compute_e1_weighted_edge_rates(
            current,
            maximum,
            NeutralLocalFieldSubstrateConfig(0.5),
            backreaction_enabled=True,
        )

        self.assertEqual(6.0, result.edge_rates[0].rate_per_second)
        self.assertLessEqual(max(x.rate_per_second for x in result.edge_rates), 6.0)

    def test_adapter_rejects_invalid_control_and_geometry(self) -> None:
        current, state = bound_state()
        config = NeutralLocalFieldSubstrateConfig(0.5)
        with self.assertRaisesRegex(E1WeightedFieldAdapterError, "boolean"):
            compute_e1_weighted_edge_rates(
                current, state, config, backreaction_enabled=1
            )
        with self.assertRaisesRegex(E1WeightedFieldAdapterError, "configuration"):
            compute_e1_weighted_edge_rates(
                current, state, object(), backreaction_enabled=True
            )
        foreign = E1LocalEdgePlasticityState(
            state.contract,
            state.edge_bindings,
            "0" * 64,
        )
        with self.assertRaises(E1WeightedFieldAdapterError):
            compute_e1_weighted_edge_rates(
                current, foreign, config, backreaction_enabled=True
            )

    def test_generator_is_symmetric_conservative_and_negative_semidefinite(self) -> None:
        current, state = bound_state()
        result = compute_e1_weighted_edge_rates(
            current,
            state,
            NeutralLocalFieldSubstrateConfig(0.5),
            backreaction_enabled=True,
        )

        generator = build_e1_weighted_diffusion_generator(current, result)

        np.testing.assert_array_equal(generator, generator.T)
        np.testing.assert_allclose(generator.sum(axis=1), 0.0, rtol=0.0, atol=1e-15)
        self.assertLessEqual(float(np.max(np.linalg.eigvalsh(generator))), 1e-14)
        self.assertEqual(np.float64, generator.dtype)

    def test_generator_rejects_incomplete_or_foreign_rate_ledgers(self) -> None:
        current, state = bound_state()
        result = compute_e1_weighted_edge_rates(
            current,
            state,
            NeutralLocalFieldSubstrateConfig(0.5),
            backreaction_enabled=True,
        )
        incomplete = E1WeightedFieldAdapterResult(
            True,
            result.base_rate_per_second,
            result.edge_rates[:-1],
            result.edge_inventory_digest,
        )
        with self.assertRaisesRegex(E1WeightedFieldAdapterError, "complete"):
            build_e1_weighted_diffusion_generator(current, incomplete)
        foreign = E1WeightedFieldAdapterResult(
            True,
            result.base_rate_per_second,
            result.edge_rates,
            "0" * 64,
        )
        with self.assertRaisesRegex(E1WeightedFieldAdapterError, "digest"):
            build_e1_weighted_diffusion_generator(current, foreign)

    def test_rate_container_validates_numbers_edges_and_uniqueness(self) -> None:
        with self.assertRaises(E1WeightedFieldAdapterError):
            E1WeightedEdgeRate("neuron.1", "neuron.0", 1.0)
        with self.assertRaises(E1WeightedFieldAdapterError):
            E1WeightedEdgeRate("neuron.0", "neuron.1", math.inf)
        edge = E1WeightedEdgeRate("neuron.0", "neuron.1", 1.0)
        with self.assertRaisesRegex(E1WeightedFieldAdapterError, "unique"):
            E1WeightedFieldAdapterResult(True, 1.0, (edge, edge), "0" * 64)

    def test_adapter_does_not_change_inputs_or_public_apis(self) -> None:
        current, state = bound_state()
        config = NeutralLocalFieldSubstrateConfig(0.5)
        layer_digest = current.digest()
        bindings = state.edge_bindings

        compute_e1_weighted_edge_rates(
            current, state, config, backreaction_enabled=True
        )

        self.assertEqual(layer_digest, current.digest())
        self.assertEqual(bindings, state.edge_bindings)
        for role in (
            "E1WeightedEdgeRate",
            "compute_e1_weighted_edge_rates",
            "build_e1_weighted_diffusion_generator",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
