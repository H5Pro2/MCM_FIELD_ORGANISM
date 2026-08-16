from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1kt_b2_pih_case_selection_contract import (
    DTS1S1KTB2PIHCaseSelectionContractError,
    S1_KT_DECISION,
    build_dts1_s1kt_b2_pih_case_selection_contract,
)


class DTS1S1KTB2PIHCaseSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1kt_b2_pih_case_selection_contract()

    def test_binds_exact_s1ks_source_and_registered_c06(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1ks_digest))
        self.assertEqual(("C06", "B2", "B2_S2_LINEAR_INTEGRATOR"), self.contract.target_case_record[:3])

    def test_selects_exact_three_pih_refinements(self) -> None:
        self.assertEqual((2, 4, 8), tuple(row[4] for row in self.contract.target_replica_records))
        self.assertEqual(self.contract.target_replica_ids, tuple(row[0] for row in self.contract.target_replica_records))

    def test_binds_one_three_interval_sequence_and_eight_components(self) -> None:
        self.assertEqual("P_IH_A_A_A", self.contract.sequence_record[0])
        self.assertEqual((3, 3, 8), (self.contract.intervals_per_target_replica, self.contract.checkpoints_per_target_replica, self.contract.signed_components_per_target_replica))

    def test_binds_corrected_complete_b2_fresh_state(self) -> None:
        fresh = self.contract.corrected_fresh_state_record
        self.assertEqual(("B2", "TWO_NODE_OPEN_LINE", ("node-a", "node-b")), fresh[:3])
        entries = dict(fresh[7])["complete_L_state_payload"]["entries"]
        self.assertEqual((0.0, 0.0), tuple(row["value"] for row in entries))
        self.assertEqual((self.contract.fresh_field_digest, self.contract.fresh_private_state_digest), (fresh[6], fresh[8]))

    def test_binds_refinement_fresh_starts_and_complete_l_carry(self) -> None:
        joined = " ".join(self.contract.fresh_start_and_carry_rules)
        self.assertIn("each-start-from-an-independent", joined)
        self.assertIn("complete-L-private-state-carry-across-all-three", joined)

    def test_binds_dual_digest_roles_and_checkpoint_identity(self) -> None:
        self.assertEqual("output_digest", dict(self.contract.complete_provenance_digest_role)["name"])
        self.assertEqual("refinement_comparison_digest", dict(self.contract.comparison_digest_role)["name"])
        self.assertIn("checkpoint-replica_id-bit-equals", " ".join(self.contract.output_acceptance_rules))

    def test_binds_nine_call_budget_without_retry(self) -> None:
        self.assertEqual((3, 3, 9), (self.contract.target_replica_count, self.contract.intervals_per_target_replica, self.contract.maximum_new_interval_calls))
        self.assertEqual(0, dict(self.contract.execution_budget)["retry_or_repeat_calls"])

    def test_selects_without_implementation_execution_or_judgment(self) -> None:
        self.assertTrue(self.contract.case_selected)
        self.assertFalse(self.contract.runner_extension_implemented)
        self.assertEqual((0, 0), (self.contract.target_replicas_executed, self.contract.interval_calls_executed))
        self.assertFalse(self.contract.case_output_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertTrue(self.contract.exact_implementation_execution_authorized_next_stage)
        self.assertEqual(S1_KT_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1kt_b2_pih_case_selection_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1KTB2PIHCaseSelectionContractError):
            replace(self.contract, maximum_new_interval_calls=10)
        source = inspect.getsource(build_dts1_s1kt_b2_pih_case_selection_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
