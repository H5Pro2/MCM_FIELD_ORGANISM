from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderError,
    execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order,
    order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight,
)
from tools.audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight import (
    build_callable_factory_call_execution_release_preflight,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.release_preflight_acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight(
            build_callable_factory_call_execution_release_preflight(1)
        )

    def test_derives_one_future_unconsumed_release_step_without_release(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
            self.release_preflight_acceptance
        )
        self.assertTrue(order.positive_release_preflight_acceptance_bound)
        self.assertTrue(order.exactly_one_future_release_step_derived)
        self.assertTrue(order.release_step_one_time)
        self.assertTrue(order.release_step_unconsumed)
        self.assertFalse(order.actual_release_granted)
        self.assertTrue(order.release_order_complete)

    def test_preserves_callable_identity_and_untouched_gate(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
            self.release_preflight_acceptance
        )
        self.assertTrue(order.callable_factory_identity_bound)
        self.assertTrue(order.callable_constructor_identity_bound)
        self.assertTrue(order.future_callable_object_identity_bound)
        self.assertTrue(order.gate_factory_step_unselected)
        self.assertTrue(order.gate_factory_step_untouched)
        self.assertTrue(order.gate_factory_step_still_unexecuted)
        preflight = order.release_preflight_acceptance.release_preflight
        self.assertEqual(preflight.release_candidate_step.role, "callable_factory")
        self.assertEqual(preflight.untouched_gate_factory_step.role, "gate_factory")

    def test_rejects_consumed_acceptance_and_all_execution_surfaces(self) -> None:
        with self.assertRaises(Exception):
            order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
                replace(self.release_preflight_acceptance, actual_release_granted=True)
            )
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
            self.release_preflight_acceptance
        )
        for field in (
            "actual_release_granted", "callable_factory_reference_stored",
            "gate_factory_reference_stored", "callable_reference_stored",
            "factory_function_called", "callable_factory_called", "gate_factory_called",
            "callable_object_created", "gate_object_created", "constructor_invoked",
            "binding_performed", "scheduler_available", "media_decode_allowed",
            "receptor_feed_allowed", "start_release_granted", "repeatability_run_allowed",
            "repeat_run_started", "memory_claim_allowed", "meaning_claim_allowed",
            "organization_claim_allowed", "ai_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderError):
                replace(order, **{field: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderError):
            execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order(order)

    def test_json_contains_contract_data_without_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order_to_jsonable(
            order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
                self.release_preflight_acceptance
            )
        )
        self.assertFalse(payload["actual_release_granted"])
        self.assertEqual(payload["release_preflight_acceptance"]["release_preflight"]["release_candidate_step"]["role"], "callable_factory")
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
