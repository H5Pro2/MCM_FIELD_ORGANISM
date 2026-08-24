from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / "S2AC_STATISCHER_T0B_ABSCHLUSS_UND_AUSWAHL_DES_KONTROLLIERTEN_BROWSER_REZEPTOR_GATES_V1.json"
_BOUND = {
    "s2ab_result": _ROOT / "docs" / "S2AB_AKTIVER_T0B_TEMPORALER_UEBERGABEEINMALLAUF_UND_LAUFZEITKLASSIFIKATION_V1.json",
    "s2ab_document": _ROOT / "docs" / "S2AB_AKTIVER_T0B_TEMPORALER_UEBERGABEEINMALLAUF_UND_LAUFZEITKLASSIFIKATION.md",
    "s2ab_receipt_test": _ROOT / "tests" / "test_s2ab_active_t0b_temporal_handoff_static_receipt.py",
}


def _contract() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


class S2ACStaticT0BClosureAndControlledBrowserGateSelectionTests(unittest.TestCase):
    def test_contract_digest_and_parent_result_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), contract["bound_source_digests"][role])

    def test_four_sources_bind_exactly_32_selected_tests(self) -> None:
        contract = _contract()
        total = sum(item["selected_test_count"] for item in contract["selected_module_sources"])
        self.assertEqual(32, total)
        for record in contract["selected_module_sources"]:
            path = _ROOT / (record["module"].replace(".", "/") + ".py")
            self.assertEqual(record["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        timing_path = _ROOT / "tests" / "test_browser_payload_timing_pair.py"
        tree = ast.parse(timing_path.read_text(encoding="utf-8"), filename=str(timing_path))
        methods = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")}
        selected = set(contract["selected_timing_pair_methods"])
        excluded = set(contract["excluded_previously_executed_timing_pair_methods"])
        self.assertEqual(methods, selected | excluded)
        self.assertTrue(selected.isdisjoint(excluded))

    def test_exact_command_contains_three_modules_and_19_method_ids(self) -> None:
        contract = _contract()
        command = contract["exact_command"]
        self.assertEqual(["python", "-m", "unittest"], command[:3])
        self.assertEqual(22, len(command[3:]))
        prefix = contract["timing_pair_test_class"] + "."
        self.assertEqual([prefix + method for method in contract["selected_timing_pair_methods"]], command[6:])
        self.assertNotIn("discover", command)

    def test_scope_excludes_real_external_closed_and_private_paths(self) -> None:
        boundary = _contract()["scope_boundary"]
        forbidden = ("installed_playwright_runtime_required", "real_browser", "network", "production_persistence", "raw_payload_retention", "closed_candidate_activation", "private_memory_engineering")
        self.assertTrue(all(boundary[key] is False for key in forbidden))

    def test_selection_is_static_and_next_execution_is_fail_closed(self) -> None:
        contract = _contract()
        self.assertTrue(all(value is False for value in contract["audit_execution"].values()))
        self.assertFalse(contract["execution_rules"]["retry_in_same_step_allowed"])
        self.assertFalse(contract["execution_rules"]["excluded_timing_test_reexecution_allowed"])
        self.assertEqual("S2AD_EXECUTE_EXACT_32_TEST_T0C_SCOPE_ONCE_MEASURE_AND_CLASSIFY_NO_RETRY_OR_REPAIR", contract["next_step"])


if __name__ == "__main__":
    unittest.main()
