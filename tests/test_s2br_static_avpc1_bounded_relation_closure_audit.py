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
        "S2BR_AVPC1_BEGRENZTER_RELATIONSKERN_STATISCHER_"
        "IMPLEMENTIERUNGS_UND_GRENZEN_ABSCHLUSSAUDIT_V1.json"
    )
)
BOUND = {
    "s2bq_receipt": (
        ROOT
        / "docs"
        / (
            "S2BQ_AVPC1_PRIVATER_BEGRENZTER_RELATIONSKERN_UND_"
            "SYNTHETISCHE_VERTRAGSTESTS_V1.json"
        )
    ),
    "s2bq_document": (
        ROOT
        / "docs"
        / (
            "S2BQ_AVPC1_PRIVATER_BEGRENZTER_RELATIONSKERN_UND_"
            "SYNTHETISCHE_VERTRAGSTESTS.md"
        )
    ),
    "s2bo_contract": (
        ROOT
        / "docs"
        / (
            "S2BO_AVPC1_BEGRENZTER_RELATIONSZUSTANDS_KAPAZITAETS_"
            "SUPPORT_KONFLIKT_RECEIPT_UND_BASELINE_VERTRAG_V1.json"
        )
    ),
    "s2bp_preflight": (
        ROOT
        / "docs"
        / (
            "S2BP_AVPC1_BEGRENZTE_RELATION_STATISCHER_"
            "IMPLEMENTIERUNGSPREFLIGHT_V1.json"
        )
    ),
    "private_implementation": PACKAGE / "_avpc1_bounded_relation.py",
    "synthetic_contract_tests": (
        ROOT / "tests" / "test_s2bq_private_avpc1_bounded_relation.py"
    ),
    "current_api": PACKAGE / "current_api.py",
    "package_root": PACKAGE / "__init__.py",
    "shared_field": PACKAGE / "shared_mcm_field.py",
    "root_lazy_exports": PACKAGE / "root_lazy_exports.py",
}


def _audit() -> dict[str, object]:
    return json.loads(ARTIFACT.read_text(encoding="ascii"))


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


class S2BRStaticAVPC1BoundedRelationClosureAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_private_inventory_and_import_boundary_are_exact(self) -> None:
        source = BOUND["private_implementation"].read_text(encoding="ascii")
        tree = ast.parse(source)
        classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
        functions = [
            node.name for node in tree.body if isinstance(node, ast.FunctionDef)
        ]
        self.assertEqual(7, len(classes))
        self.assertEqual(6, len(classes) - 1)
        self.assertEqual(
            {
                "initial_avpc1_bounded_relation_state",
                "bind_avpc1_unambiguous_overlap_exposure_receipt",
                "advance_avpc1_bounded_relation_state",
                "probe_avpc1_bounded_relation_read_only",
            },
            {name for name in functions if not name.startswith("_")},
        )
        calls = {
            node.func.id
            if isinstance(node.func, ast.Name)
            else node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, (ast.Name, ast.Attribute))
        }
        self.assertTrue(
            {
                "advance_ppb1_bank",
                "probe_s1wu_perceptual_state",
                "advance_audio_video_receptor_sequences",
                "open",
            }.isdisjoint(calls)
        )

    def test_transition_precedence_and_read_only_roles_are_closed(self) -> None:
        source = BOUND["private_implementation"].read_text(encoding="ascii")
        start = source.index("def advance_avpc1_bounded_relation_state")
        needles = (
            "if type(state) is not AVPC1BoundedRelationState",
            "if exposure.exposure_receipt_digest in state.consumed_exposure_receipt_digests",
            "elif state.accepted_exposure_count>=4",
            'elif existing and existing.status=="CONFLICTED"',
            'existing.status=="PENDING"',
            'existing.status=="STABLE"',
            "elif existing:",
            "if free is None",
        )
        positions = tuple(source.index(value, start) for value in needles)
        self.assertEqual(positions, tuple(sorted(positions)))
        for role in ("MATCH", "NO_MATCH", "NO_MATCH_CONFLICT"):
            self.assertIn(f'role,target="{role}"', source)

    def test_bound_evidence_closes_generic_baseline_classification(self) -> None:
        audit = _audit()
        evidence = audit["bound_s2bq_evidence"]
        self.assertEqual(9, evidence["final_test_count"])
        self.assertEqual(9, evidence["final_passed"])
        self.assertTrue(evidence["transition_event_sequences_equal"])
        self.assertTrue(evidence["read_only_functional_outputs_equal"])
        self.assertFalse(evidence["mcm_specific_nonreducible_effect"])
        self.assertEqual(0, audit["remaining_blocker_count"])

    def test_s2br_is_static_and_public_surfaces_remain_closed(self) -> None:
        audit = _audit()
        self.assertEqual(0, audit["privacy_acceptance"]["public_export_count"])
        self.assertEqual(
            0,
            audit["privacy_acceptance"][
                "field_snapshot_production_or_live_change_count"
            ],
        )
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))


if __name__ == "__main__":
    unittest.main()
