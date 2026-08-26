from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightError,
    execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight,
    preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order,
)
from tools.audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order import (
    build_callable_factory_call_execution_release_order,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.release_order_acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_order(
            build_callable_factory_call_execution_release_order(1)
        )

    def test_binds_one_unconsumed_execution_candidate_without_release(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution(
            self.release_order_acceptance
        )
        self.assertTrue(preflight.positive_release_order_acceptance_bound)
        self.assertTrue(preflight.exactly_one_execution_candidate_bound)
        self.assertTrue(preflight.execution_candidate_unconsumed)
        self.assertFalse(preflight.actual_release_granted)
        self.assertTrue(preflight.execution_preflight_complete)

    def test_preserves_callable_identity_and_untouched_gate(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution(
            self.release_order_acceptance
        )
        self.assertTrue(preflight.callable_identity_binding_accepted)
        self.assertTrue(preflight.gate_factory_step_unselected)
        self.assertTrue(preflight.gate_factory_step_untouched)
        self.assertTrue(preflight.gate_factory_step_still_unexecuted)
        source = preflight.release_order_acceptance.release_order.release_preflight_acceptance.release_preflight
        self.assertEqual(source.release_candidate_step.role, "callable_factory")
        self.assertEqual(source.untouched_gate_factory_step.role, "gate_factory")

    def test_rejects_release_and_all_execution_surfaces(self) -> None:
        with self.assertRaises(Exception):
            preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution(
                replace(self.release_order_acceptance, actual_release_granted=True)
            )
        preflight = preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution(
            self.release_order_acceptance
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
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightError):
                replace(preflight, **{field: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleaseExecutionPreflightError):
            execute_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight(
                preflight
            )

    def test_json_has_contract_data_without_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution_preflight_to_jsonable(
            preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_execution(
                self.release_order_acceptance
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
