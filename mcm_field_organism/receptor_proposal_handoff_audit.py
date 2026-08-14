"""Passive lossless handoff of completion groups into proposal spans."""

from __future__ import annotations

from dataclasses import dataclass, fields
from .field_step_time import MCMFieldStepTime
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_proposal_handoff import (
    ReceptorProposalBatch,
    ReceptorProposalCompletionGroup,
    ReceptorProposalHandoff,
    ReceptorProposalHandoffError,
    handoff_receptor_completion_groups,
)
from .receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
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
