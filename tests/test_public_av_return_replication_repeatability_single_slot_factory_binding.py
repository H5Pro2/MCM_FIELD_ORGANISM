from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_single_slot_construction_acceptance import (
    accept_public_av_return_replication_repeatability_single_slot_construction,
)
from mcm_field_organism.public_av_return_replication_repeatability_single_slot_factory_binding import (
    PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError,
    bind_public_av_return_replication_repeatability_single_slot_factories,
    call_public_av_return_replication_repeatability_single_slot_factories,
    public_av_return_replication_repeatability_single_slot_factory_binding_to_jsonable,
)
from tests.test_public_av_return_replication_repeatability_single_slot_construction_acceptance import (
    PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceTests,
)


class PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingTests(
    PublicAVReturnReplicationRepeatabilitySingleSlotConstructionAcceptanceTests
):
    def setUp(self) -> None:
        super().setUp()
        self.acceptance = accept_public_av_return_replication_repeatability_single_slot_construction(
            self.construction
        )

    def test_binds_constructor_identities_to_future_factory_identities(self) -> None:
        binding = bind_public_av_return_replication_repeatability_single_slot_factories(
            self.acceptance
        )
        self.assertTrue(binding.construction_acceptance_bound)
        self.assertTrue(binding.constructor_identities_bound)
        self.assertTrue(binding.callable_factory_identity_bound)
        self.assertTrue(binding.gate_factory_identity_bound)
        self.assertTrue(binding.factory_identities_unique)
        self.assertIn("single-slot-callable-factory", binding.future_callable_factory_id)
        self.assertIn("single-slot-gate-factory", binding.future_gate_factory_id)

    def test_preserves_accepted_slot_and_object_identities(self) -> None:
        binding = bind_public_av_return_replication_repeatability_single_slot_factories(
            self.acceptance
        )
        for role in (
            "selected_repeat_index", "construction_id", "object_reservation_id",
            "instantiation_order_id", "candidate_id", "logical_callable_id",
            "logical_gate_id", "reserved_executor_id", "future_callable_object_id",
            "future_gate_object_id", "callable_constructor_id", "gate_constructor_id",
            "source_id",
        ):
            self.assertEqual(getattr(self.acceptance, role), getattr(binding, role))

    def test_rejects_changed_acceptance_state(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.acceptance, constructor_invoked=True)
            bind_public_av_return_replication_repeatability_single_slot_factories(changed)

    def test_rejects_non_unique_factory_identities(self) -> None:
        binding = bind_public_av_return_replication_repeatability_single_slot_factories(
            self.acceptance
        )
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError):
            replace(binding, future_gate_factory_id=binding.future_callable_factory_id)

    def test_factory_references_objects_media_receptors_run_and_claims_remain_locked(self) -> None:
        binding = bind_public_av_return_replication_repeatability_single_slot_factories(
            self.acceptance
        )
        for role in (
            "callable_factory_reference_stored", "gate_factory_reference_stored",
            "callable_reference_stored", "factory_function_called",
            "callable_factory_called", "gate_factory_called", "callable_object_created",
            "gate_object_created", "constructor_invoked", "binding_performed",
            "media_decode_allowed", "receptor_feed_allowed", "start_release_granted",
            "repeatability_run_allowed", "memory_claim_allowed",
        ):
            with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError):
                replace(binding, **{role: True})
        with self.assertRaises(PublicAVReturnReplicationRepeatabilitySingleSlotFactoryBindingError):
            call_public_av_return_replication_repeatability_single_slot_factories(binding)

    def test_json_contains_no_factories_callables_instances_payloads_results_or_scores(self) -> None:
        payload = public_av_return_replication_repeatability_single_slot_factory_binding_to_jsonable(
            bind_public_av_return_replication_repeatability_single_slot_factories(self.acceptance)
        )
        self.assertTrue(payload["factory_identities_unique"])
        self.assertNotIn("factory_callable", payload)
        self.assertNotIn("callable_ref", payload)
        self.assertNotIn("instance", payload)
        self.assertNotIn("result", payload)
        self.assertNotIn("memory_score", payload)


if __name__ == "__main__":
    unittest.main()
