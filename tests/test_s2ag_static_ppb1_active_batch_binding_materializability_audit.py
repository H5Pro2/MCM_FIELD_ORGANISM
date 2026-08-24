from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_PACKAGE = _ROOT / "mcm_field_organism"
_ARTIFACT = _ROOT / "docs" / "S2AG_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json"
_BOUND = {
    "s2af_contract": _ROOT / "docs" / "S2AF_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_FUNKTIONS_PROVENIENZ_FAIRNESS_UND_FALSIFIKATIONSVERTRAG_V1.json",
    "s2af_document": _ROOT / "docs" / "S2AF_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_FUNKTIONS_PROVENIENZ_FAIRNESS_UND_FALSIFIKATIONSVERTRAG.md",
    "s2af_static_validator": _ROOT / "tests" / "test_s2af_static_ppb1_active_batch_binding_contract.py",
    "browser_receptor_bridge": _PACKAGE / "browser_receptor_bridge.py",
    "browser_world_contract": _PACKAGE / "browser_world_contract.py",
    "receptor_time_model": _PACKAGE / "receptor_time_model.py",
    "receptor_contract": _PACKAGE / "receptor_contract.py",
    "ppb1_receptor_profiles": _PACKAGE / "_ppb1_receptor_profiles.py",
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


class S2AGStaticPPB1ActiveBatchMaterializabilityAuditTests(unittest.TestCase):
    def test_audit_digest_and_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                audit["bound_source_digests"][role],
            )

    def test_data_and_profile_side_are_materializable_without_conversion(self) -> None:
        checks = _audit()["materializability_checks"]
        self.assertTrue(all(checks.values()))
        boundary = _audit()["parameter_boundary"]
        self.assertFalse(boundary["new_connector_parameter_required"])
        self.assertTrue(boundary["incompatible_batch_geometry_or_carrier_order_must_fail_closed"])
        self.assertTrue(
            boundary["connector_may_not_choose_capacity_threshold_update_rate_stability_or_expiry"]
        )

    def test_acceptance_is_noncircular(self) -> None:
        self.assertTrue(all(_audit()["noncircularity_checks"].values()))

    def test_exact_contract_source_binding_has_one_input_blocker(self) -> None:
        audit = _audit()
        provenance = audit["provenance_findings"]
        self.assertTrue(provenance["browser_world_contract_id_and_digest_present_in_batch"])
        self.assertFalse(provenance["browser_world_contract_payload_present_in_batch"])
        self.assertFalse(provenance["s2af_function_receives_browser_world_contract"])
        self.assertFalse(
            provenance["browser_world_contract_digest_independently_recomputable_from_s2af_inputs"]
        )
        self.assertEqual(1, audit["blocking_gap"]["count"])
        self.assertFalse(audit["implementation_eligibility"]["s2af_as_written"])

    def test_correction_and_claim_boundary_remain_narrow(self) -> None:
        audit = _audit()
        self.assertEqual(4, len(audit["required_static_correction"]["next_function_input_set"]))
        self.assertFalse(
            audit["required_static_correction"]["changes_existing_browser_ppb_or_field_mechanics"]
        )
        self.assertTrue(all(value == 0 for value in audit["execution"].values()))
        self.assertIn("NO_CONNECTOR_STORE_FUNCTION_FIELD_EFFECT_OR_MEMORY_RESULT", audit["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
