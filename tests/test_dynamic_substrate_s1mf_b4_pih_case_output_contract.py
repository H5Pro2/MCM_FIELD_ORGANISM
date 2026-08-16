from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1mf_b4_pih_case_output_contract import (
    DTS1S1MFB4PIHCaseOutputContractError,
    S1_MF_DECISION,
    build_dts1_s1mf_b4_pih_case_output_contract,
)


class DTS1S1MFB4PIHCaseOutputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1mf_b4_pih_case_output_contract()

    def test_binds_exact_selection_output_sources_and_c14(self) -> None:
        self.assertEqual(
            (64, 64),
            (
                len(self.contract.source_s1md_digest),
                len(self.contract.source_s1me_receipt_digest),
            ),
        )
        self.assertEqual(
            (
                "C14",
                "B4",
                "B4_F3_LINEAR_COUPLED",
                "P_IH_ATTENUATION",
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

    def test_binds_checkpoints_without_additional_sequences(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual(
            (1, 3),
            (
                self.contract.sequence_count_per_refinement,
                self.contract.checkpoint_count_per_refinement,
            ),
        )
        for key in (
            "checkpoint_field_digests",
            "checkpoint_private_state_digests",
            "checkpoint_adapter_output_digests",
        ):
            self.assertEqual((3, 3), (len(payload[key]), len(payload[key][0])))
        self.assertTrue(self.contract.checkpoint_parent_identity_valid)
        self.assertTrue(self.contract.refinement_outputs_distinct)

    def test_primary_output_is_r4_with_eight_nonzero_components(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual(
            (4, 8),
            (
                self.contract.primary_refinement,
                self.contract.component_count_per_refinement,
            ),
        )
        self.assertEqual(
            dict(payload["components_by_refinement"])[4],
            payload["primary_components"],
        )
        self.assertFalse(self.contract.all_primary_components_zero)
        self.assertTrue(self.contract.primary_components_nonzero)

    def test_binds_two_complete_directed_nonzero_residual_blocks(self) -> None:
        residuals = dict(dict(self.contract.case_payload)["refinement_residuals"])
        self.assertEqual(("r2_minus_r4", "r4_minus_r8"), tuple(residuals))
        self.assertEqual(
            (2, 16),
            (
                self.contract.residual_block_count,
                self.contract.residual_component_count,
            ),
        )
        self.assertFalse(self.contract.all_refinement_residuals_zero)
        self.assertTrue(self.contract.refinement_residuals_nonzero_present)

    def test_composes_no_matrix_judgment_memory_or_ai_claim(self) -> None:
        self.assertTrue(self.contract.case_record_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.candidate_comparison_present)
        self.assertFalse(self.contract.memory_capability_claim_present)
        self.assertFalse(self.contract.ai_system_claim_present)
        self.assertFalse(self.contract.runtime_integration_present)

    def test_executes_nothing_and_authorizes_only_matrix_gate(self) -> None:
        self.assertEqual(
            (0, 0),
            (
                self.contract.new_replicas_executed,
                self.contract.new_interval_calls_executed,
            ),
        )
        self.assertTrue(self.contract.matrix_gate_authorized_next_stage)
        self.assertEqual(S1_MF_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1mf_b4_pih_case_output_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1MFB4PIHCaseOutputContractError):
            replace(self.contract, memory_capability_claim_present=True)
        with self.assertRaises(DTS1S1MFB4PIHCaseOutputContractError):
            replace(self.contract, all_refinement_residuals_zero=True)
        source = inspect.getsource(build_dts1_s1mf_b4_pih_case_output_contract)
        for forbidden in ("run_dts1_one_replica", "run_dts1_b4_pih_three_refinement", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
