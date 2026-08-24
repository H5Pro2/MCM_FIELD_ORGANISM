from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_ARTIFACT = _ROOT / "docs" / (
    "S1ZO_STATISCHER_AKTIVKERN_PRIVATREFERENZ_UND_"
    "DRIFTKONSOLIDIERUNGSAUDIT_V1.json"
)
_SOURCE_PATHS = {
    "package_root": _ROOT / "mcm_field_organism" / "__init__.py",
    "current_api": _ROOT / "mcm_field_organism" / "current_api.py",
    "root_lazy_exports": _ROOT / "mcm_field_organism" / "root_lazy_exports.py",
    "shared_mcm_field": _ROOT / "mcm_field_organism" / "shared_mcm_field.py",
    "ppb1_reference": _ROOT / "mcm_field_organism" / "_ppb1_reference.py",
    "lprh1f_s1zm_private_application": _ROOT
    / "mcm_field_organism"
    / "_lprh1f_s1zm_private_proposal_application.py",
    "s1zn_closure_artifact": _ROOT
    / "docs"
    / (
        "S1ZN_LPRH1F_STATISCHER_PRIVATER_IMPLEMENTIERUNGS_RECEIPT_"
        "GRENZ_UND_ERGEBNISABSCHLUSSAUDIT_V1.json"
    ),
    "w1f_browser_smoke_test": _ROOT / "tests" / "test_browser_payload_smoke.py",
}
_FORBIDDEN_TOKENS = (
    "_ppb1_",
    "_lprh1f_",
    "_acm1h_",
    "e1_",
    "g2_d3_",
    "dynamic_substrate_",
    "lrd",
)


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


class S1ZOStaticConsolidationAuditTests(unittest.TestCase):
    def test_artifact_digest_and_bound_sources_are_exact(self) -> None:
        artifact = _load_artifact()
        self.assertEqual(_canonical_digest(artifact), artifact["artifact_digest"])
        bound = artifact["bound_source_digests"]
        self.assertIsInstance(bound, dict)
        for role, path in _SOURCE_PATHS.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), bound[role])

    def test_active_surfaces_have_no_private_or_closed_import(self) -> None:
        artifact = _load_artifact()
        for relative_path in artifact["active_surface_files"]:
            path = _ROOT / relative_path
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            imported_modules = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    imported_modules.append(node.module or "")
                elif isinstance(node, ast.Import):
                    imported_modules.extend(alias.name for alias in node.names)
            lowered = "\n".join(imported_modules).lower()
            self.assertEqual([], [token for token in _FORBIDDEN_TOKENS if token in lowered])

    def test_private_families_exist_and_historical_absence_is_allowed(self) -> None:
        package_files = [path.name.lower() for path in (_ROOT / "mcm_field_organism").glob("*.py")]
        artifact = _load_artifact()
        for prefix in artifact["private_engineering_families"]:
            self.assertTrue(any(name.startswith(prefix) for name in package_files), prefix)
        present_historical = {
            prefix: sum(name.startswith(prefix) for name in package_files)
            for prefix in artifact["historical_closed_module_prefixes"]
        }
        self.assertGreater(sum(present_historical.values()), 0)
        self.assertEqual(0, present_historical["lrd"])

    def test_shared_field_declares_no_private_candidate_state_slot(self) -> None:
        source = _SOURCE_PATHS["shared_mcm_field"].read_text(encoding="utf-8").lower()
        self.assertEqual([], [token for token in _FORBIDDEN_TOKENS if token in source])

    def test_w1f_residual_is_bounded_as_technical_only(self) -> None:
        artifact = _load_artifact()
        residual = artifact["w1f_residual"]
        self.assertEqual(
            "KNOWN_TECHNICAL_BROWSER_ASSET_DIGEST_REPRODUCIBILITY_RESIDUAL",
            residual["classification"],
        )
        self.assertFalse(residual["field_or_candidate_mechanism_implication"])
        self.assertFalse(residual["automatic_asset_or_expectation_rewrite_allowed"])
        smoke_source = (
            _ROOT / "mcm_field_organism" / "browser_payload_smoke.py"
        ).read_text(encoding="utf-8")
        self.assertIn("browser payload assets differ from W1-F", smoke_source)

    def test_decision_and_zero_execution_boundary_are_explicit(self) -> None:
        artifact = _load_artifact()
        self.assertEqual(
            "PASS_ACTIVE_CORE_PRIVATE_REFERENCES_AND_CLOSED_RESEARCH_REMAIN_SEPARATE_NO_ACTIVATION_DRIFT",
            artifact["decision"],
        )
        self.assertTrue(all(value == 0 for value in artifact["execution_counters"].values()))
        disposition = artifact["research_disposition"]
        self.assertFalse(disposition["new_candidate_opened"])
        self.assertFalse(disposition["closed_candidate_reopened"])
        self.assertFalse(disposition["memory_or_field_effect_supported"])
        self.assertTrue(disposition["active_field_core_remains_primary"])


if __name__ == "__main__":
    unittest.main()
