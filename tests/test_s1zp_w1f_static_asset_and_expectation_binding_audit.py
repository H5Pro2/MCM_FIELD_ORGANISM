from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / "S1ZP_W1F_STATISCHER_ASSET_UND_ERWARTUNGSBINDUNGSAUDIT_V1.json"
_SOURCE_PATHS = {
    "browser_payload_smoke": _ROOT / "mcm_field_organism" / "browser_payload_smoke.py",
    "browser_payload_source": _ROOT / "mcm_field_organism" / "browser_payload_source.py",
    "w1f_contract": _ROOT / "docs" / "W1F_VERTRAG_MINIMALER_REALER_BROWSER_PAYLOAD_SMOKE.md",
    "s1zo_artifact": _ROOT
    / "docs"
    / "S1ZO_STATISCHER_AKTIVKERN_PRIVATREFERENZ_UND_DRIFTKONSOLIDIERUNGSAUDIT_V1.json",
}


def _load_artifact() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    digest_payload = dict(payload)
    digest_payload.pop("artifact_digest")
    encoded = json.dumps(
        digest_payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _w1f_expected_assets() -> dict[str, str]:
    path = _SOURCE_PATHS["browser_payload_smoke"]
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "_W1F_ASSET_DIGESTS"
            for target in node.targets
        ):
            return dict(ast.literal_eval(node.value))
    raise AssertionError("_W1F_ASSET_DIGESTS is absent")


class S1ZPW1FStaticAssetAuditTests(unittest.TestCase):
    def test_artifact_and_bound_source_digests_are_exact(self) -> None:
        artifact = _load_artifact()
        self.assertEqual(_canonical_digest(artifact), artifact["artifact_digest"])
        for role, path in _SOURCE_PATHS.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                artifact["bound_source_digests"][role],
            )

    def test_w1f_expectations_equal_git_blobs(self) -> None:
        expected = _w1f_expected_assets()
        artifact = _load_artifact()
        for record in artifact["asset_records"]:
            relative = record["path"]
            blob = subprocess.check_output(["git", "cat-file", "blob", f"HEAD:{relative}"], cwd=_ROOT)
            blob_digest = hashlib.sha256(blob).hexdigest()
            name = Path(relative).name
            self.assertEqual(expected[name], record["w1f_expected_sha256"])
            self.assertEqual(expected[name], blob_digest)
            self.assertEqual(blob_digest, record["git_blob_sha256"])

    def test_worktree_difference_is_only_line_endings(self) -> None:
        artifact = _load_artifact()
        for record in artifact["asset_records"]:
            worktree = (_ROOT / record["path"]).read_bytes()
            blob = subprocess.check_output(
                ["git", "cat-file", "blob", f"HEAD:{record['path']}"], cwd=_ROOT
            )
            self.assertEqual(blob, worktree.replace(b"\r\n", b"\n"))
            self.assertTrue(record["lf_normalized_equals_git_blob"])
            if b"\r\n" in worktree:
                self.assertEqual(record["observed_crlf_count"], worktree.count(b"\r\n"))
                self.assertEqual(
                    record["observed_windows_worktree_sha256"],
                    hashlib.sha256(worktree).hexdigest(),
                )

    def test_missing_eol_binding_and_raw_byte_hash_are_statically_visible(self) -> None:
        artifact = _load_artifact()
        self.assertFalse((_ROOT / ".gitattributes").exists())
        finding = artifact["repository_eol_finding"]
        self.assertFalse(finding["gitattributes_present_before_audit"])
        self.assertFalse(finding["asset_specific_eol_rule_present"])
        source = _SOURCE_PATHS["browser_payload_source"].read_text(encoding="utf-8")
        self.assertIn("hashlib.sha256(path.read_bytes()).hexdigest()", source)

    def test_cause_decision_and_zero_execution_boundary_are_explicit(self) -> None:
        artifact = _load_artifact()
        cause = artifact["cause_finding"]
        self.assertFalse(cause["content_drift_found"])
        self.assertFalse(cause["stale_w1f_expectation_found"])
        self.assertTrue(cause["line_ending_only_worktree_difference_found"])
        self.assertTrue(cause["failure_occurs_before_browser_factory"])
        self.assertFalse(cause["field_or_candidate_mechanism_implication"])
        self.assertTrue(all(value == 0 for value in artifact["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()

