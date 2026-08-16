from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1mb_b4_pie_case_output_contract import (
    DTS1S1MBB4PIECaseOutputContractError,
    S1_MB_DECISION,
    build_dts1_s1mb_b4_pie_case_output_contract,
)


class DTS1S1MBB4PIECaseOutputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1mb_b4_pie_case_output_contract()

    def test_binds_exact_gate_output_sources_and_c13(self) -> None:
        self.assertEqual(
            (64, 64),
            (
                len(self.contract.source_s1ly_digest),
                len(self.contract.source_s1ma_digest),
            ),
        )
        self.assertEqual(
            (
                "C13",
                "B4",
                "B4_F3_LINEAR_COUPLED",
                "P_IE_CAUSAL_TWO_SUBSTEP",
                2,
                8,
            ),
            self.contract.source_s1jx_case_record[:6],
        )

    def test_binds_three_refinements_and_distinct_digests(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual(
            (2, 4, 8),
            tuple(int(value.rsplit("r", 1)[1]) for value in payload["replica_ids"]),
        )
        self.assertEqual(
            (3, 3, 3),
            (
                self.contract.replica_count,
                self.contract.distinct_provenance_digest_count,
                self.contract.comparison_digest_count,
            ),
        )

    def test_binds_checkpoints_and_independent_sequence_identity(self) -> None:
        self.assertEqual(
            (2, 4),
            (
                self.contract.sequence_count_per_refinement,
                self.contract.checkpoint_count_per_refinement,
            ),
        )
        self.assertTrue(self.contract.checkpoint_parent_identity_valid)
        self.assertTrue(self.contract.independent_sequences_bit_identical_within_refinement)
        self.assertTrue(self.contract.refinement_outputs_distinct)

    def test_primary_output_is_r4_with_eight_zero_components(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual(
            (4, 8),
            (
                self.contract.primary_refinement,
                self.contract.component_count_per_refinement,
            ),
        )
        self.assertEqual((0.0,) * 8, payload["primary_components"])
        self.assertTrue(self.contract.all_primary_components_zero)

    def test_binds_two_complete_directed_residual_blocks(self) -> None:
        residuals = dict(dict(self.contract.case_payload)["refinement_residuals"])
        self.assertEqual(("r2_minus_r4", "r4_minus_r8"), tuple(residuals))
        self.assertEqual(((0.0,) * 8, (0.0,) * 8), tuple(residuals.values()))
        self.assertEqual(
            (2, 16),
            (
                self.contract.residual_block_count,
                self.contract.residual_component_count,
            ),
        )
        self.assertTrue(self.contract.all_refinement_residuals_zero)

    def test_binds_complete_checkpoint_digest_matrices(self) -> None:
        payload = dict(self.contract.case_payload)
        for key in (
            "checkpoint_field_digests",
            "checkpoint_private_state_digests",
            "checkpoint_adapter_output_digests",
        ):
            self.assertEqual((3, 4), (len(payload[key]), len(payload[key][0])))

    def test_composes_no_matrix_or_judgment(self) -> None:
        self.assertTrue(self.contract.case_record_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.candidate_comparison_present)

    def test_executes_nothing_and_authorizes_only_matrix_gate(self) -> None:
        self.assertEqual(
            (0, 0),
            (
                self.contract.new_replicas_executed,
                self.contract.new_interval_calls_executed,
            ),
        )
        self.assertTrue(self.contract.matrix_gate_authorized_next_stage)
        self.assertEqual(S1_MB_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1mb_b4_pie_case_output_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1MBB4PIECaseOutputContractError):
            replace(self.contract, all_refinement_residuals_zero=False)
        source = inspect.getsource(build_dts1_s1mb_b4_pie_case_output_contract)
        for forbidden in ("run_dts1_one_replica", "run_dts1_b4_pie_three_refinement", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
