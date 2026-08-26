from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_formation_s1gg_static_fixed_adapter_real_kernel_binding import (
    E1FormationS1GGStaticFixedAdapterRealKernelBindingError,
    audit_e1_formation_s1gg_static_fixed_adapter_real_kernel_binding,
)


class E1FormationS1GGStaticFixedAdapterRealKernelBindingTests(unittest.TestCase):
    def test_binds_complete_real_kernel_call_chain_statically(self) -> None:
        audit = audit_e1_formation_s1gg_static_fixed_adapter_real_kernel_binding()
        self.assertTrue(audit.real_kernel_chain_compatible)
        self.assertEqual(7, len(audit.kernel_chain))
        self.assertIn(
            "advance_fixed_e1_adapter_fast_shared_field_transient",
            audit.kernel_chain,
        )
        self.assertEqual(22, len(audit.common_receipt_fields))

    def test_keeps_live_state_out_of_fixed_kernel(self) -> None:
        audit = audit_e1_formation_s1gg_static_fixed_adapter_real_kernel_binding()
        self.assertTrue(audit.source_state_attestation_available)
        self.assertNotIn("state", audit.fixed_kernel_parameters)
        self.assertNotIn("frozen_e1_state", audit.fixed_kernel_parameters)

    def test_identifies_only_fresh_field_object_bridge_as_missing(self) -> None:
        audit = audit_e1_formation_s1gg_static_fixed_adapter_real_kernel_binding()
        self.assertTrue(audit.upstream_initial_field_available)
        self.assertFalse(audit.fresh_field_present_in_s1gd_invocation)
        self.assertTrue(audit.fresh_field_bridge_required)
        self.assertEqual(
            ("six-object-separated-fresh-fields-bound-to-s1gd-invocations",),
            audit.missing_objects,
        )

    def test_execution_and_wrapper_remain_closed_and_tamper_evident(self) -> None:
        audit = audit_e1_formation_s1gg_static_fixed_adapter_real_kernel_binding()
        self.assertFalse(audit.fixed_adapter_real_wrapper_implemented)
        self.assertFalse(audit.execution_permitted)
        self.assertFalse(audit.field_execution_performed)
        with self.assertRaises(
            E1FormationS1GGStaticFixedAdapterRealKernelBindingError
        ):
            replace(audit, execution_permitted=True)

    def test_audit_calls_no_field_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1gg_static_fixed_adapter_real_kernel_binding
        )
        for forbidden in (
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_neutral_fast_shared_field_transient(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
