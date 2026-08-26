from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_object_construction import (
    PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError,
    construct_public_av_return_replication_repeatability_single_slot_objects,
    prepare_public_av_return_replication_repeatability_single_slot_object_construction,
    public_av_return_replication_repeatability_single_slot_object_construction_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_object_reservation import (
    reserve_public_av_return_replication_repeatability_single_slot_objects,
)
from tests.test_public_av_return_replication_repeatability_single_slot_instantiation_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderTests
):
    def setUp(self) -> None:
        super().setUp()
        from mcm_field_organism.public_av_return_replication_repeatability_single_slot_instantiation_order import (
            derive_public_av_return_replication_repeatability_single_slot_instantiation_order,
        )

        order = derive_public_av_return_replication_repeatability_single_slot_instantiation_order(
            self.final_preflight,
            repeat_index=3,
        )
        self.reservation = reserve_public_av_return_replication_repeatability_single_slot_objects(order)

    def test_declares_constructor_identities_for_only_selected_slot(self) -> None:
        construction = prepare_public_av_return_replication_repeatability_single_slot_object_construction(
            self.reservation
        )
        self.assertEqual(3, construction.selected_repeat_index)
        self.assertEqual((1, 2), construction.other_slots_unselected)
        self.assertTrue(construction.constructor_identities_declared)
        self.assertTrue(construction.callable_constructor_allowed_later)
        self.assertTrue(construction.gate_constructor_allowed_later)

    def test_preserves_reserved_object_and_logical_identities(self) -> None:
        construction = prepare_public_av_return_replication_repeatability_single_slot_object_construction(
            self.reservation
        )
        self.assertEqual(self.reservation.future_callable_object_id, construction.future_callable_object_id)
        self.assertEqual(self.reservation.future_gate_object_id, construction.future_gate_object_id)
        self.assertEqual(self.reservation.logical_callable_id, construction.logical_callable_id)
        self.assertEqual(self.reservation.logical_gate_id, construction.logical_gate_id)
        self.assertEqual(self.reservation.reserved_executor_id, construction.reserved_executor_id)
        self.assertTrue(construction.reserved_object_identities_bound)

    def test_rejects_nonfresh_reservation(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.reservation, object_factory_created=True)
            prepare_public_av_return_replication_repeatability_single_slot_object_construction(changed)

    def test_factory_instance_binding_decode_receptor_run_and_claims_remain_locked(self) -> None:
        construction = prepare_public_av_return_replication_repeatability_single_slot_object_construction(
            self.reservation
        )
        for role in (
            "callable_factory_called",
            "gate_factory_called",
            "callable_object_created",
            "gate_object_created",
            "constructor_invoked",
            "binding_performed",
            "media_decode_allowed",
            "receptor_feed_allowed",
            "start_release_granted",
            "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(
                PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError
            ):
                replace(construction, **{role: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionError
        ):
            construct_public_av_return_replication_repeatability_single_slot_objects(construction)

    def test_json_contains_no_instances_payloads_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_object_construction_to_jsonable(
            prepare_public_av_return_replication_repeatability_single_slot_object_construction(
                self.reservation
            )
        )
        self.assertEqual(payload["selected_repeat_index"], 3)
        self.assertNotIn("instance", payload)
        self.assertNotIn("samples", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
