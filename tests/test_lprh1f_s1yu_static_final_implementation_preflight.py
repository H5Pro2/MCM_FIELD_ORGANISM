from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1YU_LPRH1F_STATISCHER_FINALER_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
S1YT_PATH = ROOT / "docs/S1YT_LPRH1F_STATISCHER_PREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json"
S1YS_PATH = ROOT / "docs/S1YS_LPRH1F_STATISCHER_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
EXPECTED_AUDIT_DIGEST = "912d13fa7892fd395be73e68a71cdf02eb04b9754c2d84d8207ebcf19e615f51"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1YUStaticFinalImplementationPreflightTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual("65c43093957a3e41714d383971ff514c0809723c41d8d3bb66cb0246e7bfff53", audit["parent_s1yt_canonical_contract_digest"])
        paths = {
            "s1yt_contract": "docs/S1YT_LPRH1F_STATISCHER_PREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json",
            "s1yt_document": "docs/S1YT_LPRH1F_STATISCHER_PREFLIGHT_BINDUNGSKORREKTURVERTRAG.md",
            "s1yt_tests": "tests/test_lprh1f_s1yt_static_preflight_binding_correction_contract.py",
            "s1ys_preflight": "docs/S1YS_LPRH1F_STATISCHER_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json",
            "private_handoff_module": "mcm_field_organism/_lprh1_s1yn_private_local_handoff.py",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "mcm_neuron": "mcm_field_organism/mcm_neuron.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(audit["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_all_six_s1ys_blockers_have_s1yt_closures(self) -> None:
        expected = {item["blocker_id"] for item in load(S1YS_PATH)["preflight_blockers"]}
        closure = load(S1YT_PATH)["preflight_blocker_closure"]
        self.assertEqual(expected, set(closure))
        self.assertEqual(6, len(closure))

    def test_field_prestate_digest_and_drive_order_are_not_derived(self) -> None:
        contract = load(S1YT_PATH)
        self.assertNotIn("field_prestate_canonical_payload", contract)
        self.assertNotIn("authoritative_drive_order", contract)
        self.assertFalse(load(AUDIT_PATH)["requested_scope_results"]["single_shared_off_preparation_passed"])

    def test_type_schemas_lack_invariant_and_cross_link_matrix(self) -> None:
        contract = load(S1YT_PATH)
        self.assertEqual(6, len(contract["corrected_exact_private_type_schemas"]))
        self.assertNotIn("private_type_invariants", contract)
        self.assertNotIn("cross_object_links", contract)
        self.assertFalse(load(AUDIT_PATH)["requested_scope_results"]["six_private_types_passed"])

    def test_transition_registry_and_preparation_failure_atomicity_are_missing(self) -> None:
        contract = load(S1YT_PATH)
        self.assertNotIn("base_transition_registry", contract)
        self.assertNotIn("preparation_failure_atomicity", contract)

    def test_source_branch_matrix_is_not_exhaustive(self) -> None:
        contract = load(S1YT_PATH)
        self.assertIn("steering_source_invariants", contract)
        self.assertNotIn("source_kind_arm_output_matrix", contract)
        self.assertFalse(load(AUDIT_PATH)["requested_scope_results"]["private_drive_mapping_passed"])

    def test_error_order_lacks_condition_and_function_mapping(self) -> None:
        contract = load(S1YT_PATH)
        self.assertEqual(8, len(contract["finite_error_codes"]))
        self.assertNotIn("error_condition_matrix", contract)
        self.assertNotIn("all_failure_output_rule", contract)

    def test_exact_five_final_blockers_are_fail_closed(self) -> None:
        audit = load(AUDIT_PATH)
        blockers = audit["final_preflight_blockers"]
        self.assertEqual(5, len(blockers))
        self.assertEqual(5, len({item["blocker_id"] for item in blockers}))
        self.assertTrue(all(item["detail"] for item in blockers))
        self.assertFalse(audit["implementation_gate"]["preflight_passed"])
        self.assertFalse(audit["implementation_gate"]["private_consumer_code_authorized"])

    def test_provisional_scope_remains_private_and_nonexecuting(self) -> None:
        scope = load(AUDIT_PATH)["provisional_implementation_scope_after_closure"]
        self.assertEqual("mcm_field_organism._lprh1f_s1yw_private_context_consumer", scope["private_module_name"])
        self.assertEqual(2, len(scope["permitted_functions"]))
        self.assertEqual(6, scope["permitted_type_count"])
        self.assertFalse(scope["public_export_allowed"])
        self.assertFalse(scope["field_execution_allowed"])

    def test_decision_preserves_generic_engineering_boundary_without_execution(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual(30, audit["passed_role_count"])
        self.assertEqual(5, audit["failed_role_count"])
        self.assertEqual("BLOCK_LPRH1F_PRIVATE_CONSUMER_IMPLEMENTATION_FIVE_FINAL_PREFLIGHT_BINDINGS_REQUIRED", audit["decision"])
        self.assertTrue(audit["requested_scope_results"]["generic_reducible_engineering_classification_preserved"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
