from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1kq_b1_pih_case_selection_contract import (
    DTS1S1KQB1PIHCaseSelectionContractError,
    S1_KQ_DECISION,
    build_dts1_s1kq_b1_pih_case_selection_contract,
)


class DTS1S1KQB1PIHCaseSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1kq_b1_pih_case_selection_contract()

    def test_binds_exact_s1kp_source_and_registered_c02(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1kp_digest))
        self.assertEqual(("C02", "B1", "B1_FIXED_PRERELEASE_ADAPTER"), self.contract.target_case_record[:3])

    def test_selects_exact_three_pih_refinements(self) -> None:
        self.assertEqual((2, 4, 8), tuple(row[4] for row in self.contract.target_replica_records))
        self.assertEqual(self.contract.target_replica_ids, tuple(row[0] for row in self.contract.target_replica_records))

    def test_binds_one_three_interval_sequence_and_eight_components(self) -> None:
        self.assertEqual("P_IH_A_A_A", self.contract.sequence_record[0])
        self.assertEqual(3, self.contract.intervals_per_target_replica)
        self.assertEqual(3, self.contract.checkpoints_per_target_replica)
        self.assertEqual(8, self.contract.signed_components_per_target_replica)

    def test_binds_corrected_complete_b1_fresh_state(self) -> None:
        fresh = self.contract.corrected_fresh_state_record
        self.assertEqual(("B1", "TWO_NODE_OPEN_LINE", ("node-a", "node-b")), fresh[:3])
        self.assertEqual(self.contract.fresh_field_digest, fresh[6])
        self.assertEqual(self.contract.fresh_private_state_digest, fresh[8])

    def test_binds_refinement_fresh_starts_and_three_interval_carry(self) -> None:
        joined = " ".join(self.contract.fresh_start_and_carry_rules)
        self.assertIn("each-start-from-an-independent", joined)
        self.assertIn("carry-across-all-three-ordered-A-intervals", joined)

    def test_binds_dual_digest_roles_and_checkpoint_identity(self) -> None:
        self.assertEqual("output_digest", dict(self.contract.complete_provenance_digest_role)["name"])
        self.assertEqual("refinement_comparison_digest", dict(self.contract.comparison_digest_role)["name"])
        self.assertIn("checkpoint-replica_id-bit-equals", " ".join(self.contract.output_acceptance_rules))

    def test_binds_nine_call_budget_without_retry(self) -> None:
        self.assertEqual((3, 3, 9), (
            self.contract.target_replica_count,
            self.contract.intervals_per_target_replica,
            self.contract.maximum_new_interval_calls,
        ))
        self.assertEqual(0, dict(self.contract.execution_budget)["retry_or_repeat_calls"])

    def test_selects_without_implementation_execution_or_judgment(self) -> None:
        self.assertTrue(self.contract.case_selected)
        self.assertFalse(self.contract.runner_extension_implemented)
        self.assertEqual((0, 0), (self.contract.target_replicas_executed, self.contract.interval_calls_executed))
        self.assertFalse(self.contract.case_output_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertTrue(self.contract.exact_implementation_execution_authorized_next_stage)
        self.assertEqual(S1_KQ_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1kq_b1_pih_case_selection_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1KQB1PIHCaseSelectionContractError):
            replace(self.contract, maximum_new_interval_calls=10)
        source = inspect.getsource(build_dts1_s1kq_b1_pih_case_selection_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
