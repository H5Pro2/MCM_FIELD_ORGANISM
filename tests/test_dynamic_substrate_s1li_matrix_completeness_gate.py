from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1li_matrix_completeness_gate import (
    DTS1S1LIMatrixCompletenessGateError,
    S1_LI_DECISION,
    build_dts1_s1li_matrix_completeness_gate,
)


class DTS1S1LIMatrixCompletenessGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1li_matrix_completeness_gate()

    def test_binds_all_twenty_four_registered_case_ids(self) -> None:
        self.assertEqual(tuple(f"C{index:02d}" for index in range(1, 25)), self.contract.registered_case_ids)
        self.assertEqual(24, self.contract.registered_case_count)

    def test_binds_eight_completed_and_sixteen_missing_cases(self) -> None:
        self.assertEqual(tuple(f"C{index:02d}" for index in range(1, 9)), self.contract.completed_case_ids)
        self.assertEqual(tuple(f"C{index:02d}" for index in range(9, 25)), self.contract.missing_case_ids)
        self.assertEqual((8, 16), (self.contract.completed_case_count, self.contract.missing_case_count))

    def test_distinguishes_cases_from_refinement_outputs(self) -> None:
        self.assertEqual((3, 72, 24, 48), (self.contract.refinements_per_case, self.contract.required_refinement_output_count, self.contract.completed_refinement_output_count, self.contract.missing_refinement_output_count))

    def test_binds_eight_distinct_contract_and_output_digests(self) -> None:
        self.assertEqual((8, 8), (len(set(self.contract.completed_case_contract_digests)), len(set(self.contract.completed_case_output_digests))))
        self.assertTrue(all(len(value) == 64 for value in self.contract.completed_case_contract_digests + self.contract.completed_case_output_digests))

    def test_blocks_incomplete_matrix_and_supersedes_prior_authorization(self) -> None:
        self.assertFalse(self.contract.matrix_complete)
        self.assertFalse(self.contract.matrix_composition_authorized)
        self.assertFalse(self.contract.matrix_output_published)
        self.assertTrue(self.contract.prior_matrix_authorization_superseded)

    def test_binds_only_c09_b3_pie_as_next_case(self) -> None:
        self.assertEqual(("C09", "B3", "B3_F3_LOCAL_LEAKY", "P_IE_CAUSAL_TWO_SUBSTEP", 2, 8), self.contract.next_case_record[:6])
        self.assertTrue(self.contract.c09_selection_authorized_next_stage)

    def test_executes_nothing_and_makes_no_judgment(self) -> None:
        self.assertEqual((0, 0), (self.contract.new_replicas_executed, self.contract.new_interval_calls_executed))
        self.assertFalse(self.contract.judgment_present)
        self.assertFalse(self.contract.runtime_integration_present)

    def test_decision_is_exact(self) -> None:
        self.assertEqual(S1_LI_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1li_matrix_completeness_gate()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1LIMatrixCompletenessGateError):
            replace(self.contract, matrix_composition_authorized=True)
        source = inspect.getsource(build_dts1_s1li_matrix_completeness_gate)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
