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
        "S2BB_QUELLGEBUNDENER_AKTIVER_STATISCHER_PROTOTYPBASELINE_"
        "RECEIPT_UND_COMPARATOR_MATERIALISIERUNGSVERTRAG_V1.json"
    )
)
BOUND = {
    "s2ba_audit": (
        ROOT
        / "docs"
        / (
            "S2BA_STATISCHER_TECHNISCHER_WIEDERERKENNUNGS_BASELINE_"
            "BEREITSCHAFTS_UND_AUSWAHLAUDIT_V1.json"
        )
    ),
    "s1ww_complete_function_contract": (
        ROOT
        / "docs"
        / "S1WW_PPB1_VOLLSTAENDIGER_BILDUNGS_UND_PROBE_FUNKTIONSVERTRAG_V1.json"
    ),
    "active_batch_binding": PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "receptor_profiles": PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": PACKAGE / "_ppb1_reference.py",
    "formation_consumer": PACKAGE / "_ppb1_active_batch_formation_consumer.py",
    "formation_probe_handoff": (
        PACKAGE / "_ppb1_active_batch_formation_probe_handoff.py"
    ),
    "read_only_probe": PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py",
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


class S2BBStaticSourceBoundBaselineContractTests(unittest.TestCase):
    def test_contract_digest_and_bound_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_baseline_is_independent_single_prototype_and_read_only(self) -> None:
        contract = _contract()
        formation = contract["baseline_formation_rule"]
        probe = contract["baseline_probe_rule"]
        self.assertFalse(formation["candidate_poststate_access"])
        for role in (
            "support_counter",
            "stability_event",
            "slot_identity",
            "expiry",
            "replacement",
            "replay_archive",
        ):
            self.assertFalse(formation[role])
        self.assertTrue(probe["read_only"])

    def test_fairness_and_atomic_no_partial_result_are_bound(self) -> None:
        contract = _contract()
        fairness = contract["fair_budget_binding"]
        self.assertTrue(fairness["same_update_rate"])
        self.assertTrue(fairness["same_distance_metric"])
        self.assertTrue(fairness["same_match_threshold"])
        self.assertEqual(
            "EMIT_EXACTLY_ONE_COMPLETE_PAIRED_RECEIPT_OR_NO_RESULT",
            contract["atomic_materialization_order"][-1],
        )

    def test_no_advantage_classification_implementation_or_execution(self) -> None:
        contract = _contract()
        self.assertFalse(contract["comparator_contract"]["advantage_classification_available"])
        self.assertFalse(
            contract["current_fixture_prediction"][
                "registered_nontrivial_counterprediction"
            ]
        )
        self.assertFalse(
            contract["implementation_preconditions"][
                "implementation_or_execution_authorized_by_s2bb"
            ]
        )
        self.assertTrue(all(value == 0 for value in contract["execution"].values()))


if __name__ == "__main__":
    unittest.main()
