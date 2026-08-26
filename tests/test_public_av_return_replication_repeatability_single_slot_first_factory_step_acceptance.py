from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_first_factory_step_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight,
    execute_public_av_return_replication_repeatability_single_slot_accepted_first_factory_step,
    public_av_return_replication_repeatability_single_slot_first_factory_step_acceptance_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_first_factory_step_preflight import (
    preflight_public_av_return_replication_repeatability_single_slot_first_factory_step,
)
from tests.test_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepPreflightTests
):
    def setUp(self) -> None:
        super().setUp()
        self.first_step_preflight = preflight_public_av_return_replication_repeatability_single_slot_first_factory_step(
            self.execution_order_acceptance
        )

    def test_accepts_callable_selection_identity_binding_and_unconsumed_state(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(
            self.first_step_preflight
        )
        self.assertTrue(accepted.positive_first_step_preflight_accepted)
        self.assertTrue(accepted.callable_factory_step_selection_accepted)
        self.assertTrue(accepted.callable_factory_step_unconsumed_accepted)
        self.assertTrue(accepted.callable_identity_binding_accepted)
        self.assertTrue(accepted.first_factory_step_acceptance_complete)

    def test_keeps_gate_step_unselected_untouched_and_unexecuted(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(
            self.first_step_preflight
        )
        self.assertTrue(accepted.gate_factory_step_unselected_accepted)
        self.assertTrue(accepted.gate_factory_step_untouched_accepted)
        self.assertTrue(accepted.gate_factory_step_unexecuted_accepted)
        self.assertFalse(accepted.untouched_gate_factory_step.executed)

    def test_rejects_changed_preflight_or_swapped_steps(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.first_step_preflight, callable_factory_called=True)
            accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(changed)
        accepted = accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(
            self.first_step_preflight
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError):
            replace(
                accepted,
                selected_factory_step=accepted.untouched_gate_factory_step,
                untouched_gate_factory_step=accepted.selected_factory_step,
            )

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(
            self.first_step_preflight
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_factory_called",
            "gate_factory_called", "callable_object_created", "gate_object_created",
            "constructor_invoked", "binding_performed", "media_decode_allowed",
            "receptor_feed_allowed", "start_release_granted", "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError):
                replace(accepted, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFirstFactoryStepAcceptanceError):
            execute_public_av_return_replication_repeatability_single_slot_accepted_first_factory_step(accepted)

    def test_json_has_steps_but_no_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_first_factory_step_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_first_factory_step_preflight(
                self.first_step_preflight
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
