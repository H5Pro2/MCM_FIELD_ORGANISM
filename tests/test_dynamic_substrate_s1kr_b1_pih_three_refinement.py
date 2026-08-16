from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch
import unittest

import mcm_field_organism.dynamic_substrate_dts1_one_replica_orchestrator as runner


class DTS1S1KRB1PIHThreeRefinementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.call_counts = {"materializer": 0, "adapter": 0}
        real_materializer = runner.materialize_dts1_common_interval
        real_adapter = runner.advance_dts1_private_baseline

        def counted_materializer(*args, **kwargs):
            cls.call_counts["materializer"] += 1
            return real_materializer(*args, **kwargs)

        def counted_adapter(*args, **kwargs):
            cls.call_counts["adapter"] += 1
            return real_adapter(*args, **kwargs)

        with patch.object(
            runner, "materialize_dts1_common_interval", counted_materializer
        ), patch.object(
            runner, "advance_dts1_private_baseline", counted_adapter
        ):
            cls.outputs = runner.run_dts1_b1_pih_three_refinement()

    def test_executes_exactly_three_replicas_and_nine_intervals(self) -> None:
        self.assertEqual({"materializer": 9, "adapter": 9}, self.call_counts)
        self.assertEqual(runner.S1_KR_TARGET_REPLICA_IDS, tuple(output.replica_id for output in self.outputs))
        self.assertEqual((2, 4, 8), tuple(output.refinement for output in self.outputs))

    def test_outputs_are_complete_atomic_b1_pih_v2_records(self) -> None:
        for output in self.outputs:
            self.assertEqual(runner.S1_KF_OUTPUT_SCHEMA_ID, output.schema_id)
            self.assertEqual(("B1", "P_IH_ATTENUATION"), (output.model_role, output.profile_block))
            self.assertEqual((3, 8, 3), (len(output.checkpoints), len(output.signed_components), len(output.adapter_diagnostics)))

    def test_checkpoint_ids_match_parent_and_ordinals_are_carried(self) -> None:
        for output in self.outputs:
            self.assertEqual((output.replica_id,) * 3, tuple(row.replica_id for row in output.checkpoints))
            self.assertEqual((1, 2, 3), tuple(row.ordinal for row in output.checkpoints))
            self.assertEqual(("P_IH_A_A_A",) * 3, tuple(row.sequence_key for row in output.checkpoints))

    def test_comparison_digests_are_bit_identical(self) -> None:
        self.assertEqual((runner.S1_KR_TARGET_COMPARISON_DIGEST,) * 3, tuple(output.refinement_comparison_digest for output in self.outputs))

    def test_provenance_digests_are_exact_and_distinct(self) -> None:
        digests = tuple(output.output_digest for output in self.outputs)
        self.assertEqual(runner.S1_KR_TARGET_OUTPUT_DIGESTS, digests)
        self.assertEqual(3, len(set(digests)))

    def test_signed_components_are_zero_without_interpretive_claim(self) -> None:
        self.assertEqual(((0.0,) * 8,) * 3, tuple(output.signed_components for output in self.outputs))

    def test_receipt_binds_execution_without_case_or_judgment(self) -> None:
        receipt = runner.build_dts1_s1kr_implementation_receipt()
        self.assertEqual(runner.S1_KR_TARGET_OUTPUT_DIGESTS, receipt.target_output_digests)
        self.assertEqual((3, 3, 9), (receipt.target_replica_count, receipt.interval_calls_per_target, receipt.total_new_interval_calls))
        self.assertTrue(receipt.three_refinement_comparison_set_accepted)
        self.assertFalse(receipt.case_output_composed)
        self.assertFalse(receipt.matrix_case_output_published)
        self.assertFalse(receipt.baseline_or_candidate_judgment_present)

    def test_registry_remains_closed_to_other_new_profiles(self) -> None:
        for replica_id in runner.S1_KR_TARGET_REPLICA_IDS:
            self.assertEqual(replica_id, runner.DTS1OneReplicaRunnerInput(runner.S1_KC_RUNNER_INPUT_SCHEMA_ID, replica_id).replica_id)
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            runner.DTS1OneReplicaRunnerInput(runner.S1_KC_RUNNER_INPUT_SCHEMA_ID, "B1:P_IN_RELEASE_REUSE:r2")

    def test_triple_and_receipt_are_fail_closed(self) -> None:
        with patch.object(runner, "run_dts1_one_replica", side_effect=(self.outputs[0], self.outputs[0], self.outputs[2])):
            with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
                runner.run_dts1_b1_pih_three_refinement()
        receipt = runner.build_dts1_s1kr_implementation_receipt()
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            replace(receipt, total_new_interval_calls=10)


if __name__ == "__main__":
    unittest.main()
