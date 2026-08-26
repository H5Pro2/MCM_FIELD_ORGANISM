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
        "S2BF_PRIVATE_VOLLSTAENDIGE_QUELLVORPRUEFUNG_"
        "REIHENFOLGEKORREKTUR_UND_ADVERSARIALE_NULLAUFRUF_REGRESSION_V1.json"
    )
)
BOUND = {
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


def _receipt() -> dict[str, object]:
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


class S2BFStaticCorrectionReceiptTests(unittest.TestCase):
    def test_receipt_digest_and_bound_sources_are_exact(self) -> None:
        receipt = _receipt()
        self.assertEqual(_canonical_digest(receipt), receipt["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                receipt["bound_source_digests"][role],
            )

    def test_preflight_calls_precede_one_historical_comparator_call(self) -> None:
        tree = ast.parse(BOUND["corrected_private_entry"].read_text(encoding="ascii"))
        function = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name
            == "compare_s2bf_ppb1_with_static_prototype_baseline"
        )
        lines = {
            name: [
                node.lineno
                for node in ast.walk(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == name
            ]
            for name in (
                "_validate_formation",
                "_validate_probe_envelope",
                "compare_s2bd_ppb1_with_static_prototype_baseline",
            )
        }
        self.assertTrue(all(len(value) == 1 for value in lines.values()))
        self.assertLess(
            max(lines["_validate_formation"] + lines["_validate_probe_envelope"]),
            lines["compare_s2bd_ppb1_with_static_prototype_baseline"][0],
        )

    def test_blocker_is_closed_and_result_boundary_is_narrow(self) -> None:
        receipt = _receipt()
        self.assertEqual("CLOSED", receipt["s2be_blocker_closure"]["status"])
        self.assertEqual(0, receipt["adversarial_regression"]["baseline_formation_call_count"])
        self.assertEqual(4, receipt["focused_test_execution"]["final_passed"])
        self.assertFalse(
            receipt["technical_disposition"]["ppb1_specific_recognition_advantage"]
        )
        self.assertFalse(
            receipt["technical_disposition"]["mcm_specific_memory_mechanism"]
        )


if __name__ == "__main__":
    unittest.main()
