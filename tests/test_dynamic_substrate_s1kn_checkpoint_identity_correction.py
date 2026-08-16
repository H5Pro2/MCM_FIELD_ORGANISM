from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch
import unittest

import mcm_field_organism.dynamic_substrate_dts1_one_replica_orchestrator as runner


class DTS1S1KNCheckpointIdentityCorrectionTests(unittest.TestCase):
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
            cls.outputs = runner.run_dts1_s1kn_corrected_b1_pie_pair()

    def test_executes_only_r4_r8_with_exactly_eight_intervals(self) -> None:
        self.assertEqual({"materializer": 8, "adapter": 8}, self.call_counts)
        self.assertEqual(
            runner.S1_KH_TARGET_REPLICA_IDS,
            tuple(output.replica_id for output in self.outputs),
        )

    def test_every_checkpoint_matches_its_parent_replica(self) -> None:
        for output in self.outputs:
            self.assertEqual(
                (output.replica_id,) * 4,
                tuple(checkpoint.replica_id for checkpoint in output.checkpoints),
            )

    def test_corrected_provenance_digests_are_exact_new_and_distinct(self) -> None:
        corrected = tuple(output.output_digest for output in self.outputs)
        self.assertEqual(runner.S1_KN_CORRECTED_OUTPUT_DIGESTS, corrected)
        self.assertEqual(4, len(set(corrected + runner.S1_KH_TARGET_OUTPUT_DIGESTS)))

    def test_comparison_digest_and_numeric_content_are_preserved(self) -> None:
        self.assertEqual(
            (runner.S1_KF_EXEMPLAR_COMPARISON_DIGEST,) * 2,
            tuple(output.refinement_comparison_digest for output in self.outputs),
        )
        self.assertEqual(
            ((0.0,) * 8,) * 2,
            tuple(output.signed_components for output in self.outputs),
        )

    def test_output_validator_rejects_checkpoint_parent_mismatch(self) -> None:
        output = self.outputs[0]
        wrong = replace(
            output.checkpoints[0], replica_id=runner.S1_KC_EXEMPLAR_REPLICA_ID
        )
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            replace(output, checkpoints=(wrong,) + output.checkpoints[1:])

    def test_historical_s1kh_receipt_remains_unchanged(self) -> None:
        historical = runner.build_dts1_s1kh_implementation_receipt()
        self.assertEqual(
            runner.S1_KH_TARGET_OUTPUT_DIGESTS,
            historical.target_output_digests,
        )

    def test_s1kn_receipt_binds_correction_without_case_or_judgment(self) -> None:
        receipt = runner.build_dts1_s1kn_implementation_receipt()
        self.assertEqual(runner.S1_KN_CORRECTED_OUTPUT_DIGESTS, receipt.corrected_output_digests)
        self.assertEqual((2, 4, 8), (
            receipt.target_replica_count,
            receipt.interval_calls_per_target,
            receipt.total_new_interval_calls,
        ))
        self.assertTrue(receipt.numeric_comparison_content_preserved)
        self.assertFalse(receipt.historical_records_rewritten)
        self.assertEqual(0, receipt.b1_r2_or_b2_replicas_executed)
        self.assertFalse(receipt.case_output_composed)
        self.assertFalse(receipt.baseline_or_candidate_judgment_present)

    def test_corrected_pair_acceptance_is_fail_closed(self) -> None:
        with patch.object(
            runner,
            "run_dts1_b1_pie_r4_r8_extension",
            return_value=(self.outputs[0], self.outputs[0]),
        ):
            with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
                runner.run_dts1_s1kn_corrected_b1_pie_pair()

    def test_receipt_is_tamper_evident(self) -> None:
        receipt = runner.build_dts1_s1kn_implementation_receipt()
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            replace(receipt, total_new_interval_calls=9)


if __name__ == "__main__":
    unittest.main()
