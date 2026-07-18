from __future__ import annotations

import unittest

from mcm_field_organism.adapter_timing_capability import (
    AdapterTimingCapabilityError,
    AudioCallbackTiming,
    VideoFrameTiming,
    adapter_timing_capability_public_roles,
    audit_audio_callback_timing,
    audit_video_frame_timing,
)


class AdapterTimingCapabilityTests(unittest.TestCase):
    def test_audio_callback_times_remain_passive_capability_evidence(self) -> None:
        result = audit_audio_callback_timing(
            (
                AudioCallbackTiming(1.00, 1.03, 10.0301),
                AudioCallbackTiming(1.01, 1.04, 10.0402),
                AudioCallbackTiming(1.02, 1.05, 10.0501),
            ),
            reported_input_latency_seconds=0.03,
        )
        self.assertTrue(result.adc_time_exposed)
        self.assertTrue(result.adc_time_strictly_monotonic)
        self.assertTrue(result.adc_time_usable_as_source_clock)
        self.assertTrue(result.stream_current_time_usable_as_source_clock)
        self.assertAlmostEqual(0.01, result.adc_step_median_seconds)
        self.assertAlmostEqual(0.03, result.adc_to_stream_current_median_seconds)
        self.assertFalse(result.blocking_adapter_exposes_adc_time)
        self.assertFalse(result.organism_support_is_mapped)

    def test_exposed_but_resetting_audio_times_are_not_usable(self) -> None:
        result = audit_audio_callback_timing(
            (
                AudioCallbackTiming(0.00, 0.0, 10.00),
                AudioCallbackTiming(0.01, 0.0, 10.01),
                AudioCallbackTiming(0.02, 0.0, 10.02),
                AudioCallbackTiming(0.00, 0.0, 10.03),
            ),
            reported_input_latency_seconds=0.03,
        )
        self.assertTrue(result.adc_time_exposed)
        self.assertFalse(result.adc_time_usable_as_source_clock)
        self.assertTrue(result.stream_current_time_exposed)
        self.assertFalse(result.stream_current_time_usable_as_source_clock)
        self.assertIsNone(result.adc_to_stream_current_median_seconds)
        self.assertIsNone(result.stream_to_organism_offset_span_seconds)

    def test_video_negative_backend_values_are_not_timestamps(self) -> None:
        result = audit_video_frame_timing(
            (
                VideoFrameTiming(-1.0, -1.0, -4.0, 1.0, 1.1),
                VideoFrameTiming(-1.0, -1.0, -4.0, 1.1, 1.2),
                VideoFrameTiming(-1.0, -1.0, -4.0, 1.2, 1.3),
            ),
            backend_id="DSHOW",
        )
        self.assertFalse(result.position_time_available)
        self.assertFalse(result.presentation_time_available)
        self.assertTrue(result.exposure_setting_available)
        self.assertFalse(result.exposure_duration_available)
        self.assertFalse(result.organism_support_is_mapped)

    def test_video_available_but_constant_time_is_not_monotonic(self) -> None:
        result = audit_video_frame_timing(
            (
                VideoFrameTiming(0.0, 2.0, -4.0, 1.0, 1.1),
                VideoFrameTiming(0.0, 3.0, -4.0, 1.1, 1.2),
                VideoFrameTiming(0.0, 4.0, -4.0, 1.2, 1.3),
            ),
            backend_id="TEST",
        )
        self.assertTrue(result.position_time_available)
        self.assertFalse(result.position_time_strictly_monotonic)
        self.assertTrue(result.presentation_time_strictly_monotonic)

    def test_too_few_observations_are_rejected(self) -> None:
        with self.assertRaisesRegex(AdapterTimingCapabilityError, "three callbacks"):
            audit_audio_callback_timing(
                (
                    AudioCallbackTiming(1.0, 1.1, 2.0),
                    AudioCallbackTiming(1.1, 1.2, 2.1),
                ),
                reported_input_latency_seconds=0.1,
            )

    def test_public_roles_do_not_claim_field_effect_or_validity(self) -> None:
        forbidden = {
            "field_activation",
            "valid_until",
            "held_value",
            "meaning",
            "weight",
            "afterimage",
        }
        self.assertTrue(
            forbidden.isdisjoint(adapter_timing_capability_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
