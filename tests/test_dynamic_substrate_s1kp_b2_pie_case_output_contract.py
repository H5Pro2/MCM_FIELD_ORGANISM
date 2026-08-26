from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1kp_b2_pie_case_output_contract import (
    DTS1S1KPB2PIECaseOutputContractError,
    S1_KP_DECISION,
    build_dts1_s1kp_b2_pie_case_output_contract,
)


class DTS1S1KPB2PIECaseOutputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1kp_b2_pie_case_output_contract()

    def test_binds_exact_sequence_and_output_sources_for_c05(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1ko_digest))
        self.assertEqual(64, len(self.contract.source_s1kk_digest))
        self.assertEqual(("C05", "B2"), self.contract.source_s1jx_case_record[:2])

    def test_binds_three_b2_pie_refinements(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual((2, 4, 8), tuple(int(value.rsplit("r", 1)[1]) for value in payload["replica_ids"]))
        self.assertEqual(3, self.contract.replica_count)

    def test_binds_three_distinct_provenance_digests(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual(3, self.contract.distinct_provenance_digest_count)
        self.assertEqual(3, len(payload["replica_output_digests"]))
        self.assertTrue(all(len(value) == 64 for value in payload["replica_output_digests"]))

    def test_binds_valid_checkpoint_parent_identity(self) -> None:
        self.assertTrue(self.contract.checkpoint_parent_identity_valid)
        self.assertTrue(dict(self.contract.case_payload)["checkpoint_parent_identity_valid"])

    def test_binds_one_comparison_digest_and_identical_components(self) -> None:
        self.assertEqual(1, self.contract.comparison_digest_count)
        self.assertTrue(self.contract.all_components_bit_identical)
        self.assertEqual(((0.0,) * 8,) * 3, tuple(row[1] for row in dict(self.contract.case_payload)["components_by_refinement"]))

    def test_primary_output_is_r4_with_eight_components(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual(4, self.contract.primary_refinement)
        self.assertEqual(8, self.contract.component_count_per_refinement)
        self.assertEqual((0.0,) * 8, payload["primary_components"])

    def test_composes_no_matrix_or_judgment(self) -> None:
        self.assertTrue(self.contract.case_record_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.candidate_comparison_present)
        self.assertFalse(self.contract.runtime_integration_present)

    def test_executes_nothing_and_authorizes_only_next_selection(self) -> None:
        self.assertEqual((0, 0), (self.contract.new_replicas_executed, self.contract.new_interval_calls_executed))
        self.assertTrue(self.contract.next_case_selection_contract_authorized)
        self.assertEqual(S1_KP_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1kp_b2_pie_case_output_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1KPB2PIECaseOutputContractError):
            replace(self.contract, case_record_composed=False)
        source = inspect.getsource(build_dts1_s1kp_b2_pie_case_output_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
