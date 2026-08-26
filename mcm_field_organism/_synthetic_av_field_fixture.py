"""Shared synthetic AV field fixture for passive characterization probes."""

from __future__ import annotations

from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .finite_video_path import VisualGridConfig
from .field_step_time import MCMFieldStepTime
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from .shared_mcm_field import (
    SharedMCMField,
    SharedMCMFieldSnapshot,
    build_shared_mcm_field,
)


SYNTHETIC_AV_CLOCK_ID = "organism.synthetic_load.ns"
SYNTHETIC_AV_SOURCE_CLOCK_ID = "synthetic.load.source.ns"
SYNTHETIC_AV_TICKS_PER_SECOND = 1_000_000_000.0
SYNTHETIC_AUDITORY_CARRIER_IDS = tuple(
    f"auditory.synthetic.c{index}" for index in range(8)
)
SYNTHETIC_VISUAL_CONFIG = VisualGridConfig(
    source_width=120,
    source_height=80,
    grid_columns=3,
    grid_rows=2,
    frames_per_second=30.0,
)


def _frame(
    modality_id: str,
    geometry_id: str,
    snapshot_id: str,
    start_tick: int,
    end_tick: int,
    carrier_ids: tuple[str, ...],
    values: tuple[float, ...],
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality_id,
        geometry_id=geometry_id,
        snapshot_id=snapshot_id,
        clock_id=SYNTHETIC_AV_SOURCE_CLOCK_ID,
        window_start_tick=start_tick,
        window_end_tick=end_tick,
        carrier_ids=carrier_ids,
        values=values,
    )


def synthetic_av_sequences(
    phase_id: str,
    start_tick: int,
    end_tick: int,
    auditory_values: tuple[float, ...],
    visual_values: tuple[float, ...],
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    return synthetic_av_repeated_sequences(
        phase_id,
        start_tick,
        end_tick,
        end_tick - start_tick,
        auditory_values,
        visual_values,
    )


def synthetic_av_repeated_sequences(
    phase_id: str,
    start_tick: int,
    end_tick: int,
    support_ticks: int,
    auditory_values: tuple[float, ...],
    visual_values: tuple[float, ...],
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    duration = end_tick - start_tick
    if support_ticks <= 0 or duration <= 0 or duration % support_ticks:
        raise ValueError("synthetic AV interval must contain whole supports")
    auditory_frames = []
    visual_frames = []
    for index, frame_start in enumerate(range(start_tick, end_tick, support_ticks)):
        frame_end = frame_start + support_ticks
        field_time = CommonFieldTime(
            SYNTHETIC_AV_CLOCK_ID,
            frame_start,
            frame_end,
        )
        auditory = _frame(
            "auditory",
            "auditory.synthetic.line.v1",
            f"auditory.{phase_id}.{index}",
            frame_start,
            frame_end,
            SYNTHETIC_AUDITORY_CARRIER_IDS,
            auditory_values,
        )
        visual = _frame(
            "visual",
            SYNTHETIC_VISUAL_CONFIG.geometry_id,
            f"visual.{phase_id}.{index}",
            frame_start,
            frame_end,
            SYNTHETIC_VISUAL_CONFIG.carrier_ids,
            visual_values,
        )
        auditory_frames.append(OrganismTimedReceptorFrame(auditory, field_time))
        visual_frames.append(OrganismTimedReceptorFrame(visual, field_time))
    return (
        ReceptorTimeSequence(
            "auditory",
            "auditory.synthetic.line.v1",
            SYNTHETIC_AV_CLOCK_ID,
            tuple(auditory_frames),
        ),
        ReceptorTimeSequence(
            "visual",
            SYNTHETIC_VISUAL_CONFIG.geometry_id,
            SYNTHETIC_AV_CLOCK_ID,
            tuple(visual_frames),
        ),
    )


def build_synthetic_av_field(
    reference: tuple[ReceptorTimeSequence, ...],
) -> SharedMCMField:
    frames = tuple(sequence.frames[0].frame for sequence in reference)
    return build_shared_mcm_field(
        frames,
        audio_video_dock_anatomies(
            auditory_carrier_count=len(SYNTHETIC_AUDITORY_CARRIER_IDS),
            visual_grid_columns=SYNTHETIC_VISUAL_CONFIG.grid_columns,
            visual_grid_rows=SYNTHETIC_VISUAL_CONFIG.grid_rows,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )


def run_synthetic_av_load_recovery(
    phase_prefix: str,
    auditory_values: tuple[float, ...],
    visual_values: tuple[float, ...],
    load_duration_seconds: float,
    recovery_duration_seconds: float,
    *,
    support_seconds: float = 0.1,
    afterimage_config: NeutralFastAfterimageConfig | None = None,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> tuple[SharedMCMFieldSnapshot, SharedMCMFieldSnapshot, int]:
    support_ticks = round(support_seconds * SYNTHETIC_AV_TICKS_PER_SECOND)
    load_end = round(load_duration_seconds * SYNTHETIC_AV_TICKS_PER_SECOND)
    load_sequences = synthetic_av_repeated_sequences(
        f"{phase_prefix}.load",
        0,
        load_end,
        support_ticks,
        auditory_values,
        visual_values,
    )
    field = build_synthetic_av_field(load_sequences)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    load = run_neutral_asynchronous_field(
        field,
        load_sequences,
        (
            MCMFieldStepTime(
                SYNTHETIC_AV_CLOCK_ID,
                0,
                load_end,
                SYNTHETIC_AV_TICKS_PER_SECOND,
            ),
        ),
        substrate,
        afterimage_config=afterimage_config,
        dissipation_config=dissipation_config,
    )
    load_snapshot = load.field.snapshot()
    recovered_field = load.field
    source_event_count = load.handoff.assigned_event_count
    if recovery_duration_seconds > 0.0:
        recovery_end = load_end + round(
            recovery_duration_seconds * SYNTHETIC_AV_TICKS_PER_SECOND
        )
        recovery_sequences = synthetic_av_repeated_sequences(
            f"{phase_prefix}.recovery",
            load_end,
            recovery_end,
            support_ticks,
            tuple(0.0 for _ in SYNTHETIC_AUDITORY_CARRIER_IDS),
            tuple(0.0 for _ in SYNTHETIC_VISUAL_CONFIG.carrier_ids),
        )
        recovery = run_neutral_asynchronous_field(
            recovered_field,
            recovery_sequences,
            (
                MCMFieldStepTime(
                    SYNTHETIC_AV_CLOCK_ID,
                    load_end,
                    recovery_end,
                    SYNTHETIC_AV_TICKS_PER_SECOND,
                ),
            ),
            substrate,
            afterimage_config=afterimage_config,
            dissipation_config=dissipation_config,
        )
        recovered_field = recovery.field
        source_event_count += recovery.handoff.assigned_event_count
    return load_snapshot, recovered_field.snapshot(), source_event_count
