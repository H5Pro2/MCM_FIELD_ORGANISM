from __future__ import annotations

import copy
from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gd_fixed_adapter_invocation_binding as binding_fixture

from mcm_field_organism.e1_formation_s1gd_fixed_adapter_invocation_binding import bind_e1_formation_s1gd_fixed_adapter_invocations
from mcm_field_organism.e1_formation_s1gh_fresh_field_bridge import (
    E1FormationS1GHFreshFieldBridgeError,
    bind_e1_formation_s1gh_fresh_fields,
)


class E1FormationS1GHFreshFieldBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = binding_fixture.E1FormationS1GDFixedAdapterInvocationBindingTests
        source.setUpClass()
        cls.inputs = source.inputs
        cls.bindings = bind_e1_formation_s1gd_fixed_adapter_invocations(
            source.wrapper_contract,
            source.contexts,
            source.handoffs,
        )

    def test_binds_six_fresh_fields_once_in_role_order(self) -> None:
        result = bind_e1_formation_s1gh_fresh_fields(self.bindings, self.inputs)
        self.assertEqual((6, 6, 6), (
            result.fresh_field_count,
            result.unique_fresh_field_object_count,
            result.unique_fresh_layer_object_count,
        ))
        self.assertTrue(result.all_invocations_bound_once_in_order)
        self.assertEqual(
            ("r2", "fixed-adapter-ab"),
            result.role_order[0],
        )
        self.assertEqual(
            ("r8", "fixed-adapter-ba"),
            result.role_order[-1],
        )

    def test_fields_are_deep_separate_digest_identical_and_neutral(self) -> None:
        result = bind_e1_formation_s1gh_fresh_fields(self.bindings, self.inputs)
        self.assertTrue(result.all_initial_field_digests_identical)
        self.assertTrue(result.all_fresh_fields_object_separate)
        self.assertTrue(all(
            item.fresh_field is not self.inputs.initial_field
            and item.fresh_field.layer is not self.inputs.initial_field.layer
            and item.neutral_initial_state_preserved
            for item in result.fresh_bindings
        ))

    def test_preserves_states_adapters_and_keeps_probe_closed(self) -> None:
        result = bind_e1_formation_s1gh_fresh_fields(self.bindings, self.inputs)
        self.assertTrue(result.source_states_preserved)
        self.assertTrue(result.fixed_adapters_preserved)
        self.assertEqual((0, 0, 0), (
            result.probe_plans_consumed,
            result.probe_batches_consumed,
            result.field_steps_executed,
        ))
        self.assertFalse(result.field_kernel_called)

    def test_copy_failure_returns_no_partial_aggregate(self) -> None:
        calls = []

        def failing_copier(field):
            calls.append(id(field))
            if len(calls) == 4:
                raise RuntimeError("synthetic copy failure")
            return copy.deepcopy(field)

        with self.assertRaisesRegex(
            E1FormationS1GHFreshFieldBridgeError,
            "no aggregate returned",
        ):
            bind_e1_formation_s1gh_fresh_fields(
                self.bindings,
                self.inputs,
                field_copier=failing_copier,
            )
        self.assertEqual(4, len(calls))

    def test_source_reuse_and_result_tampering_fail_closed(self) -> None:
        with self.assertRaises(E1FormationS1GHFreshFieldBridgeError):
            bind_e1_formation_s1gh_fresh_fields(
                self.bindings,
                self.inputs,
                field_copier=lambda field: field,
            )
        result = bind_e1_formation_s1gh_fresh_fields(self.bindings, self.inputs)
        with self.assertRaises(E1FormationS1GHFreshFieldBridgeError):
            replace(result, field_steps_executed=1)

    def test_bridge_calls_no_probe_or_field_kernel(self) -> None:
        source = inspect.getsource(bind_e1_formation_s1gh_fresh_fields)
        for forbidden in (
            ".probe_plan",
            ".handoff.batches",
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
