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
        "S2AU_STATISCHER_BILDUNG_ZU_SPAETER_READ_ONLY_PROBE_HANDOFF_"
        "FUNKTIONS_PROVENIENZ_STABILISIERUNGS_PARTITIONS_UND_"
        "FALSIFIKATIONSVERTRAG_V1.json"
    )
)
BOUND = {
    "s2at_audit": (
        ROOT
        / "docs"
        / (
            "S2AT_STATISCHER_BILDUNGSERGEBNIS_ZU_READ_ONLY_PROBE_"
            "KOMPATIBILITAETS_UND_LUECKENAUDIT_V1.json"
        )
    ),
    "s2at_document": (
        ROOT
        / "docs"
        / (
            "S2AT_STATISCHER_BILDUNGSERGEBNIS_ZU_READ_ONLY_PROBE_"
            "KOMPATIBILITAETS_UND_LUECKENAUDIT.md"
        )
    ),
    "s2at_static_validator": (
        ROOT / "tests" / "test_s2at_static_formation_to_probe_compatibility_audit.py"
    ),
    "formation_consumer": PACKAGE / "_ppb1_active_batch_formation_consumer.py",
    "active_batch_binder": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "read_only_probe": PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py",
    "ppb1_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "receptor_time": PACKAGE / "receptor_time_model.py",
    "current_api": PACKAGE / "current_api.py",
    "package_root": PACKAGE / "__init__.py",
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


class S2AUStaticFormationToLaterProbeHandoffContractTests(unittest.TestCase):
    def test_contract_digest_and_bound_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_profile_stabilization_and_later_probe_close_s2at_contract_gaps(
        self,
    ) -> None:
        closure = _contract()["s2at_blocker_contract_closure"]
        self.assertTrue(closure["profile_config_source_bound"])
        self.assertTrue(closure["stabilized_formation_eligibility_bound"])
        self.assertTrue(closure["separate_causally_later_probe_exposure_bound"])
        self.assertEqual("STATIC_CONTRACT_ONLY", closure["closure_level"])
        self.assertFalse(closure["implementation_closure_claimed"])

    def test_partition_is_causal_disjoint_and_computed_before_findings(self) -> None:
        contract = _contract()
        later = contract["later_probe_envelope_binding"]
        partition = contract["partition_binding"]
        self.assertTrue(later["probe_source_window_start_at_or_after_formation_end"])
        self.assertTrue(later["probe_source_window_end_strictly_after_formation_end"])
        self.assertTrue(later["formation_and_probe_snapshot_pairs_disjoint"])
        self.assertTrue(partition["computed_before_probe_calls"])
        self.assertFalse(partition["depends_on_probe_findings"])

    def test_result_is_read_only_complete_and_not_a_functional_decision(self) -> None:
        contract = _contract()
        result = contract["complete_result_anatomy"]
        self.assertTrue(result["postprobe_state_digests_equal_preprobe_state_digests"])
        self.assertFalse(result["contains_bank_state_or_prototype_values"])
        self.assertFalse(result["partial_single_modality_result_observable"])
        probe_contract = contract["per_modality_probe_contract"]
        self.assertTrue(
            probe_contract[
                "recognized_value_may_be_true_or_false_"
                "without_changing_handoff_validity"
            ]
        )

    def test_implementation_and_every_execution_role_remain_zero(self) -> None:
        contract = _contract()
        gate = contract["implementation_gate"]
        self.assertFalse(gate["implementation_authorized_in_s2au"])
        self.assertTrue(all(value == 0 for value in contract["execution"].values()))


if __name__ == "__main__":
    unittest.main()
