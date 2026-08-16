from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch
import unittest

import mcm_field_organism.dynamic_substrate_dts1_one_replica_orchestrator as runner


class DTS1S1LGB2PINThreeRefinementTests(unittest.TestCase):
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
            cls.outputs = runner.run_dts1_b2_pin_three_refinement()

    def test_executes_three_replicas_twenty_four_intervals_and_six_fresh_sequences(self) -> None:
        self.assertEqual({"materializer": 24, "adapter": 24, "fresh": 6}, self.call_counts)
        self.assertEqual(runner.S1_LG_TARGET_REPLICA_IDS, tuple(output.replica_id for output in self.outputs))

    def test_outputs_are_complete_atomic_b2_pin_v2_records(self) -> None:
        for output in self.outputs:
            self.assertEqual((runner.S1_KF_OUTPUT_SCHEMA_ID, "B2", "P_IN_RELEASE_REUSE"), (output.schema_id, output.model_role, output.profile_block))
            self.assertEqual((2, 6, 8), (len(output.checkpoints), len(output.signed_components), len(output.adapter_diagnostics)))

    def test_terminal_checkpoints_have_correct_sequences_nodes_and_parent_ids(self) -> None:
        for output in self.outputs:
            self.assertEqual(("P_IN_RECOVERY_ON", "P_IN_RECOVERY_OFF"), tuple(row.sequence_key for row in output.checkpoints))
            self.assertEqual((4, 4), tuple(row.ordinal for row in output.checkpoints))
            self.assertEqual((("node-a", "node-b", "node-c"),) * 2, tuple(row.node_ids for row in output.checkpoints))
            self.assertEqual((output.replica_id,) * 2, tuple(row.replica_id for row in output.checkpoints))

    def test_independent_sequence_terminals_are_bit_identical(self) -> None:
        for output in self.outputs:
            self.assertEqual((runner.S1_LG_TERMINAL_FIELD_DIGEST,) * 2, tuple(row.complete_field_digest for row in output.checkpoints))
            self.assertEqual((runner.S1_LG_TERMINAL_PRIVATE_STATE_DIGEST,) * 2, tuple(row.private_state_digest for row in output.checkpoints))
            self.assertEqual((runner.S1_LG_TERMINAL_ADAPTER_OUTPUT_DIGEST,) * 2, tuple(row.adapter_output_digest for row in output.checkpoints))

    def test_comparison_and_provenance_digests_are_exact(self) -> None:
        self.assertEqual((runner.S1_LG_TARGET_COMPARISON_DIGEST,) * 3, tuple(output.refinement_comparison_digest for output in self.outputs))
        self.assertEqual(runner.S1_LG_TARGET_OUTPUT_DIGESTS, tuple(output.output_digest for output in self.outputs))
        self.assertEqual(3, len({output.output_digest for output in self.outputs}))

    def test_signed_components_are_zero_without_interpretive_claim(self) -> None:
        self.assertEqual((runner.S1_LG_TARGET_COMPONENTS,) * 3, tuple(output.signed_components for output in self.outputs))

    def test_receipt_binds_execution_without_case_or_judgment(self) -> None:
        receipt = runner.build_dts1_s1lg_implementation_receipt()
        self.assertEqual((3, 2, 4, 8, 24), (receipt.target_replica_count, receipt.sequences_per_target, receipt.interval_calls_per_sequence, receipt.interval_calls_per_target, receipt.total_new_interval_calls))
        self.assertTrue(receipt.sequence_terminal_digests_bit_identical)
        self.assertFalse(receipt.case_output_composed)
        self.assertFalse(receipt.release_reuse_or_baseline_judgment_present)

    def test_registry_remains_closed_to_other_new_profiles(self) -> None:
        for replica_id in runner.S1_LG_TARGET_REPLICA_IDS:
            self.assertEqual(replica_id, runner.DTS1OneReplicaRunnerInput(runner.S1_KC_RUNNER_INPUT_SCHEMA_ID, replica_id).replica_id)
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            runner.DTS1OneReplicaRunnerInput(runner.S1_KC_RUNNER_INPUT_SCHEMA_ID, "B2:P_IN_RELEASE_REUSE:r16")

    def test_triple_and_receipt_are_fail_closed(self) -> None:
        with patch.object(runner, "run_dts1_one_replica", side_effect=(self.outputs[0], self.outputs[0], self.outputs[2])):
            with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
                runner.run_dts1_b2_pin_three_refinement()
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            replace(runner.build_dts1_s1lg_implementation_receipt(), total_new_interval_calls=25)


if __name__ == "__main__":
    unittest.main()
