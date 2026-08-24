from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / "S2AD_AKTIVER_T0C_BROWSER_REZEPTOR_EINMALLAUF_UND_LAUFZEITKLASSIFIKATION_V1.json"
_BOUND = {
    "s2ac_contract": _ROOT / "docs" / "S2AC_STATISCHER_T0B_ABSCHLUSS_UND_AUSWAHL_DES_KONTROLLIERTEN_BROWSER_REZEPTOR_GATES_V1.json",
    "s2ac_document": _ROOT / "docs" / "S2AC_STATISCHER_T0B_ABSCHLUSS_UND_AUSWAHL_DES_KONTROLLIERTEN_BROWSER_REZEPTOR_GATES.md",
    "s2ac_receipt_test": _ROOT / "tests" / "test_s2ac_static_t0b_closure_and_controlled_browser_gate_selection.py",
}


def _finding() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


class S2ADActiveT0CBrowserReceptorStaticReceiptTests(unittest.TestCase):
    def test_finding_digest_and_selection_sources_are_exact(self) -> None:
        finding = _finding()
        self.assertEqual(_canonical_digest(finding), finding["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), finding["bound_source_digests"][role])

    def test_parent_exact_command_digest_is_bound(self) -> None:
        parent = json.loads(_BOUND["s2ac_contract"].read_text(encoding="utf-8"))
        encoded = json.dumps(parent["exact_command"], ensure_ascii=True, separators=(",", ":")).encode("ascii")
        binding = _finding()["command_binding"]
        self.assertEqual(binding["canonical_json_sha256"], hashlib.sha256(encoded).hexdigest())
        self.assertEqual(binding["argument_count"], len(parent["exact_command"]))

    def test_single_run_result_is_exact_and_green(self) -> None:
        result = _finding()["result"]
        self.assertEqual((1, 32, 0, 0, 0, 0), (result["execution_count"], result["test_count"], result["failure_count"], result["error_count"], result["skipped_count"], result["exit_code"]))
        self.assertEqual((0, 0, 0), (result["retry_count"], result["repair_count"], result["post_execution_tracked_diff_count"]))

    def test_runtime_is_classified_by_the_preregistered_limit(self) -> None:
        runtime = _finding()["runtime_classification"]
        self.assertLessEqual(runtime["measured_wall_seconds"], runtime["fast_gate_max_wall_seconds"])
        self.assertTrue(runtime["within_fast_gate_limit"])
        self.assertEqual("T0C_ACTIVE_FAST_CONTROLLED_BROWSER_BOUNDARY", runtime["classification"])

    def test_claim_and_execution_boundary_remain_narrow(self) -> None:
        finding = _finding()
        boundary = finding["observed_execution_boundary"]
        forbidden = ("real_browser_used", "installed_playwright_runtime_used", "network_used", "production_persistence_used", "raw_payload_retained", "closed_candidate_activated", "private_memory_engineering_executed", "excluded_timing_methods_executed", "broad_discovery_executed")
        self.assertTrue(all(boundary[key] is False for key in forbidden))
        self.assertIn("NO_REAL_BROWSER_PERCEPTION_RESEARCH_OR_MEMORY_RESULT", finding["claim_boundary"])
        self.assertFalse(finding["static_receipt_verification"]["t0c_reexecuted"])


if __name__ == "__main__":
    unittest.main()
