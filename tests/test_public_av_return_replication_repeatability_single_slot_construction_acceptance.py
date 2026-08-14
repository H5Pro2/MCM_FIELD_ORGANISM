from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_construction_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_construction,
    construct_from_public_av_return_replication_repeatability_single_slot_acceptance,
    public_av_return_replication_repeatability_single_slot_construction_acceptance_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_object_construction import (
    prepare_public_av_return_replication_repeatability_single_slot_object_construction,
)
from tests.test_public_av_return_replication_repeatability_single_slot_object_construction import (
    PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotObjectConstructionTests
):
    def setUp(self) -> None:
        super().setUp()
        self.construction = prepare_public_av_return_replication_repeatability_single_slot_object_construction(
            self.reservation
        )

    def test_accepts_reservation_constructor_and_object_identities(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_construction(
            self.construction
        )
        self.assertTrue(acceptance.reservation_identity_accepted)
        self.assertTrue(acceptance.object_identities_accepted)
        self.assertTrue(acceptance.constructor_identities_accepted)
        self.assertTrue(acceptance.construction_acceptance_complete)

    def test_preserves_gate_callable_and_constructor_identities(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_construction(
            self.construction
        )
        for role in (
            "logical_callable_id", "logical_gate_id", "future_callable_object_id",
            "future_gate_object_id", "callable_constructor_id", "gate_constructor_id",
        ):
            self.assertEqual(getattr(self.construction, role), getattr(acceptance, role))

    def test_rejects_changed_construction_state(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.construction, constructor_invoked=True)
            accept_public_av_return_replication_repeatability_single_slot_construction(changed)

    def test_factories_instances_binding_media_receptors_run_and_claims_remain_locked(self) -> None:
        acceptance = accept_public_av_return_replication_repeatability_single_slot_construction(
            self.construction
        )
        for role in (
            "callable_factory_called", "gate_factory_called", "callable_object_created",
            "gate_object_created", "constructor_invoked", "binding_performed",
            "media_decode_allowed", "receptor_feed_allowed", "start_release_granted",
            "repeatability_run_allowed", "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError):
                replace(acceptance, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceError):
            construct_from_public_av_return_replication_repeatability_single_slot_acceptance(acceptance)

    def test_json_contains_no_instances_payloads_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_construction_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_construction(self.construction)
        )
        self.assertTrue(payload["construction_acceptance_complete"])
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
