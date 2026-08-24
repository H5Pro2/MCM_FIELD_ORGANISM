from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1ZF_LPRH1F_STATISCHER_DRIVE_ABLEITUNGS_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
S1ZE_PATH = ROOT / "docs/S1ZE_LPRH1F_STATISCHER_PRIVATER_DRIVE_ABLEITUNGS_UND_DOCK_FIXTURE_KORREKTURVERTRAG_V1.json"
EXPECTED_AUDIT_DIGEST = "5c240162e601117b36e4009bed9a0c783f47124bb7744005b4e97dd6514bd353"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1ZFStaticDriveDerivationImplementationPreflightTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        parent = load(S1ZE_PATH)
        encoded = json.dumps(parent, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(audit["parent_s1ze_canonical_correction_contract_digest"], hashlib.sha256(encoded).hexdigest())
        paths = {
            "s1ze_contract": "docs/S1ZE_LPRH1F_STATISCHER_PRIVATER_DRIVE_ABLEITUNGS_UND_DOCK_FIXTURE_KORREKTURVERTRAG_V1.json",
            "s1ze_document": "docs/S1ZE_LPRH1F_STATISCHER_PRIVATER_DRIVE_ABLEITUNGS_UND_DOCK_FIXTURE_KORREKTURVERTRAG.md",
            "s1ze_tests": "tests/test_lprh1f_s1ze_static_private_drive_derivation_and_dock_fixture_correction_contract.py",
            "s1zc_contract": "docs/S1ZC_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_UND_BASELINEVERTRAG_V1.json",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "private_consumer_module": "mcm_field_organism/_lprh1f_s1za_private_context_consumer.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(audit["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_nineteen_correction_roles_are_accepted(self) -> None:
        roles = load(AUDIT_PATH)["accepted_correction_roles"]
        self.assertEqual(19, len(roles))
        self.assertEqual(19, len(set(roles)))

    def test_causal_cycle_is_closed_before_implementation(self) -> None:
        finding = load(AUDIT_PATH)["non_circularity_finding"]
        self.assertEqual(5, len(finding))
        self.assertTrue(all(finding.values()))

    def test_five_preflight_blockers_are_unique_and_actionable(self) -> None:
        blockers = load(AUDIT_PATH)["implementation_preflight_blockers"]
        self.assertEqual(5, len(blockers))
        self.assertEqual(5, len({item["blocker_id"] for item in blockers}))
        self.assertTrue(all(item["severity"] == "IMPLEMENTATION_BLOCKING" for item in blockers))
        self.assertTrue(all(item["condition"] and item["required_correction"] for item in blockers))

    def test_corrected_full_signature_and_module_name_are_not_yet_bound(self) -> None:
        parent = load(S1ZE_PATH)
        self.assertNotIn("corrected_complete_function_signatures", parent)
        self.assertNotIn("future_private_module_name", parent)
        self.assertEqual("P1_CORRECTED_APPLICATION_SIGNATURE_AND_PRIVATE_MODULE_IDENTITY_UNBOUND", load(AUDIT_PATH)["implementation_preflight_blockers"][0]["blocker_id"])

    def test_result_receipt_error_and_counter_schemas_are_not_yet_bound(self) -> None:
        parent = load(S1ZE_PATH)
        for role in (
            "private_application_type_schemas",
            "private_application_canonical_payloads",
            "finite_error_dispatch",
            "counter_ownership",
        ):
            self.assertNotIn(role, parent)

    def test_fixture_is_anatomically_bound_but_not_end_to_end_materialized(self) -> None:
        parent = load(S1ZE_PATH)
        fixture = parent["dock_consistent_fixture"]
        self.assertEqual(fixture["receptor_dock_ids"], fixture["transient_input_keys"])
        for role in (
            "ppb1_history_objects",
            "handoff_result_digests",
            "execution_ids",
            "proposal_ledgers",
            "application_ledgers",
            "exact_expected_next_layer_payloads",
        ):
            self.assertNotIn(role, fixture)

    def test_public_boundaries_remain_unchanged_and_core_change_is_unneeded(self) -> None:
        finding = load(AUDIT_PATH)["public_boundary_finding"]
        self.assertEqual(6, len(finding))
        self.assertTrue(all(value is True for key, value in finding.items() if key.endswith("_unchanged")))
        self.assertFalse(finding["core_or_public_change_required_by_correction"])

    def test_decision_blocks_implementation_with_five_failures_and_zero_execution(self) -> None:
        audit = load(AUDIT_PATH)
        gate = audit["gate_effect"]
        self.assertTrue(all(value is False for key, value in gate.items() if key != "requires_s1zg_static_preflight_binding_correction_contract"))
        self.assertTrue(gate["requires_s1zg_static_preflight_binding_correction_contract"])
        self.assertEqual(34, audit["passed_audit_role_count"])
        self.assertEqual(5, audit["failed_audit_role_count"])
        self.assertEqual("FAIL_LPRH1F_DRIVE_DERIVATION_CORRECTION_CAUSALLY_CLOSED_BUT_FIVE_IMPLEMENTATION_BINDINGS_REMAIN", audit["decision"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
