from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
ARTIFACT = (
    ROOT
    / "docs"
    / (
        "S2BU_AVPC1_VISUELLER_PROTOTYPZUSTANDS_RESOLVER_"
        "STATISCHER_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
    )
)
BOUND = {
    "s2bt_contract": (
        ROOT
        / "docs"
        / (
            "S2BT_AVPC1_PRIVATER_READ_ONLY_VISUELLER_PROTOTYPZUSTANDS_"
            "RESOLVERVERTRAG_V1.json"
        )
    ),
    "s2bt_document": (
        ROOT
        / "docs"
        / (
            "S2BT_AVPC1_PRIVATER_READ_ONLY_VISUELLER_PROTOTYPZUSTANDS_"
            "RESOLVERVERTRAG.md"
        )
    ),
    "bounded_relation": (
        ROOT / "mcm_field_organism" / "_avpc1_bounded_relation.py"
    ),
    "ppb1_reference": ROOT / "mcm_field_organism" / "_ppb1_reference.py",
    "receptor_profiles": (
        ROOT / "mcm_field_organism" / "_ppb1_receptor_profiles.py"
    ),
    "state_lifecycle": (
        ROOT
        / "mcm_field_organism"
        / "_ppb1_s1wq_perceptual_state_lifecycle.py"
    ),
    "read_only_probe": (
        ROOT
        / "mcm_field_organism"
        / "_ppb1_s1wu_read_only_perceptual_probe.py"
    ),
}


def _preflight() -> dict[str, object]:
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


class S2BUStaticAVPC1VisualPrototypeResolverPreflightTests(unittest.TestCase):
    def test_preflight_digest_and_bound_sources_are_exact(self) -> None:
        preflight = _preflight()
        self.assertEqual(_canonical_digest(preflight), preflight["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                preflight["bound_source_digests"][role],
            )

    def test_private_implementation_inventory_is_minimal(self) -> None:
        inventory = _preflight()["implementation_inventory"]
        self.assertEqual(1, inventory["private_error_type_count"])
        self.assertEqual(1, inventory["private_frozen_output_type_count"])
        self.assertEqual(1, inventory["private_resolver_function_count"])
        self.assertEqual(
            "mcm_field_organism/_avpc1_visual_prototype_resolver.py",
            inventory["target_module"],
        )

    def test_existing_rules_are_reused_without_new_selector(self) -> None:
        reuse = _preflight()["exact_reuse_plan"]
        self.assertEqual("REUSE", reuse["_validate_state"])
        self.assertEqual("REUSE", reuse["_state_identity_payload"])
        self.assertEqual("REUSE", reuse["_prototype_digest"])
        self.assertEqual("FORBIDDEN", reuse["new_distance_or_tie_rule"])
        self.assertEqual("FORBIDDEN", reuse["new_prototype_identity_rule"])
        self.assertEqual("FORBIDDEN", reuse["state_advance_call"])

    def test_materialization_and_test_boundaries_are_complete(self) -> None:
        preflight = _preflight()
        self.assertEqual(10, len(preflight["ordered_materialization_steps"]))
        self.assertEqual(8, len(preflight["synthetic_test_plan"]))
        self.assertEqual([], preflight["open_blockers"])
        self.assertTrue(preflight["implementation_materializable"])

    def test_preflight_performs_no_implementation_or_execution(self) -> None:
        preflight = _preflight()
        self.assertFalse(preflight["authorization"]["implemented"])
        self.assertFalse(preflight["authorization"]["executed"])
        self.assertFalse(preflight["authorization"]["field_or_public_path"])
        self.assertTrue(all(value == 0 for value in preflight["execution"].values()))


if __name__ == "__main__":
    unittest.main()
