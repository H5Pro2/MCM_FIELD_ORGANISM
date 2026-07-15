from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

import numpy as np

from mcm_field_organism import (
    LocalChannelGridReceptor,
    SyntheticVideoFrameSource,
    VisualCaptureError,
    VisualGridConfig,
    VisualReceptorContact,
    capture_finite_video,
    global_channel_mean_baseline,
    visual_public_roles,
)


CONFIG = VisualGridConfig(
    source_width=8,
    source_height=6,
    grid_columns=4,
    grid_rows=3,
    frames_per_second=10.0,
)


def blank_frame() -> np.ndarray:
    return np.zeros((CONFIG.source_height, CONFIG.source_width, 3), dtype=np.uint8)


class FiniteVisualReceptorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.receptor = LocalChannelGridReceptor(CONFIG)

    def test_black_frame_is_exact_active_zero(self) -> None:
        state = self.receptor.analyze(blank_frame(), frame_index=0)
        self.assertEqual(VisualReceptorContact.ACTIVE_ZERO, state.contact)
        self.assertEqual((0.0,) * CONFIG.carrier_count, state.channel_values)

    def test_local_channel_contact_stays_in_its_cell_and_channel(self) -> None:
        frame = blank_frame()
        frame[0:2, 0:2, 1] = 255
        state = self.receptor.analyze(frame, frame_index=0)
        expected = [0.0] * CONFIG.carrier_count
        expected[1] = 1.0
        self.assertEqual(tuple(expected), state.channel_values)
        self.assertEqual(VisualReceptorContact.ACTIVE_LIGHT, state.contact)

    def test_equal_global_means_at_different_places_remain_distinct(self) -> None:
        left = blank_frame()
        right = blank_frame()
        left[0:2, 0:2, 0] = 255
        right[0:2, 6:8, 0] = 255
        self.assertEqual(
            global_channel_mean_baseline(left, CONFIG),
            global_channel_mean_baseline(right, CONFIG),
        )
        left_state = self.receptor.analyze(left, frame_index=0)
        right_state = self.receptor.analyze(right, frame_index=0)
        self.assertNotEqual(left_state.channel_values, right_state.channel_values)

    def test_source_channels_remain_distinct(self) -> None:
        first = blank_frame()
        second = blank_frame()
        first[:, :, 0] = 128
        second[:, :, 2] = 128
        self.assertNotEqual(
            self.receptor.analyze(first, frame_index=0).channel_values,
            self.receptor.analyze(second, frame_index=0).channel_values,
        )

    def test_state_is_immutable_and_has_no_raw_or_semantic_roles(self) -> None:
        state = self.receptor.analyze(blank_frame(), frame_index=0)
        with self.assertRaises((FrozenInstanceError, AttributeError, TypeError)):
            state.frame_index = 1  # type: ignore[misc]
        state_roles, summary_roles = visual_public_roles()
        forbidden = {
            "raw_frame",
            "pixels",
            "image",
            "object",
            "person",
            "scene",
            "meaning",
            "movement",
            "afterimage",
            "mcm_activation",
        }
        self.assertTrue(forbidden.isdisjoint(state_roles))
        self.assertTrue(forbidden.isdisjoint(summary_roles))

    def test_invalid_frame_and_geometry_domains_are_rejected(self) -> None:
        invalid_frames = (
            np.zeros((6, 8), dtype=np.uint8),
            np.zeros((6, 8, 4), dtype=np.uint8),
            np.zeros((5, 8, 3), dtype=np.uint8),
            np.zeros((6, 8, 3), dtype=np.float32),
        )
        for frame in invalid_frames:
            with self.assertRaises(VisualCaptureError):
                self.receptor.analyze(frame, frame_index=0)
        with self.assertRaises(VisualCaptureError):
            VisualGridConfig(source_width=7, source_height=6, grid_columns=4, grid_rows=3)

    def test_1080p_candidate_has_stable_open_grid_geometry(self) -> None:
        config = VisualGridConfig()
        self.assertEqual(288, config.carrier_count)
        self.assertEqual(288, len(config.carrier_ids))
        self.assertEqual("visual.cell.r0.c0.channel0", config.carrier_ids[0])
        self.assertEqual("visual.cell.r7.c11.channel2", config.carrier_ids[-1])


class FiniteVideoCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.receptor = LocalChannelGridReceptor(CONFIG)
        self.frames = (blank_frame(), np.full((6, 8, 3), 64, dtype=np.uint8))

    def test_capture_reads_exact_frames_and_aggregates_without_raw_images(self) -> None:
        source = SyntheticVideoFrameSource(self.frames)
        observed = []
        summary = capture_finite_video(
            source,
            self.receptor,
            frame_count=2,
            observer=observed.append,
        )
        self.assertEqual(2, source.frames_read)
        self.assertEqual(2, summary.input_frames)
        self.assertEqual(2, summary.output_states)
        self.assertEqual(1, summary.active_zero_count)
        self.assertEqual(1, summary.active_light_count)
        self.assertEqual(2, len(observed))
        self.assertTrue(all(not hasattr(state, "frame") for state in observed))

    def test_same_sequence_reproduces_digest_and_order_change_does_not(self) -> None:
        first = capture_finite_video(
            SyntheticVideoFrameSource(self.frames),
            self.receptor,
            frame_count=2,
        )
        repeated = capture_finite_video(
            SyntheticVideoFrameSource(self.frames),
            self.receptor,
            frame_count=2,
        )
        reversed_run = capture_finite_video(
            SyntheticVideoFrameSource(tuple(reversed(self.frames))),
            self.receptor,
            frame_count=2,
        )
        self.assertEqual(first.sequence_digest, repeated.sequence_digest)
        self.assertNotEqual(first.sequence_digest, reversed_run.sequence_digest)

    def test_observer_presence_does_not_change_summary(self) -> None:
        without = capture_finite_video(
            SyntheticVideoFrameSource(self.frames),
            self.receptor,
            frame_count=2,
        )
        with_observer = capture_finite_video(
            SyntheticVideoFrameSource(self.frames),
            self.receptor,
            frame_count=2,
            observer=lambda state: state.digest(),
        )
        self.assertEqual(without, with_observer)

    def test_short_source_and_invalid_limits_fail_without_summary(self) -> None:
        with self.assertRaises(VisualCaptureError):
            capture_finite_video(
                SyntheticVideoFrameSource((self.frames[0],)),
                self.receptor,
                frame_count=2,
            )
        for count, maximum in ((0, 10), (2, 1)):
            with self.assertRaises(VisualCaptureError):
                capture_finite_video(
                    SyntheticVideoFrameSource(self.frames),
                    self.receptor,
                    frame_count=count,
                    max_frame_count=maximum,
                )


if __name__ == "__main__":
    unittest.main()
