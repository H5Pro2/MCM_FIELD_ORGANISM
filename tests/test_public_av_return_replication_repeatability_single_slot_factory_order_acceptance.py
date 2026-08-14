from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_order import (
    order_public_av_return_replication_repeatability_single_slot_factories,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_order_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_factory_order,
    execute_public_av_return_replication_repeatability_single_slot_accepted_factory_order,
    public_av_return_replication_repeatability_single_slot_factory_order_acceptance_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_factory_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderTests
):
    def setUp(self) -> None:
        super().setUp()
        self.factory_order = order_public_av_return_replication_repeatability_single_slot_factories(
            self.factory_call_acceptance
        )

    def test_accepts_two_orders_and_all_selected_identity_groups(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_order(
            self.factory_order
        )
        self.assertTrue(accepted.positive_factory_order_accepted)
        self.assertTrue(accepted.two_factory_order_identities_accepted)
        self.assertTrue(accepted.factory_order_identities_unique)
        self.assertTrue(accepted.callable_gate_executor_identities_accepted)
        self.assertTrue(accepted.source_identity_accepted)
        self.assertTrue(accepted.factory_order_acceptance_complete)

    def test_preserves_order_and_selected_chain_identities(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_order(
            self.factory_order
        )
        for role in (
            "selected_repeat_index", "factory_call_acceptance_id", "factory_call_preflight_id",
            "factory_acceptance_id", "factory_binding_id", "construction_acceptance_id",
            "construction_id", "object_reservation_id", "candidate_id", "logical_callable_id",
            "logical_gate_id", "reserved_executor_id", "future_callable_object_id",
            "future_gate_object_id", "callable_constructor_id", "gate_constructor_id",
            "future_callable_factory_id", "future_gate_factory_id",
            "future_callable_factory_order_id", "future_gate_factory_order_id", "source_id",
        ):
            self.assertEqual(getattr(self.factory_order, role), getattr(accepted, role))

    def test_rejects_changed_factory_order_state(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.factory_order, factory_function_called=True)
            accept_public_av_return_replication_repeatability_single_slot_factory_order(changed)

    def test_rejects_non_unique_accepted_order_identities(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_order(
            self.factory_order
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError):
            replace(
                accepted,
                future_gate_factory_order_id=accepted.future_callable_factory_order_id,
            )

    def test_execution_and_claim_surfaces_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_order(
            self.factory_order
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_factory_called",
            "gate_factory_called", "callable_object_created", "gate_object_created",
            "constructor_invoked", "binding_performed", "media_decode_allowed",
            "receptor_feed_allowed", "start_release_granted", "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError):
                replace(accepted, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryOrderAcceptanceError):
            execute_public_av_return_replication_repeatability_single_slot_accepted_factory_order(accepted)

    def test_json_contains_no_references_instances_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_factory_order_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_factory_order(
                self.factory_order
            )
        )
        self.assertTrue(payload["factory_order_acceptance_complete"])
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
