from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.public_av_return_permutation_contract import public_av_return_permutation_contract
from mcm_field_organism.public_av_return_replication_repeatability_executor_binding import (
    PublicAVReturnReplicationRepeatabilityExecutorBindingError,
    bind_public_av_return_replication_repeatability_slot_executors,
    public_av_return_replication_repeatability_executor_binding_json_value,
    public_av_return_replication_repeatability_executor_binding_public_roles,
)
from mcm_field_organism.public_av_return_replication_repeatability_preflight import (
    audit_public_av_return_replication_repeatability_preflight,
)
from mcm_field_organism.public_av_return_replication_repeatability_runner import (
    wire_public_av_return_replication_repeatability_runner,
)
from mcm_field_organism.public_av_return_replication_repeatability_slot_start import (
    bind_public_av_return_replication_repeatability_slots,
)
from mcm_field_organism.public_av_return_replication_runner import wire_public_av_return_replication_runner
from mcm_field_organism.public_media_source_contract import PublicMediaSourceAudit, nasa_earthrise_av_source_contract


MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


def accepted_source_audit() -> PublicMediaSourceAudit:
    source = nasa_earthrise_av_source_contract()
    return PublicMediaSourceAudit(source.source_id, True, True, True, True, source.expected_size_bytes, source.expected_sha1)


class PublicAVReturnReplicationRepeatabilityExecutorBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.permutation = public_av_return_permutation_contract()
        self.base_wiring = wire_public_av_return_replication_runner(permutation_contract=self.permutation)
        self.repeatability_wiring = wire_public_av_return_replication_repeatability_runner(base_wiring=self.base_wiring)
        self.preflight = audit_public_av_return_replication_repeatability_preflight(
            MEDIA,
            source_audit=accepted_source_audit(),
            repeatability_wiring=self.repeatability_wiring,
            base_wiring=self.base_wiring,
            permutation_contract=self.permutation,
        )
        self.slot_start = bind_public_av_return_replication_repeatability_slots(
            self.repeatability_wiring,
            self.preflight,
        )

    def test_three_slots_get_unique_future_executor_identities(self) -> None:
        contract = bind_public_av_return_replication_repeatability_slot_executors(
            self.slot_start,
            self.base_wiring,
            self.permutation,
        )
        self.assertEqual((1, 2, 3), tuple(item.repeat_index for item in contract.slot_executor_bindings))
        self.assertEqual(3, len({item.executor_binding_id for item in contract.slot_executor_bindings}))
        self.assertEqual(3, len({item.future_executor_id for item in contract.slot_executor_bindings}))
        self.assertFalse(contract.executor_callables_created)
        self.assertFalse(contract.entrypoint_instances_created)

    def test_preflight_runner_and_permutation_identities_are_bound_per_slot(self) -> None:
        contract = bind_public_av_return_replication_repeatability_slot_executors(
            self.slot_start,
            self.base_wiring,
            self.permutation,
        )
        for item in contract.slot_executor_bindings:
            self.assertEqual(self.slot_start.repeatability_preflight_id, item.repeatability_preflight_id)
            self.assertEqual(self.base_wiring.runner_id, item.base_runner_id)
            self.assertEqual(self.permutation.contract_id, item.permutation_contract_id)
            self.assertEqual(self.permutation.contract_digest, item.permutation_contract_digest)
            self.assertTrue(item.preflight_identity_bound)
            self.assertTrue(item.runner_identity_bound)
            self.assertTrue(item.permutation_identity_bound)

    def test_slot_start_with_created_entrypoint_is_rejected(self) -> None:
        with self.assertRaisesRegex(Exception, "fresh"):
            altered_slot = replace(self.slot_start.slot_bindings[0], entrypoint_instance_created=True)
            altered = replace(self.slot_start, slot_bindings=(altered_slot, *self.slot_start.slot_bindings[1:]))
            bind_public_av_return_replication_repeatability_slot_executors(
                altered,
                self.base_wiring,
                self.permutation,
            )

    def test_permutation_identity_mismatch_is_rejected(self) -> None:
        altered_wiring = replace(self.base_wiring, permutation_contract_digest="0" * 64)
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityExecutorBindingError, "permutation"):
            bind_public_av_return_replication_repeatability_slot_executors(
                self.slot_start,
                altered_wiring,
                self.permutation,
            )

    def test_executor_start_loop_and_claim_releases_are_blocked(self) -> None:
        contract = bind_public_av_return_replication_repeatability_slot_executors(
            self.slot_start,
            self.base_wiring,
            self.permutation,
        )
        for role in (
            "executor_binding_allowed",
            "start_allowed",
            "repeatability_run_allowed",
            "automatic_repeat_loop_available",
            "memory_claim_allowed",
        ):
            with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityExecutorBindingError, "cannot create"):
                replace(contract, **{role: True})

    def test_json_and_roles_exclude_payloads_and_scores(self) -> None:
        contract = bind_public_av_return_replication_repeatability_slot_executors(
            self.slot_start,
            self.base_wiring,
            self.permutation,
        )
        self.assertIn(
            "future_executor_id",
            repr(public_av_return_replication_repeatability_executor_binding_json_value(contract)),
        )
        forbidden = {"samples", "pixels", "memory_score", "organization_score", "reward", "target_topology"}
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_repeatability_executor_binding_public_roles()))


if __name__ == "__main__":
    unittest.main()
