from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / "S1ZV_ENGE_ROHBYTE_PORTABILITAETSIMPLEMENTIERUNG_UND_FOKUSSIERTER_ABNAHMEBEFUND_V1.json"
_BOUND = {
    "gitattributes": _ROOT / ".gitattributes",
    "s1zu_contract": _ROOT / "docs" / "S1ZU_STATISCHER_REGRESSIONSPARTITIONS_ABHAENGIGKEITS_UND_ROHBYTE_PORTABILITAETSVERTRAG_V1.json",
    "s1zu_document": _ROOT / "docs" / "S1ZU_STATISCHER_REGRESSIONSPARTITIONS_ABHAENGIGKEITS_UND_ROHBYTE_PORTABILITAETSVERTRAG.md",
    "s1zu_test_after_s1zv": _ROOT / "tests" / "test_s1zu_static_regression_partition_dependency_and_raw_byte_portability_contract.py",
    "canonical_pair_tests": _ROOT / "tests" / "test_browser_payload_timing_pair.py",
}


def _finding() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _reports() -> list[Path]:
    return sorted((_ROOT / "reports").rglob("*.json"))


class S1ZVNarrowRawBytePortabilityImplementationReceiptTests(unittest.TestCase):
    def test_finding_digest_and_bound_sources_are_exact(self) -> None:
        finding = _finding()
        self.assertEqual(_canonical_digest(finding), finding["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), finding["bound_source_digests"][role])

    def test_exact_seven_attribute_rules_are_bound(self) -> None:
        finding = _finding()
        lines = (_ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertEqual(finding["implemented_gitattributes_lines"], lines)
        self.assertEqual(7, len(lines))
        self.assertEqual(4, finding["implementation_result"]["new_effective_rule_count"])

    def test_all_reports_are_raw_byte_identical_to_git_blobs(self) -> None:
        reports = _reports()
        self.assertEqual(60, len(reports))
        manifest = []
        for path in reports:
            relative = path.relative_to(_ROOT).as_posix()
            raw = path.read_bytes()
            blob = subprocess.check_output(["git", "cat-file", "blob", f"HEAD:{relative}"], cwd=_ROOT)
            self.assertEqual(blob, raw, relative)
            manifest.append(f"{relative}:{hashlib.sha256(raw).hexdigest()}")
        digest = hashlib.sha256("\n".join(manifest).encode("utf-8")).hexdigest()
        self.assertEqual(_finding()["report_results"]["path_digest_manifest_sha256"], digest)

    def test_three_canonical_assets_match_git_and_bound_digests(self) -> None:
        for record in _finding()["canonical_asset_results"]:
            path = record["path"]
            raw = (_ROOT / path).read_bytes()
            blob = subprocess.check_output(["git", "cat-file", "blob", f"HEAD:{path}"], cwd=_ROOT)
            self.assertEqual(blob, raw)
            self.assertEqual(record["sha256"], hashlib.sha256(raw).hexdigest())

    def test_result_and_claim_boundary_remain_narrow(self) -> None:
        finding = _finding()
        self.assertEqual("PASS_NARROW_RAW_BYTE_PORTABILITY_IMPLEMENTED_FOCUSED_GATES_VALID", finding["decision"])
        self.assertFalse(finding["implementation_result"]["content_changed"])
        self.assertFalse(finding["implementation_result"]["broad_suite_executed"])
        self.assertFalse(finding["implementation_result"]["dependency_installed"])
        self.assertIn("NO_FIELD_OR_MEMORY_RESULT", finding["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
