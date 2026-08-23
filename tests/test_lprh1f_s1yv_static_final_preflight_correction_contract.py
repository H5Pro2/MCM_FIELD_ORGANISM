from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1YV_LPRH1F_STATISCHER_FINALER_PREFLIGHT_KORREKTURVERTRAG_V1.json"
S1YU_PATH = ROOT / "docs/S1YU_LPRH1F_STATISCHER_FINALER_IMPLEMENTIERUNGSPREFLIGHT_V1.json"
EXPECTED_CONTRACT_DIGEST = "a120711d5c237a5b3a2912c876284f4ab70b48b500405d6b00542afa29430e0c"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class LPRH1FS1YVStaticFinalPreflightCorrectionContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load(CONTRACT_PATH), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual("912d13fa7892fd395be73e68a71cdf02eb04b9754c2d84d8207ebcf19e615f51", contract["parent_s1yu_canonical_preflight_digest"])
        paths = {
            "s1yu_preflight": "docs/S1YU_LPRH1F_STATISCHER_FINALER_IMPLEMENTIERUNGSPREFLIGHT_V1.json",
            "s1yu_document": "docs/S1YU_LPRH1F_STATISCHER_FINALER_IMPLEMENTIERUNGSPREFLIGHT.md",
            "s1yu_tests": "tests/test_lprh1f_s1yu_static_final_implementation_preflight.py",
            "s1yt_contract": "docs/S1YT_LPRH1F_STATISCHER_PREFLIGHT_BINDUNGSKORREKTURVERTRAG_V1.json",
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

    def test_field_prestate_and_drive_order_are_canonical(self) -> None:
        binding = load(CONTRACT_PATH)["authoritative_field_prestate_and_drive_order"]
        self.assertEqual("ASCENDING_PREVIOUS_NEURON_ID_UTF8_CODEPOINT_ORDER", binding["drive_order"])
        self.assertEqual(5, len(binding["field_prestate_canonical_payload"]))
        self.assertTrue(binding["caller_supplied_field_prestate_digest_must_equal_derived_digest"])
        self.assertEqual(binding["prepared_drive_order"], binding["proposal_output_order"])

    def test_single_registered_transition_is_source_bound_and_atomic(self) -> None:
        contract = load(CONTRACT_PATH)
        registry = contract["base_transition_registry"]
        self.assertEqual(1, len(registry))
        self.assertEqual("hold_state_baseline", registry[0]["callable_name"])
        self.assertEqual(contract["bound_file_digests"]["mcm_neuron_layer"], registry[0]["source_digest"])
        atomicity = contract["preparation_failure_atomicity"]
        self.assertFalse(atomicity["observable_partial_set_on_failure"])
        self.assertFalse(atomicity["preparation_receipt_on_failure"])
        self.assertEqual(0, atomicity["retry_count"])

    def test_six_type_invariant_families_and_twelve_cross_links_are_bound(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(6, len(contract["private_type_invariants"]))
        self.assertTrue(all(value for value in contract["private_type_invariants"].values()))
        self.assertEqual(12, len(contract["cross_object_links"]))
        self.assertEqual(12, len(set(contract["cross_object_links"])))

    def test_eight_arm_source_matrix_is_exhaustive_and_balanced(self) -> None:
        matrix = load(CONTRACT_PATH)["source_kind_arm_output_matrix"]
        self.assertEqual(8, len(matrix))
        self.assertEqual(8, len({item["arm_id"] for item in matrix}))
        kinds = [item["source_kind"] for item in matrix]
        for kind in ("CANDIDATE", "GENERIC", "NO_CONTEXT", "DIGEST_ONLY"):
            self.assertEqual(2, kinds.count(kind))
        self.assertEqual(4, sum(item["local_value_count"] for item in matrix))
        self.assertEqual(4, sum(item["steering_value"] is not None for item in matrix))

    def test_candidate_and_generic_values_are_exactly_paired(self) -> None:
        matrix = {item["arm_id"]: item for item in load(CONTRACT_PATH)["source_kind_arm_output_matrix"]}
        self.assertEqual(matrix["candidate.low"]["steering_value"], matrix["generic.low"]["steering_value"])
        self.assertEqual(matrix["candidate.high"]["steering_value"], matrix["generic.high"]["steering_value"])
        self.assertEqual(matrix["candidate.low"]["output_behavior"], matrix["generic.low"]["output_behavior"])
        self.assertEqual(matrix["candidate.high"]["output_behavior"], matrix["generic.high"]["output_behavior"])

    def test_error_conditions_have_exact_order_and_function_owners(self) -> None:
        contract = load(CONTRACT_PATH)
        matrix = contract["error_condition_matrix"]
        expected_order = [
            "LPRH1F_INVALID_INPUT",
            "LPRH1F_PROVENANCE_MISMATCH",
            "LPRH1F_CAUSAL_TIME_MISMATCH",
            "LPRH1F_LOCAL_MAPPING_MISMATCH",
            "LPRH1F_DUPLICATE_FIELD_USE",
            "LPRH1F_BASE_OUTPUT_MISMATCH",
            "LPRH1F_ATOMIC_RESULT_REQUIRED",
            "LPRH1F_FIELD_EXECUTION_BLOCKED",
        ]
        self.assertEqual(expected_order, [item["code"] for item in matrix])
        self.assertTrue(all(item["function_owners"] and item["conditions"] for item in matrix))

    def test_all_failures_have_zero_output_and_unchanged_ledger(self) -> None:
        rule = load(CONTRACT_PATH)["all_failure_output_rule"]
        for role in (
            "prepared_drive_set_returned_on_preparation_failure",
            "proposal_set_returned_on_consumer_failure",
            "proposal_result_returned_on_consumer_failure",
            "field_use_ledger_changed_on_failure",
            "source_object_mutation_allowed",
        ):
            self.assertFalse(rule[role])
        self.assertEqual(0, rule["observable_partial_output_count"])
        self.assertEqual(0, rule["retry_count"])
        self.assertEqual(0, rule["field_step_count"])

    def test_all_five_s1yu_blockers_are_closed_exactly(self) -> None:
        expected = {item["blocker_id"] for item in load(S1YU_PATH)["final_preflight_blockers"]}
        closure = load(CONTRACT_PATH)["final_preflight_blocker_closure"]
        self.assertEqual(expected, set(closure))
        self.assertEqual(5, len(closure))
        self.assertTrue(all(value.startswith("CLOSED_BY_") for value in closure.values()))

    def test_future_scope_is_private_and_field_execution_remains_blocked(self) -> None:
        scope = load(CONTRACT_PATH)["implementation_scope_after_separate_audit"]
        self.assertEqual("mcm_field_organism._lprh1f_s1yx_private_context_consumer", scope["private_module_name"])
        self.assertEqual(2, len(scope["permitted_functions"]))
        self.assertEqual(6, scope["permitted_type_count"])
        self.assertEqual(8, len(scope["permitted_synthetic_test_families"]))
        self.assertFalse(scope["public_export_allowed"])
        self.assertFalse(scope["field_execution_allowed"])

    def test_decision_is_static_narrow_and_nonexecuting(self) -> None:
        contract = load(CONTRACT_PATH)
        self.assertEqual(38, contract["passed_role_count"])
        self.assertEqual(0, contract["failed_role_count"])
        self.assertEqual("PASS_LPRH1F_FIVE_FINAL_PREFLIGHT_BINDINGS_CLOSED_NO_IMPLEMENTATION_OR_EXECUTION", contract["decision"])
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))
        self.assertFalse(contract["implementation_gate"]["implementation_authorized_in_s1yv"])


if __name__ == "__main__":
    unittest.main()
