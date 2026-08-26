from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1YP_LPRH1F_STATISCHER_FELDNUTZUNGS_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_V1.json"
EXPECTED_CONTRACT_DIGEST = "ad1870f4e60107666aac5426f17ae50cad99b5592076d29ea6872e72d355f15b"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1YPStaticFieldConsumptionContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(CONTRACT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual("fce519ef762a46e7751a8616aac5c3e71563eaf9e0f4698eba71e5f2a28511c4", contract["parent_s1yo_canonical_audit_digest"])
        paths = {
            "s1yo_audit": "docs/S1YO_LPRH1_STATISCHER_IMPLEMENTIERUNGS_UND_GRENZENABSCHLUSSAUDIT_V1.json",
            "s1yo_document": "docs/S1YO_LPRH1_STATISCHER_IMPLEMENTIERUNGS_UND_GRENZENABSCHLUSSAUDIT.md",
            "s1yo_tests": "tests/test_lprh1_s1yo_static_implementation_boundary_closure_audit.py",
            "private_handoff_module": "mcm_field_organism/_lprh1_s1yn_private_local_handoff.py",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "mcm_neuron": "mcm_field_organism/mcm_neuron.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "transient_neuron_input": "mcm_field_organism/transient_neuron_input.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(contract["bound_file_digests"][role], actual)

    def test_one_engineering_consumer_with_three_separate_inputs_is_bound(self) -> None:
        function = load(CONTRACT_PATH)["single_function"]
        self.assertEqual("LPRH1F_PRIVATE_CONTEXT_CONDITIONED_LOCAL_PROPOSAL", function["function_id"])
        self.assertEqual("CONTROLLED_ENGINEERING_FIELD_CONSUMER_NOT_NEW_FIELD_CAUSE", function["classification"])
        self.assertEqual(3, len(function["input_roles"]))
        self.assertFalse(function["persistent_state_added"])
        self.assertFalse(function["receptor_relabeling_allowed"])
        self.assertFalse(function["topology_change_allowed"])

    def test_directional_local_forecast_and_invariances_are_explicit(self) -> None:
        forecast = load(CONTRACT_PATH)["functional_forecast"]
        self.assertEqual("SIGNED_LOCAL_ACTIVATION_DIFFERENCE_FROM_LPRH1_OFF_OUTPUT", forecast["primary_measure"])
        self.assertIn("DIRECTION_OF_THE_BOUND_PROTOTYPE_VALUE", forecast["matched_context_forecast"])
        self.assertIn("OPPOSITE_ORDERED", forecast["paired_context_forecast"])
        self.assertIn("EQUALS_LPRH1_OFF", forecast["unmapped_forecast"])
        self.assertIn("EQUALS_LPRH1_OFF", forecast["no_context_forecast"])
        self.assertIn("FAILS_WITHOUT_OUTPUT", forecast["single_use_forecast"])

    def test_fair_history_comparison_is_non_circular(self) -> None:
        binding = load(CONTRACT_PATH)["fair_comparison_binding"]
        self.assertEqual(7, len(binding["held_equal"]))
        self.assertIn("PRIOR_PPB1_HISTORIES", binding["history_pair"])
        self.assertIn("HISTORY_THEN_READ_ONLY_PROBE", binding["causal_order"])
        self.assertEqual(5, len(binding["invalid_if"]))
        self.assertIn("CONTEXT_IS_DERIVED_FROM_THE_LATER_FIELD_OUTPUT", binding["invalid_if"])

    def test_all_seven_mandatory_baselines_are_distinct(self) -> None:
        baselines = load(CONTRACT_PATH)["mandatory_baselines"]
        identifiers = [item["baseline_id"] for item in baselines]
        self.assertEqual(7, len(identifiers))
        self.assertEqual(7, len(set(identifiers)))
        self.assertIn("GENERIC_EQUAL_VALUE_VECTOR", identifiers)
        generic = next(item for item in baselines if item["baseline_id"] == "GENERIC_EQUAL_VALUE_VECTOR")
        self.assertIn("IDENTICAL_PROTOTYPE_VALUES_MAPPING_AND_BUDGET", generic["role"])

    def test_reduction_is_separate_from_technical_pass(self) -> None:
        rules = load(CONTRACT_PATH)["decision_rules"]
        self.assertIn("DIRECTIONAL_LOCALITY_IMMUTABILITY", rules["technical_pass"])
        self.assertIn("REPRODUCES_ALL_NUMERIC_OUTPUTS", rules["generic_reduction"])
        self.assertIn("NOT_REPRODUCED_BY_ANY_MANDATORY_BASELINE", rules["candidate_specific_remainder"])
        self.assertIn("ENGINEERING_CONTEXT_CHANNEL_ONLY", rules["interpretation_if_reduced"])

    def test_measurements_and_stop_conditions_are_complete(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(9, len(contract["measurements"]))
        self.assertEqual(6, len(contract["stop_conditions"]))
        self.assertIn("RECEPTOR_PERCEPTION_DIGEST_BEFORE_AFTER", contract["measurements"])
        self.assertIn("BASELINE_EQUIVALENCE_CLASS", contract["measurements"])

    def test_public_surfaces_and_field_sources_remain_unchanged(self) -> None:
        for relative in ("mcm_field_organism/__init__.py", "mcm_field_organism/current_api.py", "mcm_field_organism/root_lazy_exports.py"):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yp", source)
            self.assertNotIn("lprh1f", source)

    def test_decision_is_static_narrow_and_nonexecuting(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(24, contract["passed_role_count"])
        self.assertEqual(0, contract["failed_role_count"])
        self.assertEqual("PASS_LPRH1F_STATIC_FIELD_CONSUMPTION_FUNCTION_AND_FALSIFICATION_CONTRACT_NO_IMPLEMENTATION", contract["decision"])
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
