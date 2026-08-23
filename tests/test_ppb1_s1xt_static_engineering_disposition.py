from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = (
    ROOT
    / "docs/S1XT_PPB1_STATISCHE_ENGINEERINGEINORDNUNG_UND_EINZELFUNKTIONSWAHL_V1.json"
)
EXPECTED_AUDIT_DIGEST = (
    "c1187d530cf1d599aca140d1f6b2473b411019452557ab07560eaef57b5103e3"
)


def load_audit():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


class PPB1S1XTStaticEngineeringDispositionTests(unittest.TestCase):
    def test_audit_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(
            load_audit(), allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(EXPECTED_AUDIT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        audit = load_audit()
        self.assertEqual(
            "9707b0c2075bbefa9240189887dec9b554e47c27a665ecf99ceee34ad1196cb3",
            audit["parent_s1xs_canonical_audit_digest"],
        )
        paths = {
            "s1xs_document": "docs/S1XS_PPB1_STATISCHER_ENGINEERINGREGRESSION_ABSCHLUSSAUDIT.md",
            "s1xs_audit": "docs/S1XS_PPB1_STATISCHER_ENGINEERINGREGRESSION_ABSCHLUSSAUDIT_V1.json",
            "s1xs_tests": "tests/test_ppb1_s1xs_static_engineering_regression_closure_audit.py",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wq_state_identity": "mcm_field_organism/_ppb1_s1wq_perceptual_state_lifecycle.py",
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

    def test_ppb1_is_retained_only_as_engineering_reference(self) -> None:
        role = load_audit()["retained_engineering_role"]
        self.assertEqual("PPB-1", role["component_id"])
        self.assertEqual(
            "RETAIN_PRIVATE_ENGINEERING_COMPONENT_AND_MANDATORY_COMPARISON_BASE",
            role["status"],
        )
        self.assertEqual("TECHNICAL_ENGINEERING_REFERENCE_ONLY", role["interpretation"])

    def test_no_memory_field_or_public_status_is_granted(self) -> None:
        role = load_audit()["retained_engineering_role"]
        self.assertFalse(role["mcm_specific_memory_mechanism"])
        self.assertFalse(role["field_effect_finding"])
        self.assertFalse(role["public_integration_authorized"])

    def test_exactly_one_function_is_selected(self) -> None:
        selected = load_audit()["single_selected_function"]
        self.assertEqual(1, selected["selected_function_count"])
        self.assertEqual(
            "PPB1_TEMPORAL_UPDATE_UNDER_BOUNDED_CAPACITY",
            selected["function_id"],
        )

    def test_selected_history_contains_similarity_and_conflict(self) -> None:
        question = load_audit()["single_selected_function"]["question"]
        self.assertIn("PARTLY_SIMILAR", question)
        self.assertIn("PARTLY_CONFLICTING", question)
        self.assertIn("BOUNDED_CAPACITY", question)

    def test_static_prototype_baseline_has_equal_budget_and_capacity(self) -> None:
        selected = load_audit()["single_selected_function"]
        self.assertEqual(
            "STATIC_PROTOTYPE_BANK_SAME_INPUT_BUDGET_AND_CAPACITY",
            selected["mandatory_baseline"],
        )
        roles = set(load_audit()["checked_roles"])
        self.assertIn("IDENTICAL_INPUT_BUDGET_REQUIRED", roles)
        self.assertIn("IDENTICAL_CAPACITY_REQUIRED", roles)

    def test_all_five_required_observables_are_bound(self) -> None:
        self.assertEqual(
            [
                "UPDATE_AFTER_CONFIRMING_REPETITION",
                "SEPARATION_OF_OLD_AND_NEW_STATES",
                "CONFLICT_RESPONSE",
                "CONTROLLED_FORGETTING_OR_DISPLACEMENT",
                "LATER_READ_ONLY_RETRIEVAL_OF_UPDATED_STATE",
            ],
            load_audit()["single_selected_function"]["required_observables"],
        )

    def test_continuation_and_stop_rules_are_explicit(self) -> None:
        selected = load_audit()["single_selected_function"]
        self.assertEqual(
            "CLEAR_PREBOUND_DYNAMIC_FUNCTION_ADVANTAGE_OVER_STATIC_PROTOTYPE_BANK",
            selected["continuation_condition"],
        )
        self.assertEqual(
            "NO_CLEAR_ADVANTAGE_OR_UNFAIR_CAPACITY_INPUT_OR_PROBE_BUDGET",
            selected["stop_condition"],
        )

    def test_parallel_function_branches_remain_closed(self) -> None:
        self.assertEqual(
            {
                "FIELD_BACKREACTION",
                "SEMANTIC_ASSOCIATION",
                "CROSS_MODAL_BINDING",
                "ATTRACTOR_COMPLETION",
                "RESERVOIR_TEMPORAL_STATE",
                "PRODUCTION_PERSISTENCE",
            },
            set(load_audit()["excluded_parallel_functions"]),
        )

    def test_decision_is_complete_and_static(self) -> None:
        audit = load_audit()
        self.assertEqual(22, audit["passed_role_count"])
        self.assertEqual(0, audit["failed_role_count"])
        self.assertEqual(
            "PASS_RETAIN_PPB1_ENGINEERING_BASE_SELECT_ONE_BOUNDED_TEMPORAL_UPDATE_FUNCTION",
            audit["decision"],
        )
        self.assertTrue(all(value == 0 for value in audit["execution_counters"].values()))

    def test_active_public_surfaces_remain_without_s1xt(self) -> None:
        for relative in (
            "mcm_field_organism/__init__.py",
            "mcm_field_organism/current_api.py",
            "mcm_field_organism/root_lazy_exports.py",
        ):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1xt", source)
            self.assertNotIn("temporal_update_under_bounded_capacity", source)


if __name__ == "__main__":
    unittest.main()
