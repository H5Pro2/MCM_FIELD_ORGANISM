from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1YQ_LPRH1F_STATISCHER_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json"
S1YP_PATH = ROOT / "docs/S1YP_LPRH1F_STATISCHER_FELDNUTZUNGS_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_V1.json"
EXPECTED_AUDIT_DIGEST = "c8f7d3109fcc54f6f3bc875f113a8a37f0d7c63814c1a599dc2350669451c0a2"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1YQStaticMaterializabilityAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual("ad1870f4e60107666aac5426f17ae50cad99b5592076d29ea6872e72d355f15b", audit["parent_s1yp_canonical_contract_digest"])
        paths = {
            "s1yp_contract": "docs/S1YP_LPRH1F_STATISCHER_FELDNUTZUNGS_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_V1.json",
            "s1yp_document": "docs/S1YP_LPRH1F_STATISCHER_FELDNUTZUNGS_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG.md",
            "s1yp_tests": "tests/test_lprh1f_s1yp_static_field_consumption_contract.py",
            "s1yo_audit": "docs/S1YO_LPRH1_STATISCHER_IMPLEMENTIERUNGS_UND_GRENZENABSCHLUSSAUDIT_V1.json",
            "private_handoff_module": "mcm_field_organism/_lprh1_s1yn_private_local_handoff.py",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(audit["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_twenty_existing_contract_roles_are_retained(self) -> None:
        roles = load(AUDIT_PATH)["confirmed_contract_roles"]
        self.assertEqual(20, len(roles))
        self.assertEqual(20, len(set(roles)))
        self.assertIn("GENERIC_EQUAL_VALUE_VECTOR_IS_STRONGEST_BASELINE", roles)
        self.assertIn("REDUCED_RESULT_CLASSIFIED_AS_ENGINEERING_ONLY", roles)

    def test_exact_eight_materialization_blockers_are_distinct(self) -> None:
        blockers = load(AUDIT_PATH)["materialization_blockers"]
        identifiers = [item["blocker_id"] for item in blockers]
        self.assertEqual(8, len(identifiers))
        self.assertEqual(8, len(set(identifiers)))
        self.assertTrue(all(item["detail"] for item in blockers))

    def test_effect_base_output_and_private_schema_gaps_are_explicit(self) -> None:
        identifiers = {item["blocker_id"] for item in load(AUDIT_PATH)["materialization_blockers"]}
        self.assertIn("B1_EFFECT_MAGNITUDE_CLAMP_AND_TIE_RULE_UNBOUND", identifiers)
        self.assertIn("B2_BASE_TRANSITION_EVALUATION_AND_OFF_OUTPUT_BINDING_UNBOUND", identifiers)
        self.assertIn("B3_PRIVATE_DRIVE_OUTPUT_AND_RECEIPT_SCHEMAS_UNBOUND", identifiers)

    def test_field_consumption_is_separate_from_handoff_materialization(self) -> None:
        blocker = next(item for item in load(AUDIT_PATH)["materialization_blockers"] if item["blocker_id"] == "B4_FIELD_CONSUMPTION_LEDGER_MISSING")
        self.assertIn("DISTINCT_ATOMIC_LEDGER", blocker["detail"])
        self.assertIn("EXACTLY_ONE_LATER_FIELD_PROPOSAL", blocker["detail"])

    def test_baseline_fixture_and_comparator_gaps_are_explicit(self) -> None:
        identifiers = {item["blocker_id"] for item in load(AUDIT_PATH)["materialization_blockers"]}
        self.assertIn("B6_GENERIC_BASELINE_ADAPTER_AND_EQUAL_BUDGET_UNBOUND", identifiers)
        self.assertIn("B7_EXACT_HISTORY_FIXTURES_AND_DIRECTIONAL_MARGIN_UNBOUND", identifiers)
        self.assertIn("B8_MEASUREMENT_HORIZON_COMPARATOR_AND_DECISION_PRECEDENCE_UNBOUND", identifiers)

    def test_noncircular_question_is_not_yet_uniquely_materializable(self) -> None:
        result = load(AUDIT_PATH)["noncircularity_result"]
        self.assertTrue(result["history_precedes_target_output"])
        self.assertTrue(result["context_not_derived_from_target_output"])
        self.assertFalse(result["effect_materialization_is_unique"])
        self.assertFalse(result["baseline_materialization_is_fair"])
        self.assertFalse(result["atomic_field_consumption_is_defined"])

    def test_implementation_and_execution_remain_blocked(self) -> None:
        gate = load(AUDIT_PATH)["implementation_gate"]
        self.assertTrue(all(value is False for key, value in gate.items() if key.endswith("_authorized")))
        self.assertIn("ALL_EIGHT_BLOCKERS", gate["required_next_action"])

    def test_decision_is_fail_closed_and_nonexecuting(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual(20, audit["passed_role_count"])
        self.assertEqual(8, audit["failed_role_count"])
        self.assertEqual("BLOCK_LPRH1F_IMPLEMENTATION_EIGHT_MATERIALIZATION_BINDINGS_REQUIRED", audit["decision"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
