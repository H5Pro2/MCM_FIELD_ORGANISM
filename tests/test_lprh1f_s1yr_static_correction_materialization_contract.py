from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1YR_LPRH1F_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json"
S1YQ_PATH = ROOT / "docs/S1YQ_LPRH1F_STATISCHER_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json"
EXPECTED_CONTRACT_DIGEST = "99364553ca58ae63756e8e69076d38974afa72b85246831c7f5f7c9ead33b0e9"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1YRStaticCorrectionMaterializationContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(CONTRACT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual("c8f7d3109fcc54f6f3bc875f113a8a37f0d7c63814c1a599dc2350669451c0a2", contract["parent_s1yq_canonical_audit_digest"])
        paths = {
            "s1yq_audit": "docs/S1YQ_LPRH1F_STATISCHER_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json",
            "s1yq_document": "docs/S1YQ_LPRH1F_STATISCHER_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT.md",
            "s1yq_tests": "tests/test_lprh1f_s1yq_static_materializability_audit.py",
            "s1yp_contract": "docs/S1YP_LPRH1F_STATISCHER_FELDNUTZUNGS_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_V1.json",
            "private_handoff_module": "mcm_field_organism/_lprh1_s1yn_private_local_handoff.py",
            "mcm_neuron_layer": "mcm_field_organism/mcm_neuron_layer.py",
            "mcm_neuron": "mcm_field_organism/mcm_neuron.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(contract["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_midpoint_rule_is_exact_bounded_and_has_tie_rule(self) -> None:
        rule = load(CONTRACT_PATH)["exact_steering_rule"]
        self.assertEqual(1, rule["coefficient_numerator"])
        self.assertEqual(2, rule["coefficient_denominator"])
        self.assertIn("ONE_HALF_TIMES_THE_SUM_OF_BASE_ACTIVATION_AND_STEERING_VALUE", rule["equivalent_rule"])
        self.assertIn("WITHOUT_CLAMP", rule["output_domain"])
        self.assertIn("FIXTURE_IS_INVALID", rule["zero_margin_rule"])

    def test_one_base_output_set_is_shared_by_all_arms(self) -> None:
        binding = load(CONTRACT_PATH)["base_output_binding"]
        self.assertEqual(1, binding["base_transition_call_count_per_neuron"])
        self.assertEqual(1, binding["base_output_set_construction_count"])
        self.assertTrue(binding["base_output_set_is_immutable"])
        self.assertTrue(binding["all_arms_receive_same_base_output_set_digest"])
        self.assertFalse(binding["consumer_may_call_base_transition"])

    def test_six_private_types_and_distinct_field_use_ledger_are_bound(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(6, len(contract["exact_private_type_schemas"]))
        identity = contract["canonical_identity_and_digest_rules"]
        self.assertTrue(identity["field_use_namespace_is_distinct_from_s1yn_handoff_namespace"])
        self.assertIn("SORTED_UNION", identity["successful_ledger_rule"])
        self.assertIn("REMAIN_UNCHANGED", identity["failure_ledger_rule"])

    def test_private_dispatch_preserves_public_drive_and_field(self) -> None:
        boundary = load(CONTRACT_PATH)["private_dispatch_boundary"]
        self.assertFalse(boundary["existing_mcm_neuron_drive_changed"])
        self.assertFalse(boundary["shared_mcm_field_changed"])
        self.assertEqual(8, len(boundary["input_order"]))
        self.assertFalse(boundary["context_survives_return"])
        self.assertEqual(0, boundary["shared_field_advance_call_count"])

    def test_generic_baseline_is_equal_by_construction(self) -> None:
        baseline = load(CONTRACT_PATH)["generic_equal_value_baseline"]
        self.assertTrue(baseline["ordered_neuron_carrier_values_equal_candidate"])
        self.assertTrue(baseline["base_output_set_digest_equal_candidate"])
        self.assertTrue(baseline["steering_rule_equal_candidate"])
        self.assertTrue(baseline["mapped_consumer_call_count_equal_candidate"])
        self.assertIn("GENERIC_REDUCTION_BY_CONSTRUCTION", baseline["expected_interpretation"])

    def test_finite_fixture_has_exact_opposite_quarter_margins(self) -> None:
        fixture = load(CONTRACT_PATH)["finite_fixture_pair"]
        self.assertEqual([-0.5, -0.5], fixture["history_low_values"])
        self.assertEqual([0.5, 0.5], fixture["history_high_values"])
        self.assertEqual(0.0, fixture["base_activation"])
        self.assertEqual(-0.25, fixture["expected_low_activation"])
        self.assertEqual(0.25, fixture["expected_high_activation"])
        self.assertEqual(0.25, fixture["minimum_absolute_directional_margin"])

    def test_comparator_separates_immediate_proposal_from_field_propagation(self) -> None:
        comparator = load(CONTRACT_PATH)["measurement_and_comparator"]
        self.assertIn("BEFORE_ANY_ADVANCE", comparator["measurement_horizon"])
        self.assertFalse(comparator["later_field_propagation_in_scope"])
        self.assertEqual(1e-12, comparator["numeric_absolute_tolerance"])
        self.assertEqual(6, len(comparator["decision_precedence"]))
        self.assertEqual("TECHNICAL_PASS_GENERIC_REDUCTION", comparator["decision_precedence"][-2])

    def test_all_eight_blockers_are_closed_exactly(self) -> None:
        expected = {item["blocker_id"] for item in load(S1YQ_PATH)["materialization_blockers"]}
        closure = load(CONTRACT_PATH)["blocker_closure"]
        self.assertEqual(expected, set(closure))
        self.assertEqual(8, len(closure))
        self.assertTrue(all(value.startswith("CLOSED_BY_") for value in closure.values()))

    def test_decision_is_static_reduced_and_nonexecuting(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(32, contract["passed_role_count"])
        self.assertEqual(0, contract["failed_role_count"])
        self.assertEqual("PASS_LPRH1F_EIGHT_MATERIALIZATION_BLOCKERS_CLOSED_GENERIC_REDUCTION_EXPECTED_NO_IMPLEMENTATION", contract["decision"])
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))
        self.assertFalse(contract["implementation_gate"]["implementation_authorized_in_s1yr"])


if __name__ == "__main__":
    unittest.main()
