from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1ZE_LPRH1F_STATISCHER_PRIVATER_DRIVE_ABLEITUNGS_UND_DOCK_FIXTURE_KORREKTURVERTRAG_V1.json"
S1ZD_PATH = ROOT / "docs/S1ZD_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_MATERIALISIERBARKEITSAUDIT_V1.json"
LAYER_PATH = ROOT / "mcm_field_organism/mcm_neuron_layer.py"
EXPECTED_CONTRACT_DIGEST = "c46c7bf679c51e60fae21109d1a7a0692b5de82fee7fe4e64bc5d0ca753c17f5"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1ZEStaticDriveDerivationCorrectionContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(CONTRACT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load(CONTRACT_PATH)
        parent = load(S1ZD_PATH)
        encoded = json.dumps(parent, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(contract["parent_s1zd_canonical_materializability_audit_digest"], hashlib.sha256(encoded).hexdigest())
        paths = {
            "s1zd_audit": "docs/S1ZD_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_MATERIALISIERBARKEITSAUDIT_V1.json",
            "s1zd_document": "docs/S1ZD_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_MATERIALISIERBARKEITSAUDIT.md",
            "s1zd_tests": "tests/test_lprh1f_s1zd_static_private_proposal_application_materializability_audit.py",
            "s1zc_contract": "docs/S1ZC_LPRH1F_STATISCHER_PRIVATER_PROPOSAL_ANWENDUNGS_UND_BASELINEVERTRAG_V1.json",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "private_consumer_module": "mcm_field_organism/_lprh1f_s1za_private_context_consumer.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(contract["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_private_helper_is_pure_preapplication_and_unexported(self) -> None:
        helper = load(CONTRACT_PATH)["private_derivation_helper"]
        self.assertEqual("derive_lprh1f_drives_for_layer_step", helper["function_name"])
        self.assertEqual(4, len(helper["input_roles_in_order"]))
        self.assertEqual(0, helper["MCMNeuronLayer_advance_call_count"])
        self.assertEqual(0, helper["SharedMCMField_call_count"])
        self.assertFalse(helper["public_export_allowed"])

    def test_bound_perception_method_exists_and_is_source_digest_bound(self) -> None:
        source = load(CONTRACT_PATH)["bound_core_derivation_source"]
        self.assertEqual("_perception_for", source["method_name"])
        self.assertEqual(load(CONTRACT_PATH)["bound_file_digests"]["mcm_neuron_layer"], source["source_digest"])
        tree = ast.parse(LAYER_PATH.read_text(encoding="utf-8"))
        layer_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MCMNeuronLayer")
        self.assertTrue(any(isinstance(node, ast.FunctionDef) and node.name == "_perception_for" for node in layer_class.body))
        self.assertFalse(source["algorithm_duplication_allowed"])
        self.assertFalse(source["fallback_perception_allowed"])

    def test_input_validation_precedes_derivation_and_atomic_return(self) -> None:
        order = load(CONTRACT_PATH)["input_bundle_validation_order"]
        self.assertEqual(11, len(order))
        call_index = order.index("CALL_BOUND__perception_for_ONCE_PER_ORDERED_NEURON")
        self.assertGreater(call_index, order.index("DERIVE_CANONICAL_RECEPTOR_INPUT_BUNDLE_DIGEST"))
        self.assertEqual("RETURN_COMPLETE_DERIVED_DRIVE_SET_AND_RECEIPT_ATOMICALLY", order[-1])

    def test_derived_set_binds_layer_input_target_drives_and_receipt(self) -> None:
        contract = load(CONTRACT_PATH)
        schema = contract["derived_drive_set_schema"]
        payload = contract["derived_drive_set_canonical_payload"]
        receipt = contract["derivation_receipt_id_payload"]
        self.assertEqual(9, len(schema))
        for role in ("source_layer_digest", "target_step_digest", "receptor_input_bundle_digest", "ordered_drive_digests", "derivation_receipt_id"):
            self.assertIn(role, payload)
        self.assertIn("receipt_kind_LITERAL_PRIVATE_DRIVE_DERIVATION", receipt)

    def test_prepare_and_callback_share_exact_derived_drives(self) -> None:
        links = load(CONTRACT_PATH)["corrected_prepare_and_application_links"]
        self.assertIn("EXACT", links["prepare_ordered_drives_source"])
        self.assertIn("EQUALS", links["callback_drive_digest_rule"])
        self.assertIn("SAME_SOURCE_LAYER_NEURON_OBJECT", links["callback_previous_identity_rule"])
        self.assertFalse(links["second_derivation_or_capture_pass_allowed"])

    def test_fixture_dock_contact_transient_and_perception_are_consistent(self) -> None:
        fixture = load(CONTRACT_PATH)["dock_consistent_fixture"]
        self.assertEqual(fixture["ordered_neuron_ids"], fixture["receptor_dock_ids"])
        self.assertEqual(fixture["ordered_neuron_ids"], fixture["transient_input_keys"])
        self.assertEqual(fixture["ordered_neuron_ids"], [item[0] for item in fixture["receptor_contacts"]])
        self.assertEqual(fixture["receptor_contacts"][0][1], fixture["expected_derived_perception"]["receptor_contact"])
        self.assertEqual(1, fixture["expected_drive_count"])
        self.assertIn("EXACT_EQUAL", fixture["expected_callback_drive_digest_relation"])

    def test_eight_arms_share_drive_set_and_pairwise_baselines(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(8, len(contract["finite_fixture_arms"]))
        relations = contract["fixture_baseline_relations"]
        self.assertEqual(6, len(relations))
        self.assertTrue(all(relations.values()))

    def test_both_parent_blockers_are_closed_without_execution(self) -> None:
        contract = load(CONTRACT_PATH)
        expected = {item["blocker_id"] for item in load(S1ZD_PATH)["materializability_blockers"]}
        self.assertEqual(expected, set(contract["blocker_closure"]))
        gate = contract["implementation_gate"]
        self.assertTrue(all(value is False for key, value in gate.items() if key != "requires_separate_s1zf_static_closure_and_preflight_audit"))
        self.assertTrue(gate["requires_separate_s1zf_static_closure_and_preflight_audit"])
        self.assertEqual(43, contract["passed_role_count"])
        self.assertEqual(0, contract["failed_role_count"])
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
