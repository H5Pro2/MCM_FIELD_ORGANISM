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
        "S2AY_PRIVATE_PROBE_AUFRUFSTELLEN_KONSOLIDIERUNG_UND_"
        "SYNTHETISCHE_REGRESSION_V1.json"
    )
)
BOUND = {
    "s2ax_audit": (
        ROOT
        / "docs"
        / (
            "S2AX_STATISCHER_PRIVATER_HANDOFF_IMPLEMENTIERUNGS_DIGEST_"
            "READ_ONLY_ATOMARITAETS_UND_GRENZENAUDIT_V1.json"
        )
    ),
    "s2ax_document": (
        ROOT
        / "docs"
        / (
            "S2AX_STATISCHER_PRIVATER_HANDOFF_IMPLEMENTIERUNGS_DIGEST_"
            "READ_ONLY_ATOMARITAETS_UND_GRENZENAUDIT.md"
        )
    ),
    "s2ax_static_validator": (
        ROOT / "tests" / "test_s2ax_static_private_handoff_implementation_audit.py"
    ),
    "corrected_handoff": (
        PACKAGE / "_ppb1_active_batch_formation_probe_handoff.py"
    ),
    "synthetic_regression_tests": (
        ROOT / "tests" / "test_s2aw_private_formation_probe_handoff.py"
    ),
    "formation_consumer": PACKAGE / "_ppb1_active_batch_formation_consumer.py",
    "read_only_probe": PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py",
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


def _source_tree() -> ast.Module:
    return ast.parse(BOUND["corrected_handoff"].read_text(encoding="ascii"))


class S2AYStaticProbeCallSiteCorrectionReceiptTests(unittest.TestCase):
    def test_receipt_digest_and_bound_sources_are_exact(self) -> None:
        receipt = _receipt()
        self.assertEqual(_canonical_digest(receipt), receipt["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                receipt["bound_source_digests"][role],
            )

    def test_exactly_one_existing_probe_call_site_remains(self) -> None:
        call_lines = [
            node.lineno
            for node in ast.walk(_source_tree())
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "probe_s1wu_perceptual_state"
        ]
        self.assertEqual(1, len(call_lines))
        self.assertEqual(
            1,
            _receipt()["correction_scope"][
                "post_correction_probe_call_site_count"
            ],
        )

    def test_helper_is_private_and_blocker_is_closed(self) -> None:
        functions = {
            node.name
            for node in _source_tree().body
            if isinstance(node, ast.FunctionDef)
        }
        self.assertIn("_probe_modality_read_only", functions)
        self.assertEqual(
            "CLOSED_BY_IMPLEMENTATION_AND_REGRESSION",
            _receipt()["blocker_closure"]["status"],
        )

    def test_nine_regressions_pass_without_other_execution_roles(self) -> None:
        execution = _receipt()["synthetic_regression_execution"]
        self.assertEqual((9, 0, 0), (
            execution["passed"],
            execution["failed"],
            execution["errors"],
        ))
        self.assertEqual(0, execution["baseline_call_count"])
        self.assertEqual(0, execution["field_call_count"])
        self.assertEqual(0, execution["production_or_live_call_count"])


if __name__ == "__main__":
    unittest.main()
