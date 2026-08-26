from __future__ import annotations

from pathlib import Path
import unittest

import numpy as np

from mcm_field_organism.public_av_container_source import (
    PUBLIC_MEDIA_CLOCK_ID,
    PublicAVContainerSourceError,
    decode_audited_public_av_sources,
)
from mcm_field_organism.public_media_source_contract import (
    PublicMediaSourceContract,
    nasa_earthrise_av_source_contract,
)


class PublicAVContainerSourceTests(unittest.TestCase):
    def test_audited_nasa_container_yields_bounded_shared_clock_sources(self) -> None:
        sources = decode_audited_public_av_sources(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            nasa_earthrise_av_source_contract(),
            duration_seconds=0.5,
        )

        self.assertTrue(sources.source_audit.accepted)
        self.assertEqual(PUBLIC_MEDIA_CLOCK_ID, sources.clock_id)
        self.assertEqual(48_000, sources.sample_rate)
        self.assertGreater(sources.audio.frame_count, 0)
        self.assertGreater(sources.video.frame_count, 0)
        samples, audio_start, audio_end = sources.audio.read_timed_frame()
        frame, video_start, video_end = sources.video.read_timed_frame()
        self.assertEqual(480, len(samples))
        self.assertEqual((240, 320, 3), frame.shape)
        self.assertEqual(np.uint8, frame.dtype)
        self.assertFalse(frame.flags.writeable)
        self.assertLess(audio_start, audio_end)
        self.assertLess(video_start, video_end)
        self.assertEqual(PUBLIC_MEDIA_CLOCK_ID, sources.audio.capture_clock_id)
        self.assertEqual(PUBLIC_MEDIA_CLOCK_ID, sources.video.capture_clock_id)
        self.assertEqual(0, sources.source_start_tick)
        self.assertEqual(500_000_000, sources.source_end_tick)

    def test_disjoint_interval_uses_local_time_and_keeps_absolute_bounds(self) -> None:
        sources = decode_audited_public_av_sources(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            nasa_earthrise_av_source_contract(),
            duration_seconds=0.5,
            start_tick=500_000_000,
        )

        self.assertEqual(500_000_000, sources.source_start_tick)
        self.assertEqual(1_000_000_000, sources.source_end_tick)
        _, audio_start, audio_end = sources.audio.read_timed_frame()
        _, video_start, video_end = sources.video.read_timed_frame()
        self.assertEqual(0, audio_start)
        self.assertLess(audio_start, audio_end)
        self.assertEqual(0, video_start)
        self.assertLess(video_start, video_end)
        self.assertLessEqual(audio_end, 500_000_000)
        self.assertLessEqual(video_end, 500_000_000)

    def test_failed_integrity_gate_prevents_container_open(self) -> None:
        wrong = PublicMediaSourceContract("source.wrong", 1, "0" * 40)

        with self.assertRaisesRegex(PublicAVContainerSourceError, "integrity"):
            decode_audited_public_av_sources(
                Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
                wrong,
                duration_seconds=0.5,
            )

    def test_start_tick_must_be_non_negative_integer(self) -> None:
        with self.assertRaisesRegex(PublicAVContainerSourceError, "start_tick"):
            decode_audited_public_av_sources(
                Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
                nasa_earthrise_av_source_contract(),
                duration_seconds=0.5,
                start_tick=-1,
            )


if __name__ == "__main__":
    unittest.main()
