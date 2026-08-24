from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / "S2AA_STATISCHER_AKTIVGATE_ABSCHLUSS_UND_AUSWAHL_DES_TEMPORALEN_UEBERGABEGATES_V1.json"
_BOUND = {
    "s1zz_result": _ROOT / "docs" / "S1ZZ_AKTIVER_T0A_REZEPTOR_FELD_INTEGRATIONSEINMALLAUF_UND_LAUFZEITKLASSIFIKATION_V1.json",
    "s1zz_document": _ROOT / "docs" / "S1ZZ_AKTIVER_T0A_REZEPTOR_FELD_INTEGRATIONSEINMALLAUF_UND_LAUFZEITKLASSIFIKATION.md",
    "s1zz_receipt_test": _ROOT / "tests" / "test_s1zz_active_t0a_receptor_field_integration_static_receipt.py",
}


def _contract() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


class S2AAStaticActiveGateClosureAndTemporalHandoffSelectionTests(unittest.TestCase):
    def test_contract_digest_and_parent_result_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), contract["bound_source_digests"][role])

    def test_nine_selected_modules_bind_exactly_53_tests(self) -> None:
        total = 0
        for record in _contract()["selected_modules"]:
            path = _ROOT / (record["module"].replace(".", "/") + ".py")
            self.assertEqual(record["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            count = sum(isinstance(node, ast.FunctionDef) and node.name.startswith("test_") for node in ast.walk(tree))
            self.assertEqual(record["test_count"], count)
            total += count
        self.assertEqual(53, total)

    def test_exact_command_contains_only_selected_modules(self) -> None:
        contract = _contract()
        command = contract["exact_command"]
        self.assertEqual(["python", "-m", "unittest"], command[:3])
        self.assertEqual([item["module"] for item in contract["selected_modules"]], command[3:])
        self.assertNotIn("discover", command)

    def test_scope_excludes_external_closed_and_private_paths(self) -> None:
        boundary = _contract()["scope_boundary"]
        forbidden = ("external_system_clock_as_field_cause", "real_audio_video_hardware", "real_browser", "network", "filesystem_persistence", "optional_pytest_or_pyav", "closed_candidate_activation", "private_memory_engineering", "research_characterization_matrix")
        self.assertTrue(all(boundary[key] is False for key in forbidden))

    def test_selection_is_static_and_next_execution_is_fail_closed(self) -> None:
        contract = _contract()
        self.assertTrue(all(value is False for value in contract["audit_execution"].values()))
        self.assertFalse(contract["execution_rules"]["retry_in_same_step_allowed"])
        self.assertFalse(contract["execution_rules"]["repair_in_same_step_allowed"])
        self.assertEqual("S2AB_EXECUTE_EXACT_53_TEST_T0B_SCOPE_ONCE_MEASURE_AND_CLASSIFY_NO_RETRY_OR_REPAIR", contract["next_step"])


if __name__ == "__main__":
    unittest.main()
