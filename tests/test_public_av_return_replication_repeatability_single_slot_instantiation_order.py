from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_instantiation_order import (
    PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError,
    derive_public_av_return_replication_repeatability_single_slot_instantiation_order,
    instantiate_public_av_return_replication_repeatability_single_slot,
    public_av_return_replication_repeatability_single_slot_instantiation_order_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_final_execution_preflight import (
    PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderTests(
    PublicAVReturnReplicationRepeatabilityFinalExecutionPreflightTests
):
    def setUp(self) -> None:
        super().setUp()
        self.final_preflight = self.build_preflight()

    def test_derives_exactly_one_selected_fresh_slot(self) -> None:
        order = derive_public_av_return_replication_repeatability_single_slot_instantiation_order(
            self.final_preflight,
            repeat_index=2,
        )
        self.assertEqual(2, order.selected_repeat_index)
        self.assertTrue(order.exactly_one_slot_selected)
        self.assertEqual((1, 3), order.other_slots_unselected)
        self.assertTrue(order.selected_slot_is_fresh)

    def test_binds_candidate_callable_executor_gate_and_source_identities(self) -> None:
        order = derive_public_av_return_replication_repeatability_single_slot_instantiation_order(
            self.final_preflight,
            repeat_index=1,
        )
        slot = self.final_preflight.slot_preflights[0]
        self.assertEqual(slot.candidate_id, order.candidate_id)
        self.assertEqual(slot.future_callable_id, order.future_callable_id)
        self.assertEqual(slot.reserved_executor_id, order.reserved_executor_id)
        self.assertEqual(slot.reserved_gate_id, order.reserved_gate_id)
        self.assertEqual(self.final_preflight.source_id, order.source_id)
        self.assertTrue(order.candidate_identity_bound)
        self.assertTrue(order.callable_identity_bound)
        self.assertTrue(order.executor_identity_bound)
        self.assertTrue(order.gate_identity_bound)

    def test_rejects_invalid_or_nonfresh_selection(self) -> None:
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError
        ):
            derive_public_av_return_replication_repeatability_single_slot_instantiation_order(
                self.final_preflight,
                repeat_index=4,
            )
        with self.assertRaises(Exception):
            changed = replace(self.final_preflight.slot_preflights[1], scheduled=True)
            altered = replace(
                self.final_preflight,
                slot_preflights=(
                    self.final_preflight.slot_preflights[0],
                    changed,
                    self.final_preflight.slot_preflights[2],
                ),
            )
            derive_public_av_return_replication_repeatability_single_slot_instantiation_order(
                altered,
                repeat_index=2,
            )

    def test_object_decode_receptor_run_and_claim_surfaces_remain_locked(self) -> None:
        order = derive_public_av_return_replication_repeatability_single_slot_instantiation_order(
            self.final_preflight,
            repeat_index=3,
        )
        for role in (
            "callable_object_created",
            "gate_instance_created",
            "binding_performed",
            "scheduler_available",
            "media_decode_allowed",
            "receptor_feed_allowed",
            "start_release_granted",
            "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(
                PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError
            ):
                replace(order, **{role: True})
        with self.assertRaises(
            PublicAVReturnReplicationRepeatabilitySingleSlotInstantiationOrderError
        ):
            instantiate_public_av_return_replication_repeatability_single_slot(order)

    def test_json_has_no_objects_payloads_results_or_claim_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_instantiation_order_to_jsonable(
            derive_public_av_return_replication_repeatability_single_slot_instantiation_order(
                self.final_preflight,
                repeat_index=1,
            )
        )
        self.assertEqual(payload["selected_repeat_index"], 1)
        self.assertNotIn("object", payload)
        self.assertNotIn("samples", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)
        self.assertNotIn("organization_score", payload)


if __name__ == "__main__":
    unittest.main()
