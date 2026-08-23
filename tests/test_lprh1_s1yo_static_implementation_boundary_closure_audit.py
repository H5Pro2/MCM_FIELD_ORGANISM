from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "docs/S1YO_LPRH1_STATISCHER_IMPLEMENTIERUNGS_UND_GRENZENABSCHLUSSAUDIT_V1.json"
IMPLEMENTATION_PATH = ROOT / "mcm_field_organism/_lprh1_s1yn_private_local_handoff.py"
TEST_PATH = ROOT / "tests/test_lprh1_s1yn_private_local_handoff.py"
S1YN_PATH = ROOT / "docs/S1YN_LPRH1_PRIVATE_REINE_HANDOFF_IMPLEMENTIERUNG_V1.json"
S1YI_PATH = ROOT / "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json"
EXPECTED_AUDIT_DIGEST = "fce519ef762a46e7751a8616aac5c3e71563eaf9e0f4698eba71e5f2a28511c4"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_tree(path: Path) -> tuple[str, ast.Module]:
    source = path.read_text(encoding="utf-8")
    return source, ast.parse(source)


class LPRH1S1YOStaticImplementationBoundaryClosureAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(AUDIT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load(AUDIT_PATH)
        self.assertEqual("205dd293331c06f58685498cd151e5bb75f72aac1cde89584bbe930f29ab6083", audit["parent_s1yn_canonical_implementation_digest"])
        paths = {
            "s1yn_implementation_record": "docs/S1YN_LPRH1_PRIVATE_REINE_HANDOFF_IMPLEMENTIERUNG_V1.json",
            "s1yn_document": "docs/S1YN_LPRH1_PRIVATE_REINE_HANDOFF_IMPLEMENTIERUNG.md",
            "private_handoff_module": "mcm_field_organism/_lprh1_s1yn_private_local_handoff.py",
            "synthetic_contract_tests": "tests/test_lprh1_s1yn_private_local_handoff.py",
            "s1ym_erratum": "docs/S1YM_LPRH1_STATISCHES_PRAEIMPLEMENTIERUNGSERRATUM_V1.json",
            "s1yk_contract": "docs/S1YK_LPRH1_STATISCHER_FINALER_IMPLEMENTIERUNGSBINDUNGSKORREKTURVERTRAG_V1.json",
            "s1yi_contract": "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(audit["bound_file_digests"][role], actual)

    def test_six_private_output_dataclasses_are_frozen_and_slotted(self) -> None:
        _, tree = source_tree(IMPLEMENTATION_PATH)
        expected = set(load(S1YI_PATH)["exact_type_schemas"])
        classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
        self.assertEqual(expected, expected & set(classes))
        for name in expected:
            decorators = [node for node in classes[name].decorator_list if isinstance(node, ast.Call)]
            self.assertEqual(1, len(decorators))
            keywords = {item.arg: item.value for item in decorators[0].keywords}
            self.assertIsInstance(keywords["frozen"], ast.Constant)
            self.assertTrue(keywords["frozen"].value)
            self.assertIsInstance(keywords["slots"], ast.Constant)
            self.assertTrue(keywords["slots"].value)

    def test_pure_function_has_exact_nine_input_roles(self) -> None:
        _, tree = source_tree(IMPLEMENTATION_PATH)
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "materialize_lprh1_local_handoff")
        self.assertEqual(
            ["execution_id", "config", "state", "finding", "timed_probe", "target_step", "shared_dock", "receptor_input_set", "consumed_handoff_ids"],
            [item.arg for item in function.args.args],
        )

    def test_error_set_and_precedence_are_statically_present(self) -> None:
        source, tree = source_tree(IMPLEMENTATION_PATH)
        expected = set(load(S1YI_PATH)["finite_error_codes"])
        assigned = {
            node.targets[0].id
            for node in tree.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id.startswith("LPRH1_")
            and node.targets[0].id != "LPRH1_SCHEMA_VERSION"
        }
        self.assertEqual(expected, assigned)
        function_start = source.index("def materialize_lprh1_local_handoff")
        function_source = source[function_start:]
        ordered = [
            "LPRH1_INVALID_INPUT",
            "LPRH1_PROVENANCE_MISMATCH",
            "LPRH1_CAUSAL_TIME_MISMATCH",
            "LPRH1_LOCAL_MAPPING_MISMATCH",
            "LPRH1_DUPLICATE_HANDOFF",
            "LPRH1_SLOT_NOT_STABLE",
        ]
        positions = [function_source.index(item) for item in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_context_has_nine_foreign_and_one_own_digest_role(self) -> None:
        schema = load(S1YI_PATH)["exact_type_schemas"]["LPRH1TransientLocalPrototypeContext"]
        digests = [item for item in schema if item.endswith("_digest_str")]
        self.assertEqual(10, len(digests))
        self.assertEqual(9, len([item for item in digests if item != "context_digest_str"]))
        source = IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        self.assertIn("one of nine foreign digests is invalid", source)
        self.assertIn("context digest does not bind the canonical payload", source)

    def test_forbidden_runtime_calls_and_side_effect_imports_are_absent(self) -> None:
        _, tree = source_tree(IMPLEMENTATION_PATH)
        called_names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue({"advance_ppb1_bank", "probe_s1wu_perceptual_state", "advance_shared_mcm_field"}.isdisjoint(called_names))
        imported_roots = {
            alias.name.split(".")[0]
            for node in tree.body
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        self.assertTrue({"os", "pathlib", "socket", "subprocess", "urllib"}.isdisjoint(imported_roots))

    def test_nine_synthetic_tests_are_bound_but_not_run_here(self) -> None:
        _, tree = source_tree(TEST_PATH)
        methods = [
            node
            for item in tree.body
            if isinstance(item, ast.ClassDef)
            for node in item.body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]
        self.assertEqual(9, len(methods))
        result = load(S1YN_PATH)["synthetic_test_result"]
        self.assertEqual(9, result["test_count"])
        self.assertEqual(9, result["passed_count"])
        self.assertEqual(0, result["failed_count"])

    def test_public_surfaces_remain_without_lprh1(self) -> None:
        for relative in ("mcm_field_organism/__init__.py", "mcm_field_organism/current_api.py", "mcm_field_organism/root_lazy_exports.py"):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yn", source)
            self.assertNotIn("lprh", source)

    def test_all_twenty_four_roles_pass_without_execution(self) -> None:
        audit = load(AUDIT_PATH)
        results = audit["audit_results"]
        self.assertEqual(24, len(results))
        self.assertTrue(all(value for key, value in results.items() if key != "new_implementation_blocker_found"))
        self.assertFalse(results["new_implementation_blocker_found"])
        self.assertEqual(24, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
