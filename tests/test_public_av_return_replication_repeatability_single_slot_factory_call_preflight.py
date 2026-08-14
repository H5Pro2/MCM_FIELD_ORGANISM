from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_factory_binding,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_call_preflight import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError,
    call_public_av_return_replication_repeatability_single_slot_preflighted_factories,
    preflight_public_av_return_replication_repeatability_single_slot_factory_call,
    public_av_return_replication_repeatability_single_slot_factory_call_preflight_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_factory_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.factory_acceptance = accept_public_av_return_replication_repeatability_single_slot_factory_binding(
            self.binding
        )

    def test_binds_positive_factory_acceptance_and_selected_identities(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_factory_call(
            self.factory_acceptance
        )
        self.assertTrue(preflight.positive_factory_acceptance_bound)
        self.assertTrue(preflight.selected_factory_identities_bound)
        self.assertTrue(preflight.selected_constructor_identities_bound)
        self.assertTrue(preflight.selected_object_identities_bound)
        self.assertTrue(preflight.factory_call_preflight_complete)

    def test_preserves_factory_constructor_object_and_slot_identities(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_factory_call(
            self.factory_acceptance
        )
        for role in (
            "selected_repeat_index", "factory_binding_id", "construction_acceptance_id",
            "construction_id", "object_reservation_id", "candidate_id",
            "logical_callable_id", "logical_gate_id", "reserved_executor_id",
            "future_callable_object_id", "future_gate_object_id",
            "callable_constructor_id", "gate_constructor_id",
            "future_callable_factory_id", "future_gate_factory_id", "source_id",
        ):
            self.assertEqual(getattr(self.factory_acceptance, role), getattr(preflight, role))

    def test_rejects_changed_factory_acceptance_state(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.factory_acceptance, factory_function_called=True)
            preflight_public_av_return_replication_repeatability_single_slot_factory_call(changed)

    def test_rejects_factory_id_mismatch(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_factory_call(
            self.factory_acceptance
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError):
            replace(preflight, future_gate_factory_id=preflight.future_callable_factory_id)

    def test_references_calls_objects_media_receptors_runs_and_claims_remain_locked(self) -> None:
        preflight = preflight_public_av_return_replication_repeatability_single_slot_factory_call(
            self.factory_acceptance
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called",
            "callable_factory_called", "gate_factory_called", "callable_object_created",
            "gate_object_created", "constructor_invoked", "binding_performed",
            "media_decode_allowed", "receptor_feed_allowed", "start_release_granted",
            "repeatability_run_allowed", "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError):
                replace(preflight, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryCallPreflightError):
            call_public_av_return_replication_repeatability_single_slot_preflighted_factories(preflight)

    def test_json_contains_no_references_instances_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_factory_call_preflight_to_jsonable(
            preflight_public_av_return_replication_repeatability_single_slot_factory_call(
                self.factory_acceptance
            )
        )
        self.assertTrue(payload["factory_call_preflight_complete"])
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
