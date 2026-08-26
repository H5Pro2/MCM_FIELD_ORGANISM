from __future__ import annotations

import ast
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
        "S2BG_STATISCHER_KORRIGIERTER_EINSTIEG_QUELLDIGEST_"
        "VORPRUEFUNGSREIHENFOLGE_NULLAUFRUF_BLOCKERSCHLUSS_UND_"
        "GRENZENAUDIT_V1.json"
    )
)
BOUND = {
    "s2bf_receipt": (
        ROOT
        / "docs"
        / (
            "S2BF_PRIVATE_VOLLSTAENDIGE_QUELLVORPRUEFUNG_"
            "REIHENFOLGEKORREKTUR_UND_ADVERSARIALE_NULLAUFRUF_REGRESSION_V1.json"
        )
    ),
    "s2be_audit": (
        ROOT
        / "docs"
        / (
            "S2BE_STATISCHER_S2BD_IMPLEMENTIERUNGS_QUELLDIGEST_"
            "NICHTZIRKULARITAETS_ATOMARITAETS_ERGEBNIS_UND_GRENZENAUDIT_V1.json"
        )
    ),
    "corrected_private_entry": (
        PACKAGE / "_ppb1_s2bf_corrected_paired_recognition_comparator.py"
    ),
    "focused_regression_tests": (
        ROOT / "tests" / "test_s2bf_corrected_source_preflight_order.py"
    ),
    "s2bf_static_receipt_validator": (
        ROOT / "tests" / "test_s2bf_static_correction_receipt.py"
    ),
    "private_static_baseline": (
        PACKAGE / "_ppb1_s2bd_active_static_prototype_baseline.py"
    ),
    "historical_s2bd_comparator": (
        PACKAGE / "_ppb1_s2bd_paired_recognition_comparator.py"
    ),
    "formation_probe_handoff": (
        PACKAGE / "_ppb1_active_batch_formation_probe_handoff.py"
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


class S2BGStaticCorrectedRecognitionClosureAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_corrected_preflight_order_is_exact(self) -> None:
        audit = _audit()
        tree = ast.parse(BOUND["corrected_private_entry"].read_text(encoding="ascii"))
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name
            == "compare_s2bf_ppb1_with_static_prototype_baseline"
        )
        calls = {
            node.func.id: node.lineno
            for node in ast.walk(function)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id
            in {
                "_validate_formation",
                "_validate_probe_envelope",
                "compare_s2bd_ppb1_with_static_prototype_baseline",
            }
        }
        self.assertEqual(43, calls["_validate_formation"])
        self.assertEqual(44, calls["_validate_probe_envelope"])
        self.assertEqual(
            50,
            calls["compare_s2bd_ppb1_with_static_prototype_baseline"],
        )
        self.assertEqual("PASS", audit["corrected_order_audit"]["status"])

    def test_blocker_and_technical_path_are_closed(self) -> None:
        audit = _audit()
        self.assertEqual("CLOSED", audit["s2be_blocker_final_closure"]["status"])
        self.assertEqual(0, audit["open_blocker_count"])
        self.assertEqual(7, audit["passed_role_count"])
        self.assertEqual("TECHNICALLY_CLOSED", audit["technical_path_closure"]["corrected_atomic_pairing_path"])

    def test_no_execution_or_overclaim_occurred(self) -> None:
        audit = _audit()
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertFalse(
            audit["technical_path_closure"]["ppb1_specific_recognition_advantage"]
        )
        self.assertFalse(
            audit["technical_path_closure"]["mcm_specific_memory_mechanism"]
        )


if __name__ == "__main__":
    unittest.main()
