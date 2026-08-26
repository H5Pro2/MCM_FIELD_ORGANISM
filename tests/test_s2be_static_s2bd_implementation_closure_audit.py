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
        "S2BE_STATISCHER_S2BD_IMPLEMENTIERUNGS_QUELLDIGEST_"
        "NICHTZIRKULARITAETS_ATOMARITAETS_ERGEBNIS_UND_GRENZENAUDIT_V1.json"
    )
)
BOUND = {
    "s2bd_receipt": (
        ROOT
        / "docs"
        / (
            "S2BD_PRIVATE_QUELLGEBUNDENE_STATISCHE_PROTOTYPBASELINE_"
            "ATOMARER_COMPARATOR_UND_SYNTHETISCHE_VERTRAGSTESTS_V1.json"
        )
    ),
    "s2bc_preflight": (
        ROOT
        / "docs"
        / (
            "S2BC_STATISCHER_QUELLGEBUNDENER_BASELINE_MATERIALISIERBARKEITS_"
            "NICHTZIRKULARITAETS_UND_INFORMATIONSFLUSS_PREFLIGHT_V1.json"
        )
    ),
    "private_static_baseline": (
        PACKAGE / "_ppb1_s2bd_active_static_prototype_baseline.py"
    ),
    "private_paired_comparator": (
        PACKAGE / "_ppb1_s2bd_paired_recognition_comparator.py"
    ),
    "synthetic_contract_tests": (
        ROOT / "tests" / "test_s2bd_private_active_static_prototype_comparator.py"
    ),
    "s2bd_static_receipt_validator": (
        ROOT / "tests" / "test_s2bd_static_implementation_receipt.py"
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


def _call_lines(name: str) -> list[int]:
    tree = ast.parse(BOUND["private_paired_comparator"].read_text(encoding="ascii"))
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == name
    ]


class S2BEStaticS2BDImplementationClosureAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_call_order_blocker_is_exactly_located(self) -> None:
        audit = _audit()
        baseline_line = _call_lines("form_s2bb_active_static_prototype_baseline")
        candidate_line = _call_lines(
            "probe_ppb1_active_batch_formation_result_read_only"
        )
        self.assertEqual([279], baseline_line)
        self.assertEqual([283], candidate_line)
        self.assertLess(baseline_line[0], candidate_line[0])
        self.assertEqual("OPEN", audit["ordering_blocker"]["status"])

    def test_only_one_role_is_blocked_and_no_execution_occurred(self) -> None:
        audit = _audit()
        self.assertEqual(7, audit["checked_role_count"])
        self.assertEqual(6, audit["passed_role_count"])
        self.assertEqual(1, audit["blocked_role_count"])
        self.assertEqual(1, audit["open_blocker_count"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))

    def test_valid_fixture_result_is_retained_without_advantage_claim(self) -> None:
        audit = _audit()
        self.assertFalse(audit["ordering_blocker"]["valid_fixture_result_invalidated"])
        self.assertTrue(
            audit["result_boundary_audit"]["current_fixture_is_baseline_explained"]
        )
        self.assertFalse(
            audit["result_boundary_audit"]["ppb1_specific_advantage_claimed"]
        )


if __name__ == "__main__":
    unittest.main()
