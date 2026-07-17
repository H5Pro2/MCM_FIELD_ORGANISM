from __future__ import annotations

from dataclasses import fields
import unittest

from mcm_field_organism.mcm_distributor import (
    DistributedMCMConstellation,
    MCMFieldWindow,
)
from mcm_field_organism.multimodal_constellation_trace import (
    MultimodalTraceError,
    multimodal_trace_public_roles,
    observe_multimodal_constellation_trace,
)


def window(
    modality: str,
    values: tuple[float, ...],
    *,
    start: int,
    end: int,
    geometry: str | None = None,
) -> MCMFieldWindow:
    return MCMFieldWindow(
        dock_id=f"dock.{modality}",
        modality_id=modality,
        field_id=f"field.{modality}",
        geometry_id=geometry or f"field.{modality}.v1",
        snapshot_id=f"snapshot.{modality}.{start}.{end}",
        clock_id="organism.test",
        window_start_tick=start,
        window_end_tick=end,
        carrier_ids=tuple(f"{modality}.n{index}" for index in range(len(values))),
        activation=values,
        afterimage=(0.0,) * len(values),
    )


def constellation(
    audio: tuple[float, ...],
    visual: tuple[float, ...],
    *,
    start: int,
    tactile: tuple[float, ...] | None = None,
) -> DistributedMCMConstellation:
    states = [
        window("auditory", audio, start=start, end=start + 20),
        window("visual", visual, start=start + 5, end=start + 25),
    ]
    if tactile is not None:
        states.append(window("tactile", tactile, start=start + 4, end=start + 22))
    return DistributedMCMConstellation("organism.test", tuple(states))


class MultimodalConstellationTraceTests(unittest.TestCase):
    def test_exact_a_b_a_return_is_visible_without_pattern_identity(self) -> None:
        first = constellation((0.2, 0.4), (0.3, 0.7), start=100)
        changed = constellation((0.8, 0.4), (0.3, 0.7), start=200)
        returned = constellation((0.2, 0.4), (0.3, 0.7), start=300)
        trace = observe_multimodal_constellation_trace((first, changed, returned))
        comparisons = {
            (item.earlier_index, item.later_index): item for item in trace.comparisons
        }
        self.assertEqual(("auditory",), comparisons[(0, 1)].changed_modalities)
        self.assertEqual(("visual",), comparisons[(0, 1)].unchanged_modalities)
        self.assertFalse(comparisons[(0, 1)].exact_field_repeat)
        self.assertTrue(comparisons[(0, 2)].exact_field_repeat)
        self.assertEqual(("auditory", "visual"), comparisons[(0, 2)].unchanged_modalities)

    def test_timestamp_and_snapshot_changes_do_not_hide_exact_field_return(self) -> None:
        first = constellation((0.2, 0.4), (0.3, 0.7), start=100)
        later = constellation((0.2, 0.4), (0.3, 0.7), start=500)
        comparison = observe_multimodal_constellation_trace((first, later)).comparisons[0]
        self.assertTrue(comparison.exact_field_repeat)
        self.assertEqual(385, comparison.separation_ticks)
        self.assertEqual(0, comparison.overlap_ticks)

    def test_overlapping_observation_windows_are_reported_without_reordering(self) -> None:
        first = constellation((0.2,), (0.3,), start=100)
        later = constellation((0.4,), (0.3,), start=110)
        comparison = observe_multimodal_constellation_trace((first, later)).comparisons[0]
        self.assertEqual(0, comparison.separation_ticks)
        self.assertEqual(5, comparison.overlap_ticks)

    def test_added_modality_is_not_misreported_as_content_change(self) -> None:
        first = constellation((0.2,), (0.3,), start=100)
        later = constellation((0.2,), (0.3,), start=200, tactile=(0.6,))
        comparison = observe_multimodal_constellation_trace((first, later)).comparisons[0]
        self.assertEqual(("tactile",), comparison.added_modalities)
        self.assertEqual((), comparison.changed_modalities)
        self.assertFalse(comparison.exact_field_repeat)

    def test_continuing_modality_cannot_silently_change_anatomy(self) -> None:
        first = constellation((0.2,), (0.3,), start=100)
        invalid = DistributedMCMConstellation(
            "organism.test",
            (
                window("auditory", (0.2,), start=200, end=220, geometry="other.geometry"),
                window("visual", (0.3,), start=205, end=225),
            ),
        )
        with self.assertRaisesRegex(MultimodalTraceError, "changed field anatomy"):
            observe_multimodal_constellation_trace((first, invalid))

    def test_trace_rejects_nonadvancing_time_and_different_clocks(self) -> None:
        first = constellation((0.2,), (0.3,), start=100)
        same_start = constellation((0.4,), (0.3,), start=100)
        with self.assertRaisesRegex(MultimodalTraceError, "advance strictly"):
            observe_multimodal_constellation_trace((first, same_start))
        other_clock = DistributedMCMConstellation(
            "other.clock",
            tuple(
                MCMFieldWindow(**{**state.canonical_payload(), "clock_id": "other.clock"})
                for state in constellation((0.4,), (0.3,), start=200).states
            ),
        )
        with self.assertRaisesRegex(MultimodalTraceError, "one organism clock"):
            observe_multimodal_constellation_trace((first, other_clock))

    def test_observer_is_passive_and_source_constellations_are_unchanged(self) -> None:
        first = constellation((0.2,), (0.3,), start=100)
        later = constellation((0.4,), (0.3,), start=200)
        before = (first.digest(), later.digest())
        seen = []
        result = observe_multimodal_constellation_trace((first, later), observer=seen.append)
        self.assertEqual([result], seen)
        self.assertEqual(before, (first.digest(), later.digest()))

    def test_public_roles_exclude_memory_similarity_and_semantics(self) -> None:
        roles = set(multimodal_trace_public_roles())
        forbidden = {
            "pattern_id", "memory", "history_state", "similarity", "distance",
            "threshold", "label", "meaning", "word", "class_id", "winner",
            "reward", "raw_audio", "raw_video", "image", "samples",
        }
        self.assertTrue(forbidden.isdisjoint(roles))
        self.assertNotIn("constellation_digest", roles)


if __name__ == "__main__":
    unittest.main()
