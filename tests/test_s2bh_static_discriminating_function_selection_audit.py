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
        "S2BH_STATISCHER_UNTERSCHEIDBARER_PERZEPTIVER_FUNKTIONSRAUM_"
        "UND_EINZELFUNKTIONS_AUSWAHLAUDIT_V1.json"
    )
)
BOUND = {
    "s2bg_closure_audit": (
        ROOT
        / "docs"
        / (
            "S2BG_STATISCHER_KORRIGIERTER_EINSTIEG_QUELLDIGEST_"
            "VORPRUEFUNGSREIHENFOLGE_NULLAUFRUF_BLOCKERSCHLUSS_UND_"
            "GRENZENAUDIT_V1.json"
        )
    ),
    "s2ae_memory_connection_priority_audit": (
        ROOT
        / "docs"
        / (
            "S2AE_STATISCHER_PRIORISIERUNGS_UND_LUECKENAUDIT_"
            "WAHRNEHMUNGSSPEICHER_ANSCHLUSS_V1.json"
        )
    ),
    "s1xt_single_function_selection": (
        ROOT
        / "docs"
        / "S1XT_PPB1_STATISCHE_ENGINEERINGEINORDNUNG_UND_EINZELFUNKTIONSWAHL_V1.json"
    ),
    "s1ye_nonduplication_equivalence_audit": (
        ROOT
        / "docs"
        / (
            "S1YE_PPB1_STATISCHER_NICHTDUPLIZIERUNGS_"
            "INFORMATIONS_UND_AEQUIVALENZAUDIT_V1.json"
        )
    ),
    "receptor_time_alignment": PACKAGE / "receptor_time_alignment.py",
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "receptor_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "temporal_collision_audit": PACKAGE / "temporal_compact_summary_collision_audit.py",
    "corrected_recognition_control": (
        PACKAGE / "_ppb1_s2bf_corrected_paired_recognition_comparator.py"
    ),
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


class S2BHStaticDiscriminatingFunctionSelectionAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_exactly_one_function_is_selected(self) -> None:
        audit = _audit()
        selected = [item for item in audit["screened_functions"] if item["selection"]]
        self.assertEqual(1, len(selected))
        self.assertEqual(
            "AVPC1_AUDITORY_CUED_VISUAL_PERCEPTUAL_COMPLETION",
            selected[0]["function_id"],
        )
        self.assertEqual(1, audit["single_selected_function"]["selected_function_count"])

    def test_selected_function_has_a_crossed_history_counterprediction(self) -> None:
        audit = _audit()
        counterprediction = audit["required_crossed_history_counterprediction"]
        self.assertTrue(counterprediction["function_counterprediction_present"])
        self.assertEqual(
            "UNAMBIGUOUS_AUDIO_VISUAL_OVERLAP_RELATION_DURING_FORMATION",
            counterprediction["must_differ"],
        )
        self.assertTrue(counterprediction["materializability_not_yet_proven"])

    def test_no_mechanism_implementation_execution_or_overclaim(self) -> None:
        audit = _audit()
        boundary = audit["selection_boundary"]
        self.assertFalse(boundary["mechanism_selected"])
        self.assertFalse(boundary["implementation_authorized"])
        self.assertFalse(boundary["execution_authorized"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))


if __name__ == "__main__":
    unittest.main()
