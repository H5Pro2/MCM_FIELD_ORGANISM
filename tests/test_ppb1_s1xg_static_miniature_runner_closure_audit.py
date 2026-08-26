from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1XG_PPB1_STATISCHER_MINIATURRUNNER_ABSCHLUSSAUDIT_V1.json"
SOURCE_PATH = ROOT / "mcm_field_organism/_ppb1_s1xf_private_miniature_runner.py"
EXPECTED_AUDIT_DIGEST = (
    "7a2d5c3838a04d16f2cc9c87d6d6e2b07fa3781f230c4627e4939d7177c8c1f6"
)


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def source_tree():
    return ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))


def function_node(name: str) -> ast.FunctionDef:
    return next(
        node
        for node in source_tree().body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


class PPB1S1XGStaticMiniatureRunnerClosureAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_all_source_dependency_and_surface_hashes_are_exact(self) -> None:
        paths = {
            "s1xf_source": "mcm_field_organism/_ppb1_s1xf_private_miniature_runner.py",
            "s1xf_tests": "tests/test_ppb1_s1xf_private_miniature_runner.py",
            "s1xf_document": "docs/S1XF_PPB1_PRIVATER_MINIATURRUNNER_UND_RECEIPTABNAHME.md",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wq_state_identity": "mcm_field_organism/_ppb1_s1wq_perceptual_state_lifecycle.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "s1xc_fixture_registry": "mcm_field_organism/_ppb1_s1xc_fixture_registry.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                load_audit()["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_three_advances_precede_every_template_access(self) -> None:
        formation = function_node("_form_candidate")
        initial_call = next(
            node
            for node in ast.walk(formation)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "initial_ppb1_bank_state"
        )
        frame_loop = next(node for node in formation.body if isinstance(node, ast.For))
        advance_call = next(
            node
            for node in ast.walk(frame_loop)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "advance_ppb1_bank"
        )
        template_accesses = [
            node
            for node in ast.walk(formation)
            if isinstance(node, ast.Attribute) and node.attr == "candidate_prestate"
        ]
        self.assertLess(initial_call.lineno, frame_loop.lineno)
        self.assertGreater(advance_call.lineno, frame_loop.lineno)
        self.assertTrue(template_accesses)
        self.assertTrue(
            all(node.lineno > frame_loop.end_lineno for node in template_accesses)
        )

    def test_full_state_digest_and_identity_comparisons_precede_return(self) -> None:
        source = ast.get_source_segment(
            SOURCE_PATH.read_text(encoding="utf-8"), function_node("_form_candidate")
        )
        assert source is not None
        self.assertIn("state != fixture.candidate_prestate", source)
        self.assertIn("state.digest() != fixture.candidate_prestate.digest()", source)
        self.assertIn("identity_digest != fixture.candidate_state_identity_digest", source)
        self.assertNotIn("probe_s1wu_perceptual_state", source)
        self.assertNotIn("probe_s1xc_baseline_read_only", source)

    def test_runner_finishes_formations_before_cell_helpers(self) -> None:
        runner = function_node("run_s1xf_miniature_contract")
        calls = [
            (node.lineno, node.func.id)
            for node in ast.walk(runner)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        formation_line = min(line for line, name in calls if name == "_form_candidate")
        cell_lines = [
            line
            for line, name in calls
            if name in {"_candidate_cell", "_baseline_cell"}
        ]
        self.assertTrue(cell_lines)
        self.assertTrue(all(line > formation_line for line in cell_lines))

    def test_four_frozen_receipt_types_have_exact_role_counts(self) -> None:
        expected = {
            "S1XFFormationReceipt": 11,
            "S1XFCellReceipt": 18,
            "S1XFMatrixReceipt": 11,
            "S1XFRunResult": 3,
        }
        classes = {
            node.name: node
            for node in source_tree().body
            if isinstance(node, ast.ClassDef)
        }
        for name, count in expected.items():
            annotations = [
                node for node in classes[name].body if isinstance(node, ast.AnnAssign)
            ]
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

    def test_miniature_binding_is_24_and_never_consumes_registered_plans(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8")
        self.assertIn('S1XF_MINI_PROBE_CLASSES = ("exact-positive", "distinct-negative")', source)
        self.assertNotIn("materialized.cell_plans", source)
        self.assertNotIn("s1xa.", source)
        self.assertNotIn("execute_s1vn_matrix", source)
        binding = load_audit()["miniature_cell_binding"]
        self.assertEqual(24, binding["expected_cell_count"])
        self.assertEqual(0, binding["registered_s1xa_cell_id_count"])

    def test_technical_receipts_are_documented_and_tests_are_source_bound(self) -> None:
        audit = load_audit()
        document = (
            ROOT / "docs/S1XF_PPB1_PRIVATER_MINIATURRUNNER_UND_RECEIPTABNAHME.md"
        ).read_text(encoding="utf-8")
        for role, value in audit["bound_technical_receipts"].items():
            if role.endswith("_digest"):
                self.assertIn(value, document)
        test_tree = ast.parse(
            (ROOT / "tests/test_ppb1_s1xf_private_miniature_runner.py").read_text(
                encoding="utf-8"
            )
        )
        methods = [
            node
            for node in ast.walk(test_tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        self.assertEqual(12, len(methods))

    def test_s1xf_is_private_and_field_file_production_paths_are_absent(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            public_source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1xf", public_source)
            self.assertNotIn("run_s1xf_miniature_contract", public_source)
        source = SOURCE_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "SharedMCMField",
            "open(",
            "from pathlib",
            "production",
            "semantic_label",
        ):
            self.assertNotIn(forbidden, source)

    def test_decision_is_narrow_and_all_execution_counters_are_zero(self) -> None:
        audit = load_audit()
        self.assertEqual(18, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual(
            "PASS_S1XF_STATIC_CLOSURE_REGISTERED_MATRIX_REMAINS_CLOSED",
            audit["decision"],
        )
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
