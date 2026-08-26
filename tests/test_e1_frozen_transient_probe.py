from __future__ import annotations

import unittest

import numpy as np

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_frozen_transient_probe import (
    FrozenTransientE1ProbeError,
    advance_fixed_e1_adapter_fast_shared_field_transient,
    advance_frozen_e1_fast_shared_field_transient,
)
from mcm_field_organism.e1_local_edge_plasticity import (
    E1EdgeBinding,
    E1LocalEdgePlasticityState,
    build_neutral_e1_state,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from mcm_field_organism.receptor_contract import CommonFieldTime
from mcm_field_organism.receptor_distributor import ReceptorDistribution
from mcm_field_organism.receptor_proposal_handoff import (
    handoff_receptor_completion_groups,
)
from mcm_field_organism.transient_dock_trajectory import (
    map_proposal_batch_to_transient_docks,
)
from mcm_field_organism.transient_neuron_input import (
    project_transient_docks_to_neuron_inputs,
)
from tests.test_e1_transient_asynchronous_field import contract
from tests.test_neutral_asynchronous_field_runtime import (
    activation,
    fresh_field,
    sequences,
    steps,
)


def probe_inputs(source=None):
    source = sequences() if source is None else source
    proposal = steps((0, 12))
    field = fresh_field()
    handoff = handoff_receptor_completion_groups(source, proposal)
    trajectory = map_proposal_batch_to_transient_docks(
        handoff.batches[0], field.docks
    )
    transient_inputs = project_transient_docks_to_neuron_inputs(
        trajectory, field.docks
    )
    distribution = ReceptorDistribution(
        CommonFieldTime("organism.test", 0, 12), ()
    )
    return field, distribution, transient_inputs


def nonuniform_state(field, *, gain: float = 0.5):
    neutral = build_neutral_e1_state(field.layer, contract(gain=gain))
    return E1LocalEdgePlasticityState(
        neutral.contract,
        (E1EdgeBinding(*neutral.edges[0], 1.0),),
        neutral.edge_inventory_digest,
    )


class E1FrozenTransientProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage = NeutralFastAfterimageConfig(0.5)

    def test_frozen_probe_returns_identical_e1_object(self) -> None:
        field, distribution, transient_inputs = probe_inputs()
        state = nonuniform_state(field)

        result = advance_frozen_e1_fast_shared_field_transient(
            field,
            state,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )

        self.assertIs(state, result.e1_state)
        self.assertEqual(state.edge_bindings, result.e1_state.edge_bindings)

    def test_ablation_is_bit_exact_p0(self) -> None:
        field, distribution, transient_inputs = probe_inputs()
        state = nonuniform_state(field)
        p0 = advance_neutral_fast_shared_field_transient(
            field,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
        )
        ablated = advance_frozen_e1_fast_shared_field_transient(
            field,
            state,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=False,
        )

        self.assertEqual(p0.snapshot().digest(), ablated.field.snapshot().digest())

    def test_neutral_active_state_is_bit_exact_p0(self) -> None:
        field, distribution, transient_inputs = probe_inputs()
        state = build_neutral_e1_state(field.layer, contract())
        p0 = advance_neutral_fast_shared_field_transient(
            field,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
        )
        active = advance_frozen_e1_fast_shared_field_transient(
            field,
            state,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )

        self.assertEqual(p0.snapshot().digest(), active.field.snapshot().digest())

    def test_active_probe_equals_fixed_adapter_and_differs_from_ablation(self) -> None:
        field, distribution, transient_inputs = probe_inputs()
        state = nonuniform_state(field)
        active = advance_frozen_e1_fast_shared_field_transient(
            field,
            state,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )
        fixed = advance_fixed_e1_adapter_fast_shared_field_transient(
            field,
            active.applied_adapter,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
        )
        ablated = advance_frozen_e1_fast_shared_field_transient(
            field,
            state,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=False,
        )

        self.assertEqual(active.field.snapshot().digest(), fixed.snapshot().digest())
        self.assertGreater(
            float(np.max(np.abs(activation(active.field) - activation(ablated.field)))),
            0.0,
        )

    def test_zero_gain_active_is_bit_exact_ablation(self) -> None:
        field, distribution, transient_inputs = probe_inputs()
        state = nonuniform_state(field, gain=0.0)
        active = advance_frozen_e1_fast_shared_field_transient(
            field,
            state,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )
        ablated = advance_frozen_e1_fast_shared_field_transient(
            field,
            state,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=False,
        )

        self.assertEqual(active.field.snapshot().digest(), ablated.field.snapshot().digest())
        self.assertIs(active.e1_state, state)

    def test_simultaneous_modalities_are_declaration_order_invariant(self) -> None:
        source = sequences()
        first_field, first_distribution, first_inputs = probe_inputs(source)
        first_state = nonuniform_state(first_field)
        first = advance_frozen_e1_fast_shared_field_transient(
            first_field,
            first_state,
            first_distribution,
            first_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )
        second_field, second_distribution, second_inputs = probe_inputs(
            tuple(reversed(source))
        )
        second_state = nonuniform_state(second_field)
        second = advance_frozen_e1_fast_shared_field_transient(
            second_field,
            second_state,
            second_distribution,
            second_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )

        self.assertEqual(first.field.snapshot().digest(), second.field.snapshot().digest())

    def test_mismatched_adapter_rate_and_invalid_switch_fail_closed(self) -> None:
        field, distribution, transient_inputs = probe_inputs()
        state = nonuniform_state(field)
        active = advance_frozen_e1_fast_shared_field_transient(
            field,
            state,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )
        with self.assertRaisesRegex(FrozenTransientE1ProbeError, "base rate"):
            advance_fixed_e1_adapter_fast_shared_field_transient(
                field,
                active.applied_adapter,
                distribution,
                transient_inputs,
                NeutralLocalFieldSubstrateConfig(2.0),
                self.afterimage,
            )
        with self.assertRaisesRegex(FrozenTransientE1ProbeError, "boolean"):
            advance_frozen_e1_fast_shared_field_transient(
                field,
                state,
                distribution,
                transient_inputs,
                self.substrate,
                self.afterimage,
                backreaction_enabled=1,
            )

    def test_inputs_are_immutable_and_roles_stay_private(self) -> None:
        field, distribution, transient_inputs = probe_inputs()
        state = nonuniform_state(field)
        layer_digest = field.layer.digest()
        bindings = state.edge_bindings

        advance_frozen_e1_fast_shared_field_transient(
            field,
            state,
            distribution,
            transient_inputs,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )

        self.assertEqual(layer_digest, field.layer.digest())
        self.assertEqual(bindings, state.edge_bindings)
        for role in (
            "FrozenTransientE1ProbeResult",
            "advance_frozen_e1_fast_shared_field_transient",
            "advance_fixed_e1_adapter_fast_shared_field_transient",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
