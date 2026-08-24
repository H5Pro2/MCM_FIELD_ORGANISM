from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1ZC_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_UND_BASELINEVERTRAG_V1.json"
S1ZB_PATH = ROOT / "docs/S1ZB_LPRH1F_STATISCHER_PRIVATER_IMPLEMENTIERUNGS_UND_GRENZENABSCHLUSSAUDIT_V1.json"
EXPECTED_CONTRACT_DIGEST = "26d3b2243048c009a4514966ebe26e86852d3034d35cb09e6078f3868f0a6d57"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1ZCStaticPrivateProposalApplicationContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(CONTRACT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load(CONTRACT_PATH)
        parent = load(S1ZB_PATH)
        encoded = json.dumps(parent, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(contract["parent_s1zb_canonical_closure_audit_digest"], hashlib.sha256(encoded).hexdigest())
        paths = {
            "s1zb_audit": "docs/S1ZB_LPRH1F_STATISCHER_PRIVATER_IMPLEMENTIERUNGS_UND_GRENZENABSCHLUSSAUDIT_V1.json",
            "s1zb_document": "docs/S1ZB_LPRH1F_STATISCHER_PRIVATER_IMPLEMENTIERUNGS_UND_GRENZENABSCHLUSSAUDIT.md",
            "s1zb_tests": "tests/test_lprh1f_s1zb_static_private_implementation_and_boundary_closure_audit.py",
            "private_consumer_module": "mcm_field_organism/_lprh1f_s1za_private_context_consumer.py",
            "private_consumer_tests": "tests/test_lprh1f_s1za_private_layer_bound_context_consumer.py",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "mcm_neuron": "mcm_field_organism/mcm_neuron.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(contract["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_function_is_exactly_one_private_layer_application(self) -> None:
        function = load(CONTRACT_PATH)["technical_function"]
        self.assertEqual("EXACTLY_ONE_MCMNeuronLayer.advance_CALL_AFTER_ALL_BINDINGS_PASS", function["application_horizon"])
        self.assertEqual("ENGINEERING_APPLICATION_ONLY", function["interpretation"])
        signature = load(CONTRACT_PATH)["future_private_function_signature"]
        self.assertEqual("apply_lprh1f_proposal_once", signature["function_name"])
        self.assertEqual(6, len(signature["input_roles_in_order"]))
        self.assertFalse(signature["public_export_allowed"])

    def test_preapplication_order_rejects_duplicate_before_layer_call(self) -> None:
        order = load(CONTRACT_PATH)["preapplication_binding_order"]
        self.assertEqual(10, len(order))
        duplicate_index = order.index("REJECT_DUPLICATE_LAYER_APPLICATION_ID_BEFORE_ANY_LAYER_CALL")
        call_index = order.index("CALL_SOURCE_LAYER_ADVANCE_EXACTLY_ONCE_WITH_PRIVATE_TRANSITION_ADAPTER")
        self.assertLess(duplicate_index, call_index)

    def test_transition_adapter_revalidates_each_regenerated_drive(self) -> None:
        adapter = load(CONTRACT_PATH)["private_transition_adapter"]
        self.assertIn("EXACTLY_EQUALS", adapter["regenerated_drive_digest_rule"])
        self.assertIn("SAME_OBJECT", adapter["regenerated_previous_identity_rule"])
        self.assertFalse(adapter["proposal_or_source_mutation_allowed"])
        self.assertFalse(adapter["fallback_transition_allowed"])
        self.assertFalse(adapter["retry_allowed"])

    def test_application_identity_has_distinct_namespace_and_atomic_ledger(self) -> None:
        identity = load(CONTRACT_PATH)["layer_application_identity"]
        self.assertIn("DISTINCT_FROM_HANDOFF_AND_FIELD_USE", identity["namespace"])
        self.assertEqual(6, len(identity["application_id_payload"]))
        self.assertEqual(3, len(identity["receipt_id_payload"]))
        self.assertTrue(identity["duplicate_rejected_before_layer_call"])

    def test_candidate_and_generic_baseline_are_budget_and_value_equal(self) -> None:
        baseline = load(CONTRACT_PATH)["fair_baseline_contract"]
        required_true = (
            "same_source_layer_object",
            "same_prepared_drive_set_object_and_digest",
            "same_receptor_contacts_and_transient_inputs",
            "same_target_step_and_field_prestate",
            "same_local_neuron_dock_carrier_value_tuples",
            "same_proposal_numeric_outputs_required_before_application",
        )
        self.assertTrue(all(baseline[role] for role in required_true))
        self.assertEqual(1, baseline["same_layer_advance_call_budget"])
        self.assertEqual("EXACT_EQUAL", baseline["expected_next_layer_digest_relation"])
        self.assertEqual("GENERIC_REDUCTION_BY_CONSTRUCTION", baseline["expected_interpretation"])

    def test_atomic_failures_return_no_partial_layer_or_receipt(self) -> None:
        rules = load(CONTRACT_PATH)["atomicity_and_fail_closed_rules"]
        self.assertFalse(rules["partial_next_layer_observable"])
        self.assertFalse(rules["partial_receipt_observable"])
        self.assertTrue(rules["source_layer_digest_before_equals_after"])
        self.assertEqual(0, rules["retry_count"])
        self.assertEqual(0, rules["shared_mcm_field_call_count"])
        self.assertEqual(0, rules["production_call_count"])

    def test_method_invalid_and_stop_rules_are_finite(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(6, len(contract["method_invalid_conditions"]))
        rules = contract["decision_and_stop_rules"]
        self.assertEqual(4, len(rules))
        self.assertEqual(4, len({item["decision"] for item in rules}))
        self.assertEqual("TECHNICAL_APPLICATION_PASS_GENERIC_REDUCTION_CONFIRMED", rules[-1]["decision"])

    def test_no_implementation_or_execution_is_authorized(self) -> None:
        contract = load(CONTRACT_PATH)
        gate = contract["implementation_gate"]
        self.assertTrue(all(value is False for key, value in gate.items() if key != "requires_separate_static_materializability_audit"))
        self.assertTrue(gate["requires_separate_static_materializability_audit"])
        self.assertEqual(42, contract["passed_role_count"])
        self.assertEqual(0, contract["failed_role_count"])
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
