from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)
from mcm_field_organism.dynamic_substrate_s1jm_exposure_prestate_integrity_contract import (
    build_dts1_s1jm_exposure_prestate_integrity_contract,
)
from mcm_field_organism.dynamic_substrate_s1jn_finite_materialization_schema_contract import (
    DTS1S1JNFiniteMaterializationSchemaContractError,
    S1_JN_DECISION,
    build_dts1_s1jn_finite_materialization_schema_contract,
)


class DTS1S1JNFiniteMaterializationSchemaContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jn_finite_materialization_schema_contract()

    def test_binds_exact_s1jm_and_s1jk_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1jm_exposure_prestate_integrity_contract().contract_digest, contract.source_s1jm_digest)
        self.assertEqual(build_dts1_s1jk_corrected_monotonic_interval_contract().contract_digest, contract.source_s1jk_digest)

    def test_binds_complete_two_and_three_node_identities(self) -> None:
        rows = {row[0]: row for row in self._contract().field_identity_fixtures}
        self.assertEqual(2, self._contract().geometry_fixture_count)
        self.assertEqual(("node-a", "node-b"), tuple(row[0] for row in rows["TWO_NODE_OPEN_LINE"][5]))
        self.assertEqual(("node-a", "node-b", "node-c"), tuple(row[0] for row in rows["THREE_NODE_OPEN_LINE"][5]))
        self.assertEqual("dock.s1jn.auditory.2n", rows["TWO_NODE_OPEN_LINE"][9])
        self.assertEqual(3, len(rows["THREE_NODE_OPEN_LINE"][11]))

    def test_completes_receptor_distribution_identities(self) -> None:
        rows = {row[0]: row for row in self._contract().receptor_completion_fixtures}
        self.assertEqual("auditory", rows["ZERO_CONTACT_2N"][2])
        self.assertEqual("mcm.s1jn.receptor.3n", rows["ZERO_CONTACT_3N"][3])
        self.assertEqual((0.0, 0.0, 0.0), rows["ZERO_CONTACT_3N"][10])

    def test_binds_all_seven_private_state_schemas(self) -> None:
        rows = dict(self._contract().private_state_schemas)
        self.assertEqual(7, self._contract().model_role_count)
        self.assertEqual(("DTS1", "B1", "B2", "B3", "B4", "B5", "B6"), tuple(rows))
        self.assertIn("complete_resource_anatomy_payload", rows["DTS1"])
        self.assertIn("frozen_CONST_V_spec_digest", rows["B6"])

    def test_binds_exact_input_and_atomic_output(self) -> None:
        inputs = tuple(row[0] for row in self._contract().materializer_input_schema)
        self.assertEqual(("envelope_fixture", "model_role", "input_field", "private_state", "prior_envelope_digest", "prior_output_digest"), inputs)
        outputs = dict(self._contract().materializer_output_schema)
        self.assertEqual(("materialized_field", "receptor_distribution", "step_time", "geometry_digest"), outputs["model_invocation"])
        self.assertEqual(4, len(outputs["integrity_record"]))
        self.assertFalse(dict(self._contract().error_boundary)["partial_output"])

    def test_binds_fresh_carry_boundary_and_provenance_rules(self) -> None:
        fresh = " ".join(self._contract().fresh_field_rules)
        operations = " ".join(self._contract().prestate_operation_rules)
        provenance = " ".join(self._contract().provenance_rules)
        self.assertIn("last_distribution-is-null", fresh)
        self.assertIn("CARRY_PRIOR_SH", operations)
        self.assertIn("preserves-the-complete-input-field-by-identity", operations)
        self.assertIn("exact-prior-S1-JK-envelope-digest", provenance)

    def test_binds_canonical_digest_and_twenty_case_matrix(self) -> None:
        api = dict(self._contract().canonical_digest_api)
        self.assertIn("negative-zero-to-positive-zero", api["canonicalize_number"])
        self.assertIn("allow_nan_false", api["canonical_json"])
        self.assertEqual(20, self._contract().technical_test_count)
        self.assertEqual(tuple(f"T{index:02d}" for index in range(1, 21)), tuple(row[0] for row in self._contract().technical_test_matrix))

    def test_keeps_implementation_and_execution_closed(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.complete_identity_and_api_schema_bound)
        for value in (contract.common_interval_fixture_implemented, contract.adapters_implemented, contract.baseline_models_executed, contract.runtime_integration_present, contract.research_execution_permitted):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertTrue(contract.private_pure_materializer_implementation_authorized_next_stage)
        self.assertEqual(S1_JN_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JNFiniteMaterializationSchemaContractError):
            replace(contract, technical_test_count=19)
        with self.assertRaises(DTS1S1JNFiniteMaterializationSchemaContractError):
            replace(contract, common_interval_fixture_implemented=True)
        source = inspect.getsource(build_dts1_s1jn_finite_materialization_schema_contract)
        for forbidden in ("apply_", "compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
