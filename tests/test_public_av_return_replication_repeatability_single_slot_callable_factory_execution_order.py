from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderError,
    execute_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order,
    order_public_av_return_replication_repeatability_single_slot_callable_factory_execution,
    public_av_return_replication_repeatability_single_slot_callable_factory_execution_order_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight,
)
from tests.test_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.callable_factory_execution_preflight_acceptance = (
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight(
                self.callable_factory_step_execution_preflight
            )
        )

    def test_derives_one_future_callable_execution_step(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_execution(
            self.callable_factory_execution_preflight_acceptance
        )
        self.assertTrue(order.positive_execution_preflight_acceptance_bound)
        self.assertTrue(order.exactly_one_future_callable_execution_step)
        self.assertTrue(order.callable_execution_step_one_time)
        self.assertTrue(order.callable_execution_step_unexecuted)
        self.assertTrue(order.callable_factory_execution_order_complete)
        self.assertEqual(order.future_callable_execution_step.role, "callable_factory")

    def test_binds_callable_factory_constructor_and_object_identities(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_execution(
            self.callable_factory_execution_preflight_acceptance
        )
        self.assertTrue(order.callable_factory_identity_bound)
        self.assertTrue(order.callable_constructor_identity_bound)
        self.assertTrue(order.future_callable_object_identity_bound)
        self.assertEqual(order.future_callable_execution_step.factory_identity_id, order.callable_factory_identity_id)
        self.assertEqual(
            order.future_callable_execution_step.constructor_identity_id,
            order.callable_constructor_identity_id,
        )
        self.assertEqual(order.future_callable_execution_step.future_object_id, order.future_callable_object_id)

    def test_gate_factory_step_remains_unselected_untouched_and_unexecuted(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_execution(
            self.callable_factory_execution_preflight_acceptance
        )
        self.assertTrue(order.gate_factory_step_unselected)
        self.assertTrue(order.gate_factory_step_untouched)
        self.assertTrue(order.gate_factory_step_still_unexecuted)
        self.assertEqual(order.untouched_gate_factory_step.role, "gate_factory")
        self.assertFalse(order.untouched_gate_factory_step.executed)

    def test_rejects_changed_acceptance_or_gate_step_as_callable_execution(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.callable_factory_execution_preflight_acceptance, callable_factory_called=True)
            order_public_av_return_replication_repeatability_single_slot_callable_factory_execution(changed)
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_execution(
            self.callable_factory_execution_preflight_acceptance
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderError):
            replace(
                order,
                future_callable_execution_step=order.untouched_gate_factory_step,
            )

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_execution(
            self.callable_factory_execution_preflight_acceptance
        )
        for field in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_factory_called",
            "gate_factory_called", "callable_object_created", "gate_object_created",
            "constructor_invoked", "binding_performed", "scheduler_available",
            "media_decode_allowed", "receptor_feed_allowed", "start_release_granted",
            "repeatability_run_allowed", "repeat_run_started", "memory_claim_allowed",
            "meaning_claim_allowed", "organization_claim_allowed", "ai_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderError):
                replace(order, **{field: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderError):
            execute_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order(order)

    def test_json_contains_future_step_but_no_references_instances_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_execution_order_to_jsonable(
            order_public_av_return_replication_repeatability_single_slot_callable_factory_execution(
                self.callable_factory_execution_preflight_acceptance
            )
        )
        self.assertEqual(payload["future_callable_execution_step"]["role"], "callable_factory")
        self.assertEqual(payload["untouched_gate_factory_step"]["role"], "gate_factory")
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
