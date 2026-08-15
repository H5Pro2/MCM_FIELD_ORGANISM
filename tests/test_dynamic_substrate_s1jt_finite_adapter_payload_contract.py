from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from mcm_field_organism.dynamic_substrate_s1jn_finite_materialization_schema_contract import (
    build_dts1_s1jn_finite_materialization_schema_contract,
)
from mcm_field_organism.dynamic_substrate_s1js_adapter_payload_readiness_precheck import (
    build_dts1_s1js_adapter_payload_readiness_precheck,
)
from mcm_field_organism.dynamic_substrate_s1jt_finite_adapter_payload_contract import (
    DTS1S1JTFiniteAdapterPayloadContractError,
    S1_JT_B6_SPEC_DIGEST,
    S1_JT_DECISION,
    build_dts1_s1jt_finite_adapter_payload_contract,
)


class DTS1S1JTFiniteAdapterPayloadContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jt_finite_adapter_payload_contract()

    def test_binds_exact_s1js_s1jn_and_s1ja_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1js_adapter_payload_readiness_precheck().audit_digest, contract.source_s1js_digest)
        self.assertEqual(build_dts1_s1jn_finite_materialization_schema_contract().contract_digest, contract.source_s1jn_digest)
        self.assertEqual(build_dts1_s1ja_finite_configuration_matrix_contract().contract_digest, contract.source_s1ja_digest)

    def test_binds_all_six_existing_configuration_digests(self) -> None:
        records = self._contract().configuration_digests
        self.assertEqual(6, len(records))
        self.assertTrue(all(len(digest) == 64 for _role, digest in records))

    def test_binds_common_fast_runtime_without_new_values(self) -> None:
        record = dict(self._contract().common_fast_runtime_record)
        self.assertEqual((1.0, 0.5, 0.0), (record["response_time_seconds"], record["afterimage_time_constant_seconds"], record["leak_rate_per_second"]))

    def test_b1_schema_binds_exact_two_and_three_node_rates(self) -> None:
        schema = dict(self._contract().b1_fixed_adapter_schema)
        self.assertEqual((("node-a", "node-b", 1.2),), schema["two_node_edges"])
        self.assertEqual((("node-a", "node-b", 1.1), ("node-b", "node-c", 1.1)), schema["three_node_edges"])
        self.assertIn("DTS1BackreactionResult", schema["roundtrip"])

    def test_b2_schema_is_node_bound_finite_and_complete(self) -> None:
        schema = dict(self._contract().b2_l_schema)
        self.assertEqual(("node_id", "value"), schema["entry_fields"])
        self.assertIn("every-field-node", schema["shape"])
        self.assertIn("closed-minus-one-plus-one", schema["domain"])

    def test_b2_commit_uses_standard_field_advance_and_returns_L(self) -> None:
        rules = " ".join(self._contract().b2_field_commit)
        self.assertIn("SharedMCMField.advance", rules)
        self.assertIn("original-distribution-and-step-time", rules)
        self.assertIn("complete-next-B2-private-L", rules)

    def test_binds_exact_f3_arm_and_calculator_records(self) -> None:
        contract = self._contract()
        self.assertEqual(4, len(contract.f3_runtime_records))
        self.assertEqual("mcm.s1jt.b3.local-leaky", contract.f3_runtime_records[0][1])
        self.assertEqual("compute_mcm_f3_coupling", contract.f3_runtime_records[2][6])
        self.assertEqual(0.5, contract.f3_runtime_records[3][2])

    def test_b6_spec_payload_and_digest_are_finite(self) -> None:
        contract = self._contract()
        payload = dict(contract.b6_spec_payload)
        self.assertEqual("const-v", payload["model_id"])
        self.assertEqual(("eta", 1.0), payload["parameter_bindings"][0])
        self.assertEqual(S1_JT_B6_SPEC_DIGEST, contract.b6_spec_digest)
        self.assertEqual(64, len(contract.b6_spec_digest))

    def test_private_state_return_is_complete_for_every_role(self) -> None:
        rules = " ".join(self._contract().private_state_return_rules)
        for token in ("B1-returns", "B2-returns", "B3-through-B5-return", "B6-returns"):
            self.assertIn(token, rules)
        self.assertIn("exact-S1-JN-role-key-order", rules)

    def test_binds_three_finite_diagnostic_variants(self) -> None:
        variants = self._contract().diagnostic_union
        self.assertEqual(3, self._contract().diagnostic_variant_count)
        self.assertEqual(("B1_EXACT", "B2_EXACT", "B3_B6_F3"), tuple(row[0] for row in variants))
        self.assertIn("refinement", variants[2][2])

    def test_output_payload_excludes_control_and_integrity_data(self) -> None:
        schema = dict(self._contract().output_payload_schema)
        self.assertEqual(("schema_id", "model_role", "complete_field", "next_private_state", "diagnostics"), schema["fields"])
        self.assertIn("control_label", schema["excluded"])
        self.assertIn("integrity_digests", schema["excluded"])

    def test_binds_canonical_digest_and_atomic_error_boundary(self) -> None:
        digest_api = " ".join(value for _key, value in self._contract().canonical_digest_api)
        error = dict(self._contract().error_boundary)
        self.assertIn("negative-zero-to-positive-zero", digest_api)
        self.assertEqual("DTS1PrivateBaselineAdapterError", error["public_error"])
        self.assertFalse(error["partial_output"])
        self.assertFalse(error["retry"])

    def test_binds_twenty_technical_classes(self) -> None:
        contract = self._contract()
        self.assertEqual(20, contract.technical_test_count)
        self.assertEqual(tuple(f"T{index:02d}" for index in range(1, 21)), tuple(row[0] for row in contract.technical_test_matrix))

    def test_authorizes_implementation_but_executes_nothing(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.finite_payload_and_output_contract_bound)
        self.assertTrue(contract.private_adapter_implementation_authorized_next_stage)
        self.assertFalse(contract.adapters_implemented)
        self.assertFalse(contract.baseline_models_executed)
        self.assertFalse(contract.runtime_integration_present)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_JT_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JTFiniteAdapterPayloadContractError):
            replace(contract, adapters_implemented=True)
        source = inspect.getsource(build_dts1_s1jt_finite_adapter_payload_contract)
        for forbidden in ("advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
