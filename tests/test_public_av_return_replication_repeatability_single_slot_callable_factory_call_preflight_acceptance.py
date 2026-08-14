from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight,
    execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_preflight,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight_acceptance_to_jsonable,
)
from audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight import (
    build_callable_factory_call_preflight,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightAcceptanceTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.callable_factory_call_preflight = build_callable_factory_call_preflight(1)

    def test_accepts_positive_preflight_and_one_unconsumed_call_candidate(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight(
            self.callable_factory_call_preflight
        )
        self.assertTrue(accepted.positive_call_preflight_accepted)
        self.assertTrue(accepted.exactly_one_callable_call_candidate_accepted)
        self.assertTrue(accepted.callable_factory_call_candidate_unconsumed_accepted)
        self.assertTrue(accepted.callable_factory_call_preflight_acceptance_complete)
        self.assertEqual(accepted.accepted_call_candidate_step.role, "callable_factory")

    def test_preserves_identity_binding_and_untouched_gate(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight(
            self.callable_factory_call_preflight
        )
        self.assertTrue(accepted.callable_identity_binding_accepted)
        self.assertEqual(accepted.accepted_call_candidate_step.future_object_id, accepted.future_callable_object_id)
        self.assertTrue(accepted.gate_factory_step_unselected_accepted)
        self.assertTrue(accepted.gate_factory_step_untouched_accepted)
        self.assertTrue(accepted.gate_factory_step_unexecuted_accepted)

    def test_rejects_changed_preflight_or_gate_as_call_candidate(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.callable_factory_call_preflight, callable_factory_called=True)
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight(changed)
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight(
            self.callable_factory_call_preflight
        )
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightAcceptanceError
        ):
            replace(accepted, accepted_call_candidate_step=accepted.untouched_gate_factory_step)

    def test_call_execution_and_claim_surfaces_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight(
            self.callable_factory_call_preflight
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
                PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightAcceptanceError
            ):
                replace(accepted, **{field: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightAcceptanceError
        ):
            execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_preflight(
                accepted
            )

    def test_json_contains_candidate_but_no_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight(
                self.callable_factory_call_preflight
            )
        )
        self.assertEqual(payload["accepted_call_candidate_step"]["role"], "callable_factory")
        self.assertEqual(payload["untouched_gate_factory_step"]["role"], "gate_factory")
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
