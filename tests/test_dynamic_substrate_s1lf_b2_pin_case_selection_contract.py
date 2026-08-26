from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1lf_b2_pin_case_selection_contract import (
    DTS1S1LFB2PINCaseSelectionContractError,
    S1_LF_DECISION,
    build_dts1_s1lf_b2_pin_case_selection_contract,
)


class DTS1S1LFB2PINCaseSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1lf_b2_pin_case_selection_contract()

    def test_binds_exact_s1le_source_and_registered_c08(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1le_digest))
        self.assertEqual(("C08", "B2", "B2_S2_LINEAR_INTEGRATOR", "P_IN_RELEASE_REUSE", 3, 6), self.contract.target_case_record[:6])

    def test_selects_exact_three_pin_refinements(self) -> None:
        self.assertEqual((2, 4, 8), tuple(row[4] for row in self.contract.target_replica_records))
        self.assertEqual(self.contract.target_replica_ids, tuple(row[0] for row in self.contract.target_replica_records))

    def test_binds_two_four_interval_sequences_and_terminal_checkpoints(self) -> None:
        self.assertEqual(("P_IN_RECOVERY_ON", "P_IN_RECOVERY_OFF"), tuple(row[0] for row in self.contract.sequence_records))
        self.assertEqual((2, 4, 8, 2), (self.contract.sequences_per_target_replica, self.contract.intervals_per_sequence, self.contract.intervals_per_target_replica, self.contract.checkpoints_per_target_replica))

    def test_binds_corrected_complete_b2_three_node_fresh_state(self) -> None:
        fresh = self.contract.corrected_fresh_state_record
        self.assertEqual(("B2", "THREE_NODE_OPEN_LINE", ("node-a", "node-b", "node-c")), fresh[:3])
        entries = dict(fresh[7])["complete_L_state_payload"]["entries"]
        self.assertEqual((0.0, 0.0, 0.0), tuple(row["value"] for row in entries))
        self.assertEqual((self.contract.fresh_field_digest, self.contract.fresh_private_state_digest), (fresh[6], fresh[8]))

    def test_binds_independent_sequence_starts_and_internal_l_carry(self) -> None:
        joined = " ".join(self.contract.fresh_start_and_carry_rules)
        self.assertIn("two-independent", joined)
        self.assertIn("complete-L-private-state-carry-only-across-the-four", joined)
        self.assertIn("no-field-L-state-output-or-provenance-carries-between-sequences", joined)

    def test_binds_dual_digest_roles_and_complete_output_shape(self) -> None:
        self.assertEqual("output_digest", dict(self.contract.complete_provenance_digest_role)["name"])
        self.assertEqual("refinement_comparison_digest", dict(self.contract.comparison_digest_role)["name"])
        self.assertEqual((6, 8), (self.contract.signed_components_per_target_replica, self.contract.diagnostics_per_target_replica))

    def test_binds_twenty_four_call_budget_without_retry(self) -> None:
        self.assertEqual((3, 8, 24), (self.contract.target_replica_count, self.contract.intervals_per_target_replica, self.contract.maximum_new_interval_calls))
        self.assertEqual(0, dict(self.contract.execution_budget)["retry_or_repeat_calls"])

    def test_selects_without_implementation_execution_or_judgment(self) -> None:
        self.assertTrue(self.contract.case_selected)
        self.assertFalse(self.contract.runner_extension_implemented)
        self.assertEqual((0, 0), (self.contract.target_replicas_executed, self.contract.interval_calls_executed))
        self.assertFalse(self.contract.case_output_composed)
        self.assertFalse(self.contract.release_reuse_judgment_present)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertTrue(self.contract.exact_implementation_execution_authorized_next_stage)
        self.assertEqual(S1_LF_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1lf_b2_pin_case_selection_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1LFB2PINCaseSelectionContractError):
            replace(self.contract, maximum_new_interval_calls=25)
        source = inspect.getsource(build_dts1_s1lf_b2_pin_case_selection_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
