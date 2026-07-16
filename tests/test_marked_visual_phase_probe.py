from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism import (
    MarkedVisualPhaseError,
    VisualGridConfig,
    VisualWorldPhase,
    build_visual_phase_schedule,
    marked_visual_phase_public_roles,
    observe_marked_visual_phases,
    rest_change_rest_visual_schedule,
    run_visual_spatiotemporal_input_probe,
)


class MarkedVisualPhaseProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = VisualGridConfig(
            source_width=4,
            source_height=2,
            grid_columns=2,
            grid_rows=1,
            frames_per_second=10.0,
        )

    @staticmethod
    def frame(value: int) -> np.ndarray:
        return np.full((2, 4, 3), value, dtype=np.uint8)

    def test_schedule_is_contiguous_and_uses_measured_ticks(self) -> None:
        phases = rest_change_rest_visual_schedule(
            clock_id="organism.measured",
            anchor_tick=100,
            phase_duration_ticks=30,
        )
        self.assertEqual(
            ((100, 130), (130, 160), (160, 190)),
            tuple((item.window_start_tick, item.window_end_tick) for item in phases),
        )

    def test_completed_frames_are_assigned_and_boundary_frames_are_excluded(self) -> None:
        probe = run_visual_spatiotemporal_input_probe(
            (self.frame(0), self.frame(0), self.frame(255), self.frame(0)),
            self.config,
            clock_id="organism.measured",
            tick_width=10,
        )
        phases = rest_change_rest_visual_schedule(
            clock_id="organism.measured",
            anchor_tick=0,
            phase_duration_ticks=10,
        )
        result = observe_marked_visual_phases(
            probe,
            clock_id="organism.measured",
            phases=phases,
        )
        self.assertEqual(("rest.1", "change", "rest.2", None), tuple(
            item.phase_id for item in result.assignments
        ))
        self.assertEqual(1, result.outside_schedule_frame_count)
        self.assertEqual(0, result.boundary_frame_count)
        self.assertEqual(1, result.initialization_frame_count)

    def test_interval_crossing_a_phase_boundary_is_not_forced_into_a_phase(self) -> None:
        frames = (self.frame(0), self.frame(64), self.frame(128))
        probe = run_visual_spatiotemporal_input_probe(
            frames,
            self.config,
            clock_id="organism.measured",
            tick_width=11,
        )
        phases = rest_change_rest_visual_schedule(
            clock_id="organism.measured",
            anchor_tick=0,
            phase_duration_ticks=10,
        )
        result = observe_marked_visual_phases(
            probe,
            clock_id="organism.measured",
            phases=phases,
        )
        self.assertTrue(result.assignments[0].crosses_phase_boundary)
        self.assertIsNone(result.assignments[0].phase_id)

    def test_summary_reads_existing_inputs_without_inventing_movement(self) -> None:
        probe = run_visual_spatiotemporal_input_probe(
            (
                self.frame(0),
                self.frame(0),
                self.frame(255),
                self.frame(0),
                self.frame(0),
                self.frame(0),
            ),
            self.config,
            clock_id="organism.measured",
            tick_width=10,
        )
        phases = rest_change_rest_visual_schedule(
            clock_id="organism.measured",
            anchor_tick=0,
            phase_duration_ticks=20,
        )
        result = observe_marked_visual_phases(
            probe,
            clock_id="organism.measured",
            phases=phases,
        )
        by_id = {item.phase_id: item for item in result.summaries}
        self.assertEqual(0.0, by_id["rest.1"].mean_absolute_receptor_change)
        self.assertGreater(by_id["change"].mean_absolute_receptor_change, 0.0)
        self.assertEqual(0.0, by_id["rest.2"].mean_absolute_receptor_change)

    def test_first_nonzero_frame_is_visible_but_excluded_from_change_summary(self) -> None:
        probe = run_visual_spatiotemporal_input_probe(
            (
                self.frame(128),
                self.frame(128),
                self.frame(128),
                self.frame(128),
                self.frame(128),
                self.frame(128),
            ),
            self.config,
            clock_id="organism.measured",
            tick_width=10,
        )
        phases = rest_change_rest_visual_schedule(
            clock_id="organism.measured",
            anchor_tick=0,
            phase_duration_ticks=20,
        )
        result = observe_marked_visual_phases(
            probe,
            clock_id="organism.measured",
            phases=phases,
        )
        self.assertTrue(result.assignments[0].initialization_frame)
        self.assertEqual(1, result.summaries[0].frame_count)
        self.assertEqual(0.0, result.summaries[0].mean_absolute_receptor_change)

    def test_same_history_reproduces_the_complete_phase_result(self) -> None:
        frames = (
            self.frame(0),
            self.frame(0),
            self.frame(255),
            self.frame(0),
            self.frame(0),
            self.frame(0),
        )
        phases = rest_change_rest_visual_schedule(
            clock_id="organism.measured",
            anchor_tick=0,
            phase_duration_ticks=20,
        )

        def run():
            probe = run_visual_spatiotemporal_input_probe(
                frames,
                self.config,
                clock_id="organism.measured",
                tick_width=10,
            )
            return observe_marked_visual_phases(
                probe,
                clock_id="organism.measured",
                phases=phases,
            )

        self.assertEqual(run(), run())

    def test_clock_and_schedule_contracts_are_enforced(self) -> None:
        with self.assertRaises(MarkedVisualPhaseError):
            build_visual_phase_schedule(
                clock_id="organism.measured",
                anchor_tick=0,
                phases=(VisualWorldPhase("only", 1),),
            )
        probe = run_visual_spatiotemporal_input_probe(
            (self.frame(0), self.frame(0)),
            self.config,
            clock_id="organism.measured",
        )
        phases = rest_change_rest_visual_schedule(
            clock_id="another.clock",
            anchor_tick=0,
            phase_duration_ticks=1,
        )
        with self.assertRaises(MarkedVisualPhaseError):
            observe_marked_visual_phases(probe, clock_id="another.clock", phases=phases)

    def test_public_result_has_no_raw_semantic_or_detector_roles(self) -> None:
        roles = set(marked_visual_phase_public_roles())
        self.assertTrue(
            {
                "raw_frame",
                "image",
                "object",
                "semantic_label",
                "movement",
                "movement_score",
                "threshold",
                "memory",
                "writeback",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
