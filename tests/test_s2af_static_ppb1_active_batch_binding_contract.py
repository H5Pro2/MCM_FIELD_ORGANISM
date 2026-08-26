from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_PACKAGE = _ROOT / "mcm_field_organism"
_ARTIFACT = _ROOT / "docs" / "S2AF_STATISCHER_PPB1_AKTIVBATCH_BINDUNGS_FUNKTIONS_PROVENIENZ_FAIRNESS_UND_FALSIFIKATIONSVERTRAG_V1.json"
_BOUND = {
    "s2ae_audit": _ROOT / "docs" / "S2AE_STATISCHER_PRIORISIERUNGS_UND_LUECKENAUDIT_WAHRNEHMUNGSSPEICHER_ANSCHLUSS_V1.json",
    "s2ae_document": _ROOT / "docs" / "S2AE_STATISCHER_PRIORISIERUNGS_UND_LUECKENAUDIT_WAHRNEHMUNGSSPEICHER_ANSCHLUSS.md",
    "s2ae_audit_test": _ROOT / "tests" / "test_s2ae_static_perceptual_store_connection_priority_and_gap_audit.py",
    "browser_receptor_bridge": _PACKAGE / "browser_receptor_bridge.py",
    "receptor_time_model": _PACKAGE / "receptor_time_model.py",
    "receptor_contract": _PACKAGE / "receptor_contract.py",
    "ppb1_reference": _PACKAGE / "_ppb1_reference.py",
    "ppb1_receptor_profiles": _PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_lifecycle": _PACKAGE / "_ppb1_s1wq_perceptual_state_lifecycle.py",
    "ppb1_read_only_probe": _PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py",
    "current_api": _PACKAGE / "current_api.py",
}


def _contract() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


class S2AFStaticPPB1ActiveBatchBindingContractTests(unittest.TestCase):
    def test_contract_digest_and_sources_are_exact(self) -> None:
        contract = _contract()
        self.assertEqual(_canonical_digest(contract), contract["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), contract["bound_source_digests"][role])

    def test_input_and_envelope_keep_two_modalities_separate(self) -> None:
        contract = _contract()
        self.assertEqual(["auditory", "visual"], contract["input_contract"]["required_modalities_in_order"])
        self.assertEqual(2, contract["input_contract"]["exact_sequence_count"])
        envelope = contract["future_envelope_anatomy"]
        self.assertIn("auditory_stream", envelope["top_level_roles"])
        self.assertIn("visual_stream", envelope["top_level_roles"])
        self.assertTrue(contract["immutability_and_atomicity"]["auditory_and_visual_streams_never_merged"])

    def test_provenance_extends_but_does_not_change_existing_projection(self) -> None:
        extension = _contract()["provenance_extension_over_existing_ppb1_input_projection"]
        self.assertIn("snapshot_id", extension["additional_binding_roles"])
        self.assertIn("field_clock_id", extension["additional_binding_roles"])
        self.assertFalse(extension["existing_ppb1_input_projection_changed"])
        self.assertFalse(extension["existing_frame_changed"])

    def test_binding_is_pure_atomic_and_fail_closed(self) -> None:
        contract = _contract()
        function = contract["proposed_future_function"]
        self.assertEqual((0, 0, 0, 0), (function["ppb1_advance_call_count"], function["ppb1_probe_call_count"], function["field_call_count"], function["filesystem_call_count"]))
        self.assertTrue(contract["immutability_and_atomicity"]["all_or_no_envelope"])
        self.assertEqual(11, len(contract["fail_closed_error_roles"]))

    def test_fairness_falsification_and_claim_boundary_are_complete(self) -> None:
        contract = _contract()
        self.assertEqual(7, len(contract["comparison_arms"]))
        self.assertTrue(contract["fairness_contract"]["same_envelope_digest_for_every_arm"])
        self.assertTrue(contract["fairness_contract"]["connector_result_cannot_count_as_functional_success"])
        self.assertEqual(7, len(contract["falsification_and_stop_rules"]))
        self.assertTrue(all(value == 0 for value in contract["contract_execution"].values()))
        self.assertIn("NO_BINDING_STORE_FUNCTION_FIELD_RESEARCH_OR_MEMORY_MECHANISM_RESULT", contract["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
