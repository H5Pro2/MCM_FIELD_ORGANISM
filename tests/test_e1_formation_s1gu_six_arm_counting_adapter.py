from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from tests import (
    test_e1_formation_s1gk_fixed_adapter_real_wrapper_contract as contract_fixture,
)

from mcm_field_organism.e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract,
)
from mcm_field_organism.e1_formation_s1gn_live_field_carrier import (
    advance_e1_formation_s1gn_live_field_carrier_synthetically,
)
from mcm_field_organism.e1_formation_s1gt_six_arm_release_scope_contract import (
    bind_e1_formation_s1gt_six_arm_release_scope_contract,
)
from mcm_field_organism.e1_formation_s1gu_six_arm_counting_adapter import (
    E1FormationS1GUSixArmCountingAdapterError,
    run_e1_formation_s1gu_six_arm_counting_adapter,
)


class E1FormationS1GUSixArmCountingAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = contract_fixture.E1FormationS1GKFixedAdapterRealWrapperContractTests
        source.setUpClass()
        cls.bridge = source.bridge
        cls.source_contract = (
            prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
                source.bridge,
                source.integration,
            )
        )
        cls.scope = bind_e1_formation_s1gt_six_arm_release_scope_contract(
            cls.source_contract
        )

    def _run(self, **kwargs):
        return run_e1_formation_s1gu_six_arm_counting_adapter(
            self.scope,
            self.source_contract,
            self.bridge,
            **kwargs,
        )

    def test_counting_adapter_consumes_six_arms_and_all_batches(self) -> None:
        result = self._run()
        self.assertEqual(6, result.arm_count)
        self.assertEqual(2800, result.transition_call_count)
        self.assertEqual(2800, result.accounted_field_steps)
        self.assertEqual(0, result.actual_field_steps_executed)
        self.assertEqual(660, result.source_support_count)
        self.assertEqual(
            (("r2", 400), ("r4", 800), ("r8", 1600)),
            result.refinement_step_counts,
        )
        self.assertEqual(
            (("synthetic-no-field-advance", 2800),),
            result.transition_kind_counts,
        )

    def test_outputs_receipts_and_terminal_carriers_return_atomically(self) -> None:
        result = self._run()
        self.assertEqual((6, 6, 6), (
            result.terminal_carrier_count,
            result.terminal_output_count,
            result.common_receipt_count,
        ))
        self.assertTrue(result.all_batches_consumed_once_in_order)
        self.assertTrue(result.all_transitions_validated_by_shared_envelope)
        self.assertTrue(result.all_outputs_and_receipts_bound)
        self.assertTrue(result.atomic_return_complete)
        self.assertTrue(result.source_states_preserved)
        self.assertTrue(result.fixed_adapters_preserved)

    def test_execution_claim_and_full_chain_boundaries_stay_closed(self) -> None:
        result = self._run()
        self.assertFalse(result.real_kernel_called_by_adapter)
        self.assertFalse(result.full_chain_opened)
        self.assertFalse(result.persistence_performed)
        self.assertFalse(result.claims_permitted)
        self.assertFalse(result.memory_decision_permitted)
        self.assertEqual(
            "SIX_ARM_COUNTING_ADAPTER_VALIDATED_WITH_INJECTED_TRANSITIONS_REAL_KERNEL_CLOSED",
            result.decision,
        )

    def test_transition_failure_returns_no_partial_aggregate(self) -> None:
        calls = []

        def failing_transition(fresh, batch, carrier):
            calls.append((fresh.binding_digest, batch.batch_index))
            if len(calls) == 23:
                raise RuntimeError("counting transition failure")
            return advance_e1_formation_s1gn_live_field_carrier_synthetically(
                fresh,
                batch,
                carrier,
            )

        with self.assertRaisesRegex(
            E1FormationS1GUSixArmCountingAdapterError,
            "no partial aggregate",
        ):
            self._run(carrier_transition=failing_transition)
        self.assertEqual(23, len(calls))

    def test_result_is_tamper_evident(self) -> None:
        result = self._run()
        with self.assertRaises(E1FormationS1GUSixArmCountingAdapterError):
            replace(result, full_chain_opened=True)
        with self.assertRaises(E1FormationS1GUSixArmCountingAdapterError):
            replace(result, transition_call_count=2799)

    def test_adapter_calls_no_real_kernel_writer_or_full_chain_runner(self) -> None:
        source = inspect.getsource(run_e1_formation_s1gu_six_arm_counting_adapter)
        for forbidden in (
            "advance_e1_formation_s1gs_real_single_batch_transition(",
            "run_e1_formation_s1go_private_carrier_wrapper(",
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
