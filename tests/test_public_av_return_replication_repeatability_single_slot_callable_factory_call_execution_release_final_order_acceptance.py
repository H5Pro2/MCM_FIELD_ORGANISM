from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order import (
    order_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order,
    execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_final_order,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order_acceptance_to_jsonable,
)
from tools.audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order import (
    build_callable_factory_call_execution_release_final_order,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptanceTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.release_final_order_contract = build_callable_factory_call_execution_release_final_order(1)

    def test_accepts_positive_final_order_without_release(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order(
            self.release_final_order_contract
        )
        self.assertTrue(acceptance.positive_final_order_accepted)
        self.assertTrue(acceptance.exactly_one_final_lock_step_accepted)
        self.assertTrue(acceptance.final_lock_step_one_time_accepted)
        self.assertTrue(acceptance.final_lock_step_unconsumed_accepted)
        self.assertFalse(acceptance.actual_release_granted)
        self.assertTrue(acceptance.acceptance_complete)

    def test_rejects_release_and_execution_surfaces(self) -> None:
        with self.assertRaises(Exception):
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order(
                replace(self.release_final_order_contract, actual_release_granted=True)
            )
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order(
            self.release_final_order_contract
        )
        for field in (
            "actual_release_granted", "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_factory_called",
            "gate_factory_called", "callable_object_created", "gate_object_created", "constructor_invoked",
            "binding_performed", "scheduler_available", "media_decode_allowed", "receptor_feed_allowed",
            "start_release_granted", "repeatability_run_allowed", "repeat_run_started",
            "stability_threshold_defined", "memory_claim_allowed", "meaning_claim_allowed",
            "organization_claim_allowed", "ai_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptanceError):
                replace(acceptance, **{field: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseFinalOrderAcceptanceError):
            execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_final_order(
                acceptance
            )

    def test_json_excludes_references_results_and_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_final_order(
                self.release_final_order_contract
            )
        )
        self.assertFalse(payload["actual_release_granted"])
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
