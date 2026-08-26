from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_instantiation_order import (
    derive_public_av_return_replication_repeatability_single_slot_instantiation_order,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_object_reservation import (
    PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError,
    create_public_av_return_replication_repeatability_single_slot_objects,
    public_av_return_replication_repeatability_single_slot_object_reservation_to_jsonable,
    reserve_public_av_return_replication_repeatability_single_slot_objects,
)
from tests.test_public_av_return_replication_repeatability_single_slot_instantiation_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderTests
):
    def setUp(self) -> None:
        super().setUp()
        self.order = derive_public_av_return_replication_repeatability_single_slot_instantiation_order(
            self.final_preflight, repeat_index=2
        )

    def test_reserves_only_selected_slot_object_identities(self) -> None:
        reservation = reserve_public_av_return_replication_repeatability_single_slot_objects(
            self.order
        )
        self.assertEqual(2, reservation.selected_repeat_index)
        self.assertEqual((1, 3), reservation.other_slots_unselected)
        self.assertTrue(reservation.callable_object_identity_reserved)
        self.assertTrue(reservation.gate_object_identity_reserved)

    def test_preserves_logical_callable_gate_executor_and_source_identities(self) -> None:
        reservation = reserve_public_av_return_replication_repeatability_single_slot_objects(
            self.order
        )
        self.assertEqual(self.order.future_callable_id, reservation.logical_callable_id)
        self.assertEqual(self.order.reserved_gate_id, reservation.logical_gate_id)
        self.assertEqual(self.order.reserved_executor_id, reservation.reserved_executor_id)
        self.assertEqual(self.order.source_id, reservation.source_id)
        self.assertTrue(reservation.logical_identities_unchanged)

    def test_rejects_nonfresh_order(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.order, gate_instance_created=True)
            reserve_public_av_return_replication_repeatability_single_slot_objects(changed)

    def test_creation_binding_decode_receptor_run_and_claims_remain_locked(self) -> None:
        reservation = reserve_public_av_return_replication_repeatability_single_slot_objects(
            self.order
        )
        for role in (
            "callable_object_created", "gate_object_created", "object_factory_created",
            "binding_performed", "media_decode_allowed", "receptor_feed_allowed",
            "start_release_granted", "repeatability_run_allowed", "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError):
                replace(reservation, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotObjectReservationError):
            create_public_av_return_replication_repeatability_single_slot_objects(reservation)

    def test_json_contains_no_objects_payloads_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_object_reservation_to_jsonable(
            reserve_public_av_return_replication_repeatability_single_slot_objects(self.order)
        )
        self.assertEqual(payload["selected_repeat_index"], 2)
        self.assertNotIn("object", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
