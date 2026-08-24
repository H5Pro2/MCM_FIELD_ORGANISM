from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "S1ZK_LPRH1F_STATISCHER_QUELLLAYER_VORZUSTANDS_UND_DRIVE_PAYLOAD_VERTRAG_V1.json"
AUDIT = ROOT / "docs" / "S1ZL_LPRH1F_STATISCHER_QUELLZUSTANDS_ABSCHLUSS_UND_FINALER_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
EXPECTED_AUDIT_DIGEST = "4f050db68a552b9ce9e2870ebc27e4d62819976a5b985c79791140b5acf26b28"


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


class LPRH1FS1ZLStaticFinalImplementationPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_audit_digest_parent_and_immediate_sources(self) -> None:
        self.assertEqual(EXPECTED_AUDIT_DIGEST, canonical_digest(self.audit))
        self.assertEqual(
            canonical_digest(self.contract),
            self.audit["parent_s1zk_canonical_source_prestate_contract_digest"],
        )
        for role, path in (
            ("s1zk_contract", CONTRACT),
            ("s1zk_document", ROOT / "docs/S1ZK_LPRH1F_STATISCHER_QUELLLAYER_VORZUSTANDS_UND_DRIVE_PAYLOAD_VERTRAG.md"),
            ("s1zk_tests", ROOT / "tests/test_lprh1f_s1zk_static_source_layer_prestate_and_drive_payload_contract.py"),
        ):
            self.assertEqual(
                self.audit["bound_file_digests"][role],
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )

    def test_all_source_and_drive_digests_recompute(self) -> None:
        contract = self.contract
        self.assertEqual(contract["source_neuron_digest"], canonical_digest(contract["source_neuron_canonical_payload"]))
        self.assertEqual(contract["source_layer_digest"], canonical_digest(contract["source_layer_canonical_payload"]))
        self.assertEqual(contract["field_prestate_digest"], canonical_digest(contract["field_prestate_canonical_payload"]))
        self.assertEqual(contract["expected_single_derived_drive_digest"], canonical_digest(contract["expected_single_derived_drive_canonical_payload"]))
        self.assertEqual(contract["drive_input_digests"]["receptor_input_bundle_digest"], canonical_digest(contract["receptor_input_bundle_canonical_payload"]))

    def test_full_chain_has_no_remaining_blocker(self) -> None:
        closure = self.audit["full_chain_closure"]
        self.assertEqual(0, closure["implementation_preflight_blocker_count"])
        self.assertEqual([], self.audit["implementation_preflight_blockers"])
        for key, value in closure.items():
            if key not in {"non_circular_order", "implementation_preflight_blocker_count"}:
                self.assertTrue(value, key)

    def test_private_surface_is_exact_and_currently_absent(self) -> None:
        surface = self.audit["authorized_s1zm_private_surface"]
        self.assertEqual(5, len(surface["private_types"]))
        self.assertEqual(2, len(surface["private_functions"]))
        self.assertFalse((ROOT / surface["module_path"]).exists())
        self.assertFalse((ROOT / surface["test_path"]).exists())
        self.assertFalse(surface["public_export_allowed"])
        self.assertFalse(surface["additional_runtime_or_mechanic_allowed"])

    def test_synthetic_scope_and_per_arm_budget_are_finite(self) -> None:
        scope = self.audit["authorized_s1zm_synthetic_test_scope"]
        self.assertTrue(scope["execute_all_eight_bound_arms"])
        self.assertTrue(scope["verify_all_literal_digests_and_complete_next_layer_payloads"])
        self.assertFalse(scope["retry_allowed"])
        self.assertFalse(scope["registered_or_real_field_path_allowed"])
        budget = self.audit["per_arm_maximum_call_budget"]
        self.assertEqual(1, budget["drive_derivation_calls"])
        self.assertEqual(1, budget["layer_advance_calls"])
        self.assertEqual(0, budget["retries"])

    def test_authorization_is_private_while_public_boundaries_stay_closed(self) -> None:
        effect = self.audit["authorization_effect"]
        self.assertTrue(effect["s1zm_private_module_implementation_authorized"])
        self.assertTrue(effect["s1zm_private_synthetic_contract_tests_authorized"])
        self.assertTrue(effect["s1zm_bound_eight_arm_synthetic_execution_authorized"])
        self.assertFalse(effect["public_api_or_core_change_authorized"])
        self.assertFalse(effect["snapshot_or_production_integration_authorized"])
        self.assertFalse(effect["real_field_or_registered_matrix_execution_authorized"])
        self.assertFalse(effect["memory_field_effect_or_mcm_specific_claim_authorized"])
        self.assertTrue(all(value is False for value in self.audit["unchanged_boundary_requirements"].values()))

    def test_pass_decision_has_zero_preflight_execution(self) -> None:
        self.assertEqual(54, self.audit["passed_audit_role_count"])
        self.assertEqual(0, self.audit["failed_audit_role_count"])
        self.assertEqual(
            "PASS_LPRH1F_FINAL_IMPLEMENTATION_PREFLIGHT_PRIVATE_S1ZM_CODE_AND_SYNTHETIC_TESTS_AUTHORIZED",
            self.audit["decision"],
        )
        self.assertTrue(all(value == 0 for value in self.audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
