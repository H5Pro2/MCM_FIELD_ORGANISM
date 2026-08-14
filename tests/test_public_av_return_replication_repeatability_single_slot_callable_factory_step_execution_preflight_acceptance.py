from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight import (
    preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight,
    execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_step_preflight,
    public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight_acceptance_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightTests
):
    def setUp(self) -> None:
        super().setUp()
        self.callable_factory_step_execution_preflight = (
            preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution(
                self.callable_factory_step_order_acceptance
            )
        )

    def test_accepts_positive_preflight_and_single_unconsumed_callable_candidate(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight(
            self.callable_factory_step_execution_preflight
        )
        self.assertTrue(accepted.positive_execution_preflight_accepted)
        self.assertTrue(accepted.exactly_one_execution_candidate_accepted)
        self.assertTrue(accepted.callable_factory_candidate_accepted)
        self.assertTrue(accepted.callable_factory_candidate_unconsumed_accepted)
        self.assertTrue(accepted.execution_preflight_acceptance_complete)
        self.assertEqual(accepted.accepted_execution_candidate_step.role, "callable_factory")

    def test_preserves_identity_binding_and_untouched_gate_step(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight(
            self.callable_factory_step_execution_preflight
        )
        self.assertEqual(
            accepted.accepted_execution_candidate_step.factory_identity_id,
            accepted.callable_factory_identity_id,
        )
        self.assertTrue(accepted.gate_factory_step_unselected_accepted)
        self.assertTrue(accepted.gate_factory_step_untouched_accepted)
        self.assertTrue(accepted.gate_factory_step_unexecuted_accepted)
        self.assertFalse(accepted.untouched_gate_factory_step.executed)

    def test_rejects_changed_preflight_or_gate_candidate(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(
                self.callable_factory_step_execution_preflight,
                callable_factory_called=True,
            )
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight(
                changed
            )
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight(
            self.callable_factory_step_execution_preflight
        )
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceError
        ):
            replace(
                accepted,
                accepted_execution_candidate_step=accepted.untouched_gate_factory_step,
            )

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight(
            self.callable_factory_step_execution_preflight
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
                PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceError
            ):
                replace(accepted, **{field: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightAcceptanceError
        ):
            execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_step_preflight(
                accepted
            )

    def test_json_contains_candidate_identity_but_no_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight(
                self.callable_factory_step_execution_preflight
            )
        )
        self.assertEqual(payload["accepted_execution_candidate_step"]["role"], "callable_factory")
        self.assertEqual(payload["untouched_gate_factory_step"]["role"], "gate_factory")
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
