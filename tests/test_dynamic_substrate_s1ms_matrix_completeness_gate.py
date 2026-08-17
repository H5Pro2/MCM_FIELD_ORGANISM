from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ms_matrix_completeness_gate import (
    DTS1S1MSMatrixCompletenessGateError,
    S1_MS_DECISION,
    build_dts1_s1ms_matrix_completeness_gate,
)


class DTS1S1MSMatrixCompletenessGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1ms_matrix_completeness_gate()

    def test_binds_completed_and_missing_case_counts(self) -> None:
        self.assertEqual(
            tuple(f"C{index:02d}" for index in range(1, 25)),
            self.contract.registered_case_ids,
        )
        self.assertEqual(
            tuple(f"C{index:02d}" for index in range(1, 18)),
            self.contract.completed_case_ids,
        )
        self.assertEqual(
            tuple(f"C{index:02d}" for index in range(18, 25)),
            self.contract.missing_case_ids,
        )
        self.assertEqual(
            (17, 7),
            (self.contract.completed_case_count, self.contract.missing_case_count),
        )

    def test_binds_digests_for_completed_cases_and_refinements(self) -> None:
        self.assertEqual(
            (17, 17),
            (
                len(self.contract.completed_case_contract_digests),
                len(self.contract.completed_case_output_digests),
            ),
        )
        self.assertEqual(
            (3, 72, 51, 21),
            (
                self.contract.refinements_per_case,
                self.contract.required_refinement_output_count,
                self.contract.completed_refinement_output_count,
                self.contract.missing_refinement_output_count,
            ),
        )
        self.assertEqual(17, len(set(self.contract.completed_case_contract_digests)))
        self.assertEqual(17, len(set(self.contract.completed_case_output_digests)))

    def test_blocks_matrix_composition_and_restricts_next_case(self) -> None:
        self.assertFalse(self.contract.matrix_complete)
        self.assertFalse(self.contract.matrix_composition_authorized)
        self.assertFalse(self.contract.matrix_output_published)
        self.assertFalse(self.contract.judgment_present)
        self.assertFalse(self.contract.runtime_integration_present)
        self.assertTrue(self.contract.prior_matrix_authorization_superseded)
        self.assertTrue(self.contract.c18_selection_authorized_next_stage)
        self.assertEqual(
            (
                "C18",
                "B5",
                "B5_F3_FULL",
                "P_IH_ATTENUATION",
                2,
                8,
            ),
            self.contract.next_case_record[:6],
        )

    def test_keeps_memory_and_ai_as_blocked_claims(self) -> None:
        self.assertFalse(self.contract.memory_capability_claim_present)
        self.assertFalse(self.contract.ai_system_claim_present)
        rules = " ".join(self.contract.correction_rules)
        self.assertIn("development-direction-not-a-demonstrated-capability", rules)

    def test_stays_static_and_deterministic(self) -> None:
        self.assertEqual(
            (0, 0),
            (
                self.contract.new_replicas_executed,
                self.contract.new_interval_calls_executed,
            ),
        )
        self.assertEqual(S1_MS_DECISION, self.contract.decision)
        second = build_dts1_s1ms_matrix_completeness_gate()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)

    def test_tamper_closed_and_no_runtime_invocation(self) -> None:
        with self.assertRaises(DTS1S1MSMatrixCompletenessGateError):
            replace(self.contract, memory_capability_claim_present=True)
        with self.assertRaises(DTS1S1MSMatrixCompletenessGateError):
            replace(self.contract, matrix_composition_authorized=True)
        source = inspect.getsource(build_dts1_s1ms_matrix_completeness_gate)
        for forbidden in ("run_dts1", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
