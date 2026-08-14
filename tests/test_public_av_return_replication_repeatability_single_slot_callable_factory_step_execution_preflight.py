from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError,
    execute_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight,
    preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution,
    public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_step_order_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_order,
)
from tests.test_public_av_return_replication_repeatability_single_slot_callable_factory_step_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepOrderAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.callable_factory_step_order_acceptance = (
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_step_order(
                self.callable_factory_step_order
            )
        )

    def test_binds_positive_order_acceptance_and_single_execution_candidate(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution(
            self.callable_factory_step_order_acceptance
        )
        self.assertTrue(preflight.positive_order_acceptance_bound)
        self.assertTrue(preflight.exactly_one_execution_candidate_bound)
        self.assertTrue(preflight.callable_factory_candidate_bound)
        self.assertTrue(preflight.callable_factory_candidate_unconsumed)
        self.assertTrue(preflight.execution_preflight_complete)
        self.assertEqual(preflight.execution_candidate_step.role, "callable_factory")

    def test_preserves_callable_identity_binding(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution(
            self.callable_factory_step_order_acceptance
        )
        self.assertTrue(preflight.callable_identity_binding_accepted)
        self.assertEqual(preflight.execution_candidate_step.factory_identity_id, preflight.callable_factory_identity_id)
        self.assertEqual(
            preflight.execution_candidate_step.constructor_identity_id,
            preflight.callable_constructor_identity_id,
        )
        self.assertEqual(preflight.execution_candidate_step.future_object_id, preflight.future_callable_object_id)

    def test_gate_factory_step_remains_unselected_untouched_and_unexecuted(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution(
            self.callable_factory_step_order_acceptance
        )
        self.assertTrue(preflight.gate_factory_step_unselected)
        self.assertTrue(preflight.gate_factory_step_untouched)
        self.assertTrue(preflight.gate_factory_step_still_unexecuted)
        self.assertEqual(preflight.untouched_gate_factory_step.role, "gate_factory")
        self.assertFalse(preflight.untouched_gate_factory_step.executed)

    def test_rejects_changed_acceptance_or_gate_as_candidate(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.callable_factory_step_order_acceptance, callable_factory_called=True)
            preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution(changed)
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution(
            self.callable_factory_step_order_acceptance
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError):
            replace(
                preflight,
                execution_candidate_step=preflight.untouched_gate_factory_step,
                untouched_gate_factory_step=preflight.execution_candidate_step,
            )

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution(
            self.callable_factory_step_order_acceptance
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
            with self.assertRaises(
                PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError
            ):
                replace(preflight, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryStepExecutionPreflightError):
            execute_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight(
                preflight
            )

    def test_json_contains_single_candidate_but_no_references_results_or_scores(self) -> None:
        payload = (
            public_av_return_replication_repeatability_single_slot_callable_factory_step_execution_preflight_to_jsonable(
                preflight_public_av_return_replication_repeatability_single_slot_callable_factory_step_execution(
                    self.callable_factory_step_order_acceptance
                )
            )
        )
        self.assertEqual(payload["execution_candidate_step"]["role"], "callable_factory")
        self.assertEqual(payload["untouched_gate_factory_step"]["role"], "gate_factory")
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
