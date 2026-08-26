from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    ROOT
    / "docs/S1YE_PPB1_STATISCHER_NICHTDUPLIZIERUNGS_INFORMATIONS_UND_AEQUIVALENZAUDIT_V1.json"
)
REFERENCE_PATH = ROOT / "mcm_field_organism/_ppb1_reference.py"
PROBE_PATH = ROOT / "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py"
EXPECTED_AUDIT_DIGEST = "24018d0a83d65edbae36c0f1fe4a7fd0b955a9ab6fe95171b565aaa8d64c2908"


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def function_source(path: Path, name: str) -> str:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(
        item
        for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name == name
    )
    segment = ast.get_source_segment(source, node)
    assert segment is not None
    return segment


class PPB1S1YEStaticNonduplicationEquivalenceAuditTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "f80050b014c1fde4f176af67df040569c98072d7198121eb947771dd526efff0",
            audit["parent_s1yd_canonical_audit_digest"],
        )
        paths = {
            "s1yd_audit": "docs/S1YD_PPB1_STATISCHE_ENGINEERINGEINORDNUNG_UND_DYNAMISCHE_BASELINEAUSWAHL_V1.json",
            "s1yd_document": "docs/S1YD_PPB1_STATISCHE_ENGINEERINGEINORDNUNG_UND_DYNAMISCHE_BASELINEAUSWAHL.md",
            "s1yd_tests": "tests/test_ppb1_s1yd_static_dynamic_baseline_selection.py",
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

    def test_nine_observable_mechanism_roles_are_complete(self) -> None:
        self.assertEqual(9, len(load_audit()["ppb1_observable_mechanism_inventory"]))

    def test_reference_source_contains_assignment_update_and_capacity(self) -> None:
        source = function_source(REFERENCE_PATH, "advance_ppb1_bank")
        reference_source = REFERENCE_PATH.read_text(encoding="utf-8")
        self.assertIn("range(config.capacity)", reference_source)
        for role in (
            "normalized_mean_l1_distance",
            "config.match_threshold",
            "config.update_rate",
            'event = "MATCHED"',
            'event = "CREATED"',
            'event = "REPLACED"',
            "last_selected_step",
            "config.expire_after_steps",
        ):
            self.assertIn(role, source)

    def test_replacement_is_deterministic_lru_with_slot_tiebreak(self) -> None:
        source = function_source(REFERENCE_PATH, "advance_ppb1_bank")
        self.assertIn("slots[index].last_selected_step", source)
        self.assertIn("slots[index].slot_id", source)
        self.assertIn("min(", source)

    def test_probe_is_stability_filtered_nearest_and_read_only(self) -> None:
        source = function_source(PROBE_PATH, "probe_s1wu_perceptual_state")
        for role in (
            "slot.support_count >= config.stable_after",
            "normalized_mean_l1_distance",
            "min(candidates)",
            "distance <= config.match_threshold",
            "validated_state.digest() != before_digest",
        ):
            self.assertIn(role, source)
        self.assertNotIn("advance_ppb1_bank", source)

    def test_information_inventory_excludes_hidden_advantages(self) -> None:
        inventory = load_audit()["information_inventory"]
        self.assertFalse(inventory["raw_history_retained"])
        self.assertFalse(inventory["semantic_labels_retained"])
        self.assertFalse(inventory["field_state_consumed"])
        self.assertFalse(inventory["field_feedback_produced"])

    def test_all_four_observable_surfaces_are_equivalent(self) -> None:
        result = load_audit()["equivalence_result"]
        for role in (
            "same_information_surface",
            "same_state_family",
            "same_transition_family",
            "same_probe_family",
        ):
            self.assertTrue(result[role])
        self.assertFalse(result["independent_nonduplicated_counterprediction_materializable"])

    def test_audit_wrappers_are_not_interpreted_as_recognition_function(self) -> None:
        self.assertIn(
            "AUDITABILITY_NOT_THE_BOUND_RECOGNITION_FUNCTION",
            load_audit()["equivalence_result"]["wrapper_effect"],
        )

    def test_fairness_dilemma_stops_duplicate_implementation(self) -> None:
        dilemma = load_audit()["fairness_dilemma"]
        self.assertEqual("BEHAVIORAL_EQUIVALENCE_BY_CONSTRUCTION", dilemma["same_rules_result"])
        self.assertIn("CHANGED", dilemma["different_rules_result"])
        self.assertEqual(
            "DO_NOT_IMPLEMENT_OR_RUN_AOPB1_FOR_THE_CURRENT_H1_TO_H5_SCOPE",
            dilemma["decision"],
        )

    def test_branch_closes_baseline_but_retains_engineering_component(self) -> None:
        disposition = load_audit()["branch_disposition"]
        self.assertEqual(
            "TERMINALLY_CLOSED_AS_DUPLICATED_MECHANISM_FAMILY",
            disposition["aopb1_comparison_branch"],
        )
        self.assertEqual(
            "RETAIN_AS_MCM_COMPATIBLE_PERCEPTUAL_ENGINEERING_COMPONENT",
            disposition["ppb1_component"],
        )
        self.assertFalse(disposition["mcm_specific_memory_mechanism"])
        self.assertFalse(disposition["field_effect_finding"])
        self.assertFalse(disposition["competitive_advantage_finding"])

    def test_public_surfaces_remain_unchanged(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1ye", source)
            self.assertNotIn("aopb", source)

    def test_decision_is_complete_narrow_and_nonexecuting(self) -> None:
        audit = load_audit()
        self.assertEqual(25, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual(
            "STOP_AOPB1_DUPLICATION_RETAIN_PPB1_AS_ADAPTIVE_ONLINE_PROTOTYPE_ENGINEERING_COMPONENT",
            audit["decision"],
        )
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
