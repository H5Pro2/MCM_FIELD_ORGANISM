from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_call_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_factory_call_preflight,
    call_public_av_return_replication_repeatability_single_slot_accepted_factory_call,
    public_av_return_replication_repeatability_single_slot_factory_call_acceptance_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_call_preflight import (
    preflight_public_av_return_replication_repeatability_single_slot_factory_call,
)
from tests.test_public_av_return_replication_repeatability_single_slot_factory_call_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightTests
):
    def setUp(self) -> None:
        super().setUp()
        self.factory_call_preflight = preflight_public_av_return_replication_repeatability_single_slot_factory_call(
            self.factory_acceptance
        )

    def test_accepts_positive_preflight_and_all_selected_identity_groups(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_call_preflight(
            self.factory_call_preflight
        )
        self.assertTrue(accepted.positive_factory_call_preflight_accepted)
        self.assertTrue(accepted.factory_identities_accepted)
        self.assertTrue(accepted.constructor_identities_accepted)
        self.assertTrue(accepted.object_identities_accepted)
        self.assertTrue(accepted.callable_gate_executor_identities_accepted)
        self.assertTrue(accepted.source_identity_accepted)
        self.assertTrue(accepted.factory_call_acceptance_complete)

    def test_preserves_all_selected_identities(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_call_preflight(
            self.factory_call_preflight
        )
        for role in (
            "selected_repeat_index", "factory_acceptance_id", "factory_binding_id",
            "construction_acceptance_id", "construction_id", "object_reservation_id",
            "candidate_id", "logical_callable_id", "logical_gate_id", "reserved_executor_id",
            "future_callable_object_id", "future_gate_object_id", "callable_constructor_id",
            "gate_constructor_id", "future_callable_factory_id", "future_gate_factory_id",
            "source_id",
        ):
            self.assertEqual(getattr(self.factory_call_preflight, role), getattr(accepted, role))

    def test_rejects_changed_preflight_state(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.factory_call_preflight, binding_performed=True)
            accept_public_av_return_replication_repeatability_single_slot_factory_call_preflight(changed)

    def test_rejects_selected_identity_mismatch(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_call_preflight(
            self.factory_call_preflight
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError):
            replace(accepted, future_gate_factory_id=accepted.future_callable_factory_id)

    def test_references_calls_objects_binding_media_receptors_runs_and_claims_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_call_preflight(
            self.factory_call_preflight
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_factory_called",
            "gate_factory_called", "callable_object_created", "gate_object_created",
            "constructor_invoked", "binding_performed", "media_decode_allowed",
            "receptor_feed_allowed", "start_release_granted", "repeatability_run_allowed",
            "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError):
                replace(accepted, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallAcceptanceError):
            call_public_av_return_replication_repeatability_single_slot_accepted_factory_call(accepted)

    def test_json_contains_no_references_instances_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_factory_call_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_factory_call_preflight(
                self.factory_call_preflight
            )
        )
        self.assertTrue(payload["factory_call_acceptance_complete"])
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
