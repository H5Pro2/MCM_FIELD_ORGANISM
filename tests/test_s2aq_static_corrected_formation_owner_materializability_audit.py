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
        "S2AQ_STATISCHER_KORRIGIERTER_BILDUNGSVERBRAUCHER_BESITZER_"
        "ABNAHME_KONKURRENZ_UND_MATERIALISIERBARKEITSAUDIT_V1.json"
    )
)
_BOUND = {
    "s2ap_correction": (
        _ROOT
        / "docs"
        / "S2AP_STATISCHE_PRIVATE_ATOMARE_BILDUNGSVERBRAUCHER_"
        "BESITZERKORREKTUR_V1.json"
    ),
    "s2ap_document": (
        _ROOT
        / "docs"
        / "S2AP_STATISCHE_PRIVATE_ATOMARE_BILDUNGSVERBRAUCHER_"
        "BESITZERKORREKTUR.md"
    ),
    "s2ap_static_validator": (
        _ROOT
        / "tests"
        / "test_s2ap_static_atomic_formation_consumer_owner_contract_correction.py"
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


def _audit() -> dict[str, object]:
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


class S2AQStaticCorrectedFormationOwnerMaterializabilityAuditTests(
    unittest.TestCase
):
    def test_audit_digest_and_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_s2ao_owner_blocker_is_closed_on_contract_level(self) -> None:
        closure = _audit()["s2ao_blocker_reaudit"]
        self.assertTrue(closure["owner_holds_authoritative_current_state"])
        self.assertTrue(closure["stale_alias_replay_against_same_owner_rejected"])
        self.assertEqual("CLOSED_ON_CONTRACT_LEVEL", closure["status"])

    def test_concurrent_recursive_and_terminal_calls_fail_before_lifecycle(
        self,
    ) -> None:
        concurrency = _audit()["concurrency_materialization"]
        self.assertEqual(
            "NONBLOCKING_ACQUIRE_AT_METHOD_ENTRY",
            concurrency["consume_lock_acquisition"],
        )
        self.assertEqual(
            0,
            concurrency[
                "concurrent_or_recursive_failed_acquisition_lifecycle_call_count"
            ],
        )
        self.assertEqual(0, concurrency["later_terminal_call_lifecycle_call_count"])
        self.assertFalse(concurrency["deadlock_required_for_reentrant_rejection"])

    def test_scope_and_future_test_roles_are_complete(self) -> None:
        audit = _audit()
        scope = audit["scope_limit_on_one_use"]
        self.assertEqual("ONE_TERMINAL_ATTEMPT_PER_OWNER_INSTANCE", scope["guaranteed"])
        self.assertEqual(3, len(scope["not_guaranteed"]))
        self.assertEqual(9, len(audit["required_synthetic_test_roles"]))
        self.assertEqual(0, audit["remaining_blocker_count"])

    def test_implementation_is_eligible_but_not_authorized_or_executed(self) -> None:
        audit = _audit()
        gate = audit["implementation_eligibility"]
        self.assertTrue(
            gate["private_owner_consumer_and_synthetic_tests_materializable"]
        )
        self.assertFalse(gate["implementation_authorized_in_s2aq"])
        self.assertTrue(
            gate["requires_separate_s2ar_implementation_authorization"]
        )
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertIn(
            "NO_OWNER_EXECUTION_STORE_FUNCTION_RECOGNITION_"
            "FIELD_EFFECT_OR_MEMORY_RESULT",
            audit["claim_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
