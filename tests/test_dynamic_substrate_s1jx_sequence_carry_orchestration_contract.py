from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_dts1_private_baseline_adapters import (
    build_dts1_s1jw_implementation_receipt,
)
from mcm_field_organism.dynamic_substrate_s1ir_corrected_profile_contract import (
    build_dts1_s1ir_corrected_profile_contract,
)
from mcm_field_organism.dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from mcm_field_organism.dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)
from mcm_field_organism.dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    DTS1S1JXSequenceCarryOrchestrationContractError,
    S1_JX_DECISION,
    build_dts1_s1jx_sequence_carry_orchestration_contract,
)


class DTS1S1JXSequenceCarryOrchestrationContractTests(unittest.TestCase):
    def _contract(self):
        return build_dts1_s1jx_sequence_carry_orchestration_contract()

    def test_binds_exact_four_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(build_dts1_s1jw_implementation_receipt().receipt_digest, contract.source_s1jw_digest)
        self.assertEqual(build_dts1_s1jk_corrected_monotonic_interval_contract().contract_digest, contract.source_s1jk_digest)
        self.assertEqual(build_dts1_s1ja_finite_configuration_matrix_contract().contract_digest, contract.source_s1ja_digest)
        self.assertEqual(build_dts1_s1ir_corrected_profile_contract().contract_digest, contract.source_s1ir_digest)

    def test_binds_seven_sequences_and_twenty_three_envelopes(self) -> None:
        contract = self._contract()
        self.assertEqual(7, contract.sequence_count)
        self.assertEqual(23, contract.envelope_count_per_role_refinement)
        self.assertEqual(23, sum(len(row[6]) for row in contract.sequence_records))

    def test_profile_sequence_membership_is_exact(self) -> None:
        records = dict(self._contract().profile_sequence_keys)
        self.assertEqual(("P_IE_F_HIGH", "P_IE_R_HIGH"), records["P_IE_CAUSAL_TWO_SUBSTEP"])
        self.assertEqual(("P_IH_A_A_A",), records["P_IH_ATTENUATION"])
        self.assertEqual(("P_IK_A_B_A", "P_IK_A_GAP_A"), records["P_IK_INTERFERENCE"])
        self.assertEqual(("P_IN_RECOVERY_ON", "P_IN_RECOVERY_OFF"), records["P_IN_RELEASE_REUSE"])

    def test_checkpoint_ordinals_match_registered_envelopes(self) -> None:
        contract = self._contract()
        self.assertEqual(11, contract.checkpoint_count_per_role_refinement)
        records = {row[0]: row for row in contract.sequence_records}
        for key, ordinals in contract.checkpoint_ordinals:
            self.assertEqual(ordinals, records[key][5])

    def test_binds_six_roles_four_profiles_and_three_refinements(self) -> None:
        contract = self._contract()
        self.assertEqual((2, 4, 8), contract.refinement_levels)
        self.assertEqual(4, contract.primary_refinement)
        self.assertEqual(72, contract.replica_count)
        self.assertEqual(72, len({row[0] for row in contract.replica_records}))

    def test_binds_twenty_four_cases_and_three_replicas_each(self) -> None:
        contract = self._contract()
        self.assertEqual(24, contract.case_count)
        self.assertEqual(tuple(f"C{index:02d}" for index in range(1, 25)), tuple(row[0] for row in contract.case_records))
        self.assertTrue(all(len(row[6]) == 3 for row in contract.case_records))

    def test_planned_interval_cardinality_is_exact(self) -> None:
        contract = self._contract()
        self.assertEqual(414, contract.planned_baseline_interval_calls)
        self.assertEqual(6 * 3 * 23, contract.planned_baseline_interval_calls)

    def test_initialization_is_fresh_per_sequence_and_role_owned(self) -> None:
        rules = " ".join(self._contract().replica_initialization_rules)
        self.assertIn("independent-sequence", rules)
        self.assertIn("not-from-a-sibling-sequence", rules)
        self.assertIn("uniform-zero-L", rules)
        self.assertIn("complete-uniform-M", rules)
        self.assertIn("no-DTS1-candidate-sidecar", rules)

    def test_carry_keeps_field_private_state_and_provenance_together(self) -> None:
        rules = " ".join(self._contract().interval_carry_rules)
        self.assertIn("complete-field-as-the-next-interval-input-field", rules)
        self.assertIn("next-private-state-as-the-next-private-state", rules)
        self.assertIn("envelope-digest-and-canonical-complete-output-digest", rules)
        self.assertIn("replace-only-S-H", rules)
        self.assertIn("zero-contact-intervals-are-executed", rules)

    def test_forbids_every_cross_replica_carry(self) -> None:
        exclusions = " ".join(self._contract().carry_exclusions)
        self.assertIn("no-state-crosses-refinement-role-profile", exclusions)
        self.assertIn("no-r2-output-initializes-r4", exclusions)
        self.assertIn("no-checkpoint-diagnostic-residual", exclusions)
        self.assertIn("no-failed-or-partial-replica-state", exclusions)

    def test_checkpoint_and_signed_component_rules_are_exact(self) -> None:
        contract = self._contract()
        self.assertEqual((8, 8, 6, 6), tuple(row[2] for row in contract.signed_component_rules))
        self.assertEqual(28, contract.profile_component_count)
        rules = " ".join(contract.checkpoint_rules)
        self.assertIn("registered-checkpoint-boolean-is-true", rules)
        self.assertIn("read-only", rules)

    def test_refinement_outputs_separate_exact_and_native_roles(self) -> None:
        rules = " ".join(self._contract().refinement_output_rules)
        self.assertIn("B1-and-B2-require-bit-identical", rules)
        self.assertIn("B3-through-B6-publish-complete-signed-r2-minus-r4", rules)
        self.assertIn("primary-profile-components-are-r4", rules)
        self.assertIn("no-threshold-fit", rules)

    def test_atomicity_blocks_partial_replica_case_and_matrix(self) -> None:
        rules = " ".join(self._contract().atomicity_rules)
        self.assertIn("invalidates-the-complete-replica", rules)
        self.assertIn("invalidates-all-three-refinements", rules)
        self.assertIn("no-partial-sequence-checkpoint-component", rules)
        self.assertIn("only-after-all-24-complete-cases-succeed", rules)

    def test_executes_nothing_and_authorizes_only_implementation(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.orchestration_contract_bound)
        self.assertFalse(contract.orchestrator_implemented)
        self.assertEqual((0, 0), (contract.profile_cases_executed, contract.baseline_interval_calls_executed))
        self.assertFalse(contract.runtime_integration_present)
        self.assertFalse(contract.research_execution_permitted)
        self.assertTrue(contract.orchestrator_implementation_authorized_next_stage)
        self.assertEqual(S1_JX_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1JXSequenceCarryOrchestrationContractError):
            replace(contract, profile_cases_executed=1)
        source = inspect.getsource(build_dts1_s1jx_sequence_carry_orchestration_contract)
        for forbidden in ("materialize_", "advance_", "compute_", "execute_", "run_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
