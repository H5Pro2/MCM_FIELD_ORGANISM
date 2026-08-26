from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1YS_LPRH1F_STATISCHER_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
S1YR_PATH = ROOT / "docs/S1YR_LPRH1F_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json"
S1YQ_PATH = ROOT / "docs/S1YQ_LPRH1F_STATISCHER_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json"
EXPECTED_AUDIT_DIGEST = "b4d8836bb82a4f34722b2a7d09b896e778c3581c407d16f10f961de41b1066d6"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1YSStaticClosureImplementationPreflightTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual("99364553ca58ae63756e8e69076d38974afa72b85246831c7f5f7c9ead33b0e9", audit["parent_s1yr_canonical_contract_digest"])
        paths = {
            "s1yr_contract": "docs/S1YR_LPRH1F_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json",
            "s1yr_document": "docs/S1YR_LPRH1F_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG.md",
            "s1yr_tests": "tests/test_lprh1f_s1yr_static_correction_materialization_contract.py",
            "s1yq_audit": "docs/S1YQ_LPRH1F_STATISCHER_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json",
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

    def test_all_eight_s1yq_blockers_have_declared_s1yr_closures(self) -> None:
        blockers = {item["blocker_id"] for item in load(S1YQ_PATH)["materialization_blockers"]}
        closure = load(S1YR_PATH)["blocker_closure"]
        self.assertEqual(blockers, set(closure))
        self.assertEqual(8, len(closure))

    def test_primary_midpoint_wording_is_ambiguous(self) -> None:
        rule = load(S1YR_PATH)["exact_steering_rule"]
        self.assertNotIn("THE_SUM_OF", rule["activation_rule"])
        self.assertIn("THE_SUM_OF", rule["equivalent_rule"])
        self.assertFalse(load(AUDIT_PATH)["requested_scope_results"]["exact_midpoint_rule_passed"])

    def test_contextual_input_has_digest_but_no_local_values(self) -> None:
        schema = load(S1YR_PATH)["exact_private_type_schemas"]["LPRH1FContextualProposalInput"]
        self.assertIn("context_digest_str_or_none", schema)
        self.assertFalse(any("local" in item.lower() and "value" in item.lower() for item in schema))

    def test_drive_and_base_output_types_and_canonical_payloads_are_missing(self) -> None:
        contract = load(S1YR_PATH)
        type_names = set(contract["exact_private_type_schemas"])
        self.assertFalse(any("DriveSet" in name or "BaseOutputSet" in name for name in type_names))
        self.assertNotIn("canonical_payloads_for_private_types", contract)

    def test_generic_mapping_is_not_dock_equal(self) -> None:
        schema = load(S1YR_PATH)["exact_private_type_schemas"]["LPRH1FGenericEqualValueInput"]
        mapping_role = next(item for item in schema if item.startswith("ordered_local_values"))
        self.assertNotIn("dock", mapping_role.lower())
        self.assertFalse(load(AUDIT_PATH)["requested_scope_results"]["equal_budget_generic_baseline_passed"])

    def test_function_signature_error_dispatch_and_counter_owner_are_absent(self) -> None:
        contract = load(S1YR_PATH)
        self.assertNotIn("future_pure_function", contract)
        self.assertNotIn("finite_error_codes", contract)
        self.assertNotIn("error_dispatch_in_precedence_order", contract)
        self.assertNotIn("base_output_preparation_receipt", contract)

    def test_exact_six_preflight_blockers_are_fail_closed(self) -> None:
        audit = load(AUDIT_PATH)
        blockers = audit["preflight_blockers"]
        self.assertEqual(6, len(blockers))
        self.assertEqual(6, len({item["blocker_id"] for item in blockers}))
        self.assertTrue(all(item["detail"] for item in blockers))
        self.assertFalse(audit["implementation_gate"]["preflight_passed"])
        self.assertFalse(audit["implementation_gate"]["private_consumer_code_authorized"])

    def test_decision_preserves_engineering_classification_without_execution(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual(26, audit["passed_role_count"])
        self.assertEqual(6, audit["failed_role_count"])
        self.assertEqual("BLOCK_LPRH1F_PRIVATE_CONSUMER_IMPLEMENTATION_SIX_PREFLIGHT_BINDINGS_REQUIRED", audit["decision"])
        self.assertTrue(audit["requested_scope_results"]["generic_reducible_engineering_classification_preserved"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
