from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ki_b1_pie_case_output_contract import (
    DTS1S1KIB1PIECaseOutputContractError,
    S1_KI_DECISION,
    build_dts1_s1ki_b1_pie_case_output_contract,
)


class DTS1S1KIB1PIECaseOutputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1ki_b1_pie_case_output_contract()

    def test_binds_exact_s1kh_source_and_c01(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1kh_digest))
        self.assertEqual("C01", self.contract.source_s1jx_case_record[0])
        self.assertEqual("B1", self.contract.source_s1jx_case_record[1])

    def test_schema_contains_complete_three_refinement_case(self) -> None:
        schema = dict(self.contract.case_schema)
        for field in (
            "replica_ids",
            "replica_output_digests",
            "refinement_comparison_digest",
            "components_by_refinement",
            "primary_components",
            "case_output_digest",
        ):
            self.assertIn(field, schema["fields"])

    def test_binds_r2_r4_r8_and_three_distinct_provenance_digests(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual((2, 4, 8), tuple(row[0] for row in payload["components_by_refinement"]))
        self.assertEqual(3, self.contract.replica_count)
        self.assertEqual(3, self.contract.distinct_provenance_digest_count)

    def test_binds_one_comparison_digest_and_bit_identical_components(self) -> None:
        self.assertEqual(1, self.contract.comparison_digest_count)
        self.assertTrue(self.contract.all_components_bit_identical)
        self.assertEqual(((0.0,) * 8,) * 3, tuple(row[1] for row in dict(self.contract.case_payload)["components_by_refinement"]))

    def test_primary_output_is_r4_with_eight_components(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual(4, self.contract.primary_refinement)
        self.assertEqual(8, self.contract.component_count_per_refinement)
        self.assertEqual((0.0,) * 8, payload["primary_components"])

    def test_composes_no_judgment_or_matrix_publication(self) -> None:
        self.assertTrue(self.contract.case_record_composed)
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.candidate_comparison_present)
        self.assertFalse(self.contract.runtime_integration_present)

    def test_executes_no_new_replica_or_interval(self) -> None:
        self.assertEqual((0, 0), (
            self.contract.new_replicas_executed,
            self.contract.new_interval_calls_executed,
        ))

    def test_authorizes_only_next_case_selection_contract(self) -> None:
        self.assertTrue(self.contract.next_case_selection_contract_authorized)
        self.assertEqual(S1_KI_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1ki_b1_pie_case_output_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1KIB1PIECaseOutputContractError):
            replace(self.contract, baseline_judgment_present=True)
        source = inspect.getsource(build_dts1_s1ki_b1_pie_case_output_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
