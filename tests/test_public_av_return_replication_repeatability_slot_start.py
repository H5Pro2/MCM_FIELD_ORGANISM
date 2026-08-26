from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.public_av_return_replication_repeatability_preflight import (
    audit_public_av_return_replication_repeatability_preflight,
)
from mcm_field_organism.public_av_return_replication_repeatability_runner import (
    wire_public_av_return_replication_repeatability_runner,
)
from mcm_field_organism.public_av_return_replication_repeatability_slot_start import (
    PublicAVReturnReplicationRepeatabilitySlotStartError,
    bind_public_av_return_replication_repeatability_slots,
    public_av_return_replication_repeatability_slot_start_json_value,
    public_av_return_replication_repeatability_slot_start_public_roles,
)
from mcm_field_organism.public_media_source_contract import PublicMediaSourceAudit, nasa_earthrise_av_source_contract


MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


def accepted_source_audit() -> PublicMediaSourceAudit:
    source = nasa_earthrise_av_source_contract()
    return PublicMediaSourceAudit(source.source_id, True, True, True, True, source.expected_size_bytes, source.expected_sha1)


class PublicAVReturnReplicationRepeatabilitySlotStartTests(unittest.TestCase):
    def setUp(self) -> None:
        self.wiring = wire_public_av_return_replication_repeatability_runner()
        self.preflight = audit_public_av_return_replication_repeatability_preflight(
            MEDIA, source_audit=accepted_source_audit(), repeatability_wiring=self.wiring,
        )

    def test_three_positive_preflights_are_bound_to_unique_slot_identities(self) -> None:
        contract = bind_public_av_return_replication_repeatability_slots(self.wiring, self.preflight)
        self.assertEqual((1, 2, 3), tuple(item.repeat_index for item in contract.slot_bindings))
        self.assertEqual(3, len({item.binding_id for item in contract.slot_bindings}))
        self.assertEqual(3, len({item.one_shot_entrypoint_id for item in contract.slot_bindings}))

    def test_bindings_require_fresh_uncreated_entrypoints_and_no_executor(self) -> None:
        contract = bind_public_av_return_replication_repeatability_slots(self.wiring, self.preflight)
        for item in contract.slot_bindings:
            self.assertTrue(item.positive_preflight_bound)
            self.assertTrue(item.one_shot_release_unconsumed)
            self.assertTrue(item.fresh_entrypoint_required)
            self.assertFalse(item.entrypoint_instance_created)
            self.assertFalse(item.executor_bound)
            self.assertFalse(item.start_allowed)

    def test_consumed_slot_preflight_is_rejected(self) -> None:
        with self.assertRaisesRegex(Exception, "fresh"):
            slot = replace(
                self.preflight.repeat_slot_preflights[0],
                one_shot_release_unconsumed=False,
                repeat_run_started=True,
            )
            altered = replace(self.preflight, repeat_slot_preflights=(slot, *self.preflight.repeat_slot_preflights[1:]))
            bind_public_av_return_replication_repeatability_slots(self.wiring, altered)

    def test_start_executor_loop_and_claim_releases_are_blocked(self) -> None:
        contract = bind_public_av_return_replication_repeatability_slots(self.wiring, self.preflight)
        for role in ("executor_binding_allowed", "repeatability_run_allowed", "automatic_repeat_loop_available", "memory_claim_allowed"):
            with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilitySlotStartError, "cannot release"):
                replace(contract, **{role: True})

    def test_json_and_roles_exclude_payloads_and_scores(self) -> None:
        contract = bind_public_av_return_replication_repeatability_slots(self.wiring, self.preflight)
        self.assertIn("one_shot_entrypoint_id", repr(public_av_return_replication_repeatability_slot_start_json_value(contract)))
        forbidden = {"samples", "pixels", "memory_score", "organization_score", "reward", "target_topology"}
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_repeatability_slot_start_public_roles()))


if __name__ == "__main__":
    unittest.main()
