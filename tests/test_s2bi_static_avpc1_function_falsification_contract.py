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
        "S2BI_AVPC1_STATISCHER_FUNKTIONS_KAUSALITAETS_PROVENIENZ_"
        "GEGENBASELINE_FALSIFIKATIONS_UND_STOPPVERTRAG_V1.json"
    )
)
BOUND = {
    "s2bh_selection_audit": (
        ROOT
        / "docs"
        / (
            "S2BH_STATISCHER_UNTERSCHEIDBARER_PERZEPTIVER_FUNKTIONSRAUM_"
            "UND_EINZELFUNKTIONS_AUSWAHLAUDIT_V1.json"
        )
    ),
    "receptor_time_alignment": PACKAGE / "receptor_time_alignment.py",
    "receptor_time_model": PACKAGE / "receptor_time_model.py",
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "receptor_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "read_only_perceptual_probe": (
        PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py"
    ),
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


class S2BIStaticAVPC1FunctionFalsificationContractTests(unittest.TestCase):
    def test_contract_digest_and_bound_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_crossed_histories_change_only_the_relation(self) -> None:
        contract = _contract()
        crossed = contract["crossed_history_contract"]
        self.assertEqual(
            "CROSSED_UNAMBIGUOUS_OVERLAP_RELATION",
            crossed["only_causal_difference"],
        )
        self.assertTrue(crossed["same_marginal_exposure_inventory"])
        self.assertTrue(crossed["same_later_auditory_a_key_cue"])
        self.assertTrue(crossed["no_later_visual_input"])

    def test_pair_provenance_forbids_forced_or_ambiguous_pairing(self) -> None:
        contract = _contract()
        provenance = contract["overlap_provenance_contract"]
        self.assertEqual(1, provenance["auditory_snapshot_overlap_degree_required"])
        self.assertEqual(1, provenance["visual_snapshot_overlap_degree_required"])
        self.assertFalse(provenance["external_pair_id_allowed"])
        self.assertFalse(provenance["post_capture_pair_repair_allowed"])
        self.assertFalse(provenance["ambiguous_overlap_forms_relation"])

    def test_strongest_baseline_and_no_overclaim_are_bound(self) -> None:
        contract = _contract()
        strongest = contract["baseline_forecasts"][-1]
        self.assertEqual(
            "CAPACITY_MATCHED_HETEROASSOCIATIVE_NEAREST_PROTOTYPE_TABLE",
            strongest["baseline_id"],
        )
        self.assertTrue(strongest["can_explain_crossed_forecast"])
        self.assertFalse(
            contract["interpretation_rules"]["function_success_is_memory_proof"]
        )
        self.assertTrue(all(value == 0 for value in contract["execution"].values()))


if __name__ == "__main__":
    unittest.main()
