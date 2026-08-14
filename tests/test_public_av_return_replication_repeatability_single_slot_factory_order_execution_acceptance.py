from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_order_execution_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight,
    execute_public_av_return_replication_repeatability_single_slot_accepted_factory_order_execution,
    public_av_return_replication_repeatability_single_slot_factory_order_execution_acceptance_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight import (
    preflight_public_av_return_replication_repeatability_single_slot_factory_order_execution,
)
from tests.test_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionPreflightTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionPreflightTests
):
    def setUp(self) -> None:
        super().setUp()
        self.execution_preflight = preflight_public_av_return_replication_repeatability_single_slot_factory_order_execution(
            self.factory_order_acceptance
        )

    def test_accepts_positive_preflight_fixed_order_and_both_order_identities(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight(
            self.execution_preflight
        )
        self.assertTrue(accepted.positive_execution_preflight_accepted)
        self.assertTrue(accepted.two_ordered_execution_candidates_accepted)
        self.assertTrue(accepted.callable_factory_candidate_first_accepted)
        self.assertTrue(accepted.gate_factory_candidate_second_accepted)
        self.assertTrue(accepted.fixed_candidate_order_accepted)
        self.assertTrue(accepted.factory_order_execution_acceptance_complete)

    def test_preserves_fixed_candidate_order(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight(
            self.execution_preflight
        )
        self.assertEqual(
            accepted.ordered_factory_execution_candidate_ids,
            (
                accepted.future_callable_factory_order_id,
                accepted.future_gate_factory_order_id,
            ),
        )

    def test_rejects_changed_preflight_state_or_candidate_order(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.execution_preflight, factory_function_called=True)
            accept_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight(changed)
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight(
            self.execution_preflight
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError):
            replace(
                accepted,
                ordered_factory_execution_candidate_ids=tuple(
                    reversed(accepted.ordered_factory_execution_candidate_ids)
                ),
            )

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight(
            self.execution_preflight
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_factory_called",
            "gate_factory_called", "callable_object_created", "gate_object_created",
            "constructor_invoked", "binding_performed", "media_decode_allowed",
            "receptor_feed_allowed", "start_release_granted", "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError):
                replace(accepted, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionAcceptanceError):
            execute_public_av_return_replication_repeatability_single_slot_accepted_factory_order_execution(accepted)

    def test_json_contains_no_references_instances_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_factory_order_execution_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight(
                self.execution_preflight
            )
        )
        self.assertTrue(payload["factory_order_execution_acceptance_complete"])
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
