from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1lq_matrix_completeness_gate import (
    DTS1S1LQMatrixCompletenessGateError,
    S1_LQ_DECISION,
    build_dts1_s1lq_matrix_completeness_gate,
)


class DTS1S1LQMatrixCompletenessGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1lq_matrix_completeness_gate()

    def test_binds_completed_and_missing_case_counts(self) -> None:
        self.assertEqual(tuple(f"C{index:02d}" for index in range(1, 25)), self.contract.registered_case_ids)
        self.assertEqual(tuple(f"C{index:02d}" for index in range(1, 11)), self.contract.completed_case_ids)
        self.assertEqual(tuple(f"C{index:02d}" for index in range(11, 25)), self.contract.missing_case_ids)
        self.assertEqual((10, 14), (self.contract.completed_case_count, self.contract.missing_case_count))

    def test_binds_digests_for_completed_and_refinements(self) -> None:
        self.assertEqual((10, 10), (len(self.contract.completed_case_contract_digests), len(self.contract.completed_case_output_digests)))
        self.assertEqual((3, 72, 30, 42), (self.contract.refinements_per_case, self.contract.required_refinement_output_count, self.contract.completed_refinement_output_count, self.contract.missing_refinement_output_count))

    def test_blocks_matrix_composition_and_restricts_next_case(self) -> None:
        self.assertFalse(self.contract.matrix_complete)
        self.assertFalse(self.contract.matrix_composition_authorized)
        self.assertFalse(self.contract.matrix_output_published)
        self.assertFalse(self.contract.judgment_present)
        self.assertFalse(self.contract.runtime_integration_present)
        self.assertTrue(self.contract.prior_matrix_authorization_superseded)
        self.assertTrue(self.contract.c11_selection_authorized_next_stage)
        self.assertEqual(("C11", "B3", "B3_F3_LOCAL_LEAKY", "P_IK_INTERFERENCE", 3, 6), self.contract.next_case_record[:6])

    def test_stays_static_and_deterministic(self) -> None:
        self.assertEqual((0, 0), (self.contract.new_replicas_executed, self.contract.new_interval_calls_executed))
        self.assertEqual(S1_LQ_DECISION, self.contract.decision)
        second = build_dts1_s1lq_matrix_completeness_gate()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)

    def test_tamper_closed_and_no_runtime_invocation(self) -> None:
        with self.assertRaises(DTS1S1LQMatrixCompletenessGateError):
            replace(self.contract, matrix_complete=True)
        source = inspect.getsource(build_dts1_s1lq_matrix_completeness_gate)
        for forbidden in ("build_dts1_one_replica_orchestrator", "run_dts1", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
