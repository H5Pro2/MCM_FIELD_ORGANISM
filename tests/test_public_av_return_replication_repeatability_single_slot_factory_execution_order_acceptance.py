from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    order_public_av_return_replication_repeatability_single_slot_factory_execution,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_execution_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_factory_execution_order,
    execute_public_av_return_replication_repeatability_single_slot_accepted_factory_execution_order,
    public_av_return_replication_repeatability_single_slot_factory_execution_order_acceptance_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderTests
):
    def setUp(self) -> None:
        super().setUp()
        self.factory_execution_order = order_public_av_return_replication_repeatability_single_slot_factory_execution(
            self.execution_acceptance
        )

    def test_accepts_two_ordered_one_time_unexecuted_steps_and_identity_chain(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_execution_order(
            self.factory_execution_order
        )
        self.assertTrue(accepted.positive_factory_execution_order_accepted)
        self.assertTrue(accepted.exactly_two_future_steps_accepted)
        self.assertTrue(accepted.execution_steps_one_time_accepted)
        self.assertTrue(accepted.execution_steps_unexecuted_accepted)
        self.assertTrue(accepted.identity_chain_accepted)
        self.assertTrue(accepted.factory_execution_order_acceptance_complete)

    def test_preserves_step_order_and_step_identity_bindings(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_execution_order(
            self.factory_execution_order
        )
        steps = accepted.accepted_future_execution_steps
        self.assertEqual((steps[0].role, steps[1].role), ("callable_factory", "gate_factory"))
        self.assertEqual(steps[0].future_object_id, accepted.future_callable_object_id)
        self.assertEqual(steps[1].future_object_id, accepted.future_gate_object_id)

    def test_rejects_changed_order_state_or_reordered_steps(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.factory_execution_order, callable_factory_called=True)
            accept_public_av_return_replication_repeatability_single_slot_factory_execution_order(changed)
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_execution_order(
            self.factory_execution_order
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError):
            replace(accepted, accepted_future_execution_steps=tuple(reversed(accepted.accepted_future_execution_steps)))

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_execution_order(
            self.factory_execution_order
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_factory_called",
            "gate_factory_called", "callable_object_created", "gate_object_created",
            "constructor_invoked", "binding_performed", "media_decode_allowed",
            "receptor_feed_allowed", "start_release_granted", "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError):
                replace(accepted, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceError):
            execute_public_av_return_replication_repeatability_single_slot_accepted_factory_execution_order(accepted)

    def test_json_contains_two_steps_but_no_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_factory_execution_order_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_factory_execution_order(
                self.factory_execution_order
            )
        )
        self.assertEqual(len(payload["accepted_future_execution_steps"]), 2)
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
