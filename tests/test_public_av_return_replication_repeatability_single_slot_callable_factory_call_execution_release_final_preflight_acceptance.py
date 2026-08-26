from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight import (
    preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight,
    execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_final_preflight,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight_acceptance_to_jsonable,
)
from tools.audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight import (
    build_callable_factory_call_execution_release_final_preflight,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightAcceptanceTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.final_preflight_contract = build_callable_factory_call_execution_release_final_preflight(1)

    def test_accepts_positive_final_preflight_without_release(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight(
            self.final_preflight_contract
        )
        self.assertTrue(acceptance.positive_final_preflight_accepted)
        self.assertTrue(acceptance.exactly_one_final_lock_candidate_accepted)
        self.assertTrue(acceptance.final_lock_candidate_unconsumed_accepted)
        self.assertTrue(acceptance.actual_release_absence_accepted)
        self.assertFalse(acceptance.actual_release_granted)
        self.assertTrue(acceptance.acceptance_complete)

    def test_preserves_final_candidate_and_untouched_gate(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight(
            self.final_preflight_contract
        )
        source = (
            acceptance.final_preflight.execution_order_acceptance.execution_order.execution_preflight_acceptance
            .release_execution_preflight.release_order_acceptance.release_order.release_preflight_acceptance
            .release_preflight
        )
        self.assertTrue(acceptance.callable_identity_binding_accepted)
        self.assertTrue(acceptance.gate_step_untouched_accepted)
        self.assertEqual(source.release_candidate_step.role, "callable_factory")
        self.assertFalse(source.release_candidate_step.executed)
        self.assertTrue(source.release_candidate_step.one_time_future_step)
        self.assertEqual(source.untouched_gate_factory_step.role, "gate_factory")
        self.assertFalse(source.untouched_gate_factory_step.executed)

    def test_rejects_release_and_all_execution_surfaces(self) -> None:
        with self.assertRaises(Exception):
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight(
                replace(self.final_preflight_contract, actual_release_granted=True)
            )
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight(
            self.final_preflight_contract
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
                PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightAcceptanceError
            ):
                replace(acceptance, **{field: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalPreflightAcceptanceError
        ):
            execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_final_preflight(
                acceptance
            )

    def test_json_contains_contract_data_without_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_preflight(
                self.final_preflight_contract
            )
        )
        self.assertFalse(payload["actual_release_granted"])
        self.assertEqual(
            payload["final_preflight"]["execution_order_acceptance"]["execution_order"]["execution_preflight_acceptance"]["release_execution_preflight"]["release_order_acceptance"]["release_order"]["release_preflight_acceptance"]["release_preflight"]["release_candidate_step"]["role"],
            "callable_factory",
        )
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
