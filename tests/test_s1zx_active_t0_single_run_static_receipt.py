from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / "S1ZX_AKTIVER_T0_EINMALLAUF_UND_TECHNISCHER_ERGEBNISBEFUND_V1.json"
_BOUND = {
    "s1zw_contract": _ROOT / "docs" / "S1ZW_STATISCHER_PORTABILITAETSABSCHLUSS_UND_AKTIVER_T0_PREFLIGHT_V1.json",
    "s1zw_document": _ROOT / "docs" / "S1ZW_STATISCHER_PORTABILITAETSABSCHLUSS_UND_AKTIVER_T0_PREFLIGHT.md",
    "s1zw_receipt_test": _ROOT / "tests" / "test_s1zw_static_portability_closure_and_active_t0_preflight.py",
}


def _finding() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


class S1ZXActiveT0SingleRunStaticReceiptTests(unittest.TestCase):
    def test_finding_digest_and_preflight_sources_are_exact(self) -> None:
        finding = _finding()
        self.assertEqual(_canonical_digest(finding), finding["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), finding["bound_source_digests"][role])

    def test_exact_command_remains_the_six_module_t0_command(self) -> None:
        command = _finding()["exact_command"]
        self.assertEqual(["python", "-m", "unittest"], command[:3])
        self.assertEqual(6, len(command[3:]))
        self.assertNotIn("discover", command)

    def test_single_run_result_is_exact_and_green(self) -> None:
        result = _finding()["result"]
        self.assertEqual((1, 46, 0, 0, 0, 0), (result["execution_count"], result["test_count"], result["failure_count"], result["error_count"], result["skipped_count"], result["exit_code"]))
        self.assertEqual((0, 0, 0), (result["retry_count"], result["repair_count"], result["post_execution_tracked_diff_count"]))

    def test_execution_boundary_excludes_real_and_broad_paths(self) -> None:
        boundary = _finding()["observed_execution_boundary"]
        forbidden = ("real_browser_used", "network_used", "production_persistence_used", "closed_history_tier_executed", "private_engineering_tier_executed", "optional_dependency_tier_executed", "broad_discovery_executed")
        self.assertTrue(all(boundary[key] is False for key in forbidden))

    def test_claim_and_next_step_remain_narrow(self) -> None:
        finding = _finding()
        self.assertIn("NO_REAL_FIELD_RESEARCH_OR_MEMORY_RESULT", finding["claim_boundary"])
        self.assertEqual("S1ZY_STATIC_T0_RESULT_CLOSURE_AND_EXACT_NEXT_ACTIVE_REGRESSION_SCOPE_SELECTION_NO_EXECUTION", finding["next_step"])
        self.assertFalse(finding["static_receipt_verification"]["t0_reexecuted"])


if __name__ == "__main__":
    unittest.main()
