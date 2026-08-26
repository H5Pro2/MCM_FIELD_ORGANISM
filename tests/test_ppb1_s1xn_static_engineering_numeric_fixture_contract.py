from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1XN_PPB1_STATISCHER_ENGINEERING_UND_NUMERISCHER_FIXTURE_KORREKTURVERTRAG_V1.json"
EXPECTED_CONTRACT_DIGEST = (
    "cff21269c4981ffe7439de49e3eee35bd71528ed464f6f75937d1e9a192628b6"
)


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class PPB1S1XNStaticEngineeringNumericFixtureContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        self.assertEqual(
            EXPECTED_CONTRACT_DIGEST,
            canonical_digest(load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())),
        )

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())
        parent = load_json(
            "docs/S1XM_PPB1_STATISCHER_ERGEBNIS_RECEIPT_UND_NUMERISCHER_GRENZWERTAUDIT_V1.json"
        )
        self.assertEqual(contract["parent_s1xm_audit_digest"], canonical_digest(parent))
        paths = {
            "s1xm_audit_file": "docs/S1XM_PPB1_STATISCHER_ERGEBNIS_RECEIPT_UND_NUMERISCHER_GRENZWERTAUDIT_V1.json",
            "s1xm_document": "docs/S1XM_PPB1_STATISCHER_ERGEBNIS_RECEIPT_UND_NUMERISCHER_GRENZWERTAUDIT.md",
            "s1xm_tests": "tests/test_ppb1_s1xm_static_result_numeric_boundary_audit.py",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wq_lifecycle": "mcm_field_organism/_ppb1_s1wq_perceptual_state_lifecycle.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "s1xc_historical_fixture_registry": "mcm_field_organism/_ppb1_s1xc_fixture_registry.py",
            "s1xi_historical_full_runner": "mcm_field_organism/_ppb1_s1xi_private_full_runner.py",
        }
        for role, relative in paths.items():
            self.assertEqual(
                contract["bound_file_digests"][role],
                hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
            )

    def test_historical_research_artifacts_are_immutable_and_closed(self) -> None:
        binding = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "historical_immutability"
        ]
        self.assertFalse(binding["s1xc_registry_may_be_edited_by_this_contract"])
        self.assertFalse(binding["s1xi_runner_may_be_edited_by_this_contract"])
        self.assertFalse(binding["s1xl_result_may_be_recomputed_repaired_or_reinterpreted"])
        self.assertTrue(binding["new_fixture_must_use_new_schema_and_identity"])
        self.assertTrue(binding["registered_research_comparison_remains_closed"])

    def test_exact_retained_engineering_inventory_has_no_research_claim(self) -> None:
        contract = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())
        self.assertEqual(8, len(contract["retained_private_engineering_roles"]))
        self.assertEqual(4, len(contract["historical_only_roles"]))
        self.assertEqual(5, len(contract["not_retained_as_engineering_claims"]))
        self.assertIn(
            "MCM_SPECIFIC_MEMORY_MECHANISM",
            contract["not_retained_as_engineering_claims"],
        )

    def test_behavioral_classes_and_recognition_mask_are_exact(self) -> None:
        contract = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())
        self.assertEqual(
            [
                "exact-positive",
                "near-positive",
                "margin-positive",
                "margin-negative",
                "distinct-negative",
            ],
            contract["behavioral_probe_classes"],
        )
        self.assertEqual(
            [True, True, True, False, False],
            contract["expected_recognition_mask"],
        )

    def test_modality_values_are_binary_exact_and_margin_separated(self) -> None:
        bindings = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "modality_numeric_bindings"
        ]
        expected = {
            "auditory": (0.25, [0.0, 0.125, 0.1875, 0.3125, 0.625], 0.0625),
            "visual": (0.125, [0.0, 0.0625, 0.09375, 0.15625, 0.5], 0.03125),
        }
        for modality, (threshold, probes, margin) in expected.items():
            binding = bindings[modality]
            self.assertEqual(threshold, binding["match_threshold"])
            self.assertEqual(probes, binding["probe_values"])
            self.assertEqual(margin, binding["minimum_threshold_separation"])
            self.assertNotIn(threshold, probes)
            self.assertTrue(binding["all_nonzero_literals_binary_exact"])
            self.assertTrue(all(float.fromhex(value.hex()) == value for value in probes))
            self.assertGreaterEqual(threshold - probes[2], margin)
            self.assertGreaterEqual(probes[3] - threshold, margin)

    def test_fixture_fails_closed_before_use_and_has_no_post_hoc_tolerance(self) -> None:
        rules = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "behavioral_fixture_rules"
        ]
        self.assertTrue(rules["no_behavioral_probe_value_equals_threshold"])
        self.assertTrue(
            rules["expected_distance_is_precomputed_with_production_metric_during_materialization"]
        )
        self.assertTrue(rules["computed_class_side_must_match_bound_expectation"])
        self.assertTrue(rules["any_distance_or_class_side_mismatch_fails_before_test_use"])
        self.assertFalse(rules["post_observation_tolerance_selection_allowed"])

    def test_threshold_operator_unit_fixture_is_separate_and_non_decisional(self) -> None:
        fixture = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "separate_threshold_operator_unit_fixture"
        ]
        self.assertFalse(fixture["included_in_behavioral_matrix"])
        self.assertTrue(fixture["uses_math_nextafter_neighbors"])
        self.assertEqual(3, len(fixture["roles"]))
        self.assertFalse(fixture["may_create_candidate_or_baseline_function_decision"])

    def test_future_acceptance_is_engineering_equivalence_only(self) -> None:
        acceptance = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())[
            "future_engineering_acceptance"
        ]
        self.assertFalse(acceptance["novelty_or_mcm_specificity_evaluated"])
        self.assertEqual("STATIC_PROTOTYPE", acceptance["required_reference_baseline"])
        self.assertFalse(acceptance["equivalence_is_failure"])
        self.assertFalse(acceptance["equivalence_is_research_novelty"])
        self.assertFalse(acceptance["field_feedback_allowed"])

    def test_no_implementation_or_execution_is_authorized(self) -> None:
        contract = load_json(CONTRACT_PATH.relative_to(ROOT).as_posix())
        self.assertTrue(
            all(not value for value in contract["implementation_boundary"].values())
        )
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))
        self.assertEqual(
            "PASS_ENGINEERING_DISPOSITION_AND_NUMERIC_MARGIN_FIXTURE_CONTRACT_BOUND",
            contract["decision"],
        )


if __name__ == "__main__":
    unittest.main()
