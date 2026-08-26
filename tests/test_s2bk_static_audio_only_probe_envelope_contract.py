from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "mcm_field_organism"
ARTIFACT = (
    ROOT
    / "docs"
    / "S2BK_AVPC1_PRIVATER_AUDIO_ONLY_PROBENHUELLENVERTRAG_V1.json"
)
BOUND = {
    "s2bj_materializability_audit": (
        ROOT
        / "docs"
        / (
            "S2BJ_AVPC1_STATISCHER_MATERIALISIERBARKEITSAUDIT_GEKREUZTE_"
            "GESCHICHTEN_UEBERLAPPUNG_PROVENIENZ_RAND_BUDGET_UND_BASELINES_V1.json"
        )
    ),
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "receptor_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "read_only_perceptual_probe": (
        PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py"
    ),
    "receptor_time_model": PACKAGE / "receptor_time_model.py",
    "receptor_contract": PACKAGE / "receptor_contract.py",
    "browser_receptor_bridge": PACKAGE / "browser_receptor_bridge.py",
    "browser_world_contract": PACKAGE / "browser_world_contract.py",
    "current_api": PACKAGE / "current_api.py",
    "package_root": PACKAGE / "__init__.py",
    "shared_field": PACKAGE / "shared_mcm_field.py",
}


def _contract() -> dict[str, object]:
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


class S2BKStaticAudioOnlyProbeEnvelopeContractTests(unittest.TestCase):
    def test_contract_digest_and_bound_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_anatomy_is_exactly_one_auditory_and_zero_visual(self) -> None:
        anatomy = _contract()["auditory_sequence_anatomy"]
        self.assertEqual(1, anatomy["sequence_count"])
        self.assertEqual(1, anatomy["timed_frame_count"])
        self.assertEqual(0, anatomy["visual_sequence_count"])
        self.assertEqual(0, anatomy["visual_frame_count"])
        self.assertEqual(0, anatomy["visual_projection_digest_count"])

    def test_provenance_cannot_be_used_as_matching_feature(self) -> None:
        contract = _contract()
        source = contract["private_auditory_source_binding_anatomy"]
        split = contract["consumer_visibility_split"]
        self.assertFalse(source["external_loose_fields_can_replace_binding"])
        self.assertFalse(split["provenance_metadata_can_change_matching_result"])
        self.assertIn(
            "ANY_VISUAL_VALUE_IDENTITY_OR_DIGEST",
            split["read_only_auditory_matcher_must_not_receive"],
        )

    def test_contract_is_static_and_requires_preflight(self) -> None:
        contract = _contract()
        invariants = contract["invariants"]
        self.assertTrue(
            all(
                value == 0
                for value in (
                    invariants["state_advance_count"],
                    invariants["probe_execution_count"],
                    invariants["field_call_count"],
                    invariants["public_api_change_count"],
                )
            )
        )
        self.assertFalse(
            contract["materializability_decision"][
                "implementation_ready_without_preflight"
            ]
        )


if __name__ == "__main__":
    unittest.main()
