from __future__ import annotations

from dataclasses import fields
import time
import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorTimeAlignmentError,
    ReceptorTimeSequence,
    audit_receptor_time_alignment,
    capture_timed_audio_video_receptors,
    receptor_time_alignment_public_roles,
)
from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import (
    LocalChannelGridReceptor,
    SyntheticVideoFrameSource,
    VisualGridConfig,
)
from mcm_field_organism.live_audio_adapter import SyntheticAudioFrameSource
from mcm_field_organism.log_spectral_receptor import (
    LogSpectralConfig,
    LogSpectralReceptor,
)


def timed_frame(
    modality: str,
    index: int,
    start: int,
    end: int,
) -> OrganismTimedReceptorFrame:
    frame = ReceptorContactFrame(
        modality_id=modality,
        geometry_id=f"{modality}.geometry.v1",
        snapshot_id=f"{modality}.receptor.{index}",
        clock_id=f"{modality}.source",
        window_start_tick=index,
        window_end_tick=index + 1,
        carrier_ids=(f"{modality}.carrier.0",),
        values=(0.25,),
    )
    return OrganismTimedReceptorFrame(
        frame,
        CommonFieldTime("organism.test", start, end),
    )


def sequence(
    modality: str,
    intervals: tuple[tuple[int, int], ...],
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        modality_id=modality,
        geometry_id=f"{modality}.geometry.v1",
        clock_id="organism.test",
        frames=tuple(
            timed_frame(modality, index, start, end)
            for index, (start, end) in enumerate(intervals)
        ),
    )


class DelayedAudioSource:
    def __init__(
        self,
        source: SyntheticAudioFrameSource,
        delay_seconds: float,
    ) -> None:
        self.source = source
        self.delay_seconds = delay_seconds

    @property
    def overflow_count(self) -> int:
        return self.source.overflow_count

    def read_frame(self) -> tuple[float, ...]:
        time.sleep(self.delay_seconds)
        return self.source.read_frame()


class DelayedVideoSource:
    def __init__(
        self,
        source: SyntheticVideoFrameSource,
        delay_seconds: float,
    ) -> None:
        self.source = source
        self.delay_seconds = delay_seconds

    def read_frame(self) -> np.ndarray:
        time.sleep(self.delay_seconds)
        return self.source.read_frame()


class ReceptorTimeAlignmentAuditTests(unittest.TestCase):
    def test_exact_one_to_one_intervals_are_reported_without_selection(self) -> None:
        auditory = sequence("auditory", ((0, 10), (10, 20)))
        visual = sequence("visual", ((1, 9), (11, 19)))
        result = audit_receptor_time_alignment(visual, auditory)

        self.assertEqual(("auditory", "visual"), result.modality_ids)
        self.assertEqual((2, 2), result.frame_counts)
        self.assertEqual(2, len(result.overlaps))
        self.assertEqual(result.overlaps, result.unambiguous_overlaps)
        self.assertEqual((), result.ambiguous_snapshot_ids)
        self.assertEqual((), result.unmatched_snapshot_ids)
        self.assertTrue(result.has_complete_one_to_one_alignment)

    def test_rate_mismatch_is_ambiguous_instead_of_forcing_a_pair(self) -> None:
        auditory = sequence(
            "auditory",
            ((0, 10), (10, 20), (20, 30)),
        )
        visual = sequence("visual", ((5, 25),))
        result = audit_receptor_time_alignment(auditory, visual)

        self.assertEqual(3, len(result.overlaps))
        self.assertEqual((), result.unambiguous_overlaps)
        self.assertEqual(
            {
                "auditory.receptor.0",
                "auditory.receptor.1",
                "auditory.receptor.2",
                "visual.receptor.0",
            },
            set(result.ambiguous_snapshot_ids),
        )
        self.assertFalse(result.has_complete_one_to_one_alignment)

    def test_nonoverlapping_state_is_reported_as_unmatched(self) -> None:
        auditory = sequence("auditory", ((0, 10),))
        visual = sequence("visual", ((20, 30),))
        result = audit_receptor_time_alignment(auditory, visual)
        self.assertEqual((), result.overlaps)
        self.assertEqual(
            {"auditory.receptor.0", "visual.receptor.0"},
            set(result.unmatched_snapshot_ids),
        )

    def test_input_order_does_not_change_canonical_audit(self) -> None:
        auditory = sequence("auditory", ((0, 10), (10, 20)))
        visual = sequence("visual", ((1, 9), (11, 19)))
        self.assertEqual(
            audit_receptor_time_alignment(auditory, visual),
            audit_receptor_time_alignment(visual, auditory),
        )

    def test_one_receptor_sequence_cannot_overlap_itself_in_time(self) -> None:
        with self.assertRaisesRegex(
            ReceptorTimeAlignmentError,
            "cannot overlap",
        ):
            sequence("auditory", ((0, 10), (9, 20)))

    def test_public_roles_retain_no_raw_sensor_payload_or_pairing_rule(self) -> None:
        roles = set(receptor_time_alignment_public_roles())
        roles.update(item.name for item in fields(ReceptorTimeSequence))
        self.assertTrue(
            {
                "raw_audio",
                "raw_video",
                "samples",
                "image",
                "gain",
                "selected_pair",
                "interpolation",
                "held_value",
                "mean_value",
            }.isdisjoint(roles)
        )


class TimedAudioVideoCaptureTests(unittest.TestCase):
    def test_every_completed_receptor_state_gets_organism_time(self) -> None:
        audio_config = LogSpectralConfig(
            sample_rate=1000,
            window_size=100,
            hop_size=20,
            min_frequency=10.0,
            max_frequency=400.0,
            band_count=4,
        )
        audio_frames = tuple(
            tuple(
                0.25
                * np.sin(
                    2.0
                    * np.pi
                    * 100.0
                    * sample
                    / audio_config.sample_rate
                )
                for sample in range(index * 20, (index + 1) * 20)
            )
            for index in range(10)
        )
        visual_config = VisualGridConfig(
            source_width=12,
            source_height=8,
            grid_columns=2,
            grid_rows=2,
            frames_per_second=10.0,
        )
        visual_frames = (
            np.full((8, 12, 3), 32, dtype=np.uint8),
            np.full((8, 12, 3), 224, dtype=np.uint8),
        )
        result = capture_timed_audio_video_receptors(
            DelayedAudioSource(
                SyntheticAudioFrameSource(audio_frames),
                delay_seconds=0.006,
            ),
            DelayedVideoSource(
                SyntheticVideoFrameSource(visual_frames),
                delay_seconds=0.025,
            ),
            BroadbandHearingPath(LogSpectralReceptor(audio_config)),
            LocalChannelGridReceptor(visual_config),
            nominal_duration_seconds=0.2,
        )

        auditory, visual = result.sequences
        self.assertEqual(("auditory", "visual"), result.audit.modality_ids)
        self.assertEqual(6, len(auditory.frames))
        self.assertEqual(2, len(visual.frames))
        self.assertEqual(
            {"organism.monotonic_ns"},
            {
                item.field_time.clock_id
                for sequence_out in result.sequences
                for item in sequence_out.frames
            },
        )
        self.assertEqual((6, 2), result.audit.frame_counts)

    def test_buffered_audio_keeps_callback_time_instead_of_read_time(self) -> None:
        audio_config = LogSpectralConfig(
            sample_rate=1000,
            window_size=100,
            hop_size=20,
            min_frequency=10.0,
            max_frequency=400.0,
            band_count=4,
        )
        frames = tuple((0.0,) * 20 for _ in range(10))

        class TimedSource:
            capture_clock_id = "organism.monotonic_ns"
            capture_ticks_per_second = 1_000_000_000.0

            def __init__(self) -> None:
                self.index = 0
                self.overflow_count = 0

            def read_timed_frame(self):
                index = self.index
                self.index += 1
                return (
                    frames[index],
                    1_000_000_000 + index * 20_000_000,
                    1_020_000_000 + index * 20_000_000,
                )

        visual_config = VisualGridConfig(
            source_width=12,
            source_height=8,
            grid_columns=2,
            grid_rows=2,
            frames_per_second=10.0,
        )
        result = capture_timed_audio_video_receptors(
            TimedSource(),
            SyntheticVideoFrameSource(
                (
                    np.zeros((8, 12, 3), dtype=np.uint8),
                    np.zeros((8, 12, 3), dtype=np.uint8),
                )
            ),
            BroadbandHearingPath(LogSpectralReceptor(audio_config)),
            LocalChannelGridReceptor(visual_config),
            nominal_duration_seconds=0.2,
        )
        auditory = result.sequences[0]
        self.assertEqual(
            tuple(
                (1_000_000_000 + index * 20_000_000, 1_020_000_000 + index * 20_000_000)
                for index in range(4, 10)
            ),
            tuple(
                (
                    item.field_time.window_start_tick,
                    item.field_time.window_end_tick,
                )
                for item in auditory.frames
            ),
        )


if __name__ == "__main__":
    unittest.main()
