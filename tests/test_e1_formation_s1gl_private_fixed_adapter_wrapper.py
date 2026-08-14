from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gk_fixed_adapter_real_wrapper_contract as contract_fixture

from mcm_field_organism.e1_formation_s1gk_fixed_adapter_real_wrapper_contract import prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract
from mcm_field_organism.e1_formation_s1gl_private_fixed_adapter_wrapper import (
    E1FormationS1GLPrivateFixedAdapterWrapperError,
    build_e1_formation_s1gl_synthetic_batch_receipt,
    build_e1_formation_s1gl_synthetic_only_gate,
    build_e1_formation_s1gl_synthetic_terminal_output,
    run_e1_formation_s1gl_private_fixed_adapter_wrapper,
)


class E1FormationS1GLPrivateFixedAdapterWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = contract_fixture.E1FormationS1GKFixedAdapterRealWrapperContractTests
        source.setUpClass()
        cls.bridge = source.bridge
        cls.contract = prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
            source.bridge,
            source.integration,
        )

    def _run(self, batch_kernel=build_e1_formation_s1gl_synthetic_batch_receipt):
        return run_e1_formation_s1gl_private_fixed_adapter_wrapper(
            self.contract,
            self.bridge,
            build_e1_formation_s1gl_synthetic_only_gate(),
            batch_kernel=batch_kernel,
            terminal_output_factory=build_e1_formation_s1gl_synthetic_terminal_output,
        )

    def test_private_wrapper_consumes_all_six_arms_and_batches(self) -> None:
        result = self._run()
        self.assertEqual((6, 2800, 2800), (
            result.arm_count,
            result.injected_batch_kernel_calls,
            result.accounted_field_steps,
        ))
        self.assertEqual(
            (("r2", 400), ("r4", 800), ("r8", 1600)),
            result.refinement_step_counts,
        )
        self.assertTrue(result.all_batches_consumed_once_in_order)
        self.assertTrue(result.all_field_tokens_contiguous)

    def test_returns_six_bound_outputs_and_receipts_without_real_steps(self) -> None:
        result = self._run()
        self.assertEqual((6, 6, 660, 0), (
            result.terminal_output_count,
            result.common_receipt_count,
            result.source_support_count,
            result.actual_field_steps_executed,
        ))
        self.assertTrue(result.all_outputs_and_receipts_bound)
        self.assertFalse(result.real_batch_adapter_called)

    def test_preserves_fields_states_and_adapters(self) -> None:
        result = self._run()
        self.assertTrue(result.fresh_fields_preserved)
        self.assertTrue(result.source_states_preserved)
        self.assertTrue(result.fixed_adapters_preserved)
        self.assertFalse(result.persistence_performed)
        self.assertFalse(result.claims_permitted)

    def test_injected_batch_failure_returns_no_partial_aggregate(self) -> None:
        calls = []

        def failing_kernel(fresh, batch, token):
            calls.append((fresh.binding_digest, batch.batch_index))
            if len(calls) == 17:
                raise RuntimeError("synthetic batch failure")
            return build_e1_formation_s1gl_synthetic_batch_receipt(
                fresh,
                batch,
                token,
            )

        with self.assertRaisesRegex(
            E1FormationS1GLPrivateFixedAdapterWrapperError,
            "no aggregate returned",
        ):
            self._run(batch_kernel=failing_kernel)
        self.assertEqual(17, len(calls))

    def test_gate_and_batch_token_tampering_fail_closed(self) -> None:
        gate = build_e1_formation_s1gl_synthetic_only_gate()
        with self.assertRaises(E1FormationS1GLPrivateFixedAdapterWrapperError):
            replace(gate, real_field_execution_permitted=True)

        def wrong_token_kernel(fresh, batch, token):
            receipt = build_e1_formation_s1gl_synthetic_batch_receipt(
                fresh,
                batch,
                token,
            )
            return replace(
                receipt,
                current_field_token_digest="0" * 64,
                receipt_digest=receipt.receipt_digest,
            )

        with self.assertRaises(E1FormationS1GLPrivateFixedAdapterWrapperError):
            self._run(batch_kernel=wrong_token_kernel)

    def test_wrapper_contains_no_real_batch_adapter_or_writer(self) -> None:
        source = inspect.getsource(
            run_e1_formation_s1gl_private_fixed_adapter_wrapper
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
