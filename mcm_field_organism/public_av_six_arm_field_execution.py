"""Execute the fixed bounded six-arm public AV field comparison."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

from .asynchronous_receptor_events import audit_asynchronous_receptor_events
from .broadband_hearing_path import BroadbandHearingPath
from .field_step_time import MCMFieldStepTime
from .field_time_partition import partition_receptor_completion_time
from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .public_av_container_source import (
    PUBLIC_MEDIA_CLOCK_ID,
    PUBLIC_MEDIA_TICKS_PER_SECOND,
    decode_audited_public_av_sources,
)
from .public_av_field_preregistration import public_av_passive_field_preregistration
from .public_media_source_contract import PublicMediaSourceContract
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from .shared_mcm_field import build_shared_mcm_field


class PublicAVSixArmFieldExecutionError(ValueError):
    """Raised when execution differs from the fixed preregistration."""


@dataclass(frozen=True, slots=True)
class PublicAVFieldArmResult:
    arm_id: str
    source_event_count: int
    completion_group_count: int
    mixed_completion_group_count: int
    proposal_step_count: int
    final_completion_tick: int
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    layer_digest: str
    snapshot_digest: str


@dataclass(frozen=True, slots=True)
class PublicAVSixArmFieldExecution:
    runner_id: str
    source_id: str
    clock_id: str
    duration_limit_ticks: int
    arms: tuple[PublicAVFieldArmResult, ...]
    joint_reproduction_exact: bool
    permutation_activation_linf: float
    permutation_afterimage_linf: float
    coarse_fine_activation_linf: float
    coarse_fine_afterimage_linf: float
    auditory_only_activation_linf: float
    visual_only_activation_linf: float
    raw_payload_retained: bool = False
    metadata_used_by_field: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        arms = tuple(self.arms)
        if len(arms) != 6 or len({arm.arm_id for arm in arms}) != 6:
            raise PublicAVSixArmFieldExecutionError("execution requires six unique arms")
        if self.duration_limit_ticks != 500_000_000:
            raise PublicAVSixArmFieldExecutionError("execution duration changed")
        if any(
            (
                self.raw_payload_retained,
                self.metadata_used_by_field,
                self.memory_claim_allowed,
                self.meaning_claim_allowed,
                self.organization_claim_allowed,
                self.ai_claim_allowed,
            )
        ):
            raise PublicAVSixArmFieldExecutionError("execution cannot retain payloads or release claims")
        object.__setattr__(self, "arms", arms)


def public_av_receptor_sequences(
    path: Path,
    contract: PublicMediaSourceContract,
    *,
    start_tick: int = 0,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    audio_config = LogSpectralConfig()
    visual_config = VisualGridConfig(320, 240, 10, 8, 29.97)
    sources = decode_audited_public_av_sources(
        path,
        contract,
        duration_seconds=0.5,
        start_tick=start_tick,
        audio_frame_samples=audio_config.hop_size,
    )
    hearing = BroadbandHearingPath(LogSpectralReceptor(audio_config))
    auditory = []
    for _ in range(sources.audio.frame_count):
        samples, source_start, source_end = sources.audio.read_timed_frame()
        state = hearing.push(samples)
        if state is None:
            continue
        frame = ReceptorContactFrame(
            state.modality_id,
            state.geometry_id,
            f"auditory.receptor.{state.snapshot_index}",
            "audio.sample",
            state.window_start_sample,
            state.window_end_sample,
            state.carrier_ids,
            state.energy,
        )
        auditory.append(
            OrganismTimedReceptorFrame(
                frame,
                CommonFieldTime(PUBLIC_MEDIA_CLOCK_ID, source_start, source_end),
            )
        )
    receptor = LocalChannelGridReceptor(visual_config)
    visual = []
    for index in range(sources.video.frame_count):
        pixels, start, end = sources.video.read_timed_frame()
        state = receptor.analyze(pixels, frame_index=index)
        frame = ReceptorContactFrame(
            state.modality_id,
            state.geometry_id,
            f"visual.receptor.{state.frame_index}",
            "video.frame",
            state.frame_index,
            state.frame_index + 1,
            state.carrier_ids,
            state.channel_values,
        )
        visual.append(OrganismTimedReceptorFrame(frame, CommonFieldTime(PUBLIC_MEDIA_CLOCK_ID, start, end)))
    return (
        ReceptorTimeSequence("auditory", auditory[0].frame.geometry_id, PUBLIC_MEDIA_CLOCK_ID, tuple(auditory)),
        ReceptorTimeSequence("visual", visual[0].frame.geometry_id, PUBLIC_MEDIA_CLOCK_ID, tuple(visual)),
    )


def _sequences(
    path: Path,
    contract: PublicMediaSourceContract,
    *,
    start_tick: int = 0,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    """Compatibility entrypoint for the established public AV research chain."""

    return public_av_receptor_sequences(path, contract, start_tick=start_tick)


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def execute_public_av_six_arm_field_run(
    path: Path,
    contract: PublicMediaSourceContract,
) -> PublicAVSixArmFieldExecution:
    """Execute only the fixed v1 preregistration on fresh fields."""

    plan = public_av_passive_field_preregistration()
    sequences = public_av_receptor_sequences(path, contract)
    if contract.source_id != plan.source_id:
        raise PublicAVSixArmFieldExecutionError("source contract differs from preregistration")
    reference = tuple(sequence.frames[0].frame for sequence in sequences)
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference[0].carrier_ids),
        visual_grid_columns=10,
        visual_grid_rows=8,
    )
    results = []
    for arm in plan.arms:
        selected = tuple(
            sequence for sequence in sequences if sequence.modality_id in arm.included_modalities
        )
        ordered = tuple(reversed(selected)) if arm.reverse_sequence_declaration else selected
        event_audit = audit_asynchronous_receptor_events(ordered)
        if arm.partition_id == "coarse":
            steps = (MCMFieldStepTime(PUBLIC_MEDIA_CLOCK_ID, 0, plan.duration_limit_ticks, PUBLIC_MEDIA_TICKS_PER_SECOND),)
        else:
            steps = tuple(
                item.step_time
                for item in partition_receptor_completion_time(
                    ordered,
                    horizon_start_tick=0,
                    horizon_end_tick=plan.duration_limit_ticks,
                    ticks_per_second=PUBLIC_MEDIA_TICKS_PER_SECOND,
                ).slices
            )
        field = build_shared_mcm_field(reference, anatomies, sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS)
        run = run_neutral_asynchronous_field(
            field,
            ordered,
            steps,
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
        )
        results.append(
            PublicAVFieldArmResult(
                arm.arm_id,
                event_audit.total_event_count,
                len(event_audit.completion_groups),
                event_audit.mixed_completion_group_count,
                len(steps),
                event_audit.completion_groups[-1].completion_tick,
                tuple(neuron.activation for neuron in run.field.layer.neurons),
                tuple(neuron.afterimage for neuron in run.field.layer.neurons),
                run.field.layer.digest(),
                run.field.snapshot().digest(),
            )
        )
    by_id = {arm.arm_id: arm for arm in results}
    fine = by_id["joint.fine"]
    reproduction = by_id["joint.fine.reproduction"]
    permutation = by_id["joint.fine.permuted"]
    coarse = by_id["joint.coarse"]
    auditory = by_id["auditory_only.fine"]
    visual = by_id["visual_only.fine"]
    return PublicAVSixArmFieldExecution(
        "public.av.nasa-earthrise.passive-field.runner.execution.v1",
        plan.source_id,
        plan.clock_id,
        plan.duration_limit_ticks,
        tuple(results),
        fine.activation == reproduction.activation and fine.afterimage == reproduction.afterimage,
        _linf(fine.activation, permutation.activation),
        _linf(fine.afterimage, permutation.afterimage),
        _linf(coarse.activation, fine.activation),
        _linf(coarse.afterimage, fine.afterimage),
        _linf(fine.activation, auditory.activation),
        _linf(fine.activation, visual.activation),
    )


def public_av_six_arm_field_execution_public_roles() -> tuple[str, ...]:
    return tuple(item.name for cls in (PublicAVFieldArmResult, PublicAVSixArmFieldExecution) for item in fields(cls))
