from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.public_visual_temporal_map import (
    ExternalTimeSection,
    observe_public_visual_temporal_map,
    temporal_map_json_value,
)
from mcm_field_organism.public_visual_world import PublicVisualReceptorSequence
from tools.run_public_visual_temporal_map import LAUF_106_DIGEST


CONFIG = VisualGridConfig(8, 6, 4, 3, 8.0)


def sequence() -> tuple[PublicVisualReceptorSequence, LocalChannelGridReceptor]:
    receptor = LocalChannelGridReceptor(CONFIG)
    states = tuple(
        receptor.analyze(np.full((6, 8, 3), value, dtype=np.uint8), frame_index=index)
        for index, value in enumerate((32, 96, 224, 64))
    )
    return PublicVisualReceptorSequence(states, (0, 125, 250, 375), 125, 12), receptor


class PublicVisualTemporalMapTests(unittest.TestCase):
    def test_maps_every_interval_and_keeps_external_sections(self) -> None:
        reduced, receptor = sequence()
        result = observe_public_visual_temporal_map(
            reduced,
            reduced,
            receptor,
            (ExternalTimeSection(0, 250), ExternalTimeSection(250, 500)),
        )

        self.assertEqual(4, result.interval_count)
        self.assertEqual((0, 1), tuple(item.section_index for item in result.sections))
        self.assertEqual(0.0, result.actual_repeat_max_abs_residual)
        self.assertEqual(0.0, result.static_repeat_max_abs_residual)
        self.assertNotEqual(result.actual[-1].activation, result.static_baseline[-1].activation)
        self.assertEqual(((-1, 0), (0, -1), (0, 1), (1, 0)), result.diffusion_offsets)
        self.assertEqual(1.0, result.response_time_seconds)
        self.assertEqual(0.5, result.afterimage_time_constant_seconds)
        self.assertEqual(result.digest(), result.digest())

    def test_sections_must_be_fixed_contiguous_and_complete(self) -> None:
        reduced, receptor = sequence()
        with self.assertRaisesRegex(ValueError, "contiguous"):
            observe_public_visual_temporal_map(
                reduced, reduced, receptor, (ExternalTimeSection(125, 500),)
            )
        with self.assertRaisesRegex(ValueError, "complete"):
            observe_public_visual_temporal_map(
                reduced, reduced, receptor, (ExternalTimeSection(0, 250),)
            )

    def test_observer_artifact_contains_no_runtime_snapshot_or_raw_frame(self) -> None:
        reduced, receptor = sequence()
        result = observe_public_visual_temporal_map(
            reduced, reduced, receptor, (ExternalTimeSection(0, 500),)
        )
        document = temporal_map_json_value(result)

        self.assertNotIn("field", document)
        self.assertNotIn("snapshot", document)
        self.assertNotIn("raw_frames", document)
        self.assertEqual(
            ["current_receptor_projection", "fixed_symmetric_diffusion", "fast_afterimage"],
            document["explanation_baseline"],
        )

    def test_runner_is_pinned_to_documented_lauf_106_digest(self) -> None:
        finding = Path(
            "docs/forschung/016_OEFFENTLICHE_VISUELLE_AUSSENWELT_WAHRNEHMUNGSBEFUND.md"
        ).read_text(encoding="utf-8")

        self.assertIn(LAUF_106_DIGEST, finding)


if __name__ == "__main__":
    unittest.main()
