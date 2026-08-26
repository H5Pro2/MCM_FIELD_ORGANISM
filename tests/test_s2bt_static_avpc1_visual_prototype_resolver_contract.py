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
        "S2BT_AVPC1_PRIVATER_READ_ONLY_VISUELLER_PROTOTYPZUSTANDS_"
        "RESOLVERVERTRAG_V1.json"
    )
)
BOUND = {
    "s2bs_audit": (
        ROOT
        / "docs"
        / (
            "S2BS_AVPC1_PRIVATER_CONSUMER_WERTMATERIALISIERUNGS_UND_"
            "HANDOFF_LUECKENAUDIT_V1.json"
        )
    ),
    "s2bs_document": (
        ROOT
        / "docs"
        / (
            "S2BS_AVPC1_PRIVATER_CONSUMER_WERTMATERIALISIERUNGS_UND_"
            "HANDOFF_LUECKENAUDIT.md"
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


def _contract() -> dict[str, object]:
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


class S2BTStaticAVPC1VisualPrototypeResolverContractTests(unittest.TestCase):
    def test_contract_digest_and_bound_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_input_and_output_roles_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(
            [
                "resolver_id",
                "relation_finding",
                "relation_state",
                "profile",
                "visual_bank_state",
            ],
            contract["resolver_signature"]["ordered_inputs"],
        )
        self.assertEqual(
            [
                "resolver_id",
                "relation_finding_digest",
                "relation_state_identity_digest",
                "observed_relation_state_digest",
                "profile_binding_digest",
                "visual_bank_config_digest",
                "visual_bank_state_identity_digest",
                "visual_bank_state_digest",
                "relation_slot_id",
                "visual_prototype_slot_id",
                "visual_prototype_identity_digest",
                "modality_id",
                "geometry_id",
                "carrier_ids",
                "prototype_values",
                "support_count",
                "resolved_state_digest",
            ],
            contract["output_contract"]["ordered_fields"],
        )

    def test_exact_identity_resolution_has_no_search_or_update(self) -> None:
        contract = _contract()
        resolution = contract["resolution_rule"]
        self.assertEqual("EXACT_SHA256_PROTOTYPE_IDENTITY", resolution["selector"])
        self.assertEqual(1, resolution["required_matching_stable_slot_count"])
        self.assertFalse(resolution["distance_search_allowed"])
        self.assertFalse(resolution["tie_rule_allowed"])
        self.assertFalse(resolution["prototype_update_allowed"])
        self.assertFalse(resolution["value_conversion_allowed"])

    def test_all_source_and_fail_closed_roles_are_bound(self) -> None:
        contract = _contract()
        self.assertEqual(10, len(contract["ordered_validation_roles"]))
        failures = contract["fail_closed_contract"]
        for role in (
            "NON_MATCH_OR_CONFLICT_FINDING",
            "RELATION_STATE_MISMATCH",
            "PROFILE_OR_VISUAL_BANK_MISMATCH",
            "TARGET_ABSENT",
            "TARGET_DUPLICATED",
            "TARGET_UNSTABLE",
            "SOURCE_MUTATION",
        ):
            self.assertIn(role, failures)
            self.assertEqual("NO_OUTPUT", failures[role])

    def test_contract_keeps_implementation_and_field_closed(self) -> None:
        contract = _contract()
        self.assertFalse(contract["authorization"]["implementation"])
        self.assertFalse(contract["authorization"]["execution"])
        self.assertFalse(contract["authorization"]["public_api"])
        self.assertFalse(contract["authorization"]["field_or_production_path"])
        self.assertTrue(all(value == 0 for value in contract["execution"].values()))


if __name__ == "__main__":
    unittest.main()
