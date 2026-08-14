from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order import (
    order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order,
    execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_execution_order,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order_acceptance_to_jsonable,
)
from tools.audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order import (
    build_callable_factory_call_execution_release_execution_order,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptanceTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.release_execution_order = build_callable_factory_call_execution_release_execution_order(1)

    def test_accepts_positive_execution_order_without_release(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order(
            self.release_execution_order
        )
        self.assertTrue(acceptance.positive_execution_order_accepted)
        self.assertTrue(acceptance.exactly_one_future_execution_step_accepted)
        self.assertTrue(acceptance.execution_step_one_time_accepted)
        self.assertTrue(acceptance.execution_step_unexecuted_accepted)
        self.assertFalse(acceptance.actual_release_granted)
        self.assertTrue(acceptance.acceptance_complete)

    def test_preserves_candidate_and_gate(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order(
            self.release_execution_order
        )
        source = (
            acceptance.execution_order.execution_preflight_acceptance.release_execution_preflight
            .release_order_acceptance.release_order.release_preflight_acceptance.release_preflight
        )
        self.assertTrue(acceptance.callable_identity_accepted)
        self.assertTrue(acceptance.gate_step_untouched_accepted)
        self.assertEqual(source.release_candidate_step.role, "callable_factory")
        self.assertFalse(source.release_candidate_step.executed)
        self.assertTrue(source.release_candidate_step.one_time_future_step)
        self.assertEqual(source.untouched_gate_factory_step.role, "gate_factory")
        self.assertFalse(source.untouched_gate_factory_step.executed)

    def test_rejects_release_and_all_execution_surfaces(self) -> None:
        with self.assertRaises(Exception):
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order(
                replace(self.release_execution_order, actual_release_granted=True)
            )
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order(
            self.release_execution_order
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
            with self.assertRaises(
                PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptanceError
            ):
                replace(acceptance, **{field: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionOrderAcceptanceError
        ):
            execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_execution_order(
                acceptance
            )

    def test_json_contains_contract_data_without_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_order(
                self.release_execution_order
            )
        )
        self.assertFalse(payload["actual_release_granted"])
        self.assertEqual(
            payload["execution_order"]["execution_preflight_acceptance"]["release_execution_preflight"]["release_order_acceptance"]["release_order"]["release_preflight_acceptance"]["release_preflight"]["release_candidate_step"]["role"],
            "callable_factory",
        )
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
