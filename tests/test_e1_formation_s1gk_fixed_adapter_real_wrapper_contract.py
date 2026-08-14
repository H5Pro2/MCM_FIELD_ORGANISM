from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

import tests.test_e1_formation_s1gj_synthetic_fixed_adapter_receipt_integration as integration_fixture

from mcm_field_organism.e1_formation_s1gj_synthetic_fixed_adapter_receipt_integration import integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts
from mcm_field_organism.e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    E1FormationS1GKFixedAdapterRealWrapperContractError,
    prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract,
)


class E1FormationS1GKFixedAdapterRealWrapperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = integration_fixture.E1FormationS1GJSyntheticFixedAdapterReceiptIntegrationTests
        source.setUpClass()
        cls.bridge = source.bridge
        cls.integration = integrate_e1_formation_s1gj_synthetic_fixed_adapter_receipts(
            cls.bridge,
            output_factory=source._output,
        )

    def test_binds_six_arm_real_wrapper_budget_and_schema(self) -> None:
        contract = prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
            self.bridge,
            self.integration,
        )
        self.assertEqual((6, 2800, 2800, 660), (
            contract.wrapper_arm_count,
            contract.planned_kernel_call_count,
            contract.planned_field_step_count,
            contract.planned_source_support_count,
        ))
        self.assertEqual(18, len(contract.output_fields))
        self.assertEqual(22, len(contract.receipt_fields))

    def test_requires_atomic_return_and_fail_closed_policy(self) -> None:
        contract = prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
            self.bridge,
            self.integration,
        )
        self.assertTrue(contract.atomic_six_return_required)
        self.assertIn("return-no-partial-aggregate", contract.abort_policy)
        self.assertIn("no-retry", contract.abort_policy)
        self.assertFalse(contract.retry_permitted)
        self.assertFalse(contract.posthoc_parameter_change_permitted)

    def test_allows_implementation_but_not_execution(self) -> None:
        contract = prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
            self.bridge,
            self.integration,
        )
        self.assertTrue(contract.real_wrapper_implementation_permitted)
        self.assertFalse(contract.owner_authorization_present)
        self.assertFalse(contract.execution_permitted)
        self.assertFalse(contract.field_execution_performed)
        self.assertFalse(contract.live_state_permitted_in_fixed_kernel)

    def test_tampering_fails_closed(self) -> None:
        contract = prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract(
            self.bridge,
            self.integration,
        )
        with self.assertRaises(E1FormationS1GKFixedAdapterRealWrapperContractError):
            replace(contract, execution_permitted=True)
        with self.assertRaises(E1FormationS1GKFixedAdapterRealWrapperContractError):
            replace(contract, planned_kernel_call_count=2799)

    def test_contract_builder_calls_no_field_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            prepare_e1_formation_s1gk_fixed_adapter_real_wrapper_contract
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
