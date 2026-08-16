from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1mk_matrix_completeness_gate import (
    build_dts1_s1mk_matrix_completeness_gate,
)
from mcm_field_organism.dynamic_substrate_s1ml_b4_pin_case_selection_contract import (
    DTS1S1MLB4PINCaseSelectionContractError,
    S1_ML_DECISION,
    S1_ML_SEQUENCE_KEYS,
    S1_ML_SOURCE_S1MK_DIGEST,
    build_dts1_s1ml_b4_pin_case_selection_contract,
)


class DTS1S1MLB4PINCaseSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1ml_b4_pin_case_selection_contract()

    def test_binds_exact_s1mk_source_and_registered_c16(self) -> None:
        source = build_dts1_s1mk_matrix_completeness_gate()
        self.assertEqual(S1_ML_SOURCE_S1MK_DIGEST, source.contract_digest)
        self.assertEqual(64, len(self.contract.source_s1mk_digest))
        self.assertEqual(
            ("C16", "B4", "B4_F3_LINEAR_COUPLED", "P_IN_RELEASE_REUSE", 3, 6),
            self.contract.target_case_record[:6],
        )
        self.assertEqual(source.next_case_record, self.contract.target_case_record)

    def test_selects_exact_three_pin_refinements(self) -> None:
        self.assertEqual(3, self.contract.target_replica_count)
        self.assertEqual(3, len(self.contract.target_replica_records))
        self.assertEqual(
            (
                ("B4:P_IN_RELEASE_REUSE:r2", 2),
                ("B4:P_IN_RELEASE_REUSE:r4", 4),
                ("B4:P_IN_RELEASE_REUSE:r8", 8),
            ),
            tuple((row[0], row[4]) for row in self.contract.target_replica_records),
        )

    def test_binds_two_recovery_sequences_and_twenty_four_call_budget(self) -> None:
        self.assertEqual(
            S1_ML_SEQUENCE_KEYS,
            tuple(row[0] for row in self.contract.sequence_records),
        )
        self.assertEqual(
            ("P_IN_RELEASE_REUSE", "P_IN_RELEASE_REUSE"),
            tuple(row[1] for row in self.contract.sequence_records),
        )
        self.assertEqual((4, 4), tuple(row[3] for row in self.contract.sequence_records))
        self.assertEqual(((4,), (4,)), tuple(row[5] for row in self.contract.sequence_records))
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

    def test_binds_no_execution_static_boundaries_or_claims(self) -> None:
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
        self.assertFalse(self.contract.release_reuse_judgment_present)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.candidate_comparison_present)
        self.assertFalse(self.contract.memory_capability_claim_present)
        self.assertFalse(self.contract.ai_system_claim_present)
        self.assertFalse(self.contract.runtime_integration_present)
        self.assertTrue(self.contract.exact_implementation_execution_authorized_next_stage)
        self.assertEqual(S1_ML_DECISION, self.contract.decision)

    def test_tamper_closed_and_no_runtime_code_paths(self) -> None:
        second = build_dts1_s1ml_b4_pin_case_selection_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1MLB4PINCaseSelectionContractError):
            replace(self.contract, interval_calls_executed=1)
        with self.assertRaises(DTS1S1MLB4PINCaseSelectionContractError):
            replace(self.contract, memory_capability_claim_present=True)
        source = inspect.getsource(build_dts1_s1ml_b4_pin_case_selection_contract)
        for forbidden in ("run_dts1", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
