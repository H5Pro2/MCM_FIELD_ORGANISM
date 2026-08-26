from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from tests import (
    test_e1_formation_s1gk_fixed_adapter_real_wrapper_contract as contract_fixture,
)

from mcm_field_organism.e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_REFINEMENT_BATCH_COUNTS,
    S1_GF_ROLE_ORDER,
)
from mcm_field_organism.e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract,
)
from mcm_field_organism.e1_formation_s1gt_six_arm_release_scope_contract import (
    E1FormationS1GTSixArmReleaseScopeContractError,
    S1_GT_EXCLUDED_SCOPE,
    S1_GT_RELEASE_SCOPE,
    bind_e1_formation_s1gt_six_arm_release_scope_contract,
)


class E1FormationS1GTSixArmReleaseScopeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = contract_fixture.E1FormationS1GKFixedAdapterRealWrapperContractTests
        source.setUpClass()
        cls.source_contract = (
            prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
                source.bridge,
                source.integration,
            )
        )

    def _contract(self):
        return bind_e1_formation_s1gt_six_arm_release_scope_contract(
            self.source_contract
        )

    def test_six_arm_fixed_adapter_scope_and_budget_are_bound(self) -> None:
        contract = self._contract()
        self.assertEqual(S1_GT_RELEASE_SCOPE, contract.release_scope)
        self.assertEqual(S1_GF_ROLE_ORDER, contract.role_order)
        self.assertEqual(
            S1_GF_REFINEMENT_BATCH_COUNTS,
            contract.refinement_step_counts,
        )
        self.assertEqual(6, contract.fixed_adapter_arm_count)
        self.assertEqual(2800, contract.planned_real_transition_count)
        self.assertEqual(2800, contract.planned_field_step_count)
        self.assertEqual(660, contract.planned_source_support_count)

    def test_full_matrix_execution_memory_decision_and_writers_are_excluded(self) -> None:
        contract = self._contract()
        for excluded in (
            "no-45-call-same-session-chain",
            "no-ec46-or-memory-decision",
            "no-formation-run",
            "no-writer-or-persistence",
            "no-retry-or-posthoc-parameter-change",
        ):
            self.assertIn(excluded, S1_GT_EXCLUDED_SCOPE)
            self.assertIn(excluded, contract.excluded_scope)
        self.assertEqual(0, contract.full_chain_call_count_permitted)
        self.assertEqual(0, contract.full_chain_field_steps_permitted)
        self.assertFalse(contract.execution_permitted)
        self.assertFalse(contract.field_execution_performed)
        self.assertFalse(contract.persistence_performed)
        self.assertFalse(contract.claims_permitted)
        self.assertFalse(contract.memory_decision_permitted)

    def test_required_gates_keep_s1go_synthetic_reference_closed(self) -> None:
        contract = self._contract()
        self.assertIn(
            "s1go-synthetic-only-reference-remains-closed-to-real-envelope",
            contract.required_gates,
        )
        self.assertTrue(contract.s1gs_adapter_imported_for_static_binding)
        self.assertTrue(contract.s1go_wrapper_reference_imported_for_static_gate_check)
        self.assertTrue(contract.six_arm_implementation_permitted_next)
        self.assertFalse(contract.owner_authorization_present)

    def test_contract_is_deterministic_and_tamper_evident(self) -> None:
        first = self._contract()
        second = self._contract()
        self.assertEqual(first.contract_digest, second.contract_digest)
        with self.assertRaises(E1FormationS1GTSixArmReleaseScopeContractError):
            replace(first, execution_permitted=True)
        with self.assertRaises(E1FormationS1GTSixArmReleaseScopeContractError):
            replace(first, full_chain_call_count_permitted=45)

    def test_binder_calls_no_real_runner_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            bind_e1_formation_s1gt_six_arm_release_scope_contract
        )
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
