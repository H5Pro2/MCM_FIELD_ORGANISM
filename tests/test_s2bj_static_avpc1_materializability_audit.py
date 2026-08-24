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
    / (
        "S2BJ_AVPC1_STATISCHER_MATERIALISIERBARKEITSAUDIT_GEKREUZTE_"
        "GESCHICHTEN_UEBERLAPPUNG_PROVENIENZ_RAND_BUDGET_UND_BASELINES_V1.json"
    )
)
BOUND = {
    "s2bi_contract": (
        ROOT
        / "docs"
        / (
            "S2BI_AVPC1_STATISCHER_FUNKTIONS_KAUSALITAETS_PROVENIENZ_"
            "GEGENBASELINE_FALSIFIKATIONS_UND_STOPPVERTRAG_V1.json"
        )
    ),
    "receptor_time_alignment": PACKAGE / "receptor_time_alignment.py",
    "receptor_time_model": PACKAGE / "receptor_time_model.py",
    "browser_receptor_bridge": PACKAGE / "browser_receptor_bridge.py",
    "browser_world_contract": PACKAGE / "browser_world_contract.py",
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "receptor_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "formation_consumer": PACKAGE / "_ppb1_active_batch_formation_consumer.py",
    "read_only_perceptual_probe": (
        PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py"
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


class S2BJStaticAVPC1MaterializabilityAuditTests(unittest.TestCase):
    def test_audit_digest_and_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_crossed_window_witness_is_one_to_one_and_margin_matched(self) -> None:
        audit = _audit()
        witness = audit["p2_crossed_window_witness"]
        self.assertEqual(1, witness["auditory_overlap_degree_per_snapshot"])
        self.assertEqual(1, witness["visual_overlap_degree_per_snapshot"])
        self.assertEqual(0, witness["ambiguous_snapshot_count"])
        self.assertEqual(0, witness["unmatched_snapshot_count"])
        self.assertTrue(witness["same_auditory_marginal_inventory"])
        self.assertTrue(witness["same_visual_marginal_inventory"])

    def test_exactly_one_audio_only_binding_blocker_is_open(self) -> None:
        audit = _audit()
        probe = audit["p4_audio_only_probe_binding_audit"]
        self.assertFalse(
            probe[
                "honest_no_visual_input_is_representable_by_current_active_batch_envelope"
            ]
        )
        self.assertEqual("BLOCKED", probe["status"])
        self.assertEqual(1, audit["open_blocker_count"])
        self.assertFalse(audit["materializability_summary"]["avpc1_function_stopped"])

    def test_no_registration_implementation_execution_or_claim(self) -> None:
        audit = _audit()
        self.assertTrue(
            audit["relation_capacity_and_budget_materializability"][
                "concrete_capacity_and_confirmation_values_are_not_registered_by_this_audit"
            ]
        )
        self.assertFalse(
            audit["implementation_readiness"]["implementation_or_execution_authorized"]
        )
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))


if __name__ == "__main__":
    unittest.main()
