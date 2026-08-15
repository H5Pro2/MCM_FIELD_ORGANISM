from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1gu_real_transition_builder_contract import (
    E1FormationS1GURealTransitionBuilderContractError,
    audit_e1_formation_s1gu_real_transition_builder_contract,
)


class E1FormationS1GURealTransitionBuilderContractTests(unittest.TestCase):
    def test_builder_interface_requires_next_field_and_adapter_receipt(self) -> None:
        contract = audit_e1_formation_s1gu_real_transition_builder_contract()
        self.assertIn(
            ("next_field", "SharedMCMField"),
            contract.builder_interface,
        )
        self.assertIn(
            (
                "adapter_call_receipt",
                "E1FormationS1GVRealAdapterCallReceipt",
            ),
            contract.builder_interface,
        )
        self.assertFalse(contract.next_field_alone_is_sufficient_provenance)
        self.assertTrue(contract.typed_adapter_call_receipt_required)

    def test_receipt_binds_gate_token_route_fields_and_attestations(self) -> None:
        contract = audit_e1_formation_s1gu_real_transition_builder_contract()
        for required in (
            "gate_digest",
            "authorization_digest",
            "consumed_token_digest",
            "previous_carrier_digest",
            "previous_field_digest",
            "next_field_digest",
            "source_state_digest_before",
            "source_state_digest_after",
            "fixed_adapter_digest_before",
            "fixed_adapter_digest_after",
            "adapter_calls",
            "field_steps_executed",
        ):
            self.assertIn(required, contract.required_adapter_receipt_fields)

    def test_builder_validation_requires_new_one_step_field(self) -> None:
        contract = audit_e1_formation_s1gu_real_transition_builder_contract()
        self.assertIn(
            "require-new-field-object-and-one-layer-tick-advance",
            contract.validation_sequence,
        )
        self.assertIn(
            "construct-next-carrier-with-one-batch-support-and-step-increment",
            contract.validation_sequence,
        )
        self.assertIn(
            "next-field-object-is-reused-or-digest-mismatched",
            contract.abort_conditions,
        )

    def test_receipt_schema_builder_execution_and_token_remain_closed(self) -> None:
        contract = audit_e1_formation_s1gu_real_transition_builder_contract()
        self.assertFalse(contract.adapter_call_receipt_schema_implemented)
        self.assertFalse(contract.pure_transition_builder_implementation_permitted)
        self.assertFalse(contract.pure_transition_builder_implemented)
        self.assertFalse(contract.adapter_or_kernel_access_permitted)
        self.assertFalse(contract.authorization_token_creation_permitted)
        self.assertFalse(contract.execution_permitted)
        self.assertFalse(contract.persistence_permitted)
        self.assertFalse(contract.claims_permitted)

    def test_contract_is_deterministic_and_tampering_fails_closed(self) -> None:
        first = audit_e1_formation_s1gu_real_transition_builder_contract()
        second = audit_e1_formation_s1gu_real_transition_builder_contract()
        self.assertEqual(first, second)
        self.assertTrue(all(value for _, value in first.checks))
        with self.assertRaises(E1FormationS1GURealTransitionBuilderContractError):
            replace(first, next_field_alone_is_sufficient_provenance=True)
        with self.assertRaises(E1FormationS1GURealTransitionBuilderContractError):
            replace(first, execution_permitted=True)

    def test_audit_calls_no_adapter_kernel_token_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1gu_real_transition_builder_contract
        )
        for forbidden in (
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "issue_e1_formation_s1gt_synthetic_single_use_token(",
            ".consume(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
