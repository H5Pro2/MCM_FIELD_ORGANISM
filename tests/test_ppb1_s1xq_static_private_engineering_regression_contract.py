from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1XQ_PPB1_STATISCHER_PRIVATER_ENGINEERING_REGRESSIONSVERTRAG_V1.json"
EXPECTED_CONTRACT_DIGEST = (
    "72eeed148a75a61253099c77f10e359243e287d6c8e8d9517fe4833e29187688"
)


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class PPB1S1XQStaticPrivateEngineeringRegressionContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        self.assertEqual(
            EXPECTED_CONTRACT_DIGEST,
            canonical_digest(load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())),
        )

    def test_parent_and_all_bound_files_are_exact(self) -> None:
        contract = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())
        parent = load_json(
            "docs/S1XP_PPB1_STATISCHER_MARGIN_FIXTURE_IMPLEMENTIERUNGSABSCHLUSSAUDIT_V1.json"
        )
        self.assertEqual(contract["parent_s1xp_audit_digest"], canonical_digest(parent))
        paths = {
            "s1xp_audit_file": "docs/S1XP_PPB1_STATISCHER_MARGIN_FIXTURE_IMPLEMENTIERUNGSABSCHLUSSAUDIT_V1.json",
            "s1xp_document": "docs/S1XP_PPB1_STATISCHER_MARGIN_FIXTURE_IMPLEMENTIERUNGSABSCHLUSSAUDIT.md",
            "s1xp_tests": "tests/test_ppb1_s1xp_static_margin_fixture_closure_audit.py",
            "s1xo_numeric_margin_fixture": "mcm_field_organism/_ppb1_s1xo_private_numeric_margin_fixture.py",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "s1wq_lifecycle": "mcm_field_organism/_ppb1_s1wq_perceptual_state_lifecycle.py",
            "receptor_contract": "mcm_field_organism/receptor_contract.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                contract["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_fixture_and_private_config_bindings_are_exact(self) -> None:
        contract = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())
        fixture = contract["fixture_binding"]
        self.assertEqual(
            "58a4e4d213914296900f30a3696cef38a3687526ef6986a1ac795467fdbcc0c8",
            fixture["bundle_digest"],
        )
        self.assertEqual(2, len(fixture["ordered_modality_ids"]))
        self.assertEqual(5, len(fixture["ordered_probe_classes"]))
        self.assertEqual([True, True, True, False, False], fixture["expected_recognition_mask"])
        self.assertFalse(fixture["threshold_operator_cases_included"])
        config = contract["private_config_binding"]
        self.assertEqual((12, 0.25), (config["auditory"]["carrier_count"], config["auditory"]["match_threshold"]))
        self.assertEqual((72, 0.125), (config["visual"]["carrier_count"], config["visual"]["match_threshold"]))
        self.assertTrue(config["config_must_be_new_and_not_reuse_s1xc_identity"])

    def test_formation_is_real_bounded_and_not_injected(self) -> None:
        formation = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "formation_binding"
        ]
        self.assertEqual([0.0, 0.0, 0.0], formation["ordered_frame_scalar_values"])
        self.assertEqual(3, formation["formation_steps_per_modality"])
        self.assertEqual(["CREATED", "MATCHED", "MATCHED"], formation["expected_event_sequence"])
        self.assertEqual(1, formation["expected_occupied_slot_count"])
        self.assertEqual(1, formation["expected_stabilized_slot_count"])
        self.assertEqual(3, formation["expected_support_count"])
        self.assertTrue(formation["candidate_state_must_be_formed_not_injected"])

    def test_candidate_probe_is_read_only_and_fixture_bound(self) -> None:
        probe = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "candidate_probe_binding"
        ]
        self.assertEqual("probe_s1wu_perceptual_state", probe["probe_function"])
        self.assertEqual(5, probe["probe_count_per_modality"])
        self.assertTrue(probe["each_probe_uses_value_equal_copy_of_same_stabilized_state"])
        self.assertTrue(probe["each_probe_window_is_later_than_formation"])
        self.assertFalse(probe["probe_order_may_change_state_or_result"])
        self.assertTrue(probe["state_digest_before_must_equal_after"])
        self.assertTrue(probe["state_identity_before_must_equal_after"])

    def test_static_baseline_has_one_prototype_and_no_privileged_information(self) -> None:
        baseline = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "static_prototype_baseline_binding"
        ]
        self.assertEqual("static-zero-prototype", baseline["baseline_id"])
        self.assertEqual(1, baseline["stored_prototype_count"])
        self.assertEqual("normalized_mean_l1_distance", baseline["distance_function"])
        self.assertFalse(baseline["raw_history_access_used"])
        self.assertFalse(baseline["candidate_state_identity_available_to_baseline"])

    def test_exact_call_budget_is_finite_and_retry_free(self) -> None:
        budget = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "exact_call_budget"
        ]
        self.assertEqual(1, budget["numeric_fixture_builder_call_count"])
        self.assertEqual(2, budget["initial_state_call_count"])
        self.assertEqual(6, budget["formation_advance_call_count"])
        self.assertEqual(10, budget["candidate_read_only_probe_call_count"])
        self.assertEqual(10, budget["static_baseline_distance_call_count"])
        self.assertEqual(20, budget["total_engineering_cell_count"])
        self.assertEqual(0, budget["registered_s1xa_cell_count"])
        self.assertEqual(0, budget["retry_count"])

    def test_execution_order_forms_before_probes_and_aggregates_last(self) -> None:
        order = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "required_execution_order"
        ]
        self.assertEqual(9, len(order))
        self.assertLess(order.index("E3_FORM_AND_VERIFY_BOTH_PPB1_STATES_WITH_THREE_ADVANCES_EACH"), order.index("E5_EVALUATE_TEN_READ_ONLY_CANDIDATE_PROBES"))
        self.assertLess(order.index("E6_EVALUATE_TEN_STATIC_ZERO_PROTOTYPE_DISTANCES"), order.index("E7_VERIFY_COMPLETE_CANDIDATE_BASELINE_EQUIVALENCE"))
        self.assertEqual("E8_RETURN_ONE_ATOMIC_PRIVATE_ENGINEERING_RECEIPT", order[-1])

    def test_expected_equivalence_is_engineering_pass_not_novelty(self) -> None:
        acceptance = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "engineering_acceptance"
        ]
        self.assertTrue(acceptance["equivalence_is_expected"])
        self.assertFalse(acceptance["equivalence_is_failure"])
        self.assertFalse(acceptance["equivalence_is_research_novelty"])
        self.assertEqual(
            "ENGINEERING_REGRESSION_VALID_EQUIVALENT_TO_STATIC_PROTOTYPE",
            acceptance["pass_decision"],
        )

    def test_fail_closed_rules_prohibit_partial_retry_and_historical_paths(self) -> None:
        contract = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())
        rules = contract["method_invalid_conditions"]
        self.assertEqual(9, len(rules))
        self.assertIn("ANY_CELL_IS_MISSING_DUPLICATE_REORDERED_OR_RETRIED", rules)
        self.assertIn("THRESHOLD_OPERATOR_CASE_ENTERS_BEHAVIORAL_REGRESSION", rules)
        atomic = contract["atomic_failure_rules"]
        self.assertTrue(all(not value for value in atomic.values()))

    def test_claim_and_implementation_boundaries_remain_closed(self) -> None:
        contract = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())
        claims = contract["claim_boundary"]
        self.assertFalse(claims["technical_memory_function_evaluated"])
        self.assertFalse(claims["mcm_specificity_evaluated"])
        self.assertFalse(claims["field_effect_evaluated"])
        self.assertTrue(claims["engineering_equivalence_may_be_reported"])
        self.assertTrue(
            all(not value for value in contract["implementation_boundary"].values())
        )

    def test_decision_is_narrow_and_all_execution_counters_are_zero(self) -> None:
        contract = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())
        self.assertEqual(
            "PASS_PRIVATE_PPB1_ENGINEERING_REGRESSION_CONTRACT_BOUND",
            contract["decision"],
        )
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
