from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_order_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_factory_order,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionPreflightError,
    execute_public_av_return_replication_repeatability_single_slot_factory_order_preflight,
    preflight_public_av_return_replication_repeatability_single_slot_factory_order_execution,
    public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_factory_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionPreflightTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.factory_order_acceptance = accept_public_av_return_replication_repeatability_single_slot_factory_order(
            self.factory_order
        )

    def test_binds_two_ordered_future_execution_candidates(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_factory_order_execution(
            self.factory_order_acceptance
        )
        self.assertTrue(preflight.positive_factory_order_acceptance_bound)
        self.assertTrue(preflight.two_ordered_execution_candidates_bound)
        self.assertTrue(preflight.callable_factory_execution_candidate_first)
        self.assertTrue(preflight.gate_factory_execution_candidate_second)
        self.assertTrue(preflight.execution_candidate_order_fixed)
        self.assertEqual(
            preflight.ordered_factory_execution_candidate_ids,
            (
                preflight.future_callable_factory_order_id,
                preflight.future_gate_factory_order_id,
            ),
        )

    def test_preserves_order_acceptance_chain_identities(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_factory_order_execution(
            self.factory_order_acceptance
        )
        for role in (
            "selected_repeat_index", "factory_order_id", "factory_call_acceptance_id",
            "factory_call_preflight_id", "factory_acceptance_id", "factory_binding_id",
            "construction_acceptance_id", "construction_id", "object_reservation_id",
            "candidate_id", "logical_callable_id", "logical_gate_id", "reserved_executor_id",
            "future_callable_object_id", "future_gate_object_id", "callable_constructor_id",
            "gate_constructor_id", "future_callable_factory_id", "future_gate_factory_id",
            "future_callable_factory_order_id", "future_gate_factory_order_id", "source_id",
        ):
            self.assertEqual(getattr(self.factory_order_acceptance, role), getattr(preflight, role))

    def test_rejects_changed_order_acceptance_state(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.factory_order_acceptance, gate_factory_called=True)
            preflight_public_av_return_replication_repeatability_single_slot_factory_order_execution(changed)

    def test_rejects_candidate_order_change(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_factory_order_execution(
            self.factory_order_acceptance
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionPreflightError):
            replace(
                preflight,
                ordered_factory_execution_candidate_ids=(
                    preflight.future_gate_factory_order_id,
                    preflight.future_callable_factory_order_id,
                ),
            )

    def test_references_calls_objects_binding_media_receptors_runs_and_claims_remain_locked(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_factory_order_execution(
            self.factory_order_acceptance
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called",
            "callable_factory_called", "gate_factory_called", "callable_object_created",
            "gate_object_created", "constructor_invoked", "binding_performed",
            "media_decode_allowed", "receptor_feed_allowed", "start_release_granted",
            "repeatability_run_allowed", "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionPreflightError):
                replace(preflight, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderExecutionPreflightError):
            execute_public_av_return_replication_repeatability_single_slot_factory_order_preflight(preflight)

    def test_json_contains_no_references_instances_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_factory_order_execution_preflight_to_jsonable(
            preflight_public_av_return_replication_repeatability_single_slot_factory_order_execution(
                self.factory_order_acceptance
            )
        )
        self.assertTrue(payload["factory_order_execution_preflight_complete"])
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
