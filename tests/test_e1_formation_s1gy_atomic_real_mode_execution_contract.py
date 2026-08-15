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
from mcm_field_organism.e1_formation_s1gt_six_arm_release_scope_contract import (
    bind_e1_formation_s1gt_six_arm_release_scope_contract,
)
from mcm_field_organism.e1_formation_s1gv_real_mode_binding_contract import (
    bind_e1_formation_s1gv_real_mode_binding_contract,
)
from mcm_field_organism.e1_formation_s1gw_real_mode_gate import (
    build_e1_formation_s1gw_real_mode_gate,
)
from mcm_field_organism.e1_formation_s1gx_real_mode_preflight import (
    preflight_e1_formation_s1gx_real_mode,
)
from mcm_field_organism.e1_formation_s1gy_atomic_real_mode_execution_contract import (
    E1FormationS1GYAtomicRealModeExecutionContractError,
    S1_GY_ATOMIC_RESULT,
    S1_GY_PRECONDITIONS,
    S1_GY_SINGLE_CALL,
    bind_e1_formation_s1gy_atomic_real_mode_execution_contract,
)


class E1FormationS1GYAtomicRealModeExecutionContractTests(unittest.TestCase):
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
        scope = bind_e1_formation_s1gt_six_arm_release_scope_contract(
            cls.source_contract
        )
        real_mode = bind_e1_formation_s1gv_real_mode_binding_contract(scope)
        gate = build_e1_formation_s1gw_real_mode_gate(real_mode)
        cls.preflight = preflight_e1_formation_s1gx_real_mode(
            scope,
            real_mode,
            gate,
            cls.source_contract,
            cls.bridge,
        )

    def _contract(self):
        return bind_e1_formation_s1gy_atomic_real_mode_execution_contract(
            self.preflight
        )

    def test_contract_binds_preconditions_and_single_later_call(self) -> None:
        contract = self._contract()
        self.assertEqual(S1_GY_PRECONDITIONS, contract.preconditions)
        self.assertEqual(S1_GY_SINGLE_CALL, contract.single_call_contract)
        self.assertIn("one-later-s1gu-call-only", contract.single_call_contract)
        self.assertIn("carrier-transition-from-s1gw-gate-only", contract.single_call_contract)
        self.assertIn("no-retry", contract.single_call_contract)
        self.assertTrue(contract.implementation_permitted_next)
        self.assertFalse(contract.execution_permitted)

    def test_contract_binds_atomic_result_without_ec46_or_memory_decision(self) -> None:
        contract = self._contract()
        self.assertEqual(S1_GY_ATOMIC_RESULT, contract.atomic_result_contract)
        self.assertEqual(6, contract.expected_arm_count)
        self.assertEqual(2800, contract.expected_transition_count)
        self.assertEqual(2800, contract.expected_field_step_count)
        self.assertEqual(660, contract.expected_source_support_count)
        self.assertEqual(6, contract.expected_output_count)
        self.assertEqual(6, contract.expected_receipt_count)
        self.assertFalse(contract.ec46_evaluation_permitted)
        self.assertFalse(contract.claims_permitted)
        self.assertFalse(contract.memory_decision_permitted)

    def test_contract_keeps_execution_owner_retry_and_persistence_closed(self) -> None:
        contract = self._contract()
        self.assertFalse(contract.owner_authorization_present)
        self.assertFalse(contract.field_execution_performed)
        self.assertFalse(contract.retry_permitted)
        self.assertFalse(contract.persistence_performed)
        self.assertEqual(
            "ATOMIC_REAL_MODE_EXECUTION_CONTRACT_BOUND_NO_EXECUTION",
            contract.decision,
        )

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = self._contract()
        second = self._contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1FormationS1GYAtomicRealModeExecutionContractError):
            replace(first, execution_permitted=True)
        with self.assertRaises(E1FormationS1GYAtomicRealModeExecutionContractError):
            replace(first, expected_transition_count=2799)

    def test_contract_calls_no_runner_transition_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            bind_e1_formation_s1gy_atomic_real_mode_execution_contract
        )
        for forbidden in (
            "run_e1_formation_s1gu_six_arm_counting_adapter(",
            "advance_e1_formation_s1gs_real_single_batch_transition(",
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
