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
        "S2AT_STATISCHER_BILDUNGSERGEBNIS_ZU_READ_ONLY_PROBE_"
        "KOMPATIBILITAETS_UND_LUECKENAUDIT_V1.json"
    )
)
BOUND = {
    "s2as_audit": (
        ROOT
        / "docs"
        / (
            "S2AS_STATISCHER_PRIVATER_BILDUNGSVERBRAUCHER_IMPLEMENTIERUNGS_"
            "DIGEST_ATOMARITAETS_UND_GRENZENAUDIT_V1.json"
        )
    ),
    "s2as_document": (
        ROOT
        / "docs"
        / (
            "S2AS_STATISCHER_PRIVATER_BILDUNGSVERBRAUCHER_IMPLEMENTIERUNGS_"
            "DIGEST_ATOMARITAETS_UND_GRENZENAUDIT.md"
        )
    ),
    "s2as_static_validator": (
        ROOT / "tests" / "test_s2as_static_private_formation_consumer_audit.py"
    ),
    "s2ar_consumer": PACKAGE / "_ppb1_active_batch_formation_consumer.py",
    "s2ar_tests": (
        ROOT / "tests" / "test_s2ar_private_active_batch_formation_consumer.py"
    ),
    "s1wu_probe": PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py",
    "s1wu_tests": (
        ROOT / "tests" / "test_ppb1_s1wu_read_only_perceptual_probe.py"
    ),
    "s1wv_audit": (
        ROOT / "docs" / "S1WV_PPB1_STATISCHER_READ_ONLY_PROBE_ABSCHLUSSAUDIT_V1.json"
    ),
    "ppb1_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "receptor_time": PACKAGE / "receptor_time_model.py",
    "current_api": PACKAGE / "current_api.py",
    "package_root": PACKAGE / "__init__.py",
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


def _tree(role: str) -> ast.Module:
    return ast.parse(BOUND[role].read_text(encoding="ascii"))


class S2ATStaticFormationToProbeCompatibilityAuditTests(unittest.TestCase):
    def test_artifact_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_formation_result_and_probe_signatures_are_structurally_compatible(
        self,
    ) -> None:
        formation = next(
            node
            for node in _tree("s2ar_consumer").body
            if isinstance(node, ast.ClassDef)
            and node.name == "PPB1ActiveBatchFormationResult"
        )
        fields = {
            node.target.id
            for node in formation.body
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
        }
        self.assertTrue(
            {"auditory_poststate", "visual_poststate"}.issubset(fields)
        )
        probe = next(
            node
            for node in _tree("s1wu_probe").body
            if isinstance(node, ast.FunctionDef)
            and node.name == "probe_s1wu_perceptual_state"
        )
        self.assertEqual(
            ["config", "state", "frame", "probe_id"],
            [argument.arg for argument in probe.args.args],
        )

    def test_current_fixture_does_not_guarantee_stabilized_eligibility(self) -> None:
        source = BOUND["s2ar_tests"].read_text(encoding="ascii")
        probe_source = BOUND["s1wu_probe"].read_text(encoding="ascii")
        self.assertIn("PPB1ModalityParameters(8, 0.02, 0.05, 3, 256)", source)
        self.assertIn("for index in range(2)", source)
        self.assertIn("slot.support_count >= config.stable_after", probe_source)
        self.assertFalse(
            _audit()["current_s2ar_fixture_limit"][
                "fixture_may_be_used_as_positive_recognition_fixture"
            ]
        )

    def test_three_handoff_blockers_prevent_implementation_or_execution(self) -> None:
        audit = _audit()
        self.assertEqual(3, audit["remaining_blocker_count"])
        self.assertTrue(
            all(item["status"] == "OPEN" for item in audit["handoff_blockers"])
        )
        self.assertFalse(
            audit["implementation_eligibility"][
                "direct_formation_result_to_probe_connector_eligible"
            ]
        )
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))


if __name__ == "__main__":
    unittest.main()
