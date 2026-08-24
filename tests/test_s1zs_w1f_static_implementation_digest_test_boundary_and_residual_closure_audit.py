from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / (
    "S1ZS_W1F_STATISCHER_IMPLEMENTIERUNGS_DIGEST_TESTGRENZEN_UND_"
    "RESTABSCHLUSSAUDIT_V1.json"
)
_BOUND_SOURCES = {
    "gitattributes": _ROOT / ".gitattributes",
    "s1zr_document": _ROOT / "docs" / "S1ZR_W1F_DREI_ASSET_EOL_IMPLEMENTIERUNG_UND_SYNTHETISCHER_ABNAHMEBEFUND.md",
    "s1zr_finding": _ROOT / "docs" / "S1ZR_W1F_DREI_ASSET_EOL_IMPLEMENTIERUNG_UND_SYNTHETISCHER_ABNAHMEBEFUND_V1.json",
    "s1zr_receipt_tests": _ROOT / "tests" / "test_s1zr_w1f_three_asset_eol_implementation_receipt.py",
    "s1zp_tests_after_implementation": _ROOT / "tests" / "test_s1zp_w1f_static_asset_and_expectation_binding_audit.py",
    "s1zq_tests_after_implementation": _ROOT / "tests" / "test_s1zq_w1f_static_three_asset_eol_correction_contract.py",
    "browser_payload_smoke": _ROOT / "mcm_field_organism" / "browser_payload_smoke.py",
    "browser_payload_source": _ROOT / "mcm_field_organism" / "browser_payload_source.py",
}


def _audit() -> dict[str, object]:
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


class S1ZSStaticResidualClosureAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in _BOUND_SOURCES.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_three_rules_remain_exact_and_narrow(self) -> None:
        lines = (_ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertEqual(3, len(lines))
        self.assertTrue(all(line.endswith(" text eol=lf") for line in lines))
        self.assertTrue(all(line.startswith("tools/controlled_browser_payload_world/") for line in lines))
        boundary = _audit()["implemented_boundary"]
        self.assertEqual(3, boundary["exact_gitattributes_rule_count"])
        self.assertFalse(boundary["global_eol_rule_present"])

    def test_assets_equal_worktree_git_blob_and_w1f_without_import(self) -> None:
        expected = _w1f_assets()
        for record in _audit()["asset_closure"]:
            path = record["path"]
            raw = (_ROOT / path).read_bytes()
            blob = subprocess.check_output(["git", "cat-file", "blob", f"HEAD:{path}"], cwd=_ROOT)
            digest = hashlib.sha256(raw).hexdigest()
            self.assertEqual(raw, blob)
            self.assertEqual(expected[Path(path).name], digest)
            self.assertEqual(record["raw_worktree_git_blob_and_w1f_sha256"], digest)

    def test_prior_receipt_is_bound_without_broad_suite_claim(self) -> None:
        receipt = _audit()["accepted_prior_test_receipt"]
        self.assertEqual((10, 0), (receipt["static_gate_test_count"], receipt["static_gate_failure_count"]))
        self.assertEqual(
            (14, 0),
            (receipt["synthetic_source_and_fake_smoke_test_count"], receipt["synthetic_failure_count"]),
        )
        self.assertFalse(receipt["real_browser_used"])
        self.assertFalse(receipt["broad_project_suite_run_after_correction"])

    def test_closure_decision_and_zero_reexecution_are_explicit(self) -> None:
        audit = _audit()
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))
        self.assertEqual(
            "PASS_W1F_EOL_REPRODUCIBILITY_RESIDUAL_CLOSED_BROAD_PROJECT_SUITE_STATUS_NOT_YET_ESTABLISHED",
            audit["decision"],
        )
        self.assertIn("NO_FULL_SUITE", audit["claim_boundary"])


if __name__ == "__main__":
    unittest.main()

