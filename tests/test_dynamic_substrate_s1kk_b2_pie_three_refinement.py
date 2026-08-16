from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch
import unittest

import mcm_field_organism.dynamic_substrate_dts1_one_replica_orchestrator as runner


class DTS1S1KKB2PIEThreeRefinementTests(unittest.TestCase):
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
            cls.outputs = runner.run_dts1_b2_pie_three_refinement()

    def test_executes_exactly_three_replicas_and_twelve_intervals(self) -> None:
        self.assertEqual({"materializer": 12, "adapter": 12}, self.call_counts)
        self.assertEqual(
            runner.S1_KK_TARGET_REPLICA_IDS,
            tuple(output.replica_id for output in self.outputs),
        )
        self.assertEqual((2, 4, 8), tuple(output.refinement for output in self.outputs))

    def test_outputs_are_complete_atomic_b2_v2_records(self) -> None:
        for output in self.outputs:
            self.assertEqual(runner.S1_KF_OUTPUT_SCHEMA_ID, output.schema_id)
            self.assertEqual("B2", output.model_role)
            self.assertEqual(4, len(output.checkpoints))
            self.assertEqual(8, len(output.signed_components))
            self.assertEqual(4, len(output.adapter_diagnostics))

    def test_comparison_digests_are_bit_identical(self) -> None:
        self.assertEqual(
            (runner.S1_KK_TARGET_COMPARISON_DIGEST,) * 3,
            tuple(output.refinement_comparison_digest for output in self.outputs),
        )

    def test_provenance_digests_are_exact_and_distinct(self) -> None:
        digests = tuple(output.output_digest for output in self.outputs)
        self.assertEqual(runner.S1_KK_TARGET_OUTPUT_DIGESTS, digests)
        self.assertEqual(3, len(set(digests)))

    def test_sequences_start_fresh_and_carry_l_only_internally(self) -> None:
        for output in self.outputs:
            checkpoints = output.checkpoints
            self.assertEqual(checkpoints[0].private_state_digest, checkpoints[2].private_state_digest)
            self.assertEqual(checkpoints[1].private_state_digest, checkpoints[3].private_state_digest)
            self.assertNotEqual(checkpoints[0].private_state_digest, checkpoints[1].private_state_digest)
            self.assertEqual((output.replica_id,) * 4, tuple(row.replica_id for row in checkpoints))

    def test_signed_components_are_the_expected_zero_control(self) -> None:
        self.assertEqual(
            ((0.0,) * 8,) * 3,
            tuple(output.signed_components for output in self.outputs),
        )

    def test_receipt_binds_execution_without_case_or_judgment(self) -> None:
        receipt = runner.build_dts1_s1kk_implementation_receipt()
        self.assertEqual(runner.S1_KK_TARGET_OUTPUT_DIGESTS, receipt.target_output_digests)
        self.assertEqual((3, 4, 12), (
            receipt.target_replica_count,
            receipt.interval_calls_per_target,
            receipt.total_new_interval_calls,
        ))
        self.assertTrue(receipt.three_refinement_comparison_set_accepted)
        self.assertFalse(receipt.case_output_composed)
        self.assertFalse(receipt.matrix_case_output_published)
        self.assertFalse(receipt.baseline_or_candidate_judgment_present)

    def test_registry_remains_closed_to_other_roles_and_profiles(self) -> None:
        for replica_id in runner.S1_KK_TARGET_REPLICA_IDS:
            self.assertEqual(
                replica_id,
                runner.DTS1OneReplicaRunnerInput(
                    runner.S1_KC_RUNNER_INPUT_SCHEMA_ID, replica_id
                ).replica_id,
            )
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            runner.DTS1OneReplicaRunnerInput(
                runner.S1_KC_RUNNER_INPUT_SCHEMA_ID,
                "B2:P_IK_INTERFERENCE:r2",
            )

    def test_triple_and_receipt_are_fail_closed(self) -> None:
        with patch.object(
            runner,
            "run_dts1_one_replica",
            side_effect=(self.outputs[0], self.outputs[0], self.outputs[2]),
        ):
            with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
                runner.run_dts1_b2_pie_three_refinement()
        receipt = runner.build_dts1_s1kk_implementation_receipt()
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            replace(receipt, total_new_interval_calls=13)


if __name__ == "__main__":
    unittest.main()
