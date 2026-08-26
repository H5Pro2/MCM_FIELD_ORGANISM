from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1YY_LPRH1F_STATISCHER_LAYERVERTRAG_UND_QUELLBINDUNGSKORREKTUR_V1.json"
S1YX_PATH = ROOT / "docs/S1YX_LPRH1F_STATISCHER_IMPLEMENTIERUNGSEINGANGS_BLOCKERAUDIT_V1.json"
EXPECTED_CONTRACT_DIGEST = "2d6de20121d1c4bd9f8ba9f6e127720b8b65eb69dd80f688fbe85839cd58a8c9"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def class_fields(relative: str, class_name: str) -> set[str]:
    tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
    node = next(item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == class_name)
    return {
        target.id
        for item in node.body
        if isinstance(item, ast.AnnAssign) and isinstance((target := item.target), ast.Name)
    }


class LPRH1FS1YYStaticLayerSourceBindingCorrectionContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(CONTRACT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load(CONTRACT_PATH)
        parent = load(S1YX_PATH)
        encoded = json.dumps(parent, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(contract["parent_s1yx_canonical_blocker_audit_digest"], hashlib.sha256(encoded).hexdigest())
        paths = {
            "s1yx_audit": "docs/S1YX_LPRH1F_STATISCHER_IMPLEMENTIERUNGSEINGANGS_BLOCKERAUDIT_V1.json",
            "s1yx_document": "docs/S1YX_LPRH1F_STATISCHER_IMPLEMENTIERUNGSEINGANGS_BLOCKERAUDIT.md",
            "s1yx_tests": "tests/test_lprh1f_s1yx_static_implementation_entry_blocker_audit.py",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "mcm_neuron": "mcm_field_organism/mcm_neuron.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(contract["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_signature_adds_only_source_layer_and_no_layer_id(self) -> None:
        signature = load(CONTRACT_PATH)["corrected_prepare_signature"]
        self.assertEqual(["source_layer_MCMNeuronLayer"], signature["added_input_roles"])
        self.assertEqual([], signature["removed_input_roles"])
        self.assertIn("source_layer_MCMNeuronLayer", signature["input_roles_in_order"])
        self.assertNotIn("layer_id_str", signature["input_roles_in_order"])
        self.assertFalse(signature["external_layer_id_parameter_allowed"])

    def test_layer_source_roles_exist_on_bound_type(self) -> None:
        fields = class_fields("mcm_field_organism/mcm_neuron_layer.py", "MCMNeuronLayer")
        self.assertIn("layer_id", fields)
        self.assertIn("neurons", fields)
        source = (ROOT / "mcm_field_organism/mcm_neuron_layer.py").read_text(encoding="utf-8")
        self.assertIn("def digest(self) -> str:", source)

    def test_field_prestate_roles_are_all_layer_derived(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(load(S1YX_PATH)["required_field_prestate_payload"], contract["canonical_field_prestate_payload"])
        sources = contract["authoritative_layer_source"]
        self.assertEqual("source_layer.layer_id", sources["layer_id_source"])
        self.assertFalse(sources["caller_layer_id_allowed"])
        self.assertFalse(sources["synthetic_layer_id_allowed"])
        self.assertFalse(sources["field_id_as_layer_id_allowed"])

    def test_drive_layer_mapping_is_exact_and_one_to_one(self) -> None:
        rules = load(CONTRACT_PATH)["exact_drive_layer_identity_rules"]
        self.assertEqual("EXACT_EQUAL_NONZERO", rules["cardinality"])
        self.assertEqual("EXACT_ONE_TO_ONE_SAME_INDEX", rules["neuron_id_mapping"])
        self.assertEqual("EXACT_SAME_OBJECT", rules["previous_object_identity"])
        self.assertEqual("EXACT_EQUAL", rules["previous_neuron_digest"])
        self.assertEqual("EVERY_DRIVE_STEP_TIME_EXACTLY_EQUALS_TARGET_STEP", rules["target_step"])

    def test_prepared_set_and_receipt_bind_source_layer_digest(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertIn("source_layer_digest_str", contract["corrected_prepared_drive_set_schema"])
        self.assertIn("source_layer_digest", contract["corrected_prepared_drive_set_canonical_payload"])
        self.assertIn("source_layer_digest", contract["corrected_preparation_receipt_id_payload"])

    def test_fail_closed_matrix_covers_all_required_mismatches(self) -> None:
        matrix = load(CONTRACT_PATH)["fail_closed_matrix"]
        self.assertEqual(7, len(matrix))
        self.assertTrue(all(item["output"] == "NONE" for item in matrix))
        conditions = " ".join(item["condition"] for item in matrix)
        for role in ("GEOMETRY_ID", "SOURCE_TICK", "OBJECT_OR_DIGEST", "FIELD_PRESTATE_DIGEST", "CHANGES"):
            self.assertIn(role, conditions)

    def test_sources_are_immutable_and_failures_are_atomic(self) -> None:
        rules = load(CONTRACT_PATH)["immutability_and_atomicity"]
        self.assertTrue(rules["source_layer_digest_before_equals_after"])
        self.assertTrue(rules["each_drive_digest_before_equals_after"])
        self.assertFalse(rules["source_layer_mutation_allowed"])
        self.assertFalse(rules["drive_mutation_allowed"])
        self.assertFalse(rules["partial_prepared_output_observable"])
        self.assertEqual(0, rules["retry_count"])
        self.assertEqual(0, rules["field_step_count"])

    def test_public_field_and_implementation_paths_remain_blocked(self) -> None:
        boundary = load(CONTRACT_PATH)["private_boundary"]
        self.assertEqual(9, len(boundary))
        self.assertTrue(all(value is False for value in boundary.values()))
        gate = load(CONTRACT_PATH)["implementation_gate"]
        self.assertFalse(gate["consumer_code_authorized"])
        self.assertTrue(gate["requires_separate_static_s1yz_acceptance_and_reauthorization_audit"])

    def test_single_parent_blocker_is_closed_without_execution(self) -> None:
        contract = load(CONTRACT_PATH)
        expected = {load(S1YX_PATH)["blocker"]["blocker_id"]}
        self.assertEqual(expected, set(contract["blocker_closure"]))
        self.assertEqual(35, contract["passed_role_count"])
        self.assertEqual(0, contract["failed_role_count"])
        self.assertEqual("PASS_LPRH1F_LAYER_SOURCE_BINDING_CORRECTION_CONTRACT_NO_IMPLEMENTATION", contract["decision"])
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
