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
        "S2BO_AVPC1_BEGRENZTER_RELATIONSZUSTANDS_KAPAZITAETS_SUPPORT_"
        "KONFLIKT_RECEIPT_UND_BASELINE_VERTRAG_V1.json"
    )
)
BOUND = {
    "s2bn_closure_audit": (
        ROOT
        / "docs"
        / "S2BN_AVPC1_AUDIO_ONLY_IMPLEMENTIERUNGS_UND_GRENZEN_ABSCHLUSSAUDIT_V1.json"
    ),
    "s2bi_function_contract": (
        ROOT
        / "docs"
        / (
            "S2BI_AVPC1_STATISCHER_FUNKTIONS_KAUSALITAETS_PROVENIENZ_"
            "GEGENBASELINE_FALSIFIKATIONS_UND_STOPPVERTRAG_V1.json"
        )
    ),
    "s2bj_materializability_audit": (
        ROOT
        / "docs"
        / (
            "S2BJ_AVPC1_STATISCHER_MATERIALISIERBARKEITSAUDIT_GEKREUZTE_"
            "GESCHICHTEN_UEBERLAPPUNG_PROVENIENZ_RAND_BUDGET_UND_BASELINES_V1.json"
        )
    ),
    "audio_only_envelope": PACKAGE / "_avpc1_audio_only_probe_envelope.py",
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "read_only_perceptual_probe": (
        PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py"
    ),
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "receptor_time_alignment": PACKAGE / "receptor_time_alignment.py",
    "receptor_time_model": PACKAGE / "receptor_time_model.py",
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


class S2BOStaticAVPC1BoundedRelationContractTests(unittest.TestCase):
    def test_contract_digest_and_bound_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_capacity_support_and_full_policy_are_exact(self) -> None:
        budget = _contract()["fixed_resource_budget"]
        self.assertEqual(2, budget["relation_slot_capacity"])
        self.assertEqual(2, budget["support_required_for_stable_relation"])
        self.assertEqual(4, budget["accepted_state_changing_exposure_budget"])
        self.assertEqual(
            "ATOMIC_REJECT_STATE_UNCHANGED",
            budget["full_capacity_new_key_policy"],
        )
        self.assertFalse(budget["replacement_or_eviction_allowed"])

    def test_slot_and_conflict_anatomy_are_total(self) -> None:
        contract = _contract()
        self.assertEqual(
            {"FREE", "PENDING", "STABLE", "CONFLICTED"},
            {slot["status"] for slot in contract["slot_states"]},
        )
        conflict = contract["conflict_policy"]
        self.assertTrue(conflict["conflict_is_absorbing_for_this_relation_state"])
        self.assertFalse(
            conflict["retry_confirmation_majority_vote_or_post_hoc_repair_allowed"]
        )

    def test_probe_is_audio_only_read_only_and_baseline_matched(self) -> None:
        contract = _contract()
        probe = contract["read_only_probe_contract"]
        self.assertFalse(probe["current_visual_frame_or_probe_allowed"])
        self.assertFalse(probe["relation_or_content_state_mutation_allowed"])
        strongest = contract["fair_baseline_materialization"][-1]
        self.assertEqual(
            "CAPACITY_MATCHED_HETEROASSOCIATIVE_EXACT_IDENTITY_TABLE",
            strongest["baseline_id"],
        )
        self.assertTrue(strongest["same_conflict_and_full_capacity_policy"])

    def test_contract_has_no_execution_or_claim(self) -> None:
        contract = _contract()
        self.assertEqual(
            0,
            contract["materialization_status"]["open_contract_blocker_count"],
        )
        self.assertFalse(
            contract["materialization_status"][
                "implementation_ready_without_preflight"
            ]
        )
        self.assertTrue(all(value == 0 for value in contract["execution"].values()))
        self.assertFalse(
            contract["decision_and_stop_rules"]["success_is_memory_proof"]
        )


if __name__ == "__main__":
    unittest.main()
