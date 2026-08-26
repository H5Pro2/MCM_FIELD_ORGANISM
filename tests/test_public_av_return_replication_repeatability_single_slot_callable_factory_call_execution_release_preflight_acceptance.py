from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight import (
    preflight_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight,
    execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_preflight,
    public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight_acceptance_to_jsonable,
)
from tools.audit_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight import (
    build_callable_factory_call_execution_release_preflight,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightAcceptanceTests(
    unittest.TestCase
):
    def setUp(self) -> None:
        self.release_preflight = build_callable_factory_call_execution_release_preflight(1)

    def test_accepts_one_unconsumed_candidate_without_release(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight(
            self.release_preflight
        )
        self.assertTrue(acceptance.positive_release_preflight_accepted)
        self.assertTrue(acceptance.exactly_one_release_candidate_accepted)
        self.assertTrue(acceptance.release_candidate_unconsumed_accepted)
        self.assertTrue(acceptance.actual_release_absence_accepted)
        self.assertFalse(acceptance.actual_release_granted)
        self.assertTrue(acceptance.acceptance_complete)

    def test_rejects_release_or_changed_gate_role(self) -> None:
        with self.assertRaises(Exception):
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight(
                replace(self.release_preflight, actual_release_granted=True)
            )
        changed_gate = replace(self.release_preflight.untouched_gate_factory_step, role="callable_factory")
        with self.assertRaises(Exception):
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight(
                replace(self.release_preflight, untouched_gate_factory_step=changed_gate)
            )

    def test_execution_and_all_claim_surfaces_remain_locked(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight(
            self.release_preflight
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
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightAcceptanceError):
                replace(acceptance, **{field: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotCallableFactoryCallExecutionReleasePreflightAcceptanceError):
            execute_public_av_return_replication_repeatability_single_slot_accepted_callable_factory_call_execution_release_preflight(
                acceptance
            )

    def test_json_has_contract_data_without_references_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_callable_factory_call_execution_release_preflight(
                self.release_preflight
            )
        )
        self.assertEqual(payload["release_preflight"]["release_candidate_step"]["role"], "callable_factory")
        self.assertFalse(payload["actual_release_granted"])
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
