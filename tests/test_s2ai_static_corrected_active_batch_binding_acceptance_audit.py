from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_PACKAGE = _ROOT / "mcm_field_organism"
_ARTIFACT = _ROOT / "docs" / "S2AI_STATISCHER_KORRIGIERTER_AKTIVBATCH_BINDUNGS_ABNAHME_UND_IMPLEMENTIERUNGSFREIGABEAUDIT_V1.json"
_BOUND = {
    "s2ah_correction": _ROOT / "docs" / "S2AH_STATISCHE_S2AF_BROWSERWELT_QUELLBINDUNGS_VERTRAGSKORREKTUR_V1.json",
    "s2ah_document": _ROOT / "docs" / "S2AH_STATISCHE_S2AF_BROWSERWELT_QUELLBINDUNGS_VERTRAGSKORREKTUR.md",
    "s2ah_static_validator": _ROOT / "tests" / "test_s2ah_static_browser_world_source_binding_contract_correction.py",
    "s2af_contract": _ROOT / "docs" / "S2AF_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_FUNKTIONS_PROVENIENZ_FAIRNESS_UND_FALSIFIKATIONSVERTRAG_V1.json",
    "s2ag_audit": _ROOT / "docs" / "S2AG_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json",
    "receptor_time_model": _PACKAGE / "receptor_time_model.py",
    "receptor_contract": _PACKAGE / "receptor_contract.py",
    "ppb1_reference": _PACKAGE / "_ppb1_reference.py",
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


class S2AIStaticCorrectedActiveBatchBindingAcceptanceAuditTests(unittest.TestCase):
    def test_audit_digest_and_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_s2ag_contract_source_blocker_is_closed(self) -> None:
        closure = _audit()["s2ag_blocker_reaudit"]
        self.assertTrue(closure["contract_object_added_as_exact_input"])
        self.assertTrue(closure["contract_digest_is_independently_recomputable"])
        self.assertEqual("CLOSED_ON_CONTRACT_LEVEL", closure["status"])

    def test_pure_binder_does_not_gain_hidden_uniqueness_state(self) -> None:
        interpretation = _audit()["purity_and_call_budget_interpretation"]
        self.assertTrue(interpretation["binder_is_stateless_and_deterministic"])
        self.assertTrue(interpretation["allowed_call_count_per_binding_is_preregistered_caller_or_fixture_budget"])
        self.assertFalse(interpretation["binder_global_uniqueness_ledger_required"])
        self.assertFalse(interpretation["binder_consumes_input_or_authorization"])

    def test_one_source_clock_identity_role_remains_unbound(self) -> None:
        audit = _audit()
        gap = audit["remaining_time_identity_gap"]
        self.assertEqual(1, gap["count"])
        self.assertFalse(gap["facts"]["receptor_time_sequence_requires_source_clock_match_per_frame"])
        self.assertFalse(gap["facts"]["s2af_requires_one_source_clock_within_each_modality"])
        self.assertTrue(gap["facts"]["ppb1_bank_rejects_source_clock_change_after_first_accepted_frame"])
        self.assertFalse(audit["implementation_gate"]["private_binder_implementation_authorized"])

    def test_correction_and_execution_boundary_are_narrow(self) -> None:
        audit = _audit()
        correction = audit["required_static_correction"]
        self.assertTrue(correction["auditory_and_visual_source_clock_ids_may_differ"])
        self.assertTrue(correction["every_frame_source_clock_must_equal_its_stream_source_clock"])
        self.assertFalse(correction["new_numeric_parameter_required"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertIn("NO_CONNECTOR_STORE_FUNCTION_FIELD_EFFECT_OR_MEMORY_RESULT", audit["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
