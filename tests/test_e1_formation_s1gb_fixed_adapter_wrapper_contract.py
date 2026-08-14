from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1gb_fixed_adapter_wrapper_contract import (
    E1FormationS1GBFixedAdapterWrapperContractError,
    prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract,
)


class E1FormationS1GBFixedAdapterWrapperContractTests(unittest.TestCase):
    def test_identifies_exact_probe_object_bridge_as_the_remaining_input_gap(self) -> None:
        contract = prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract()
        self.assertTrue(contract.current_probe_source_digest_bound)
        self.assertFalse(contract.exact_probe_sequence_object_present_in_ten_role_chain)
        self.assertFalse(contract.exact_probe_plan_object_present_in_ten_role_chain)
        self.assertTrue(contract.new_probe_context_bridge_required)

    def test_keeps_old_eight_role_context_from_substituting_for_new_slot(self) -> None:
        contract = prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract()
        self.assertIn("binding", contract.probe_context_fields)
        self.assertIn("probe_sequences", contract.probe_context_fields)
        self.assertIn("probe_plan", contract.probe_context_fields)
        self.assertEqual(6, contract.fixed_role_count)

    def test_source_state_is_attestation_only_and_excluded_from_kernel(self) -> None:
        contract = prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract()
        self.assertIn("never-pass-source-state-object-to-field-kernel", contract.loop_contract)
        self.assertIn(("source_state", "exact E1LocalEdgePlasticityState for attestation only"), contract.wrapper_inputs)

    def test_only_context_bridge_implementation_is_open(self) -> None:
        contract = prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract()
        self.assertTrue(contract.probe_context_bridge_implementation_permitted)
        self.assertFalse(contract.fixed_adapter_wrapper_implementation_permitted)
        self.assertFalse(contract.execution_permitted)
        with self.assertRaises(E1FormationS1GBFixedAdapterWrapperContractError):
            replace(contract, fixed_adapter_wrapper_implementation_permitted=True)

    def test_builder_calls_no_probe_kernel_or_writer(self) -> None:
        source = inspect.getsource(prepare_e1_formation_s1gb_fixed_adapter_wrapper_contract)
        for forbidden in ("advance_fixed_e1_adapter_fast_shared_field_transient(", "advance_frozen_e1_fast_shared_field_transient(", "advance_neutral_fast_shared_field_transient(", "open(", "write_text(", "write_bytes("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
