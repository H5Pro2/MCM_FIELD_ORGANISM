from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "S1ZG_LPRH1F_STATISCHER_PRIVATER_ANWENDUNGSPREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json"
AUDIT = ROOT / "docs" / "S1ZH_LPRH1F_STATISCHER_BINDUNGSKORREKTUR_ABNAHME_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
EXPECTED_AUDIT_DIGEST = "c7e45bf7e6195b74e83bcbc363de8a70834c50736b2e2ad43e026f607f2cd868"
BOUND_PATHS = {
    "s1zg_contract": "docs/S1ZG_LPRH1F_STATISCHER_PRIVATER_ANWENDUNGSPREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json",
    "s1zg_document": "docs/S1ZG_LPRH1F_STATISCHER_PRIVATER_ANWENDUNGSPREFLIGHT_BINDUNGSKORREKTURVERTRAG.md",
    "s1zg_tests": "tests/test_lprh1f_s1zg_static_private_application_preflight_binding_correction_contract.py",
    "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
    "private_consumer_module": "mcm_field_organism/_lprh1f_s1za_private_context_consumer.py",
    "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
    "package_root": "mcm_field_organism/__init__.py",
    "current_api": "mcm_field_organism/current_api.py",
    "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
}


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class LPRH1FS1ZHStaticBindingAcceptancePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_audit_digest_parent_and_bound_sources(self) -> None:
        self.assertEqual(EXPECTED_AUDIT_DIGEST, canonical_digest(self.audit))
        self.assertEqual(
            canonical_digest(self.contract),
            self.audit["parent_s1zg_canonical_correction_contract_digest"],
        )
        self.assertEqual(set(BOUND_PATHS), set(self.audit["bound_file_digests"]))
        for role, relative in BOUND_PATHS.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(self.audit["bound_file_digests"][role], actual)

    def test_three_blockers_are_finite_and_implementation_blocking(self) -> None:
        blockers = self.audit["implementation_preflight_blockers"]
        self.assertEqual(3, len(blockers))
        self.assertEqual(3, len({item["blocker_id"] for item in blockers}))
        self.assertTrue(all(
            item["severity"] == "IMPLEMENTATION_BLOCKING" for item in blockers
        ))
        self.assertEqual(
            {
                "H1_DERIVATION_RECEIPT_OBJECT_AND_DERIVED_SET_LINK_CONFLICT",
                "H2_DERIVATION_HELPER_ERROR_DISPATCH_AND_INPUT_IMMUTABILITY_INCOMPLETE",
                "H3_EIGHT_ARM_HANDOFF_PROVENANCE_AND_COMPLETE_NEXT_LAYER_PAYLOADS_REMAIN_SYMBOLIC",
            },
            {item["blocker_id"] for item in blockers},
        )

    def test_receipt_object_link_is_absent_from_s1zg(self) -> None:
        binding = self.contract["derived_drive_set_complete_binding"]
        self.assertNotIn("derivation_receipt_schema", self.contract)
        self.assertNotIn("derivation_receipt", binding)
        self.assertNotIn("derived_drive_set_schema", self.contract)
        self.assertTrue(self.audit["absence_evidence"]["derived_set_nested_receipt_field_absent"])

    def test_helper_dispatch_and_mapping_immutability_are_absent(self) -> None:
        errors = self.contract["finite_error_precedence"]
        self.assertTrue(all("APPLICATION" in item for item in errors))
        binding = self.contract["derived_drive_set_complete_binding"]
        self.assertNotIn("contact_mapping_before_after_digest_rule", binding)
        self.assertNotIn("transient_mapping_before_after_digest_rule", binding)
        self.assertTrue(self.audit["absence_evidence"]["helper_specific_error_precedence_absent"])

    def test_fixture_provenance_and_complete_next_payloads_are_absent(self) -> None:
        fixture = self.contract["finite_eight_arm_fixture"]
        self.assertIsInstance(fixture["required_source_provenance"]["candidate"], str)
        self.assertNotIn("candidate_handoff_source_payload", fixture)
        self.assertNotIn("no_context_handoff_source_payload", fixture)
        self.assertNotIn("expected_next_layer_canonical_payload", fixture["arms"][0])
        self.assertTrue(self.audit["absence_evidence"]["per_arm_complete_next_layer_canonical_payload_absent"])

    def test_valid_direction_is_preserved_without_core_change(self) -> None:
        finding = self.audit["non_circularity_finding"]
        self.assertTrue(finding["drive_derivation_still_precedes_prepare"])
        self.assertTrue(finding["proposal_materialization_still_precedes_single_layer_application"])
        self.assertFalse(finding["core_or_public_change_required"])
        self.assertTrue(all(self.audit["preserved_findings"].values()))

    def test_fail_decision_zero_execution_and_next_static_contract(self) -> None:
        self.assertEqual(32, self.audit["passed_audit_role_count"])
        self.assertEqual(3, self.audit["failed_audit_role_count"])
        self.assertEqual(
            "FAIL_LPRH1F_APPLICATION_PREFLIGHT_THREE_STATIC_BINDINGS_REMAIN",
            self.audit["decision"],
        )
        gate = self.audit["gate_effect"]
        next_gate = "requires_s1zi_static_binding_completion_contract"
        self.assertTrue(gate[next_gate])
        self.assertTrue(all(
            value is False for key, value in gate.items() if key != next_gate
        ))
        self.assertTrue(all(value == 0 for value in self.audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
