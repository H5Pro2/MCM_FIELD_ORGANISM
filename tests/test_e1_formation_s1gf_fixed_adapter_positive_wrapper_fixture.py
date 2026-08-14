from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gd_fixed_adapter_invocation_binding as binding_fixture

from mcm_field_organism.e1_formation_s1gd_fixed_adapter_invocation_binding import bind_e1_formation_s1gd_fixed_adapter_invocations
from mcm_field_organism.e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    E1FormationS1GFFixedAdapterPositiveWrapperFixtureError,
    build_e1_formation_s1gf_counting_receipt,
    build_e1_formation_s1gf_synthetic_positive_gate,
    run_e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture,
)


class E1FormationS1GFFixedAdapterPositiveWrapperFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = binding_fixture.E1FormationS1GDFixedAdapterInvocationBindingTests
        source.setUpClass()
        cls.bindings = bind_e1_formation_s1gd_fixed_adapter_invocations(
            source.wrapper_contract,
            source.contexts,
            source.handoffs,
        )

    def _run(self):
        calls = []

        def counting_kernel(invocation, batch):
            calls.append(
                (
                    invocation.context.binding.refinement_id,
                    invocation.context.binding.role_id,
                    batch.batch_index,
                )
            )
            return build_e1_formation_s1gf_counting_receipt(invocation, batch)

        result = run_e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture(
            self.bindings,
            build_e1_formation_s1gf_synthetic_positive_gate(),
            counting_kernel=counting_kernel,
        )
        return result, tuple(calls)

    def test_consumes_six_positive_plans_in_exact_order(self) -> None:
        result, calls = self._run()
        self.assertEqual(6, result.invocation_count)
        self.assertEqual(2800, len(calls))
        self.assertEqual(("r2", "fixed-adapter-ab", 0), calls[0])
        self.assertEqual(("r8", "fixed-adapter-ba", 799), calls[-1])
        self.assertEqual(
            (("r2", 400), ("r4", 800), ("r8", 1600)),
            result.refinement_batch_counts,
        )

    def test_accounting_is_positive_but_real_execution_stays_zero(self) -> None:
        result, _ = self._run()
        self.assertEqual(
            (2800, 2800, 2800, 0),
            (
                result.positive_batches_consumed,
                result.injected_fake_kernel_calls,
                result.accounted_field_steps,
                result.actual_field_steps_executed,
            ),
        )
        self.assertFalse(result.real_kernel_called)
        self.assertFalse(result.field_object_constructed)
        self.assertFalse(result.observed_vectors_present)

    def test_preserves_source_states_and_fixed_adapters(self) -> None:
        result, _ = self._run()
        self.assertTrue(result.source_states_preserved)
        self.assertTrue(result.fixed_adapters_preserved)
        self.assertFalse(result.persistence_performed)
        self.assertFalse(result.claims_permitted)

    def test_injected_kernel_failure_returns_no_partial_aggregate(self) -> None:
        calls = []

        def failing_kernel(invocation, batch):
            calls.append((invocation.invocation_digest, batch.batch_index))
            if len(calls) == 17:
                raise RuntimeError("synthetic failure")
            return build_e1_formation_s1gf_counting_receipt(invocation, batch)

        with self.assertRaisesRegex(
            E1FormationS1GFFixedAdapterPositiveWrapperFixtureError,
            "no aggregate returned",
        ):
            run_e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture(
                self.bindings,
                build_e1_formation_s1gf_synthetic_positive_gate(),
                counting_kernel=failing_kernel,
            )
        self.assertEqual(17, len(calls))

    def test_tampered_gate_and_receipt_fail_closed(self) -> None:
        gate = build_e1_formation_s1gf_synthetic_positive_gate()
        with self.assertRaises(E1FormationS1GFFixedAdapterPositiveWrapperFixtureError):
            replace(gate, real_kernel_permitted=True)

        first_invocation = self.bindings.invocations[0]
        first_batch = first_invocation.context.probe_plan.handoff.batches[0]
        receipt = build_e1_formation_s1gf_counting_receipt(
            first_invocation,
            first_batch,
        )
        with self.assertRaises(E1FormationS1GFFixedAdapterPositiveWrapperFixtureError):
            replace(receipt, actual_field_steps_executed=1)

    def test_fixture_imports_no_real_field_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            run_e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture
        )
        for forbidden in (
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
