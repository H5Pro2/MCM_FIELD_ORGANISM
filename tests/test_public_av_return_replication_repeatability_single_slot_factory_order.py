from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_call_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_factory_call_preflight,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError,
    execute_public_av_return_replication_repeatability_single_slot_factory_order,
    order_public_av_return_replication_repeatability_single_slot_factories,
    public_av_return_replication_repeatability_single_slot_factory_order_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_factory_call_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.factory_call_acceptance = accept_public_av_return_replication_repeatability_single_slot_factory_call_preflight(
            self.factory_call_preflight
        )

    def test_derives_one_callable_and_one_gate_factory_order(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_factories(
            self.factory_call_acceptance
        )
        self.assertTrue(order.positive_factory_call_acceptance_bound)
        self.assertTrue(order.exactly_one_callable_factory_order_derived)
        self.assertTrue(order.exactly_one_gate_factory_order_derived)
        self.assertTrue(order.factory_order_identities_unique)
        self.assertIn("single-slot-callable-factory-order", order.future_callable_factory_order_id)
        self.assertIn("single-slot-gate-factory-order", order.future_gate_factory_order_id)

    def test_preserves_selected_acceptance_chain_identities(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_factories(
            self.factory_call_acceptance
        )
        for role in (
            "selected_repeat_index", "factory_call_preflight_id", "factory_acceptance_id",
            "factory_binding_id", "construction_acceptance_id", "construction_id",
            "object_reservation_id", "candidate_id", "logical_callable_id",
            "logical_gate_id", "reserved_executor_id", "future_callable_object_id",
            "future_gate_object_id", "callable_constructor_id", "gate_constructor_id",
            "future_callable_factory_id", "future_gate_factory_id", "source_id",
        ):
            self.assertEqual(getattr(self.factory_call_acceptance, role), getattr(order, role))

    def test_rejects_changed_factory_call_acceptance_state(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.factory_call_acceptance, callable_factory_called=True)
            order_public_av_return_replication_repeatability_single_slot_factories(changed)

    def test_rejects_non_unique_factory_order_identities(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_factories(
            self.factory_call_acceptance
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError):
            replace(order, future_gate_factory_order_id=order.future_callable_factory_order_id)

    def test_references_calls_objects_binding_media_receptors_runs_and_claims_remain_locked(self) -> None:
        order = order_public_av_return_replication_repeatability_single_slot_factories(
            self.factory_call_acceptance
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called",
            "callable_factory_called", "gate_factory_called", "callable_object_created",
            "gate_object_created", "constructor_invoked", "binding_performed",
            "media_decode_allowed", "receptor_feed_allowed", "start_release_granted",
            "repeatability_run_allowed", "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError):
                replace(order, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderError):
            execute_public_av_return_replication_repeatability_single_slot_factory_order(order)

    def test_json_contains_no_references_instances_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_factory_order_to_jsonable(
            order_public_av_return_replication_repeatability_single_slot_factories(
                self.factory_call_acceptance
            )
        )
        self.assertTrue(payload["factory_order_identities_unique"])
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
