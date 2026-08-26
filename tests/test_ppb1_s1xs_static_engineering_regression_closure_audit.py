from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    ROOT / "docs/S1XS_PPB1_STATISCHER_ENGINEERINGREGRESSION_ABSCHLUSSAUDIT_V1.json"
)
SOURCE_PATH = ROOT / "mcm_field_organism/_ppb1_s1xr_private_engineering_regression.py"
EXPECTED_AUDIT_DIGEST = (
    "9707b0c2075bbefa9240189887dec9b554e47c27a665ecf99ceee34ad1196cb3"
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


def direct_calls(node: ast.AST, name: str) -> list[ast.Call]:
    return [
        item
        for item in ast.walk(node)
        if isinstance(item, ast.Call)
        and isinstance(item.func, ast.Name)
        and item.func.id == name
    ]


class PPB1S1XSStaticEngineeringRegressionClosureAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_all_source_dependency_and_surface_hashes_are_exact(self) -> None:
        paths = {
            "s1xr_source": "mcm_field_organism/_ppb1_s1xr_private_engineering_regression.py",
            "s1xr_tests": "tests/test_ppb1_s1xr_private_engineering_regression.py",
            "s1xr_document": "docs/S1XR_PPB1_PRIVATE_ENGINEERING_REGRESSION_IMPLEMENTIERUNG.md",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wq_state_identity": "mcm_field_organism/_ppb1_s1wq_perceptual_state_lifecycle.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "s1xo_margin_fixture": "mcm_field_organism/_ppb1_s1xo_private_numeric_margin_fixture.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                load_audit()["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_contract_digest_and_single_fixture_build_are_static(self) -> None:
        tree = source_tree()
        contract = next(
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "S1XR_CONTRACT_DIGEST" for target in node.targets)
        )
        self.assertIn(load_audit()["parent_s1xq_contract_digest"], ast.get_source_segment(source_text(), contract))
        runner = function_node("run_s1xr_private_engineering_regression")
        self.assertEqual(1, len(direct_calls(runner, "build_s1xo_numeric_margin_fixture")))

    def test_formation_has_one_initial_state_and_three_step_loop(self) -> None:
        formation = function_node("_form_state")
        self.assertEqual(1, len(direct_calls(formation, "initial_ppb1_bank_state")))
        loop = next(node for node in formation.body if isinstance(node, ast.For))
        self.assertEqual("range(3)", ast.unparse(loop.iter))
        self.assertEqual(1, len(direct_calls(loop, "advance_ppb1_bank")))
        probe_helpers = {
            "probe_s1wu_perceptual_state",
            "normalized_mean_l1_distance",
        }
        self.assertTrue(
            all(
                not isinstance(node, ast.Call)
                or not isinstance(node.func, ast.Name)
                or node.func.id not in probe_helpers
                for node in ast.walk(formation)
            )
        )

    def test_runner_forms_both_modalities_before_candidate_and_baseline_cells(self) -> None:
        runner = function_node("run_s1xr_private_engineering_regression")
        calls = [
            (node.lineno, node.func.id)
            for node in ast.walk(runner)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        formation_line = min(line for line, name in calls if name == "_form_state")
        candidate_line = min(line for line, name in calls if name == "_candidate_cells")
        baseline_line = min(line for line, name in calls if name == "_baseline_cells")
        self.assertLess(formation_line, candidate_line)
        self.assertLess(candidate_line, baseline_line)
        self.assertIn("cells = candidate_cells + baseline_cells", source_text())

    def test_probe_and_baseline_helpers_bind_five_fixture_rows_each(self) -> None:
        for helper_name, call_name in (
            ("_candidate_cells", "probe_s1wu_perceptual_state"),
            ("_baseline_cells", "normalized_mean_l1_distance"),
        ):
            helper = function_node(helper_name)
            loop = next(node for node in helper.body if isinstance(node, ast.For))
            segment = ast.get_source_segment(source_text(), loop)
            assert segment is not None
            self.assertIn("fixture.probe_classes", segment)
            self.assertIn("fixture.probe_values", segment)
            self.assertIn("fixture.expected_recognition", segment)
            self.assertIn("fixture.computed_distances", segment)
            self.assertEqual(1, len(direct_calls(loop, call_name)))
        self.assertEqual(10, load_audit()["call_budget"]["candidate_probe_count"])
        self.assertEqual(10, load_audit()["call_budget"]["baseline_distance_count"])

    def test_candidate_is_read_only_and_baseline_has_no_state_identity(self) -> None:
        candidate = ast.get_source_segment(source_text(), function_node("_candidate_cells"))
        baseline = ast.get_source_segment(source_text(), function_node("_baseline_cells"))
        assert candidate is not None and baseline is not None
        self.assertIn("before = state.digest()", candidate)
        self.assertIn("after = state.digest()", candidate)
        self.assertIn('"state_unchanged": before == after', candidate)
        self.assertIn('"raw_history_access_used": False', candidate)
        self.assertIn('"observed_state_digest": None', baseline)
        self.assertIn('"state_identity_digest": None', baseline)
        self.assertNotIn("probe_s1wu_perceptual_state", baseline)

    def test_equivalence_compares_recognition_and_distance(self) -> None:
        runner = ast.get_source_segment(
            source_text(), function_node("run_s1xr_private_engineering_regression")
        )
        assert runner is not None
        self.assertIn("candidate_map.keys() == baseline_map.keys()", runner)
        self.assertIn("candidate_map[key].recognized == baseline_map[key].recognized", runner)
        self.assertIn("candidate_map[key].distance == baseline_map[key].distance", runner)

    def test_four_receipt_types_are_frozen_slotted_and_role_complete(self) -> None:
        expected = {
            "S1XRFormationReceipt": 10,
            "S1XREngineeringCellReceipt": 13,
            "S1XREngineeringRegressionReceipt": 10,
            "S1XREngineeringRegressionResult": 3,
        }
        classes = {
            node.name: node for node in source_tree().body if isinstance(node, ast.ClassDef)
        }
        for name, count in expected.items():
            annotations = [node for node in classes[name].body if isinstance(node, ast.AnnAssign)]
            self.assertEqual(count, len(annotations))
            decorator = next(
                item
                for item in classes[name].decorator_list
                if isinstance(item, ast.Call)
                and isinstance(item.func, ast.Name)
                and item.func.id == "dataclass"
            )
            keywords = {
                item.arg: item.value.value
                for item in decorator.keywords
                if item.arg and isinstance(item.value, ast.Constant)
            }
            self.assertEqual({"frozen": True, "slots": True}, keywords)

    def test_twenty_cell_receipt_and_technical_result_are_narrowly_bound(self) -> None:
        audit = load_audit()
        self.assertEqual(2, audit["receipt_inventory"]["ordered_formation_receipt_count"])
        self.assertEqual(10, audit["receipt_inventory"]["ordered_candidate_cell_count"])
        self.assertEqual(10, audit["receipt_inventory"]["ordered_baseline_cell_count"])
        document = (ROOT / "docs/S1XR_PPB1_PRIVATE_ENGINEERING_REGRESSION_IMPLEMENTIERUNG.md").read_text(encoding="utf-8")
        for value in audit["bound_technical_receipts"].values():
            self.assertIn(value, document)

    def test_twelve_synthetic_tests_are_source_bound(self) -> None:
        tree = ast.parse(
            (ROOT / "tests/test_ppb1_s1xr_private_engineering_regression.py").read_text(encoding="utf-8")
        )
        methods = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        self.assertEqual(12, len(methods))

    def test_s1xr_is_private_and_matrix_field_file_paths_are_absent(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            public_source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1xr", public_source)
            self.assertNotIn("run_s1xr_private_engineering_regression", public_source)
        source = source_text()
        for forbidden in (
            "_ppb1_s1xc_fixture_registry",
            "_ppb1_s1xi_private_full_runner",
            "materialize_s1xc_fixture_registry",
            "run_s1xi_registered_matrix",
            "SharedMCMField",
            "open(",
            "write_text(",
            "production_adapter",
            "snapshot",
            "semantic_label",
        ):
            self.assertNotIn(forbidden, source)

    def test_decision_is_narrow_and_all_execution_counters_are_zero(self) -> None:
        audit = load_audit()
        self.assertEqual(19, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual(
            "PASS_S1XR_STATIC_CLOSURE_ENGINEERING_EQUIVALENCE_ONLY",
            audit["decision"],
        )
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
