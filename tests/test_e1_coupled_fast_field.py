from __future__ import annotations

import unittest

import numpy as np

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_coupled_fast_field import (
    E1CoupledFastFieldError,
    advance_e1_coupled_fast_shared_field,
)
from mcm_field_organism.e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1EdgeBinding,
    E1LocalEdgePlasticityContract,
    E1LocalEdgePlasticityState,
    advance_e1_local_edge_plasticity,
    build_neutral_e1_state,
    e1_free_node_resources,
)
from mcm_field_organism.e1_weighted_field_adapter import (
    compute_e1_weighted_edge_rates,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from tests.test_neutral_fast_afterimage import (
    distribution,
    shared_field,
    step,
    values,
    with_fast_state,
)


def contract(*, gain: float = 0.5) -> E1LocalEdgePlasticityContract:
    return E1LocalEdgePlasticityContract(
        E1_CONTRACT_ID,
        1.0,
        1.5,
        0.25,
        gain,
    )


def nonuniform_state(field, *, gain: float = 0.5) -> E1LocalEdgePlasticityState:
    neutral = build_neutral_e1_state(field.layer, contract(gain=gain))
    return E1LocalEdgePlasticityState(
        neutral.contract,
        (
            E1EdgeBinding(*neutral.edges[0], 0.2),
            E1EdgeBinding(*neutral.edges[1], 1.0),
        ),
        neutral.edge_inventory_digest,
    )


class E1CoupledFastFieldTests(unittest.TestCase):
    def setUp(self) -> None:
        self.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage = NeutralFastAfterimageConfig(0.5)

    def test_a0_field_is_exactly_the_existing_p0_field_for_nonuniform_e1(self) -> None:
        initial = with_fast_state(
            shared_field(),
            (-0.8, 0.1, 0.7),
            (0.2, -0.1, 0.3),
        )
        state = nonuniform_state(initial)
        world = distribution(0, 10, "contact", (0.9, -0.2, 0.4))
        interval = step(0, 10)

        p0 = advance_neutral_fast_shared_field(
            initial,
            world,
            interval,
            self.substrate,
            self.afterimage,
        )
        a0 = advance_e1_coupled_fast_shared_field(
            initial,
            state,
            world,
            interval,
            self.substrate,
            self.afterimage,
            backreaction_enabled=False,
        )

        self.assertEqual(p0.snapshot().digest(), a0.field.snapshot().digest())
        self.assertNotEqual(state, a0.e1_state)
        self.assertFalse(a0.applied_adapter.backreaction_enabled)

    def test_active_nonuniform_coupling_changes_the_field(self) -> None:
        initial = with_fast_state(
            shared_field(),
            (-0.8, 0.1, 0.7),
            (0.0, 0.0, 0.0),
        )
        state = nonuniform_state(initial)
        world = distribution(0, 10, "contact", (0.9, -0.2, 0.4))
        interval = step(0, 10)

        a0 = advance_e1_coupled_fast_shared_field(
            initial,
            state,
            world,
            interval,
            self.substrate,
            self.afterimage,
            backreaction_enabled=False,
        )
        a1 = advance_e1_coupled_fast_shared_field(
            initial,
            state,
            world,
            interval,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )

        self.assertGreater(
            float(np.max(np.abs(values(a1.field, "activation") - values(a0.field, "activation")))),
            1e-6,
        )
        self.assertGreater(
            float(np.max(np.abs(values(a1.field, "afterimage") - values(a0.field, "afterimage")))),
            1e-6,
        )

    def test_zero_gain_active_arm_is_exactly_a0(self) -> None:
        initial = with_fast_state(shared_field(), (-0.7, 0.0, 0.8), (0.0,) * 3)
        state = nonuniform_state(initial, gain=0.0)
        world = distribution(0, 10, "contact", (0.2, 0.6, -0.3))
        interval = step(0, 10)

        a0 = advance_e1_coupled_fast_shared_field(
            initial, state, world, interval, self.substrate, self.afterimage,
            backreaction_enabled=False,
        )
        a1 = advance_e1_coupled_fast_shared_field(
            initial, state, world, interval, self.substrate, self.afterimage,
            backreaction_enabled=True,
        )

        self.assertEqual(a0.field, a1.field)
        self.assertEqual(a0.e1_state, a1.e1_state)
        self.assertEqual(
            tuple(item.rate_per_second for item in a0.applied_adapter.edge_rates),
            tuple(item.rate_per_second for item in a1.applied_adapter.edge_rates),
        )

    def test_applied_adapter_comes_from_the_first_half_e1_state(self) -> None:
        initial = with_fast_state(shared_field(), (-0.9, 0.0, 0.6), (0.0,) * 3)
        state = nonuniform_state(initial)
        world = distribution(0, 10, "contact", (0.4, 0.2, -0.5))
        interval = step(0, 10)
        midpoint = advance_e1_local_edge_plasticity(initial.layer, state, 0.5)
        expected = compute_e1_weighted_edge_rates(
            initial.layer,
            midpoint,
            self.substrate,
            backreaction_enabled=True,
        )

        result = advance_e1_coupled_fast_shared_field(
            initial, state, world, interval, self.substrate, self.afterimage,
            backreaction_enabled=True,
        )

        self.assertEqual(expected, result.applied_adapter)

    def test_uniform_contact_free_field_matches_two_half_e1_steps(self) -> None:
        initial = with_fast_state(shared_field(), (0.4, 0.4, 0.4), (0.4,) * 3)
        state = nonuniform_state(initial)
        world = distribution(0, 10, "absent", None)
        interval = step(0, 10)
        expected = advance_e1_local_edge_plasticity(initial.layer, state, 0.5)
        expected = advance_e1_local_edge_plasticity(initial.layer, expected, 0.5)

        result = advance_e1_coupled_fast_shared_field(
            initial, state, world, interval, self.substrate, self.afterimage,
            backreaction_enabled=True,
        )

        np.testing.assert_allclose(values(result.field, "activation"), (0.4,) * 3)
        self.assertEqual(expected, result.e1_state)

    def test_coupled_step_preserves_ranges_balance_and_inputs(self) -> None:
        initial = with_fast_state(shared_field(), (-0.8, 0.1, 0.7), (0.2,) * 3)
        state = nonuniform_state(initial)
        layer_digest = initial.layer.digest()
        bindings = state.edge_bindings
        result = advance_e1_coupled_fast_shared_field(
            initial,
            state,
            distribution(0, 10, "contact", (1.0, -0.4, 0.3)),
            step(0, 10),
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )

        self.assertEqual(layer_digest, initial.layer.digest())
        self.assertEqual(bindings, state.edge_bindings)
        for role in ("activation", "afterimage"):
            self.assertTrue(np.all(np.abs(values(result.field, role)) <= 1.0))
        free = dict(e1_free_node_resources(result.field.layer, result.e1_state))
        self.assertGreaterEqual(min(free.values()), 0.0)

    def test_time_refinement_reduces_the_coupling_difference(self) -> None:
        initial = with_fast_state(shared_field(), (-0.8, 0.1, 0.7), (0.0,) * 3)
        initial_state = nonuniform_state(initial)

        def integrate(parts: int):
            field = initial
            state = initial_state
            ticks = 12 // parts
            for index in range(parts):
                start = index * ticks
                end = (index + 1) * ticks
                result = advance_e1_coupled_fast_shared_field(
                    field,
                    state,
                    distribution(start, end, f"contact.{parts}.{index}", (0.6, -0.2, 0.4)),
                    step(start, end),
                    self.substrate,
                    self.afterimage,
                    backreaction_enabled=True,
                )
                field, state = result.field, result.e1_state
            return field, state

        one_field, one_state = integrate(1)
        two_field, two_state = integrate(2)
        four_field, four_state = integrate(4)
        one_two = max(
            float(np.max(np.abs(values(one_field, "activation") - values(two_field, "activation")))),
            max(abs(a.binding - b.binding) for a, b in zip(one_state.edge_bindings, two_state.edge_bindings, strict=True)),
        )
        two_four = max(
            float(np.max(np.abs(values(two_field, "activation") - values(four_field, "activation")))),
            max(abs(a.binding - b.binding) for a, b in zip(two_state.edge_bindings, four_state.edge_bindings, strict=True)),
        )
        self.assertGreater(one_two, 0.0)
        self.assertLess(two_four, one_two)

    def test_invalid_arm_control_is_rejected_without_public_exports(self) -> None:
        initial = shared_field()
        state = build_neutral_e1_state(initial.layer, contract())
        with self.assertRaisesRegex(E1CoupledFastFieldError, "boolean"):
            advance_e1_coupled_fast_shared_field(
                initial,
                state,
                distribution(0, 10, "contact", (0.0,) * 3),
                step(0, 10),
                self.substrate,
                self.afterimage,
                backreaction_enabled=1,
            )
        for role in (
            "E1CoupledFastFieldStepResult",
            "advance_e1_coupled_fast_shared_field",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
