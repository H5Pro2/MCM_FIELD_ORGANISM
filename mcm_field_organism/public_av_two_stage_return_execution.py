"""Executable implementation of the fixed two-stage public AV return run."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path

from .field_step_time import MCMFieldStepTime
from .field_time_partition import partition_receptor_completion_time
from .finite_audio_video_field_run import ORTHOGONAL_FIELD_SAMPLE_OFFSETS, audio_video_dock_anatomies
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from .public_av_container_source import PUBLIC_MEDIA_TICKS_PER_SECOND
from .public_av_no_input_gap_audit import PublicAVNoInputGapAudit
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_preregistration import public_av_two_stage_return_preregistration
from .public_av_two_stage_return_preflight import PublicAVTwoStageReturnPreflight
from .public_av_two_stage_return_runner import PublicAVTwoStageReturnRunnerWiring
from .public_media_source_contract import PublicMediaSourceContract
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_time_alignment import OrganismTimedReceptorFrame, ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField, build_shared_mcm_field


class PublicAVTwoStageReturnExecutionError(ValueError):
    """Raised when execution differs from the audited fixed contract."""


@dataclass(frozen=True, slots=True)
class PublicAVTwoStageReturnArmResult:
    arm_id: str
    stage_one_source_event_count: int
    stage_two_source_event_count: int
    stage_one_snapshot_digest: str
    post_resolution_snapshot_digest: str | None
    stage_two_snapshot_digest: str
    stage_two_layer_digest: str
    stage_two_activation: tuple[float, ...]
    stage_two_afterimage: tuple[float, ...]
    carried_field_state: bool
    fresh_field_before_stage_two: bool


@dataclass(frozen=True, slots=True)
class PublicAVTwoStageReturnExecution:
    runner_id: str
    source_id: str
    clock_id: str
    stage_duration_ticks: int
    resolution_duration_ticks: int
    arms: tuple[PublicAVTwoStageReturnArmResult, ...]
    stage_two_activation_linf_between_arms: float
    stage_two_afterimage_linf_between_arms: float
    stage_two_layer_digest_equal: bool
    stage_two_snapshot_digest_equal: bool
    raw_payload_retained: bool = False
    metadata_used_by_field: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        arms = tuple(self.arms)
        if {arm.arm_id for arm in arms} != {"continued_field", "fresh_stage_two_baseline"}:
            raise PublicAVTwoStageReturnExecutionError("execution requires the two fixed arms")
        if self.stage_duration_ticks != 500_000_000 or self.resolution_duration_ticks != 100_000_000:
            raise PublicAVTwoStageReturnExecutionError("execution intervals changed")
        forbidden = (
            self.raw_payload_retained,
            self.metadata_used_by_field,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(forbidden):
            raise PublicAVTwoStageReturnExecutionError("execution cannot retain payloads or release claims")
        object.__setattr__(self, "arms", arms)


def shift_receptor_time_sequences(
    sequences: tuple[ReceptorTimeSequence, ...],
    tick_offset: int,
) -> tuple[ReceptorTimeSequence, ...]:
    """Shift only organism time; reduced receptor frames remain unchanged."""

    if tick_offset != 600_000_000:
        raise PublicAVTwoStageReturnExecutionError("stage-two offset must remain fixed")
    shifted = []
    for sequence in sequences:
        frames = tuple(
            OrganismTimedReceptorFrame(
                item.frame,
                CommonFieldTime(
                    item.field_time.clock_id,
                    item.field_time.window_start_tick + tick_offset,
                    item.field_time.window_end_tick + tick_offset,
                ),
            )
            for item in sequence.frames
        )
        shifted.append(ReceptorTimeSequence(sequence.modality_id, sequence.geometry_id, sequence.clock_id, frames))
    return tuple(shifted)


def _steps(
    sequences: tuple[ReceptorTimeSequence, ...], start_tick: int, end_tick: int
) -> tuple[MCMFieldStepTime, ...]:
    return tuple(
        item.step_time
        for item in partition_receptor_completion_time(
            sequences,
            horizon_start_tick=start_tick,
            horizon_end_tick=end_tick,
            ticks_per_second=PUBLIC_MEDIA_TICKS_PER_SECOND,
        ).slices
    )


def _fresh_field(sequences: tuple[ReceptorTimeSequence, ...]) -> SharedMCMField:
    reference = tuple(sequence.frames[0].frame for sequence in sequences)
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference[0].carrier_ids),
        visual_grid_columns=10,
        visual_grid_rows=8,
    )
    return build_shared_mcm_field(reference, anatomies, sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS)


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def execute_public_av_two_stage_return_run(
    path: Path,
    contract: PublicMediaSourceContract,
    wiring: PublicAVTwoStageReturnRunnerWiring,
    gap_audit: PublicAVNoInputGapAudit,
    preflight: PublicAVTwoStageReturnPreflight,
) -> PublicAVTwoStageReturnExecution:
    """Execute the fixed comparison; callers must separately authorize the run."""

    plan = public_av_two_stage_return_preregistration()
    if not isinstance(wiring, PublicAVTwoStageReturnRunnerWiring):
        raise PublicAVTwoStageReturnExecutionError("runner wiring is required")
    if not isinstance(gap_audit, PublicAVNoInputGapAudit) or not gap_audit.audit_complete:
        raise PublicAVTwoStageReturnExecutionError("completed no-input-gap audit is required")
    if not isinstance(preflight, PublicAVTwoStageReturnPreflight):
        raise PublicAVTwoStageReturnExecutionError("positive execution preflight is required")
    if not preflight.single_bounded_run_release_granted or preflight.field_run_started:
        raise PublicAVTwoStageReturnExecutionError("single bounded run is not released")
    if preflight.media_path != str(path) or preflight.source_id != plan.source_id:
        raise PublicAVTwoStageReturnExecutionError("preflight path or source differs")
    if wiring.preregistration_id != plan.preregistration_id or gap_audit.runner_id != wiring.runner_id:
        raise PublicAVTwoStageReturnExecutionError("runner contracts do not match")
    if contract.source_id != plan.source_id or wiring.source_id != plan.source_id:
        raise PublicAVTwoStageReturnExecutionError("source differs from preregistration")

    stage_one_sequences = _sequences(path, contract)
    stage_two_sequences = shift_receptor_time_sequences(stage_one_sequences, 600_000_000)
    stage_one_steps = _steps(stage_one_sequences, 0, 500_000_000)
    stage_two_steps = _steps(stage_two_sequences, 600_000_000, 1_100_000_000)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    results = []
    for arm in wiring.arms:
        stage_one = run_neutral_asynchronous_field(
            _fresh_field(stage_one_sequences), stage_one_sequences, stage_one_steps, substrate,
            afterimage_config=afterimage,
        )
        stage_one_digest = stage_one.field.snapshot().digest()
        if arm.carry_field_state_to_stage_two:
            gap_time = CommonFieldTime(wiring.clock_id, 500_000_000, 600_000_000)
            gap_field = advance_neutral_fast_shared_field(
                stage_one.field,
                ReceptorDistribution(gap_time, ()),
                MCMFieldStepTime(wiring.clock_id, 500_000_000, 600_000_000, PUBLIC_MEDIA_TICKS_PER_SECOND),
                substrate,
                afterimage,
            )
            stage_two_start = gap_field
            post_resolution_digest = gap_field.snapshot().digest()
        else:
            stage_two_start = _fresh_field(stage_one_sequences)
            post_resolution_digest = None
        stage_two = run_neutral_asynchronous_field(
            stage_two_start, stage_two_sequences, stage_two_steps, substrate,
            afterimage_config=afterimage,
        )
        activation = tuple(neuron.activation for neuron in stage_two.field.layer.neurons)
        trace = tuple(neuron.afterimage for neuron in stage_two.field.layer.neurons)
        results.append(
            PublicAVTwoStageReturnArmResult(
                arm.arm_id,
                stage_one.source_support_count,
                stage_two.source_support_count,
                stage_one_digest,
                post_resolution_digest,
                stage_two.field.snapshot().digest(),
                stage_two.field.layer.digest(),
                activation,
                trace,
                arm.carry_field_state_to_stage_two,
                arm.fresh_field_before_stage_two,
            )
        )
    by_id = {item.arm_id: item for item in results}
    continued = by_id["continued_field"]
    baseline = by_id["fresh_stage_two_baseline"]
    return PublicAVTwoStageReturnExecution(
        runner_id="public.av.nasa-earthrise.two-stage-return.execution.v1",
        source_id=plan.source_id,
        clock_id=plan.clock_id,
        stage_duration_ticks=plan.stage_duration_ticks,
        resolution_duration_ticks=100_000_000,
        arms=tuple(results),
        stage_two_activation_linf_between_arms=_linf(continued.stage_two_activation, baseline.stage_two_activation),
        stage_two_afterimage_linf_between_arms=_linf(continued.stage_two_afterimage, baseline.stage_two_afterimage),
        stage_two_layer_digest_equal=continued.stage_two_layer_digest == baseline.stage_two_layer_digest,
        stage_two_snapshot_digest_equal=continued.stage_two_snapshot_digest == baseline.stage_two_snapshot_digest,
    )


def public_av_two_stage_return_execution_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVTwoStageReturnArmResult, PublicAVTwoStageReturnExecution)
        for item in fields(cls)
    )
