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
    E1FormationS1GVRealModeBindingContractError,
    S1_GV_REAL_MODE_BINDINGS,
    S1_GV_REMAINING_CLOSED,
    bind_e1_formation_s1gv_real_mode_binding_contract,
)


class E1FormationS1GVRealModeBindingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = contract_fixture.E1FormationS1GKFixedAdapterRealWrapperContractTests
        source.setUpClass()
        source_contract = prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
            source.bridge,
            source.integration,
        )
        cls.scope = bind_e1_formation_s1gt_six_arm_release_scope_contract(
            source_contract
        )

    def _contract(self):
        return bind_e1_formation_s1gv_real_mode_binding_contract(self.scope)

    def test_real_mode_binding_targets_s1gu_injection_and_s1gs_transition(self) -> None:
        contract = self._contract()
        self.assertEqual(S1_GV_REAL_MODE_BINDINGS, contract.real_mode_bindings)
        self.assertTrue(contract.s1gu_transition_injection_present)
        self.assertTrue(contract.s1gs_real_transition_bound)
        self.assertTrue(contract.real_mode_implementation_permitted_next)
        self.assertEqual(2800, contract.planned_real_transition_count)
        self.assertEqual(2800, contract.planned_field_step_count)
        self.assertEqual(660, contract.planned_source_support_count)

    def test_execution_full_chain_persistence_retry_and_claims_remain_closed(self) -> None:
        contract = self._contract()
        for boundary in (
            "no-real-mode-run",
            "no-owner-authorization",
            "no-formation-run",
            "no-p0-probe",
            "no-frozen-e1-active-probe",
            "no-45-call-chain",
            "no-ec46-evaluation",
            "no-persistence-or-writer",
            "no-retry",
            "no-memory-claim",
        ):
            self.assertIn(boundary, S1_GV_REMAINING_CLOSED)
            self.assertIn(boundary, contract.remaining_closed)
        self.assertFalse(contract.real_mode_execution_permitted)
        self.assertFalse(contract.owner_authorization_present)
        self.assertFalse(contract.field_execution_performed)
        self.assertFalse(contract.full_chain_opened)
        self.assertFalse(contract.persistence_performed)
        self.assertFalse(contract.retry_permitted)
        self.assertFalse(contract.claims_permitted)
        self.assertFalse(contract.memory_decision_permitted)

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = self._contract()
        second = self._contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1FormationS1GVRealModeBindingContractError):
            replace(first, real_mode_execution_permitted=True)
        with self.assertRaises(E1FormationS1GVRealModeBindingContractError):
            replace(first, planned_real_transition_count=2799)

    def test_binder_calls_no_adapter_runner_real_transition_kernel_or_writer(self) -> None:
        source = inspect.getsource(bind_e1_formation_s1gv_real_mode_binding_contract)
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
