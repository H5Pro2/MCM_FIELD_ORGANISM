from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / "S1ZR_W1F_DREI_ASSET_EOL_IMPLEMENTIERUNG_UND_SYNTHETISCHER_ABNAHMEBEFUND_V1.json"
_BOUND_SOURCES = {
    "gitattributes": _ROOT / ".gitattributes",
    "s1zp_tests_after_authorized_implementation": _ROOT / "tests" / "test_s1zp_w1f_static_asset_and_expectation_binding_audit.py",
    "s1zq_tests_after_authorized_implementation": _ROOT / "tests" / "test_s1zq_w1f_static_three_asset_eol_correction_contract.py",
    "browser_payload_smoke": _ROOT / "mcm_field_organism" / "browser_payload_smoke.py",
    "browser_payload_source": _ROOT / "mcm_field_organism" / "browser_payload_source.py",
    "browser_payload_smoke_tests": _ROOT / "tests" / "test_browser_payload_smoke.py",
    "browser_payload_source_tests": _ROOT / "tests" / "test_browser_payload_source.py",
    "s1zq_contract": _ROOT / "docs" / "S1ZQ_W1F_STATISCHER_DREI_ASSET_EOL_KORREKTURVERTRAG_V1.json",
}


def _finding() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _w1f_assets() -> dict[str, str]:
    path = _BOUND_SOURCES["browser_payload_smoke"]
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "_W1F_ASSET_DIGESTS"
            for target in node.targets
        ):
            return dict(ast.literal_eval(node.value))
    raise AssertionError("W1-F asset binding is absent")


class S1ZRW1FEOLImplementationReceiptTests(unittest.TestCase):
    def test_finding_digest_and_bound_sources_are_exact(self) -> None:
        finding = _finding()
        self.assertEqual(_canonical_digest(finding), finding["artifact_digest"])
        for role, path in _BOUND_SOURCES.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                finding["bound_source_digests"][role],
            )

    def test_exact_attribute_rules_are_the_only_implemented_rules(self) -> None:
        finding = _finding()
        lines = (_ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertEqual(finding["implemented_gitattributes_lines"], lines)
        self.assertEqual(3, len(lines))

    def test_raw_worktree_git_blob_and_w1f_digests_are_identical(self) -> None:
        expected = _w1f_assets()
        for record in _finding()["asset_results"]:
            path = record["path"]
            raw = (_ROOT / path).read_bytes()
            blob = subprocess.check_output(["git", "cat-file", "blob", f"HEAD:{path}"], cwd=_ROOT)
            digest = hashlib.sha256(raw).hexdigest()
            self.assertEqual(raw, blob)
            self.assertEqual(expected[Path(path).name], digest)
            self.assertEqual(
                {record["raw_worktree_sha256"], record["git_blob_sha256"], record["w1f_expected_sha256"]},
                {digest},
            )

    def test_git_attributes_and_zero_asset_content_diff_are_exact(self) -> None:
        for record in _finding()["asset_results"]:
            path = record["path"]
            observed = subprocess.check_output(
                ["git", "check-attr", "text", "eol", "--", path], cwd=_ROOT, text=True
            )
            self.assertIn(f"{path}: text: set", observed)
            self.assertIn(f"{path}: eol: lf", observed)
            diff = subprocess.check_output(["git", "diff", "HEAD", "--", path], cwd=_ROOT)
            self.assertEqual(b"", diff)

    def test_test_result_and_claim_boundary_are_narrow(self) -> None:
        finding = _finding()
        results = finding["test_results"]
        self.assertEqual((10, 0), (results["static_gate_test_count"], results["static_gate_failure_count"]))
        self.assertEqual(
            (14, 0),
            (results["synthetic_source_and_fake_smoke_test_count"], results["synthetic_failure_count"]),
        )
        self.assertFalse(results["real_browser_used"])
        boundary = finding["change_boundary"]
        self.assertTrue(all(value is False for key, value in boundary.items() if key != "effective_gitattributes_rule_count"))
        self.assertEqual(3, boundary["effective_gitattributes_rule_count"])


if __name__ == "__main__":
    unittest.main()

