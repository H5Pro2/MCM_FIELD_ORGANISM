from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1md_b4_pih_case_selection_contract import (
    DTS1S1MDB4PIHCaseSelectionContractError,
    S1_MD_DECISION,
    build_dts1_s1md_b4_pih_case_selection_contract,
)


class DTS1S1MDB4PIHCaseSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1md_b4_pih_case_selection_contract()

    def test_binds_exact_s1mc_source_and_registered_c14(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1mc_digest))
        self.assertEqual(
            (
                "C14",
                "B4",
                "B4_F3_LINEAR_COUPLED",
                "P_IH_ATTENUATION",
                2,
                8,
            ),
            self.contract.target_case_record[:6],
        )

    def test_selects_exact_three_pih_refinements(self) -> None:
        self.assertEqual(
            (2, 4, 8),
            tuple(row[4] for row in self.contract.target_replica_records),
        )
        self.assertEqual(
            self.contract.target_replica_ids,
            tuple(row[0] for row in self.contract.target_replica_records),
        )
        self.assertEqual(("P_IH_A_A_A",), self.contract.target_replica_records[0][5])

    def test_binds_pih_sequence_and_nine_call_budget(self) -> None:
        self.assertEqual("P_IH_A_A_A", self.contract.sequence_record[0])
        self.assertEqual((1, 2, 3), self.contract.sequence_record[5])
        self.assertEqual(
            (3, 1, 3, 3, 9),
            (
                self.contract.target_replica_count,
                self.contract.sequences_per_target_replica,
                self.contract.intervals_per_sequence,
                self.contract.intervals_per_target_replica,
                self.contract.maximum_new_interval_calls,
            ),
        )
        self.assertEqual(0, dict(self.contract.execution_budget)["retry_or_repeat_calls"])

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
        joined = " ".join(self.contract.fresh_start_and_carry_rules)
        self.assertIn("P_IH_A_A_A-starts-once", joined)
        self.assertIn("three-ordered-intervals", joined)

    def test_binds_dual_digest_roles_without_claims(self) -> None:
        self.assertEqual(
            "output_digest",
            dict(self.contract.complete_provenance_digest_role)["name"],
        )
        self.assertEqual(
            "refinement_comparison_digest",
            dict(self.contract.comparison_digest_role)["name"],
        )
        self.assertFalse(self.contract.memory_capability_claim_present)
        self.assertFalse(self.contract.ai_system_claim_present)

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
        self.assertFalse(self.contract.candidate_comparison_present)
        self.assertFalse(self.contract.runtime_integration_present)
        self.assertTrue(self.contract.exact_implementation_execution_authorized_next_stage)
        self.assertEqual(S1_MD_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1md_b4_pih_case_selection_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1MDB4PIHCaseSelectionContractError):
            replace(self.contract, memory_capability_claim_present=True)
        with self.assertRaises(DTS1S1MDB4PIHCaseSelectionContractError):
            replace(self.contract, maximum_new_interval_calls=10)
        source = inspect.getsource(build_dts1_s1md_b4_pih_case_selection_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
