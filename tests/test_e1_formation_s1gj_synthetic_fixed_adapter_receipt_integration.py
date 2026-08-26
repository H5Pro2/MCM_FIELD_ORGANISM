from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gh_fresh_field_bridge as bridge_fixture

from mcm_field_organism.e1_formation_s1gh_fresh_field_bridge import bind_e1_formation_s1gh_fresh_fields
from mcm_field_organism.e1_formation_s1gi_fixed_adapter_output_converter import build_e1_formation_s1gi_synthetic_typed_output
from mcm_field_organism.e1_formation_s1gj_synthetic_fixed_adapter_receipt_integration import (
    E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError,
    integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts,
)


class E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = bridge_fixture.E1FormationS1GHFreshFieldBridgeTests
        source.setUpClass()
        cls.bridge = bind_e1_formation_s1gh_fresh_fields(
            source.bindings,
            source.inputs,
        )

    @staticmethod
    def _output(fresh):
        size = len(fresh.ordered_neuron_ids)
        activation = tuple((index + 1) / (2.0 * size) for index in range(size))
        afterimage = tuple(-value / 3.0 for value in activation)
        return build_e1_formation_s1gi_synthetic_typed_output(
            fresh,
            activation,
            afterimage,
        )

    def test_atomically_returns_six_outputs_and_receipts(self) -> None:
        result = integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts(
            self.bridge,
            output_factory=self._output,
        )
        self.assertEqual((6, 6), (result.output_count, result.receipt_count))
        self.assertTrue(result.atomic_return_complete)
        self.assertTrue(result.all_fresh_bindings_consumed_once_in_order)
        self.assertEqual(("r2", "fixed-adapter-ab"), result.role_order[0])
        self.assertEqual(("r8", "fixed-adapter-ba"), result.role_order[-1])

    def test_binds_exact_step_and_support_accounting_without_execution(self) -> None:
        result = integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts(
            self.bridge,
            output_factory=self._output,
        )
        self.assertEqual(
            (("r2", 400), ("r4", 800), ("r8", 1600)),
            result.refinement_step_counts,
        )
        self.assertEqual((2800, 0, 660), (
            result.planned_field_steps,
            result.actual_field_steps_executed,
            result.total_source_support_count,
        ))
        self.assertFalse(result.field_kernel_called)

    def test_preserves_raw_vectors_fields_states_and_adapters(self) -> None:
        result = integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts(
            self.bridge,
            output_factory=self._output,
        )
        self.assertTrue(result.all_raw_vectors_lossless)
        self.assertTrue(result.all_causal_evidence_separate)
        self.assertTrue(result.fresh_fields_preserved)
        self.assertTrue(result.source_states_preserved)
        self.assertTrue(result.fixed_adapters_preserved)

    def test_factory_failure_returns_no_partial_aggregate(self) -> None:
        calls = []

        def failing_factory(fresh):
            calls.append(fresh.binding_digest)
            if len(calls) == 4:
                raise RuntimeError("synthetic output failure")
            return self._output(fresh)

        with self.assertRaisesRegex(
            E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError,
            "no aggregate returned",
        ):
            integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts(
                self.bridge,
                output_factory=failing_factory,
            )
        self.assertEqual(4, len(calls))

    def test_cross_bound_output_and_result_tampering_fail_closed(self) -> None:
        first_output = self._output(self.bridge.fresh_bindings[0])

        def wrong_factory(_fresh):
            return first_output

        with self.assertRaises(
            E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError
        ):
            integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts(
                self.bridge,
                output_factory=wrong_factory,
            )
        result = integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts(
            self.bridge,
            output_factory=self._output,
        )
        with self.assertRaises(
            E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationError
        ):
            replace(result, actual_field_steps_executed=1)

    def test_integration_calls_no_field_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts
        )
        for forbidden in (
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
