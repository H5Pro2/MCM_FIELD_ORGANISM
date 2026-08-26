from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch
import unittest

import mcm_field_organism.dynamic_substrate_dts1_one_replica_orchestrator as runner


class DTS1S1LOB3PIHThreeRefinementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.call_counts = {"materializer": 0, "adapter": 0, "fresh": 0}
        real_materializer = runner.materialize_dts1_common_interval
        real_adapter = runner.advance_dts1_private_baseline
        real_fresh = runner._build_fresh_state

        def counted_materializer(*args, **kwargs):
            cls.call_counts["materializer"] += 1
            return real_materializer(*args, **kwargs)

        def counted_adapter(*args, **kwargs):
            cls.call_counts["adapter"] += 1
            return real_adapter(*args, **kwargs)

        def counted_fresh(*args, **kwargs):
            cls.call_counts["fresh"] += 1
            return real_fresh(*args, **kwargs)

        with (
            patch.object(runner, "materialize_dts1_common_interval", counted_materializer),
            patch.object(runner, "advance_dts1_private_baseline", counted_adapter),
            patch.object(runner, "_build_fresh_state", counted_fresh),
        ):
            cls.outputs = runner.run_dts1_b3_pih_three_refinement()

    def test_executes_three_replicas_nine_intervals_and_three_fresh_starts(self) -> None:
        self.assertEqual({"materializer": 9, "adapter": 9, "fresh": 3}, self.call_counts)
        self.assertEqual(runner.S1_LO_TARGET_REPLICA_IDS, tuple(output.replica_id for output in self.outputs))
        self.assertEqual((2, 4, 8), tuple(output.refinement for output in self.outputs))

    def test_outputs_are_complete_atomic_b3_pih_records(self) -> None:
        for output in self.outputs:
            self.assertEqual(
                (runner.S1_KF_OUTPUT_SCHEMA_ID, "B3", "P_IH_ATTENUATION"),
                (output.schema_id, output.model_role, output.profile_block),
            )
            self.assertEqual((3, 8, 3), (len(output.checkpoints), len(output.signed_components), len(output.adapter_diagnostics)))

    def test_checkpoint_sequences_share_local_carry(self) -> None:
        for output in self.outputs:
            self.assertEqual(("P_IH_A_A_A",) * 3, tuple(row.sequence_key for row in output.checkpoints))
            self.assertEqual((1, 2, 3), tuple(row.ordinal for row in output.checkpoints))
            self.assertEqual((output.replica_id,) * 3, tuple(row.replica_id for row in output.checkpoints))

    def test_checkpoint_private_state_digests_are_exact(self) -> None:
        self.assertEqual(
            runner.S1_LO_CHECKPOINT_PRIVATE_STATE_DIGESTS,
            tuple(output.checkpoints[-1].private_state_digest for output in self.outputs),
        )

    def test_provenance_and_comparison_digests_are_distinct_and_exact(self) -> None:
        self.assertEqual(runner.S1_LO_TARGET_OUTPUT_DIGESTS, tuple(output.output_digest for output in self.outputs))
        self.assertEqual(runner.S1_LO_TARGET_COMPARISON_DIGESTS, tuple(output.refinement_comparison_digest for output in self.outputs))
        self.assertEqual((3, 3), (len(set(runner.S1_LO_TARGET_OUTPUT_DIGESTS)), len(set(runner.S1_LO_TARGET_COMPARISON_DIGESTS))))

    def test_components_are_bound_by_refinement_and_not_all_zero(self) -> None:
        self.assertEqual(runner.S1_LO_TARGET_COMPONENTS_BY_REFINEMENT, tuple((output.refinement, output.signed_components) for output in self.outputs))
        self.assertFalse(all(value == 0.0 for _, values in runner.S1_LO_TARGET_COMPONENTS_BY_REFINEMENT for value in values))

    def test_receipt_binds_execution_without_case_or_judgment(self) -> None:
        receipt = runner.build_dts1_s1lo_implementation_receipt()
        self.assertEqual((3, 3, 9), (receipt.target_replica_count, receipt.interval_calls_per_target, receipt.total_new_interval_calls))
        self.assertEqual(runner.S1_LO_TARGET_OUTPUT_DIGESTS, tuple(receipt.target_output_digests))
        self.assertTrue(receipt.three_interval_sequence_carry_implemented)
        self.assertTrue(receipt.checkpoint_parent_identity_enforced)
        self.assertFalse(receipt.all_signed_components_zero)
        self.assertFalse(receipt.case_output_composed)
        self.assertFalse(receipt.baseline_or_candidate_judgment_present)

    def test_registry_remains_closed_to_other_new_profiles(self) -> None:
        for replica_id in runner.S1_LO_TARGET_REPLICA_IDS:
            self.assertEqual(replica_id, runner.DTS1OneReplicaRunnerInput(runner.S1_KC_RUNNER_INPUT_SCHEMA_ID, replica_id).replica_id)
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            runner.DTS1OneReplicaRunnerInput(runner.S1_KC_RUNNER_INPUT_SCHEMA_ID, "B3:P_IH_ATTENUATION:r16")

    def test_triple_and_receipt_are_fail_closed(self) -> None:
        with patch.object(runner, "run_dts1_one_replica", side_effect=(self.outputs[0], self.outputs[1], self.outputs[1])):
            with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
                runner.run_dts1_b3_pih_three_refinement()
        receipt = runner.build_dts1_s1lo_implementation_receipt()
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            replace(receipt, total_new_interval_calls=10)


if __name__ == "__main__":
    unittest.main()
