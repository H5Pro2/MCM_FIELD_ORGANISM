from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_step_order import (
    order_public_av_return_replication_repeatability_single_slot_callable_factory_step,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_step_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_order,
    execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_step_order,
    public_av_return_replication_repeatability_single_slot_callable_factory_step_order_acceptance_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_callable_factory_step_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderTests
):
    def setUp(self) -> None:
        super().setUp()
        self.callable_factory_step_order = order_public_av_return_replication_repeatability_single_slot_callable_factory_step(
            self.first_step_acceptance
        )

    def test_accepts_one_time_unexecuted_callable_order_and_identity_binding(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_order(
            self.callable_factory_step_order
        )
        self.assertTrue(accepted.positive_callable_factory_step_order_accepted)
        self.assertTrue(accepted.exactly_one_callable_factory_order_accepted)
        self.assertTrue(accepted.callable_factory_order_one_time_accepted)
        self.assertTrue(accepted.callable_factory_order_unexecuted_accepted)
        self.assertTrue(accepted.callable_identity_binding_accepted)
        self.assertTrue(accepted.callable_factory_step_order_acceptance_complete)

    def test_keeps_gate_step_unselected_untouched_and_unexecuted(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_order(
            self.callable_factory_step_order
        )
        self.assertTrue(accepted.gate_factory_step_unselected_accepted)
        self.assertTrue(accepted.gate_factory_step_untouched_accepted)
        self.assertTrue(accepted.gate_factory_step_unexecuted_accepted)
        self.assertFalse(accepted.untouched_gate_factory_step.executed)

    def test_rejects_changed_order_or_swapped_steps(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.callable_factory_step_order, callable_factory_called=True)
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_order(changed)
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_order(
            self.callable_factory_step_order
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError):
            replace(
                accepted,
                selected_factory_step=accepted.untouched_gate_factory_step,
                untouched_gate_factory_step=accepted.selected_factory_step,
            )

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_order(
            self.callable_factory_step_order
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_factory_called",
            "gate_factory_called", "callable_object_created", "gate_object_created",
            "constructor_invoked", "binding_performed", "media_decode_allowed",
            "receptor_feed_allowed", "start_release_granted", "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError):
                replace(accepted, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceError):
            execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_step_order(accepted)

    def test_json_has_order_and_steps_but_no_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_step_order_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_order(
                self.callable_factory_step_order
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
