from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
S1ZG = ROOT / "docs" / "S1ZG_LPRH1F_STATISCHER_PRIVATER_ANWENDUNGSPREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json"
S1ZI = ROOT / "docs" / "S1ZI_LPRH1F_STATISCHER_RECEIPT_HELPER_UND_FIXTURE_PAYLOAD_KORREKTURVERTRAG_V1.json"
AUDIT = ROOT / "docs" / "S1ZJ_LPRH1F_STATISCHER_RECEIPT_HELPER_FIXTURE_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
EXPECTED_AUDIT_DIGEST = "1b1482be6350cce029b70202ed4597141afb247e30f027e1f73925a68203c84e"


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class LPRH1FS1ZJStaticFinalImplementationPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.s1zg = json.loads(S1ZG.read_text(encoding="utf-8"))
        cls.s1zi = json.loads(S1ZI.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_audit_digest_parent_and_immediate_files(self) -> None:
        self.assertEqual(EXPECTED_AUDIT_DIGEST, canonical_digest(self.audit))
        self.assertEqual(
            canonical_digest(self.s1zi),
            self.audit["parent_s1zi_canonical_correction_contract_digest"],
        )
        for role, path in (
            ("s1zi_contract", S1ZI),
            ("s1zi_document", ROOT / "docs/S1ZI_LPRH1F_STATISCHER_RECEIPT_HELPER_UND_FIXTURE_PAYLOAD_KORREKTURVERTRAG.md"),
            ("s1zi_tests", ROOT / "tests/test_lprh1f_s1zi_static_receipt_helper_and_fixture_payload_correction_contract.py"),
        ):
            self.assertEqual(
                self.audit["bound_file_digests"][role],
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )

    def test_s1zi_three_corrections_are_accepted(self) -> None:
        finding = self.audit["materializability_finding"]
        self.assertTrue(finding["derivation_receipt_materializable"])
        self.assertTrue(finding["helper_error_dispatch_materializable"])
        self.assertTrue(finding["helper_input_immutability_checks_materializable"])
        self.assertTrue(finding["four_handoff_sources_materializable"])
        self.assertTrue(finding["four_non_handoff_sources_materializable"])
        self.assertTrue(finding["eight_complete_next_layer_payloads_materializable"])

    def test_common_source_layer_is_not_a_complete_canonical_payload(self) -> None:
        common = self.s1zg["finite_eight_arm_fixture"]["common_layer"]
        self.assertNotIn("neurons", common)
        self.assertNotIn("position", common)
        self.assertNotIn("perception", common)
        self.assertNotIn("source.layer", self.s1zi["finite_fixture_source_registry"])
        self.assertTrue(self.audit["absence_evidence"]["s1zi_source_registry_has_no_source_layer_entry"])

    def test_one_blocker_requires_only_source_prestate_completion(self) -> None:
        blockers = self.audit["implementation_preflight_blockers"]
        self.assertEqual(1, len(blockers))
        self.assertEqual(
            "J1_COMMON_SOURCE_LAYER_CANONICAL_PRESTATE_PAYLOAD_INCOMPLETE",
            blockers[0]["blocker_id"],
        )
        self.assertEqual("IMPLEMENTATION_BLOCKING", blockers[0]["severity"])
        direction = self.audit["bounded_correction_direction"]
        self.assertFalse(direction["new_mechanic_allowed"])
        self.assertFalse(direction["core_or_public_change_allowed"])
        self.assertEqual(3, len(direction["required_digest_roles"]))

    def test_preserved_findings_and_public_boundaries_remain_true(self) -> None:
        preserved = self.audit["preserved_findings"]
        self.assertFalse(preserved["core_or_public_change_required"])
        self.assertTrue(all(
            value is True
            for key, value in preserved.items()
            if key != "core_or_public_change_required"
        ))
        finding = self.audit["materializability_finding"]
        self.assertFalse(finding["common_source_layer_object_materializable_without_invention"])
        self.assertFalse(finding["source_layer_digest_materializable_without_invention"])
        self.assertFalse(finding["field_prestate_digest_materializable_without_invention"])
        self.assertFalse(finding["expected_derived_drive_digest_materializable_without_invention"])

    def test_fail_decision_keeps_implementation_and_execution_blocked(self) -> None:
        self.assertEqual(43, self.audit["passed_audit_role_count"])
        self.assertEqual(1, self.audit["failed_audit_role_count"])
        self.assertEqual(
            "FAIL_LPRH1F_FINAL_IMPLEMENTATION_PREFLIGHT_COMMON_SOURCE_LAYER_PRESTATE_INCOMPLETE",
            self.audit["decision"],
        )
        gate = self.audit["gate_effect"]
        next_gate = "requires_s1zk_static_source_prestate_completion_contract"
        self.assertTrue(gate[next_gate])
        self.assertTrue(all(
            value is False for key, value in gate.items() if key != next_gate
        ))
        self.assertTrue(all(value == 0 for value in self.audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
