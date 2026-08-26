from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1YT_LPRH1F_STATISCHER_PREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json"
S1YS_PATH = ROOT / "docs/S1YS_LPRH1F_STATISCHER_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
EXPECTED_CONTRACT_DIGEST = "65c43093957a3e41714d383971ff514c0809723c41d8d3bb66cb0246e7bfff53"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1YTStaticPreflightBindingCorrectionContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(CONTRACT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual("b4d8836bb82a4f34722b2a7d09b896e778c3581c407d16f10f961de41b1066d6", contract["parent_s1ys_canonical_preflight_digest"])
        paths = {
            "s1ys_preflight": "docs/S1YS_LPRH1F_STATISCHER_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT_V1.json",
            "s1ys_document": "docs/S1YS_LPRH1F_STATISCHER_ABSCHLUSS_UND_IMPLEMENTIERUNGSPREFLIGHT.md",
            "s1ys_tests": "tests/test_lprh1f_s1ys_static_closure_implementation_preflight.py",
            "s1yr_contract": "docs/S1YR_LPRH1F_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json",
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

    def test_midpoint_has_one_unambiguous_operation_order(self) -> None:
        rule = load(CONTRACT_PATH)["canonical_midpoint_operation"]
        self.assertEqual(4, len(rule["operation_order"]))
        self.assertIn("OPEN_BASE_ACTIVATION_PLUS_STEERING_VALUE_CLOSE", rule["single_formula"])
        self.assertEqual(0.5, rule["coefficient"])
        self.assertEqual(0, rule["clamp_call_count"])
        self.assertFalse(rule["alternate_formula_allowed"])

    def test_two_private_function_signatures_separate_preparation_and_consumer(self) -> None:
        functions = load(CONTRACT_PATH)["future_private_functions"]
        self.assertEqual(["prepare_lprh1f_base_drive_set", "materialize_lprh1f_proposal"], [item["function_id"] for item in functions])
        self.assertEqual(6, len(functions[0]["input_roles_in_order"]))
        self.assertEqual(3, len(functions[1]["input_roles_in_order"]))
        self.assertEqual(0, functions[1]["base_transition_call_count"])
        self.assertTrue(all(item["field_call_count"] == 0 for item in functions))

    def test_six_corrected_types_carry_actual_objects_and_values(self) -> None:
        schemas = load(CONTRACT_PATH)["corrected_exact_private_type_schemas"]
        self.assertEqual(6, len(schemas))
        self.assertIn("drive_MCMNeuronDrive", schemas["LPRH1FPreparedDrive"])
        self.assertIn("base_output_MCMNeuronOutput", schemas["LPRH1FPreparedDrive"])
        steering = schemas["LPRH1FSteeringInput"]
        self.assertIn("handoff_result_LPRH1HandoffResult_or_none", steering)
        self.assertIn("ordered_local_values_tuple_neuron_dock_carrier_value", steering)

    def test_all_six_private_and_supporting_payloads_are_complete(self) -> None:
        contract = load(CONTRACT_PATH)
        schemas = contract["corrected_exact_private_type_schemas"]
        payloads = contract["canonical_payloads_for_private_types"]
        self.assertEqual(set(schemas), set(payloads))
        self.assertEqual(6, len(payloads))
        supporting = contract["supporting_canonical_payloads"]
        self.assertEqual(10, len(supporting))
        self.assertIn("TransientNeuronDockInput", supporting)
        self.assertIn("LPRH1HandoffResult", supporting)
        self.assertTrue(all(value for value in payloads.values()))

    def test_candidate_and_generic_mapping_and_budget_are_exactly_equal(self) -> None:
        invariants = load(CONTRACT_PATH)["steering_source_invariants"]
        self.assertIn("NEURON_DOCK_CARRIER_VALUE_TUPLES_EQUAL_EXACTLY", invariants["candidate_and_generic_mapping_budget_rule"])
        self.assertIn("SAME_OBJECT_IDENTITY_AND_DIGEST", invariants["candidate_and_generic_prepared_drive_set_rule"])
        self.assertIn("ONE_MIDPOINT_APPLICATION_PER_ORDERED_LOCAL_VALUE", invariants["candidate_and_generic_consumer_budget_rule"])

    def test_counter_owners_are_disjoint(self) -> None:
        counters = load(CONTRACT_PATH)["counter_ownership"]
        self.assertEqual("LPRH1FPreparedDriveSet", counters["preparation_owner"])
        self.assertEqual("LPRH1FProposalResult", counters["consumer_owner"])
        self.assertEqual(0, counters["consumer_base_transition_call_count"])
        self.assertTrue(counters["no_counter_is_counted_by_BOTH_PREPARATION_AND_CONSUMER"])

    def test_error_set_precedence_and_atomic_order_are_finite(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(8, len(contract["finite_error_codes"]))
        self.assertEqual(contract["finite_error_codes"], contract["error_dispatch_in_precedence_order"])
        self.assertEqual(11, len(contract["atomic_consumer_order"]))
        self.assertIn("ONLY_OBSERVABLE_COMMIT", contract["atomic_consumer_order"][-1])

    def test_all_six_s1ys_blockers_are_closed_exactly(self) -> None:
        expected = {item["blocker_id"] for item in load(S1YS_PATH)["preflight_blockers"]}
        closure = load(CONTRACT_PATH)["preflight_blocker_closure"]
        self.assertEqual(expected, set(closure))
        self.assertEqual(6, len(closure))
        self.assertTrue(all(value.startswith("CLOSED_BY_") for value in closure.values()))

    def test_decision_is_static_narrow_and_nonexecuting(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(34, contract["passed_role_count"])
        self.assertEqual(0, contract["failed_role_count"])
        self.assertEqual("PASS_LPRH1F_SIX_PREFLIGHT_BINDINGS_CLOSED_NO_IMPLEMENTATION_OR_EXECUTION", contract["decision"])
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))
        self.assertFalse(contract["implementation_gate"]["implementation_authorized_in_s1yt"])


if __name__ == "__main__":
    unittest.main()
