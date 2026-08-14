from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec114_external_origin_attestation_contract import (
    S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA,
)
from mcm_field_organism.e1_common_probe_ec115_external_origin_boundary_inventory import (
    E1CommonProbeEC115ExternalOriginBoundaryInventoryError,
    audit_e1_common_probe_ec115_external_origin_boundary_inventory,
)


class E1CommonProbeEC115ExternalOriginBoundaryInventoryTests(unittest.TestCase):
    def test_all_relevant_project_boundary_kinds_are_classified(self) -> None:
        inventory = audit_e1_common_probe_ec115_external_origin_boundary_inventory()
        self.assertEqual(6, len(inventory.candidates))
        self.assertEqual(
            {
                "configuration-and-prompt-files",
                "caller-supplied-boolean",
                "synthetic-structure-validation",
                "process-local-time-and-file-binding",
                "organism-field-continuity",
                "controlled-testworld-payload-reduction",
            },
            {item.boundary_kind for item in inventory.candidates},
        )

    def test_no_candidate_provides_authenticated_external_owner_event(self) -> None:
        inventory = audit_e1_common_probe_ec115_external_origin_boundary_inventory()
        self.assertEqual((), inventory.eligible_candidate_ids)
        self.assertFalse(inventory.externally_authenticated_event_boundary_present)
        self.assertTrue(
            all(not item.externally_authenticated_owner_event for item in inventory.candidates)
        )

    def test_synthetic_bridge_has_partial_fields_but_is_not_origin(self) -> None:
        inventory = audit_e1_common_probe_ec115_external_origin_boundary_inventory()
        bridge = next(
            item
            for item in inventory.candidates
            if item.candidate_id == "ec112-ec113-synthetic-message-bridge"
        )
        self.assertEqual(5, len(bridge.covered_evidence_fields))
        self.assertIn("exact_owner_message_digest", bridge.covered_evidence_fields)
        self.assertFalse(bridge.eligible_for_ec114_attestation)
        self.assertLess(
            set(bridge.covered_evidence_fields),
            set(S1_EC114_REQUIRED_EXTERNAL_EVIDENCE_SCHEMA),
        )

    def test_attestation_token_and_execution_remain_closed(self) -> None:
        inventory = audit_e1_common_probe_ec115_external_origin_boundary_inventory()
        self.assertFalse(inventory.ec114_attestation_implementation_permitted)
        self.assertFalse(inventory.external_release_issued)
        self.assertFalse(inventory.owner_scope_token_creation_permitted)
        self.assertFalse(inventory.execution_permitted)
        self.assertFalse(inventory.real_result_ingress_permitted)

    def test_inventory_is_deterministic_and_tamper_evident(self) -> None:
        first = audit_e1_common_probe_ec115_external_origin_boundary_inventory()
        second = audit_e1_common_probe_ec115_external_origin_boundary_inventory()
        self.assertEqual(first.inventory_digest, second.inventory_digest)
        with self.assertRaises(E1CommonProbeEC115ExternalOriginBoundaryInventoryError):
            replace(first, ec114_attestation_implementation_permitted=True)

    def test_audit_does_not_invoke_candidates_or_io(self) -> None:
        source = inspect.getsource(
            audit_e1_common_probe_ec115_external_origin_boundary_inventory
        )
        for forbidden in (
            "bind_e1_common_probe_n2_r2_ec78_owner_authorization(",
            "prepare_e1_confirmation_same_session_preflight(",
            "classify_e1_common_probe_ec112_owner_message(",
            "validate_e1_common_probe_ec113_synthetic_bridge_candidate(",
            "create_e1_common_probe_ec110_owner_scope_token(",
            "run_shared_mcm_field_session(",
            "read_text(",
            "read_bytes(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
