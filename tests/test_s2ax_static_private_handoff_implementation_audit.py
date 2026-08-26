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
        "S2AX_STATISCHER_PRIVATER_HANDOFF_IMPLEMENTIERUNGS_DIGEST_"
        "READ_ONLY_ATOMARITAETS_UND_GRENZENAUDIT_V1.json"
    )
)
BOUND = {
    "s2aw_receipt": (
        ROOT
        / "docs"
        / (
            "S2AW_PRIVATER_BILDUNGSERGEBNIS_ZU_READ_ONLY_PROBE_HANDOFF_UND_"
            "SYNTHETISCHE_VERTRAGSTESTS_V1.json"
        )
    ),
    "s2aw_document": (
        ROOT
        / "docs"
        / (
            "S2AW_PRIVATER_BILDUNGSERGEBNIS_ZU_READ_ONLY_PROBE_HANDOFF_UND_"
            "SYNTHETISCHE_VERTRAGSTESTS.md"
        )
    ),
    "private_handoff": (
        PACKAGE / "_ppb1_active_batch_formation_probe_handoff.py"
    ),
    "synthetic_tests": (
        ROOT / "tests" / "test_s2aw_private_formation_probe_handoff.py"
    ),
    "s2av_audit": (
        ROOT
        / "docs"
        / (
            "S2AV_STATISCHER_HANDOFF_VERTRAGS_VOLLSTAENDIGKEITS_"
            "NICHTZIRKULARITAETS_KAUSALPARTITIONS_UND_"
            "MATERIALISIERBARKEITSAUDIT_V1.json"
        )
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


def _probe_call_lines() -> list[int]:
    source = BOUND["private_handoff"].read_text(encoding="ascii")
    tree = ast.parse(source)
    return [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "probe_s1wu_perceptual_state"
    ]


class S2AXStaticPrivateHandoffImplementationAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_read_only_atomicity_and_boundaries_pass(self) -> None:
        audit = _audit()
        self.assertEqual(
            "PASS",
            audit["preflight_partition_and_read_only_audit"]["status"],
        )
        self.assertEqual("PASS", audit["boundary_audit"]["status"])

    def test_actual_two_call_sites_conflict_with_bound_single_site(self) -> None:
        audit = _audit()
        blocker = audit["contract_conformance_blocker"]
        self.assertEqual([385, 391], sorted(_probe_call_lines()))
        self.assertEqual(1, blocker["s2av_bound_existing_probe_call_site_count"])
        self.assertEqual(2, blocker["s2aw_actual_existing_probe_call_site_count"])
        self.assertTrue(blocker["source_materialization_conflict"])
        self.assertFalse(blocker["runtime_call_count_behavior_conflict"])
        self.assertEqual("OPEN", blocker["status"])

    def test_correction_is_not_authorized_and_no_execution_occurred(self) -> None:
        audit = _audit()
        self.assertEqual(1, audit["remaining_blocker_count"])
        self.assertFalse(audit["implementation_status"]["contract_closed"])
        self.assertFalse(
            audit["implementation_status"]["correction_authorized_in_s2ax"]
        )
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))


if __name__ == "__main__":
    unittest.main()
