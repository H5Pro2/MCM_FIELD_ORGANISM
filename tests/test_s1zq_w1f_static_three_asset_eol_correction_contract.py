from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import subprocess
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / "S1ZQ_W1F_STATISCHER_DREI_ASSET_EOL_KORREKTURVERTRAG_V1.json"
_BOUND_SOURCES = {
    "s1zp_artifact": _ROOT / "docs" / "S1ZP_W1F_STATISCHER_ASSET_UND_ERWARTUNGSBINDUNGSAUDIT_V1.json",
    "s1zp_document": _ROOT / "docs" / "S1ZP_W1F_STATISCHER_ASSET_UND_ERWARTUNGSBINDUNGSAUDIT.md",
    "browser_payload_smoke": _ROOT / "mcm_field_organism" / "browser_payload_smoke.py",
    "browser_payload_source": _ROOT / "mcm_field_organism" / "browser_payload_source.py",
    "browser_payload_smoke_tests": _ROOT / "tests" / "test_browser_payload_smoke.py",
    "browser_payload_source_tests": _ROOT / "tests" / "test_browser_payload_source.py",
}


def _artifact() -> dict[str, object]:
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


class S1ZQStaticEOLCorrectionContractTests(unittest.TestCase):
    def test_contract_digest_and_bound_sources_are_exact(self) -> None:
        contract = _artifact()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in _BOUND_SOURCES.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_exactly_three_narrow_attribute_rules_are_bound_and_implemented(self) -> None:
        lines = _artifact()["exact_gitattributes_lines"]
        self.assertEqual(3, len(lines))
        self.assertEqual(3, len(set(lines)))
        self.assertTrue(all(line.endswith(" text eol=lf") for line in lines))
        self.assertTrue(
            all(line.startswith("tools/controlled_browser_payload_world/") for line in lines)
        )
        self.assertEqual(
            {"index.html", "styles.css", "world.js"},
            {line.split()[0].rsplit("/", 1)[-1] for line in lines},
        )
        self.assertEqual(lines, (_ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines())
        for line in lines:
            path = line.split()[0]
            observed = subprocess.check_output(
                ["git", "check-attr", "text", "eol", "--", path],
                cwd=_ROOT,
                text=True,
            )
            self.assertIn(f"{path}: text: set", observed)
            self.assertIn(f"{path}: eol: lf", observed)

    def test_all_postcorrection_digests_preserve_git_and_w1f_bytes(self) -> None:
        expected = _w1f_assets()
        for record in _artifact()["asset_expectations"]:
            blob = subprocess.check_output(
                ["git", "cat-file", "blob", f"HEAD:{record['path']}"], cwd=_ROOT
            )
            blob_digest = hashlib.sha256(blob).hexdigest()
            name = Path(record["path"]).name
            self.assertEqual(expected[name], blob_digest)
            self.assertEqual(
                {
                    record["expected_raw_worktree_sha256_after_correction"],
                    record["expected_git_blob_sha256"],
                    record["expected_w1f_sha256"],
                },
                {blob_digest},
            )

    def test_implementation_and_execution_boundaries_are_narrow(self) -> None:
        contract = _artifact()
        limits = contract["implementation_constraints"]
        self.assertEqual(3, limits["gitattributes_effective_rule_count"])
        self.assertFalse(limits["global_eol_rule_allowed"])
        self.assertFalse(limits["asset_content_change_allowed"])
        self.assertFalse(limits["w1f_expectation_change_allowed"])
        self.assertFalse(limits["source_code_change_allowed"])
        self.assertFalse(limits["real_browser_execution_allowed"])
        self.assertTrue(limits["synthetic_fake_playwright_tests_allowed_after_correction"])
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))

    def test_fail_closed_set_and_next_step_are_complete(self) -> None:
        contract = _artifact()
        self.assertEqual(7, len(contract["fail_closed_conditions"]))
        self.assertIn("GIT_BLOB_DIGEST_CHANGED", contract["fail_closed_conditions"])
        self.assertIn("REAL_BROWSER_FACTORY_OR_BINARY_USED", contract["fail_closed_conditions"])
        self.assertEqual(
            "PASS_STATIC_THREE_ASSET_EOL_CORRECTION_SCOPE_BOUND_S1ZR_NARROW_IMPLEMENTATION_ELIGIBLE",
            contract["decision"],
        )


if __name__ == "__main__":
    unittest.main()
