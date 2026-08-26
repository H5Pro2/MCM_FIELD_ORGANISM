from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


_ROOT = Path(__file__).parents[1]
_PACKAGE = _ROOT / "mcm_field_organism"
_ARTIFACT = _ROOT / "docs" / "S2AE_STATISCHER_PRIORISIERUNGS_UND_LUECKENAUDIT_WAHRNEHMUNGSSPEICHER_ANSCHLUSS_V1.json"
_BOUND = {
    "s2ad_result": _ROOT / "docs" / "S2AD_AKTIVER_T0C_BROWSER_REZEPTOR_EINMALLAUF_UND_LAUFZEITKLASSIFIKATION_V1.json",
    "s2ad_document": _ROOT / "docs" / "S2AD_AKTIVER_T0C_BROWSER_REZEPTOR_EINMALLAUF_UND_LAUFZEITKLASSIFIKATION.md",
    "s2ad_receipt_test": _ROOT / "tests" / "test_s2ad_active_t0c_browser_receptor_static_receipt.py",
    "current_api": _PACKAGE / "current_api.py",
    "package_root": _PACKAGE / "__init__.py",
    "browser_receptor_bridge": _PACKAGE / "browser_receptor_bridge.py",
    "receptor_time_model": _PACKAGE / "receptor_time_model.py",
    "receptor_contract": _PACKAGE / "receptor_contract.py",
    "ppb1_reference": _PACKAGE / "_ppb1_reference.py",
    "ppb1_receptor_profiles": _PACKAGE / "_ppb1_receptor_profiles.py",
    "ppb1_lifecycle": _PACKAGE / "_ppb1_s1wq_perceptual_state_lifecycle.py",
    "ppb1_read_only_probe": _PACKAGE / "_ppb1_s1wu_read_only_perceptual_probe.py",
    "ppb1_temporal_result_closure": _ROOT / "docs" / "S1YC_PPB1_STATISCHER_RUNNER_UND_ERGEBNISABSCHLUSSAUDIT_V1.json",
    "ppb1_equivalence_audit": _ROOT / "docs" / "S1YE_PPB1_STATISCHER_NICHTDUPLIZIERUNGS_INFORMATIONS_UND_AEQUIVALENZAUDIT_V1.json",
    "ppb1_freshness_contract": _ROOT / "docs" / "S1WP_PPB1_FRISCHE_EINMALIGKEITS_UND_VERBRAUCHSVERTRAG_V1.json",
    "lprh1f_terminal_closure": _ROOT / "docs" / "S1ZN_LPRH1F_STATISCHER_PRIVATER_IMPLEMENTIERUNGS_RECEIPT_GRENZ_UND_ERGEBNISABSCHLUSSAUDIT_V1.json",
}


def _audit() -> dict[str, object]:
    return json.loads(_ARTIFACT.read_text(encoding="utf-8"))


def _canonical_digest(payload: dict[str, object]) -> str:
    value = dict(payload)
    value.pop("artifact_digest")
    encoded = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


class S2AEStaticPerceptualStoreConnectionPriorityAndGapAuditTests(unittest.TestCase):
    def test_audit_digest_and_all_bound_sources_are_exact(self) -> None:
        audit = _audit()
        self.assertEqual(_canonical_digest(audit), audit["artifact_digest"])
        for role, path in _BOUND.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), audit["bound_source_digests"][role])

    def test_no_explicit_active_sequence_to_ppb1_bridge_exists(self) -> None:
        files = list(_PACKAGE.glob("*.py"))
        hits = []
        for path in files:
            source = path.read_text(encoding="utf-8")
            if ("_ppb1" in source or "PPB1" in source) and any(name in source for name in ("BrowserReceptorSequenceBatch", "ReceptorTimeSequence", "CapturedAudioVideoNeutralFieldRun")):
                hits.append(path.name)
        inventory = _audit()["static_gap_inventory"]
        self.assertEqual(inventory["package_module_count"], len(files))
        self.assertEqual([], hits)

    def test_memory_connection_is_ranked_before_production_and_live(self) -> None:
        priorities = _audit()["priority_order"]
        self.assertEqual([1, 2, 3, 4], [item["rank"] for item in priorities])
        self.assertEqual("SELECT", priorities[0]["decision"])
        self.assertEqual("DEFER", priorities[1]["decision"])
        self.assertEqual("DEFER", priorities[2]["decision"])

    def test_selected_connection_preserves_frames_and_changes_no_state(self) -> None:
        connection = _audit()["selected_next_connection"]
        self.assertEqual("PPB1_PRIVATE_ACTIVE_RECEPTOR_BATCH_BINDING", connection["connection_id"])
        self.assertTrue(connection["frame_values_carrier_order_and_snapshot_identity_unchanged"])
        self.assertFalse(connection["state_advance_or_probe_call_allowed_during_binding"])
        self.assertFalse(connection["field_feedback_allowed"])
        self.assertFalse(connection["public_api_or_snapshot_change_allowed"])

    def test_synthetic_test_is_possible_without_production_or_live_input(self) -> None:
        fairness = _audit()["synthetic_fairness_path"]
        self.assertFalse(fairness["production_connection_required_before_test"])
        self.assertFalse(fairness["live_audio_video_required_before_test"])
        self.assertTrue(fairness["controlled_browser_batch_sufficient"])
        self.assertEqual(6, len(_audit()["comparison_baselines"]))
        self.assertTrue(all(value == 0 for value in _audit()["audit_execution"].values()))


if __name__ == "__main__":
    unittest.main()
