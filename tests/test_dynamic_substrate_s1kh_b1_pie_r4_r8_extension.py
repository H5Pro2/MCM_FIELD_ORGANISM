from __future__ import annotations

from unittest.mock import patch
import unittest

import mcm_field_organism.dynamic_substrate_dts1_one_replica_orchestrator as runner


class DTS1S1KHB1PIER4R8ExtensionTests(unittest.TestCase):
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

        with patch.object(runner, "materialize_dts1_common_interval", counted_materializer), patch.object(
            runner, "advance_dts1_private_baseline", counted_adapter
        ):
            cls.outputs = runner.run_dts1_b1_pie_r4_r8_extension()

    def test_executes_exactly_one_r4_and_one_r8_with_eight_calls(self) -> None:
        self.assertEqual({"materializer": 8, "adapter": 8}, self.call_counts)
        self.assertEqual(runner.S1_KH_TARGET_REPLICA_IDS, tuple(output.replica_id for output in self.outputs))
        self.assertEqual((4, 8), tuple(output.refinement for output in self.outputs))

    def test_both_outputs_are_complete_atomic_v2_records(self) -> None:
        self.assertTrue(all(output.schema_id == runner.S1_KF_OUTPUT_SCHEMA_ID for output in self.outputs))
        self.assertTrue(all(len(output.checkpoints) == 4 for output in self.outputs))
        self.assertTrue(all(len(output.signed_components) == 8 for output in self.outputs))
        self.assertTrue(all(len(output.adapter_diagnostics) == 4 for output in self.outputs))

    def test_r4_and_r8_comparison_digests_equal_bound_r2(self) -> None:
        self.assertEqual(
            (runner.S1_KF_EXEMPLAR_COMPARISON_DIGEST,) * 2,
            tuple(output.refinement_comparison_digest for output in self.outputs),
        )

    def test_identity_bearing_provenance_digests_are_distinct(self) -> None:
        self.assertEqual(2, len({output.output_digest for output in self.outputs}))
        self.assertNotIn(
            runner.S1_KF_EXEMPLAR_OUTPUT_DIGEST,
            {output.output_digest for output in self.outputs},
        )

    def test_b1_signed_components_remain_bit_identical_zero(self) -> None:
        self.assertEqual(((0.0,) * 8,) * 2, tuple(output.signed_components for output in self.outputs))

    def test_s1kh_receipt_remains_the_immutable_historical_pair(self) -> None:
        receipt = runner.build_dts1_s1kh_implementation_receipt()
        self.assertEqual(
            runner.S1_KH_TARGET_OUTPUT_DIGESTS,
            receipt.target_output_digests,
        )
        self.assertNotEqual(
            tuple(output.output_digest for output in self.outputs),
            receipt.target_output_digests,
        )
        self.assertEqual(
            tuple(output.refinement_comparison_digest for output in self.outputs),
            receipt.target_comparison_digests,
        )
        self.assertEqual((2, 4, 8), (
            receipt.target_replica_count,
            receipt.interval_calls_per_target,
            receipt.total_new_interval_calls,
        ))
        self.assertTrue(receipt.three_refinement_comparison_set_accepted)
        self.assertFalse(receipt.matrix_case_output_published)

    def test_input_registry_accepts_only_r2_r4_r8(self) -> None:
        for replica_id in runner.S1_KH_ALLOWED_REPLICA_IDS:
            record = runner.DTS1OneReplicaRunnerInput(runner.S1_KC_RUNNER_INPUT_SCHEMA_ID, replica_id)
            self.assertEqual(replica_id, record.replica_id)
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            runner.DTS1OneReplicaRunnerInput(
                runner.S1_KC_RUNNER_INPUT_SCHEMA_ID,
                "B1:P_IK_INTERFERENCE:r4",
            )

    def test_pair_acceptance_is_fail_closed_without_partial_return(self) -> None:
        with patch.object(
            runner,
            "run_dts1_one_replica",
            side_effect=(self.outputs[0], self.outputs[0]),
        ):
            with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
                runner.run_dts1_b1_pie_r4_r8_extension()


if __name__ == "__main__":
    unittest.main()
