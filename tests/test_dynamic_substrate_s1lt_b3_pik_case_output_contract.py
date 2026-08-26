from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_LS_TARGET_COMPONENTS_BY_REFINEMENT,
    S1_LS_TARGET_REPLICA_IDS,
    build_dts1_s1ls_implementation_receipt,
)
from mcm_field_organism.dynamic_substrate_s1lr_b3_pik_case_selection_contract import (
    build_dts1_s1lr_b3_pik_case_selection_contract,
)
from mcm_field_organism.dynamic_substrate_s1lt_b3_pik_case_output_contract import (
    DTS1S1LTB3PIKCaseOutputContractError,
    S1_LT_CASE_OUTPUT_DIGEST,
    S1_LT_DECISION,
    S1_LT_REFINEMENT_RESIDUALS,
    S1_LT_SOURCE_S1LR_DIGEST,
    S1_LT_SOURCE_S1LS_DIGEST,
    _case_payload,
    build_dts1_s1lt_b3_pik_case_output_contract,
)


class DTS1S1LTB3PIKCaseOutputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1lt_b3_pik_case_output_contract()

    def test_binds_exact_sources_and_c11_case(self) -> None:
        self.assertEqual((64, 64), (len(self.contract.source_s1lr_digest), len(self.contract.source_s1ls_digest)))
        self.assertEqual(S1_LT_SOURCE_S1LR_DIGEST, self.contract.source_s1lr_digest)
        self.assertEqual(S1_LT_SOURCE_S1LS_DIGEST, self.contract.source_s1ls_digest)
        self.assertEqual(("C11", "B3", "B3_F3_LOCAL_LEAKY", "P_IK_INTERFERENCE", 3, 6), self.contract.source_s1jx_case_record[:6])

    def test_binds_three_refinements_and_primary_components(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual(S1_LS_TARGET_REPLICA_IDS, payload["replica_ids"])
        self.assertEqual((2, 4, 8), tuple(int(value.rsplit("r", 1)[1]) for value in payload["replica_ids"]))
        self.assertEqual(S1_LS_TARGET_COMPONENTS_BY_REFINEMENT, payload["components_by_refinement"])
        self.assertEqual(4, self.contract.primary_refinement)
        self.assertEqual(payload["primary_components"], dict(payload["components_by_refinement"])[4])
        self.assertTrue(self.contract.primary_components_nonzero)

    def test_binds_two_directed_nonzero_residual_blocks(self) -> None:
        residuals = dict(dict(self.contract.case_payload)["refinement_residuals"])
        self.assertEqual(("r2_minus_r4", "r4_minus_r8"), tuple(residuals))
        self.assertEqual(dict(S1_LT_REFINEMENT_RESIDUALS), residuals)
        self.assertEqual((2, 12), (self.contract.residual_block_count, self.contract.residual_component_count))
        self.assertFalse(self.contract.all_refinement_residuals_zero)
        self.assertTrue(self.contract.residuals_shrink_r4_to_r8)

    def test_binds_complete_checkpoint_digest_matrices(self) -> None:
        payload = dict(self.contract.case_payload)
        for key in ("checkpoint_field_digests", "checkpoint_private_state_digests", "checkpoint_adapter_output_digests"):
            self.assertEqual((3, 2), (len(payload[key]), len(payload[key][0])))

    def test_composes_no_matrix_or_judgment(self) -> None:
        self.assertTrue(self.contract.case_record_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.candidate_comparison_present)
        self.assertFalse(self.contract.runtime_integration_present)

    def test_executes_nothing_and_authorizes_only_c12_selection(self) -> None:
        self.assertEqual((0, 0), (self.contract.new_replicas_executed, self.contract.new_interval_calls_executed))
        self.assertTrue(self.contract.c12_selection_authorized_next_stage)
        self.assertEqual(S1_LT_DECISION, self.contract.decision)

    def test_case_payload_digest_and_chain_are_deterministic(self) -> None:
        self.assertEqual(S1_LT_CASE_OUTPUT_DIGEST, self.contract.case_output_digest)
        self.assertEqual(tuple(_case_payload().items()), self.contract.case_payload)
        second = build_dts1_s1lt_b3_pik_case_output_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        self.assertEqual(S1_LT_CASE_OUTPUT_DIGEST, second.case_output_digest)

    def test_tamper_closed_and_call_free(self) -> None:
        with self.assertRaises(DTS1S1LTB3PIKCaseOutputContractError):
            replace(self.contract, baseline_judgment_present=True)
        s1lr = build_dts1_s1lr_b3_pik_case_selection_contract()
        s1ls = build_dts1_s1ls_implementation_receipt()
        self.assertEqual(S1_LT_SOURCE_S1LR_DIGEST, s1lr.contract_digest)
        self.assertEqual(S1_LT_SOURCE_S1LS_DIGEST, s1ls.receipt_digest)
        source = inspect.getsource(build_dts1_s1lt_b3_pik_case_output_contract)
        for forbidden in ("run_dts1_b3_pik_three_refinement", "run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
