from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.public_av_no_input_gap_audit import (
    audit_public_av_no_input_gap_step_time,
)
from mcm_field_organism.public_av_two_stage_return_preflight import (
    PublicAVTwoStageReturnPreflightError,
    audit_public_av_two_stage_return_preflight,
    public_av_two_stage_return_preflight_public_roles,
)
from mcm_field_organism.public_av_two_stage_return_runner import (
    wire_public_av_two_stage_return_runner,
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


class PublicAVTwoStageReturnPreflightTests(unittest.TestCase):
    def test_preflight_grants_only_one_bounded_run_when_all_gates_match(self) -> None:
        preflight = audit_public_av_two_stage_return_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
        )
        self.assertTrue(preflight.source_audit_accepted)
        self.assertTrue(preflight.runner_id_matches_gap_audit)
        self.assertTrue(preflight.preregistration_id_matches)
        self.assertTrue(preflight.intervals_fixed)
        self.assertTrue(preflight.no_input_gap_contact_free)
        self.assertTrue(preflight.fixed_field_parameters_match_preregistration)
        self.assertTrue(preflight.single_bounded_run_release_granted)
        self.assertFalse(preflight.field_run_started)

    def test_fixed_intervals_and_release_scope_are_constructively_enforced(self) -> None:
        preflight = audit_public_av_two_stage_return_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
        )
        self.assertEqual((0, 500_000_000), preflight.stage_one_interval_ticks)
        self.assertEqual((500_000_000, 600_000_000), preflight.resolution_interval_ticks)
        self.assertEqual((600_000_000, 1_100_000_000), preflight.stage_two_interval_ticks)
        self.assertEqual(
            "one_public_av_two_stage_return_run_0p5s_plus_0p1s_gap",
            preflight.release_scope,
        )
        with self.assertRaisesRegex(PublicAVTwoStageReturnPreflightError, "intervals"):
            replace(preflight, stage_two_interval_ticks=(600_000_000, 1_000_000_000))

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
        preflight = audit_public_av_two_stage_return_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=negative,
        )
        self.assertFalse(preflight.source_audit_accepted)
        self.assertFalse(preflight.source_sha1_matches)
        self.assertFalse(preflight.single_bounded_run_release_granted)

    def test_gap_and_runner_identities_are_bound(self) -> None:
        wiring = wire_public_av_two_stage_return_runner()
        gap = audit_public_av_no_input_gap_step_time(wiring)
        preflight = audit_public_av_two_stage_return_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
            wiring=wiring,
            gap_audit=gap,
        )
        self.assertTrue(preflight.runner_id_matches_gap_audit)
        preflight = audit_public_av_two_stage_return_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
            wiring=wiring,
            gap_audit=replace(gap, runner_id="other.runner"),
        )
        self.assertFalse(preflight.runner_id_matches_gap_audit)
        self.assertFalse(preflight.single_bounded_run_release_granted)

    def test_preflight_does_not_start_run_or_release_claims(self) -> None:
        preflight = audit_public_av_two_stage_return_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
        )
        with self.assertRaisesRegex(PublicAVTwoStageReturnPreflightError, "cannot start"):
            replace(preflight, field_run_started=True)
        with self.assertRaisesRegex(PublicAVTwoStageReturnPreflightError, "cannot start"):
            replace(preflight, memory_claim_allowed=True)

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
        }
        self.assertTrue(forbidden.isdisjoint(public_av_two_stage_return_preflight_public_roles()))


if __name__ == "__main__":
    unittest.main()
