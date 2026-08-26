from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.public_av_return_replication_preflight import audit_public_av_return_replication_preflight
from mcm_field_organism.public_av_return_replication_repeatability_preflight import (
    PublicAVReturnReplicationRepeatabilityPreflightError,
    audit_public_av_return_replication_repeatability_preflight,
    public_av_return_replication_repeatability_preflight_json_value,
    public_av_return_replication_repeatability_preflight_public_roles,
)
from mcm_field_organism.public_av_return_replication_repeatability_runner import (
    wire_public_av_return_replication_repeatability_runner,
)
from mcm_field_organism.public_av_return_replication_runner import wire_public_av_return_replication_runner
from mcm_field_organism.public_media_source_contract import (
    PublicMediaSourceAudit,
    nasa_earthrise_av_source_contract,
)


MEDIA = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


def accepted_source_audit() -> PublicMediaSourceAudit:
    contract = nasa_earthrise_av_source_contract()
    return PublicMediaSourceAudit(
        contract.source_id,
        True,
        True,
        True,
        True,
        contract.expected_size_bytes,
        contract.expected_sha1,
    )


class PublicAVReturnReplicationRepeatabilityPreflightTests(unittest.TestCase):
    def test_three_repeat_slots_require_separate_unconsumed_one_shot_releases(self) -> None:
        preflight = audit_public_av_return_replication_repeatability_preflight(
            MEDIA,
            source_audit=accepted_source_audit(),
        )
        self.assertEqual((1, 2, 3), tuple(slot.repeat_index for slot in preflight.repeat_slot_preflights))
        self.assertTrue(preflight.all_slots_have_separate_unconsumed_one_shot_release)
        self.assertTrue(all(slot.positive_one_shot_release_available for slot in preflight.repeat_slot_preflights))
        self.assertTrue(all(slot.one_shot_release_unconsumed for slot in preflight.repeat_slot_preflights))
        self.assertFalse(preflight.repeatability_run_allowed)

    def test_contract_parameters_are_identical_and_state_carry_is_absent(self) -> None:
        preflight = audit_public_av_return_replication_repeatability_preflight(
            MEDIA,
            source_audit=accepted_source_audit(),
        )
        self.assertTrue(preflight.identical_contract_parameters_across_slots)
        self.assertTrue(preflight.no_cross_repeat_state_carry)
        for slot in preflight.repeat_slot_preflights:
            self.assertTrue(slot.contract_parameters_identical)
            self.assertTrue(slot.fresh_runner_instance_required)
            self.assertTrue(slot.fresh_field_at_repeat_start)
            self.assertTrue(slot.cross_repeat_state_carry_absent)
            self.assertFalse(slot.prior_execution_receipt_reusable)

    def test_consumed_or_mismatched_slot_preflight_is_rejected(self) -> None:
        source = accepted_source_audit()
        base = wire_public_av_return_replication_runner()
        slots = tuple(
            audit_public_av_return_replication_preflight(MEDIA, source_audit=source, wiring=base)
            for _ in range(3)
        )
        with self.assertRaisesRegex(Exception, "cannot start"):
            replace(slots[0], field_run_started=True)

        mismatched = (replace(slots[0], media_path="different.mp4"), slots[1], slots[2])
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityPreflightError, "fresh"):
            audit_public_av_return_replication_repeatability_preflight(
                MEDIA,
                source_audit=source,
                base_wiring=base,
                slot_preflights=mismatched,
            )

    def test_runner_locks_and_claims_are_constructively_blocked(self) -> None:
        preflight = audit_public_av_return_replication_repeatability_preflight(
            MEDIA,
            source_audit=accepted_source_audit(),
        )
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityPreflightError, "cannot release"):
            replace(preflight, repeatability_run_allowed=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityPreflightError, "cannot release"):
            replace(preflight, automatic_repeat_loop_available=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityPreflightError, "cannot release"):
            replace(preflight, stability_threshold_defined=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationRepeatabilityPreflightError, "cannot release"):
            replace(preflight, memory_claim_allowed=True)

    def test_repeatability_runner_with_state_carry_is_rejected_before_preflight(self) -> None:
        source = accepted_source_audit()
        wiring = wire_public_av_return_replication_repeatability_runner()
        with self.assertRaisesRegex(Exception, "fresh"):
            altered_slot = replace(wiring.repeat_slots[0], cross_repeat_state_carry_allowed=True)
            replace(wiring, repeat_slots=(altered_slot, *wiring.repeat_slots[1:]))
        preflight = audit_public_av_return_replication_repeatability_preflight(
            MEDIA,
            source_audit=source,
            repeatability_wiring=wiring,
        )
        self.assertTrue(preflight.all_slots_non_executable)

    def test_json_and_public_roles_exclude_payloads_and_claim_scores(self) -> None:
        preflight = audit_public_av_return_replication_repeatability_preflight(
            MEDIA,
            source_audit=accepted_source_audit(),
        )
        encoded = repr(public_av_return_replication_repeatability_preflight_json_value(preflight))
        self.assertIn("repeat_slot_preflights", encoded)
        forbidden = {
            "samples",
            "pixels",
            "memory_score",
            "organization_score",
            "meaning_score",
            "label",
            "reward",
            "target_topology",
        }
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_repeatability_preflight_public_roles()))


if __name__ == "__main__":
    unittest.main()
