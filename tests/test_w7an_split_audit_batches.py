from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mcm_field_organism.w7ae_cap_seven_path_consumer as ae
import mcm_field_organism.w7ag_passive_cap_measurement_handoff as ag


class W7ANSplitAuditBatchTests(unittest.TestCase):
    def test_w7ae_countercontrol_wrapper_runs_both_batches(self) -> None:
        inputs = tuple(object() for _ in range(4))
        path_audit = object()
        branch_audit = object()
        result = object()
        with patch.object(
            ae,
            "_audit_w7ae_path_order",
            return_value=path_audit,
        ) as path_order, patch.object(
            ae,
            "_audit_w7ae_branch_order",
            return_value=branch_audit,
        ) as branch_order, patch.object(
            ae,
            "_finalize_w7ae_countercontrols",
            return_value=result,
        ) as finalize:
            actual = ae._countercontrols(*inputs, _refinement=4)
        self.assertIs(actual, result)
        path_order.assert_called_once_with(*inputs, _refinement=4)
        branch_order.assert_called_once_with(*inputs, _refinement=4)
        finalize.assert_called_once_with(inputs[3], path_audit, branch_audit)

    def test_w7ae_finalizer_rejects_cross_resolution_audits(self) -> None:
        digests = tuple(f"path-{index}" for index in range(7))
        paths = tuple(
            SimpleNamespace(cap_path_consumption_digest=item)
            for item in digests
        )
        path_audit = ae._W7AECAPPathOrderAudit(digests, 1)
        branch_audit = ae._W7AECAPBranchOrderAudit("main", "probe", 2)
        with self.assertRaisesRegex(
            ae.W7AECAPSevenPathConsumerError,
            "split countercontrol audits differ",
        ):
            ae._finalize_w7ae_countercontrols(
                paths,
                path_audit,
                branch_audit,
            )

    def test_w7ag_audit_wrapper_runs_35_and_1_batches(self) -> None:
        measurements = tuple(
            SimpleNamespace(path_id=path_id, checkpoint=checkpoint)
            for path_id in ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
            for checkpoint in range(5)
        )
        materialization = ag._W7AGMeasurementMaterialization(
            "plan",
            "cap",
            2,
            measurements,
        )
        inputs = tuple(object() for _ in range(5))
        tasks = object()
        order_audit = object()
        passivity_audit = object()
        result = object()
        with patch.object(ag, "_validate_w7ag_inputs"), patch.object(
            ag,
            "_measurement_tasks",
            return_value=tasks,
        ), patch.object(
            ag,
            "_audit_w7ag_measurement_order",
            return_value=order_audit,
        ) as order, patch.object(
            ag,
            "_audit_w7ag_observer_passivity",
            return_value=passivity_audit,
        ) as passivity, patch.object(
            ag,
            "_finalize_w7ag_measurement_audits",
            return_value=result,
        ) as finalize:
            actual = ag._audit_w7ag_measurements(*inputs, materialization)
        self.assertIs(actual, result)
        order.assert_called_once_with(
            inputs[0],
            inputs[2],
            tasks,
            materialization,
        )
        passivity.assert_called_once_with(
            inputs[0],
            inputs[2],
            inputs[3],
            materialization,
        )
        finalize.assert_called_once_with(
            inputs[3],
            inputs[4],
            materialization,
            order_audit,
            passivity_audit,
        )

    def test_w7ag_finalizer_rejects_cross_resolution_audits(self) -> None:
        measurements = tuple(
            SimpleNamespace(path_id=path_id, checkpoint=checkpoint)
            for path_id in ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
            for checkpoint in range(5)
        )
        materialization = ag._W7AGMeasurementMaterialization(
            "plan",
            "cap",
            1,
            measurements,
        )
        order_audit = ag._W7AGMeasurementOrderAudit("order", 1)
        passivity_audit = ag._W7AGObserverPassivityAudit("passivity", 4)
        with self.assertRaisesRegex(
            ag.W7AGPassiveCAPMeasurementError,
            "split measurement audits differ",
        ):
            ag._finalize_w7ag_measurement_audits(
                SimpleNamespace(seven_path_plan_digest="plan"),
                SimpleNamespace(cap_seven_path_consumption_digest="cap"),
                materialization,
                order_audit,
                passivity_audit,
            )

    def test_split_audits_are_not_public_exports(self) -> None:
        from mcm_field_organism import current_api

        for name in (
            "_audit_w7ae_path_order",
            "_audit_w7ae_branch_order",
            "_audit_w7ag_measurement_order",
            "_audit_w7ag_observer_passivity",
        ):
            self.assertFalse(hasattr(current_api, name))


if __name__ == "__main__":
    unittest.main()
