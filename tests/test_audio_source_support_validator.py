from __future__ import annotations

from dataclasses import replace
import unittest

from tests.audio_source_support_validator import (
    SyntheticAudioHopMetadata,
    validate_audio_source_support,
)


class AudioSourceSupportValidatorPreregisteredArms(unittest.TestCase):
    SOURCE_TICKS_PER_SECOND = 1_000_000_000
    ADC_START_TICK = 1_000_000_000
    SAMPLE_RATE = 48_000
    HOP_SIZE = 480

    def setUp(self) -> None:
        self.sample_rate = self.SAMPLE_RATE
        self.hop_size = self.HOP_SIZE
        self.adc_width = (
            self.hop_size * self.SOURCE_TICKS_PER_SECOND // self.sample_rate
        )

    def sequence(self) -> tuple[SyntheticAudioHopMetadata, ...]:
        return tuple(
            SyntheticAudioHopMetadata(
                sample_start=index * self.hop_size,
                sample_end=(index + 1) * self.hop_size,
                frame_count=self.hop_size,
                sample_rate=self.sample_rate,
                adc_start_tick=self.ADC_START_TICK + index * self.adc_width,
                adc_end_tick=self.ADC_START_TICK + (index + 1) * self.adc_width,
                organism_callback_tick=10_000_000_000 + index * self.adc_width,
            )
            for index in range(12)
        )

    def validate(self, frames: tuple[SyntheticAudioHopMetadata, ...]):
        return validate_audio_source_support(
            frames,
            sample_rate=self.sample_rate,
            hop_size=self.hop_size,
            source_ticks_per_second=self.SOURCE_TICKS_PER_SECOND,
        )

    def changed(self, index: int, **changes: object):
        frames = list(self.sequence())
        frames[index] = replace(frames[index], **changes)
        return tuple(frames)

    def assert_rejected(self, result, index: int, reason: str) -> None:
        self.assertFalse(result.accepted)
        self.assertEqual(index, result.accepted_count)
        self.assertEqual(index, result.rejected_index)
        self.assertEqual(reason, result.rejection_reason)

    def test_arm_v_accepts_twelve_lossless_hops(self) -> None:
        result = self.validate(self.sequence())
        self.assertTrue(result.accepted)
        self.assertEqual(12, result.accepted_count)

    def test_arm_j_organism_callback_jitter_does_not_change_support(self) -> None:
        frames = tuple(
            replace(
                frame,
                organism_callback_tick=frame.organism_callback_tick + (index % 3) * 137,
            )
            for index, frame in enumerate(self.sequence())
        )
        self.assertEqual(self.validate(self.sequence()), self.validate(frames))

    def test_arm_d_rejects_duplicate_adc_start(self) -> None:
        frames = self.sequence()
        duplicate_start = frames[4].adc_start_tick
        assert duplicate_start is not None
        self.assert_rejected(
            self.validate(
                self.changed(
                    5,
                    adc_start_tick=duplicate_start,
                    adc_end_tick=duplicate_start + self.adc_width,
                )
            ),
            5,
            "adc_time_not_strictly_monotonic",
        )

    def test_arm_r_rejects_adc_rollback(self) -> None:
        frames = self.sequence()
        rollback_start = frames[3].adc_start_tick
        assert rollback_start is not None
        self.assert_rejected(
            self.validate(
                self.changed(
                    5,
                    adc_start_tick=rollback_start,
                    adc_end_tick=rollback_start + self.adc_width,
                )
            ),
            5,
            "adc_time_not_strictly_monotonic",
        )

    def test_arm_o_rejects_overlapping_adc_intervals(self) -> None:
        frame = self.sequence()[5]
        self.assert_rejected(
            self.validate(
                self.changed(
                    5,
                    adc_start_tick=frame.adc_start_tick - 1,
                    adc_end_tick=frame.adc_end_tick - 1,
                )
            ),
            5,
            "adc_interval_overlap",
        )

    def test_arm_g_rejects_adc_gap(self) -> None:
        frame = self.sequence()[5]
        self.assert_rejected(
            self.validate(
                self.changed(
                    5,
                    adc_start_tick=frame.adc_start_tick + 1,
                    adc_end_tick=frame.adc_end_tick + 1,
                )
            ),
            5,
            "adc_interval_gap",
        )

    def test_arm_b_minus_rejects_479_samples(self) -> None:
        self.assert_rejected(
            self.validate(self.changed(5, frame_count=479, sample_end=2879)),
            5,
            "frame_count_does_not_match_hop",
        )

    def test_arm_b_plus_rejects_481_samples(self) -> None:
        self.assert_rejected(
            self.validate(self.changed(5, frame_count=481, sample_end=2881)),
            5,
            "frame_count_does_not_match_hop",
        )

    def test_arm_s_rejects_sample_rate_change(self) -> None:
        self.assert_rejected(
            self.validate(self.changed(5, sample_rate=44_100)),
            5,
            "sample_rate_changed",
        )

    def test_arm_i_rejects_input_overflow(self) -> None:
        self.assert_rejected(
            self.validate(self.changed(5, input_overflow=True)),
            5,
            "input_overflow",
        )

    def test_arm_q_rejects_queue_loss(self) -> None:
        self.assert_rejected(
            self.validate(self.changed(5, queue_loss=True)),
            5,
            "queue_loss",
        )

    def test_arm_n_rejects_missing_adc_time(self) -> None:
        self.assert_rejected(
            self.validate(self.changed(5, adc_start_tick=None, adc_end_tick=None)),
            5,
            "adc_time_missing_or_invalid",
        )

    def test_arm_w_rejects_analysis_window_as_new_support(self) -> None:
        self.assert_rejected(
            self.validate(self.changed(5, support_role="analysis_window")),
            5,
            "analysis_window_is_not_new_source_support",
        )

    def test_arm_c_rejects_current_transport_without_adc_exposure(self) -> None:
        self.assert_rejected(
            self.validate(
                self.changed(
                    0,
                    adc_time_exposed=False,
                    adc_start_tick=None,
                    adc_end_tick=None,
                )
            ),
            0,
            "backend_adc_time_not_exposed",
        )


if __name__ == "__main__":
    unittest.main()
