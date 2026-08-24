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
        "S2BS_AVPC1_PRIVATER_CONSUMER_WERTMATERIALISIERUNGS_UND_"
        "HANDOFF_LUECKENAUDIT_V1.json"
    )
)
BOUND = {
    "s2br_audit": (
        ROOT
        / "docs"
        / (
            "S2BR_AVPC1_BEGRENZTER_RELATIONSKERN_STATISCHER_"
            "IMPLEMENTIERUNGS_UND_GRENZEN_ABSCHLUSSAUDIT_V1.json"
        )
    ),
    "s2br_document": (
        ROOT
        / "docs"
        / (
            "S2BR_AVPC1_BEGRENZTER_RELATIONSKERN_STATISCHER_"
            "IMPLEMENTIERUNGS_UND_GRENZEN_ABSCHLUSSAUDIT.md"
        )
    ),
    "bounded_relation": PACKAGE / "_avpc1_bounded_relation.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "read_only_probe": PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py",
    "formation_consumer": PACKAGE / "_ppb1_active_batch_formation_consumer.py",
    "formation_probe_handoff": (
        PACKAGE / "_ppb1_active_batch_formation_probe_handoff.py"
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


def _class_fields(path: Path, class_name: str) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="ascii"))
    target = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    return tuple(
        node.target.id
        for node in target.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
    )


class S2BSStaticAVPC1ConsumerValueMaterializationGapAuditTests(
    unittest.TestCase
):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_existing_findings_return_identity_but_not_prototype_values(self) -> None:
        relation_fields = _class_fields(
            BOUND["bounded_relation"],
            "AVPC1ReadOnlyRelationFinding",
        )
        probe_fields = _class_fields(
            BOUND["read_only_probe"],
            "S1WUReadOnlyPerceptualFinding",
        )
        self.assertIn("visual_prototype_identity_digest", relation_fields)
        self.assertIn("selected_prototype_digest", probe_fields)
        self.assertNotIn("prototype_values", relation_fields)
        self.assertNotIn("prototype_values", probe_fields)

    def test_existing_value_outputs_do_not_fill_the_relation_gap(self) -> None:
        readout_fields = _class_fields(BOUND["ppb1_reference"], "PPB1Readout")
        formation_fields = _class_fields(
            BOUND["formation_consumer"],
            "PPB1ActiveBatchFormationResult",
        )
        handoff_fields = _class_fields(
            BOUND["formation_probe_handoff"],
            "PPB1ActiveBatchFormationProbeResult",
        )
        self.assertIn("prototype_values", readout_fields)
        self.assertIn("poststate_digest", readout_fields)
        self.assertIn("visual_poststate", formation_fields)
        self.assertNotIn("relation_finding", formation_fields)
        self.assertIn("visual_finding", handoff_fields)
        self.assertNotIn("prototype_values", handoff_fields)

    def test_exact_private_resolver_is_absent_and_one_gap_is_selected(self) -> None:
        sources = tuple(
            path.read_text(encoding="ascii")
            for role, path in BOUND.items()
            if role
            in {
                "bounded_relation",
                "ppb1_reference",
                "read_only_probe",
                "formation_consumer",
                "formation_probe_handoff",
            }
        )
        self.assertFalse(
            any(
                "resolve_avpc1_visual_prototype_state" in source
                for source in sources
            )
        )
        audit = _audit()
        self.assertEqual(1, audit["selected_gap_count"])
        self.assertEqual(
            "PRIVATE_READ_ONLY_VISUAL_PROTOTYPE_STATE_RESOLVER",
            audit["selected_next_component"]["role"],
        )

    def test_audit_adds_no_runtime_or_public_path(self) -> None:
        audit = _audit()
        self.assertFalse(audit["selected_next_component"]["implemented"])
        self.assertFalse(audit["selected_next_component"]["execution_authorized"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertEqual(0, audit["public_or_field_change_count"])


if __name__ == "__main__":
    unittest.main()
