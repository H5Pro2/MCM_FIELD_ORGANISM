from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs" / (
    "S1XD_PPB1_STATISCHER_QUELL_DIGEST_EXPORT_UND_"
    "NICHTAUSFUEHRUNGSAUDIT_V1.json"
)
SOURCE_PATH = ROOT / "mcm_field_organism" / "_ppb1_s1xc_fixture_registry.py"
EXPECTED_AUDIT_DIGEST = (
    "aaacb723a09e228ff0dc7d93908d27006675d518ea0c22d159625431385aba14"
)


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def source_tree():
    return ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))


class PPB1S1XDStaticSourceExportNonexecutionAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_all_bound_file_hashes_are_exact(self) -> None:
        paths = {
            "s1xc_source": "mcm_field_organism/_ppb1_s1xc_fixture_registry.py",
            "s1xc_tests": "tests/test_ppb1_s1xc_fixture_registry.py",
            "s1xc_document": "docs/S1XC_PPB1_PRIVATE_FIXTURE_REGISTRY_UND_READ_ONLY_BASELINEADAPTER.md",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                load_audit()["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_expected_private_classes_and_entry_functions_exist(self) -> None:
        tree = source_tree()
        classes = {
            node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
        }
        functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        audit = load_audit()["ast_inventory"]
        self.assertTrue(set(audit["frozen_data_classes"]) <= set(classes))
        for class_name in audit["frozen_data_classes"]:
            decorator = next(
                item
                for item in classes[class_name].decorator_list
                if isinstance(item, ast.Call)
                and isinstance(item.func, ast.Name)
                and item.func.id == "dataclass"
            )
            keywords = {
                item.arg: item.value.value
                for item in decorator.keywords
                if item.arg is not None and isinstance(item.value, ast.Constant)
            }
            self.assertEqual({"frozen": True, "slots": True}, keywords)
        self.assertEqual(
            set(audit["private_entry_functions"]),
            functions
            & {"materialize_s1xc_fixture_registry", "probe_s1xc_baseline_read_only"},
        )

    def test_forbidden_runtime_symbols_and_domain_state_writes_are_absent(self) -> None:
        tree = source_tree()
        names = {
            node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
        } | {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        self.assertTrue(
            set(load_audit()["forbidden_runtime_symbols_absent"]).isdisjoint(names)
        )
        attribute_writes = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
            and isinstance(node.ctx, ast.Store)
        ]
        subscript_writes = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Store)
        ]
        self.assertEqual(
            ["code", "detail"], sorted(node.attr for node in attribute_writes)
        )
        self.assertTrue(
            all(
                isinstance(node.value, ast.Name) and node.value.id == "self"
                for node in attribute_writes
            )
        )
        self.assertEqual([], subscript_writes)

    def test_no_file_network_process_or_production_import_exists(self) -> None:
        imported = set()
        for node in ast.walk(source_tree()):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue(
            imported.isdisjoint({"os", "pathlib", "socket", "subprocess", "requests"})
        )

    def test_s1xc_is_absent_from_all_public_export_surfaces(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1xc", source)
            self.assertNotIn("materialize_s1xc_fixture_registry", source)
            self.assertNotIn("probe_s1xc_baseline_read_only", source)

    def test_finding_ast_has_no_poststate_role(self) -> None:
        finding = next(
            node
            for node in source_tree().body
            if isinstance(node, ast.ClassDef) and node.name == "S1XCBaselineFinding"
        )
        annotated = {
            node.target.id
            for node in finding.body
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
        }
        self.assertNotIn("poststate", annotated)
        self.assertNotIn("prototype_values", annotated)

    def test_source_bound_test_count_and_documented_digests_are_exact(self) -> None:
        test_tree = ast.parse(
            (ROOT / "tests/test_ppb1_s1xc_fixture_registry.py").read_text(
                encoding="utf-8"
            )
        )
        methods = [
            node
            for node in ast.walk(test_tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        self.assertEqual(13, len(methods))
        document = (ROOT / "docs/S1XC_PPB1_PRIVATE_FIXTURE_REGISTRY_UND_READ_ONLY_BASELINEADAPTER.md").read_text(encoding="utf-8")
        for digest in load_audit()["bound_implementation_digests"].values():
            self.assertIn(digest, document)

    def test_decision_is_narrow_and_every_execution_counter_is_zero(self) -> None:
        audit = load_audit()
        self.assertEqual(17, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual(
            "PASS_PRIVATE_IMPLEMENTATION_STATICALLY_BOUND_MATRIX_EXECUTION_STILL_CLOSED",
            audit["decision"],
        )
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
