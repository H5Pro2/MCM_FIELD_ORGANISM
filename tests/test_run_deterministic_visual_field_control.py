from __future__ import annotations

import unittest

from mcm_field_organism import VisualGridConfig
from tools.run_deterministic_visual_field_control import (
    _control_windows,
    _deterministic_visual_frame,
    _run_control,
)


class DeterministicVisualFieldControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = VisualGridConfig(
            source_width=12,
            source_height=8,
            grid_columns=2,
            grid_rows=2,
            frames_per_second=15.0,
        )

    def test_frame_is_spatially_structured_and_immutable(self) -> None:
        frame = _deterministic_visual_frame(self.config)
        self.assertEqual((8, 12, 3), frame.shape)
        self.assertFalse(frame.flags.writeable)
        self.assertGreater(len(set(frame.reshape(-1, 3)[:, 0])), 1)

    def test_windows_preserve_exact_receptor_lage_and_rates(self) -> None:
        windows = _control_windows(window_count=3, visual_config=self.config)
        self.assertEqual(3, len(windows))
        self.assertTrue(
            all(
                tuple(len(sequence.frames) for sequence in window.receptor_sequences)
                == (100, 15)
                for window in windows
            )
        )
        visual_values = tuple(
            window.receptor_sequences[1].frames[0].frame.values
            for window in windows
        )
        self.assertTrue(all(values == visual_values[0] for values in visual_values))
        self.assertEqual((0, 3000, 6000), tuple(window.start_tick for window in windows))
        self.assertEqual((3000, 6000, 9000), tuple(window.end_tick for window in windows))

    def test_independent_control_runs_are_exactly_reproducible(self) -> None:
        windows = _control_windows(window_count=3, visual_config=self.config)
        first, first_states = _run_control(windows, self.config)
        second, second_states = _run_control(windows, self.config)

        self.assertEqual(345, first.source_support_count)
        self.assertEqual(
            tuple(item.digest() for item in first_states),
            tuple(item.digest() for item in second_states),
        )
        self.assertEqual(
            first.field.snapshot().digest(),
            second.field.snapshot().digest(),
        )


if __name__ == "__main__":
    unittest.main()
