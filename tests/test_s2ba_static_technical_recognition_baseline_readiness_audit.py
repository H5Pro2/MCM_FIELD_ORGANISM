from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "mcm_field_organism"
ARTIFACT = (
    ROOT
    / "docs"
    / (
        "S2BA_STATISCHER_TECHNISCHER_WIEDERERKENNUNGS_BASELINE_"
        "BEREITSCHAFTS_UND_AUSWAHLAUDIT_V1.json"
    )
)
BOUND = {
    "s2az_audit": (
        ROOT
        / "docs"
        / (
            "S2AZ_STATISCHER_KORRIGIERTER_HANDOFF_QUELLDIGEST_"
            "AUFRUFSTELLEN_BLOCKERSCHLUSS_UND_GRENZENAUDIT_V1.json"
        )
    ),
    "s1ww_complete_function_contract": (
        ROOT
        / "docs"
        / "S1WW_PPB1_VOLLSTAENDIGER_BILDUNGS_UND_PROBE_FUNKTIONSVERTRAG_V1.json"
    ),
    "s1yd_dynamic_baseline_selection": (
        ROOT
        / "docs"
        / (
            "S1YD_PPB1_STATISCHE_ENGINEERINGEINORDNUNG_UND_"
            "DYNAMISCHE_BASELINEAUSWAHL_V1.json"
        )
    ),
    "s1ye_nonduplication_audit": (
        ROOT
        / "docs"
        / (
            "S1YE_PPB1_STATISCHER_NICHTDUPLIZIERUNGS_"
            "INFORMATIONS_UND_AEQUIVALENZAUDIT_V1.json"
        )
    ),
    "existing_static_baseline": (
        PACKAGE / "_ppb1_s1ya_private_static_prototype_baseline.py"
    ),
    "existing_static_baseline_tests": (
        ROOT / "tests" / "test_ppb1_s1ya_private_static_prototype_baseline.py"
    ),
    "active_formation_probe_handoff": (
        PACKAGE / "_ppb1_active_batch_formation_probe_handoff.py"
    ),
    "active_handoff_tests": (
        ROOT / "tests" / "test_s2aw_private_formation_probe_handoff.py"
    ),
    "read_only_probe": PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py",
    "current_api": PACKAGE / "current_api.py",
    "package_root": PACKAGE / "__init__.py",
    "shared_field": PACKAGE / "shared_mcm_field.py",
}


def _audit() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


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


class S2BAStaticRecognitionBaselineReadinessAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_exactly_one_primary_baseline_is_selected(self) -> None:
        audit = _audit()
        selected = [item for item in audit["baseline_screen"] if item["selected"]]
        self.assertEqual(1, len(selected))
        self.assertEqual("SIMPLE_STATIC_PROTOTYPE_BANK", selected[0]["baseline_id"])

    def test_current_fixture_is_baseline_explained_and_not_execution_ready(self) -> None:
        audit = _audit()
        assessment = audit["static_counterprediction_assessment"]
        readiness = audit["readiness"]
        self.assertFalse(assessment["independent_current_counterprediction_present"])
        self.assertTrue(
            assessment[
                "technical_recognition_path_explained_by_selected_baseline_for_current_fixture"
            ]
        )
        self.assertFalse(readiness["implementation_or_execution_ready"])
        self.assertEqual(3, len(readiness["open_blockers"]))

    def test_aopb_remains_closed_and_no_execution_occurred(self) -> None:
        audit = _audit()
        aopb = next(
            item
            for item in audit["baseline_screen"]
            if item["baseline_id"]
            == "AOPB1_CAPACITY_MATCHED_ADAPTIVE_ONLINE_PROTOTYPE_BANK"
        )
        self.assertTrue(aopb["must_not_be_reopened"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertFalse(
            audit["technical_disposition"]["ppb1_specific_recognition_advantage"]
        )


if __name__ == "__main__":
    unittest.main()
