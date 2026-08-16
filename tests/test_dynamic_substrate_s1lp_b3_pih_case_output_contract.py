from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1lp_b3_pih_case_output_contract import (
    DTS1S1LPB3PIHCaseOutputContractError,
    S1_LP_CASE_ID,
    S1_LP_DECISION,
    S1_LP_SOURCE_S1LM_DIGEST,
    S1_LP_SOURCE_S1LO_DIGEST,
    S1_LP_SOURCE_S1LN_DIGEST,
    build_dts1_s1lp_b3_pih_case_output_contract,
    S1_LP_CASE_OUTPUT_DIGEST,
    _case_payload,
)
from mcm_field_organism.dynamic_substrate_s1lm_b3_pih_case_selection_contract import (
    build_dts1_s1lm_b3_pih_case_selection_contract,
)
from mcm_field_organism.dynamic_substrate_s1ln_b3_pih_resource_anatomy_contract import (
    build_dts1_s1ln_b3_pih_resource_anatomy_contract,
)
from mcm_field_organism.dynamic_substrate_dts1_one_replica_orchestrator import (
    build_dts1_s1lo_implementation_receipt,
    S1_LO_TARGET_REPLICA_IDS,
    S1_LO_TARGET_COMPONENTS_BY_REFINEMENT,
)


class DTS1S1LPB3PIHCaseOutputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1lp_b3_pih_case_output_contract()

    def test_binds_expected_boundary_sources_and_target_case(self) -> None:
        self.assertEqual(
            (
                64,
                64,
                64,
            ),
            (
                len(self.contract.source_s1lm_digest),
                len(self.contract.source_s1ln_digest),
                len(self.contract.source_s1lo_receipt_digest),
            ),
        )
        self.assertEqual(S1_LP_CASE_ID, S1_LP_CASE_ID)
        self.assertEqual(S1_LP_SOURCE_S1LM_DIGEST, self.contract.source_s1lm_digest)
        self.assertEqual(S1_LP_SOURCE_S1LN_DIGEST, self.contract.source_s1ln_digest)
        self.assertEqual(S1_LP_SOURCE_S1LO_DIGEST, self.contract.source_s1lo_receipt_digest)

    def test_binds_three_refinements_and_primaries(self) -> None:
        payload = dict(self.contract.case_payload)
        self.assertEqual(S1_LO_TARGET_REPLICA_IDS, payload["replica_ids"])
        self.assertEqual((2, 4, 8), tuple(int(value.rsplit("r", 1)[1]) for value in payload["replica_ids"]))
        self.assertEqual(
            S1_LO_TARGET_COMPONENTS_BY_REFINEMENT,
            payload["components_by_refinement"],
        )
        self.assertEqual(4, self.contract.primary_refinement)
        self.assertEqual(payload["primary_components"], dict(payload["components_by_refinement"])[4])

    def test_records_components_and_digests(self) -> None:
        self.assertEqual(self.contract.comparison_digest_count, 3)
        self.assertEqual(self.contract.distinct_provenance_digest_count, 3)
        self.assertEqual(self.contract.distinct_private_state_digest_count, 3)
        self.assertEqual(self.contract.case_output_digest, S1_LP_CASE_OUTPUT_DIGEST)
        self.assertEqual(tuple(_case_payload().items()), self.contract.case_payload)

    def test_composes_no_runtime_and_static_boundary_checks(self) -> None:
        self.assertEqual(3, self.contract.replica_count)
        self.assertEqual(3, self.contract.checkpoint_count_per_refinement)
        self.assertEqual(8, self.contract.component_count_per_refinement)
        self.assertTrue(self.contract.case_record_composed)
        self.assertTrue(self.contract.primary_components_nonzero)
        self.assertFalse(self.contract.all_components_bit_identical)
        self.assertFalse(self.contract.runtime_integration_present)
        self.assertFalse(self.contract.next_case_output_contract_authorized)
        self.assertEqual((0, 0), (self.contract.new_replicas_executed, self.contract.new_interval_calls_executed))
        self.assertFalse(self.contract.matrix_24_case_output_published)
        self.assertFalse(self.contract.baseline_judgment_present)
        self.assertFalse(self.contract.candidate_comparison_present)

    def test_chain_consistency_and_determinism(self) -> None:
        self.assertEqual(S1_LP_DECISION, self.contract.decision)
        second = build_dts1_s1lp_b3_pih_case_output_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        self.assertEqual(S1_LP_CASE_OUTPUT_DIGEST, self.contract.case_output_digest)

    def test_tamper_closed_and_no_runtime_invocation(self) -> None:
        with self.assertRaises(DTS1S1LPB3PIHCaseOutputContractError):
            replace(self.contract, decision="CHANGED")
        s1lm = build_dts1_s1lm_b3_pih_case_selection_contract()
        s1ln = build_dts1_s1ln_b3_pih_resource_anatomy_contract()
        s1lo = build_dts1_s1lo_implementation_receipt()
        self.assertEqual(S1_LP_SOURCE_S1LM_DIGEST, s1lm.contract_digest)
        self.assertEqual(S1_LP_SOURCE_S1LN_DIGEST, s1ln.contract_digest)
        self.assertEqual(S1_LP_SOURCE_S1LO_DIGEST, s1lo.receipt_digest)
        source = inspect.getsource(build_dts1_s1lp_b3_pih_case_output_contract)
        for forbidden in ("run_dts1_b3_pih_three_refinement", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
