from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightError,
    execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight,
    preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight_to_jsonable,
)
from tools.audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order import (
    build_callable_factory_call_execution_order,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.call_execution_order_acceptance = (
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_order(
                build_callable_factory_call_execution_order(1)
            )
        )

    def test_binds_positive_order_acceptance_and_one_release_candidate(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
            self.call_execution_order_acceptance
        )
        self.assertTrue(preflight.positive_execution_order_acceptance_bound)
        self.assertTrue(preflight.exactly_one_release_candidate_bound)
        self.assertTrue(preflight.release_candidate_unconsumed)
        self.assertFalse(preflight.actual_release_granted)
        self.assertTrue(preflight.release_preflight_complete)
        self.assertEqual(preflight.release_candidate_step.role, "callable_factory")

    def test_binds_callable_identity_and_keeps_gate_untouched(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
            self.call_execution_order_acceptance
        )
        self.assertTrue(preflight.callable_identity_binding_accepted)
        self.assertEqual(preflight.release_candidate_step.future_object_id, preflight.future_callable_object_id)
        self.assertTrue(preflight.gate_factory_step_unselected)
        self.assertTrue(preflight.gate_factory_step_untouched)
        self.assertTrue(preflight.gate_factory_step_still_unexecuted)

    def test_rejects_changed_acceptance_or_gate_release_candidate(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.call_execution_order_acceptance, callable_factory_called=True)
            preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
                changed
            )
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
            self.call_execution_order_acceptance
        )
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightError
        ):
            replace(preflight, release_candidate_step=preflight.untouched_gate_factory_step)

    def test_release_execution_and_claim_surfaces_remain_locked(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
            self.call_execution_order_acceptance
        )
        for field in (
            "actual_release_granted", "callable_factory_reference_stored",
            "gate_factory_reference_stored", "callable_reference_stored",
            "factory_function_called", "callable_factory_called", "gate_factory_called",
            "callable_object_created", "gate_object_created", "constructor_invoked",
            "binding_performed", "scheduler_available", "media_decode_allowed",
            "receptor_feed_allowed", "start_release_granted", "repeatability_run_allowed",
            "repeat_run_started", "memory_claim_allowed", "meaning_claim_allowed",
            "organization_claim_allowed", "ai_claim_allowed",
        ):
            with self.assertRaises(
                PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightError
            ):
                replace(preflight, **{field: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightError
        ):
            execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight(
                preflight
            )

    def test_json_contains_release_candidate_but_no_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight_to_jsonable(
            preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release(
                self.call_execution_order_acceptance
            )
        )
        self.assertEqual(payload["release_candidate_step"]["role"], "callable_factory")
        self.assertEqual(payload["untouched_gate_factory_step"]["role"], "gate_factory")
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
