from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1kl_checkpoint_identity_audit import (
    DTS1S1KLCheckpointIdentityAuditError,
    S1_KL_DECISION,
    build_dts1_s1kl_checkpoint_identity_audit,
)


class DTS1S1KLCheckpointIdentityAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = build_dts1_s1kl_checkpoint_identity_audit()

    def test_binds_exact_s1kk_receipt_and_runner_source(self) -> None:
        self.assertEqual(64, len(self.audit.source_s1kk_digest))
        self.assertEqual(64, len(self.audit.runner_source_digest))

    def test_audits_six_replicas_and_twenty_four_checkpoints(self) -> None:
        self.assertEqual(6, self.audit.audited_replica_count)
        self.assertEqual(24, self.audit.audited_checkpoint_count)

    def test_finds_only_b1_r4_and_r8_affected(self) -> None:
        affected = tuple(row for row in self.audit.identity_records if row[6] == "AFFECTED_HISTORICAL_V2")
        self.assertEqual((4, 8), tuple(int(row[0].rsplit("r", 1)[1]) for row in affected))
        self.assertEqual(2, self.audit.affected_replica_count)
        self.assertEqual(8, self.audit.mismatched_checkpoint_count)

    def test_b1_r2_and_all_b2_outputs_are_unaffected(self) -> None:
        unaffected = tuple(row for row in self.audit.identity_records if row[6] == "UNAFFECTED")
        self.assertEqual(4, len(unaffected))
        self.assertTrue(all(row[3] == row[4] and row[5] == 0 for row in unaffected))

    def test_separates_numeric_comparison_and_provenance_impact(self) -> None:
        self.assertFalse(self.audit.numeric_results_invalidated)
        self.assertFalse(self.audit.comparison_digests_invalidated)
        self.assertFalse(self.audit.affected_provenance_outputs_valid_as_corrected_records)

    def test_preserves_historical_outputs_without_rewrite(self) -> None:
        self.assertEqual(2, len(self.audit.affected_output_digests))
        self.assertEqual(4, len(self.audit.unaffected_output_digests))
        self.assertFalse(self.audit.historical_records_rewritten)

    def test_executes_nothing_and_blocks_case_composition(self) -> None:
        self.assertEqual((0, 0), (self.audit.replicas_executed, self.audit.interval_calls_executed))
        self.assertTrue(self.audit.case_composition_blocked)

    def test_authorizes_only_versioned_correction_contract(self) -> None:
        self.assertTrue(self.audit.versioned_correction_contract_authorized_next_stage)
        self.assertEqual(S1_KL_DECISION, self.audit.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1kl_checkpoint_identity_audit()
        self.assertEqual(self.audit.audit_digest, second.audit_digest)
        with self.assertRaises(DTS1S1KLCheckpointIdentityAuditError):
            replace(self.audit, mismatched_checkpoint_count=7)
        source = inspect.getsource(build_dts1_s1kl_checkpoint_identity_audit)
        for forbidden in ("run_dts1_one_replica(", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
