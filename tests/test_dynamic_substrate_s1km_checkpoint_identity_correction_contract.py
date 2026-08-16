from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.dynamic_substrate_s1km_checkpoint_identity_correction_contract import (
    DTS1S1KMCheckpointIdentityCorrectionContractError,
    S1_KM_DECISION,
    build_dts1_s1km_checkpoint_identity_correction_contract,
)


class DTS1S1KMCheckpointIdentityCorrectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_dts1_s1km_checkpoint_identity_correction_contract()

    def test_binds_exact_s1kl_audit_and_affected_pair(self) -> None:
        self.assertEqual(64, len(self.contract.source_s1kl_digest))
        self.assertEqual((4, 8), tuple(int(value.rsplit("r", 1)[1]) for value in self.contract.target_replica_ids))
        self.assertEqual(2, len(self.contract.historical_output_digests))

    def test_requires_checkpoint_parent_identity_and_fail_closed_validation(self) -> None:
        joined = " ".join(self.contract.identity_rules)
        self.assertIn("checkpoint-replica_id-must-bit-equal", joined)
        self.assertIn("fail-closed", joined)

    def test_keeps_v2_schema_under_versioned_semantic_overlay(self) -> None:
        self.assertEqual("mcm.s1jz.complete-replica-output.v2", dict(self.contract.corrected_output_schema)["schema_id"])
        self.assertTrue(self.contract.semantic_overlay_bound)
        self.assertFalse(self.contract.output_schema_version_changed)

    def test_preserves_comparison_digest_by_bound_identity_exclusion(self) -> None:
        self.assertEqual("refinement-specific-control-identity", dict(self.contract.checkpoint_comparison_exclusions)["replica_id"])
        self.assertEqual(64, len(self.contract.bound_comparison_digest))
        self.assertIn("comparison-digest-must-remain-bit-identical", " ".join(self.contract.versioning_rules))

    def test_binds_exact_pair_and_eight_call_budget(self) -> None:
        self.assertEqual((2, 4, 8), (
            self.contract.target_replica_count,
            self.contract.intervals_per_target,
            self.contract.maximum_new_interval_calls,
        ))
        self.assertEqual(0, dict(self.contract.rerun_plan)["retry_or_repeat_calls"])

    def test_requires_new_provenance_and_identical_numeric_content(self) -> None:
        joined = " ".join(self.contract.acceptance_rules)
        self.assertIn("numeric-checkpoints-components-and-adapter-diagnostics-bit-equal", joined)
        self.assertIn("corrected-provenance-digests-differ", joined)

    def test_leaves_b1_r2_and_all_b2_outputs_unaffected(self) -> None:
        scope = " ".join(self.contract.unaffected_scope)
        self.assertIn("B1-r2", scope)
        self.assertIn("all-B2-P_IE", scope)

    def test_implements_and_executes_nothing_and_blocks_composition(self) -> None:
        self.assertFalse(self.contract.runner_correction_implemented)
        self.assertEqual((0, 0), (self.contract.replicas_executed, self.contract.interval_calls_executed))
        self.assertFalse(self.contract.historical_records_rewritten)
        self.assertTrue(self.contract.case_composition_blocked)
        self.assertTrue(self.contract.exact_correction_and_rerun_authorized_next_stage)
        self.assertEqual(S1_KM_DECISION, self.contract.decision)

    def test_is_deterministic_tamper_evident_and_call_free(self) -> None:
        second = build_dts1_s1km_checkpoint_identity_correction_contract()
        self.assertEqual(self.contract.contract_digest, second.contract_digest)
        with self.assertRaises(DTS1S1KMCheckpointIdentityCorrectionContractError):
            replace(self.contract, maximum_new_interval_calls=9)
        source = inspect.getsource(build_dts1_s1km_checkpoint_identity_correction_contract)
        for forbidden in ("run_dts1_one_replica", "materialize_", "advance_"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
