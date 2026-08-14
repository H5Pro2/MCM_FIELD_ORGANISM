from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_step_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderError,
    execute_public_av_return_replication_repeatability_single_slot_callable_factory_step_order,
    order_public_av_return_replication_repeatability_single_slot_callable_factory_step,
    public_av_return_replication_repeatability_single_slot_callable_factory_step_order_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_first_factory_step_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight,
)
from tests.test_public_av_return_replication_repeatability_single_slot_first_factory_step_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.first_step_acceptance = (
            accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(
                self.first_step_preflight
            )
        )

    def test_derives_one_future_one_time_callable_factory_order(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_step(
            self.first_step_acceptance
        )
        self.assertTrue(order.positive_first_step_acceptance_bound)
        self.assertTrue(order.exactly_one_callable_factory_order_derived)
        self.assertTrue(order.callable_factory_order_one_time)
        self.assertTrue(order.callable_factory_order_unexecuted)
        self.assertTrue(order.callable_factory_step_order_complete)

    def test_binds_callable_factory_constructor_and_future_object_identities(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_step(
            self.first_step_acceptance
        )
        self.assertTrue(order.callable_factory_identity_bound)
        self.assertTrue(order.callable_constructor_identity_bound)
        self.assertTrue(order.future_callable_object_identity_bound)
        self.assertEqual(order.callable_factory_identity_id, order.selected_factory_step.factory_identity_id)
        self.assertEqual(order.callable_constructor_identity_id, order.selected_factory_step.constructor_identity_id)
        self.assertEqual(order.future_callable_object_id, order.selected_factory_step.future_object_id)

    def test_gate_factory_step_remains_unselected_untouched_and_unexecuted(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_step(
            self.first_step_acceptance
        )
        self.assertTrue(order.gate_factory_step_unselected)
        self.assertTrue(order.gate_factory_step_untouched)
        self.assertTrue(order.gate_factory_step_still_unexecuted)
        self.assertEqual(order.untouched_gate_factory_step.role, "gate_factory")
        self.assertFalse(order.untouched_gate_factory_step.executed)

    def test_rejects_changed_acceptance_or_swapped_steps(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.first_step_acceptance, callable_factory_called=True)
            order_public_av_return_replication_repeatability_single_slot_callable_factory_step(changed)
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_step(
            self.first_step_acceptance
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderError):
            replace(
                order,
                selected_factory_step=order.untouched_gate_factory_step,
                untouched_gate_factory_step=order.selected_factory_step,
            )

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_callable_factory_step(
            self.first_step_acceptance
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_factory_called",
            "gate_factory_called", "callable_object_created", "gate_object_created",
            "constructor_invoked", "binding_performed", "media_decode_allowed",
            "receptor_feed_allowed", "start_release_granted", "repeatability_run_allowed",
            "memory_claim_allowed", "meaning_claim_allowed", "organization_claim_allowed",
            "ai_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderError):
                replace(order, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderError):
            execute_public_av_return_replication_repeatability_single_slot_callable_factory_step_order(order)

    def test_json_contains_order_identity_but_no_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_step_order_to_jsonable(
            order_public_av_return_replication_repeatability_single_slot_callable_factory_step(
                self.first_step_acceptance
            )
        )
        self.assertEqual(payload["selected_factory_step"]["role"], "callable_factory")
        self.assertEqual(payload["untouched_gate_factory_step"]["role"], "gate_factory")
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
