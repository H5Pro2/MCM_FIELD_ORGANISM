"""Bounded partition probe for one controlled asynchronous audio-video source."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math

from .asynchronous_receptor_events import audit_asynchronous_receptor_events
from .controlled_audio_video_test_world import (
    ControlledAudioVideoTestWorld,
    ControlledWorldPhase,
    _base_configs,
    _scheduled_phase_sequences,
)
from .field_step_time import MCMFieldStepTime
from .field_time_partition import partition_receptor_completion_time
from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_time_alignment import ReceptorTimeSequence
from .shared_mcm_field import build_shared_mcm_field


@dataclass(frozen=True, slots=True)
class AsynchronousPartitionArm:
    arm_id: str
    source_id: str
    partition_id: str
    sequence_order: tuple[str, ...]
    source_event_count: int
    completion_group_count: int
    mixed_completion_group_count: int
    final_completion_tick: int
    proposal_step_count: int
    field_tick: int
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    layer_digest: str
    snapshot_digest: str
    audio_rate_hz: float
    video_rate_hz: float


@dataclass(frozen=True, slots=True)
class AsynchronousAudioVideoPartitionProbe:
    arms: tuple[AsynchronousPartitionArm, ...]
    coarse_fine_activation_linf: float
    coarse_fine_afterimage_linf: float
    permutation_activation_linf: float
    permutation_afterimage_linf: float
    reproduction_exact: bool
    source_event_counts_equal: bool
    completion_horizon_equal: bool


def _world(
    source_id: str,
    *,
    audio_rate_hz: float = 100.0,
    video_rate_hz: float = 10.0,
) -> ControlledAudioVideoTestWorld:
    audio_config, visual_config = _base_configs()
    audio_config = replace(
        audio_config,
        hop_size=round(audio_config.sample_rate / audio_rate_hz),
    )
    visual_config = replace(visual_config, frames_per_second=video_rate_hz)
    auditory = source_id in {"wa", "wav"}
    visual = source_id in {"wv", "wav"}
    return ControlledAudioVideoTestWorld(
        f"world.asynchronous.{source_id}",
        (
            ControlledWorldPhase(
                "contact.0",
                1.0,
                320.0 if auditory else 0.0,
                0.25 if auditory else 0.0,
                (2, 3),
                (1, 0) if visual else (0, 0),
                (6, 5),
                (220, 70, 45) if visual else (16, 16, 16),
            ),
        ),
        audio_config,
        visual_config,
    )


def _sequences(
    world: ControlledAudioVideoTestWorld,
    *,
    clock_id: str,
    ticks_per_second: float,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    audio_source, video_source, auditory_path, visual_receptor = (
        world.open_sources()
    )
    return _scheduled_phase_sequences(
        world,
        world.phases[0],
        audio_source,
        video_source,
        auditory_path,
        visual_receptor,
        audio_frame_start=0,
        video_frame_start=0,
        clock_id=clock_id,
        ticks_per_second=ticks_per_second,
    )


def _run_arm(
    source_id: str,
    partition_id: str,
    *,
    reverse_sequences: bool = False,
    reproduction_id: str | None = None,
    clock_id: str = "organism.asynchronous_partition",
    ticks_per_second: float = 1_000_000.0,
    audio_rate_hz: float = 100.0,
    video_rate_hz: float = 10.0,
) -> AsynchronousPartitionArm:
    world = _world(
        source_id,
        audio_rate_hz=audio_rate_hz,
        video_rate_hz=video_rate_hz,
    )
    sequences = _sequences(
        world,
        clock_id=clock_id,
        ticks_per_second=ticks_per_second,
    )
    visual_receptor = world.open_sources()[3]
    reference_frames = tuple(sequence.frames[0].frame for sequence in sequences)
    field = build_shared_mcm_field(
        reference_frames,
        audio_video_dock_anatomies(
            auditory_carrier_count=len(reference_frames[0].carrier_ids),
            visual_grid_columns=visual_receptor.config.grid_columns,
            visual_grid_rows=visual_receptor.config.grid_rows,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    horizon_end = round(world.duration_seconds * ticks_per_second)
    if partition_id == "coarse":
        steps = (
            MCMFieldStepTime(
                clock_id,
                0,
                horizon_end,
                ticks_per_second,
            ),
        )
    elif partition_id == "fine":
        steps = tuple(
            item.step_time
            for item in partition_receptor_completion_time(
                sequences,
                horizon_start_tick=0,
                horizon_end_tick=horizon_end,
                ticks_per_second=ticks_per_second,
            ).slices
        )
    else:
        raise ValueError("partition_id must be coarse or fine")
    ordered = tuple(reversed(sequences)) if reverse_sequences else sequences
    audit = audit_asynchronous_receptor_events(ordered)
    run = run_neutral_asynchronous_field(
        field,
        ordered,
        steps,
        NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=NeutralFastAfterimageConfig(0.5),
    )
    neurons = run.field.layer.neurons
    return AsynchronousPartitionArm(
        arm_id=reproduction_id or (
            f"{source_id}.{partition_id}.permuted"
            if reverse_sequences
            else f"{source_id}.{partition_id}"
        ),
        source_id=source_id,
        partition_id=partition_id,
        sequence_order=tuple(item.modality_id for item in ordered),
        source_event_count=audit.total_event_count,
        completion_group_count=len(audit.completion_groups),
        mixed_completion_group_count=audit.mixed_completion_group_count,
        final_completion_tick=audit.completion_groups[-1].completion_tick,
        proposal_step_count=len(steps),
        field_tick=run.field.layer.tick,
        activation=tuple(neuron.activation for neuron in neurons),
        afterimage=tuple(neuron.afterimage for neuron in neurons),
        layer_digest=run.field.layer.digest(),
        snapshot_digest=run.field.snapshot().digest(),
        audio_rate_hz=audio_rate_hz,
        video_rate_hz=video_rate_hz,
    )


def run_asynchronous_partition_arm(
    source_id: str,
    partition_id: str,
    **kwargs: object,
) -> AsynchronousPartitionArm:
    """Run one fresh arm with explicit technical rate parameters."""

    return _run_arm(source_id, partition_id, **kwargs)


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def run_asynchronous_audio_video_partition_probe(
) -> AsynchronousAudioVideoPartitionProbe:
    """Compare lossless coarse/fine partitions and neutral source controls."""

    controls = tuple(_run_arm(source_id, "coarse") for source_id in ("w0", "wv", "wa"))
    coarse = _run_arm("wav", "coarse")
    fine = _run_arm("wav", "fine")
    reproduction = _run_arm("wav", "fine", reproduction_id="wav.fine.reproduction")
    permutation = _run_arm("wav", "fine", reverse_sequences=True)
    arms = controls + (coarse, fine, reproduction, permutation)
    all_finite = all(
        math.isfinite(value)
        for arm in arms
        for value in arm.activation + arm.afterimage
    )
    if not all_finite:
        raise ValueError("partition probe produced non-finite field values")
    return AsynchronousAudioVideoPartitionProbe(
        arms=arms,
        coarse_fine_activation_linf=_linf(coarse.activation, fine.activation),
        coarse_fine_afterimage_linf=_linf(coarse.afterimage, fine.afterimage),
        permutation_activation_linf=_linf(fine.activation, permutation.activation),
        permutation_afterimage_linf=_linf(fine.afterimage, permutation.afterimage),
        reproduction_exact=(
            fine.activation == reproduction.activation
            and fine.afterimage == reproduction.afterimage
        ),
        source_event_counts_equal=len({arm.source_event_count for arm in arms}) == 1,
        completion_horizon_equal=(
            len(
                {
                    (arm.completion_group_count, arm.final_completion_tick)
                    for arm in arms
                }
            )
            == 1
        ),
    )
