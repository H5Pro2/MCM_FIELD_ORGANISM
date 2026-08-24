from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_PACKAGE = _ROOT / "mcm_field_organism"
_ARTIFACT = _ROOT / "docs" / "S2AJ_STATISCHE_MODALITAETSINTERNE_QUELLCLOCK_IDENTITAETS_VERTRAGSKORREKTUR_V1.json"
_BOUND = {
    "s2ai_audit": _ROOT / "docs" / "S2AI_STATISCHER_KORRIGIERTER_AKTIVBATCH_BINDUNGS_ABNAHME_UND_IMPLEMENTIERUNGSFREIGABEAUDIT_V1.json",
    "s2ai_document": _ROOT / "docs" / "S2AI_STATISCHER_KORRIGIERTER_AKTIVBATCH_BINDUNGS_ABNAHME_UND_IMPLEMENTIERUNGSFREIGABEAUDIT.md",
    "s2ai_static_validator": _ROOT / "tests" / "test_s2ai_static_corrected_active_batch_binding_acceptance_audit.py",
    "s2ah_correction": _ROOT / "docs" / "S2AH_STATISCHE_S2AF_BROWSERWELT_QUELLBINDUNGS_VERTRAGSKORREKTUR_V1.json",
    "s2af_contract": _ROOT / "docs" / "S2AF_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_FUNKTIONS_PROVENIENZ_FAIRNESS_UND_FALSIFIKATIONSVERTRAG_V1.json",
    "receptor_time_model": _PACKAGE / "receptor_time_model.py",
    "receptor_contract": _PACKAGE / "receptor_contract.py",
    "ppb1_reference": _PACKAGE / "_ppb1_reference.py",
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


class S2AJStaticWithinModalitySourceClockCorrectionTests(unittest.TestCase):
    def test_contract_digest_and_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_clock_is_derived_per_stream_without_external_parameter(self) -> None:
        clock = _contract()["source_clock_identity_contract"]
        self.assertFalse(clock["external_source_clock_parameter_allowed"])
        self.assertTrue(clock["every_frame_clock_equals_its_stream_source_clock"])
        self.assertTrue(clock["auditory_and_visual_source_clocks_may_differ"])
        self.assertFalse(clock["source_ticks_compared_across_modalities"])
        self.assertFalse(clock["source_ticks_compared_across_different_clocks"])

    def test_source_window_end_advances_but_overlap_remains_allowed(self) -> None:
        clock = _contract()["source_clock_identity_contract"]
        self.assertTrue(clock["source_window_end_must_strictly_advance_within_stream_clock"])
        self.assertFalse(clock["source_window_overlap_forbidden"])

    def test_digest_and_failure_rules_are_atomic(self) -> None:
        contract = _contract()
        digest = contract["digest_correction"]
        self.assertTrue(digest["stream_canonical_payload_includes_source_clock_id"])
        self.assertFalse(digest["existing_batch_digest_changed"])
        failure = contract["fail_closed_addition"]
        self.assertEqual("NONE", failure["output"])
        self.assertFalse(failure["partial_stream_or_envelope_allowed"])

    def test_blocker_closes_only_on_contract_level(self) -> None:
        contract = _contract()
        self.assertFalse(contract["closed_blocker"]["implementation_closure_claimed"])
        self.assertFalse(contract["implementation_gate"]["private_binder_implementation_authorized_in_s2aj"])
        self.assertTrue(all(value == 0 for value in contract["execution"].values()))
        self.assertIn("NO_CONNECTOR_STORE_FUNCTION_FIELD_EFFECT_OR_MEMORY_RESULT", contract["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
