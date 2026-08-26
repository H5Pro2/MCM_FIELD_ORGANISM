from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1lz_b4_pie_case_selection_contract import (
    DTS1S1LZB4PIECaseSelectionContractError,
    S1_LZ_DECISION,
    build_dts1_s1lz_b4_pie_case_selection_contract,
)


class DTS1S1LZB4PIECaseSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1lz_b4_pie_case_selection_contract()

    def test_binds_exact_s1ly_source_and_registered_c13(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1ly_digest))
        self.assertEqual(
            (
                "C13",
                "B4",
                "B4_F3_LINEAR_COUPLED",
                "P_IE_CAUSAL_TWO_SUBSTEP",
                2,
                8,
            ),
            self.contract.target_case_record[:6],
        )

    def test_selects_exact_three_pie_refinements(self) -> None:
        self.assertEqual((2, 4, 8), tuple(row[4] for row in self.contract.target_replica_records))
        self.assertEqual(
            self.contract.target_replica_ids,
            tuple(row[0] for row in self.contract.target_replica_records),
        )
        self.assertEqual(
            ("P_IE_F_HIGH", "P_IE_R_HIGH"),
            self.contract.target_replica_records[0][5],
        )

    def test_binds_complete_b4_fresh_state_and_linear_coupled_arm(self) -> None:
        fresh = self.contract.corrected_fresh_state_record
        self.assertEqual(("B4", "TWO_NODE_OPEN_LINE", ("node-a", "node-b")), fresh[:3])
        substrate = dict(dict(fresh[5])["substrate"])
        arm = dict(substrate["arm"])
        self.assertEqual((("node-a", 0.5), ("node-b", 0.5)), substrate["masses"])
        self.assertEqual("mcm.s1jt.b4.linear-coupled", arm["arm_id"])
        self.assertEqual((1.0, 0.5, 1.0), (arm["lambda_sm_per_second"], arm["kappa"], arm["eta"]))
        self.assertEqual(self.contract.fresh_field_digest, fresh[6])
        self.assertEqual(self.contract.fresh_private_state_digest, fresh[8])

    def test_binds_embedded_m_state_and_b4_configuration(self) -> None:
        private = dict(self.contract.corrected_fresh_state_record[7])
        self.assertEqual(
            self.contract.embedded_m_state_digest,
            private["embedded_M_state_digest"],
        )
        self.assertEqual(
            self.contract.b4_configuration_digest,
            private["B4_configuration_digest"],
        )
        joined = " ".join(self.contract.fresh_start_rules)
        self.assertIn("uniform-M-and-the-bound-linear-coupled-arm", joined)
        self.assertIn("carry-only-between-the-two-ordered-intervals", joined)

    def test_binds_dual_digest_roles_and_b4_residual_rule(self) -> None:
        self.assertEqual(
            "output_digest",
            dict(self.contract.complete_provenance_digest_role)["name"],
        )
        self.assertEqual(
            "refinement_comparison_digest",
            dict(self.contract.comparison_digest_role)["name"],
        )
        rules = " ".join(self.contract.output_acceptance_rules)
        self.assertIn("must-not-be-forced-bit-identical", rules)
        self.assertIn("r2-minus-r4-and-r4-minus-r8-residuals", rules)

    def test_binds_twelve_call_budget_without_retry(self) -> None:
        self.assertEqual(
            (3, 2, 2, 4, 12),
            (
                self.contract.target_replica_count,
                self.contract.sequences_per_target_replica,
                self.contract.intervals_per_sequence,
                self.contract.intervals_per_target_replica,
                self.contract.maximum_new_interval_calls,
            ),
        )
        self.assertEqual(0, dict(self.contract.execution_budget)["retry_or_repeat_calls"])

    def test_selects_without_implementation_execution_or_judgment(self) -> None:
        self.assertTrue(self.contract.case_selected)
        self.assertFalse(self.contract.runner_extension_implemented)
        self.assertEqual(
            (0, 0),
            (
                self.contract.target_replicas_executed,
                self.contract.interval_calls_executed,
            ),
        )
        self.assertFalse(self.contract.case_output_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.runtime_integration_present)
        self.assertTrue(self.contract.exact_implementation_execution_authorized_next_stage)
        self.assertEqual(S1_LZ_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1lz_b4_pie_case_selection_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1LZB4PIECaseSelectionContractError):
            replace(self.contract, maximum_new_interval_calls=13)
        source = inspect.getsource(build_dts1_s1lz_b4_pie_case_selection_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
