from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1ZB_LPRH1F_STATISCHER_PRIVATER_IMPLEMENTIERUNGS_UND_GRENZENABSCHLUSSAUDIT_V1.json"
S1ZA_PATH = ROOT / "docs/S1ZA_LPRH1F_PRIVATE_LAYERGEBUNDENE_CONSUMER_IMPLEMENTIERUNG_V1.json"
MODULE_PATH = ROOT / "mcm_field_organism/_lprh1f_s1za_private_context_consumer.py"
TEST_PATH = ROOT / "tests/test_lprh1f_s1za_private_layer_bound_context_consumer.py"
EXPECTED_AUDIT_DIGEST = "7d9c6d998c9d44439d38fa768eeae5ccec7517f30466674fadb4f26d72b1237d"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


class LPRH1FS1ZBStaticPrivateImplementationClosureAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_all_bound_files_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        parent = load(S1ZA_PATH)
        encoded = json.dumps(parent, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(audit["parent_s1za_canonical_implementation_digest"], hashlib.sha256(encoded).hexdigest())
        paths = {
            "s1za_implementation": "docs/S1ZA_LPRH1F_PRIVATE_LAYERGEBUNDENE_CONSUMER_IMPLEMENTIERUNG_V1.json",
            "s1za_document": "docs/S1ZA_LPRH1F_PRIVATE_LAYERGEBUNDENE_CONSUMER_IMPLEMENTIERUNG.md",
            "private_consumer_module": "mcm_field_organism/_lprh1f_s1za_private_context_consumer.py",
            "synthetic_contract_tests": "tests/test_lprh1f_s1za_private_layer_bound_context_consumer.py",
            "s1yz_audit": "docs/S1YZ_LPRH1F_STATISCHER_LAYERQUELLBINDUNGS_ABNAHME_UND_IMPLEMENTIERUNGSFREIGABEAUDIT_V1.json",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "mcm_neuron": "mcm_field_organism/mcm_neuron.py",
        }
        for role, relative in paths.items():
            self.assertEqual(audit["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_exactly_two_permitted_module_functions_are_non_private(self) -> None:
        functions = [
            node.name
            for node in parse(MODULE_PATH).body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not node.name.startswith("_")
        ]
        expected = load(AUDIT_PATH)["source_structure_findings"]["permitted_public_function_names"]
        self.assertEqual(expected, functions)

    def test_six_transport_types_and_one_error_class_are_exact(self) -> None:
        classes = [node.name for node in parse(MODULE_PATH).body if isinstance(node, ast.ClassDef)]
        structure = load(AUDIT_PATH)["source_structure_findings"]
        expected = [structure["finite_error_class_name"], *structure["private_transport_type_names"]]
        self.assertEqual(expected, classes)
        self.assertEqual(6, structure["private_transport_type_count"])

    def test_eight_error_codes_and_eight_source_arms_are_static(self) -> None:
        tree = parse(MODULE_PATH)
        error_names = {
            target.id
            for node in tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name) and target.id.startswith("LPRH1F_") and target.id not in {"LPRH1F_SCHEMA_VERSION", "LPRH1F_BASE_TRANSITION_ID"}
        }
        self.assertEqual(8, len(error_names))
        arm_assignment = next(
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "_ARM_MATRIX" for target in node.targets)
        )
        self.assertIsInstance(arm_assignment.value, ast.Dict)
        assert isinstance(arm_assignment.value, ast.Dict)
        self.assertEqual(8, len(arm_assignment.value.keys))

    def test_implementation_invariants_are_all_accepted(self) -> None:
        findings = load(AUDIT_PATH)["implementation_acceptance"]
        self.assertEqual(10, len(findings))
        self.assertTrue(all(findings.values()))

    def test_eight_synthetic_test_methods_exist(self) -> None:
        classes = [node for node in parse(TEST_PATH).body if isinstance(node, ast.ClassDef)]
        methods = [
            node.name
            for cls in classes
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        self.assertEqual(8, len(methods))
        self.assertEqual(8, load(AUDIT_PATH)["test_acceptance"]["implemented_test_method_count"])

    def test_no_field_production_persistence_or_process_calls_exist(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        forbidden = (
            "SharedMCMField",
            "advance_mcm_neuron_layer",
            ".advance(",
            "snapshot(",
            "subprocess",
            "socket",
            "requests",
            "open(",
            "Path(",
        )
        for token in forbidden:
            self.assertNotIn(token, source)
        findings = load(AUDIT_PATH)["static_no_execution_findings"]
        self.assertTrue(all(value is False for value in findings.values()))

    def test_public_boundaries_are_digest_unchanged_and_unexported(self) -> None:
        boundary = load(AUDIT_PATH)["public_boundary_acceptance"]
        unchanged = [value for key, value in boundary.items() if key.endswith("_digest_unchanged")]
        negative = [value for key, value in boundary.items() if not key.endswith("_digest_unchanged")]
        self.assertEqual(6, len(unchanged))
        self.assertTrue(all(unchanged))
        self.assertTrue(all(value is False for value in negative))

    def test_closure_accepts_only_private_engineering_component(self) -> None:
        audit = load(AUDIT_PATH)
        gate = audit["closure_gate"]
        self.assertTrue(gate["private_s1za_implementation_accepted"])
        self.assertTrue(gate["private_synthetic_engineering_component_available"])
        self.assertFalse(gate["public_or_production_integration_authorized"])
        self.assertFalse(gate["field_proposal_application_authorized"])
        self.assertTrue(gate["new_static_contract_required_before_any_field_application"])
        self.assertEqual(45, audit["passed_audit_role_count"])
        self.assertEqual(0, audit["failed_audit_role_count"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
