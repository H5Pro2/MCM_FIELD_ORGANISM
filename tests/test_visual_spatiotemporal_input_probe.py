from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism import (
    SyntheticVideoFrameSource,
    VisualGridConfig,
    VisualSpatiotemporalProbeError,
    capture_visual_spatiotemporal_input_probe,
    capture_visual_spatiotemporal_time_window,
    run_visual_spatiotemporal_input_probe,
    visual_spatiotemporal_probe_public_roles,
)


class VisualSpatiotemporalInputProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = VisualGridConfig(
            source_width=10,
            source_height=6,
            grid_columns=5,
            grid_rows=3,
            frames_per_second=10.0,
        )

    def frame(self, row: int, column: int, channel: int = 0) -> np.ndarray:
        frame = np.zeros((6, 10, 3), dtype=np.uint8)
        frame[row * 2:(row + 1) * 2, column * 2:(column + 1) * 2, channel] = 255
        return frame

    @staticmethod
    def at(result, tick: int, position: tuple[int, int, int]):
        return next(
            item.local_input
            for item in result.ticks[tick].observations
            if item.position == position
        )

    @staticmethod
    def differences(observation):
        return {
            item.relative_position: item.activation_difference
            for item in observation.pair_differences
        }

    def test_adjacent_shift_is_present_as_current_contact_plus_prior_neighbor(self) -> None:
        result = run_visual_spatiotemporal_input_probe(
            (self.frame(1, 1), self.frame(1, 2), self.frame(1, 3)),
            self.config,
        )
        center = self.at(result, 1, (1, 2, 0))
        right = self.at(result, 2, (1, 3, 0))
        self.assertEqual(1.0, center.receptor_contact)
        self.assertEqual(1.0, self.differences(center)[(0, -1, 0)])
        self.assertEqual(1.0, right.receptor_contact)
        self.assertEqual(1.0, self.differences(right)[(0, -1, 0)])

    def test_mirrored_sequence_mirrors_only_the_local_offset(self) -> None:
        forward = run_visual_spatiotemporal_input_probe(
            (self.frame(1, 1), self.frame(1, 2)), self.config
        )
        reverse = run_visual_spatiotemporal_input_probe(
            (self.frame(1, 3), self.frame(1, 2)), self.config
        )
        forward_center = self.at(forward, 1, (1, 2, 0))
        reverse_center = self.at(reverse, 1, (1, 2, 0))
        self.assertEqual(forward_center.receptor_contact, reverse_center.receptor_contact)
        self.assertEqual(1.0, self.differences(forward_center)[(0, -1, 0)])
        self.assertEqual(1.0, self.differences(reverse_center)[(0, 1, 0)])
        self.assertEqual(0.0, self.differences(forward_center)[(0, 1, 0)])
        self.assertEqual(0.0, self.differences(reverse_center)[(0, -1, 0)])

    def test_stationary_contact_has_no_active_prior_neighbor(self) -> None:
        result = run_visual_spatiotemporal_input_probe(
            (self.frame(1, 2), self.frame(1, 2)), self.config
        )
        center = self.at(result, 1, (1, 2, 0))
        self.assertEqual(1.0, center.receptor_contact)
        self.assertEqual(1.0, center.prior_activation)
        self.assertTrue(all(value == -1.0 for value in self.differences(center).values()))

    def test_nonlocal_jump_has_no_active_immediate_prior_neighbor(self) -> None:
        result = run_visual_spatiotemporal_input_probe(
            (self.frame(1, 0), self.frame(1, 4)), self.config
        )
        target = self.at(result, 1, (1, 4, 0))
        self.assertEqual(1.0, target.receptor_contact)
        self.assertEqual(0.0, target.prior_activation)
        self.assertTrue(all(value == 0.0 for value in self.differences(target).values()))

    def test_one_tick_interruption_removes_the_prior_neighbor_contact(self) -> None:
        zero = np.zeros((6, 10, 3), dtype=np.uint8)
        result = run_visual_spatiotemporal_input_probe(
            (self.frame(1, 1), zero, self.frame(1, 2)), self.config
        )
        target = self.at(result, 2, (1, 2, 0))
        self.assertEqual(1.0, target.receptor_contact)
        self.assertEqual(0.0, target.prior_activation)
        self.assertTrue(all(value == 0.0 for value in self.differences(target).values()))

    def test_channel_change_does_not_cross_into_other_channel_neighbors(self) -> None:
        result = run_visual_spatiotemporal_input_probe(
            (self.frame(1, 1, 0), self.frame(1, 2, 1)), self.config
        )
        target = self.at(result, 1, (1, 2, 1))
        self.assertEqual(1.0, target.receptor_contact)
        self.assertTrue(all(value == 0.0 for value in self.differences(target).values()))

    def test_probe_retains_no_frames_and_introduces_no_inferred_roles(self) -> None:
        result = run_visual_spatiotemporal_input_probe(
            (self.frame(1, 1), self.frame(1, 2)), self.config
        )
        self.assertEqual((0, 1), tuple(tick.frame_index for tick in result.ticks))
        self.assertEqual((1, 2), tuple(tick.field_tick for tick in result.ticks))
        self.assertEqual(45, len(result.ticks[0].observations))
        roles = set(visual_spatiotemporal_probe_public_roles())
        forbidden = {
            "frame", "image", "pixels", "motion", "direction", "velocity",
            "object", "person", "scene", "label", "meaning", "pattern_id",
            "memory", "reward", "winner", "attention",
        }
        self.assertTrue(forbidden.isdisjoint(roles))

    def test_frame_generator_is_consumed_once_in_stream_order(self) -> None:
        reads = []

        def frames():
            for index, column in enumerate((1, 2, 3)):
                reads.append(index)
                yield self.frame(1, column)

        result = run_visual_spatiotemporal_input_probe(frames(), self.config)
        self.assertEqual([0, 1, 2], reads)
        self.assertEqual((0, 1, 2), tuple(item.frame_index for item in result.ticks))

    def test_finite_source_uses_measured_organism_time_and_exact_read_count(self) -> None:
        source = SyntheticVideoFrameSource((self.frame(1, 1), self.frame(1, 2)))
        clock = iter((100, 120, 200, 230))
        result = capture_visual_spatiotemporal_input_probe(
            source,
            self.config,
            frame_count=2,
            clock=lambda: next(clock),
            clock_id="organism.measured",
        )
        self.assertEqual(2, source.frames_read)
        self.assertEqual((0, 1), tuple(item.frame_index for item in result.ticks))
        self.assertEqual(
            ((100, 120), (200, 230)),
            tuple((item.window_start_tick, item.window_end_tick) for item in result.ticks),
        )

    def test_time_window_stops_on_clock_and_retains_final_crossing_frame(self) -> None:
        source = SyntheticVideoFrameSource(
            (self.frame(1, 1), self.frame(1, 2), self.frame(1, 3))
        )
        clock = iter((100, 110, 120, 130, 140, 155, 160))
        result = capture_visual_spatiotemporal_time_window(
            source,
            self.config,
            window_start_tick=100,
            window_end_tick=150,
            clock=lambda: next(clock),
            clock_id="organism.measured",
        )
        self.assertEqual(3, source.frames_read)
        self.assertEqual(
            ((100, 110), (120, 130), (140, 155)),
            tuple((item.window_start_tick, item.window_end_tick) for item in result.ticks),
        )

    def test_time_window_fails_if_frame_limit_precedes_clock_end(self) -> None:
        source = SyntheticVideoFrameSource(
            (self.frame(1, 1), self.frame(1, 2), self.frame(1, 3))
        )
        clock = iter((100, 110, 120, 130, 140))
        with self.assertRaises(VisualSpatiotemporalProbeError):
            capture_visual_spatiotemporal_time_window(
                source,
                self.config,
                window_start_tick=100,
                window_end_tick=150,
                clock=lambda: next(clock),
                max_frame_count=2,
            )
        self.assertEqual(2, source.frames_read)

    def test_finite_source_rejects_invalid_limits_before_reading(self) -> None:
        source = SyntheticVideoFrameSource((self.frame(1, 1), self.frame(1, 2)))
        with self.assertRaises(VisualSpatiotemporalProbeError):
            capture_visual_spatiotemporal_input_probe(source, self.config, frame_count=1)
        self.assertEqual(0, source.frames_read)

    def test_short_sequence_and_invalid_tick_width_are_rejected(self) -> None:
        with self.assertRaises(VisualSpatiotemporalProbeError):
            run_visual_spatiotemporal_input_probe((self.frame(1, 1),), self.config)
        with self.assertRaises(VisualSpatiotemporalProbeError):
            run_visual_spatiotemporal_input_probe(
                (self.frame(1, 1), self.frame(1, 2)), self.config, tick_width=0
            )


if __name__ == "__main__":
    unittest.main()
    capture_visual_spatiotemporal_input_probe,
