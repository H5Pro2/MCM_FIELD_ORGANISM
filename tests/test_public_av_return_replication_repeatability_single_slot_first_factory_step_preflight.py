from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_execution_order_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_factory_execution_order,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_first_factory_step_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError,
    execute_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight,
    preflight_public_av_return_replication_repeatability_single_slot_first_factory_step,
    public_av_return_replication_repeatability_single_slot_first_factory_step_preflight_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_factory_execution_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryExecutionOrderAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.execution_order_acceptance = (
            accept_public_av_return_replication_repeatability_single_slot_factory_execution_order(
                self.factory_execution_order
            )
        )

    def test_selects_only_unconsumed_callable_factory_step(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_first_factory_step(
            self.execution_order_acceptance
        )
        self.assertTrue(preflight.positive_execution_order_acceptance_bound)
        self.assertTrue(preflight.exactly_one_callable_factory_step_selected)
        self.assertTrue(preflight.callable_factory_step_unconsumed)
        self.assertEqual(preflight.selected_factory_step.step_index, 1)
        self.assertEqual(preflight.selected_factory_step.role, "callable_factory")
        self.assertEqual(
            preflight.selected_callable_factory_step_id,
            self.execution_order_acceptance.accepted_future_execution_steps[0].step_id,
        )

    def test_binds_callable_factory_constructor_and_future_object_identities(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_first_factory_step(
            self.execution_order_acceptance
        )
        self.assertTrue(preflight.callable_factory_identity_bound)
        self.assertTrue(preflight.callable_constructor_identity_bound)
        self.assertTrue(preflight.future_callable_object_identity_bound)
        self.assertEqual(preflight.callable_factory_identity_id, preflight.selected_factory_step.factory_identity_id)
        self.assertEqual(
            preflight.callable_constructor_identity_id,
            preflight.selected_factory_step.constructor_identity_id,
        )
        self.assertEqual(preflight.future_callable_object_id, preflight.selected_factory_step.future_object_id)

    def test_gate_factory_step_remains_unselected_untouched_and_unexecuted(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_first_factory_step(
            self.execution_order_acceptance
        )
        self.assertTrue(preflight.gate_factory_step_unselected)
        self.assertTrue(preflight.gate_factory_step_untouched)
        self.assertTrue(preflight.gate_factory_step_still_unexecuted)
        self.assertEqual(preflight.untouched_gate_factory_step.step_index, 2)
        self.assertEqual(preflight.untouched_gate_factory_step.role, "gate_factory")
        self.assertFalse(preflight.untouched_gate_factory_step.executed)

    def test_rejects_consumed_or_swapped_steps(self) -> None:
        with self.assertRaises(Exception):
            consumed = replace(
                self.execution_order_acceptance.accepted_future_execution_steps[0],
                executed=True,
            )
            replace(
                self.execution_order_acceptance,
                accepted_future_execution_steps=(
                    consumed,
                    self.execution_order_acceptance.accepted_future_execution_steps[1],
                ),
            )
        with self.assertRaises(Exception):
            preflight_public_av_return_replication_repeatability_single_slot_first_factory_step(
                replace(
                    self.execution_order_acceptance,
                    accepted_future_execution_steps=tuple(
                        reversed(self.execution_order_acceptance.accepted_future_execution_steps)
                    ),
                )
            )

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_first_factory_step(
            self.execution_order_acceptance
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
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError):
                replace(preflight, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightError):
            execute_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(preflight)

    def test_json_contains_step_and_identity_data_but_no_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_first_factory_step_preflight_to_jsonable(
            preflight_public_av_return_replication_repeatability_single_slot_first_factory_step(
                self.execution_order_acceptance
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
