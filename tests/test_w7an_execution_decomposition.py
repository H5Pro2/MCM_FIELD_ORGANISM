from __future__ import annotations

import unittest

from mcm_field_organism.w7an_execution_decomposition import (
    W7ANExecutionBatch,
    W7ANExecutionDecompositionError,
    build_w7an_execution_decomposition,
)


class W7ANExecutionDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = build_w7an_execution_decomposition()

    def test_primary_and_reverse_repeat_are_separate(self) -> None:
        self.assertEqual(36, len(self.plan.batches))
        self.assertEqual(
            ("r1", "r2", "r4"),
            tuple(self.plan.batches[index].resolution_id for index in (0, 6, 12)),
        )
        self.assertEqual(
            ("r4", "r2", "r1"),
            tuple(self.plan.batches[index].resolution_id for index in (18, 24, 30)),
        )

    def test_inventory_exposes_full_cost(self) -> None:
        self.assertEqual(627, self.plan.primary_integration_count)
        self.assertEqual(627, self.plan.repeat_integration_count)
        self.assertEqual(1254, self.plan.total_integration_count)
        self.assertEqual(948, self.plan.validation_integration_count)

    def test_only_primary_canonical_work_retains_witnesses(self) -> None:
        self.assertEqual(306, self.plan.retained_witness_count)
        self.assertEqual(
            306,
            sum(item.retained_witness_count for item in self.plan.batches),
        )

    def test_each_batch_is_bounded(self) -> None:
        self.assertEqual(67, self.plan.maximum_batch_integration_count)
        self.assertTrue(
            all(item.integration_count <= 67 for item in self.plan.batches)
        )

    def test_phase_order_respects_cap_before_measurement_dependency(self) -> None:
        self.assertEqual(
            (
                "cap-canonical",
                "cap-path-order-control",
                "cap-branch-order-control",
                "measurement-canonical",
                "measurement-order-control",
                "observer-passivity-control",
            ),
            tuple(item.phase for item in self.plan.batches[:6]),
        )

    def test_plan_is_static_and_does_not_claim_completion(self) -> None:
        self.assertFalse(self.plan.runtime_executed)
        self.assertFalse(self.plan.container_completed)

    def test_invalid_batch_binding_is_rejected(self) -> None:
        source = self.plan.batches[0]
        with self.assertRaises(W7ANExecutionDecompositionError):
            W7ANExecutionBatch(
                source.batch_id,
                source.pass_id,
                source.resolution_id,
                source.refinement,
                source.phase,
                source.integration_count - 1,
                source.retained_witness_count,
                source.batch_digest,
            )

    def test_decomposition_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "build_w7an_execution_decomposition"))


if __name__ == "__main__":
    unittest.main()
