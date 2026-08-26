from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1XP_PPB1_STATISCHER_MARGIN_FIXTURE_IMPLEMENTIERUNGSABSCHLUSSAUDIT_V1.json"
SOURCE_PATH = ROOT / "mcm_field_organism/_ppb1_s1xo_private_numeric_margin_fixture.py"
EXPECTED_AUDIT_DIGEST = (
    "50222511f3675374b782caa5d1ca126280ada46d8a3d77f871e93bdcf2638da8"
)


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def source_tree() -> ast.Module:
    return ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))


class PPB1S1XPStaticMarginFixtureClosureAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        self.assertEqual(EXPECTED_AUDIT_DIGEST, canonical_digest(load_audit()))

    def test_parent_contract_and_all_bound_files_are_exact(self) -> None:
        audit = load_audit()
        parent_path = ROOT / "docs/S1XN_PPB1_STATISCHER_ENGINEERING_UND_NUMERISCHER_FIXTURE_KORREKTURVERTRAG_V1.json"
        parent = json.loads(parent_path.read_text(encoding="utf-8"))
        self.assertEqual(audit["parent_s1xn_contract_digest"], canonical_digest(parent))
        paths = {
            "s1xo_source": "mcm_field_organism/_ppb1_s1xo_private_numeric_margin_fixture.py",
            "s1xo_tests": "tests/test_ppb1_s1xo_private_numeric_margin_fixture.py",
            "s1xo_document": "docs/S1XO_PPB1_PRIVATE_NUMERISCHE_MARGIN_FIXTURE_UND_VALIDATOR.md",
            "s1xn_contract_file": "docs/S1XN_PPB1_STATISCHER_ENGINEERING_UND_NUMERISCHER_FIXTURE_KORREKTURVERTRAG_V1.json",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1xc_historical_fixture_registry": "mcm_field_organism/_ppb1_s1xc_fixture_registry.py",
            "s1xi_historical_full_runner": "mcm_field_organism/_ppb1_s1xi_private_full_runner.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                audit["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_source_imports_only_bound_reference_helpers(self) -> None:
        imports = [
            node
            for node in source_tree().body
            if isinstance(node, ast.ImportFrom) and node.level == 1
        ]
        self.assertEqual(1, len(imports))
        reference = imports[0]
        self.assertEqual("_ppb1_reference", reference.module)
        self.assertEqual(
            {"_digest", "normalized_mean_l1_distance"},
            {item.name for item in reference.names},
        )
        self.assertIn(
            load_audit()["parent_s1xn_contract_digest"],
            SOURCE_PATH.read_text(encoding="utf-8"),
        )

    def test_numeric_specs_classes_mask_and_margins_are_exact(self) -> None:
        assignments = {
            target.id: node.value
            for node in source_tree().body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
            and target.id
            in {"S1XO_PROBE_CLASSES", "S1XO_EXPECTED_MASK", "S1XO_MODALITY_SPECS"}
        }
        classes = ast.literal_eval(assignments["S1XO_PROBE_CLASSES"])
        mask = ast.literal_eval(assignments["S1XO_EXPECTED_MASK"])
        specs = ast.literal_eval(assignments["S1XO_MODALITY_SPECS"])
        audit = load_audit()["numeric_fixture_audit"]
        self.assertEqual(5, len(classes))
        self.assertEqual(tuple(audit["expected_recognition_mask"]), mask)
        for modality in ("auditory", "visual"):
            self.assertEqual(audit[modality]["carrier_count"], specs[modality]["carrier_count"])
            self.assertEqual(audit[modality]["threshold"], specs[modality]["threshold"])
            self.assertEqual(tuple(audit[modality]["probe_values"]), specs[modality]["probe_values"])
            self.assertEqual(audit[modality]["minimum_margin"], specs[modality]["minimum_margin"])
            self.assertNotIn(specs[modality]["threshold"], specs[modality]["probe_values"])

    def test_validator_recomputes_metric_and_fails_closed_on_class_and_margin(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8")
        self.assertIn("recomputed = normalized_mean_l1_distance(", source)
        self.assertIn("measured != recomputed or measured != scalar", source)
        self.assertIn("(measured <= threshold) is not expected", source)
        self.assertIn("abs(measured - threshold) < minimum_margin", source)
        self.assertIn("measured == threshold", source)

    def test_operator_cases_bind_nextafter_below_equal_above_and_less_equal(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8")
        self.assertIn('"below": math.nextafter(threshold, -math.inf)', source)
        self.assertIn('"equal": threshold', source)
        self.assertIn('"above": math.nextafter(threshold, math.inf)', source)
        self.assertIn("distance <= threshold", source)

    def test_three_frozen_slotted_types_have_exact_roles(self) -> None:
        expected = {
            "S1XOModalityNumericFixture": 9,
            "S1XOThresholdOperatorCase": 6,
            "S1XONumericMarginFixtureBundle": 3,
        }
        classes = {
            node.name: node for node in source_tree().body if isinstance(node, ast.ClassDef)
        }
        for name, role_count in expected.items():
            kind = classes[name]
            self.assertEqual(
                role_count,
                len([node for node in kind.body if isinstance(node, ast.AnnAssign)]),
            )
            decorator = next(
                item
                for item in kind.decorator_list
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

    def test_tests_and_bundle_receipt_are_source_bound(self) -> None:
        test_source = (
            ROOT / "tests/test_ppb1_s1xo_private_numeric_margin_fixture.py"
        ).read_text(encoding="utf-8")
        test_tree = ast.parse(test_source)
        methods = [
            node
            for node in ast.walk(test_tree)
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        self.assertEqual(11, len(methods))
        self.assertIn(load_audit()["bound_technical_fixture"]["bundle_digest"], test_source)

    def test_state_probe_runner_field_file_and_production_paths_are_absent(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8")
        for forbidden in (
            "initial_ppb1_bank_state",
            "advance_ppb1_bank",
            "probe_s1wu_perceptual_state",
            "materialize_s1xc_fixture_registry",
            "run_s1xi_registered_matrix",
            "SharedMCMField",
            "open(",
            "write_text(",
            "production_adapter",
            "production_coordinator",
            "run_production",
        ):
            self.assertNotIn(forbidden, source)

    def test_s1xo_is_private_and_historical_sources_remain_exact(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            self.assertNotIn("s1xo", (ROOT / relative).read_text(encoding="utf-8").lower())
        audit = load_audit()
        for role, relative in (
            ("s1xc_historical_fixture_registry", "mcm_field_organism/_ppb1_s1xc_fixture_registry.py"),
            ("s1xi_historical_full_runner", "mcm_field_organism/_ppb1_s1xi_private_full_runner.py"),
        ):
            self.assertEqual(
                audit["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_decision_is_narrow_and_all_execution_counters_are_zero(self) -> None:
        audit = load_audit()
        self.assertEqual(18, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual(
            "PASS_S1XO_STATIC_CLOSURE_PRIVATE_NUMERIC_MARGIN_FIXTURE_VALID",
            audit["decision"],
        )
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
