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
    / "S2AP_STATISCHE_PRIVATE_ATOMARE_BILDUNGSVERBRAUCHER_"
    "BESITZERKORREKTUR_V1.json"
)
_BOUND = {
    "s2ao_audit": (
        _ROOT
        / "docs"
        / (
            "S2AO_STATISCHER_PPB1_BILDUNGSVERBRAUCHER_VOLLSTAENDIGKEITS_"
            "NICHTZIRKULARITAETS_EINMALIGKEITS_UND_"
            "MATERIALISIERBARKEITSAUDIT_V1.json"
        )
    ),
    "s2ao_document": (
        _ROOT
        / "docs"
        / (
            "S2AO_STATISCHER_PPB1_BILDUNGSVERBRAUCHER_VOLLSTAENDIGKEITS_"
            "NICHTZIRKULARITAETS_EINMALIGKEITS_UND_"
            "MATERIALISIERBARKEITSAUDIT.md"
        )
    ),
    "s2ao_static_validator": (
        _ROOT
        / "tests"
        / "test_s2ao_static_formation_consumer_materializability_audit.py"
    ),
    "s2an_contract": (
        _ROOT
        / "docs"
        / (
            "S2AN_STATISCHER_PRIVATER_AKTIVBATCH_ZU_PPB1_"
            "BILDUNGSVERBRAUCHS_FUNKTIONS_PROVENIENZ_UND_"
            "FALSIFIKATIONSVERTRAG_V1.json"
        )
    ),
    "active_batch_binder": _PACKAGE / "_ppb1_active_receptor_batch_binding.py",
    "ppb1_reference": _PACKAGE / "_ppb1_reference.py",
    "ppb1_lifecycle": _PACKAGE / "_ppb1_s1wq_perceptual_state_lifecycle.py",
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


class S2APStaticAtomicFormationConsumerOwnerCorrectionTests(
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

    def test_owner_scope_is_instance_local_and_explicit(self) -> None:
        scope = _contract()["owner_scope_boundary"]
        self.assertFalse(scope["process_global_uniqueness_claimed"])
        self.assertFalse(scope["cross_process_uniqueness_claimed"])
        self.assertFalse(scope["filesystem_or_production_persistence"])
        self.assertTrue(
            scope[
                "future_controlled_runner_must_create_exactly_one_owner_"
                "per_registered_authorization"
            ]
        )

    def test_preflight_rejection_does_not_begin_an_attempt(self) -> None:
        preflight = _contract()["preflight_without_consumption"]
        self.assertEqual(0, preflight["lifecycle_call_count"])
        self.assertFalse(preflight["owner_state_change_on_rejection"])
        self.assertEqual(5, len(preflight["checks"]))

    def test_started_attempt_has_exactly_one_terminal_outcome(self) -> None:
        transition = _contract()["terminal_attempt_transition"]
        success = transition["success_transition"]
        failure = transition["failure_after_attempt_begin_transition"]
        self.assertEqual(("CONSUMED", 1, 1), (
            success["status"], success["attempt_count"], success["use_count"]
        ))
        self.assertEqual(("FAILED", 1, 0), (
            failure["status"], failure["attempt_count"], failure["use_count"]
        ))
        self.assertFalse(transition["retry_from_consumed_or_failed_allowed"])

    def test_atomicity_blocker_and_execution_boundary_are_narrow(self) -> None:
        contract = _contract()
        self.assertEqual(6, len(contract["atomic_commit_rules"]))
        self.assertFalse(contract["closed_blocker"]["implementation_closure_claimed"])
        self.assertFalse(
            contract["implementation_gate"][
                "owner_consumer_or_test_implementation_authorized_in_s2ap"
            ]
        )
        self.assertTrue(all(value == 0 for value in contract["execution"].values()))
        self.assertIn(
            "NO_OWNER_EXECUTION_STORE_FUNCTION_RECOGNITION_"
            "FIELD_EFFECT_OR_MEMORY_RESULT",
            contract["claim_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
