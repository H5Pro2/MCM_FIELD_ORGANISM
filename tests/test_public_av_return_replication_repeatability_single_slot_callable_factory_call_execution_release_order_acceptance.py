from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderError,
    order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order,
    execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_order,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order_acceptance_to_jsonable,
)
from tools.audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order import (
    build_callable_factory_call_execution_release_order,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderAcceptanceTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.release_order = build_callable_factory_call_execution_release_order(1)

    def test_accepts_positive_release_order_without_granting_release(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order(
            self.release_order
        )
        self.assertTrue(acceptance.positive_release_order_accepted)
        self.assertTrue(acceptance.exactly_one_future_release_step_accepted)
        self.assertTrue(acceptance.release_step_unconsumed_accepted)
        self.assertTrue(acceptance.actual_release_absence_accepted)
        self.assertFalse(acceptance.actual_release_granted)
        self.assertTrue(acceptance.acceptance_complete)

    def test_preserves_release_candidate_and_untouched_gate(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order(
            self.release_order
        )
        preflight = acceptance.release_order.release_preflight_acceptance.release_preflight
        self.assertEqual(preflight.release_candidate_step.role, "callable_factory")
        self.assertFalse(preflight.release_candidate_step.executed)
        self.assertTrue(preflight.release_candidate_step.one_time_future_step)
        self.assertEqual(preflight.untouched_gate_factory_step.role, "gate_factory")
        self.assertFalse(preflight.untouched_gate_factory_step.executed)
        self.assertTrue(acceptance.gate_step_untouched_accepted)

    def test_rejects_consumed_order_and_all_execution_surfaces(self) -> None:
        with self.assertRaises(
            (
                PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderError,
                PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderAcceptanceError,
            )
        ):
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order(
                replace(self.release_order, actual_release_granted=True)
            )
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order(
            self.release_order
        )
        for field in (
            "actual_release_granted",
            "callable_factory_reference_stored",
            "gate_factory_reference_stored",
            "callable_reference_stored",
            "factory_function_called",
            "callable_factory_called",
            "gate_factory_called",
            "callable_object_created",
            "gate_object_created",
            "constructor_invoked",
            "binding_performed",
            "scheduler_available",
            "media_decode_allowed",
            "receptor_feed_allowed",
            "start_release_granted",
            "repeatability_run_allowed",
            "repeat_run_started",
            "stability_threshold_defined",
            "memory_claim_allowed",
            "meaning_claim_allowed",
            "organization_claim_allowed",
            "ai_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderAcceptanceError):
                replace(acceptance, **{field: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseOrderAcceptanceError):
            execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_order(
                acceptance
            )

    def test_json_contains_contract_data_without_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order(
                self.release_order
            )
        )
        self.assertFalse(payload["actual_release_granted"])
        self.assertEqual(
            payload["release_order"]["release_preflight_acceptance"]["release_preflight"]["release_candidate_step"]["role"],
            "callable_factory",
        )
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
