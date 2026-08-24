from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "S1ZF_LPRH1F_STATISCHER_DRIVE_ABLEITUNGS_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
CONTRACT = ROOT / "docs" / "S1ZG_LPRH1F_STATISCHER_PRIVATER_ANWENDUNGSPREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json"
EXPECTED_CONTRACT_DIGEST = "ebef4463089de486fd27630c801c31454b0a86b6ed348f0ee29e40e7d0775a20"
BOUND_PATHS = {
    "s1zf_audit": "docs/S1ZF_LPRH1F_STATISCHER_DRIVE_ABLEITUNGS_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json",
    "s1zf_document": "docs/S1ZF_LPRH1F_STATISCHER_DRIVE_ABLEITUNGS_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT.md",
    "s1zf_tests": "tests/test_lprh1f_s1zf_static_drive_derivation_closure_and_implementation_preflight.py",
    "s1ze_contract": "docs/S1ZE_LPRH1F_STATISCHER_PRIVATER_DRIVE_ABLEITUNGS_UND_DOCK_FIXTURE_KORREKTURVERTRAG_V1.json",
    "s1zc_contract": "docs/S1ZC_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_UND_BASELINEVERTRAG_V1.json",
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


class LPRH1FS1ZGStaticPrivateApplicationBindingCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_contract_digest_and_parent_are_bound(self) -> None:
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, canonical_digest(self.contract))
        self.assertEqual(
            canonical_digest(self.audit),
            self.contract["parent_s1zf_canonical_preflight_audit_digest"],
        )
        self.assertEqual(set(BOUND_PATHS), set(self.contract["bound_file_digests"]))
        for role, relative in BOUND_PATHS.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(self.contract["bound_file_digests"][role], actual)

    def test_module_and_complete_signatures_close_p1(self) -> None:
        module = self.contract["future_private_module"]
        self.assertFalse(module["public_export_allowed"])
        self.assertEqual(2, len(self.contract["exact_private_function_signatures"]))
        apply_signature = self.contract["exact_private_function_signatures"][1]
        self.assertEqual("apply_lprh1f_proposal_once", apply_signature["function_name"])
        self.assertIn(
            "derived_drive_set_LPRH1FDerivedDriveSet",
            apply_signature["input_roles_in_order"],
        )

    def test_derived_set_receipt_and_application_types_close_p2_and_p3(self) -> None:
        binding = self.contract["derived_drive_set_complete_binding"]
        self.assertEqual(
            "EXACT_ASCENDING_SOURCE_LAYER_NEURON_IDS",
            binding["ordered_drive_ids_rule"],
        )
        self.assertIn("derivation_receipt_digest", binding["derived_set_payload"])
        self.assertEqual(13, len(self.contract["application_receipt_schema"]))
        self.assertEqual(4, len(self.contract["applied_result_schema"]))
        self.assertIn(
            "ANY_FAILURE_RETURNS_NO_RESULT_NO_RECEIPT_NO_LEDGER_CHANGE",
            self.contract["atomic_application_invariants"],
        )

    def test_error_precedence_and_disjoint_counters_close_p4(self) -> None:
        errors = self.contract["finite_error_precedence"]
        self.assertEqual(11, len(errors))
        self.assertEqual("01_", errors[0][:3])
        self.assertEqual("11_", errors[-1][:3])
        owners = self.contract["counter_ownership"]
        self.assertEqual(
            ["perception_derivation_call_count"],
            owners["derive_lprh1f_drives_for_layer_step"],
        )
        self.assertEqual(0, owners["retry_count"])

    def test_complete_eight_arm_fixture_closes_p5(self) -> None:
        fixture = self.contract["finite_eight_arm_fixture"]
        arms = fixture["arms"]
        self.assertEqual(8, len(arms))
        self.assertEqual(8, len({arm["arm_id"] for arm in arms}))
        self.assertEqual(8, len({arm["execution_id"] for arm in arms}))
        self.assertEqual(["neuron.0"], fixture["common_layer"]["receptor_dock_ids"])
        self.assertEqual(1, fixture["per_arm_budgets"]["layer_advance_calls"])
        self.assertEqual(0, fixture["per_arm_budgets"]["retries"])
        self.assertEqual(4, len(fixture["expected_pair_relations"]))

    def test_all_five_blockers_close_but_implementation_stays_blocked(self) -> None:
        blockers = {
            item["blocker_id"] for item in self.audit["implementation_preflight_blockers"]
        }
        self.assertEqual(blockers, set(self.contract["blocker_closure"]))
        self.assertTrue(all(
            value.startswith("CLOSED_BY_")
            for value in self.contract["blocker_closure"].values()
        ))
        gate = self.contract["implementation_gate"]
        next_gate = "requires_s1zh_static_correction_acceptance_and_implementation_preflight"
        self.assertTrue(gate[next_gate])
        self.assertTrue(all(
            value is False for key, value in gate.items() if key != next_gate
        ))

    def test_decision_claim_boundary_and_zero_execution(self) -> None:
        self.assertEqual(57, self.contract["passed_role_count"])
        self.assertEqual(0, self.contract["failed_role_count"])
        self.assertEqual(
            "PASS_LPRH1F_FIVE_PRIVATE_APPLICATION_PREFLIGHT_BINDINGS_CLOSED_NO_IMPLEMENTATION",
            self.contract["decision"],
        )
        self.assertIn("GENERALLY_REDUCIBLE", self.contract["claim_boundary"])
        self.assertTrue(all(
            value == 0 for value in self.contract["execution_counters"].values()
        ))


if __name__ == "__main__":
    unittest.main()
