from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1lj_b3_pie_case_selection_contract import (
    DTS1S1LJB3PIECaseSelectionContractError,
    S1_LJ_DECISION,
    build_dts1_s1lj_b3_pie_case_selection_contract,
)


class DTS1S1LJB3PIECaseSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1lj_b3_pie_case_selection_contract()

    def test_binds_exact_s1li_source_and_registered_c09(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1li_digest))
        self.assertEqual(("C09", "B3", "B3_F3_LOCAL_LEAKY", "P_IE_CAUSAL_TWO_SUBSTEP", 2, 8), self.contract.target_case_record[:6])

    def test_selects_exact_three_pie_refinements(self) -> None:
        self.assertEqual((2, 4, 8), tuple(row[4] for row in self.contract.target_replica_records))
        self.assertEqual(self.contract.target_replica_ids, tuple(row[0] for row in self.contract.target_replica_records))

    def test_binds_complete_b3_fresh_state_and_local_leaky_arm(self) -> None:
        fresh = self.contract.corrected_fresh_state_record
        self.assertEqual(("B3", "TWO_NODE_OPEN_LINE", ("node-a", "node-b")), fresh[:3])
        substrate = dict(dict(fresh[5])["substrate"])
        self.assertEqual((("node-a", 0.5), ("node-b", 0.5)), substrate["masses"])
        self.assertEqual("mcm.s1jt.b3.local-leaky", dict(substrate["arm"])["arm_id"])
        self.assertEqual(self.contract.fresh_field_digest, fresh[6])
        self.assertEqual(self.contract.fresh_private_state_digest, fresh[8])

    def test_binds_embedded_m_state_and_sequence_local_carry(self) -> None:
        private = dict(self.contract.corrected_fresh_state_record[7])
        self.assertEqual(self.contract.embedded_m_state_digest, private["embedded_M_state_digest"])
        joined = " ".join(self.contract.fresh_start_rules)
        self.assertIn("uniform-M-and-the-bound-local-leaky-arm", joined)
        self.assertIn("carry-only-between-the-two-ordered-intervals", joined)

    def test_binds_dual_digest_roles_and_b3_residual_rule(self) -> None:
        self.assertEqual("output_digest", dict(self.contract.complete_provenance_digest_role)["name"])
        self.assertEqual("refinement_comparison_digest", dict(self.contract.comparison_digest_role)["name"])
        rules = " ".join(self.contract.output_acceptance_rules)
        self.assertIn("must-not-be-forced-bit-identical", rules)
        self.assertIn("r2-minus-r4-and-r4-minus-r8-residuals", rules)

    def test_binds_twelve_call_budget_without_retry(self) -> None:
        self.assertEqual((3, 2, 2, 4, 12), (self.contract.target_replica_count, self.contract.sequences_per_target_replica, self.contract.intervals_per_sequence, self.contract.intervals_per_target_replica, self.contract.maximum_new_interval_calls))
        self.assertEqual(0, dict(self.contract.execution_budget)["retry_or_repeat_calls"])

    def test_requires_three_atomic_outputs_before_later_composition(self) -> None:
        self.assertIn("all-three-replicas-must-pass", " ".join(self.contract.output_acceptance_rules))
        self.assertFalse(self.contract.case_output_composed)

    def test_selects_without_implementation_execution_or_judgment(self) -> None:
        self.assertTrue(self.contract.case_selected)
        self.assertFalse(self.contract.runner_extension_implemented)
        self.assertEqual((0, 0), (self.contract.target_replicas_executed, self.contract.interval_calls_executed))
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.runtime_integration_present)
        self.assertTrue(self.contract.exact_implementation_execution_authorized_next_stage)
        self.assertEqual(S1_LJ_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1lj_b3_pie_case_selection_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1LJB3PIECaseSelectionContractError):
            replace(self.contract, maximum_new_interval_calls=13)
        source = inspect.getsource(build_dts1_s1lj_b3_pie_case_selection_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
