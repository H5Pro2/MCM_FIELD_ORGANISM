from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_LW_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
    S1_LW_CHECKPOINT_FIELD_DIGESTS,
    S1_LW_CHECKPOINT_PRIVATE_STATE_DIGESTS,
    S1_LW_TARGET_COMPONENTS_BY_REFINEMENT,
    S1_LW_TARGET_REPLICA_IDS,
    build_dts1_s1lw_implementation_receipt,
)
from mcm_field_organism.dynamic_substrate_s1lv_b3_pin_case_selection_contract import (
    build_dts1_s1lv_b3_pin_case_selection_contract,
)
from mcm_field_organism.dynamic_substrate_s1lx_b3_pin_case_output_contract import (
    DTS1S1LXB3PINCaseOutputContractError,
    S1_LX_CASE_OUTPUT_DIGEST,
    S1_LX_DECISION,
    S1_LX_REFINEMENT_RESIDUALS,
    S1_LX_SOURCE_S1LV_DIGEST,
    S1_LX_SOURCE_S1LW_DIGEST,
    _case_payload,
    build_dts1_s1lx_b3_pin_case_output_contract,
)


class DTS1S1LXB3PINCaseOutputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1lx_b3_pin_case_output_contract()

    def test_binds_exact_sources_and_c12_case(self) -> None:
        self.assertEqual(
            (64, 64),
            (
                len(self.contract.source_s1lv_digest),
                len(self.contract.source_s1lw_digest),
            ),
        )
        self.assertEqual(S1_LX_SOURCE_S1LV_DIGEST, self.contract.source_s1lv_digest)
        self.assertEqual(S1_LX_SOURCE_S1LW_DIGEST, self.contract.source_s1lw_digest)
        self.assertEqual(
            ("C12", "B3", "B3_F3_LOCAL_LEAKY", "P_IN_RELEASE_REUSE", 3, 6),
            self.contract.source_s1jx_case_record[:6],
        )

    def test_binds_three_refinements_and_zero_primary_components(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual(S1_LW_TARGET_REPLICA_IDS, payload["replica_ids"])
        self.assertEqual(
            (2, 4, 8),
            tuple(int(value.rsplit("r", 1)[1]) for value in payload["replica_ids"]),
        )
        self.assertEqual(
            S1_LW_TARGET_COMPONENTS_BY_REFINEMENT,
            payload["components_by_refinement"],
        )
        self.assertEqual(4, self.contract.primary_refinement)
        self.assertEqual(
            payload["primary_components"],
            dict(payload["components_by_refinement"])[4],
        )
        self.assertEqual((0.0,) * 6, payload["primary_components"])
        self.assertTrue(self.contract.all_primary_components_zero)
        self.assertFalse(self.contract.primary_components_nonzero)

    def test_binds_two_directed_zero_residual_blocks(self) -> None:
        residuals = dict(dict(self.contract.case_payload)["refinement_residuals"])
        self.assertEqual(("r2_minus_r4", "r4_minus_r8"), tuple(residuals))
        self.assertEqual(dict(S1_LX_REFINEMENT_RESIDUALS), residuals)
        self.assertEqual((0.0,) * 6, residuals["r2_minus_r4"])
        self.assertEqual((0.0,) * 6, residuals["r4_minus_r8"])
        self.assertEqual(
            (2, 12),
            (
                self.contract.residual_block_count,
                self.contract.residual_component_count,
            ),
        )
        self.assertTrue(self.contract.all_refinement_residuals_zero)

    def test_binds_complete_bit_identical_checkpoint_digest_matrices(self) -> None:
        payload = dict(self.contract.case_payload)
        expected = {
            "checkpoint_field_digests": S1_LW_CHECKPOINT_FIELD_DIGESTS,
            "checkpoint_private_state_digests": S1_LW_CHECKPOINT_PRIVATE_STATE_DIGESTS,
            "checkpoint_adapter_output_digests": S1_LW_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
        }
        for key, rows in expected.items():
            self.assertEqual(rows, payload[key])
            self.assertEqual((3, 2), (len(payload[key]), len(payload[key][0])))
            self.assertTrue(all(row[0] == row[1] for row in payload[key]))
        self.assertTrue(self.contract.independent_sequence_terminals_bit_identical)

    def test_composes_no_matrix_or_judgment(self) -> None:
        self.assertTrue(self.contract.case_record_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.candidate_comparison_present)
        self.assertFalse(self.contract.runtime_integration_present)

    def test_executes_nothing_and_authorizes_only_c13_selection(self) -> None:
        self.assertEqual(
            (0, 0),
            (
                self.contract.new_replicas_executed,
                self.contract.new_interval_calls_executed,
            ),
        )
        self.assertTrue(self.contract.c13_selection_authorized_next_stage)
        self.assertEqual(S1_LX_DECISION, self.contract.decision)

    def test_case_payload_digest_and_chain_are_deterministic(self) -> None:
        self.assertEqual(S1_LX_CASE_OUTPUT_DIGEST, self.contract.case_output_digest)
        self.assertEqual(tuple(_case_payload().items()), self.contract.case_payload)
        second = build_dts1_s1lx_b3_pin_case_output_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        self.assertEqual(S1_LX_CASE_OUTPUT_DIGEST, second.case_output_digest)

    def test_tamper_closed_and_call_free(self) -> None:
        with self.assertRaises(DTS1S1LXB3PINCaseOutputContractError):
            replace(self.contract, baseline_judgment_present=True)
        s1lv = build_dts1_s1lv_b3_pin_case_selection_contract()
        s1lw = build_dts1_s1lw_implementation_receipt()
        self.assertEqual(S1_LX_SOURCE_S1LV_DIGEST, s1lv.contract_digest)
        self.assertEqual(S1_LX_SOURCE_S1LW_DIGEST, s1lw.receipt_digest)
        source = inspect.getsource(build_dts1_s1lx_b3_pin_case_output_contract)
        for forbidden in (
            "run_dts1_b3_pin_three_refinement",
            "run_dts1_one_replica",
            "materialize_",
            "advance_",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
