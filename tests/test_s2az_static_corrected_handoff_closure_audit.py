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
        "S2AZ_STATISCHER_KORRIGIERTER_HANDOFF_QUELLDIGEST_"
        "AUFRUFSTELLEN_BLOCKERSCHLUSS_UND_GRENZENAUDIT_V1.json"
    )
)
BOUND = {
    "s2ay_receipt": (
        ROOT
        / "docs"
        / (
            "S2AY_PRIVATE_PROBE_AUFRUFSTELLEN_KONSOLIDIERUNG_UND_"
            "SYNTHETISCHE_REGRESSION_V1.json"
        )
    ),
    "s2ay_document": (
        ROOT
        / "docs"
        / (
            "S2AY_PRIVATE_PROBE_AUFRUFSTELLEN_KONSOLIDIERUNG_UND_"
            "SYNTHETISCHE_REGRESSION.md"
        )
    ),
    "s2ay_static_validator": (
        ROOT / "tests" / "test_s2ay_static_probe_call_site_correction_receipt.py"
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


def _tree() -> ast.Module:
    return ast.parse(BOUND["corrected_handoff"].read_text(encoding="ascii"))


class S2AZStaticCorrectedHandoffClosureAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_one_probe_call_site_and_two_shared_helper_calls_are_exact(self) -> None:
        tree = _tree()
        probe_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "probe_s1wu_perceptual_state"
        ]
        main = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name
            == "probe_ppb1_active_batch_formation_result_read_only"
        )
        helper_calls = [
            node
            for node in ast.walk(main)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_probe_modality_read_only"
        ]
        self.assertEqual((1, 2), (len(probe_calls), len(helper_calls)))

    def test_blocker_read_only_atomicity_and_boundaries_are_closed(self) -> None:
        audit = _audit()
        self.assertEqual("CLOSED", audit["s2ax_blocker_closure"]["status"])
        self.assertEqual("PASS", audit["read_only_atomicity_reaudit"]["status"])
        self.assertEqual("PASS", audit["boundary_reaudit"]["status"])
        self.assertEqual(0, audit["remaining_blocker_count"])

    def test_no_execution_or_baseline_decision_occurred(self) -> None:
        audit = _audit()
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertFalse(
            audit["technical_path_status"][
                "baseline_implementation_or_execution_authorized"
            ]
        )


if __name__ == "__main__":
    unittest.main()
