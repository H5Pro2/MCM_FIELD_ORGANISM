from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    ROOT
    / "docs/S1YD_PPB1_STATISCHE_ENGINEERINGEINORDNUNG_UND_DYNAMISCHE_BASELINEAUSWAHL_V1.json"
)
EXPECTED_AUDIT_DIGEST = "f80050b014c1fde4f176af67df040569c98072d7198121eb947771dd526efff0"


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


class PPB1S1YDStaticDynamicBaselineSelectionTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "31467bcb43e00bee39b0930380ee39868c1534a94dbed7b910973b71c41222fa",
            audit["parent_s1yc_canonical_audit_digest"],
        )
        paths = {
            "s1yc_audit": "docs/S1YC_PPB1_STATISCHER_RUNNER_UND_ERGEBNISABSCHLUSSAUDIT_V1.json",
            "s1yc_document": "docs/S1YC_PPB1_STATISCHER_RUNNER_UND_ERGEBNISABSCHLUSSAUDIT.md",
            "s1yb_document": "docs/S1YB_PPB1_PRIVATER_ZEITLICHER_AKTUALISIERUNGSVERGLEICH.md",
            "s1xu_contract": "docs/S1XU_PPB1_STATISCHER_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_ZEITLICHE_AKTUALISIERUNG.md",
            "s1xz_fixture_document": "docs/S1XZ_PPB1_PRIVATE_ZEITLICHE_AKTUALISIERUNGSFIXTURE_UND_VALIDATOR.md",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wq_lifecycle": "mcm_field_organism/_ppb1_s1wq_perceptual_state_lifecycle.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                audit["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_s1yb_value_and_comparison_limit_are_separate(self) -> None:
        value = load_audit()["s1yb_engineering_value"]
        self.assertEqual(4, len(value["confirmed_roles"]))
        self.assertEqual(
            "STATIC_BASELINE_CANNOT_EXPRESS_THE_TESTED_UPDATE_FUNCTION",
            value["comparison_limit"],
        )
        self.assertFalse(value["competitive_mechanism_evidence"])

    def test_exactly_six_families_are_screened_and_one_is_selected(self) -> None:
        screening = load_audit()["baseline_screening"]
        self.assertEqual(6, len(screening))
        selected = [item for item in screening if item["selected"]]
        self.assertEqual(1, len(selected))
        self.assertEqual(
            "AOPB-1_CAPACITY_MATCHED_ADAPTIVE_ONLINE_PROTOTYPE_BANK",
            selected[0]["baseline_id"],
        )

    def test_selected_baseline_is_same_scope_engineering_baseline(self) -> None:
        selected = load_audit()["selected_dynamic_baseline"]
        self.assertEqual(1, selected["selected_baseline_count"])
        self.assertEqual(
            "ENGINEERING_BASELINE_NOT_RESEARCH_CANDIDATE",
            selected["classification"],
        )
        screened = {item["baseline_id"]: item for item in load_audit()["baseline_screening"]}
        self.assertTrue(screened[selected["baseline_id"]]["same_function_scope"])

    def test_ppb1_source_exposes_online_prototype_baseline_roles(self) -> None:
        source = (ROOT / "mcm_field_organism/_ppb1_reference.py").read_text(encoding="utf-8")
        for role in (
            "capacity",
            "match_threshold",
            "update_rate",
            "prototype_values",
            "normalized_mean_l1_distance",
            "last_selected_step",
            'PPB1_EVENTS = ("MATCHED", "CREATED", "REPLACED")',
        ):
            self.assertIn(role, source)

    def test_all_eight_fairness_roles_are_bound(self) -> None:
        self.assertEqual(
            8, len(load_audit()["selected_dynamic_baseline"]["required_equal_roles"])
        )

    def test_raw_history_semantics_and_field_are_forbidden(self) -> None:
        forbidden = set(load_audit()["selected_dynamic_baseline"]["forbidden_advantages"])
        self.assertEqual(
            {
                "RAW_HISTORY_ACCESS",
                "ADDITIONAL_INPUTS_OR_PROBES",
                "ADDITIONAL_CAPACITY",
                "SEMANTIC_LABELS",
                "FIELD_STATE_OR_FIELD_FEEDBACK",
            },
            forbidden,
        )

    def test_replay_attractor_and_reservoir_are_not_selected(self) -> None:
        screening = {item["baseline_id"]: item for item in load_audit()["baseline_screening"]}
        for baseline in ("REPLAY", "ATTRACTOR_PATTERN_COMPLETION", "RESERVOIR_TEMPORAL_STATE"):
            self.assertFalse(screening[baseline]["selected"])
            self.assertFalse(screening[baseline]["same_function_scope"])

    def test_reducibility_continuation_and_invalidity_are_explicit(self) -> None:
        selected = load_audit()["selected_dynamic_baseline"]
        self.assertIn("REPRODUCES", selected["reducibility_rule"])
        self.assertIn("BEHAVIORAL_DIFFERENCE", selected["continuation_rule"])
        self.assertIn("INVALIDATES", selected["invalidity_rule"])

    def test_public_surfaces_remain_without_s1yd_or_aopb1(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yd", source)
            self.assertNotIn("aopb", source)

    def test_decision_is_complete_narrow_and_nonexecuting(self) -> None:
        audit = load_audit()
        self.assertEqual(21, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual(
            "PASS_SELECT_AOPB1_AS_SINGLE_STRONGER_DYNAMIC_ENGINEERING_BASELINE",
            audit["decision"],
        )
        self.assertIn("NO_MEMORY_MECHANISM", audit["claim_boundary"])
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
