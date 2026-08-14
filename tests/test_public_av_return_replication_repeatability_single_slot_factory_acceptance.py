from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError,
    accept_public_av_return_replication_repeatability_single_slot_factory_binding,
    call_public_av_return_replication_repeatability_single_slot_accepted_factories,
    public_av_return_replication_repeatability_single_slot_factory_acceptance_to_jsonable,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_binding import (
    bind_public_av_return_replication_repeatability_single_slot_factories,
)
from tests.test_public_av_return_replication_repeatability_single_slot_factory_binding import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingTests
):
    def setUp(self) -> None:
        super().setUp()
        self.binding = bind_public_av_return_replication_repeatability_single_slot_factories(
            self.acceptance
        )

    def test_accepts_factory_binding_constructor_factory_and_object_identities(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_binding(
            self.binding
        )
        self.assertTrue(accepted.factory_binding_accepted)
        self.assertTrue(accepted.constructor_identities_accepted)
        self.assertTrue(accepted.factory_identities_accepted)
        self.assertTrue(accepted.object_identities_accepted)
        self.assertTrue(accepted.factory_acceptance_complete)

    def test_preserves_all_factory_chain_identities(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_binding(
            self.binding
        )
        for role in (
            "callable_constructor_id", "gate_constructor_id", "future_callable_factory_id",
            "future_gate_factory_id", "future_callable_object_id", "future_gate_object_id",
            "logical_callable_id", "logical_gate_id", "source_id",
        ):
            self.assertEqual(getattr(self.binding, role), getattr(accepted, role))

    def test_rejects_binding_with_reference_or_call_state(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.binding, callable_factory_reference_stored=True)
            accept_public_av_return_replication_repeatability_single_slot_factory_binding(changed)

    def test_references_calls_objects_media_receptors_runs_and_claims_remain_locked(self) -> None:
        accepted = accept_public_av_return_replication_repeatability_single_slot_factory_binding(
            self.binding
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called", "callable_object_created",
            "gate_object_created", "media_decode_allowed", "receptor_feed_allowed",
            "start_release_granted", "repeatability_run_allowed", "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError):
                replace(accepted, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryAcceptanceError):
            call_public_av_return_replication_repeatability_single_slot_accepted_factories(accepted)

    def test_json_contains_no_references_instances_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_factory_acceptance_to_jsonable(
            accept_public_av_return_replication_repeatability_single_slot_factory_binding(self.binding)
        )
        self.assertTrue(payload["factory_acceptance_complete"])
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)


if __name__ == "__main__":
    unittest.main()
