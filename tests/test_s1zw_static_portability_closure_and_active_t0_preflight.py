from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / "S1ZW_STATISCHER_PORTABILITAETSABSCHLUSS_UND_AKTIVER_T0_PREFLIGHT_V1.json"
_BOUND = {
    "s1zv_finding": _ROOT / "docs" / "S1ZV_ENGE_ROHBYTE_PORTABILITAETSIMPLEMENTIERUNG_UND_FOKUSSIERTER_ABNAHMEBEFUND_V1.json",
    "s1zv_document": _ROOT / "docs" / "S1ZV_ENGE_ROHBYTE_PORTABILITAETSIMPLEMENTIERUNG_UND_FOKUSSIERTER_ABNAHMEBEFUND.md",
    "s1zv_receipt_test": _ROOT / "tests" / "test_s1zv_narrow_raw_byte_portability_implementation_receipt.py",
    "gitattributes": _ROOT / ".gitattributes",
}


def _contract() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


class S1ZWStaticPortabilityClosureAndActiveT0PreflightTests(unittest.TestCase):
    def test_contract_digest_and_parent_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), contract["bound_source_digests"][role])

    def test_six_module_digests_and_46_tests_are_exact(self) -> None:
        total = 0
        for record in _contract()["t0_modules"]:
            path = _ROOT / (record["module"].replace(".", "/") + ".py")
            self.assertEqual(record["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            count = sum(isinstance(node, ast.FunctionDef) and node.name.startswith("test_") for node in ast.walk(tree))
            self.assertEqual(record["test_count"], count)
            total += count
        self.assertEqual(46, total)

    def test_runtime_prerequisites_are_available_without_optional_tiers(self) -> None:
        environment = _contract()["preflight_environment"]
        self.assertEqual(environment["numpy_available"], importlib.util.find_spec("numpy") is not None)
        self.assertEqual(environment["cv2_available"], importlib.util.find_spec("cv2") is not None)
        self.assertFalse(environment["pytest_required"])
        self.assertFalse(environment["pyav_required"])

    def test_command_and_execution_boundary_are_fail_closed(self) -> None:
        contract = _contract()
        command = contract["exact_command"]
        self.assertEqual([item["module"] for item in contract["t0_modules"]], command[3:])
        self.assertEqual(["python", "-m", "unittest"], command[:3])
        rules = contract["execution_rules"]
        self.assertTrue(rules["single_execution_only"])
        self.assertFalse(rules["retry_in_same_step_allowed"])
        self.assertFalse(rules["repair_in_same_step_allowed"])
        self.assertFalse(rules["broad_discovery_allowed"])

    def test_s1zw_contains_no_execution_or_result_claim(self) -> None:
        contract = _contract()
        self.assertTrue(all(value is False for value in contract["audit_execution"].values()))
        self.assertIn("NO_T0_RESULT", contract["claim_boundary"])
        self.assertEqual("S1ZX_EXECUTE_EXACT_T0_COMMAND_ONCE_CAPTURE_RESULT_NO_RETRY_OR_REPAIR", contract["next_step"])


if __name__ == "__main__":
    unittest.main()
