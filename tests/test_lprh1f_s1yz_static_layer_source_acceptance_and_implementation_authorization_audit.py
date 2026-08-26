from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1YZ_LPRH1F_STATISCHER_LAYERQUELLBINDUNGS_ABNAHME_UND_IMPLEMENTIERUNGSFREIGABEAUDIT_V1.json"
S1YY_PATH = ROOT / "docs/S1YY_LPRH1F_STATISCHER_LAYERVERTRAG_UND_QUELLBINDUNGSKORREKTUR_V1.json"
EXPECTED_AUDIT_DIGEST = "ef306e5d70851b16eaa3018b2bad042b92a446f834b3a831900862640017ebb7"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1YZStaticLayerSourceAcceptanceAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        parent = load(S1YY_PATH)
        encoded = json.dumps(parent, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(audit["parent_s1yy_canonical_contract_digest"], hashlib.sha256(encoded).hexdigest())
        paths = {
            "s1yy_contract": "docs/S1YY_LPRH1F_STATISCHER_LAYERVERTRAG_UND_QUELLBINDUNGSKORREKTUR_V1.json",
            "s1yy_document": "docs/S1YY_LPRH1F_STATISCHER_LAYERVERTRAG_UND_QUELLBINDUNGSKORREKTUR.md",
            "s1yy_tests": "tests/test_lprh1f_s1yy_static_layer_source_binding_correction_contract.py",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "mcm_neuron": "mcm_field_organism/mcm_neuron.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(audit["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_all_eight_acceptance_findings_pass(self) -> None:
        findings = load(AUDIT_PATH)["acceptance_findings"]
        self.assertEqual(8, len(findings))
        self.assertTrue(all(findings.values()))

    def test_mutual_binding_chain_is_complete_and_ordered(self) -> None:
        chain = load(AUDIT_PATH)["mutual_binding_chain"]
        self.assertEqual(6, len(chain))
        self.assertEqual("VALIDATED_SOURCE_LAYER_OBJECT", chain[0])
        self.assertEqual("PREPARED_DRIVE_SET_AND_PREPARATION_RECEIPT", chain[-1])

    def test_all_parent_failures_are_accepted_as_empty_and_atomic(self) -> None:
        audit = load(AUDIT_PATH)["fail_closed_acceptance"]
        parent = load(S1YY_PATH)
        self.assertEqual(len(parent["fail_closed_matrix"]), audit["audited_failure_case_count"])
        self.assertEqual("NONE", audit["every_failure_output"])
        self.assertTrue(audit["every_failure_has_finite_error_code"])
        for role in ("partial_prepared_output_count", "preparation_receipt_count_on_failure", "retry_count", "field_step_count", "source_mutation_count"):
            self.assertEqual(0, audit[role])

    def test_layer_identity_cannot_be_replaced(self) -> None:
        findings = load(AUDIT_PATH)["non_replaceability_findings"]
        self.assertEqual(5, len(findings))
        self.assertTrue(all(value is False for value in findings.values()))

    def test_public_boundaries_are_unchanged(self) -> None:
        regression = load(AUDIT_PATH)["public_boundary_regression"]
        unchanged = [value for key, value in regression.items() if key.endswith("_unchanged_from_s1yy_binding")]
        changes = [value for key, value in regression.items() if key.endswith("_change")]
        self.assertEqual(6, len(unchanged))
        self.assertTrue(all(unchanged))
        self.assertEqual(3, len(changes))
        self.assertTrue(all(value is False for value in changes))

    def test_authorized_scope_is_private_exact_and_synthetic(self) -> None:
        scope = load(AUDIT_PATH)["authorized_s1za_scope"]
        self.assertEqual("mcm_field_organism._lprh1f_s1za_private_context_consumer", scope["private_module_name"])
        self.assertEqual(2, len(scope["permitted_functions"]))
        self.assertEqual(6, scope["permitted_private_type_count"])
        self.assertEqual(8, len(scope["permitted_synthetic_test_families"]))
        self.assertTrue(scope["prepare_signature_must_equal_s1yy"])
        self.assertTrue(scope["synthetic_execution_only"])
        self.assertFalse(scope["new_equation_parameter_source_branch_or_error_code_allowed"])

    def test_public_and_field_paths_remain_prohibited(self) -> None:
        prohibitions = load(AUDIT_PATH)["continuing_prohibitions"]
        self.assertEqual(10, len(prohibitions))
        self.assertTrue(all(value is False for value in prohibitions.values()))

    def test_decision_reauthorizes_only_private_implementation(self) -> None:
        audit = load(AUDIT_PATH)
        gate = audit["implementation_gate"]
        self.assertTrue(gate["s1yy_contract_accepted"])
        self.assertTrue(gate["private_s1za_consumer_code_authorized"])
        self.assertTrue(gate["private_s1za_synthetic_contract_tests_authorized"])
        self.assertTrue(gate["separate_postimplementation_static_audit_required"])
        self.assertFalse(gate["field_execution_authorized"])
        self.assertEqual(39, audit["passed_audit_role_count"])
        self.assertEqual(0, audit["failed_audit_role_count"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
