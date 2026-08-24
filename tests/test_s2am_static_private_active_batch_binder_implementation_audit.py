from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_PACKAGE = _ROOT / "mcm_field_organism"
_ARTIFACT = (
    _ROOT
    / "docs"
    / (
        "S2AM_STATISCHER_PRIVATER_AKTIVBATCH_BINDER_"
        "IMPLEMENTIERUNGS_UND_GRENZAUDIT_V1.json"
    )
)
_BOUND = {
    "s2al_receipt": (
        _ROOT
        / "docs"
        / (
            "S2AL_PRIVATER_REINER_AKTIVBATCH_BINDER_UND_"
            "SYNTHETISCHE_VERTRAGSTESTS_V1.json"
        )
    ),
    "s2al_document": (
        _ROOT
        / "docs"
        / "S2AL_PRIVATER_REINER_AKTIVBATCH_BINDER_UND_SYNTHETISCHE_VERTRAGSTESTS.md"
    ),
    "private_binder": _PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "synthetic_contract_tests": (
        _ROOT / "tests" / "test_s2al_private_active_receptor_batch_binding.py"
    ),
    "s2ak_audit": (
        _ROOT
        / "docs"
        / (
            "S2AK_STATISCHER_VOLLSTAENDIG_KORRIGIERTER_"
            "AKTIVBATCH_BINDUNGS_ABSCHLUSSAUDIT_V1.json"
        )
    ),
    "current_api": _PACKAGE / "current_api.py",
    "package_root": _PACKAGE / "__init__.py",
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


class S2AMStaticPrivateActiveBatchBinderImplementationAuditTests(unittest.TestCase):
    def test_audit_digest_and_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_private_implementation_inventory_is_exact(self) -> None:
        inventory = _audit()["implementation_inventory"]
        self.assertEqual(1, inventory["private_error_type_count"])
        self.assertEqual(3, inventory["private_frozen_value_type_count"])
        self.assertEqual(1, inventory["private_pure_bind_function_count"])
        self.assertEqual(0, inventory["unexpected_runtime_type_or_function_count"])

    def test_source_ast_has_no_forbidden_calls(self) -> None:
        source = _BOUND["private_binder"].read_text(encoding="ascii")
        tree = ast.parse(source)
        calls = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.add(node.func.attr)
        self.assertTrue(
            {
                "advance_ppb1_bank",
                "probe_s1wu_perceptual_state",
                "advance_audio_video_receptor_sequences",
                "open",
            }.isdisjoint(calls)
        )
        self.assertTrue(
            all(
                value == 0
                for value in _audit()["forbidden_call_scan"].values()
            )
        )

    def test_digest_time_atomicity_and_privacy_are_complete(self) -> None:
        audit = _audit()
        closure = audit["digest_dependency_closure"]
        self.assertEqual(15, closure["required_role_count"])
        self.assertEqual(15, closure["materialized_role_count"])
        self.assertEqual([], closure["missing_roles"])
        self.assertTrue(
            audit["source_and_time_acceptance"][
                "source_window_overlap_remains_allowed"
            ]
        )
        self.assertFalse(
            audit["atomicity_and_purity_acceptance"][
                "global_uniqueness_or_consumption_ledger"
            ]
        )
        self.assertEqual(0, audit["privacy_acceptance"]["public_export_count"])

    def test_evidence_is_reused_without_execution_and_claim_stays_narrow(self) -> None:
        audit = _audit()
        evidence = audit["synthetic_evidence_reused_without_reexecution"]
        self.assertEqual(7, evidence["receipt_final_test_count"])
        self.assertEqual(7, evidence["receipt_final_passed"])
        self.assertEqual(0, evidence["s2am_test_reexecution_count"])
        self.assertEqual(0, audit["remaining_blocker_count"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertIn(
            "NO_STORE_FORMATION_RECOGNITION_FIELD_EFFECT_OR_MEMORY_RESULT",
            audit["claim_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
