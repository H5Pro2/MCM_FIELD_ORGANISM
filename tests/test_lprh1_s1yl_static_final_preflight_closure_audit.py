from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1YL_LPRH1_STATISCHER_FINALER_BINDUNGS_UND_IMPLEMENTIERUNGSPREFLIGHT_ABSCHLUSSAUDIT_V1.json"
S1YK_PATH = ROOT / "docs/S1YK_LPRH1_STATISCHER_FINALER_IMPLEMENTIERUNGSBINDUNGSKORREKTURVERTRAG_V1.json"
S1YI_PATH = ROOT / "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json"
EXPECTED_AUDIT_DIGEST = "e7dfd4d85d9428deba5d369cca652c5ccb099031f76ed733824710d2d34d98eb"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1S1YLStaticFinalPreflightClosureAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual("3b914f2b9d90470223225b070ae1b8673d9665791b697d125871bc30a84d04aa", audit["parent_s1yk_canonical_contract_digest"])
        paths = {
            "s1yk_contract": "docs/S1YK_LPRH1_STATISCHER_FINALER_IMPLEMENTIERUNGSBINDUNGSKORREKTURVERTRAG_V1.json",
            "s1yk_document": "docs/S1YK_LPRH1_STATISCHER_FINALER_IMPLEMENTIERUNGSBINDUNGSKORREKTURVERTRAG.md",
            "s1yk_tests": "tests/test_lprh1_s1yk_static_final_binding_contract.py",
            "s1yi_contract": "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json",
            "s1yg_contract": "docs/S1YG_LPRH1_STATISCHER_FUNKTIONS_PROVENIENZ_KAUSALITAETS_UND_FALSIFIKATIONSVERTRAG_V1.json",
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

    def test_all_ten_cross_contract_results_pass(self) -> None:
        results = load(AUDIT_PATH)["cross_contract_results"]
        self.assertEqual(10, len(results))
        self.assertTrue(all(value for key, value in results.items() if key != "new_materialization_blocker_found"))
        self.assertFalse(results["new_materialization_blocker_found"])

    def test_output_payloads_match_output_digest_roles(self) -> None:
        contract = load(S1YK_PATH)
        payloads = contract["canonical_output_payloads"]
        self.assertEqual(4, len([key for key in payloads if key.endswith("_payload_keys")]))
        self.assertNotIn("context_digest", payloads["context_payload_keys"])
        self.assertNotIn("receipt_digest", payloads["no_context_receipt_payload_keys"])
        self.assertNotIn("envelope_digest", payloads["envelope_payload_keys"])
        self.assertNotIn("receipt_digest", payloads["handoff_receipt_payload_keys"])

    def test_receipt_namespaces_and_source_digest_order_are_complete(self) -> None:
        contract = load(S1YK_PATH)
        self.assertTrue(contract["receipt_identity_namespaces"]["ids_must_differ_for_negative_result"])
        order = contract["source_object_digest_order"]
        self.assertEqual(8, len(order))
        self.assertEqual(8, len(set(order)))

    def test_six_type_families_match_s1yi_types(self) -> None:
        self.assertEqual(set(load(S1YI_PATH)["exact_type_schemas"]), set(load(S1YK_PATH)["type_invariants"]))

    def test_error_dispatch_matches_s1yi_codes_exactly(self) -> None:
        expected = set(load(S1YI_PATH)["finite_error_codes"])
        dispatch = load(S1YK_PATH)["error_dispatch_in_precedence_order"]
        self.assertEqual(expected, {item["code"] for item in dispatch})
        self.assertEqual(list(range(1, 9)), [item["stage"] for item in dispatch])

    def test_commit_and_failure_atomicity_are_complete(self) -> None:
        contract = load(S1YK_PATH)
        self.assertEqual(13, len(contract["atomic_commit_order"]))
        self.assertIn("ONLY_OBSERVABLE_COMMIT", contract["atomic_commit_order"][-1])
        self.assertEqual(0, contract["failure_atomicity"]["observable_intermediate_output_count"])
        self.assertFalse(contract["failure_atomicity"]["ledger_update_before_final_return"])

    def test_all_six_s1yj_blockers_are_closed(self) -> None:
        closure = load(S1YK_PATH)["blocker_closure"]
        self.assertEqual(6, len(closure))
        self.assertTrue(all(value.startswith("CLOSED_BY_") for value in closure.values()))

    def test_private_implementation_scope_is_exact_and_field_blocked(self) -> None:
        preflight = load(AUDIT_PATH)["implementation_preflight"]
        self.assertEqual("mcm_field_organism._lprh1_s1ym_private_local_handoff", preflight["private_module_name"])
        self.assertEqual("materialize_lprh1_local_handoff", preflight["pure_function_name"])
        self.assertEqual(6, len(preflight["permitted_new_types"]))
        self.assertEqual(8, len(preflight["permitted_test_scope"]))
        self.assertFalse(preflight["public_api_permission"])
        self.assertFalse(preflight["snapshot_permission"])
        self.assertFalse(preflight["production_permission"])
        self.assertFalse(preflight["field_consumption_permission"])
        self.assertFalse(preflight["field_step_permission"])

    def test_public_surfaces_remain_without_lprh1(self) -> None:
        for relative in ("mcm_field_organism/__init__.py", "mcm_field_organism/current_api.py", "mcm_field_organism/root_lazy_exports.py"):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yl", source)
            self.assertNotIn("lprh", source)

    def test_decision_is_complete_narrow_and_nonexecuting(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual(28, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual("PASS_LPRH1_FINAL_STATIC_PREFLIGHT_PRIVATE_SYNTHETIC_IMPLEMENTATION_SEPARATELY_AUTHORIZABLE", audit["decision"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
