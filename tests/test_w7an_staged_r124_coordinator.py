from __future__ import annotations

import inspect
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mcm_field_organism.w7an_staged_r124_coordinator as coordinator


class _FakeResolutionExecutor:
    def __init__(self, resolution_id, p0_references, digest, fail_at=None):
        self.resolution_id = resolution_id
        self.p0_references = p0_references
        self.digest = digest
        self.fail_at = fail_at
        self.phase = 0
        self.resolution_result = None

    def advance(self):
        if self.phase == self.fail_at:
            raise coordinator.W7ANStagedResolutionExecutorError("child stop")
        self.phase += 1
        ready = self.phase == 6
        if ready:
            self.resolution_result = SimpleNamespace(
                resolution_result_digest=self.digest
            )
        return SimpleNamespace(
            phase_id=f"phase-{self.phase}",
            phase_receipt_digest=f"receipt-{self.resolution_id}-{self.phase}",
            resolution_result_ready=ready,
        )


class W7ANStagedR124CoordinatorTests(unittest.TestCase):
    def _inputs(self):
        p0 = SimpleNamespace(
            p0_zero_start_measurement_reference_digest=(
                coordinator._P0_REFERENCE_DIGEST
            )
        )
        return (*(object() for _ in range(6)), p0)

    def test_full_static_coordination_uses_bound_role_order(self) -> None:
        inputs = self._inputs()
        p0 = inputs[-1]
        digests = {
            **coordinator._CANONICAL_STAGED_RESOLUTION_DIGESTS,
        }
        starts = []

        def start(resolution_id, refinement, *child_inputs):
            starts.append((resolution_id, refinement, child_inputs[-1]))
            return _FakeResolutionExecutor(
                resolution_id,
                child_inputs[-1],
                digests[resolution_id],
            )

        with patch.object(
            coordinator,
            "_start_w7an_staged_resolution",
            side_effect=start,
        ):
            state = coordinator._start_w7an_staged_r124_coordinator(*inputs)
            receipts = tuple(state.advance() for _ in range(36))

        self.assertTrue(state.completed)
        self.assertEqual(36, state.completed_phase_count)
        self.assertEqual(
            coordinator._ROLES,
            tuple(
                (receipt.pass_id, receipt.resolution_id, receipt.refinement)
                for receipt in receipts[::6]
            ),
        )
        self.assertEqual(
            (6, 12, 18, 24, 30, 36),
            tuple(
                item.completed_phase_count
                for item in receipts
                if item.resolution_completed
            ),
        )
        self.assertTrue(receipts[-1].coordinator_completed)
        self.assertTrue(
            all(child_p0 is p0 for _, _, child_p0 in starts)
        )
        self.assertEqual({"r1", "r2", "r4"}, set(state.primary_results))
        self.assertEqual({"r1", "r2", "r4"}, set(state.repeat_results))
        with self.assertRaisesRegex(
            coordinator.W7ANStagedR124CoordinatorError,
            "already complete",
        ):
            state.advance()

    def test_child_failure_does_not_advance_global_phase(self) -> None:
        inputs = self._inputs()
        child = _FakeResolutionExecutor(
            "r1",
            inputs[-1],
            coordinator._CANONICAL_STAGED_R1_DIGEST,
            fail_at=0,
        )
        with patch.object(
            coordinator,
            "_start_w7an_staged_resolution",
            return_value=child,
        ):
            state = coordinator._start_w7an_staged_r124_coordinator(*inputs)
            with self.assertRaisesRegex(
                coordinator.W7ANStagedResolutionExecutorError,
                "child stop",
            ):
                state.advance()
        self.assertEqual(0, state.completed_phase_count)
        self.assertEqual([], state.receipts)
        self.assertEqual(coordinator._ROLES[0], state.next_role)

    def test_reverse_repeat_mismatch_stops_terminally(self) -> None:
        inputs = self._inputs()
        starts = 0

        def start(resolution_id, refinement, *child_inputs):
            nonlocal starts
            starts += 1
            digest = {
                **coordinator._CANONICAL_STAGED_RESOLUTION_DIGESTS,
            }[resolution_id]
            if starts == 4:
                digest = "changed-r4"
            return _FakeResolutionExecutor(
                resolution_id,
                child_inputs[-1],
                digest,
            )

        with patch.object(
            coordinator,
            "_start_w7an_staged_resolution",
            side_effect=start,
        ):
            state = coordinator._start_w7an_staged_r124_coordinator(*inputs)
            for _ in range(23):
                state.advance()
            with self.assertRaisesRegex(
                coordinator.W7ANStagedR124CoordinatorError,
                "differs from its primary",
            ):
                state.advance()
            with self.assertRaisesRegex(
                coordinator.W7ANStagedR124CoordinatorError,
                "differs from its primary",
            ):
                state.advance()
        self.assertFalse(state.completed)
        self.assertIsNotNone(state.terminal_error)

    def test_noncanonical_p0_reference_is_rejected_before_start(self) -> None:
        inputs = (*self._inputs()[:-1], SimpleNamespace(
            p0_zero_start_measurement_reference_digest="changed"
        ))
        with self.assertRaisesRegex(
            coordinator.W7ANStagedR124CoordinatorError,
            "canonical shared P0",
        ):
            coordinator._start_w7an_staged_r124_coordinator(*inputs)

    def test_completed_coordination_delegates_to_pure_finalizer_once(self) -> None:
        inputs = self._inputs()
        state = coordinator._start_w7an_staged_r124_coordinator(*inputs)
        state.role_index = len(coordinator._ROLES)
        state.completed_phase_count = coordinator._TOTAL_PHASES
        state.receipts = [object()] * coordinator._TOTAL_PHASES
        primary = {
            resolution_id: SimpleNamespace(
                resolution_id=resolution_id,
                resolution_result_digest=digest,
                p0_references=inputs[-1],
            )
            for resolution_id, digest in (
                tuple(coordinator._CANONICAL_STAGED_RESOLUTION_DIGESTS.items())
            )
        }
        state.primary_results = primary
        state.repeat_results = {
            resolution_id: SimpleNamespace(
                resolution_result_digest=item.resolution_result_digest
            )
            for resolution_id, item in primary.items()
        }
        container = SimpleNamespace(
            resolution_container_digest=(
                coordinator._CANONICAL_STAGED_CONTAINER_DIGEST
            )
        )
        canonical = tuple(object() for _ in range(3))
        with patch.object(
            coordinator,
            "_finalize_w7an_r124_resolution_results",
            return_value=container,
        ) as finalize:
            actual = coordinator._finalize_w7an_staged_r124_coordinator(
                state,
                *canonical,
            )
        self.assertIs(actual, container)
        self.assertIs(state.resolution_container, container)
        finalize.assert_called_once_with(
            state.plan,
            inputs[-1],
            *canonical,
            (primary["r1"], primary["r2"], primary["r4"]),
        )
        with self.assertRaisesRegex(
            coordinator.W7ANStagedR124CoordinatorError,
            "already finalized",
        ):
            coordinator._finalize_w7an_staged_r124_coordinator(
                state,
                *canonical,
            )

    def test_incomplete_coordination_cannot_finalize(self) -> None:
        state = coordinator._start_w7an_staged_r124_coordinator(
            *self._inputs()
        )
        with self.assertRaisesRegex(
            coordinator.W7ANStagedR124CoordinatorError,
            "all 36 verified phases",
        ):
            coordinator._finalize_w7an_staged_r124_coordinator(
                state,
                *(object() for _ in range(3)),
            )

    def test_global_finalizers_do_not_execute_or_materialize(self) -> None:
        coordinator_source = inspect.getsource(
            coordinator._finalize_w7an_staged_r124_coordinator
        )
        container_source = inspect.getsource(
            coordinator._finalize_w7an_r124_resolution_results
        )
        self.assertNotIn(".advance(", coordinator_source)
        self.assertNotIn("_start_w7an_staged_resolution", coordinator_source)
        self.assertNotIn("_build_resolution(", container_source)
        self.assertNotIn("_materialize_", container_source)

    def test_coordinator_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "_start_w7an_staged_r124_coordinator")
        )
        self.assertFalse(
            hasattr(current_api, "W7ANCoordinatorPhaseReceipt")
        )
        self.assertFalse(
            hasattr(current_api, "_finalize_w7an_staged_r124_coordinator")
        )


if __name__ == "__main__":
    unittest.main()
