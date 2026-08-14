from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight,
    execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_preflight,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight_acceptance_to_jsonable,
)
from audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight import (
    build_callable_factory_call_execution_preflight,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptanceTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.call_execution_preflight = build_callable_factory_call_execution_preflight(1)

    def test_accepts_positive_preflight_and_one_unconsumed_candidate(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight(self.call_execution_preflight)
        self.assertTrue(accepted.positive_call_execution_preflight_accepted)
        self.assertTrue(accepted.exactly_one_call_execution_candidate_accepted)
        self.assertTrue(accepted.callable_factory_call_candidate_unconsumed_accepted)
        self.assertTrue(accepted.call_execution_preflight_acceptance_complete)

    def test_preserves_callable_identity_and_untouched_gate(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight(self.call_execution_preflight)
        self.assertEqual(accepted.accepted_call_execution_candidate_step.role, "callable_factory")
        self.assertEqual(accepted.accepted_call_execution_candidate_step.future_object_id, accepted.future_callable_object_id)
        self.assertTrue(accepted.gate_factory_step_unselected_accepted)
        self.assertTrue(accepted.gate_factory_step_untouched_accepted)
        self.assertTrue(accepted.gate_factory_step_unexecuted_accepted)

    def test_rejects_changed_preflight_or_gate_candidate(self) -> None:
        with self.assertRaises(Exception):
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight(
                replace(self.call_execution_preflight, callable_factory_called=True)
            )
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight(self.call_execution_preflight)
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptanceError):
            replace(accepted, accepted_call_execution_candidate_step=accepted.untouched_gate_factory_step)

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight(self.call_execution_preflight)
        for field in (
            "callable_factory_reference_stored", "gate_factory_reference_stored", "callable_reference_stored",
            "factory_function_called", "callable_factory_called", "gate_factory_called",
            "callable_object_created", "gate_object_created", "constructor_invoked",
            "binding_performed", "media_decode_allowed", "receptor_feed_allowed",
            "start_release_granted", "repeat_run_started", "memory_claim_allowed", "ai_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptanceError):
                replace(accepted, **{field: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionPreflightAcceptanceError):
            execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_preflight(accepted)

    def test_json_contains_no_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_preflight(self.call_execution_preflight)
        )
        self.assertEqual(payload["accepted_call_execution_candidate_step"]["role"], "callable_factory")
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
