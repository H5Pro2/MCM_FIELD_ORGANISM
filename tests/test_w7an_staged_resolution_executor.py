from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mcm_field_organism.w7an_staged_resolution_executor as staged


class W7ANStagedResolutionExecutorTests(unittest.TestCase):
    def _executor(self):
        return staged._start_w7an_staged_resolution(
            "r2",
            2,
            object(),
            object(),
            object(),
            SimpleNamespace(seven_path_plan_digest="plan"),
            object(),
            object(),
            SimpleNamespace(
                p0_zero_start_measurement_reference_digest="p0"
            ),
        )

    def test_six_phases_advance_once_and_finalize_only_at_end(self) -> None:
        executor = self._executor()
        paths = tuple(
            SimpleNamespace(cap_path_consumption_digest=f"path-{index}")
            for index in range(7)
        )
        cap_materialization = SimpleNamespace(path_results=paths)
        path_audit = SimpleNamespace(
            path_digests=tuple(
                item.cap_path_consumption_digest for item in paths
            )
        )
        branch_audit = SimpleNamespace()
        controls = SimpleNamespace()
        cap_result = SimpleNamespace(
            cap_seven_path_consumption_digest="cap-result"
        )
        measurements = tuple(
            SimpleNamespace(measurement_result_digest=f"measurement-{index}")
            for index in range(35)
        )
        measurement_materialization = SimpleNamespace(
            measurements=measurements
        )
        tasks = object()
        order_audit = SimpleNamespace(order_countercontrol_digest="order")
        passivity_audit = SimpleNamespace(
            observer_passivity_digest="passivity"
        )
        handoff = SimpleNamespace(measurement_handoff_digest="handoff")
        pair_container = SimpleNamespace(pair_container_digest="pairs")
        resolution_result = SimpleNamespace(
            resolution_result_digest="resolution"
        )
        witness_index = iter(range(102))

        def build_witness(*_args):
            return SimpleNamespace(
                witness_digest=f"witness-{next(witness_index)}"
            )

        def materialize_cap(*_args, **kwargs):
            observer = kwargs["_integration_observer"]
            for _ in range(67):
                observer(
                    SimpleNamespace(branch_kind="main"),
                    object(),
                    object(),
                )
            return cap_materialization

        def materialize_measurements(*_args, **kwargs):
            observer = kwargs["_integration_observer"]
            for _ in range(35):
                observer(object(), object(), object())
            return measurement_materialization

        with patch.object(
            staged,
            "_build_witness",
            side_effect=build_witness,
        ), patch.object(
            staged,
            "_materialize_w7ae_cap_paths",
            side_effect=materialize_cap,
        ) as cap_phase, patch.object(
            staged,
            "_audit_w7ae_path_order",
            return_value=path_audit,
        ) as path_phase, patch.object(
            staged,
            "_audit_w7ae_branch_order",
            return_value=branch_audit,
        ) as branch_phase, patch.object(
            staged,
            "_finalize_w7ae_countercontrols",
            return_value=controls,
        ), patch.object(
            staged,
            "_finalize_w7ae_cap_materialization",
            return_value=cap_result,
        ), patch.object(
            staged,
            "_materialize_w7ag_measurements",
            side_effect=materialize_measurements,
        ) as measurement_phase, patch.object(
            staged,
            "_measurement_tasks",
            return_value=tasks,
        ), patch.object(
            staged,
            "_audit_w7ag_measurement_order",
            return_value=order_audit,
        ) as order_phase, patch.object(
            staged,
            "_audit_w7ag_observer_passivity",
            return_value=passivity_audit,
        ) as passivity_phase, patch.object(
            staged,
            "_finalize_w7ag_measurement_audits",
            return_value=handoff,
        ), patch.object(
            staged,
            "_build_pair_container",
            return_value=pair_container,
        ), patch.object(
            staged._W7ANStagedResolutionExecutor,
            "_finalize_resolution_result",
            return_value=resolution_result,
        ):
            receipts = tuple(executor.advance() for _ in range(6))

        self.assertEqual(
            tuple(item[0] for item in staged._PHASES),
            tuple(item.phase_id for item in receipts),
        )
        self.assertEqual(
            (67, 67, 4, 35, 35, 1),
            tuple(item.integration_count for item in receipts),
        )
        self.assertEqual(
            (False, False, False, False, False, True),
            tuple(item.resolution_result_ready for item in receipts),
        )
        self.assertIs(executor.resolution_result, resolution_result)
        self.assertIsNone(executor.next_phase_id)
        self.assertEqual(67, len(executor.production_witnesses))
        self.assertEqual(35, len(executor.measurement_witnesses))
        for mocked in (
            cap_phase,
            path_phase,
            branch_phase,
            measurement_phase,
            order_phase,
            passivity_phase,
        ):
            self.assertEqual(1, mocked.call_count)
        with self.assertRaisesRegex(
            staged.W7ANStagedResolutionExecutorError,
            "already complete",
        ):
            executor.advance()

    def test_failed_phase_does_not_advance_or_create_receipt(self) -> None:
        executor = self._executor()
        with patch.object(
            staged,
            "_materialize_w7ae_cap_paths",
            side_effect=RuntimeError("stop"),
        ):
            with self.assertRaisesRegex(RuntimeError, "stop"):
                executor.advance()
        self.assertEqual(0, executor.completed_phase_count)
        self.assertEqual([], executor.receipts)
        self.assertEqual("cap-canonical", executor.next_phase_id)
        self.assertIsNone(executor.resolution_result)

    def test_missing_witnesses_stop_the_first_phase(self) -> None:
        executor = self._executor()
        with patch.object(
            staged,
            "_materialize_w7ae_cap_paths",
            return_value=SimpleNamespace(path_results=()),
        ):
            with self.assertRaisesRegex(
                staged.W7ANStagedResolutionExecutorError,
                "67 witnesses",
            ):
                executor.advance()
        self.assertEqual(0, executor.completed_phase_count)
        self.assertIsNone(executor.cap_materialization)

    def test_invalid_resolution_role_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            staged.W7ANStagedResolutionExecutorError,
            "role is invalid",
        ):
            staged._start_w7an_staged_resolution(
                "r3",
                3,
                *(object() for _ in range(7)),
            )

    def test_executor_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "_start_w7an_staged_resolution")
        )
        self.assertFalse(hasattr(current_api, "W7ANPhaseReceipt"))


if __name__ == "__main__":
    unittest.main()
