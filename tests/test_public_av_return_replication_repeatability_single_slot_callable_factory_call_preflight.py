from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError,
    execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight,
    preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight_to_jsonable,
)
from audit_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order import (
    build_callable_factory_execution_order,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_execution_order_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.callable_factory_execution_order_acceptance = (
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_execution_order(
                build_callable_factory_execution_order(1)
            )
        )

    def test_binds_positive_execution_order_acceptance_and_one_call_candidate(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call(
            self.callable_factory_execution_order_acceptance
        )
        self.assertTrue(preflight.positive_execution_order_acceptance_bound)
        self.assertTrue(preflight.exactly_one_callable_call_candidate_bound)
        self.assertTrue(preflight.callable_factory_call_candidate_unconsumed)
        self.assertTrue(preflight.callable_factory_call_preflight_complete)
        self.assertEqual(preflight.call_candidate_step.role, "callable_factory")

    def test_binds_callable_factory_constructor_and_object_identities(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call(
            self.callable_factory_execution_order_acceptance
        )
        self.assertTrue(preflight.callable_factory_identity_bound)
        self.assertTrue(preflight.callable_constructor_identity_bound)
        self.assertTrue(preflight.future_callable_object_identity_bound)
        self.assertEqual(preflight.call_candidate_step.factory_identity_id, preflight.callable_factory_identity_id)
        self.assertEqual(preflight.call_candidate_step.constructor_identity_id, preflight.callable_constructor_identity_id)
        self.assertEqual(preflight.call_candidate_step.future_object_id, preflight.future_callable_object_id)

    def test_gate_factory_step_remains_unselected_untouched_and_unexecuted(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call(
            self.callable_factory_execution_order_acceptance
        )
        self.assertTrue(preflight.gate_factory_step_unselected)
        self.assertTrue(preflight.gate_factory_step_untouched)
        self.assertTrue(preflight.gate_factory_step_still_unexecuted)
        self.assertEqual(preflight.untouched_gate_factory_step.role, "gate_factory")
        self.assertFalse(preflight.untouched_gate_factory_step.executed)

    def test_rejects_changed_acceptance_or_gate_as_call_candidate(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.callable_factory_execution_order_acceptance, callable_factory_called=True)
            preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call(changed)
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call(
            self.callable_factory_execution_order_acceptance
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError):
            replace(preflight, call_candidate_step=preflight.untouched_gate_factory_step)

    def test_call_execution_and_claim_surfaces_remain_locked(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call(
            self.callable_factory_execution_order_acceptance
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
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError):
                replace(preflight, **{field: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallPreflightError):
            execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight(preflight)

    def test_json_contains_call_candidate_but_no_references_instances_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_preflight_to_jsonable(
            preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call(
                self.callable_factory_execution_order_acceptance
            )
        )
        self.assertEqual(payload["call_candidate_step"]["role"], "callable_factory")
        self.assertEqual(payload["untouched_gate_factory_step"]["role"], "gate_factory")
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
