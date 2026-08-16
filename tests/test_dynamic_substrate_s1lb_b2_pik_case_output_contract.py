from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1lb_b2_pik_case_output_contract import (
    DTS1S1LBB2PIKCaseOutputContractError,
    S1_LB_DECISION,
    build_dts1_s1lb_b2_pik_case_output_contract,
)


class DTS1S1LBB2PIKCaseOutputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1lb_b2_pik_case_output_contract()

    def test_binds_exact_sequence_and_output_sources_for_c07(self) -> None:
        self.assertEqual((64, 64), (len(self.contract.source_s1ky_digest), len(self.contract.source_s1la_digest)))
        self.assertEqual(("C07", "B2", "B2_S2_LINEAR_INTEGRATOR", "P_IK_INTERFERENCE", 3, 6), self.contract.source_s1jx_case_record[:6])

    def test_binds_three_refinements_and_distinct_provenance(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual((2, 4, 8), tuple(int(value.rsplit("r", 1)[1]) for value in payload["replica_ids"]))
        self.assertEqual((3, 3), (self.contract.replica_count, self.contract.distinct_provenance_digest_count))

    def test_binds_two_terminal_checkpoints_per_refinement(self) -> None:
        self.assertEqual((2, 2), (self.contract.sequence_count_per_refinement, self.contract.checkpoint_count_per_refinement))
        self.assertTrue(self.contract.checkpoint_parent_identity_valid)

    def test_binds_distinct_sequence_terminals_and_refinement_identity(self) -> None:
        payload = dict(self.contract.case_payload)
        for key in ("terminal_field_digests", "terminal_private_state_digests", "terminal_adapter_output_digests"):
            self.assertEqual(2, len(set(payload[key])))
        self.assertTrue(self.contract.sequence_terminals_distinct)
        self.assertTrue(self.contract.terminal_digest_pairs_bit_identical_across_refinements)

    def test_binds_one_comparison_digest_and_identical_components(self) -> None:
        self.assertEqual(1, self.contract.comparison_digest_count)
        self.assertTrue(self.contract.all_components_bit_identical)
        self.assertEqual(6, self.contract.nonzero_component_count)

    def test_primary_output_is_r4_with_six_components(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual((4, 6), (self.contract.primary_refinement, self.contract.component_count_per_refinement))
        self.assertTrue(all(value != 0.0 for value in payload["primary_components"]))

    def test_composes_no_matrix_interference_or_other_judgment(self) -> None:
        self.assertTrue(self.contract.case_record_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.interference_judgment_present)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.candidate_comparison_present)

    def test_executes_nothing_and_authorizes_only_b1_pin_selection(self) -> None:
        self.assertEqual((0, 0), (self.contract.new_replicas_executed, self.contract.new_interval_calls_executed))
        self.assertTrue(self.contract.b1_pin_case_selection_authorized_next_stage)
        self.assertEqual(S1_LB_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1lb_b2_pik_case_output_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1LBB2PIKCaseOutputContractError):
            replace(self.contract, sequence_terminals_distinct=False)
        source = inspect.getsource(build_dts1_s1lb_b2_pik_case_output_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
