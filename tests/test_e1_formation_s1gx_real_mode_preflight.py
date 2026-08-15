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
    E1FormationS1GXRealModePreflightError,
    preflight_e1_formation_s1gx_real_mode,
)


class E1FormationS1GXRealModePreflightTests(unittest.TestCase):
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
        cls.real_mode_contract = bind_e1_formation_s1gv_real_mode_binding_contract(
            cls.scope
        )
        cls.gate = build_e1_formation_s1gw_real_mode_gate(cls.real_mode_contract)

    def _preflight(self):
        return preflight_e1_formation_s1gx_real_mode(
            self.scope,
            self.real_mode_contract,
            self.gate,
            self.source_contract,
            self.bridge,
        )

    def test_preflight_binds_callable_and_expected_six_arm_shape(self) -> None:
        result = self._preflight()
        self.assertEqual(
            "advance_e1_formation_s1gs_real_single_batch_transition",
            result.selected_transition_name,
        )
        self.assertTrue(result.callable_selected)
        self.assertEqual(6, result.expected_arm_count)
        self.assertEqual(2800, result.expected_transition_count)
        self.assertEqual(2800, result.expected_field_step_count)
        self.assertEqual(660, result.expected_source_support_count)
        self.assertEqual(6, result.expected_output_count)
        self.assertEqual(6, result.expected_receipt_count)

    def test_preflight_does_not_execute_callable_runner_or_claim_path(self) -> None:
        result = self._preflight()
        self.assertFalse(result.callable_executed)
        self.assertFalse(result.s1gu_runner_executed)
        self.assertFalse(result.real_mode_execution_permitted)
        self.assertFalse(result.owner_authorization_present)
        self.assertFalse(result.field_execution_performed)
        self.assertFalse(result.full_chain_opened)
        self.assertFalse(result.persistence_performed)
        self.assertFalse(result.retry_permitted)
        self.assertFalse(result.claims_permitted)
        self.assertFalse(result.memory_decision_permitted)
        self.assertEqual(
            "S1GU_REAL_MODE_PREFLIGHT_BOUND_CALLABLE_NOT_EXECUTED",
            result.decision,
        )

    def test_preflight_is_deterministic_and_tamper_evident(self) -> None:
        first = self._preflight()
        second = self._preflight()
        self.assertEqual(first.preflight_digest, second.preflight_digest)
        with self.assertRaises(E1FormationS1GXRealModePreflightError):
            replace(first, callable_executed=True)
        with self.assertRaises(E1FormationS1GXRealModePreflightError):
            replace(first, expected_transition_count=2799)

    def test_preflight_calls_no_s1gu_runner_real_transition_kernel_or_writer(self) -> None:
        source = inspect.getsource(preflight_e1_formation_s1gx_real_mode)
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
