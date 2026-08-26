from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1YW_LPRH1F_STATISCHER_FINALER_ABSCHLUSS_UND_IMPLEMENTIERUNGSFREIGABEAUDIT_V1.json"
S1YV_PATH = ROOT / "docs/S1YV_LPRH1F_STATISCHER_FINALER_PREFLIGHT_KORREKTURVERTRAG_V1.json"
EXPECTED_AUDIT_DIGEST = "bdde5d93269c0836064b5c9da6666bfcb6af61f068d4e42f66dc8e321cedc2ea"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1YWStaticFinalClosureAndAuthorizationAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_evidence_files_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        parent = load(S1YV_PATH)
        encoded = json.dumps(parent, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(audit["parent_s1yv_canonical_contract_digest"], hashlib.sha256(encoded).hexdigest())
        paths = {
            "s1yv_contract": "docs/S1YV_LPRH1F_STATISCHER_FINALER_PREFLIGHT_KORREKTURVERTRAG_V1.json",
            "s1yv_document": "docs/S1YV_LPRH1F_STATISCHER_FINALER_PREFLIGHT_KORREKTURVERTRAG.md",
            "s1yv_tests": "tests/test_lprh1f_s1yv_static_final_preflight_correction_contract.py",
        }
        for role, relative in paths.items():
            self.assertEqual(audit["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_all_parent_blockers_are_closed_once(self) -> None:
        audit = load(AUDIT_PATH)
        parent = load(S1YV_PATH)
        expected = set(parent["final_preflight_blocker_closure"])
        closures = audit["audited_closures"]
        self.assertEqual(expected, {item["blocker_id"] for item in closures})
        self.assertEqual(5, len(closures))
        self.assertTrue(all(item["status"] == "CLOSED" and item["evidence"] for item in closures))

    def test_non_circularity_is_complete(self) -> None:
        findings = load(AUDIT_PATH)["non_circularity_findings"]
        self.assertEqual(6, len(findings))
        self.assertTrue(all(findings.values()))

    def test_materializability_has_no_open_decision(self) -> None:
        findings = load(AUDIT_PATH)["materializability_findings"]
        self.assertEqual(2, findings["function_count"])
        self.assertEqual(6, findings["private_type_count"])
        self.assertEqual(8, findings["source_arm_count"])
        self.assertEqual(8, findings["error_code_count"])
        self.assertEqual(8, findings["synthetic_test_family_count"])
        self.assertFalse(findings["implementation_decision_left_to_code"])

    def test_authorized_scope_exactly_matches_parent(self) -> None:
        audit = load(AUDIT_PATH)["authorized_s1yx_scope"]
        parent = load(S1YV_PATH)["implementation_scope_after_separate_audit"]
        self.assertEqual(parent["private_module_name"], audit["private_module_name"])
        self.assertEqual(parent["permitted_functions"], audit["functions"])
        self.assertEqual(parent["permitted_type_count"], len(audit["private_types"]))
        self.assertEqual(parent["permitted_synthetic_test_families"], audit["synthetic_test_families"])
        self.assertFalse(audit["new_equation_parameter_branch_or_error_code_allowed"])

    def test_all_public_and_field_surfaces_remain_blocked(self) -> None:
        prohibitions = load(AUDIT_PATH)["continuing_prohibitions"]
        self.assertEqual(10, len(prohibitions))
        self.assertTrue(all(value is False for value in prohibitions.values()))

    def test_authorization_is_private_conditional_and_requires_later_audit(self) -> None:
        gate = load(AUDIT_PATH)["implementation_gate"]
        self.assertTrue(gate["s1yx_private_consumer_implementation_authorized"])
        self.assertTrue(gate["s1yx_synthetic_contract_tests_authorized"])
        self.assertTrue(gate["authorization_requires_exact_parent_digest"])
        self.assertTrue(gate["authorization_void_on_bound_source_drift"])
        self.assertTrue(gate["authorization_void_on_scope_expansion"])
        self.assertTrue(gate["separate_postimplementation_static_audit_required"])

    def test_decision_is_static_narrow_and_nonexecuting(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual(31, audit["passed_audit_role_count"])
        self.assertEqual(0, audit["failed_audit_role_count"])
        self.assertEqual("PASS_LPRH1F_FINAL_CLOSURE_PRIVATE_S1YX_IMPLEMENTATION_AUTHORIZED", audit["decision"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))
        self.assertIn("GENERICALLY_REDUCIBLE_ENGINEERING_COUPLING", audit["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
