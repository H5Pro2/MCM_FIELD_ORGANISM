from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.public_av_return_replication_preflight import (
    PublicAVReturnReplicationPreflightError,
    audit_public_av_return_replication_preflight,
    public_av_return_replication_preflight_public_roles,
)
from mcm_field_organism.public_av_return_replication_runner import (
    wire_public_av_return_replication_runner,
)
from mcm_field_organism.public_media_source_contract import (
    PublicMediaSourceAudit,
    nasa_earthrise_av_source_contract,
)


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


class PublicAVReturnReplicationPreflightTests(unittest.TestCase):
    def test_preflight_grants_exactly_one_bounded_replication_when_all_gates_match(self) -> None:
        preflight = audit_public_av_return_replication_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
        )
        self.assertTrue(preflight.source_audit_accepted)
        self.assertTrue(preflight.preregistration_id_matches)
        self.assertTrue(preflight.compatibility_audit_id_matches)
        self.assertTrue(preflight.permutation_contract_digest_matches)
        self.assertTrue(preflight.arm_ids_complete)
        self.assertEqual(6, preflight.arm_count)
        self.assertTrue(preflight.all_arms_structurally_supported)
        self.assertTrue(preflight.fixed_field_parameters_match_preregistration)
        self.assertTrue(preflight.runner_wiring_non_executable)
        self.assertTrue(preflight.runner_run_lock_engaged)
        self.assertTrue(preflight.single_bounded_replication_run_release_granted)
        self.assertEqual(1, preflight.repeat_count_authorized)
        self.assertFalse(preflight.field_run_started)

    def test_intervals_and_release_scope_are_constructively_enforced(self) -> None:
        preflight = audit_public_av_return_replication_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
        )
        self.assertEqual((0, 500_000_000), preflight.stage_one_interval_ticks)
        self.assertEqual((500_000_000, 600_000_000), preflight.resolution_interval_ticks)
        self.assertEqual((600_000_000, 1_100_000_000), preflight.stage_two_interval_ticks)
        self.assertEqual(
            "one_public_av_six_arm_return_replication_0p5s_plus_0p1s_gap",
            preflight.release_scope,
        )
        with self.assertRaisesRegex(PublicAVReturnReplicationPreflightError, "intervals"):
            replace(preflight, stage_two_interval_ticks=(600_000_000, 1_000_000_000))
        with self.assertRaisesRegex(PublicAVReturnReplicationPreflightError, "exactly one"):
            replace(preflight, repeat_count_authorized=2)

    def test_negative_source_audit_blocks_release(self) -> None:
        contract = nasa_earthrise_av_source_contract()
        negative = PublicMediaSourceAudit(
            contract.source_id,
            True,
            True,
            False,
            False,
            contract.expected_size_bytes,
            "0" * 40,
        )
        preflight = audit_public_av_return_replication_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=negative,
        )
        self.assertFalse(preflight.source_audit_accepted)
        self.assertFalse(preflight.source_sha1_matches)
        self.assertFalse(preflight.single_bounded_replication_run_release_granted)

    def test_runner_identity_is_bound_to_preflight(self) -> None:
        wiring = wire_public_av_return_replication_runner()
        preflight = audit_public_av_return_replication_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
            wiring=wiring,
        )
        self.assertTrue(preflight.compatibility_audit_id_matches)
        altered = replace(wiring, compatibility_audit_id="other.audit")
        preflight = audit_public_av_return_replication_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
            wiring=altered,
        )
        self.assertFalse(preflight.compatibility_audit_id_matches)
        self.assertFalse(preflight.single_bounded_replication_run_release_granted)

    def test_preflight_does_not_start_run_decode_media_feed_receptors_or_release_claims(self) -> None:
        preflight = audit_public_av_return_replication_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
        )
        self.assertFalse(preflight.media_decode_allowed)
        self.assertFalse(preflight.receptor_feed_allowed)
        with self.assertRaisesRegex(PublicAVReturnReplicationPreflightError, "cannot start"):
            replace(preflight, field_run_started=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationPreflightError, "cannot start"):
            replace(preflight, memory_claim_allowed=True)
        with self.assertRaisesRegex(PublicAVReturnReplicationPreflightError, "cannot start"):
            replace(preflight, organization_threshold_defined=True)

    def test_public_roles_exclude_payloads_and_claim_scores(self) -> None:
        forbidden = {
            "raw_samples",
            "pixels",
            "container_metadata",
            "label",
            "reward",
            "memory_score",
            "meaning_score",
            "organization_score",
            "field_state",
        }
        self.assertTrue(forbidden.isdisjoint(public_av_return_replication_preflight_public_roles()))


if __name__ == "__main__":
    unittest.main()
