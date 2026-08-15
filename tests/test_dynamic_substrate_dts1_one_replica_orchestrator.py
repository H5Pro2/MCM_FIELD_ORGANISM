from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch
import unittest

import mcm_field_organism.dynamic_substrate_dts1_one_replica_orchestrator as runner


class DTS1OneReplicaOrchestratorTests(unittest.TestCase):
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

        input_record = runner.DTS1OneReplicaRunnerInput(
            runner.S1_KC_RUNNER_INPUT_SCHEMA_ID,
            runner.S1_KC_EXEMPLAR_REPLICA_ID,
        )
        with patch.object(runner, "materialize_dts1_common_interval", counted_materializer), patch.object(
            runner, "advance_dts1_private_baseline", counted_adapter
        ):
            cls.first = runner.run_dts1_one_replica(input_record)
            cls.second = runner.run_dts1_one_replica(input_record)

    def test_two_repeats_use_exact_eight_calls(self) -> None:
        self.assertEqual({"materializer": 8, "adapter": 8}, self.call_counts)

    def test_two_repeats_are_bit_identical(self) -> None:
        self.assertEqual(self.first, self.second)
        self.assertEqual(self.first.output_digest, self.second.output_digest)
        self.assertEqual(
            self.first.refinement_comparison_digest,
            self.second.refinement_comparison_digest,
        )

    def test_s1kc_receipt_remains_historical_v1_evidence(self) -> None:
        receipt = runner.build_dts1_s1kc_implementation_receipt()
        self.assertEqual(
            (runner.S1_KC_EXEMPLAR_OUTPUT_DIGEST,) * 2,
            receipt.repeat_output_digests,
        )
        self.assertEqual((2, 4, 8), (
            receipt.technical_repeat_count,
            receipt.interval_calls_per_repeat,
            receipt.total_interval_calls,
        ))
        self.assertEqual((0, 0), (
            receipt.other_replicas_executed,
            receipt.complete_matrix_cases_executed,
        ))

    def test_s1kf_receipt_binds_two_dual_digest_r2_repeats(self) -> None:
        receipt = runner.build_dts1_s1kf_implementation_receipt()
        self.assertEqual(
            (self.first.output_digest, self.second.output_digest),
            receipt.repeat_output_digests,
        )
        self.assertEqual(
            (
                self.first.refinement_comparison_digest,
                self.second.refinement_comparison_digest,
            ),
            receipt.repeat_comparison_digests,
        )
        self.assertEqual((2, 4, 8), (
            receipt.technical_repeat_count,
            receipt.interval_calls_per_repeat,
            receipt.total_interval_calls,
        ))
        self.assertFalse(receipt.r4_r8_runner_implemented)
        self.assertEqual(0, receipt.r4_r8_replicas_executed)

    def test_v2_provenance_digest_differs_from_historical_v1(self) -> None:
        self.assertNotEqual(runner.S1_KC_EXEMPLAR_OUTPUT_DIGEST, self.first.output_digest)
        self.assertEqual(runner.S1_KF_EXEMPLAR_OUTPUT_DIGEST, self.first.output_digest)
        self.assertEqual(
            runner.S1_KF_EXEMPLAR_COMPARISON_DIGEST,
            self.first.refinement_comparison_digest,
        )

    def test_output_identity_is_exact_exemplar(self) -> None:
        self.assertEqual((
            runner.S1_KF_OUTPUT_SCHEMA_ID,
            runner.S1_KC_EXEMPLAR_REPLICA_ID,
            "B1",
            "P_IE_CAUSAL_TWO_SUBSTEP",
            2,
        ), (
            self.first.schema_id,
            self.first.replica_id,
            self.first.model_role,
            self.first.profile_block,
            self.first.refinement,
        ))

    def test_two_sequences_have_independent_fresh_starts(self) -> None:
        checkpoints = self.first.checkpoints
        self.assertEqual(("P_IE_F_HIGH", "P_IE_F_HIGH", "P_IE_R_HIGH", "P_IE_R_HIGH"), tuple(item.sequence_key for item in checkpoints))
        self.assertEqual((1, 2, 1, 2), tuple(item.ordinal for item in checkpoints))
        self.assertNotEqual(checkpoints[1].complete_field_digest, checkpoints[2].complete_field_digest)

    def test_checkpoints_are_complete_and_canonical(self) -> None:
        self.assertEqual(4, len(self.first.checkpoints))
        for checkpoint in self.first.checkpoints:
            self.assertEqual(("node-a", "node-b"), checkpoint.node_ids)
            self.assertEqual(2, len(checkpoint.activation))
            self.assertEqual(2, len(checkpoint.afterimage))
            self.assertEqual(64, len(checkpoint.complete_field_digest))
            self.assertEqual(64, len(checkpoint.private_state_digest))
            self.assertEqual(64, len(checkpoint.adapter_output_digest))

    def test_signed_components_follow_bound_left_minus_right_order(self) -> None:
        checkpoints = {(item.sequence_key, item.ordinal): item for item in self.first.checkpoints}
        expected = []
        for ordinal in (1, 2):
            left = checkpoints[("P_IE_F_HIGH", ordinal)]
            right = checkpoints[("P_IE_R_HIGH", ordinal)]
            for channel in ("activation", "afterimage"):
                left_values = getattr(left, channel)
                right_values = getattr(right, channel)
                expected.extend(left_values[index] - right_values[index] for index in range(2))
        self.assertEqual(tuple(expected), self.first.signed_components)

    def test_output_digest_covers_complete_output(self) -> None:
        self.assertEqual(self.first.output_digest, runner._digest(self.first._payload(include_digest=False)))
        self.assertEqual(self.first.output_digest, self.first.canonical_payload()["output_digest"])

    def test_comparison_digest_uses_exact_identity_neutral_payload(self) -> None:
        payload = self.first._comparison_payload()
        self.assertNotIn("replica_id", payload)
        self.assertNotIn("refinement", payload)
        self.assertNotIn("output_digest", payload)
        self.assertNotIn("refinement_comparison_digest", payload)
        self.assertTrue(all("replica_id" not in checkpoint for checkpoint in payload["checkpoints"]))
        self.assertIn("signed_components", payload)
        self.assertIn("adapter_diagnostics", payload)
        self.assertEqual(
            self.first.refinement_comparison_digest,
            runner._digest(payload),
        )

    def test_factory_roundtrips_fresh_field_and_private_state(self) -> None:
        field, state = runner._build_fresh_b1_two_node_state()
        self.assertEqual(0, field.layer.tick)
        self.assertIsNone(field.last_distribution)
        self.assertEqual("B1", state.model_role)

    def test_input_rejects_every_unregistered_value(self) -> None:
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            runner.DTS1OneReplicaRunnerInput("wrong", runner.S1_KC_EXEMPLAR_REPLICA_ID)
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            runner.DTS1OneReplicaRunnerInput(runner.S1_KC_RUNNER_INPUT_SCHEMA_ID, "B3:P_IE_CAUSAL_TWO_SUBSTEP:r2")

    def test_atomic_error_wraps_without_partial_output(self) -> None:
        input_record = runner.DTS1OneReplicaRunnerInput(
            runner.S1_KC_RUNNER_INPUT_SCHEMA_ID,
            runner.S1_KC_EXEMPLAR_REPLICA_ID,
        )
        with patch.object(runner, "_build_fresh_b1_two_node_state", side_effect=ValueError("closed")):
            with self.assertRaisesRegex(runner.DTS1OneReplicaOrchestratorError, "closed"):
                runner.run_dts1_one_replica(input_record)

    def test_output_is_tamper_evident(self) -> None:
        changed = (self.first.signed_components[0] + 1.0,) + self.first.signed_components[1:]
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            replace(self.first, signed_components=changed)
        with self.assertRaises(runner.DTS1OneReplicaOrchestratorError):
            replace(self.first, checkpoints=(object(),) * 4)


if __name__ == "__main__":
    unittest.main()
