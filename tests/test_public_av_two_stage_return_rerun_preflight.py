from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.public_av_two_stage_return_rerun_preflight import (
    PublicAVTwoStageReturnRerunPreflightError,
    audit_public_av_two_stage_return_rerun_preflight,
    public_av_two_stage_return_rerun_preflight_public_roles,
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


class PublicAVTwoStageReturnRerunPreflightTests(unittest.TestCase):
    def test_corrected_nullable_baseline_role_is_accepted_for_one_run(self) -> None:
        preflight = audit_public_av_two_stage_return_rerun_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
        )
        self.assertEqual(
            "post_resolution_snapshot_digest",
            preflight.nullable_baseline_role,
        )
        self.assertTrue(preflight.nullable_baseline_role_accepted)
        self.assertTrue(preflight.baseline_null_snapshot_is_not_synthetic)
        self.assertTrue(preflight.continued_snapshot_digest_required)
        self.assertTrue(preflight.base_single_run_release_granted)
        self.assertTrue(preflight.corrected_single_run_release_granted)
        self.assertEqual(1, preflight.repeat_count_authorized)
        self.assertFalse(preflight.field_run_started)

    def test_release_scope_and_claim_sperren_are_constructive(self) -> None:
        preflight = audit_public_av_two_stage_return_rerun_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=accepted_source_audit(),
        )
        self.assertEqual(
            "one_corrected_public_av_two_stage_return_run_nullable_baseline_v1",
            preflight.release_scope,
        )
        with self.assertRaisesRegex(PublicAVTwoStageReturnRerunPreflightError, "cannot start"):
            replace(preflight, field_run_started=True)
        with self.assertRaisesRegex(PublicAVTwoStageReturnRerunPreflightError, "cannot start"):
            replace(preflight, organization_claim_allowed=True)
        with self.assertRaisesRegex(PublicAVTwoStageReturnRerunPreflightError, "exactly"):
            replace(preflight, repeat_count_authorized=2)

    def test_negative_source_audit_keeps_corrected_release_closed(self) -> None:
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
        preflight = audit_public_av_two_stage_return_rerun_preflight(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            source_audit=negative,
        )
        self.assertFalse(preflight.base_single_run_release_granted)
        self.assertFalse(preflight.corrected_single_run_release_granted)

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
        self.assertTrue(
            forbidden.isdisjoint(public_av_two_stage_return_rerun_preflight_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
