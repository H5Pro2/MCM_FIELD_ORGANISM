from __future__ import annotations

import math
import unittest

import numpy as np

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_asynchronous_field_runtime import (
    E1AsynchronousFieldRuntimeError,
    run_e1_asynchronous_field,
)
from mcm_field_organism.e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    build_neutral_e1_state,
    e1_free_node_resources,
)
from mcm_field_organism.neutral_asynchronous_field_runtime import (
    run_neutral_asynchronous_field,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from tests.test_neutral_asynchronous_field_runtime import (
    activation,
    fresh_field,
    sequence,
    sequences,
    steps,
)


def contract(*, gain: float = 0.5) -> E1LocalEdgePlasticityContract:
    return E1LocalEdgePlasticityContract(
        E1_CONTRACT_ID,
        1.0,
        1.5,
        0.25,
        gain,
    )


class E1TransientAsynchronousFieldTests(unittest.TestCase):
    def setUp(self) -> None:
        self.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage = NeutralFastAfterimageConfig(0.5)
        self.source = sequences()
        self.proposals = steps((0, 12))

    def run_e1(self, *, gain: float = 0.5, enabled: bool):
        field = fresh_field()
        state = build_neutral_e1_state(field.layer, contract(gain=gain))
        return run_e1_asynchronous_field(
            field,
            state,
            self.source,
            self.proposals,
            self.substrate,
            self.afterimage,
            backreaction_enabled=enabled,
        )

    def test_a0_field_is_bit_exact_p0_while_e1_changes(self) -> None:
        field = fresh_field()
        initial = build_neutral_e1_state(field.layer, contract())
        initial_layer_digest = field.layer.digest()

        p0 = run_neutral_asynchronous_field(
            field,
            self.source,
            self.proposals,
            self.substrate,
            afterimage_config=self.afterimage,
        )
        a0 = run_e1_asynchronous_field(
            field,
            initial,
            self.source,
            self.proposals,
            self.substrate,
            self.afterimage,
            backreaction_enabled=False,
        )

        self.assertEqual(p0.field.snapshot().digest(), a0.field.snapshot().digest())
        self.assertNotEqual(initial, a0.e1_state)
        self.assertEqual(initial_layer_digest, field.layer.digest())
        self.assertTrue(
            all(
                not adapter.backreaction_enabled
                for step_result in a0.steps
                for adapter in step_result.applied_adapters
            )
        )

    def test_a1_changes_later_field_and_preserves_local_resource_balance(self) -> None:
        a0 = self.run_e1(enabled=False)
        a1 = self.run_e1(enabled=True)

        self.assertGreater(
            float(np.max(np.abs(activation(a1.field) - activation(a0.field)))),
            0.0,
        )
        free = dict(e1_free_node_resources(a1.field.layer, a1.e1_state))
        self.assertGreaterEqual(min(free.values()), 0.0)
        self.assertAlmostEqual(
            len(a1.field.layer.neurons) * a1.e1_state.contract.node_capacity,
            math.fsum(free.values())
            + math.fsum(item.binding for item in a1.e1_state.edge_bindings),
            places=13,
        )

    def test_zero_gain_a1_is_bit_exact_a0(self) -> None:
        a0 = self.run_e1(gain=0.0, enabled=False)
        a1 = self.run_e1(gain=0.0, enabled=True)

        self.assertEqual(a0.field.snapshot().digest(), a1.field.snapshot().digest())
        self.assertEqual(a0.e1_state, a1.e1_state)
        self.assertTrue(
            all(
                adapter.backreaction_enabled
                for step_result in a1.steps
                for adapter in step_result.applied_adapters
            )
        )

    def test_completion_timeline_and_source_supports_are_preserved(self) -> None:
        result = self.run_e1(enabled=True)

        self.assertEqual(5, result.source_support_count)
        self.assertEqual(5, result.handoff.assigned_event_count)
        self.assertTrue(result.handoff.every_in_horizon_event_assigned_once)
        self.assertEqual((2, 4, 5, 9, 12), result.steps[0].interval_end_ticks)
        self.assertEqual(5, len(result.steps[0].applied_adapters))

    def test_simultaneous_modalities_are_declaration_order_invariant(self) -> None:
        first_field = fresh_field()
        first = run_e1_asynchronous_field(
            first_field,
            build_neutral_e1_state(first_field.layer, contract()),
            self.source,
            self.proposals,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )
        second_field = fresh_field()
        second = run_e1_asynchronous_field(
            second_field,
            build_neutral_e1_state(second_field.layer, contract()),
            tuple(reversed(self.source)),
            self.proposals,
            self.substrate,
            self.afterimage,
            backreaction_enabled=True,
        )

        self.assertEqual(first.field.snapshot().digest(), second.field.snapshot().digest())
        self.assertEqual(first.e1_state, second.e1_state)

    def test_invalid_switch_and_out_of_horizon_support_fail_closed(self) -> None:
        field = fresh_field()
        state = build_neutral_e1_state(field.layer, contract())
        with self.assertRaisesRegex(E1AsynchronousFieldRuntimeError, "boolean"):
            run_e1_asynchronous_field(
                field,
                state,
                self.source,
                self.proposals,
                self.substrate,
                self.afterimage,
                backreaction_enabled=1,
            )
        future = (
            sequence("auditory", ((20, 0.4),)),
            sequence("visual", ((4, -0.6),)),
        )
        with self.assertRaisesRegex(E1AsynchronousFieldRuntimeError, "exactly once"):
            run_e1_asynchronous_field(
                field,
                state,
                future,
                self.proposals,
                self.substrate,
                self.afterimage,
                backreaction_enabled=True,
            )

    def test_private_runtime_is_not_exported(self) -> None:
        private_roles = (
            "E1AsynchronousFieldRun",
            "run_e1_asynchronous_field",
            "E1TransientCoupledFieldStepResult",
            "advance_e1_coupled_fast_shared_field_transient",
        )
        for role in private_roles:
            with self.subTest(role=role):
                self.assertFalse(hasattr(mcm_field_organism, role))
                self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
