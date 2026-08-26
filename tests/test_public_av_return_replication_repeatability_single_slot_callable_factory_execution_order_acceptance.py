from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_execution_order import (
    order_public_av_return_replication_repeatability_single_slot_callable_factory_execution,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_execution_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order,
    execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_execution_order,
    public_av_return_replication_repeatability_single_slot_callable_factory_execution_order_acceptance_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptanceTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderTests
):
    def setUp(self) -> None:
        super().setUp()
        self.callable_factory_execution_order = (
            order_public_av_return_replication_repeatability_single_slot_callable_factory_execution(
                self.callable_factory_execution_preflight_acceptance
            )
        )

    def test_accepts_one_future_unconsumed_callable_execution_step(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order(
            self.callable_factory_execution_order
        )
        self.assertTrue(accepted.positive_callable_factory_execution_order_accepted)
        self.assertTrue(accepted.exactly_one_future_callable_execution_step_accepted)
        self.assertTrue(accepted.callable_execution_step_one_time_accepted)
        self.assertTrue(accepted.callable_execution_step_unexecuted_accepted)
        self.assertTrue(accepted.callable_factory_execution_order_acceptance_complete)

    def test_preserves_callable_identity_binding_and_untouched_gate(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order(
            self.callable_factory_execution_order
        )
        self.assertTrue(accepted.callable_identity_binding_accepted)
        self.assertEqual(accepted.accepted_callable_execution_step.role, "callable_factory")
        self.assertEqual(
            accepted.accepted_callable_execution_step.future_object_id,
            accepted.future_callable_object_id,
        )
        self.assertTrue(accepted.gate_factory_step_unselected_accepted)
        self.assertTrue(accepted.gate_factory_step_untouched_accepted)
        self.assertTrue(accepted.gate_factory_step_unexecuted_accepted)

    def test_rejects_changed_order_or_gate_as_callable_step(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.callable_factory_execution_order, callable_factory_called=True)
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order(changed)
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order(
            self.callable_factory_execution_order
        )
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptanceError
        ):
            replace(accepted, accepted_callable_execution_step=accepted.untouched_gate_factory_step)

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order(
            self.callable_factory_execution_order
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
            with self.assertRaises(
                PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptanceError
            ):
                replace(accepted, **{field: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryExecutionOrderAcceptanceError
        ):
            execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_execution_order(
                accepted
            )

    def test_json_contains_step_identity_but_no_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_execution_order_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order(
                self.callable_factory_execution_order
            )
        )
        self.assertEqual(payload["accepted_callable_execution_step"]["role"], "callable_factory")
        self.assertEqual(payload["untouched_gate_factory_step"]["role"], "gate_factory")
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
