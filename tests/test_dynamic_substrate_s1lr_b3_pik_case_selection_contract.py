from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1lr_b3_pik_case_selection_contract import (
    DTS1S1LRB3PIKCaseSelectionContractError,
    S1_LR_DECISION,
    S1_LR_SEQUENCE_KEYS,
    S1_LR_SOURCE_S1LP_DECISION,
    build_dts1_s1lp_b3_pih_case_output_contract,
    build_dts1_s1lr_b3_pik_case_selection_contract,
)
from mcm_field_organism.dynamic_substrate_s1jz_finite_orchestrator_api_contract import (
    S1_JZ_FRESH_STATE_RECORDS,
)


class DTS1S1LRB3PIKCaseSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1lr_b3_pik_case_selection_contract()

    def test_binds_exact_s1lp_source_and_registered_c11(self) -> None:
        source = build_dts1_s1lp_b3_pih_case_output_contract()
        self.assertEqual(("C11", "B3", "B3_F3_LOCAL_LEAKY", "P_IK_INTERFERENCE", 3, 6), self.contract.target_case_record[:6])
        self.assertEqual(S1_LR_SOURCE_S1LP_DECISION, source.decision)
        self.assertEqual(("C10",), source.source_s1jx_case_record[:1])
        self.assertEqual(self.contract.target_replica_ids, tuple(row[0] for row in self.contract.target_replica_records))

    def test_selects_exact_three_replica_profiles(self) -> None:
        self.assertEqual(3, self.contract.target_replica_count)
        self.assertEqual(3, len(self.contract.target_replica_records))
        self.assertEqual((("B3:P_IK_INTERFERENCE:r2", 2), ("B3:P_IK_INTERFERENCE:r4", 4), ("B3:P_IK_INTERFERENCE:r8", 8)), tuple((row[0], row[4]) for row in self.contract.target_replica_records))

    def test_binds_two_sequences_and_sequence_layout(self) -> None:
        self.assertEqual(S1_LR_SEQUENCE_KEYS, tuple(row[0] for row in self.contract.sequence_records))
        self.assertEqual(("P_IK_INTERFERENCE", "P_IK_INTERFERENCE"), tuple(row[1] for row in self.contract.sequence_records))
        self.assertEqual((4, 4), tuple(row[3] for row in self.contract.sequence_records))

    def test_binds_three_node_fresh_state_and_complete_m_state(self) -> None:
        fresh = self.contract.corrected_fresh_state_record
        self.assertEqual(("B3", "THREE_NODE_OPEN_LINE", ("node-a", "node-b", "node-c")), fresh[:3])
        self.assertEqual(self.contract.fresh_field_digest, fresh[6])
        self.assertEqual(self.contract.fresh_private_state_digest, fresh[8])
        fresh_private = dict(fresh[7])
        self.assertEqual(self.contract.embedded_m_state_digest, fresh_private["embedded_M_state_digest"])
        self.assertEqual(S1_JZ_FRESH_STATE_RECORDS[S1_JZ_FRESH_STATE_RECORDS.index(fresh)][6], self.contract.fresh_field_digest)

    def test_binds_no_execution_static_boundaries(self) -> None:
        self.assertTrue(self.contract.case_selected)
        self.assertFalse(self.contract.runner_extension_implemented)
        self.assertEqual((0, 0), (self.contract.target_replicas_executed, self.contract.interval_calls_executed))
        self.assertFalse(self.contract.case_output_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.runtime_integration_present)
        self.assertTrue(self.contract.exact_implementation_execution_authorized_next_stage)
        self.assertEqual((3, 2, 4, 8, 24), (self.contract.target_replica_count, self.contract.sequences_per_target_replica, self.contract.intervals_per_sequence, self.contract.intervals_per_target_replica, self.contract.maximum_new_interval_calls))
        self.assertEqual((2, 6, 8), (self.contract.checkpoints_per_target_replica, self.contract.signed_components_per_target_replica, self.contract.diagnostics_per_target_replica))

    def test_tamper_closed_and_no_runtime_code_paths(self) -> None:
        self.assertEqual(S1_LR_DECISION, self.contract.decision)
        second = build_dts1_s1lr_b3_pik_case_selection_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1LRB3PIKCaseSelectionContractError):
            replace(self.contract, interval_calls_executed=1)
        source = inspect.getsource(build_dts1_s1lr_b3_pik_case_selection_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
