from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gd_fixed_adapter_invocation_binding as binding_fixture

from mcm_field_organism.e1_formation_s1gd_fixed_adapter_invocation_binding import bind_e1_formation_s1gd_fixed_adapter_invocations
from mcm_field_organism.e1_formation_s1ge_fixed_adapter_nullbatch_shell import (
    E1FormationS1GEFixedAdapterNullBatchShellError,
    build_e1_formation_s1ge_synthetic_nullbatch_gate,
    validate_all_e1_formation_s1ge_fixed_adapter_nullbatches,
    validate_e1_formation_s1ge_fixed_adapter_nullbatch,
)


class E1FormationS1GEFixedAdapterNullBatchShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = binding_fixture.E1FormationS1GDFixedAdapterInvocationBindingTests
        source.setUpClass()
        cls.bindings = bind_e1_formation_s1gd_fixed_adapter_invocations(source.wrapper_contract, source.contexts, source.handoffs)

    def test_validates_all_six_without_positive_work(self) -> None:
        gate = build_e1_formation_s1ge_synthetic_nullbatch_gate()
        result = validate_all_e1_formation_s1ge_fixed_adapter_nullbatches(self.bindings, gate)
        self.assertEqual(6, result.validated_invocation_count)
        self.assertTrue(result.all_six_inputs_validated)
        self.assertEqual((0, 0, 0, 0), (result.field_objects_constructed, result.kernel_calls, result.field_steps_executed, result.observed_outputs_emitted))

    def test_outputs_carry_only_validated_input_digests(self) -> None:
        gate = build_e1_formation_s1ge_synthetic_nullbatch_gate()
        result = validate_all_e1_formation_s1ge_fixed_adapter_nullbatches(self.bindings, gate)
        self.assertTrue(all(item.input_validation_complete for item in result.outputs))
        self.assertTrue(all(not item.observed_vectors_present and not item.probe_output_emitted and not item.receipt_emitted for item in result.outputs))

    def test_positive_batch_gate_fails_closed(self) -> None:
        gate = build_e1_formation_s1ge_synthetic_nullbatch_gate()
        with self.assertRaises(E1FormationS1GEFixedAdapterNullBatchShellError):
            replace(gate, batch_count=1)

    def test_result_is_deterministic_and_tamper_evident(self) -> None:
        gate = build_e1_formation_s1ge_synthetic_nullbatch_gate()
        first = validate_all_e1_formation_s1ge_fixed_adapter_nullbatches(self.bindings, gate)
        second = validate_all_e1_formation_s1ge_fixed_adapter_nullbatches(self.bindings, gate)
        self.assertEqual(first.result_digest, second.result_digest)
        with self.assertRaises(E1FormationS1GEFixedAdapterNullBatchShellError):
            replace(first, kernel_calls=1)

    def test_shell_calls_no_field_kernel_writer_or_plan_batches(self) -> None:
        source = inspect.getsource(validate_e1_formation_s1ge_fixed_adapter_nullbatch)
        for forbidden in ("probe_plan.handoff.batches", "advance_fixed_e1_adapter_fast_shared_field_transient(", "map_proposal_batch_to_transient_docks(", "project_transient_docks_to_neuron_inputs(", "open(", "write_text(", "write_bytes("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
