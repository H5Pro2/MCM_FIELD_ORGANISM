from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1fz_static_real_receipt_boundary import (
    E1FormationS1FZStaticRealReceiptBoundaryError,
    audit_e1_formation_s1fz_static_real_receipt_boundary,
)


class E1FormationS1FZStaticRealReceiptBoundaryTests(unittest.TestCase):
    def test_existing_p0_and_frozen_outputs_are_losslessly_convertible(self) -> None:
        audit = audit_e1_formation_s1fz_static_real_receipt_boundary()
        self.assertTrue(audit.existing_converter_lossless_with_bound_context)
        self.assertFalse(audit.existing_wrapper_change_required)
        self.assertEqual(22, len(audit.common_receipt_fields))
        self.assertEqual(22, len(audit.direct_output_mapping) + len(audit.bound_context_mapping))

    def test_fixed_adapter_gap_is_wrapper_not_field_kernel(self) -> None:
        audit = audit_e1_formation_s1fz_static_real_receipt_boundary()
        self.assertTrue(audit.fixed_adapter_field_kernel_exists)
        self.assertFalse(audit.fixed_adapter_real_wrapper_implemented)
        self.assertIn("source_state_digest", audit.fixed_wrapper_required_outputs)
        self.assertIn("fixed_adapter_digest", audit.fixed_wrapper_required_outputs)

    def test_fixed_adapter_contract_keeps_live_state_out_of_kernel(self) -> None:
        audit = audit_e1_formation_s1fz_static_real_receipt_boundary()
        self.assertIn("source-state-object-never-passed-to-field-kernel", audit.fixed_wrapper_invariants)
        self.assertIn("fixed-adapter-derived-before-probe-and-held-constant", audit.fixed_wrapper_invariants)

    def test_audit_remains_non_executing_and_tamper_evident(self) -> None:
        audit = audit_e1_formation_s1fz_static_real_receipt_boundary()
        self.assertFalse(audit.fixed_adapter_wrapper_implementation_permitted)
        self.assertFalse(audit.execution_permitted)
        self.assertFalse(audit.field_execution_performed)
        with self.assertRaises(E1FormationS1FZStaticRealReceiptBoundaryError):
            replace(audit, execution_permitted=True)

    def test_audit_calls_no_probe_kernel_or_writer(self) -> None:
        source = inspect.getsource(audit_e1_formation_s1fz_static_real_receipt_boundary)
        for forbidden in ("advance_fixed_e1_adapter_fast_shared_field_transient(", "advance_frozen_e1_fast_shared_field_transient(", "advance_neutral_fast_shared_field_transient(", "run_e1_common_probe_real_probe_wrapper(", "open(", "write_text(", "write_bytes("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
