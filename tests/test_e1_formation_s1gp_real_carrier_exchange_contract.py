from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1gp_real_carrier_exchange_contract import (
    E1FormationS1GPRealCarrierExchangeContractError,
    audit_e1_formation_s1gp_real_carrier_exchange_contract,
)


class E1FormationS1GPRealCarrierExchangeContractTests(unittest.TestCase):
    def test_real_exchange_inputs_and_adapter_chain_are_bound(self) -> None:
        contract = audit_e1_formation_s1gp_real_carrier_exchange_contract()
        self.assertTrue(contract.carrier_input_is_real_adapter_complete)
        self.assertTrue(contract.real_adapter_chain_is_signature_compatible)
        self.assertEqual(
            ("fresh", "batch", "carrier"),
            tuple(name for name, _ in contract.exchange_inputs),
        )
        self.assertEqual(8, len(contract.real_adapter_sequence))

    def test_preconditions_and_postconditions_keep_state_explicit(self) -> None:
        contract = audit_e1_formation_s1gp_real_carrier_exchange_contract()
        self.assertIn(
            "carrier-current-field-digest-recomputes-exactly",
            contract.preconditions,
        )
        self.assertIn(
            "next-field-is-new-explicit-object",
            contract.postconditions,
        )
        self.assertIn(
            "actual-field-step-count-increments-by-one",
            contract.postconditions,
        )
        self.assertFalse(contract.hidden_field_state_permitted)

    def test_synthetic_transition_and_go_wrapper_remain_synthetic(
        self,
    ) -> None:
        contract = audit_e1_formation_s1gp_real_carrier_exchange_contract()
        self.assertFalse(contract.synthetic_transition_is_real_compatible)
        self.assertFalse(contract.current_go_wrapper_is_real_transition_compatible)
        self.assertTrue(contract.separate_real_transition_type_required)
        self.assertEqual(5, len(contract.incompatibilities))

    def test_only_real_transition_schema_is_open(self) -> None:
        contract = audit_e1_formation_s1gp_real_carrier_exchange_contract()
        self.assertTrue(contract.real_transition_schema_implementation_permitted)
        self.assertFalse(contract.real_adapter_implementation_permitted)
        self.assertFalse(contract.execution_permitted)
        self.assertFalse(contract.field_execution_performed)
        self.assertFalse(contract.persistence_performed)
        self.assertFalse(contract.claims_permitted)
        with self.assertRaises(E1FormationS1GPRealCarrierExchangeContractError):
            replace(contract, real_adapter_implementation_permitted=True)

    def test_contract_is_deterministic_and_all_checks_pass(self) -> None:
        first = audit_e1_formation_s1gp_real_carrier_exchange_contract()
        second = audit_e1_formation_s1gp_real_carrier_exchange_contract()
        self.assertEqual(first, second)
        self.assertTrue(all(value for _, value in first.checks))
        self.assertEqual(
            "REAL_EXCHANGE_POINT_BOUND_SEPARATE_REAL_TRANSITION_TYPE_REQUIRED",
            first.decision,
        )

    def test_audit_calls_no_adapter_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1gp_real_carrier_exchange_contract
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
