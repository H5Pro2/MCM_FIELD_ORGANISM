from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1kj_b2_pie_case_selection_contract import (
    DTS1S1KJB2PIECaseSelectionContractError,
    S1_KJ_DECISION,
    build_dts1_s1kj_b2_pie_case_selection_contract,
)


class DTS1S1KJB2PIECaseSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1kj_b2_pie_case_selection_contract()

    def test_binds_exact_s1ki_source_and_registered_c05(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1ki_digest))
        self.assertEqual(("C05", "B2", "B2_S2_LINEAR_INTEGRATOR"), self.contract.target_case_record[:3])

    def test_selects_exact_three_pie_refinements(self) -> None:
        self.assertEqual((2, 4, 8), tuple(row[4] for row in self.contract.target_replica_records))
        self.assertEqual(self.contract.target_replica_ids, tuple(row[0] for row in self.contract.target_replica_records))

    def test_binds_corrected_complete_b2_fresh_state(self) -> None:
        fresh = self.contract.corrected_fresh_state_record
        self.assertEqual(("B2", "TWO_NODE_OPEN_LINE", ("node-a", "node-b")), fresh[:3])
        private = dict(fresh[7])
        entries = private["complete_L_state_payload"]["entries"]
        self.assertEqual((0.0, 0.0), tuple(row["value"] for row in entries))
        self.assertEqual(self.contract.fresh_field_digest, fresh[6])
        self.assertEqual(self.contract.fresh_private_state_digest, fresh[8])

    def test_binds_separate_fresh_starts_and_sequence_local_carry(self) -> None:
        joined = " ".join(self.contract.fresh_start_rules)
        self.assertIn("each-start-from-an-independent", joined)
        self.assertIn("carries-only-between-the-two-ordered-intervals-of-one-sequence", joined)

    def test_binds_dual_digest_roles_and_v2_output(self) -> None:
        self.assertEqual("output_digest", dict(self.contract.complete_provenance_digest_role)["name"])
        self.assertEqual("refinement_comparison_digest", dict(self.contract.comparison_digest_role)["name"])
        self.assertEqual("mcm.s1jz.complete-replica-output.v2", dict(self.contract.corrected_output_schema)["schema_id"])

    def test_binds_twelve_call_budget_without_retry(self) -> None:
        self.assertEqual(3, self.contract.target_replica_count)
        self.assertEqual(4, self.contract.intervals_per_target_replica)
        self.assertEqual(12, self.contract.maximum_new_interval_calls)
        self.assertEqual(0, dict(self.contract.execution_budget)["retry_or_repeat_calls"])

    def test_requires_three_atomic_outputs_before_later_composition(self) -> None:
        rules = " ".join(self.contract.output_acceptance_rules)
        self.assertIn("bit-identical-across-r2-r4-r8", rules)
        self.assertIn("all-three-replicas-must-pass", rules)
        self.assertFalse(self.contract.case_output_composed)

    def test_selects_without_implementation_execution_or_judgment(self) -> None:
        self.assertTrue(self.contract.case_selected)
        self.assertFalse(self.contract.runner_extension_implemented)
        self.assertEqual((0, 0), (self.contract.target_replicas_executed, self.contract.interval_calls_executed))
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.runtime_integration_present)
        self.assertTrue(self.contract.exact_implementation_execution_authorized_next_stage)
        self.assertEqual(S1_KJ_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1kj_b2_pie_case_selection_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1KJB2PIECaseSelectionContractError):
            replace(self.contract, maximum_new_interval_calls=13)
        source = inspect.getsource(build_dts1_s1kj_b2_pie_case_selection_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
