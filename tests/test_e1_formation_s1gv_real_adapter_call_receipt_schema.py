from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_formation_s1gv_real_adapter_call_receipt_schema import (
    E1FormationS1GVRealAdapterCallReceipt,
    audit_e1_formation_s1gv_real_adapter_call_receipt_schema,
)


class E1FormationS1GVRealAdapterCallReceiptSchemaTests(unittest.TestCase):
    def test_schema_contains_every_s1gu_required_field(self) -> None:
        audit = audit_e1_formation_s1gv_real_adapter_call_receipt_schema()
        self.assertFalse(audit.missing_required_fields)
        self.assertTrue(
            set(audit.required_fields).issubset(audit.schema_fields)
        )
        self.assertIn("receipt_id", audit.schema_fields)

    def test_schema_is_frozen_slotted_and_digest_bound(self) -> None:
        audit = audit_e1_formation_s1gv_real_adapter_call_receipt_schema()
        self.assertTrue(audit.schema_frozen)
        self.assertTrue(audit.schema_slotted)
        self.assertTrue(audit.digest_integrity_enforced)

    def test_one_call_step_token_field_and_attestations_are_required(self) -> None:
        audit = audit_e1_formation_s1gv_real_adapter_call_receipt_schema()
        self.assertTrue(audit.one_call_one_step_enforced)
        self.assertTrue(audit.token_consumption_marker_required)
        self.assertTrue(audit.new_field_object_marker_required)
        self.assertTrue(audit.source_state_attestation_preserved)
        self.assertTrue(audit.fixed_adapter_attestation_preserved)

    def test_schema_integrity_is_not_misreported_as_authenticity(self) -> None:
        audit = audit_e1_formation_s1gv_real_adapter_call_receipt_schema()
        self.assertFalse(audit.structural_integrity_is_execution_authenticity)
        self.assertTrue(audit.external_authenticity_path_required)
        self.assertFalse(audit.receipt_factory_implemented)
        self.assertFalse(audit.receipt_instance_created)

    def test_adapter_kernel_execution_and_claims_remain_closed(self) -> None:
        audit = audit_e1_formation_s1gv_real_adapter_call_receipt_schema()
        self.assertFalse(audit.adapter_or_kernel_access_permitted)
        self.assertFalse(audit.execution_permitted)
        self.assertFalse(audit.persistence_permitted)
        self.assertFalse(audit.claims_permitted)
        self.assertEqual(
            "REAL_ADAPTER_CALL_RECEIPT_SCHEMA_READY_AUTHENTICITY_PATH_ABSENT",
            audit.decision,
        )

    def test_receipt_schema_enforces_exact_invariants_in_source(self) -> None:
        source = inspect.getsource(
            E1FormationS1GVRealAdapterCallReceipt.__post_init__
        )
        for required in (
            "self.previous_field_digest == self.next_field_digest",
            "self.source_state_digest_before",
            "self.fixed_adapter_digest_before",
            "self.token_consumed_before_adapter is not True",
            "self.next_field_object_replaced is not True",
            "self.adapter_calls != 1",
            "self.field_steps_executed != 1",
            "self.receipt_digest != _digest(payload)",
        ):
            self.assertIn(required, source)

    def test_audit_calls_no_adapter_kernel_factory_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1gv_real_adapter_call_receipt_schema
        )
        for forbidden in (
            "map_proposal_batch_to_transient_docks(",
            "project_transient_docks_to_neuron_inputs(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "E1FormationS1GVRealAdapterCallReceipt(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
