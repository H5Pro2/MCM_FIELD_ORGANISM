from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_dts1_common_interval_materializer import (
    build_dts1_s1jo_implementation_receipt,
)
from mcm_field_organism.dynamic_substrate_s1it_private_adapter_contract import (
    build_dts1_s1it_private_adapter_contract,
)
from mcm_field_organism.dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from mcm_field_organism.dynamic_substrate_s1jp_baseline_adapter_bridge_contract import (
    DTS1S1JPBaselineAdapterBridgeContractError,
    S1_JP_DECISION,
    build_dts1_s1jp_baseline_adapter_bridge_contract,
)


class DTS1S1JPBaselineAdapterBridgeContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jp_baseline_adapter_bridge_contract()

    def test_binds_exact_s1jo_s1it_and_s1ja_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1jo_implementation_receipt().receipt_digest, contract.source_s1jo_digest)
        self.assertEqual(build_dts1_s1it_private_adapter_contract().contract_digest, contract.source_s1it_digest)
        self.assertEqual(build_dts1_s1ja_finite_configuration_matrix_contract().contract_digest, contract.source_s1ja_digest)

    def test_common_interval_call_remains_exactly_four_valued(self) -> None:
        self.assertEqual(
            ("materialized_field", "receptor_distribution", "step_time", "geometry_digest"),
            self._contract().common_invocation_schema,
        )

    def test_binds_six_distinct_role_bridges_and_private_schemas(self) -> None:
        contract = self._contract()
        self.assertEqual(6, contract.adapter_role_count)
        self.assertEqual(("B1", "B2", "B3", "B4", "B5", "B6"), tuple(row[0] for row in contract.adapter_bridges))
        self.assertEqual(("complete_L_state_payload", "B2_configuration_digest"), contract.adapter_bridges[1][1])

    def test_b1_and_b2_return_their_complete_private_state(self) -> None:
        rows = self._contract().adapter_bridges
        self.assertIn("bit-identical-fixed-adapter-private-state", rows[0][5])
        self.assertIn("complete-resulting-L-private-state", rows[1][5])

    def test_f3_roles_bind_exact_calculators_and_m_roundtrip(self) -> None:
        rows = self._contract().adapter_bridges[2:]
        self.assertTrue(all("advance_mcm_f3_shared_field" in row[2] for row in rows))
        self.assertTrue(all("M-digest" in row[5] for row in rows))
        self.assertIn("compute_mcm_f3_local_leaky_baseline", rows[0][2])
        self.assertIn("compute_mcm_f3_linear_coupled_baseline", rows[1][2])
        self.assertIn("compute_mcm_f3_coupling", rows[2][2])
        self.assertIn("compute_w7n_coupling_baseline:const-v", rows[3][2])

    def test_integrity_control_and_candidate_data_are_inaccessible(self) -> None:
        rules = " ".join(self._contract().information_barrier_rules)
        self.assertIn("digests-never-enter-a-baseline-kernel", rules)
        self.assertIn("candidate-sidecar-never-enter", rules)
        self.assertIn("no-global-closure-cache-replay-retry", rules)

    def test_time_refinement_preserves_one_physical_interval(self) -> None:
        rules = " ".join(self._contract().time_and_refinement_rules)
        self.assertIn("only-from-the-S1-JO-step-time", rules)
        self.assertIn("equal-contiguous-subwindows", rules)
        self.assertIn("never-reapplied", rules)
        self.assertIn("complete-original-S1-JO-window", rules)

    def test_output_is_complete_explicit_and_atomic(self) -> None:
        schema = " ".join(self._contract().output_schema)
        self.assertIn("one-complete-SharedMCMField", schema)
        self.assertIn("one-complete-next-private-state", schema)
        self.assertIn("one-canonical-output-digest", schema)
        self.assertIn("no-field-state-diagnostic-or-digest-partial-output", schema)

    def test_zero_contact_and_neutral_controls_are_not_reinterpreted(self) -> None:
        rules = " ".join(self._contract().neutral_and_failure_rules)
        self.assertIn("never-short-circuited-as-no-ops", rules)
        self.assertIn("delegate-to-that-path-without-reimplementation", rules)
        self.assertIn("may-remove-only-the-bound-model-specific-contribution", rules)

    def test_validation_is_before_atomic_publication(self) -> None:
        phases = self._contract().validation_order
        self.assertEqual("exact-adapter-role-private-schema-configuration-digest-and-refinement", phases[0])
        self.assertEqual("canonical-complete-output-digest-and-atomic-publication", phases[-1])

    def test_binds_fourteen_technical_classes(self) -> None:
        contract = self._contract()
        self.assertEqual(14, contract.technical_test_count)
        self.assertEqual(tuple(f"T{index:02d}" for index in range(1, 15)), tuple(row[0] for row in contract.technical_test_matrix))

    def test_implements_and_executes_nothing(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.complete_bridge_contract_bound)
        self.assertTrue(contract.private_adapter_implementation_authorized_next_stage)
        self.assertEqual((False, False, False, False, False), (contract.adapter_context_implemented, contract.adapters_implemented, contract.baseline_models_executed, contract.runtime_integration_present, contract.research_execution_permitted))
        self.assertEqual((0, 0), (contract.technical_field_steps_executed, contract.research_field_steps_executed))
        self.assertEqual(S1_JP_DECISION, contract.decision)

    def test_is_deterministic_and_tamper_evident(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JPBaselineAdapterBridgeContractError):
            replace(contract, adapter_role_count=5)
        with self.assertRaises(DTS1S1JPBaselineAdapterBridgeContractError):
            replace(contract, adapters_implemented=True)

    def test_builder_contains_no_kernel_or_runtime_call(self) -> None:
        source = inspect.getsource(build_dts1_s1jp_baseline_adapter_bridge_contract)
        for forbidden in ("advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
