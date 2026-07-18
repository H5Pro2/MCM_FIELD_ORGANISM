"""Passive snapshot-resume control for explicit local field transitions."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import MCMNeuronTransition
from .passive_field_segmentation_comparison import (
    BoundaryDistributionFactory,
    FieldFactory,
    PassiveSegmentationBranch,
    PassiveSegmentationStep,
    PassiveFieldSegmentationError,
    TransitionFactory,
    _endpoint,
    _initial_field,
    _initial_field_digest,
)
from .receptor_proposal_handoff_audit import (
    ReceptorProposalBatch,
    ReceptorProposalHandoff,
    handoff_receptor_completion_groups,
)
from .receptor_time_alignment import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField, restore_shared_mcm_field
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class PassiveFieldResumeControlError(ValueError):
    """Raised when an interrupted field branch cannot be compared exactly."""


@dataclass(frozen=True, slots=True)
class PassiveResumeSegmentationComparison:
    segmentation_id: str
    resume_tick: int
    uninterrupted: PassiveSegmentationBranch
    resumed: PassiveSegmentationBranch
    snapshot_digest: str
    restored_snapshot_digest: str
    uninterrupted_reproducible: bool
    resumed_reproducible: bool
    traces_equal: bool


@dataclass(frozen=True, slots=True)
class PassiveFieldResumeComparison:
    coarse: PassiveResumeSegmentationComparison
    fine: PassiveResumeSegmentationComparison
    all_events_assigned_once: bool
    coarse_resume_exact: bool
    fine_resume_exact: bool


def _transition(
    factory: TransitionFactory,
) -> MCMNeuronTransition:
    if not callable(factory):
        raise PassiveFieldResumeControlError(
            "resume control requires one explicit transition factory"
        )
    transition = factory()
    if not callable(transition):
        raise PassiveFieldResumeControlError(
            "transition factory must return one explicit transition"
        )
    return transition


def _advance_batch(
    field: SharedMCMField,
    batch: ReceptorProposalBatch,
    transition: MCMNeuronTransition,
    distribution_factory: BoundaryDistributionFactory,
) -> tuple[SharedMCMField, PassiveSegmentationStep]:
    trajectory = map_proposal_batch_to_transient_docks(batch, field.docks)
    local_inputs = project_transient_docks_to_neuron_inputs(
        trajectory,
        field.docks,
    )
    distribution = distribution_factory(batch)
    try:
        next_field = field.advance(
            distribution,
            transition,
            transient_neuron_inputs=local_inputs,
        )
    except ValueError as exc:
        raise PassiveFieldResumeControlError(
            f"passive resume branch failed: {exc}"
        ) from exc
    return next_field, PassiveSegmentationStep(
        step_index=batch.batch_index,
        step_time=batch.step_time,
        event_count=batch.event_count,
        modality_event_counts=batch.modality_event_counts,
        technical_layer_tick=next_field.layer.tick,
        endpoint=_endpoint(next_field),
    )


def _branch(
    segmentation_id: str,
    handoff: ReceptorProposalHandoff,
    field_factory: FieldFactory,
    transition_factory: TransitionFactory,
    distribution_factory: BoundaryDistributionFactory,
    *,
    resume_tick: int | None,
) -> tuple[PassiveSegmentationBranch, str | None, str | None]:
    try:
        field = _initial_field(field_factory)
    except PassiveFieldSegmentationError as exc:
        raise PassiveFieldResumeControlError(str(exc)) from exc
    initial_digest = _initial_field_digest(field)
    transition = _transition(transition_factory)
    traces = []
    snapshot_digest = None
    restored_digest = None
    resumed = resume_tick is None
    for batch in handoff.batches:
        field, trace = _advance_batch(
            field,
            batch,
            transition,
            distribution_factory,
        )
        traces.append(trace)
        if resume_tick is not None and batch.step_time.end_tick == resume_tick:
            snapshot = field.snapshot()
            snapshot_digest = snapshot.digest()
            field = restore_shared_mcm_field(snapshot)
            restored_digest = field.snapshot().digest()
            transition = _transition(transition_factory)
            resumed = True
    if not resumed or snapshot_digest is None or restored_digest is None:
        if resume_tick is not None:
            raise PassiveFieldResumeControlError(
                "resume_tick must end one completed field step"
            )
    return (
        PassiveSegmentationBranch(
            segmentation_id=segmentation_id,
            initial_field_digest=initial_digest,
            source_event_count=handoff.source_event_count,
            assigned_event_count=handoff.assigned_event_count,
            every_event_assigned_once=(
                handoff.every_in_horizon_event_assigned_once
            ),
            steps=tuple(traces),
            endpoint=_endpoint(field),
        ),
        snapshot_digest,
        restored_digest,
    )


def _validated_steps(
    values: Iterable[MCMFieldStepTime],
    resume_tick: int,
    role: str,
) -> tuple[MCMFieldStepTime, ...]:
    steps = tuple(values)
    if len(steps) < 2 or any(not isinstance(item, MCMFieldStepTime) for item in steps):
        raise PassiveFieldResumeControlError(
            f"{role} requires at least two explicit field steps"
        )
    end_ticks = tuple(item.end_tick for item in steps)
    if resume_tick not in end_ticks[:-1]:
        raise PassiveFieldResumeControlError(
            f"{role} resume_tick must end a non-final field step"
        )
    return steps


def _compare_segmentation(
    segmentation_id: str,
    handoff: ReceptorProposalHandoff,
    resume_tick: int,
    field_factory: FieldFactory,
    transition_factory: TransitionFactory,
    distribution_factory: BoundaryDistributionFactory,
) -> PassiveResumeSegmentationComparison:
    uninterrupted, _, _ = _branch(
        segmentation_id,
        handoff,
        field_factory,
        transition_factory,
        distribution_factory,
        resume_tick=None,
    )
    uninterrupted_replay, _, _ = _branch(
        segmentation_id,
        handoff,
        field_factory,
        transition_factory,
        distribution_factory,
        resume_tick=None,
    )
    resumed, snapshot_digest, restored_digest = _branch(
        segmentation_id,
        handoff,
        field_factory,
        transition_factory,
        distribution_factory,
        resume_tick=resume_tick,
    )
    resumed_replay, replay_snapshot, replay_restored = _branch(
        segmentation_id,
        handoff,
        field_factory,
        transition_factory,
        distribution_factory,
        resume_tick=resume_tick,
    )
    initial_digests = {
        uninterrupted.initial_field_digest,
        uninterrupted_replay.initial_field_digest,
        resumed.initial_field_digest,
        resumed_replay.initial_field_digest,
    }
    if len(initial_digests) != 1:
        raise PassiveFieldResumeControlError(
            "resume branches must rebuild the same initial field"
        )
    if snapshot_digest is None or restored_digest is None:
        raise PassiveFieldResumeControlError(
            "resumed branch did not produce a complete snapshot boundary"
        )
    return PassiveResumeSegmentationComparison(
        segmentation_id=segmentation_id,
        resume_tick=resume_tick,
        uninterrupted=uninterrupted,
        resumed=resumed,
        snapshot_digest=snapshot_digest,
        restored_snapshot_digest=restored_digest,
        uninterrupted_reproducible=(
            uninterrupted == uninterrupted_replay
        ),
        resumed_reproducible=(
            resumed == resumed_replay
            and snapshot_digest == replay_snapshot
            and restored_digest == replay_restored
        ),
        traces_equal=(
            uninterrupted == resumed
            and snapshot_digest == restored_digest
        ),
    )


def compare_passive_field_resume(
    sequences: Iterable[ReceptorTimeSequence],
    coarse_steps: Iterable[MCMFieldStepTime],
    fine_steps: Iterable[MCMFieldStepTime],
    *,
    resume_tick: int,
    field_factory: FieldFactory,
    transition_factory: TransitionFactory,
    distribution_factory: BoundaryDistributionFactory,
) -> PassiveFieldResumeComparison:
    """Compare uninterrupted and independently restored passive field paths."""

    if isinstance(resume_tick, bool) or not isinstance(resume_tick, int):
        raise PassiveFieldResumeControlError("resume_tick must be an integer")
    sequences_in = tuple(sequences)
    coarse_steps_in = _validated_steps(
        coarse_steps,
        resume_tick,
        "coarse segmentation",
    )
    fine_steps_in = _validated_steps(
        fine_steps,
        resume_tick,
        "fine segmentation",
    )
    coarse_horizon = (
        coarse_steps_in[0].clock_id,
        coarse_steps_in[0].start_tick,
        coarse_steps_in[-1].end_tick,
        coarse_steps_in[0].ticks_per_second,
    )
    fine_horizon = (
        fine_steps_in[0].clock_id,
        fine_steps_in[0].start_tick,
        fine_steps_in[-1].end_tick,
        fine_steps_in[0].ticks_per_second,
    )
    if coarse_horizon != fine_horizon:
        raise PassiveFieldResumeControlError(
            "resume segmentations must cover the same organism horizon"
        )
    try:
        coarse_handoff = handoff_receptor_completion_groups(
            sequences_in,
            coarse_steps_in,
        )
        fine_handoff = handoff_receptor_completion_groups(
            sequences_in,
            fine_steps_in,
        )
    except ValueError as exc:
        raise PassiveFieldResumeControlError(
            f"resume handoff failed: {exc}"
        ) from exc
    if (
        not coarse_handoff.every_in_horizon_event_assigned_once
        or not fine_handoff.every_in_horizon_event_assigned_once
        or coarse_handoff.assigned_event_count != fine_handoff.assigned_event_count
    ):
        raise PassiveFieldResumeControlError(
            "resume segmentations must assign every source event exactly once"
        )
    coarse = _compare_segmentation(
        "coarse",
        coarse_handoff,
        resume_tick,
        field_factory,
        transition_factory,
        distribution_factory,
    )
    fine = _compare_segmentation(
        "fine",
        fine_handoff,
        resume_tick,
        field_factory,
        transition_factory,
        distribution_factory,
    )
    return PassiveFieldResumeComparison(
        coarse=coarse,
        fine=fine,
        all_events_assigned_once=True,
        coarse_resume_exact=coarse.traces_equal,
        fine_resume_exact=fine.traces_equal,
    )


def passive_field_resume_control_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            PassiveResumeSegmentationComparison,
            PassiveFieldResumeComparison,
        )
        for item in fields(contract)
    )
