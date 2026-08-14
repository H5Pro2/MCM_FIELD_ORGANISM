from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.public_av_container_source import PUBLIC_MEDIA_CLOCK_ID
from mcm_field_organism.public_av_interval_audit import (
    PublicAVCommonIntervalAudit,
    PublicAVIntervalAuditError,
    public_av_interval_audit_json_value,
    public_av_interval_audit_public_roles,
    run_public_av_interval_audit,
)
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


NASA_SOURCE = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


class PublicAVIntervalAuditTests(unittest.TestCase):
    def test_audits_monotonic_bounded_repeatable_common_pts_axis(self) -> None:
        result = run_public_av_interval_audit(
            NASA_SOURCE,
            nasa_earthrise_av_source_contract(),
            duration_seconds=0.5,
        )

        self.assertEqual(PUBLIC_MEDIA_CLOCK_ID, result.clock_id)
        self.assertTrue(result.shared_clock)
        self.assertTrue(result.audio.monotonic)
        self.assertTrue(result.video.monotonic)
        self.assertTrue(result.audio.non_overlapping)
        self.assertTrue(result.video.non_overlapping)
        self.assertTrue(result.audio.bounded_to_limit)
        self.assertTrue(result.video.bounded_to_limit)
        self.assertGreater(result.common_axis_overlap_ticks, 0)
        self.assertEqual(
            result.audio.interval_digest,
            result.repeated_audio_interval_digest,
        )
        self.assertEqual(
            result.video.interval_digest,
            result.repeated_video_interval_digest,
        )
        self.assertTrue(result.repeatable)
        self.assertFalse(result.accepted_for_receptor_run)
        self.assertFalse(result.field_run_allowed)

    def test_disjoint_interval_is_repeatable_on_local_axis(self) -> None:
        result = run_public_av_interval_audit(
            NASA_SOURCE,
            nasa_earthrise_av_source_contract(),
            duration_seconds=0.5,
            start_tick=500_000_000,
        )

        self.assertEqual(500_000_000, result.source_start_tick)
        self.assertEqual(1_000_000_000, result.source_end_tick)
        self.assertEqual(0, result.audio.first_start_tick)
        self.assertEqual(0, result.video.first_start_tick)
        self.assertTrue(result.repeatable)

    def test_json_artifact_contains_no_raw_payload_or_metadata(self) -> None:
        result = run_public_av_interval_audit(
            NASA_SOURCE,
            nasa_earthrise_av_source_contract(),
            duration_seconds=0.5,
        )
        document = public_av_interval_audit_json_value(result)

        self.assertNotIn("samples", str(document))
        self.assertNotIn("pixels", str(document))
        self.assertNotIn("description", str(document))
        self.assertFalse(document["metadata_used_by_receptor"])
        self.assertFalse(document["raw_payload_retained"])

    def test_public_roles_exclude_receptor_memory_and_payload_roles(self) -> None:
        forbidden = {
            "receptor_values",
            "field_state",
            "memory",
            "meaning",
            "reward",
            "raw_audio",
            "raw_video",
            "samples",
            "pixels",
        }

        self.assertTrue(forbidden.isdisjoint(public_av_interval_audit_public_roles()))

    def test_interval_audit_cannot_release_receptors_or_fields(self) -> None:
        result = run_public_av_interval_audit(
            NASA_SOURCE,
            nasa_earthrise_av_source_contract(),
            duration_seconds=0.5,
        )

        with self.assertRaisesRegex(PublicAVIntervalAuditError, "cannot release"):
            PublicAVCommonIntervalAudit(
                clock_id=result.clock_id,
                ticks_per_second=result.ticks_per_second,
                source_start_tick=result.source_start_tick,
                source_end_tick=result.source_end_tick,
                duration_limit_ticks=result.duration_limit_ticks,
                audio=result.audio,
                video=result.video,
                shared_clock=result.shared_clock,
                common_axis_overlap_ticks=result.common_axis_overlap_ticks,
                repeated_audio_interval_digest=result.repeated_audio_interval_digest,
                repeated_video_interval_digest=result.repeated_video_interval_digest,
                repeatable=result.repeatable,
                accepted_for_receptor_run=True,
            )


if __name__ == "__main__":
    unittest.main()
