from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_PACKAGE = _ROOT / "mcm_field_organism"
_ARTIFACT = _ROOT / "docs" / "S2AH_STATISCHE_S2AF_BROWSERWELT_QUELLBINDUNGS_VERTRAGSKORREKTUR_V1.json"
_BOUND = {
    "s2ag_audit": _ROOT / "docs" / "S2AG_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json",
    "s2ag_document": _ROOT / "docs" / "S2AG_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT.md",
    "s2ag_static_validator": _ROOT / "tests" / "test_s2ag_static_ppb1_active_batch_binding_materializability_audit.py",
    "s2af_contract": _ROOT / "docs" / "S2AF_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_FUNKTIONS_PROVENIENZ_FAIRNESS_UND_FALSIFIKATIONSVERTRAG_V1.json",
    "browser_world_contract": _PACKAGE / "browser_world_contract.py",
    "browser_receptor_bridge": _PACKAGE / "browser_receptor_bridge.py",
    "ppb1_receptor_profiles": _PACKAGE / "_ppb1_receptor_profiles.py",
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


class S2AHStaticBrowserWorldSourceBindingCorrectionTests(unittest.TestCase):
    def test_contract_digest_and_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                contract["bound_source_digests"][role],
            )

    def test_only_function_inputs_and_source_validation_are_superseded(self) -> None:
        scope = _contract()["supersession_scope"]
        self.assertFalse(scope["historical_s2af_artifact_changed"])
        self.assertTrue(scope["replaces_only_s2af_proposed_future_function_inputs"])
        self.assertTrue(scope["strengthens_only_contract_source_validation_and_fail_closed_order"])
        self.assertTrue(scope["all_other_s2af_roles_remain_bound"])

    def test_corrected_function_has_exact_authoritative_source(self) -> None:
        contract = _contract()
        function = contract["corrected_future_function"]
        self.assertEqual(4, len(function["inputs_in_order"]))
        self.assertEqual("BrowserWorldContract", function["added_input"])
        source = contract["authoritative_contract_source"]
        self.assertEqual("BrowserWorldContract", source["required_exact_type"])
        self.assertFalse(source["external_contract_id_allowed"])
        self.assertFalse(source["external_expected_digest_allowed"])
        self.assertFalse(source["unverified_batch_contract_digest_allowed"])

    def test_contract_id_and_digest_are_checked_before_envelope(self) -> None:
        order = _contract()["corrected_validation_order"]
        id_index = order.index("REQUIRE_CONTRACT_ID_EQUALS_BATCH_CONTRACT_ID")
        digest_index = order.index("REQUIRE_RECOMPUTED_CONTRACT_DIGEST_EQUALS_BATCH_CONTRACT_DIGEST")
        build_index = order.index("BUILD_ALL_STREAM_AND_FRAME_PROVENANCE_VALUES_PRIVATELY")
        self.assertLess(id_index, build_index)
        self.assertLess(digest_index, build_index)
        self.assertEqual(7, len(_contract()["corrected_fail_closed_matrix"]))

    def test_blocker_is_closed_only_on_contract_level(self) -> None:
        contract = _contract()
        self.assertFalse(contract["closed_blocker"]["implementation_closure_claimed"])
        self.assertFalse(contract["implementation_gate"]["connector_implementation_authorized_in_s2ah"])
        self.assertTrue(
            contract["implementation_gate"]["requires_separate_static_s2ai_acceptance_and_reauthorization_audit"]
        )
        self.assertTrue(all(value == 0 for value in contract["execution"].values()))
        self.assertIn("NO_CONNECTOR_STORE_FUNCTION_FIELD_EFFECT_OR_MEMORY_RESULT", contract["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
