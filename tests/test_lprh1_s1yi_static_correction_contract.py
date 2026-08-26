from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/S1YI_LPRH1_STATISCHER_KORREKTUR_UND_MATERIALISIERUNGSVERTRAG_V1.json"
EXPECTED_CONTRACT_DIGEST = "8de3ed1392f1038bc6dcfd63287bf6f8e452aa1771fab1836d4230e6da0c7bd9"


def load_contract():
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


class LPRH1S1YIStaticCorrectionContractTests(unittest.TestCase):
    def test_contract_is_canonical_and_digest_bound(self) -> None:
        encoded = json.dumps(load_contract(), allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertEqual(EXPECTED_CONTRACT_DIGEST, hashlib.sha256(encoded).hexdigest())

    def test_parent_and_bound_files_are_exact(self) -> None:
        contract = load_contract()
        self.assertEqual("5ccde1140bfdf29594bd8596101c3cab11a3349a2a430af3169980b29f944081", contract["parent_s1yh_canonical_audit_digest"])
        paths = {
            "s1yh_audit": "docs/S1YH_LPRH1_STATISCHER_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT_V1.json",
            "s1yh_document": "docs/S1YH_LPRH1_STATISCHER_VOLLSTAENDIGKEITS_NICHTZIRKULARITAETS_UND_MATERIALISIERBARKEITSAUDIT.md",
            "s1yh_tests": "tests/test_lprh1_s1yh_static_contract_audit.py",
            "receptor_time_model": "mcm_field_organism/receptor_time_model.py",
            "field_step_time": "mcm_field_organism/field_step_time.py",
            "receptor_contract": "mcm_field_organism/receptor_contract.py",
            "transient_neuron_input": "mcm_field_organism/transient_neuron_input.py",
            "shared_mcm_field": "mcm_field_organism/shared_mcm_field.py",
            "ppb1_reference": "mcm_field_organism/_ppb1_reference.py",
            "s1wu_read_only_probe": "mcm_field_organism/_ppb1_s1wu_read_only_perceptual_probe.py",
            "package_root": "mcm_field_organism/__init__.py",
            "current_api": "mcm_field_organism/current_api.py",
            "root_lazy_exports": "mcm_field_organism/root_lazy_exports.py",
        }
        for role, relative in paths.items():
            self.assertEqual(contract["bound_file_digests"][role], hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_one_pure_function_has_nine_inputs_and_no_runtime_calls(self) -> None:
        function = load_contract()["future_pure_function"]
        self.assertEqual("materialize_lprh1_local_handoff", function["function_id"])
        self.assertEqual(9, len(function["input_roles_in_order"]))
        self.assertEqual(0, function["state_or_probe_calls"])
        self.assertEqual(0, function["field_calls"])

    def test_eight_canonical_payload_schemas_are_exact(self) -> None:
        rule = load_contract()["canonical_digest_rule"]
        payload_roles = [key for key in rule if key.endswith("_payload_keys")]
        self.assertEqual(8, len(payload_roles))
        self.assertIn("UTF8_JSON_ALLOW_NAN_FALSE", rule["encoding"])

    def test_handoff_ids_and_pure_single_use_ledger_are_bound(self) -> None:
        identity = load_contract()["handoff_identity"]
        self.assertEqual(9, len(identity["handoff_id_payload_keys"]))
        self.assertEqual(3, len(identity["receipt_id_payload_keys"]))
        self.assertIn("FAILS_BEFORE_OUTPUT", identity["duplicate_rule"])
        self.assertIn("SORTED_UNION", identity["successful_postcondition"])
        self.assertEqual(0, identity["retry_count"])

    def test_six_exact_type_schemas_have_unique_fields(self) -> None:
        schemas = load_contract()["exact_type_schemas"]
        self.assertEqual(6, len(schemas))
        for fields in schemas.values():
            self.assertEqual(len(fields), len(set(fields)))
        self.assertEqual(4, len(schemas["LPRH1LocalNeuronContext"]))
        self.assertEqual(18, len(schemas["LPRH1TransientLocalPrototypeContext"]))

    def test_active_types_support_atomic_timed_dock_and_receptor_inputs(self) -> None:
        timed = (ROOT / "mcm_field_organism/receptor_time_model.py").read_text(encoding="utf-8")
        field = (ROOT / "mcm_field_organism/shared_mcm_field.py").read_text(encoding="utf-8")
        transient = (ROOT / "mcm_field_organism/transient_neuron_input.py").read_text(encoding="utf-8")
        self.assertIn("class OrganismTimedReceptorFrame", timed)
        self.assertIn("class SharedFieldDock", field)
        self.assertIn("class TransientNeuronInputSet", transient)

    def test_mapping_order_is_config_authoritative_and_nonfusing(self) -> None:
        rules = load_contract()["exact_order_and_mapping_rules"]
        self.assertEqual("PPB1_CONFIG_CARRIER_IDS_IS_AUTHORITATIVE", rules["carrier_order"])
        self.assertIn("EXACTLY_ONE_CONTEXT", rules["local_projection"])
        self.assertEqual("SAME_AS_CONFIG_CARRIER_ORDER", rules["local_context_order"])
        self.assertFalse(rules["fusion_or_reordering_allowed"])

    def test_causal_envelope_cardinality_is_exact(self) -> None:
        rules = load_contract()["exact_causal_and_envelope_rules"]
        self.assertTrue(rules["timed_probe_frame_is_digest_bound_original_probe"])
        self.assertTrue(rules["target_clock_equals_probe_organism_clock"])
        self.assertTrue(rules["target_start_equals_probe_organism_end"])
        self.assertTrue(rules["receptor_input_step_equals_target_step"])
        self.assertEqual(1, rules["envelope_receptor_cardinality"])
        self.assertEqual("EXACTLY_ZERO_OR_ONE", rules["envelope_context_cardinality"])

    def test_eight_error_codes_and_exact_budget_are_bound(self) -> None:
        contract = load_contract()
        self.assertEqual(8, len(contract["finite_error_codes"]))
        budget = contract["exact_call_budget_per_valid_request"]
        self.assertEqual(1, budget["handoff_function_call_count"])
        self.assertEqual(1, budget["extraction_attempt_count"])
        self.assertTrue(all(budget[key] == 0 for key in budget if key not in {"handoff_function_call_count", "extraction_attempt_count"}))

    def test_all_seven_s1yh_blockers_are_closed(self) -> None:
        closure = load_contract()["blocker_closure"]
        self.assertEqual({f"M{index}_" for index in range(1, 8)}, {key[:3] for key in closure})
        self.assertTrue(all(value.startswith("CLOSED_BY_") for value in closure.values()))

    def test_public_surfaces_remain_without_lprh1(self) -> None:
        for relative in ("mcm_field_organism/__init__.py", "mcm_field_organism/current_api.py", "mcm_field_organism/root_lazy_exports.py"):
            source = (ROOT / relative).read_text(encoding="utf-8").lower()
            self.assertNotIn("s1yi", source)
            self.assertNotIn("lprh", source)

    def test_decision_is_complete_narrow_and_nonexecuting(self) -> None:
        contract = load_contract()
        self.assertEqual(26, contract["passed_role_count"])
        self.assertEqual(0, contract["failed_role_count"])
        self.assertEqual("PASS_LPRH1_SEVEN_MATERIALIZATION_BINDINGS_CLOSED_NO_IMPLEMENTATION_OR_EXECUTION", contract["decision"])
        self.assertTrue(all(value == 0 for value in contract["execution_counters"].values()))


if __name__ == "__main__":
    unittest.main()
