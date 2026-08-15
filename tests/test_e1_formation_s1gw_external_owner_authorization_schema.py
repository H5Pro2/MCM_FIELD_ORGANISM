from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_formation_s1gw_external_owner_authorization_schema import (
    E1FormationS1GWExternalOwnerAuthorization,
    S1_GW_NON_AUTHORIZATION_MESSAGES,
    audit_e1_formation_s1gw_external_owner_authorization_schema,
)


class E1FormationS1GWExternalOwnerAuthorizationSchemaTests(unittest.TestCase):
    def test_schema_binds_project_run_gate_target_and_owner_origin(self) -> None:
        audit = audit_e1_formation_s1gw_external_owner_authorization_schema()
        self.assertFalse(audit.missing_required_fields)
        for required in (
            "external_origin_receipt_digest",
            "owner_message_digest",
            "project_id",
            "run_id",
            "gate_digest",
            "binding_digest",
            "batch_index",
            "carrier_digest",
        ):
            self.assertIn(required, audit.schema_fields)
        self.assertTrue(audit.exact_target_binding_required)
        self.assertTrue(audit.external_origin_receipt_required)

    def test_scope_is_exactly_one_nonpersistent_attempt(self) -> None:
        audit = audit_e1_formation_s1gw_external_owner_authorization_schema()
        for required in (
            "maximum_adapter_calls",
            "maximum_field_steps",
            "single_use",
            "non_persistent",
            "retry_permitted",
            "reparametrization_permitted",
            "partial_return_permitted",
            "claims_permitted",
            "expires_after_success_or_failure",
        ):
            self.assertIn(required, audit.schema_fields)
        self.assertEqual(10, len(audit.required_owner_clauses))

    def test_continue_messages_are_explicitly_not_authorization(self) -> None:
        audit = audit_e1_formation_s1gw_external_owner_authorization_schema()
        self.assertIn("ok weiter", S1_GW_NON_AUTHORIZATION_MESSAGES)
        self.assertFalse(audit.current_continue_message_is_authorization)

    def test_integrity_is_not_confused_with_external_authenticity(self) -> None:
        audit = audit_e1_formation_s1gw_external_owner_authorization_schema()
        self.assertTrue(audit.schema_frozen)
        self.assertTrue(audit.schema_slotted)
        self.assertFalse(audit.structural_validity_is_external_authenticity)
        self.assertFalse(audit.authorization_factory_implemented)
        self.assertFalse(audit.authorization_instance_created)

    def test_target_token_execution_and_claims_remain_closed(self) -> None:
        audit = audit_e1_formation_s1gw_external_owner_authorization_schema()
        self.assertFalse(audit.target_selected)
        self.assertFalse(audit.token_creation_permitted)
        self.assertFalse(audit.execution_permitted)
        self.assertFalse(audit.persistence_permitted)
        self.assertFalse(audit.claims_permitted)
        self.assertEqual(
            "EXTERNAL_OWNER_AUTHORIZATION_SCHEMA_BOUND_"
            "TARGET_AND_ORIGIN_REQUIRED",
            audit.decision,
        )

    def test_schema_source_enforces_exact_scope(self) -> None:
        source = inspect.getsource(
            E1FormationS1GWExternalOwnerAuthorization.__post_init__
        )
        for required in (
            "self.project_id != S1_GW_PROJECT_ID",
            "not self.run_id.startswith(\"S1-G\")",
            "self.maximum_adapter_calls != 1",
            "self.maximum_field_steps != 1",
            "self.single_use is not True",
            "self.non_persistent is not True",
            "self.retry_permitted is not False",
            "self.expires_after_success_or_failure is not True",
        ):
            self.assertIn(required, source)

    def test_audit_calls_no_factory_token_adapter_kernel_or_writer(self) -> None:
        source = inspect.getsource(
            audit_e1_formation_s1gw_external_owner_authorization_schema
        )
        for forbidden in (
            "E1FormationS1GWExternalOwnerAuthorization(",
            "issue_e1_formation_s1gt_synthetic_single_use_token(",
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
