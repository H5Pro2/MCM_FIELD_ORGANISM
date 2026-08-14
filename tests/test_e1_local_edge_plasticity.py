from __future__ import annotations

from dataclasses import replace
import math
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1EdgeBinding,
    E1LocalEdgePlasticityContract,
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    advance_e1_local_edge_plasticity,
    build_neutral_e1_state,
    e1_free_node_resources,
    validate_e1_state_for_layer,
)
from mcm_field_organism.mcm_neuron import MCMFieldPerception, MCMNeuron
from mcm_field_organism.mcm_neuron_layer import MCMNeuronLayer
from mcm_field_organism.mcm_substrate_state import (
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)


def layer(activation: tuple[float, ...] = (-1.0, 0.0, 1.0)) -> MCMNeuronLayer:
    neurons = tuple(
        MCMNeuron(
            neuron_id=f"neuron.{index}",
            field_id="field.e1",
            modality_id="shared",
            geometry_id="geometry.e1.line",
            position=(index,),
            activation=value,
            afterimage=0.0,
            perception=MCMFieldPerception(0, None, ()),
        )
        for index, value in enumerate(activation)
    )
    return MCMNeuronLayer(
        layer_id="layer.e1.line",
        neurons=neurons,
        sample_offsets=((-1,), (1,)),
    )


def contract(
    *,
    binding_rate: float = 2.0,
    release_rate: float = 0.5,
) -> E1LocalEdgePlasticityContract:
    return E1LocalEdgePlasticityContract(
        E1_CONTRACT_ID,
        1.0,
        binding_rate,
        release_rate,
        0.25,
    )


class E1LocalEdgePlasticityTests(unittest.TestCase):
    def test_neutral_state_uses_every_existing_edge_once(self) -> None:
        current = layer()
        state = build_neutral_e1_state(current, contract())

        self.assertEqual(mcm_substrate_edge_inventory(current), state.edges)
        self.assertEqual(
            mcm_substrate_edge_inventory_digest(current),
            state.edge_inventory_digest,
        )
        self.assertTrue(all(item.binding == 0.0 for item in state.edge_bindings))
        self.assertEqual(
            tuple((neuron.neuron_id, 1.0) for neuron in current.neurons),
            e1_free_node_resources(current, state),
        )

    def test_contract_rejects_invalid_numbers_and_identity(self) -> None:
        valid = (E1_CONTRACT_ID, 1.0, 2.0, 0.5, 0.25)
        invalid = (
            ("e1.wrong", *valid[1:]),
            (valid[0], 0.0, *valid[2:]),
            (valid[0], True, *valid[2:]),
            (valid[0], 1.0, -1.0, 0.5, 0.25),
            (valid[0], 1.0, 2.0, math.inf, 0.25),
            (valid[0], 1.0, 2.0, 0.5, 1.01),
        )
        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(E1LocalEdgePlasticityError):
                    E1LocalEdgePlasticityContract(*values)

    def test_edge_and_state_reject_invalid_inventory_values(self) -> None:
        with self.assertRaises(E1LocalEdgePlasticityError):
            E1EdgeBinding("neuron.1", "neuron.0", 0.0)
        with self.assertRaises(E1LocalEdgePlasticityError):
            E1EdgeBinding("neuron.0", "neuron.1", -0.1)
        with self.assertRaises(E1LocalEdgePlasticityError):
            E1EdgeBinding("neuron.0", "neuron.1", True)

        current = layer()
        state = build_neutral_e1_state(current, contract())
        duplicate = state.edge_bindings + (state.edge_bindings[0],)
        with self.assertRaisesRegex(E1LocalEdgePlasticityError, "unique"):
            E1LocalEdgePlasticityState(
                state.contract,
                duplicate,
                state.edge_inventory_digest,
            )
        with self.assertRaisesRegex(E1LocalEdgePlasticityError, "capacities"):
            E1LocalEdgePlasticityState(
                state.contract,
                (E1EdgeBinding("neuron.0", "neuron.1", 2.1),),
                state.edge_inventory_digest,
            )

    def test_layer_validation_rejects_missing_edges_and_foreign_digest(self) -> None:
        current = layer()
        state = build_neutral_e1_state(current, contract())
        missing = E1LocalEdgePlasticityState(
            state.contract,
            state.edge_bindings[:-1],
            state.edge_inventory_digest,
        )
        with self.assertRaisesRegex(E1LocalEdgePlasticityError, "complete"):
            validate_e1_state_for_layer(current, missing)
        foreign = E1LocalEdgePlasticityState(
            state.contract,
            state.edge_bindings,
            "0" * 64,
        )
        with self.assertRaisesRegex(E1LocalEdgePlasticityError, "digest"):
            validate_e1_state_for_layer(current, foreign)

    def test_pure_release_matches_the_analytic_exponential(self) -> None:
        current = layer((0.0, 0.0))
        base = build_neutral_e1_state(current, contract(binding_rate=0.0))
        initial = E1LocalEdgePlasticityState(
            base.contract,
            (E1EdgeBinding(*base.edges[0], 1.25),),
            base.edge_inventory_digest,
        )

        result = advance_e1_local_edge_plasticity(current, initial, 0.75)

        self.assertAlmostEqual(
            1.25 * math.exp(-0.5 * 0.75),
            result.edge_bindings[0].binding,
            places=14,
        )

    def test_field_tension_binds_but_uniform_field_does_not(self) -> None:
        tense = layer((-1.0, 0.0, 1.0))
        uniform = layer((0.5, 0.5, 0.5))
        tense_state = build_neutral_e1_state(tense, contract(release_rate=0.0))
        uniform_state = build_neutral_e1_state(uniform, contract(release_rate=0.0))

        bound = advance_e1_local_edge_plasticity(tense, tense_state, 0.5)
        unchanged = advance_e1_local_edge_plasticity(uniform, uniform_state, 0.5)

        self.assertTrue(all(item.binding > 0.0 for item in bound.edge_bindings))
        self.assertEqual(uniform_state, unchanged)

    def test_repeated_steps_preserve_nonnegativity_and_resource_balance(self) -> None:
        current = layer((-1.0, 0.25, 1.0))
        state = build_neutral_e1_state(current, contract())
        for _ in range(500):
            state = advance_e1_local_edge_plasticity(current, state, 0.2)
            free = dict(e1_free_node_resources(current, state))
            self.assertGreaterEqual(min(free.values()), 0.0)
            self.assertGreaterEqual(
                min(item.binding for item in state.edge_bindings), 0.0
            )
            self.assertAlmostEqual(
                len(current.neurons) * state.contract.node_capacity,
                math.fsum(free.values())
                + math.fsum(item.binding for item in state.edge_bindings),
                places=13,
            )

    def test_state_construction_and_transition_are_order_invariant(self) -> None:
        current = layer()
        base = build_neutral_e1_state(current, contract())
        reversed_state = E1LocalEdgePlasticityState(
            base.contract,
            tuple(reversed(base.edge_bindings)),
            base.edge_inventory_digest,
        )

        self.assertEqual(base, reversed_state)
        self.assertEqual(
            advance_e1_local_edge_plasticity(current, base, 0.4),
            advance_e1_local_edge_plasticity(current, reversed_state, 0.4),
        )

    def test_transition_does_not_change_input_state_or_layer(self) -> None:
        current = layer()
        state = build_neutral_e1_state(current, contract())
        layer_digest = current.digest()
        bindings = state.edge_bindings

        result = advance_e1_local_edge_plasticity(current, state, 0.5)

        self.assertIsNot(result, state)
        self.assertEqual(bindings, state.edge_bindings)
        self.assertEqual(layer_digest, current.digest())

    def test_time_refinement_converges(self) -> None:
        current = layer((-1.0, 0.1, 1.0))
        initial = build_neutral_e1_state(current, contract())

        def integrate(parts: int) -> E1LocalEdgePlasticityState:
            state = initial
            for _ in range(parts):
                state = advance_e1_local_edge_plasticity(
                    current, state, 0.8 / parts
                )
            return state

        one = integrate(1)
        two = integrate(2)
        four = integrate(4)
        one_two = max(
            abs(a.binding - b.binding)
            for a, b in zip(one.edge_bindings, two.edge_bindings, strict=True)
        )
        two_four = max(
            abs(a.binding - b.binding)
            for a, b in zip(two.edge_bindings, four.edge_bindings, strict=True)
        )
        self.assertGreater(one_two, 0.0)
        self.assertLess(two_four, one_two)

    def test_module_has_no_serialization_or_public_api_surface(self) -> None:
        state = build_neutral_e1_state(layer(), contract())
        for role in ("canonical_payload", "from_payload", "digest"):
            self.assertFalse(hasattr(state, role))
        for role in (
            "E1LocalEdgePlasticityState",
            "advance_e1_local_edge_plasticity",
            "build_neutral_e1_state",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))

    def test_elapsed_time_must_be_explicit_positive_and_finite(self) -> None:
        current = layer()
        state = build_neutral_e1_state(current, contract())
        for elapsed in (0.0, -1.0, math.inf, True):
            with self.subTest(elapsed=elapsed):
                with self.assertRaises(E1LocalEdgePlasticityError):
                    advance_e1_local_edge_plasticity(current, state, elapsed)


if __name__ == "__main__":
    unittest.main()
