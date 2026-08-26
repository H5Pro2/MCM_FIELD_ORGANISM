"""Executable mechanics for the six-arm public AV return replication."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path
from typing import Callable

from .field_step_time import MCMFieldStepTime
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from .public_av_container_source import PUBLIC_MEDIA_TICKS_PER_SECOND
from .public_av_return_permutation_contract import PublicAVReturnPermutationContract
from .public_av_return_replication_preflight import PublicAVReturnReplicationPreflight
from .public_av_return_replication_preregistration import public_av_return_replication_preregistration
from .public_av_return_replication_runner import PublicAVReturnReplicationRunnerWiring
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps, shift_receptor_time_sequences
from .public_media_source_contract import PublicMediaSourceContract
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_time_alignment import OrganismTimedReceptorFrame, ReceptorTimeSequence
from .shared_field_component_intervention import intervene_shared_field_component


class PublicAVReturnReplicationExecutionError(ValueError):
    """Raised when six-arm replication execution leaves its preflight boundary."""


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationArmResult:
    arm_id: str
    stage_one_source_event_count: int
    stage_two_source_event_count: int
    stage_one_snapshot_digest: str
    post_resolution_snapshot_digest: str | None
    intervention_audit_id: str | None
    stage_two_snapshot_digest: str
    stage_two_layer_digest: str
    stage_two_activation: tuple[float, ...]
    stage_two_afterimage: tuple[float, ...]
    stage_two_contact_mode: str
    stage_two_sequence_digest: tuple[str, str] | None

    def __post_init__(self) -> None:
        if not self.arm_id or not self.stage_one_snapshot_digest:
            raise PublicAVReturnReplicationExecutionError("arm result requires technical identities")
        if self.stage_two_source_event_count < 0 or self.stage_one_source_event_count < 1:
            raise PublicAVReturnReplicationExecutionError("event counts must remain technical")
        object.__setattr__(self, "stage_two_activation", tuple(self.stage_two_activation))
        object.__setattr__(self, "stage_two_afterimage", tuple(self.stage_two_afterimage))
        if len(self.stage_two_activation) != len(self.stage_two_afterimage):
            raise PublicAVReturnReplicationExecutionError("activation and afterimage vectors must align")
        if self.stage_two_sequence_digest is not None:
            object.__setattr__(self, "stage_two_sequence_digest", tuple(self.stage_two_sequence_digest))


@dataclass(frozen=True, slots=True)
class PublicAVReturnReplicationExecution:
    execution_id: str
    runner_id: str
    preflight_id: str
    source_id: str
    clock_id: str
    stage_duration_ticks: int
    resolution_duration_ticks: int
    arms: tuple[PublicAVReturnReplicationArmResult, ...]
    pairwise_activation_linf: tuple[tuple[float, ...], ...]
    pairwise_afterimage_linf: tuple[tuple[float, ...], ...]
    layer_digest_equality: tuple[tuple[bool, ...], ...]
    snapshot_digest_equality: tuple[tuple[bool, ...], ...]
    raw_payload_retained: bool = False
    metadata_used_by_field: bool = False
    memory_threshold_defined: bool = False
    organization_threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        arms = tuple(self.arms)
        expected = {
            "return.continued.full_state",
            "return.fresh_stage_two",
            "control.activation_only_carry",
            "control.afterimage_only_carry",
            "control.stage_two_order_permuted",
            "control.stage_two_sequence_withheld",
        }
        if {arm.arm_id for arm in arms} != expected:
            raise PublicAVReturnReplicationExecutionError("execution requires all six replication arms")
        if self.stage_duration_ticks != 500_000_000 or self.resolution_duration_ticks != 100_000_000:
            raise PublicAVReturnReplicationExecutionError("execution intervals changed")
        forbidden = (
            self.raw_payload_retained,
            self.metadata_used_by_field,
            self.memory_threshold_defined,
            self.organization_threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )
        if any(forbidden):
            raise PublicAVReturnReplicationExecutionError(
                "execution cannot retain payloads, define thresholds, or release claims"
            )
        object.__setattr__(self, "arms", arms)
        object.__setattr__(self, "pairwise_activation_linf", tuple(tuple(row) for row in self.pairwise_activation_linf))
        object.__setattr__(self, "pairwise_afterimage_linf", tuple(tuple(row) for row in self.pairwise_afterimage_linf))
        object.__setattr__(self, "layer_digest_equality", tuple(tuple(row) for row in self.layer_digest_equality))
        object.__setattr__(self, "snapshot_digest_equality", tuple(tuple(row) for row in self.snapshot_digest_equality))


def _advance_contact_free(
    field,
    start_tick: int,
    end_tick: int,
    substrate: NeutralLocalFieldSubstrateConfig,
    afterimage: NeutralFastAfterimageConfig,
):
    gap_time = CommonFieldTime("public.media.pts_ns", start_tick, end_tick)
    return advance_neutral_fast_shared_field(
        field,
        ReceptorDistribution(gap_time, ()),
        MCMFieldStepTime("public.media.pts_ns", start_tick, end_tick, PUBLIC_MEDIA_TICKS_PER_SECOND),
        substrate,
        afterimage,
    )


def _permuted_stage_two_sequences(
    sequences: tuple[ReceptorTimeSequence, ...],
    contract: PublicAVReturnPermutationContract,
) -> tuple[ReceptorTimeSequence, ...]:
    shifted = shift_receptor_time_sequences(sequences, 600_000_000)
    mappings = {item.modality_id: item.source_rank_to_time_slot_rank for item in contract.modality_mappings}
    output = []
    for sequence in shifted:
        mapping = mappings[sequence.modality_id]
        sorted_frames = tuple(sorted(sequence.frames, key=lambda item: item.field_time.window_start_tick))
        reordered = [None] * len(sorted_frames)
        for source_rank, time_slot_rank in enumerate(mapping):
            source = sorted_frames[source_rank]
            slot = sorted_frames[time_slot_rank].field_time
            reordered[time_slot_rank] = OrganismTimedReceptorFrame(source.frame, slot)
        output.append(ReceptorTimeSequence(sequence.modality_id, sequence.geometry_id, sequence.clock_id, tuple(reordered)))
    return tuple(output)


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def _pairwise_linf(vectors: tuple[tuple[float, ...], ...]) -> tuple[tuple[float, ...], ...]:
    return tuple(tuple(_linf(left, right) for right in vectors) for left in vectors)


def _pairwise_equal(values: tuple[str, ...]) -> tuple[tuple[bool, ...], ...]:
    return tuple(tuple(left == right for right in values) for left in values)


def execute_public_av_return_replication(
    path: Path,
    contract: PublicMediaSourceContract,
    wiring: PublicAVReturnReplicationRunnerWiring,
    preflight: PublicAVReturnReplicationPreflight,
    permutation_contract: PublicAVReturnPermutationContract,
) -> PublicAVReturnReplicationExecution:
    """Execute the fixed six-arm replication; callers must consume a one-shot gate first."""

    plan = public_av_return_replication_preregistration()
    if not isinstance(path, Path):
        raise PublicAVReturnReplicationExecutionError("path must be a pathlib.Path")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVReturnReplicationExecutionError("source contract is required")
    if not isinstance(wiring, PublicAVReturnReplicationRunnerWiring):
        raise PublicAVReturnReplicationExecutionError("runner wiring is required")
    if not isinstance(preflight, PublicAVReturnReplicationPreflight):
        raise PublicAVReturnReplicationExecutionError("positive replication preflight is required")
    if not isinstance(permutation_contract, PublicAVReturnPermutationContract):
        raise PublicAVReturnReplicationExecutionError("permutation contract is required")
    if not preflight.single_bounded_replication_run_release_granted or preflight.field_run_started:
        raise PublicAVReturnReplicationExecutionError("single bounded replication is not released")
    if preflight.media_path != str(path) or preflight.source_id != plan.source_id:
        raise PublicAVReturnReplicationExecutionError("preflight path or source differs")
    if contract.source_id != plan.source_id or wiring.source_id != plan.source_id:
        raise PublicAVReturnReplicationExecutionError("source differs from preregistration")
    if wiring.preregistration_id != plan.preregistration_id:
        raise PublicAVReturnReplicationExecutionError("runner preregistration differs")
    if wiring.permutation_contract_digest != permutation_contract.contract_digest:
        raise PublicAVReturnReplicationExecutionError("permutation contract digest differs")
    if not preflight.arm_ids_complete or not preflight.all_arms_wired or len(wiring.arms) != 6:
        raise PublicAVReturnReplicationExecutionError("six complete arms are required")

    stage_one_sequences = _sequences(path, contract)
    stage_two_sequences = shift_receptor_time_sequences(stage_one_sequences, 600_000_000)
    permuted_stage_two_sequences = _permuted_stage_two_sequences(stage_one_sequences, permutation_contract)
    stage_one_steps = _steps(stage_one_sequences, 0, 500_000_000)
    stage_two_steps = _steps(stage_two_sequences, 600_000_000, 1_100_000_000)
    permuted_stage_two_steps = _steps(permuted_stage_two_sequences, 600_000_000, 1_100_000_000)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)

    results = []
    for arm in wiring.arms:
        stage_one = run_neutral_asynchronous_field(
            _fresh_field(stage_one_sequences),
            stage_one_sequences,
            stage_one_steps,
            substrate,
            afterimage_config=afterimage,
        )
        stage_one_digest = stage_one.field.snapshot().digest()
        post_resolution = None
        intervention_id = None
        if arm.arm_id == "return.fresh_stage_two":
            stage_two_start = _fresh_field(stage_one_sequences)
        else:
            post_resolution = _advance_contact_free(stage_one.field, 500_000_000, 600_000_000, substrate, afterimage)
            if arm.component_intervention_mode is not None:
                intervention = intervene_shared_field_component(post_resolution, arm.component_intervention_mode)
                stage_two_start = intervention.field
                intervention_id = intervention.audit.intervention_id
            else:
                stage_two_start = post_resolution

        if arm.arm_id == "control.stage_two_sequence_withheld":
            stage_two_field = _advance_contact_free(stage_two_start, 600_000_000, 1_100_000_000, substrate, afterimage)
            stage_two_count = 0
        else:
            sequences = permuted_stage_two_sequences if arm.arm_id == permutation_contract.arm_id else stage_two_sequences
            steps = permuted_stage_two_steps if arm.arm_id == permutation_contract.arm_id else stage_two_steps
            stage_two = run_neutral_asynchronous_field(
                stage_two_start,
                sequences,
                steps,
                substrate,
                afterimage_config=afterimage,
            )
            stage_two_field = stage_two.field
            stage_two_count = stage_two.source_support_count

        activation = tuple(neuron.activation for neuron in stage_two_field.layer.neurons)
        trace = tuple(neuron.afterimage for neuron in stage_two_field.layer.neurons)
        results.append(
            PublicAVReturnReplicationArmResult(
                arm_id=arm.arm_id,
                stage_one_source_event_count=stage_one.source_support_count,
                stage_two_source_event_count=stage_two_count,
                stage_one_snapshot_digest=stage_one_digest,
                post_resolution_snapshot_digest=None if post_resolution is None else post_resolution.snapshot().digest(),
                intervention_audit_id=intervention_id,
                stage_two_snapshot_digest=stage_two_field.snapshot().digest(),
                stage_two_layer_digest=stage_two_field.layer.digest(),
                stage_two_activation=activation,
                stage_two_afterimage=trace,
                stage_two_contact_mode=arm.stage_two_contact_mode,
                stage_two_sequence_digest=arm.stage_two_sequence_digest,
            )
        )

    activations = tuple(item.stage_two_activation for item in results)
    traces = tuple(item.stage_two_afterimage for item in results)
    layers = tuple(item.stage_two_layer_digest for item in results)
    snapshots = tuple(item.stage_two_snapshot_digest for item in results)
    return PublicAVReturnReplicationExecution(
        execution_id="public.av.nasa-earthrise.return-replication.execution.v1",
        runner_id=wiring.runner_id,
        preflight_id=preflight.preflight_id,
        source_id=plan.source_id,
        clock_id=plan.clock_id,
        stage_duration_ticks=plan.stage_duration_ticks,
        resolution_duration_ticks=plan.resolution_duration_ticks,
        arms=tuple(results),
        pairwise_activation_linf=_pairwise_linf(activations),
        pairwise_afterimage_linf=_pairwise_linf(traces),
        layer_digest_equality=_pairwise_equal(layers),
        snapshot_digest_equality=_pairwise_equal(snapshots),
    )


def bind_public_av_return_replication_executor(
    preflight: PublicAVReturnReplicationPreflight,
    permutation_contract: PublicAVReturnPermutationContract,
) -> Callable[[Path, PublicMediaSourceContract, PublicAVReturnReplicationRunnerWiring], PublicAVReturnReplicationExecution]:
    if not isinstance(preflight, PublicAVReturnReplicationPreflight):
        raise PublicAVReturnReplicationExecutionError("positive replication preflight is required")
    if not isinstance(permutation_contract, PublicAVReturnPermutationContract):
        raise PublicAVReturnReplicationExecutionError("permutation contract is required")

    def _executor(
        path: Path,
        contract: PublicMediaSourceContract,
        wiring: PublicAVReturnReplicationRunnerWiring,
    ) -> PublicAVReturnReplicationExecution:
        return execute_public_av_return_replication(path, contract, wiring, preflight, permutation_contract)

    return _executor


def public_av_return_replication_execution_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVReturnReplicationArmResult, PublicAVReturnReplicationExecution)
        for item in fields(cls)
    )
