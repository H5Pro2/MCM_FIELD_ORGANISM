from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1YJ_LPRH1_STATISCHER_KORREKTURABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHTAUDIT_V1.json"
EXPECTED_AUDIT_DIGEST = "bffc570218ba0189f3cd0982871a6878cbc76df17dc6688c5b0c9498cd3445a8"


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


class LPRH1S1YJStaticImplementationPreflightAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load_audit()
        self.assertEqual("8de3ed1392f1038bc6dcfd63287bf6f8e452aa1771fab1836d4230e6da0c7bd9", audit["parent_s1yi_canonical_contract_digest"])
        paths = {
            "s1yi_contract": "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json",
            "s1yi_document": "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG.md",
            "s1yi_tests": "tests/test_lprh1_s1yi_static_correction_contract.py",
            "receptor_time_model": "mcm_field_organism/receptor_time_model.py",
            "field_step_time": "mcm_field_organism/field_step_time.py",
            "receptor_contract": "mcm_field_organism/receptor_contract.py",
            "transient_neuron_input": "mcm_field_organism/transient_neuron_input.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(audit["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_twenty_confirmed_bindings_are_preserved(self) -> None:
        audit = load_audit()
        self.assertEqual(20, audit["passed_role_count"])
        self.assertEqual(20, len(audit["confirmed_bindings"]))

    def test_exactly_six_implementation_blockers_are_bound(self) -> None:
        audit = load_audit()
        self.assertEqual(6, audit["failed_role_count"])
        self.assertEqual(6, len(audit["implementation_blockers"]))
        self.assertEqual({f"P{index}_" for index in range(1, 7)}, {item["blocker_id"][:3] for item in audit["implementation_blockers"]})

    def test_four_output_digest_payloads_are_demonstrably_missing(self) -> None:
        contract = json.loads((ROOT / "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json").read_text(encoding="utf-8"))
        digest_rule = contract["canonical_digest_rule"]
        for role in ("context", "no_context_receipt", "envelope", "handoff_receipt"):
            self.assertNotIn(f"{role}_payload_keys", digest_rule)
        self.assertEqual("P1_OUTPUT_DIGEST_PAYLOADS_MISSING", load_audit()["implementation_blockers"][0]["blocker_id"])

    def test_receipt_id_payload_lacks_receipt_kind(self) -> None:
        contract = json.loads((ROOT / "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json").read_text(encoding="utf-8"))
        keys = contract["handoff_identity"]["receipt_id_payload_keys"]
        self.assertNotIn("receipt_kind", keys)
        self.assertIn("P2_RECEIPT_ID_NAMESPACE_COLLISION", {item["blocker_id"] for item in load_audit()["implementation_blockers"]})

    def test_source_digest_tuple_order_is_absent(self) -> None:
        contract = json.loads((ROOT / "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json").read_text(encoding="utf-8"))
        self.assertIn("source_object_digests_tuple_str", contract["exact_type_schemas"]["LPRH1HandoffReceipt"])
        self.assertNotIn("source_object_digest_order", contract)

    def test_type_validators_error_matrix_and_commit_order_are_absent(self) -> None:
        contract = json.loads((ROOT / "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json").read_text(encoding="utf-8"))
        self.assertNotIn("type_invariants", contract)
        self.assertNotIn("error_dispatch", contract)
        self.assertNotIn("atomic_commit_order", contract)

    def test_preflight_permissions_are_false(self) -> None:
        audit = load_audit()
        self.assertFalse(audit["implementation_permission"])
        self.assertFalse(audit["field_permission"])
        self.assertEqual("BLOCKED_SIX_IMPLEMENTATION_BINDINGS_REQUIRED", audit["preflight_decision"])

    def test_public_surfaces_remain_without_lprh1(self) -> None:
        for relative in ("mcm_field_organism/__init__.py", "mcm_field_organism/current_api.py", "mcm_field_organism/root_lazy_exports.py"):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yj", source)
            self.assertNotIn("lprh", source)

    def test_decision_is_blocked_narrow_and_nonexecuting(self) -> None:
        audit = load_audit()
        self.assertEqual("BLOCKED_LPRH1_IMPLEMENTATION_PREFLIGHT_CORRECTION_REQUIRED_NO_IMPLEMENTATION_OR_EXECUTION", audit["decision"])
        self.assertIn("NO_UNAMBIGUOUS_IMPLEMENTATION", audit["claim_boundary"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
