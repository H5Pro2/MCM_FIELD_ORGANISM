from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1YC_PPB1_STATISCHER_RUNNER_UND_ERGEBNISABSCHLUSSAUDIT_V1.json"
SOURCE_PATH = ROOT / "mcm_field_organism/_ppb1_s1yb_private_temporal_update_runner.py"
EXPECTED_AUDIT_DIGEST = "31467bcb43e00bee39b0930380ee39868c1534a94dbed7b910973b71c41222fa"


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


class PPB1S1YCStaticRunnerResultClosureAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_all_source_dependency_and_surface_hashes_are_exact(self) -> None:
        paths = {
            "s1yb_runner": "mcm_field_organism/_ppb1_s1yb_private_temporal_update_runner.py",
            "s1yb_tests": "tests/test_ppb1_s1yb_private_temporal_update_runner.py",
            "s1yb_document": "docs/S1YB_PPB1_PRIVATER_ZEITLICHER_AKTUALISIERUNGSVERGLEICH.md",
            "s1xz_fixture": "mcm_field_organism/_ppb1_s1xz_private_temporal_update_fixture.py",
            "s1ya_baseline": "mcm_field_organism/_ppb1_s1ya_private_static_prototype_baseline.py",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wq_lifecycle": "mcm_field_organism/_ppb1_s1wq_perceptual_state_lifecycle.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(load_audit()["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_preflight_fixture_and_single_builder_call_are_static(self) -> None:
        source = source_text()
        self.assertIn(load_audit()["parent_s1xy_preflight_digest"], source)
        self.assertIn(load_audit()["fixture_bundle_digest"], source)
        runner = function_node("run_s1yb_private_temporal_update_comparison")
        calls = [node for node in ast.walk(runner) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "build_s1xz_temporal_update_fixture"]
        self.assertEqual(1, len(calls))

    def test_history_order_is_fixture_order_and_all_ten_are_aggregated(self) -> None:
        runner = ast.get_source_segment(source_text(), function_node("run_s1yb_private_temporal_update_comparison"))
        assert runner is not None
        self.assertIn("for plan in fixture.history_plans", runner)
        self.assertIn("len(self.ordered_history_receipt_digests) != 10", source_text())

    def test_formation_precomparison_update_terminal_and_probe_order_is_exact(self) -> None:
        history = ast.get_source_segment(source_text(), function_node("_run_history"))
        assert history is not None
        positions = [
            history.index("for index, role in enumerate(plan.formation_roles)"),
            history.index("baseline = form_s1ya_static_baseline"),
            history.index("preupdate_equal ="),
            history.index("for offset, role in enumerate(plan.update_roles)"),
            history.index("candidate_terminal_digest ="),
            history.index("for index, role in enumerate(plan.ordered_probe_roles)"),
        ]
        self.assertEqual(positions, sorted(positions))

    def test_each_update_pairs_candidate_transition_and_frozen_handoff(self) -> None:
        node = function_node("_run_history")
        loop = next(item for item in ast.walk(node) if isinstance(item, ast.For) and "plan.update_roles" in ast.unparse(item.iter))
        calls = {
            item.func.id
            for item in ast.walk(loop)
            if isinstance(item, ast.Call) and isinstance(item.func, ast.Name)
        }
        self.assertIn("advance_s1wq_perceptual_state", calls)
        self.assertIn("receive_s1ya_frozen_exposure", calls)

    def test_each_probe_pairs_two_read_only_calls_and_checks_state(self) -> None:
        node = function_node("_run_history")
        loop = next(item for item in ast.walk(node) if isinstance(item, ast.For) and "plan.ordered_probe_roles" in ast.unparse(item.iter))
        probe_calls = [item for item in ast.walk(loop) if isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == "probe_s1wu_perceptual_state"]
        segment = ast.get_source_segment(source_text(), loop)
        assert segment is not None
        self.assertEqual(2, len(probe_calls))
        self.assertIn("candidate_state.digest() == candidate_before", segment)
        self.assertIn("baseline_carry.frozen_state.digest() == baseline_before", segment)

    def test_baseline_probe_reuses_frozen_source_clock(self) -> None:
        helper = ast.get_source_segment(source_text(), function_node("_baseline_probe_frame"))
        assert helper is not None
        self.assertIn("carry.frozen_state.source_clock_id", helper)
        self.assertNotIn('"clock.s1yb.baseline', helper)

    def test_exact_call_budgets_are_source_bound_in_fourteen_tests(self) -> None:
        audit = load_audit()
        budget = audit["call_budget"]
        self.assertEqual((1, 10, 10, 64, 36, 28, 32, 32, 32, 0), tuple(budget.values()))
        test_source = (ROOT / "tests/test_ppb1_s1yb_private_temporal_update_runner.py").read_text(encoding="utf-8")
        test_tree = ast.parse(test_source)
        methods = [node for node in ast.walk(test_tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
        self.assertEqual(14, len(methods))
        for literal in ("self.assertEqual(64, candidate_advance.call_count)", "self.assertEqual(36, baseline_advance.call_count)", "self.assertEqual(28, frozen_handoff.call_count)", "self.assertEqual(64, probe.call_count)", "self.assertEqual(32, comparator.call_count)"):
            self.assertIn(literal, test_source)

    def test_mandatory_advantage_controls_and_relation_operator_are_exact(self) -> None:
        source = source_text()
        for pair in (("H2", "gradual_3"), ("H3", "conflict_b"), ("H4", "origin"), ("H4", "opposite_c"), ("H5", "gradual_3")):
            self.assertIn(f'(\"{pair[0]}\", \"{pair[1]}\")', source)
        for pair in (("H1", "conflict_b"), ("H2", "conflict_b"), ("H3", "opposite_c"), ("H4", "far_control"), ("H5", "conflict_b")):
            self.assertIn(f'(\"{pair[0]}\", \"{pair[1]}\")', source)
        relation = ast.get_source_segment(source, function_node("_relation"))
        assert relation is not None
        for forbidden in ("digest", "slot", "support", "identity"):
            self.assertNotIn(forbidden, relation.lower())

    def test_four_receipt_types_are_frozen_slotted_and_complete(self) -> None:
        expected = {"S1YBPairedProbeReceipt": 21, "S1YBHistoryReceipt": 22, "S1YBAggregateReceipt": 16, "S1YBRunResult": 3}
        classes = {node.name: node for node in source_tree().body if isinstance(node, ast.ClassDef)}
        for name, count in expected.items():
            self.assertEqual(count, len([item for item in classes[name].body if isinstance(item, ast.AnnAssign)]))
            decorator = next(item for item in classes[name].decorator_list if isinstance(item, ast.Call) and isinstance(item.func, ast.Name) and item.func.id == "dataclass")
            keywords = {item.arg: item.value.value for item in decorator.keywords if item.arg and isinstance(item.value, ast.Constant)}
            self.assertEqual({"frozen": True, "slots": True}, keywords)

    def test_technical_result_is_exactly_documented_and_test_bound(self) -> None:
        audit = load_audit()
        document = (ROOT / "docs/S1YB_PPB1_PRIVATER_ZEITLICHER_AKTUALISIERUNGSVERGLEICH.md").read_text(encoding="utf-8")
        tests = (ROOT / "tests/test_ppb1_s1yb_private_temporal_update_runner.py").read_text(encoding="utf-8")
        result = audit["bound_technical_result"]
        self.assertIn(result["decision"], document)
        self.assertIn(result["aggregate_receipt_digest"], document)
        self.assertIn(result["aggregate_receipt_digest"], tests)
        self.assertEqual((14, 4, 14, 10, 10), (result["strict_advantage_count"], result["diagnostic_loss_count"], result["tie_count"], result["mandatory_advantage_count"], result["negative_control_safe_count"]))

    def test_s1yb_is_private_and_forbidden_paths_are_absent(self) -> None:
        for relative in ("mcm_field_organism/__init__.py", "mcm_field_organism/current_api.py", "mcm_field_organism/root_lazy_exports.py"):
            public_source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yb", public_source)
            self.assertNotIn("run_s1yb_private_temporal_update_comparison", public_source)
        source = source_text()
        for forbidden in ("_ppb1_s1xc_fixture_registry", "_ppb1_s1xi_private_full_runner", "run_s1xi_registered_matrix", "SharedMCMField", "open(", "write_text(", "production_adapter", "semantic_label"):
            self.assertNotIn(forbidden, source)

    def test_decision_is_narrow_and_all_execution_counters_are_zero(self) -> None:
        audit = load_audit()
        self.assertEqual(24, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual("PASS_S1YB_STATIC_CLOSURE_SYNTHETIC_TEMPORAL_UPDATE_FUNCTION_ONLY", audit["decision"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
