from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.finite_video_path import VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig
from mcm_field_organism.public_av_receptor_run import (
    PublicAVReceptorRun,
    PublicAVReceptorRunError,
    public_av_receptor_event_timeline,
    public_av_receptor_run_json_value,
    public_av_receptor_run_public_roles,
    run_public_av_receptor_run,
)
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


NASA_SOURCE = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


def receptor_run() -> PublicAVReceptorRun:
    return run_public_av_receptor_run(
        NASA_SOURCE,
        nasa_earthrise_av_source_contract(),
        LogSpectralConfig(),
        VisualGridConfig(320, 240, 10, 8, 29.97),
        duration_seconds=0.5,
    )


class PublicAVReceptorRunTests(unittest.TestCase):
    def test_reduces_audio_and_video_without_field_release(self) -> None:
        result = receptor_run()

        self.assertEqual(41, len(result.auditory_frames))
        self.assertEqual(15, len(result.visual_frames))
        self.assertTrue(result.repeatable)
        self.assertFalse(result.raw_payload_retained)
        self.assertFalse(result.metadata_used_by_receptor)
        self.assertFalse(result.field_run_allowed)
        self.assertEqual(
            result.auditory_sequence_digest,
            result.repeated_auditory_sequence_digest,
        )
        self.assertEqual(
            result.visual_sequence_digest,
            result.repeated_visual_sequence_digest,
        )

    def test_output_contains_intervals_and_digests_but_no_payload_values(self) -> None:
        document = public_av_receptor_run_json_value(receptor_run())
        rendered = str(document)

        self.assertIn("receptor_state_digest", rendered)
        self.assertNotIn("samples", rendered)
        self.assertNotIn("pixels", rendered)
        self.assertNotIn("energy", rendered)
        self.assertNotIn("channel_values", rendered)

    def test_disjoint_interval_has_local_event_timeline_and_absolute_bounds(self) -> None:
        result = run_public_av_receptor_run(
            NASA_SOURCE,
            nasa_earthrise_av_source_contract(),
            LogSpectralConfig(),
            VisualGridConfig(320, 240, 10, 8, 29.97),
            duration_seconds=0.5,
            start_tick=500_000_000,
        )
        timeline, digest = public_av_receptor_event_timeline(result)
        repeated_timeline, repeated_digest = public_av_receptor_event_timeline(result)

        self.assertEqual(500_000_000, result.source_start_tick)
        self.assertEqual(1_000_000_000, result.source_end_tick)
        self.assertEqual(57, len(timeline))
        self.assertGreater(timeline[0]["elapsed_ticks"], 0)
        self.assertLessEqual(timeline[-1]["elapsed_ticks"], 500_000_000)
        self.assertEqual(timeline, repeated_timeline)
        self.assertEqual(digest, repeated_digest)

    def test_public_roles_exclude_field_memory_and_raw_payloads(self) -> None:
        forbidden = {
            "samples",
            "pixels",
            "energy",
            "channel_values",
            "field_state",
            "memory",
            "meaning",
            "reward",
        }

        self.assertTrue(forbidden.isdisjoint(public_av_receptor_run_public_roles()))

    def test_result_cannot_release_field_or_payloads(self) -> None:
        result = receptor_run()
        values = {
            role: getattr(result, role) for role in result.__dataclass_fields__
        }
        values["field_run_allowed"] = True

        with self.assertRaisesRegex(PublicAVReceptorRunError, "cannot retain"):
            PublicAVReceptorRun(**values)

    def test_failed_receptor_preflight_blocks_run(self) -> None:
        with self.assertRaisesRegex(PublicAVReceptorRunError, "prerequisites"):
            run_public_av_receptor_run(
                NASA_SOURCE,
                nasa_earthrise_av_source_contract(),
                LogSpectralConfig(),
                VisualGridConfig(640, 480, 10, 8, 29.97),
                duration_seconds=0.5,
            )


if __name__ == "__main__":
    unittest.main()
