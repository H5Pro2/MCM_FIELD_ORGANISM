from __future__ import annotations

import inspect
import unittest
from unittest.mock import patch

import mcm_field_organism.w7ae_cap_seven_path_consumer as ae
import mcm_field_organism.w7ag_passive_cap_measurement_handoff as ag


class W7ANStagedPrivateBoundaryTests(unittest.TestCase):
    def test_w7ae_public_wrapper_materializes_then_audits(self) -> None:
        inputs = tuple(object() for _ in range(6))
        materialization = object()
        result = object()
        observer = object()
        with patch.object(
            ae,
            "_materialize_w7ae_cap_paths",
            return_value=materialization,
        ) as materialize, patch.object(
            ae,
            "_audit_w7ae_cap_materialization",
            return_value=result,
        ) as audit:
            actual = ae.consume_w7ae_cap_seven_path_plan(
                *inputs,
                _refinement=2,
                _integration_observer=observer,
            )
        self.assertIs(actual, result)
        materialize.assert_called_once_with(
            *inputs,
            _refinement=2,
            _integration_observer=observer,
        )
        audit.assert_called_once_with(*inputs, materialization)

    def test_w7ag_public_wrapper_materializes_then_audits(self) -> None:
        inputs = tuple(object() for _ in range(5))
        materialization = object()
        result = object()
        observer = object()
        with patch.object(
            ag,
            "_materialize_w7ag_measurements",
            return_value=materialization,
        ) as materialize, patch.object(
            ag,
            "_audit_w7ag_measurements",
            return_value=result,
        ) as audit:
            actual = ag.compose_w7ag_passive_cap_measurement_handoff(
                *inputs,
                _refinement=4,
                _integration_observer=observer,
            )
        self.assertIs(actual, result)
        materialize.assert_called_once_with(
            *inputs,
            _refinement=4,
            _integration_observer=observer,
        )
        audit.assert_called_once_with(*inputs, materialization)

    def test_public_defaults_remain_r1_and_unobserved(self) -> None:
        for function in (
            ae.consume_w7ae_cap_seven_path_plan,
            ag.compose_w7ag_passive_cap_measurement_handoff,
        ):
            parameters = inspect.signature(function).parameters
            self.assertEqual(1, parameters["_refinement"].default)
            self.assertIsNone(parameters["_integration_observer"].default)
            self.assertEqual(
                inspect.Parameter.KEYWORD_ONLY,
                parameters["_refinement"].kind,
            )

    def test_materialization_types_reject_empty_inventories(self) -> None:
        with self.assertRaises(ae.W7AECAPSevenPathConsumerError):
            ae._W7AECAPPathMaterialization(
                "plan",
                "p0",
                "observer",
                "field",
                1,
                (),
            )
        with self.assertRaises(ag.W7AGPassiveCAPMeasurementError):
            ag._W7AGMeasurementMaterialization("plan", "cap", 1, ())

    def test_audits_reject_unbound_materializations_first(self) -> None:
        with self.assertRaisesRegex(
            ae.W7AECAPSevenPathConsumerError,
            "requires a path materialization",
        ):
            ae._audit_w7ae_cap_materialization(
                *(object() for _ in range(6)),
                object(),
            )
        with self.assertRaisesRegex(
            ag.W7AGPassiveCAPMeasurementError,
            "requires a materialization",
        ):
            ag._audit_w7ag_measurements(
                *(object() for _ in range(5)),
                object(),
            )

    def test_private_stages_are_not_current_api_exports(self) -> None:
        from mcm_field_organism import current_api

        for name in (
            "_materialize_w7ae_cap_paths",
            "_audit_w7ae_cap_materialization",
            "_materialize_w7ag_measurements",
            "_audit_w7ag_measurements",
        ):
            self.assertFalse(hasattr(current_api, name))


if __name__ == "__main__":
    unittest.main()
