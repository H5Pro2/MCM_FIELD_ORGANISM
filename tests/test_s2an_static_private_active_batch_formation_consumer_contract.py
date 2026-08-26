from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_PACKAGE = _ROOT / "mcm_field_organism"
_ARTIFACT = (
    _ROOT
    / "docs"
    / (
        "S2AN_STATISCHER_PRIVATER_AKTIVBATCH_ZU_PPB1_"
        "BILDUNGSVERBRAUCHS_FUNKTIONS_PROVENIENZ_UND_"
        "FALSIFIKATIONSVERTRAG_V1.json"
    )
)
_BOUND = {
    "s2am_audit": (
        _ROOT
        / "docs"
        / "S2AM_STATISCHER_PRIVATER_AKTIVBATCH_BINDER_"
        "IMPLEMENTIERUNGS_UND_GRENZAUDIT_V1.json"
    ),
    "s2am_document": (
        _ROOT
        / "docs"
        / "S2AM_STATISCHER_PRIVATER_AKTIVBATCH_BINDER_"
        "IMPLEMENTIERUNGS_UND_GRENZAUDIT.md"
    ),
    "s2am_static_validator": (
        _ROOT
        / "tests"
        / "test_s2am_static_private_active_batch_binder_implementation_audit.py"
    ),
    "active_batch_binder": _PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "ppb1_reference": _PACKAGE / "_ppb1_reference.py",
    "ppb1_lifecycle": _PACKAGE / "_ppb1_s1wq_perceptual_state_lifecycle.py",
    "ppb1_read_only_probe": (
        _PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py"
    ),
    "ppb1_receptor_profiles": _PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_fixture_and_baseline_registry": (
        _PACKAGE / "_ppb1_s1xc_fixture_registry.py"
    ),
    "current_api": _PACKAGE / "current_api.py",
    "package_root": _PACKAGE / "__init__.py",
}


def _contract() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


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


class S2ANStaticPrivateActiveBatchFormationConsumerContractTests(
    unittest.TestCase
):
    def test_contract_digest_and_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_only_fresh_separate_modality_states_are_allowed(self) -> None:
        fresh = _contract()["fresh_bank_prestate_contract"]
        self.assertEqual(0, fresh["accepted_step_count"])
        self.assertIsNone(fresh["source_clock_id"])
        self.assertTrue(fresh["all_slots_free"])
        self.assertFalse(fresh["continuation_or_prefilled_state_allowed"])

    def test_one_use_authorization_is_explicit_and_not_hidden(self) -> None:
        contract = _contract()
        prestate = contract["one_use_authorization_prestate"]
        poststate = contract["one_use_authorization_poststate"]
        self.assertEqual(("AUTHORIZED", 0), (prestate["status"], prestate["use_count"]))
        self.assertEqual(("CONSUMED", 1), (poststate["status"], poststate["use_count"]))
        self.assertFalse(poststate["retry_from_consumed_state_allowed"])
        self.assertFalse(poststate["hidden_global_ledger_inside_pure_transition"])

    def test_schedule_and_per_frame_transition_are_exact(self) -> None:
        contract = _contract()
        schedule = contract["deterministic_frame_schedule"]
        self.assertEqual(4, len(schedule["sort_key_in_order"]))
        self.assertTrue(schedule["within_modality_original_order_must_be_preserved"])
        self.assertFalse(schedule["cross_modality_source_ticks_compared"])
        transition = contract["per_frame_transition_contract"]
        self.assertEqual("advance_s1wq_perceptual_state", transition["function"])
        self.assertEqual(1, transition["accepted_step_delta_per_call"])

    def test_atomic_fairness_falsification_and_claim_boundary_are_complete(
        self,
    ) -> None:
        contract = _contract()
        self.assertEqual(10, len(contract["atomic_validation_order"]))
        self.assertEqual(9, len(contract["fail_closed_error_roles"]))
        self.assertEqual(7, len(contract["fair_comparison_binding"]["comparison_arms"]))
        self.assertEqual(7, len(contract["falsification_and_stop_rules"]))
        self.assertTrue(
            all(
                value == 0
                for value in contract["contract_execution"].values()
            )
        )
        self.assertIn(
            "NO_CONSUMER_STORE_FUNCTION_RECOGNITION_FIELD_EFFECT_OR_MEMORY_RESULT",
            contract["claim_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
