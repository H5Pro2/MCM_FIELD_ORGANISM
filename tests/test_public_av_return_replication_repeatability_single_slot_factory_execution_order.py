from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_order_execution_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError,
    execute_public_av_return_replication_repeatability_single_slot_factory_execution_order,
    order_public_av_return_replication_repeatability_single_slot_factory_execution,
    public_av_return_replication_repeatability_single_slot_factory_execution_order_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_factory_order_execution_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.execution_acceptance = accept_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight(
            self.execution_preflight
        )

    def test_derives_two_ordered_one_time_future_steps(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_factory_execution(
            self.execution_acceptance
        )
        self.assertTrue(order.positive_execution_acceptance_bound)
        self.assertTrue(order.exactly_two_future_execution_steps_derived)
        self.assertTrue(order.callable_factory_step_first)
        self.assertTrue(order.gate_factory_step_second)
        self.assertTrue(order.execution_steps_one_time)
        self.assertTrue(order.execution_steps_unexecuted)
        self.assertEqual(order.future_execution_steps[0].role, "callable_factory")
        self.assertEqual(order.future_execution_steps[1].role, "gate_factory")

    def test_preserves_execution_acceptance_chain_identities(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_factory_execution(
            self.execution_acceptance
        )
        for role in (
            "selected_repeat_index", "execution_preflight_id", "factory_order_acceptance_id",
            "factory_order_id", "factory_call_acceptance_id", "factory_call_preflight_id",
            "factory_acceptance_id", "factory_binding_id", "construction_acceptance_id",
            "construction_id", "object_reservation_id", "candidate_id", "logical_callable_id",
            "logical_gate_id", "reserved_executor_id", "future_callable_object_id",
            "future_gate_object_id", "callable_constructor_id", "gate_constructor_id",
            "future_callable_factory_id", "future_gate_factory_id",
            "future_callable_factory_order_id", "future_gate_factory_order_id", "source_id",
        ):
            self.assertEqual(getattr(self.execution_acceptance, role), getattr(order, role))

    def test_rejects_changed_execution_acceptance_state(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.execution_acceptance, callable_object_created=True)
            order_public_av_return_replication_repeatability_single_slot_factory_execution(changed)

    def test_rejects_reordered_future_steps(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_factory_execution(
            self.execution_acceptance
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError):
            replace(order, future_execution_steps=tuple(reversed(order.future_execution_steps)))

    def test_references_calls_objects_binding_media_receptors_runs_and_claims_remain_locked(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_factory_execution(
            self.execution_acceptance
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called",
            "callable_factory_called", "gate_factory_called", "callable_object_created",
            "gate_object_created", "constructor_invoked", "binding_performed",
            "media_decode_allowed", "receptor_feed_allowed", "start_release_granted",
            "repeatability_run_allowed", "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError):
                replace(order, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderError):
            execute_public_av_return_replication_repeatability_single_slot_factory_execution_order(order)

    def test_json_contains_no_references_instances_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_factory_execution_order_to_jsonable(
            order_public_av_return_replication_repeatability_single_slot_factory_execution(
                self.execution_acceptance
            )
        )
        self.assertTrue(payload["factory_execution_order_complete"])
        self.assertEqual(len(payload["future_execution_steps"]), 2)
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
