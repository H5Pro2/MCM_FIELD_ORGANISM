from __future__ import annotations

import unittest

import numpy as np

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_frozen_history_probe import (
    FrozenE1ProbeError,
    advance_fixed_e1_adapter_probe,
    advance_frozen_e1_probe,
)
from mcm_field_organism.e1_local_edge_plasticity import (
    E1EdgeBinding,
    E1LocalEdgePlasticityState,
    build_neutral_e1_state,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from tests.test_e1_coupled_fast_field import contract
from tests.test_neutral_fast_afterimage import (
    distribution,
    shared_field,
    step,
    values,
    with_fast_state,
)


def frozen_state(field, *, gain: float = 0.5) -> E1LocalEdgePlasticityState:
    neutral = build_neutral_e1_state(field.layer, contract(gain=gain))
    return E1LocalEdgePlasticityState(
        neutral.contract,
        (
            E1EdgeBinding(*neutral.edges[0], 0.2),
            E1EdgeBinding(*neutral.edges[1], 1.0),
        ),
        neutral.edge_inventory_digest,
    )


class FrozenE1HistoryProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage = NeutralFastAfterimageConfig(0.5)

    def probe_field(self):
        return with_fast_state(
            shared_field(),
            (0.3, -0.2, 0.6),
            (0.1, 0.0, -0.1),
        )

    def test_frozen_probe_returns_the_identical_e1_state_object(self) -> None:
        initial = self.probe_field()
        state = frozen_state(initial)

        result = advance_frozen_e1_probe(
            initial,
            state,
            distribution(0, 10, "probe", (0.75, -0.25, 0.25)),
            step(0, 10),
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )

        self.assertIs(state, result.e1_state)
        self.assertEqual(state.edge_bindings, result.e1_state.edge_bindings)

    def test_ablated_frozen_probe_is_bit_exact_to_p0(self) -> None:
        initial = self.probe_field()
        state = frozen_state(initial)
        world = distribution(0, 10, "probe", (0.75, -0.25, 0.25))
        interval = step(0, 10)

        p0 = advance_neutral_fast_shared_field(
            initial,
            world,
            interval,
            self.substrate,
            self.afterimage,
        )
        ablated = advance_frozen_e1_probe(
            initial,
            state,
            world,
            interval,
            self.substrate,
            self.afterimage,
            backreaction_enabled=False,
        )

        self.assertEqual(p0.snapshot().digest(), ablated.field.snapshot().digest())

    def test_active_frozen_probe_equals_its_fixed_adapter_baseline(self) -> None:
        initial = self.probe_field()
        state = frozen_state(initial)
        active = advance_frozen_e1_probe(
            initial,
            state,
            distribution(0, 10, "probe", (0.75, -0.25, 0.25)),
            step(0, 10),
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )
        fixed = advance_fixed_e1_adapter_probe(
            initial,
            active.applied_adapter,
            distribution(0, 10, "probe", (0.75, -0.25, 0.25)),
            step(0, 10),
            self.substrate,
            self.afterimage,
        )

        self.assertEqual(active.field.snapshot().digest(), fixed.snapshot().digest())

    def test_active_nonuniform_frozen_state_changes_the_probe_field(self) -> None:
        initial = self.probe_field()
        state = frozen_state(initial)
        world = distribution(0, 10, "probe", (0.75, -0.25, 0.25))
        interval = step(0, 10)
        active = advance_frozen_e1_probe(
            initial,
            state,
            world,
            interval,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )
        ablated = advance_frozen_e1_probe(
            initial,
            state,
            world,
            interval,
            self.substrate,
            self.afterimage,
            backreaction_enabled=False,
        )

        self.assertGreater(
            float(np.max(np.abs(values(active.field, "activation") - values(ablated.field, "activation")))),
            1e-6,
        )

    def test_zero_gain_active_probe_is_numerically_identical_to_ablation(self) -> None:
        initial = self.probe_field()
        state = frozen_state(initial, gain=0.0)
        world = distribution(0, 10, "probe", (0.75, -0.25, 0.25))
        interval = step(0, 10)
        active = advance_frozen_e1_probe(
            initial, state, world, interval, self.substrate, self.afterimage,
            backreaction_enabled=True,
        )
        ablated = advance_frozen_e1_probe(
            initial, state, world, interval, self.substrate, self.afterimage,
            backreaction_enabled=False,
        )

        self.assertEqual(active.field, ablated.field)
        self.assertIs(active.e1_state, state)
        self.assertIs(ablated.e1_state, state)

    def test_probe_does_not_change_field_or_state_inputs(self) -> None:
        initial = self.probe_field()
        state = frozen_state(initial)
        layer_digest = initial.layer.digest()
        bindings = state.edge_bindings

        advance_frozen_e1_probe(
            initial,
            state,
            distribution(0, 10, "probe", (0.75, -0.25, 0.25)),
            step(0, 10),
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )

        self.assertEqual(layer_digest, initial.layer.digest())
        self.assertEqual(bindings, state.edge_bindings)

    def test_invalid_arm_control_and_fixed_adapter_are_rejected(self) -> None:
        initial = self.probe_field()
        state = frozen_state(initial)
        with self.assertRaisesRegex(FrozenE1ProbeError, "boolean"):
            advance_frozen_e1_probe(
                initial,
                state,
                distribution(0, 10, "probe", (0.75, -0.25, 0.25)),
                step(0, 10),
                self.substrate,
                self.afterimage,
                backreaction_enabled=1,
            )
        with self.assertRaisesRegex(FrozenE1ProbeError, "adapter"):
            advance_fixed_e1_adapter_probe(
                initial,
                object(),
                distribution(0, 10, "probe", (0.75, -0.25, 0.25)),
                step(0, 10),
                self.substrate,
                self.afterimage,
            )

    def test_probe_roles_are_not_exported_through_public_apis(self) -> None:
        for role in (
            "FrozenE1ProbeResult",
            "advance_frozen_e1_probe",
            "advance_fixed_e1_adapter_probe",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
