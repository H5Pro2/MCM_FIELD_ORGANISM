from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / "S1ZZ_AKTIVER_T0A_REZEPTOR_FELD_INTEGRATIONSEINMALLAUF_UND_LAUFZEITKLASSIFIKATION_V1.json"
_BOUND = {
    "s1zy_contract": _ROOT / "docs" / "S1ZY_STATISCHER_T0_ABSCHLUSS_UND_AUSWAHL_DES_AKTIVEN_REZEPTOR_FELD_INTEGRATIONSGATES_V1.json",
    "s1zy_document": _ROOT / "docs" / "S1ZY_STATISCHER_T0_ABSCHLUSS_UND_AUSWAHL_DES_AKTIVEN_REZEPTOR_FELD_INTEGRATIONSGATES.md",
    "s1zy_receipt_test": _ROOT / "tests" / "test_s1zy_static_t0_closure_and_active_receptor_field_gate_selection.py",
}


def _finding() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


class S1ZZActiveT0AReceptorFieldIntegrationStaticReceiptTests(unittest.TestCase):
    def test_finding_digest_and_selection_sources_are_exact(self) -> None:
        finding = _finding()
        self.assertEqual(_canonical_digest(finding), finding["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), finding["bound_source_digests"][role])

    def test_exact_command_remains_the_nine_module_scope(self) -> None:
        command = _finding()["exact_command"]
        self.assertEqual(["python", "-m", "unittest"], command[:3])
        self.assertEqual(9, len(command[3:]))
        self.assertNotIn("discover", command)

    def test_single_run_result_is_exact_and_green(self) -> None:
        result = _finding()["result"]
        self.assertEqual((1, 66, 0, 0, 0, 0), (result["execution_count"], result["test_count"], result["failure_count"], result["error_count"], result["skipped_count"], result["exit_code"]))
        self.assertEqual((0, 0, 0), (result["retry_count"], result["repair_count"], result["post_execution_tracked_diff_count"]))

    def test_runtime_is_classified_by_the_preregistered_limit(self) -> None:
        runtime = _finding()["runtime_classification"]
        self.assertLessEqual(runtime["measured_wall_seconds"], runtime["fast_gate_max_wall_seconds"])
        self.assertTrue(runtime["within_fast_gate_limit"])
        self.assertEqual("T0A_ACTIVE_FAST_INTEGRATION", runtime["classification"])

    def test_claim_and_execution_boundary_remain_narrow(self) -> None:
        finding = _finding()
        boundary = finding["observed_execution_boundary"]
        forbidden = ("real_audio_video_hardware_used", "real_browser_used", "network_used", "filesystem_persistence_used", "closed_candidate_activated", "private_memory_engineering_executed", "broad_discovery_executed")
        self.assertTrue(all(boundary[key] is False for key in forbidden))
        self.assertIn("NO_REAL_SENSOR_RESEARCH_OR_MEMORY_RESULT", finding["claim_boundary"])
        self.assertFalse(finding["static_receipt_verification"]["t0a_reexecuted"])


if __name__ == "__main__":
    unittest.main()
