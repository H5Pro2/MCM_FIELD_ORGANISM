from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1ke_dual_refinement_digest_contract import (
    DTS1S1KEDualRefinementDigestContractError,
    S1_KE_DECISION,
    build_dts1_s1ke_dual_refinement_digest_contract,
)


class DTS1S1KEDualRefinementDigestContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1ke_dual_refinement_digest_contract()

    def _contract(self):
        return self.contract

    def test_binds_exact_s1kd_s1jx_and_s1jz_sources(self) -> None:
        contract = self._contract()
        self.assertEqual(64, len(contract.source_s1kd_digest))
        self.assertEqual(64, len(contract.source_s1jx_digest))
        self.assertEqual(64, len(contract.source_s1jz_digest))

    def test_keeps_complete_output_digest_identity_bearing(self) -> None:
        role = dict(self._contract().complete_provenance_digest_role)
        self.assertEqual("output_digest", role["name"])
        self.assertIn("identity-bearing", role["domain"])
        self.assertFalse(role["cross_refinement_equality_required"])

    def test_binds_separate_identity_neutral_comparison_digest(self) -> None:
        role = dict(self._contract().comparison_digest_role)
        self.assertEqual("refinement_comparison_digest", role["name"])
        self.assertTrue(role["cross_refinement_equality_required_for_B1_B2"])

    def test_excludes_only_control_identity_and_derived_digests(self) -> None:
        schema = dict(self._contract().comparison_payload_schema)
        self.assertEqual(
            ("replica_id", "refinement", "output_digest", "refinement_comparison_digest"),
            tuple(row[0] for row in schema["top_level_exclusions"]),
        )
        self.assertEqual(("replica_id",), tuple(row[0] for row in schema["checkpoint_exclusions"]))

    def test_comparison_keeps_all_numeric_and_diagnostic_content(self) -> None:
        schema = dict(self._contract().comparison_payload_schema)
        checkpoint_fields = schema["checkpoint_fields"]
        for field in ("activation", "afterimage", "complete_field_digest", "private_state_digest", "adapter_output_digest"):
            self.assertIn(field, checkpoint_fields)
        self.assertIn("signed_components", schema["fields"])
        self.assertIn("adapter_diagnostics", schema["fields"])

    def test_corrected_output_publishes_both_digests_atomically(self) -> None:
        schema = dict(self._contract().corrected_output_schema)
        self.assertIn("refinement_comparison_digest", schema["fields"])
        self.assertIn("output_digest", schema["fields"])
        self.assertIn("both-digests", schema["publication"])

    def test_synthetic_refinements_have_distinct_provenance_one_comparison(self) -> None:
        contract = self._contract()
        self.assertEqual((3, 1), (
            contract.distinct_complete_provenance_digest_count,
            contract.distinct_comparison_digest_count,
        ))
        self.assertEqual((2, 4, 8), tuple(row[1] for row in contract.synthetic_dual_digest_records))

    def test_changes_no_runner_and_executes_nothing(self) -> None:
        contract = self._contract()
        self.assertFalse(contract.existing_r2_runner_changed)
        self.assertFalse(contract.r4_r8_runner_implemented)
        self.assertEqual((0, 0, 0), (
            contract.r4_r8_replicas_executed,
            contract.interval_calls_executed,
            contract.complete_matrix_cases_executed,
        ))
        self.assertFalse(contract.runtime_integration_present)

    def test_authorizes_only_r2_dual_digest_implementation(self) -> None:
        contract = self._contract()
        self.assertTrue(contract.r2_dual_digest_implementation_authorized_next_stage)
        self.assertEqual(S1_KE_DECISION, contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        contract = self._contract()
        self.assertEqual(contract.contract_digest, self._contract().contract_digest)
        with self.assertRaises(DTS1S1KEDualRefinementDigestContractError):
            replace(contract, r4_r8_runner_implemented=True)
        source = inspect.getsource(build_dts1_s1ke_dual_refinement_digest_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
