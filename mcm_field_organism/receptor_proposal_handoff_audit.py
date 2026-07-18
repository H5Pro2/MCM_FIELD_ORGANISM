"""Passive lossless handoff of completion groups into proposal spans."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

from .asynchronous_receptor_events import audit_asynchronous_receptor_events
from .field_step_time import MCMFieldStepTime
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


class ReceptorProposalHandoffError(ValueError):
    """Raised when events and proposal spans cannot form one causal handoff."""


@dataclass(frozen=True, slots=True)
class ReceptorProposalCompletionGroup:
    completion_tick: int
    timed_frames: tuple[OrganismTimedReceptorFrame, ...]

    @property
    def modality_ids(self) -> tuple[str, ...]:
        return tuple(item.frame.modality_id for item in self.timed_frames)


@dataclass(frozen=True, slots=True)
class ReceptorProposalBatch:
    batch_index: int
    step_time: MCMFieldStepTime
    completion_groups: tuple[ReceptorProposalCompletionGroup, ...]
    modality_event_counts: tuple[tuple[str, int], ...]

    @property
    def event_count(self) -> int:
        return sum(len(group.timed_frames) for group in self.completion_groups)


@dataclass(frozen=True, slots=True)
class ReceptorProposalHandoff:
    clock_id: str
    modality_ids: tuple[str, ...]
    batches: tuple[ReceptorProposalBatch, ...]
    source_event_count: int
    assigned_event_count: int
    completed_before_or_at_start_snapshot_ids: tuple[str, ...]
    completed_after_horizon_snapshot_ids: tuple[str, ...]
    every_in_horizon_event_assigned_once: bool

    def snapshot_ids_for(self, modality_id: str) -> tuple[str, ...]:
        if modality_id not in self.modality_ids:
            raise KeyError(modality_id)
        return tuple(
            item.frame.snapshot_id
            for batch in self.batches
            for group in batch.completion_groups
            for item in group.timed_frames
            if item.frame.modality_id == modality_id
        )

    def frames_for(self, modality_id: str) -> tuple[ReceptorContactFrame, ...]:
        if modality_id not in self.modality_ids:
            raise KeyError(modality_id)
        return tuple(
            item.frame
            for batch in self.batches
            for group in batch.completion_groups
            for item in group.timed_frames
            if item.frame.modality_id == modality_id
        )


@dataclass(frozen=True, slots=True)
class ProposalSegmentationComparison:
    coarse: ReceptorProposalHandoff
    fine: ReceptorProposalHandoff
    source_snapshot_ids_by_modality: tuple[tuple[str, tuple[str, ...]], ...]
    coarse_preserves_dock_order: bool
    fine_preserves_dock_order: bool
    coarse_preserves_reduced_frames: bool
    fine_preserves_reduced_frames: bool
    segmentations_reconstruct_same_dock_sequences: bool


def _validated_steps(
    proposal_steps: Iterable[MCMFieldStepTime],
) -> tuple[MCMFieldStepTime, ...]:
    steps = tuple(proposal_steps)
    if not steps or any(not isinstance(item, MCMFieldStepTime) for item in steps):
        raise ReceptorProposalHandoffError(
            "handoff requires explicit proposal step times"
        )
    clock_id = steps[0].clock_id
    if any(item.clock_id != clock_id for item in steps):
        raise ReceptorProposalHandoffError(
            "proposal steps must share one organism clock"
        )
    for previous, current in zip(steps, steps[1:]):
        if previous.end_tick != current.start_tick:
            raise ReceptorProposalHandoffError(
                "proposal steps must be contiguous and ordered"
            )
        if previous.ticks_per_second != current.ticks_per_second:
            raise ReceptorProposalHandoffError(
                "proposal steps must share one clock rate"
            )
    return steps


def handoff_receptor_completion_groups(
    sequences: Iterable[ReceptorTimeSequence],
    proposal_steps: Iterable[MCMFieldStepTime],
) -> ReceptorProposalHandoff:
    """Assign every in-horizon completion group once, without reducing it."""

    steps = _validated_steps(proposal_steps)
    sequences_in = tuple(sequences)
    event_audit = audit_asynchronous_receptor_events(sequences_in)
    if event_audit.clock_id != steps[0].clock_id:
        raise ReceptorProposalHandoffError(
            "receptor events and proposal steps must share one organism clock"
        )
    horizon_start = steps[0].start_tick
    horizon_end = steps[-1].end_tick
    all_frames = tuple(
        item
        for sequence in sequences_in
        for item in sequence.frames
    )
    before = tuple(
        sorted(
            item.frame.snapshot_id
            for item in all_frames
            if item.field_time.window_end_tick <= horizon_start
        )
    )
    after = tuple(
        sorted(
            item.frame.snapshot_id
            for item in all_frames
            if item.field_time.window_end_tick > horizon_end
        )
    )
    frames_by_completion: dict[int, list[OrganismTimedReceptorFrame]] = {}
    for item in all_frames:
        frames_by_completion.setdefault(
            item.field_time.window_end_tick, []
        ).append(item)
    completion_groups = tuple(
        ReceptorProposalCompletionGroup(
            completion_tick,
            tuple(
                sorted(
                    grouped,
                    key=lambda item: (
                        item.frame.modality_id,
                        item.frame.snapshot_id,
                        item.field_time.window_start_tick,
                    ),
                )
            ),
        )
        for completion_tick, grouped in sorted(frames_by_completion.items())
    )
    batches = []
    for batch_index, step in enumerate(steps):
        groups = tuple(
            group
            for group in completion_groups
            if step.start_tick < group.completion_tick <= step.end_tick
        )
        batches.append(
            ReceptorProposalBatch(
                batch_index=batch_index,
                step_time=step,
                completion_groups=groups,
                modality_event_counts=tuple(
                    (
                        modality_id,
                        sum(
                            item.frame.modality_id == modality_id
                            for group in groups
                            for item in group.timed_frames
                        ),
                    )
                    for modality_id in event_audit.modality_ids
                ),
            )
        )
    assigned_frames = tuple(
        item
        for batch in batches
        for group in batch.completion_groups
        for item in group.timed_frames
    )
    in_horizon_keys = tuple(
        (item.frame.modality_id, item.frame.snapshot_id)
        for item in all_frames
        if horizon_start < item.field_time.window_end_tick <= horizon_end
    )
    assigned_keys = tuple(
        (item.frame.modality_id, item.frame.snapshot_id)
        for item in assigned_frames
    )
    return ReceptorProposalHandoff(
        clock_id=event_audit.clock_id,
        modality_ids=event_audit.modality_ids,
        batches=tuple(batches),
        source_event_count=len(all_frames),
        assigned_event_count=len(assigned_frames),
        completed_before_or_at_start_snapshot_ids=before,
        completed_after_horizon_snapshot_ids=after,
        every_in_horizon_event_assigned_once=(
            len(assigned_keys) == len(set(assigned_keys))
            and sorted(assigned_keys) == sorted(in_horizon_keys)
        ),
    )


def _sequence(
    modality_id: str,
    completion_ticks: tuple[int, ...],
) -> ReceptorTimeSequence:
    geometry_id = f"{modality_id}.geometry.v1"
    return ReceptorTimeSequence(
        modality_id,
        geometry_id,
        "organism.test",
        tuple(
            OrganismTimedReceptorFrame(
                ReceptorContactFrame(
                    modality_id=modality_id,
                    geometry_id=geometry_id,
                    snapshot_id=f"{modality_id}.receptor.{index}",
                    clock_id=f"{modality_id}.source",
                    window_start_tick=index,
                    window_end_tick=index + 1,
                    carrier_ids=(f"{modality_id}.carrier.0",),
                    values=(0.25,),
                ),
                CommonFieldTime(
                    "organism.test",
                    completion_tick - 1,
                    completion_tick,
                ),
            )
            for index, completion_tick in enumerate(completion_ticks)
        ),
    )


def _steps(boundaries: tuple[int, ...]) -> tuple[MCMFieldStepTime, ...]:
    return tuple(
        MCMFieldStepTime("organism.test", start, end, 10.0)
        for start, end in zip(boundaries, boundaries[1:])
    )


def run_receptor_proposal_handoff_audit() -> ProposalSegmentationComparison:
    """Compare two proposal segmentations of the same asynchronous history."""

    sequences = (
        _sequence("auditory", (1, 2, 4, 5, 7, 8, 10, 12)),
        _sequence("visual", (3, 7, 11)),
    )
    coarse = handoff_receptor_completion_groups(
        sequences,
        _steps((0, 6, 12)),
    )
    fine = handoff_receptor_completion_groups(
        sequences,
        _steps((0, 3, 6, 9, 12)),
    )
    source = tuple(
        (
            sequence.modality_id,
            tuple(item.frame.snapshot_id for item in sequence.frames),
        )
        for sequence in sequences
    )
    source_by_modality = dict(source)
    source_frames = {
        sequence.modality_id: tuple(item.frame for item in sequence.frames)
        for sequence in sequences
    }
    coarse_preserves = all(
        coarse.snapshot_ids_for(modality_id) == snapshot_ids
        for modality_id, snapshot_ids in source
    )
    fine_preserves = all(
        fine.snapshot_ids_for(modality_id) == snapshot_ids
        for modality_id, snapshot_ids in source
    )
    coarse_frames = all(
        coarse.frames_for(modality_id) == frames
        for modality_id, frames in source_frames.items()
    )
    fine_frames = all(
        fine.frames_for(modality_id) == frames
        for modality_id, frames in source_frames.items()
    )
    same = all(
        coarse.snapshot_ids_for(modality_id)
        == fine.snapshot_ids_for(modality_id)
        == source_by_modality[modality_id]
        for modality_id in coarse.modality_ids
    )
    return ProposalSegmentationComparison(
        coarse=coarse,
        fine=fine,
        source_snapshot_ids_by_modality=source,
        coarse_preserves_dock_order=coarse_preserves,
        fine_preserves_dock_order=fine_preserves,
        coarse_preserves_reduced_frames=coarse_frames,
        fine_preserves_reduced_frames=fine_frames,
        segmentations_reconstruct_same_dock_sequences=same,
    )


def receptor_proposal_handoff_audit_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            ReceptorProposalCompletionGroup,
            ReceptorProposalBatch,
            ReceptorProposalHandoff,
            ProposalSegmentationComparison,
        )
        for item in fields(contract)
    )
