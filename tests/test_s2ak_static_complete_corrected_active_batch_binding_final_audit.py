from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_PACKAGE = _ROOT / "mcm_field_organism"
_ARTIFACT = _ROOT / "docs" / "S2AK_STATISCHER_VOLLSTAENDIG_KORRIGIERTER_AKTIVBATCH_BINDUNGS_ABSCHLUSSAUDIT_V1.json"
_BOUND = {
    "s2aj_correction": _ROOT / "docs" / "S2AJ_STATISCHE_MODALITAETSINTERNE_QUELLCLOCK_IDENTITAETS_VERTRAGSKORREKTUR_V1.json",
    "s2aj_document": _ROOT / "docs" / "S2AJ_STATISCHE_MODALITAETSINTERNE_QUELLCLOCK_IDENTITAETS_VERTRAGSKORREKTUR.md",
    "s2aj_static_validator": _ROOT / "tests" / "test_s2aj_static_within_modality_source_clock_contract_correction.py",
    "s2ah_correction": _ROOT / "docs" / "S2AH_STATISCHE_S2AF_BROWSERWELT_QUELLBINDUNGS_VERTRAGSKORREKTUR_V1.json",
    "s2af_contract": _ROOT / "docs" / "S2AF_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_FUNKTIONS_PROVENIENZ_FAIRNESS_UND_FALSIFIKATIONSVERTRAG_V1.json",
    "browser_world_contract": _PACKAGE / "browser_world_contract.py",
    "browser_receptor_bridge": _PACKAGE / "browser_receptor_bridge.py",
    "receptor_time_model": _PACKAGE / "receptor_time_model.py",
    "receptor_contract": _PACKAGE / "receptor_contract.py",
    "ppb1_receptor_profiles": _PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_reference": _PACKAGE / "_ppb1_reference.py",
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


class S2AKStaticCompleteCorrectedActiveBatchBindingFinalAuditTests(unittest.TestCase):
    def test_audit_digest_and_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_both_prior_blockers_are_closed_and_none_remain(self) -> None:
        audit = _audit()
        self.assertEqual(2, len(audit["closed_blockers"]))
        self.assertEqual(0, audit["remaining_blocker_count"])
        self.assertEqual(4, len(audit["complete_input_roles_in_order"]))

    def test_all_output_roles_have_authoritative_materialization(self) -> None:
        audit = _audit()
        self.assertEqual(15, len(audit["complete_role_materialization"]))
        self.assertTrue(audit["complete_output_anatomy"]["all_value_types_frozen_and_slotted"])
        self.assertFalse(audit["complete_output_anatomy"]["envelope_contains_raw_payload_or_field_snapshot"])

    def test_binding_remains_pure_private_and_noncircular(self) -> None:
        audit = _audit()
        purity = audit["noncircularity_and_purity"]
        self.assertFalse(purity["acceptance_depends_on_store_formation_or_probe_result"])
        self.assertFalse(purity["binder_calls_ppb1_advance_or_probe"])
        self.assertFalse(purity["binder_has_global_uniqueness_or_consumption_ledger"])
        boundary = audit["private_implementation_boundary"]
        self.assertFalse(boundary["public_api_export_allowed"])
        self.assertFalse(boundary["package_root_export_allowed"])

    def test_implementation_is_eligible_but_not_yet_authorized(self) -> None:
        audit = _audit()
        gate = audit["implementation_eligibility"]
        self.assertTrue(gate["private_binder_and_synthetic_contract_tests_materializable"])
        self.assertEqual(0, gate["remaining_static_contract_blocker_count"])
        self.assertFalse(gate["implementation_authorized_in_s2ak"])
        self.assertTrue(gate["requires_separate_s2al_implementation_authorization"])
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertIn("NO_CONNECTOR_EXECUTION_STORE_FUNCTION_FIELD_EFFECT_OR_MEMORY_RESULT", audit["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
