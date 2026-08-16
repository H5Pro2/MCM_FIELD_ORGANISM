from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1mh_b4_pik_case_selection_contract import (
    DTS1S1MHB4PIKCaseSelectionContractError,
    S1_MH_DECISION,
    S1_MH_SEQUENCE_KEYS,
    build_dts1_s1mh_b4_pik_case_selection_contract,
)


class DTS1S1MHB4PIKCaseSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1mh_b4_pik_case_selection_contract()

    def test_binds_exact_s1mg_source_and_registered_c15(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1mg_digest))
        self.assertEqual(
            (
                "C15",
                "B4",
                "B4_F3_LINEAR_COUPLED",
                "P_IK_INTERFERENCE",
                3,
                6,
            ),
            self.contract.target_case_record[:6],
        )
        self.assertEqual(
            self.contract.target_replica_ids,
            tuple(row[0] for row in self.contract.target_replica_records),
        )

    def test_selects_exact_three_pik_refinements(self) -> None:
        self.assertEqual(3, self.contract.target_replica_count)
        self.assertEqual(3, len(self.contract.target_replica_records))
        self.assertEqual(
            (
                ("B4:P_IK_INTERFERENCE:r2", 2),
                ("B4:P_IK_INTERFERENCE:r4", 4),
                ("B4:P_IK_INTERFERENCE:r8", 8),
            ),
            tuple((row[0], row[4]) for row in self.contract.target_replica_records),
        )

    def test_binds_two_sequences_and_twenty_four_call_budget(self) -> None:
        self.assertEqual(
            S1_MH_SEQUENCE_KEYS,
            tuple(row[0] for row in self.contract.sequence_records),
        )
        self.assertEqual(
            ("P_IK_INTERFERENCE", "P_IK_INTERFERENCE"),
            tuple(row[1] for row in self.contract.sequence_records),
        )
        self.assertEqual((4, 4), tuple(row[3] for row in self.contract.sequence_records))
        self.assertEqual(
            (3, 2, 4, 8, 24),
            (
                self.contract.target_replica_count,
                self.contract.sequences_per_target_replica,
                self.contract.intervals_per_sequence,
                self.contract.intervals_per_target_replica,
                self.contract.maximum_new_interval_calls,
            ),
        )
        self.assertEqual(
            (2, 6, 8),
            (
                self.contract.checkpoints_per_target_replica,
                self.contract.signed_components_per_target_replica,
                self.contract.diagnostics_per_target_replica,
            ),
        )

    def test_binds_complete_b4_three_node_fresh_state_and_linear_arm(self) -> None:
        fresh = self.contract.corrected_fresh_state_record
        self.assertEqual(
            ("B4", "THREE_NODE_OPEN_LINE", ("node-a", "node-b", "node-c")),
            fresh[:3],
        )
        substrate = dict(dict(fresh[5])["substrate"])
        arm = dict(substrate["arm"])
        self.assertEqual(
            (
                ("node-a", 0.3333333333333333),
                ("node-b", 0.3333333333333333),
                ("node-c", 0.3333333333333333),
            ),
            substrate["masses"],
        )
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
        joined = " ".join(self.contract.fresh_start_and_carry_rules)
        self.assertIn("P_IK_A_B_A-and-P_IK_A_GAP_A", joined)
        self.assertIn("four-ordered-intervals", joined)

    def test_selects_without_implementation_execution_or_claims(self) -> None:
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
        self.assertFalse(self.contract.candidate_comparison_present)
        self.assertFalse(self.contract.memory_capability_claim_present)
        self.assertFalse(self.contract.ai_system_claim_present)
        self.assertFalse(self.contract.runtime_integration_present)
        self.assertTrue(self.contract.exact_implementation_execution_authorized_next_stage)
        self.assertEqual(S1_MH_DECISION, self.contract.decision)

    def test_tamper_closed_and_no_runtime_code_paths(self) -> None:
        second = build_dts1_s1mh_b4_pik_case_selection_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1MHB4PIKCaseSelectionContractError):
            replace(self.contract, interval_calls_executed=1)
        with self.assertRaises(DTS1S1MHB4PIKCaseSelectionContractError):
            replace(self.contract, memory_capability_claim_present=True)
        source = inspect.getsource(build_dts1_s1mh_b4_pik_case_selection_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
