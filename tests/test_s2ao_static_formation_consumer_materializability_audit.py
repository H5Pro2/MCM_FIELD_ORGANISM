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
        "S2AO_STATISCHER_PPB1_BILDUNGSVERBRAUCHER_VOLLSTAENDIGKEITS_"
        "NICHTZIRKULARITAETS_EINMALIGKEITS_UND_"
        "MATERIALISIERBARKEITSAUDIT_V1.json"
    )
)
_BOUND = {
    "s2an_contract": (
        _ROOT
        / "docs"
        / (
            "S2AN_STATISCHER_PRIVATER_AKTIVBATCH_ZU_PPB1_"
            "BILDUNGSVERBRAUCHS_FUNKTIONS_PROVENIENZ_UND_"
            "FALSIFIKATIONSVERTRAG_V1.json"
        )
    ),
    "s2an_document": (
        _ROOT
        / "docs"
        / (
            "S2AN_STATISCHER_PRIVATER_AKTIVBATCH_ZU_PPB1_"
            "BILDUNGSVERBRAUCHS_FUNKTIONS_PROVENIENZ_UND_"
            "FALSIFIKATIONSVERTRAG.md"
        )
    ),
    "s2an_static_validator": (
        _ROOT
        / "tests"
        / "test_s2an_static_private_active_batch_formation_consumer_contract.py"
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


class S2AOStaticFormationConsumerMaterializabilityAuditTests(
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

    def test_schedule_lifecycle_and_local_atomicity_are_materializable(self) -> None:
        audit = _audit()
        parts = audit["materializable_contract_parts"]
        self.assertTrue(all(parts.values()))
        noncircular = audit["noncircularity_checks"]
        self.assertFalse(
            noncircular["schedule_depends_on_later_transition_or_probe_result"]
        )
        self.assertFalse(
            noncircular["authorization_depends_on_later_functional_result"]
        )
        self.assertFalse(
            noncircular[
                "formation_acceptance_depends_on_recognition_or_baseline_advantage"
            ]
        )
        self.assertTrue(noncircular["consumer_success_is_not_store_function_success"])
        self.assertTrue(noncircular["existing_lifecycle_rules_are_not_changed"])

    def test_value_only_authorization_cannot_enforce_one_use(self) -> None:
        audit = _audit()
        replay = audit["one_use_replay_analysis"]
        self.assertFalse(
            replay["old_authorized_object_is_invalidated_by_returning_poststate"]
        )
        self.assertTrue(replay["caller_can_resubmit_same_authorized_object"])
        self.assertFalse(
            replay["function_can_observe_an_authoritative_current_owner_state"]
        )
        self.assertFalse(replay["s2an_one_use_requirement_materializable_as_written"])
        self.assertEqual(1, audit["blocking_gap"]["count"])

    def test_owner_correction_is_narrow_and_implementation_stays_blocked(self) -> None:
        audit = _audit()
        correction = audit["required_static_correction"]
        self.assertEqual(7, len(correction["owner_rules"]))
        self.assertFalse(
            correction["owner_filesystem_or_production_persistence_allowed"]
        )
        self.assertFalse(correction["hidden_process_global_ledger_allowed"])
        self.assertFalse(audit["implementation_eligibility"]["s2an_as_written"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertIn(
            "NO_OWNER_CONSUMER_STORE_FUNCTION_RECOGNITION_"
            "FIELD_EFFECT_OR_MEMORY_RESULT",
            audit["claim_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
