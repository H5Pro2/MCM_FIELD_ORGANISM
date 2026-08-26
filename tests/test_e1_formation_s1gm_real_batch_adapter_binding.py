from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1gm_real_batch_adapter_binding import (
    E1FormationS1GMRealBatchAdapterBindingError,
    audit_e1_formation_s1gm_real_batch_adapter_binding,
)


class E1FormationS1GMRealBatchAdapterBindingTests(unittest.TestCase):
    def test_real_batch_chain_exists_and_is_signature_bound(self) -> None:
        audit = audit_e1_formation_s1gm_real_batch_adapter_binding()
        self.assertTrue(audit.real_kernel_chain_exists)
        self.assertEqual(6, len(audit.real_batch_chain))
        self.assertIn("field", audit.real_kernel_parameters)
        self.assertNotIn("state", audit.real_kernel_parameters)

    def test_current_token_interface_is_not_directly_real_compatible(self) -> None:
        audit = audit_e1_formation_s1gm_real_batch_adapter_binding()
        self.assertFalse(audit.current_s1gl_interface_carries_live_field)
        self.assertFalse(audit.current_s1gl_interface_directly_real_compatible)
        self.assertIn(
            ("current_field_token_digest", "str"),
            audit.current_s1gl_batch_interface,
        )

    def test_requires_explicit_carrier_and_forbids_hidden_state(self) -> None:
        audit = audit_e1_formation_s1gm_real_batch_adapter_binding()
        self.assertTrue(audit.explicit_live_field_carrier_required)
        self.assertTrue(audit.wrapper_interface_revision_required)
        self.assertFalse(audit.hidden_mutable_field_state_permitted)
        self.assertIn("current_field", audit.required_carrier_fields)
        self.assertIn("terminal-snapshot-from-digest-token", audit.forbidden_state_shortcuts)

    def test_only_carrier_implementation_is_open(self) -> None:
        audit = audit_e1_formation_s1gm_real_batch_adapter_binding()
        self.assertTrue(audit.live_field_carrier_implementation_permitted)
        self.assertFalse(audit.real_batch_adapter_implementation_permitted)
        self.assertFalse(audit.execution_permitted)
        self.assertFalse(audit.field_execution_performed)
        with self.assertRaises(E1FormationS1GMRealBatchAdapterBindingError):
            replace(audit, real_batch_adapter_implementation_permitted=True)

    def test_audit_calls_no_field_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1gm_real_batch_adapter_binding
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
