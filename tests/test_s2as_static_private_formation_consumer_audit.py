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
        "S2AS_STATISCHER_PRIVATER_BILDUNGSVERBRAUCHER_IMPLEMENTIERUNGS_"
        "DIGEST_ATOMARITAETS_UND_GRENZENAUDIT_V1.json"
    )
)
BOUND = {
    "s2ar_receipt": (
        ROOT
        / "docs"
        / (
            "S2AR_PRIVATER_ATOMARER_AKTIVBATCH_BILDUNGSVERBRAUCHER_UND_"
            "SYNTHETISCHE_VERTRAGSTESTS_V1.json"
        )
    ),
    "s2ar_document": (
        ROOT
        / "docs"
        / (
            "S2AR_PRIVATER_ATOMARER_AKTIVBATCH_BILDUNGSVERBRAUCHER_UND_"
            "SYNTHETISCHE_VERTRAGSTESTS.md"
        )
    ),
    "private_consumer": PACKAGE / "_ppb1_active_batch_formation_consumer.py",
    "synthetic_contract_tests": (
        ROOT / "tests" / "test_s2ar_private_active_batch_formation_consumer.py"
    ),
    "active_batch_binder": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "ppb1_lifecycle": PACKAGE / "_ppb1_s1wq_perceptual_state_lifecycle.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
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


def _consumer_tree() -> ast.Module:
    source = BOUND["private_consumer"].read_text(encoding="ascii")
    return ast.parse(source)


class S2ASStaticPrivateFormationConsumerAuditTests(unittest.TestCase):
    def test_artifact_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_inventory_and_lifecycle_call_site_are_exact(self) -> None:
        tree = _consumer_tree()
        class_names = {
            node.name for node in tree.body if isinstance(node, ast.ClassDef)
        }
        self.assertEqual(
            set(_audit()["source_inventory"]["private_class_names"]),
            class_names,
        )
        calls = [
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        self.assertEqual(1, calls.count("advance_s1wq_perceptual_state"))
        self.assertEqual(1, calls.count("initial_ppb1_bank_state"))

    def test_owner_and_atomicity_audits_pass_without_remaining_blocker(self) -> None:
        audit = _audit()
        self.assertEqual("PASS", audit["preflight_and_owner_audit"]["status"])
        self.assertEqual("PASS", audit["atomicity_audit"]["status"])
        self.assertEqual("PASS", audit["digest_and_identity_audit"]["status"])
        self.assertEqual(0, audit["remaining_blocker_count"])

    def test_public_field_and_execution_boundaries_remain_closed(self) -> None:
        audit = _audit()
        boundary = audit["boundary_audit"]
        self.assertFalse(boundary["current_api_changed"])
        self.assertFalse(boundary["package_root_changed"])
        self.assertFalse(boundary["shared_field_or_snapshot_changed"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertIn(
            "NO_FORMATION_EXECUTION_RECOGNITION_ADVANTAGE_"
            "FIELD_EFFECT_OR_MEMORY_RESULT",
            audit["claim_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
