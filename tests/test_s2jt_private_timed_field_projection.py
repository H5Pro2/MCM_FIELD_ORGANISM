from __future__ import annotations

from dataclasses import replace
import hashlib
import unittest

from mcm_field_organism.broadband_hearing_path import (
    AuditoryReceptorContact,
    AuditoryReceptorState,
)
from mcm_field_organism.field_time_partition import (
    partition_receptor_completion_time,
)
from mcm_field_organism.finite_video_path import (
    VisualReceptorContact,
    VisualReceptorState,
)
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from mcm_field_organism.shared_mcm_field import ReceptorDockAnatomy
from tools._s2jo_private_canonical_av_boundary import (
    CanonicalAVEpisodeReceiptV1,
    CanonicalInputBindingV1,
    CanonicalReducedReceptorSequenceReceiptV1,
    CanonicalReductionResultV1,
    S2JO_AUDIO_CONFIG,
    S2JO_FRAME_BYTES,
    S2JO_FRAME_COUNT,
    S2JO_HOP_BYTES,
    S2JO_HOP_COUNT,
    S2JO_INPUT_BINDING_SCHEMA,
    S2JO_LEDGER_SCHEMA,
    S2JO_OPERATION_COUNT,
    S2JO_RAW_BYTES,
    S2JO_TICKS_PER_SECOND,
    S2JO_VISUAL_CONFIG,
    StreamingResourceLedgerV1,
)
from tools._s2jt_private_timed_field_projection import (
    S2JTProjectionError,
    project_s2jo_reduction_to_time_sequences,
    run_observed_field_pair,
    run_s2jt_observed_field,
    s2jt_default_dock_anatomies,
)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _visual_window(index: int) -> tuple[int, int]:
    return (
        index * S2JO_TICKS_PER_SECOND // 30,
        (index + 1) * S2JO_TICKS_PER_SECOND // 30,
    )


def _audio_window(index: int) -> tuple[int, int]:
    return index * 10_000_000, (index + 1) * 10_000_000


def _binding(role: str, position: int, window: tuple[int, int]) -> CanonicalInputBindingV1:
    return CanonicalInputBindingV1(
        S2JO_INPUT_BINDING_SCHEMA,
        role,
        position,
        window[0],
        window[1],
        _sha(f"payload-{role}-{position}"),
        _sha(f"functional-{role}-{position}"),
    )


def _bindings() -> tuple[CanonicalInputBindingV1, ...]:
    values = [
        _binding("VISUAL_FRAME", index, _visual_window(index))
        for index in range(S2JO_FRAME_COUNT)
    ]
    values.extend(
        _binding("AUDIO_HOP", index, _audio_window(index))
        for index in range(S2JO_HOP_COUNT)
    )
    return tuple(
        sorted(
            values,
            key=lambda item: (
                item.window_start_tick,
                0 if item.role == "VISUAL_FRAME" else 1,
                item.position,
            ),
        )
    )


def _reduction(
    *,
    bindings: tuple[CanonicalInputBindingV1, ...] | None = None,
) -> CanonicalReductionResultV1:
    audio_geometry = "auditory.log48.50-18000.w4800.h480.v1"
    episode = CanonicalAVEpisodeReceiptV1.build(bindings or _bindings(), audio_geometry)
    visual_states = tuple(
        VisualReceptorState(
            "visual",
            S2JO_VISUAL_CONFIG.geometry_id,
            index,
            S2JO_VISUAL_CONFIG.carrier_ids,
            tuple((index + 1) / 10 for _ in S2JO_VISUAL_CONFIG.carrier_ids),
            VisualReceptorContact.ACTIVE_LIGHT,
        )
        for index in range(S2JO_FRAME_COUNT)
    )
    auditory_carriers = tuple(f"auditory.band.{index}" for index in range(48))
    auditory_states = tuple(
        AuditoryReceptorState(
            "auditory",
            audio_geometry,
            index,
            index * S2JO_AUDIO_CONFIG.hop_size,
            (index + S2JO_AUDIO_CONFIG.warmup_hops) * S2JO_AUDIO_CONFIG.hop_size,
            auditory_carriers,
            tuple((index + 1) / 20 for _ in auditory_carriers),
            AuditoryReceptorContact.ACTIVE_ENERGY,
        )
        for index in range(11)
    )
    reduced = CanonicalReducedReceptorSequenceReceiptV1.build(
        episode.functional_episode_digest,
        visual_states,
        auditory_states,
    )
    ledger = StreamingResourceLedgerV1(
        S2JO_LEDGER_SCHEMA,
        S2JO_FRAME_COUNT,
        S2JO_HOP_COUNT,
        S2JO_FRAME_COUNT * S2JO_FRAME_BYTES,
        S2JO_HOP_COUNT * S2JO_HOP_BYTES,
        S2JO_RAW_BYTES,
        1,
        1,
        1,
        S2JO_OPERATION_COUNT,
        False,
    )
    return CanonicalReductionResultV1(
        episode,
        reduced,
        visual_states,
        auditory_states,
        ledger,
    )


def _small_sequences() -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    clock = "organism.s2jt.test"

    def timed(
        modality: str,
        geometry: str,
        snapshot: str,
        source_start: int,
        field_start: int,
        carriers: tuple[str, ...],
        values: tuple[float, ...],
    ) -> OrganismTimedReceptorFrame:
        return OrganismTimedReceptorFrame(
            ReceptorContactFrame(
                modality,
                geometry,
                snapshot,
                f"{modality}.source",
                source_start,
                source_start + 10,
                carriers,
                values,
            ),
            CommonFieldTime(clock, field_start, field_start + 10),
        )

    auditory = ReceptorTimeSequence(
        "auditory",
        "auditory.small",
        clock,
        (
            timed("auditory", "auditory.small", "auditory.small.0", 0, 0, ("a0", "a1"), (0.2, 0.4)),
            timed("auditory", "auditory.small", "auditory.small.1", 10, 10, ("a0", "a1"), (0.3, 0.5)),
        ),
    )
    visual = ReceptorTimeSequence(
        "visual",
        "visual.small",
        clock,
        (
            timed("visual", "visual.small", "visual.small.0", 0, 0, ("v0", "v1", "v2"), (0.1, 0.3, 0.5)),
            timed("visual", "visual.small", "visual.small.1", 10, 10, ("v0", "v1", "v2"), (0.2, 0.4, 0.6)),
        ),
    )
    return auditory, visual


def _small_steps(sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]):
    partition = partition_receptor_completion_time(
        sequences,
        horizon_start_tick=0,
        horizon_end_tick=20,
        ticks_per_second=1_000.0,
    )
    return tuple(item.step_time for item in partition.slices)


def _small_anatomies() -> dict[str, ReceptorDockAnatomy]:
    return {
        "auditory": ReceptorDockAnatomy("auditory", "dock.auditory.small", ((0, 0), (0, 1))),
        "visual": ReceptorDockAnatomy("visual", "dock.visual.small", ((1, 0), (1, 1), (1, 2))),
    }


class S2JTPrivateTimedFieldProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reduction = _reduction()
        cls.projection = project_s2jo_reduction_to_time_sequences(cls.reduction)

    def test_auditory_state_uses_only_triggering_hop_j_plus_nine(self) -> None:
        auditory = self.projection.sequences[0]
        self.assertEqual(self.projection.auditory_trigger_hops, tuple(range(9, 20)))
        for index, timed in enumerate(auditory.frames):
            trigger = index + 9
            self.assertEqual(
                (timed.field_time.window_start_tick, timed.field_time.window_end_tick),
                _audio_window(trigger),
            )
            self.assertEqual(timed.frame.window_start_tick, index * 480)
            self.assertEqual(timed.frame.window_end_tick, (index + 10) * 480)

    def test_simultaneous_completions_form_two_unordered_groups(self) -> None:
        self.assertEqual(self.projection.mixed_completion_ticks, (100_000_000, 200_000_000))
        partition = partition_receptor_completion_time(
            self.projection.sequences,
            horizon_start_tick=0,
            horizon_end_tick=200_000_000,
            ticks_per_second=float(S2JO_TICKS_PER_SECOND),
        )
        mixed = [item for item in partition.slices if len(item.completion_events) == 2]
        self.assertEqual([item.step_time.end_tick for item in mixed], [100_000_000, 200_000_000])
        self.assertTrue(all({event.modality_id for event in item.completion_events} == {"auditory", "visual"} for item in mixed))

    def test_default_docks_are_336_unique_and_row_separated(self) -> None:
        anatomies = s2jt_default_dock_anatomies()
        auditory = anatomies["auditory"].positions
        visual = anatomies["visual"].positions
        self.assertEqual((len(auditory), len(visual)), (48, 288))
        self.assertEqual({row for row, _ in auditory}, {0})
        self.assertEqual({row for row, _ in visual}, set(range(1, 9)))
        self.assertEqual(len(set(auditory + visual)), 336)

    def test_all_17_events_appear_once_in_15_completion_groups(self) -> None:
        partition = partition_receptor_completion_time(
            self.projection.sequences,
            horizon_start_tick=0,
            horizon_end_tick=200_000_000,
            ticks_per_second=float(S2JO_TICKS_PER_SECOND),
        )
        snapshot_ids = tuple(
            event.snapshot_id
            for time_slice in partition.slices
            for event in time_slice.completion_events
        )
        self.assertEqual(len(partition.slices), 15)
        self.assertEqual(len(snapshot_ids), 17)
        self.assertEqual(len(set(snapshot_ids)), 17)

    def test_complete_200_ms_field_run_remains_locked(self) -> None:
        with self.assertRaisesRegex(S2JTProjectionError, "S2JT_FULL_EXECUTION_LOCKED"):
            run_s2jt_observed_field(self.projection)

    def test_shifted_canonical_time_fails_closed(self) -> None:
        bindings = list(_bindings())
        index = next(i for i, item in enumerate(bindings) if item.role == "AUDIO_HOP" and item.position == 9)
        old = bindings[index]
        bindings[index] = _binding(old.role, old.position, (old.window_start_tick + 1, old.window_end_tick + 1))
        with self.assertRaisesRegex(S2JTProjectionError, "S2JT_INPUT_TIME_INVALID"):
            project_s2jo_reduction_to_time_sequences(_reduction(bindings=tuple(bindings)))

    def test_changed_reduced_sequence_fails_closed(self) -> None:
        visual = list(self.reduction.visual_states)
        visual[0] = replace(visual[0], channel_values=tuple(0.9 for _ in visual[0].channel_values))
        changed = replace(self.reduction, visual_states=tuple(visual))
        with self.assertRaisesRegex(S2JTProjectionError, "S2JT_REDUCED_STATE_INVALID"):
            project_s2jo_reduction_to_time_sequences(changed)

    def test_duplicate_or_missing_binding_fails_closed(self) -> None:
        bindings = list(_bindings())
        bindings[-1] = bindings[-2]
        with self.assertRaisesRegex(S2JTProjectionError, "S2JT_INPUT_BINDING_INVALID"):
            project_s2jo_reduction_to_time_sequences(_reduction(bindings=tuple(bindings)))

    def test_observed_and_direct_arms_start_separate_and_zero(self) -> None:
        sequences = _small_sequences()
        result = run_observed_field_pair(sequences, _small_steps(sequences), _small_anatomies(), expected_dock_count=5)
        self.assertTrue(result.initial_fields_distinct)
        self.assertTrue(result.initial_fields_zero)

    def test_observer_is_read_only_and_final_field_matches_direct_arm(self) -> None:
        sequences = _small_sequences()
        result = run_observed_field_pair(sequences, _small_steps(sequences), _small_anatomies(), expected_dock_count=5)
        self.assertEqual(len(result.trajectory), 2)
        self.assertEqual(tuple(item.completion_tick for item in result.trajectory), (10, 20))
        self.assertEqual(tuple(item.cumulative_support for item in result.trajectory), (2, 4))
        self.assertTrue(result.final_components_equal)
        self.assertTrue(result.final_digests_equal)
        self.assertEqual(result.observed_field.snapshot().digest(), result.direct_run.field.snapshot().digest())

    def test_small_field_assigns_each_event_exactly_once(self) -> None:
        sequences = _small_sequences()
        result = run_observed_field_pair(sequences, _small_steps(sequences), _small_anatomies(), expected_dock_count=5)
        self.assertTrue(result.handoff.every_in_horizon_event_assigned_once)
        self.assertEqual(result.handoff.source_event_count, 4)
        self.assertEqual(result.handoff.assigned_event_count, 4)

    def test_duplicate_source_support_fails_closed(self) -> None:
        auditory, visual = _small_sequences()
        duplicate_frame = replace(
            auditory.frames[1].frame,
            snapshot_id="auditory.small.duplicate",
            window_start_tick=auditory.frames[0].frame.window_start_tick,
            window_end_tick=auditory.frames[0].frame.window_end_tick,
        )
        duplicate_timed = replace(auditory.frames[1], frame=duplicate_frame)
        duplicate_sequence = replace(auditory, frames=(auditory.frames[0], duplicate_timed))
        sequences = (duplicate_sequence, visual)
        with self.assertRaisesRegex(S2JTProjectionError, "S2JT_HANDOFF_INVALID"):
            run_observed_field_pair(sequences, _small_steps(sequences), _small_anatomies(), expected_dock_count=5)

    def test_overlapping_docks_fail_closed(self) -> None:
        sequences = _small_sequences()
        anatomies = _small_anatomies()
        anatomies["visual"] = ReceptorDockAnatomy(
            "visual", "dock.visual.overlap", ((0, 1), (1, 1), (1, 2))
        )
        with self.assertRaisesRegex(S2JTProjectionError, "S2JT_DOCK_GEOMETRY_INVALID"):
            run_observed_field_pair(sequences, _small_steps(sequences), anatomies, expected_dock_count=5)


if __name__ == "__main__":
    unittest.main()
