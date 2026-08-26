from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1XJ_PPB1_STATISCHER_VOLLFORM_RUNNER_SPERREN_RECEIPT_UND_AGGREGATOR_ABSCHLUSSAUDIT_V1.json"
SOURCE_PATH = ROOT / "mcm_field_organism/_ppb1_s1xi_private_full_runner.py"
EXPECTED_AUDIT_DIGEST = (
    "c4475ab701cd27b0ce5e049bd4f28fb940ec4b8f1b2c655f534bbacf4c871094"
)


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def source_text() -> str:
    return SOURCE_PATH.read_text(encoding="utf-8")


def source_tree() -> ast.Module:
    return ast.parse(source_text())


def function_node(name: str) -> ast.FunctionDef:
    return next(
        node
        for node in source_tree().body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


class PPB1S1XJStaticFullRunnerClosureAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_all_source_dependency_and_surface_hashes_are_exact(self) -> None:
        paths = {
            "s1xi_source": "mcm_field_organism/_ppb1_s1xi_private_full_runner.py",
            "s1xi_tests": "tests/test_ppb1_s1xi_private_full_runner.py",
            "s1xi_document": "docs/S1XI_PPB1_PRIVATER_VOLLFORM_RUNNER_RECEIPT_UND_AGGREGATOR_MIT_ERSATZPLAENEN.md",
            "s1xc_fixture_registry": "mcm_field_organism/_ppb1_s1xc_fixture_registry.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "s1xf_miniature_runner": "mcm_field_organism/_ppb1_s1xf_private_miniature_runner.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                load_audit()["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_parent_and_contract_digests_are_canonically_bound(self) -> None:
        audit = load_audit()
        for role, relative in (
            ("parent_s1xh_preflight_digest", "docs/S1XH_PPB1_STATISCHER_REGISTERED_MATRIX_IMPLEMENTIERUNGSDELTA_UND_AUSFUEHRUNGSPREFLIGHT_V1.json"),
            ("bound_s1xe_contract_digest", "docs/S1XE_PPB1_STATISCHER_PRIVATER_MATRIXRUNNER_RECEIPT_UND_ENTSCHEIDUNGSVERTRAG_V1.json"),
        ):
            value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            encoded = json.dumps(
                value, allow_nan=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
            self.assertEqual(audit[role], hashlib.sha256(encoded).hexdigest())
            self.assertIn(audit[role], source_text())

    def test_registered_flag_has_one_false_assignment_and_no_mutation(self) -> None:
        assignments = [
            node
            for node in source_tree().body
            if isinstance(node, (ast.Assign, ast.AnnAssign))
            and any(
                isinstance(target, ast.Name)
                and target.id == "S1XI_REGISTERED_EXECUTION_ENABLED"
                for target in (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
            )
        ]
        self.assertEqual(1, len(assignments))
        self.assertIsInstance(assignments[0].value, ast.Constant)
        self.assertIs(assignments[0].value.value, False)
        stores = [
            node
            for node in ast.walk(source_tree())
            if isinstance(node, ast.Name)
            and node.id == "S1XI_REGISTERED_EXECUTION_ENABLED"
            and isinstance(node.ctx, ast.Store)
        ]
        self.assertEqual(1, len(stores))

    def test_registered_guard_precedes_executor_and_has_no_early_project_call(self) -> None:
        entry = function_node("run_s1xi_registered_matrix")
        guard = next(node for node in entry.body if isinstance(node, ast.If))
        registered_call = next(
            node
            for node in ast.walk(entry)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_execute_plan_set"
        )
        self.assertLess(guard.lineno, registered_call.lineno)
        calls_before_guard = [
            node
            for node in ast.walk(entry)
            if isinstance(node, ast.Call)
            and node.lineno < guard.lineno
            and isinstance(node.func, ast.Name)
        ]
        self.assertEqual([], calls_before_guard)
        guard_source = ast.get_source_segment(source_text(), guard)
        self.assertIn("S1XI_REGISTERED_EXECUTION_LOCKED", guard_source)

    def test_registered_and_substitute_plan_sources_are_separate(self) -> None:
        core = ast.get_source_segment(source_text(), function_node("_execute_plan_set"))
        substitutes = ast.get_source_segment(source_text(), function_node("_substitute_plans"))
        self.assertIn("_registered_plans(materialized.cell_plans)", core)
        self.assertIn("_substitute_plans(materialized.modalities)", core)
        self.assertIn('"s1xi-sub.', substitutes)
        self.assertIn("S1XC_SYSTEM_IDS", substitutes)
        self.assertEqual(24, load_audit()["receipt_inventory"]["substitute_cell_receipt_count"])

    def test_four_frozen_receipt_types_have_exact_role_counts(self) -> None:
        expected = {
            "S1XIExecutionPlan": 8,
            "S1XIRegisteredCellReceipt": 19,
            "S1XIRegisteredMatrixReceipt": 15,
            "S1XIRunResult": 3,
        }
        classes = {
            node.name: node for node in source_tree().body if isinstance(node, ast.ClassDef)
        }
        for name, count in expected.items():
            self.assertEqual(
                count,
                len([node for node in classes[name].body if isinstance(node, ast.AnnAssign)]),
            )
            decorator = next(
                item
                for item in classes[name].decorator_list
                if isinstance(item, ast.Call)
                and isinstance(item.func, ast.Name)
                and item.func.id == "dataclass"
            )
            values = {
                item.arg: item.value.value
                for item in decorator.keywords
                if item.arg and isinstance(item.value, ast.Constant)
            }
            self.assertEqual({"frozen": True, "slots": True}, values)

    def test_receipts_bind_plan_and_keep_substitute_decisions_null(self) -> None:
        cell_source = ast.get_source_segment(
            source_text(),
            next(node for node in source_tree().body if isinstance(node, ast.ClassDef) and node.name == "S1XIRegisteredCellReceipt"),
        )
        matrix_source = ast.get_source_segment(
            source_text(),
            next(node for node in source_tree().body if isinstance(node, ast.ClassDef) and node.name == "S1XIRegisteredMatrixReceipt"),
        )
        self.assertIn('"cell_plan_digest": self.cell_plan_digest', cell_source)
        self.assertIn("len(self.ordered_cell_receipt_digests) != 24", matrix_source)
        self.assertIn("self.technical_function_decision is not None", matrix_source)
        self.assertIn("len(self.ordered_cell_receipt_digests) != 60", matrix_source)
        self.assertIn("self.registry_digest != S1XC_REGISTRY_DIGEST", matrix_source)

    def test_aggregator_compares_each_complete_baseline_without_mixing(self) -> None:
        aggregator = ast.get_source_segment(source_text(), function_node("_baseline_explanation"))
        self.assertIn("for system in S1XC_SYSTEM_IDS[1:]", aggregator)
        self.assertIn("baseline.keys() == candidate.keys()", aggregator)
        self.assertIn("_same_distance", aggregator)
        self.assertNotIn("any(", aggregator)

    def test_synthetic_tests_document_and_private_surfaces_are_bound(self) -> None:
        test_tree = ast.parse(
            (ROOT / "tests/test_ppb1_s1xi_private_full_runner.py").read_text(encoding="utf-8")
        )
        methods = [
            node
            for node in ast.walk(test_tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        self.assertEqual(12, len(methods))
        document = (ROOT / "docs/S1XI_PPB1_PRIVATER_VOLLFORM_RUNNER_RECEIPT_UND_AGGREGATOR_MIT_ERSATZPLAENEN.md").read_text(encoding="utf-8")
        self.assertIn(
            load_audit()["bound_technical_receipts"]["substitute_matrix_receipt_digest"],
            document,
        )
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            public_source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1xi", public_source)
            self.assertNotIn("run_s1xi_registered_matrix", public_source)

    def test_field_file_snapshot_and_production_paths_are_absent(self) -> None:
        source = source_text()
        for forbidden in (
            "SharedMCMField",
            "open(",
            "from pathlib",
            "snapshot",
            "production",
            "semantic_label",
        ):
            self.assertNotIn(forbidden, source)

    def test_decision_is_narrow_and_all_execution_counters_are_zero(self) -> None:
        audit = load_audit()
        self.assertEqual(20, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual(
            "PASS_IMPLEMENTATION_STATICALLY_CLOSED_REGISTERED_EXECUTION_AUTHORIZATION_STILL_MISSING",
            audit["decision"],
        )
        self.assertEqual(0, audit["implementation_closure"]["s1xh_implementation_gap_count_remaining"])
        self.assertFalse(audit["implementation_closure"]["registered_execution_authorization_present"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
