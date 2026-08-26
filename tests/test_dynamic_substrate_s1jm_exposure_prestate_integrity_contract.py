from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)
from mcm_field_organism.dynamic_substrate_s1jl_model_view_equivalence_precheck import (
    build_dts1_s1jl_model_view_equivalence_precheck,
)
from mcm_field_organism.dynamic_substrate_s1jm_exposure_prestate_integrity_contract import (
    DTS1S1JMExposurePrestateIntegrityContractError,
    S1_JM_DECISION,
    build_dts1_s1jm_exposure_prestate_integrity_contract,
)


class DTS1S1JMExposurePrestateIntegrityContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jm_exposure_prestate_integrity_contract()

    def test_binds_exact_s1jl_and_s1jk_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1jl_model_view_equivalence_precheck().audit_digest, contract.source_s1jl_digest)
        self.assertEqual(build_dts1_s1jk_corrected_monotonic_interval_contract().contract_digest, contract.source_s1jk_digest)

    def test_binds_four_noninterchangeable_digest_roles(self) -> None:
        contract = self._contract()
        rows = {row[0]: row[1:] for row in contract.digest_roles}
        self.assertEqual(4, contract.digest_role_count)
        self.assertIn("common_exposure_digest", rows)
        self.assertIn("private_prestate_digest", rows)
        self.assertIn("materialized_input_digest", rows)
        self.assertIn("orchestration_control_digest", rows)
        self.assertIn("cross-model-equality", rows["common_exposure_digest"][1])
        self.assertIn("never-a-cross-model-equality", rows["private_prestate_digest"][1])

    def test_model_receives_only_four_value_objects(self) -> None:
        contract = self._contract()
        self.assertEqual(("materialized_field", "receptor_distribution", "step_time", "geometry_digest"), contract.model_invocation_fields)
        self.assertEqual(4, contract.model_invocation_field_count)
        exclusions = " ".join(contract.model_invocation_exclusions)
        self.assertIn("all-four-integrity-digests", exclusions)
        self.assertIn("checkpoint", exclusions)
        self.assertIn("candidate-sidecar-for-B1-through-B6", exclusions)

    def test_binds_external_equivalence_matrix(self) -> None:
        rows = self._contract().cross_model_equivalence_matrix
        self.assertIn(("P_IE_F_HIGH_vs_R_HIGH", (1, 2), "COMMON_EXPOSURE_EQUAL_BY_ORDINAL"), rows)
        self.assertIn(("P_IN_RECOVERY_ON_vs_OFF", (1, 2, 3, 4), "COMMON_EXPOSURE_EQUAL_BY_ORDINAL"), rows)
        self.assertIn(("P_IK_A_B_A_vs_A_GAP_A", (2,), "COMMON_EXPOSURE_INTENTIONALLY_DIFFERENT_B_VS_GAP"), rows)

    def test_keeps_checkpoint_out_of_causal_exposure_and_model_input(self) -> None:
        exposure_fields = tuple(row[0] for row in self._contract().common_exposure_payload_schema)
        control_fields = tuple(row[0] for row in self._contract().orchestration_control_schema)
        self.assertNotIn("checkpoint_after_interval", exposure_fields)
        self.assertIn("checkpoint_after_interval", control_fields)

    def test_private_state_is_provenance_not_result_gate(self) -> None:
        rules = " ".join(self._contract().private_state_rules)
        self.assertIn("may-be-equal-or-different", rules)
        self.assertIn("neither-outcome-is-an-acceptance-condition", rules)
        self.assertIn("no-private-digest-may-select", rules)

    def test_binds_value_only_canonicalization(self) -> None:
        rules = " ".join(self._contract().canonicalization_rules)
        self.assertIn("no-object-repr-memory-address-or-process-state", rules)
        self.assertIn("negative-zero-is-canonicalized-to-positive-zero", rules)
        self.assertIn("allow-nan-false", rules)

    def test_keeps_materialization_and_execution_closed(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.exposure_prestate_separation_bound)
        for value in (contract.materialization_identity_schema_bound, contract.common_interval_fixture_implemented, contract.adapters_implemented, contract.baseline_models_executed, contract.runtime_integration_present, contract.research_execution_permitted):
            self.assertFalse(value)
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertTrue(contract.finite_materialization_schema_contract_authorized_next_stage)
        self.assertEqual(S1_JM_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_execution_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JMExposurePrestateIntegrityContractError):
            replace(contract, digest_role_count=3)
        with self.assertRaises(DTS1S1JMExposurePrestateIntegrityContractError):
            replace(contract, materialization_identity_schema_bound=True)
        source = inspect.getsource(build_dts1_s1jm_exposure_prestate_integrity_contract)
        for forbidden in ("apply_", "compute_", "advance_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
