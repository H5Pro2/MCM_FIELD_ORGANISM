"""Passive same-dock adjacency audit for asynchronous receptor completions."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

from .asynchronous_receptor_events import audit_asynchronous_receptor_events
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_time_alignment import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


@dataclass(frozen=True, slots=True)
class DockAdjacencyMeasure:
    modality_id: str
    event_count: int
    within_dock_pair_count: int
    globally_adjacent_pair_count: int
    interrupted_pair_count: int
    intervening_group_counts: tuple[int, ...]

    @property
    def globally_adjacent_pair_fraction(self) -> float | None:
        if self.within_dock_pair_count == 0:
            return None
        return self.globally_adjacent_pair_count / self.within_dock_pair_count


@dataclass(frozen=True, slots=True)
class DockAdjacencyAudit:
    clock_id: str
    completion_group_count: int
    measures: tuple[DockAdjacencyMeasure, ...]

    def measure(self, modality_id: str) -> DockAdjacencyMeasure:
        for item in self.measures:
            if item.modality_id == modality_id:
                return item
        raise KeyError(modality_id)


@dataclass(frozen=True, slots=True)
class AsynchronousDockAdjacencyAuditResult:
    alternating: DockAdjacencyAudit
    rate_skewed: DockAdjacencyAudit
    synchronized: DockAdjacencyAudit
    rate_skewed_information_is_asymmetric: bool


def audit_asynchronous_dock_adjacency(
    sequences: Iterable[ReceptorTimeSequence],
) -> DockAdjacencyAudit:
    """Compare local sequence adjacency with global completion adjacency."""

    event_audit = audit_asynchronous_receptor_events(sequences)
    group_indexes: dict[str, list[int]] = {
        modality_id: [] for modality_id in event_audit.modality_ids
    }
    for group_index, group in enumerate(event_audit.completion_groups):
        for modality_id in group.modality_ids:
            group_indexes[modality_id].append(group_index)

    measures = []
    for modality_id in event_audit.modality_ids:
        indexes = tuple(group_indexes[modality_id])
        gaps = tuple(
            current - previous - 1
            for previous, current in zip(indexes, indexes[1:])
        )
        adjacent = sum(gap == 0 for gap in gaps)
        measures.append(
            DockAdjacencyMeasure(
                modality_id=modality_id,
                event_count=len(indexes),
                within_dock_pair_count=max(0, len(indexes) - 1),
                globally_adjacent_pair_count=adjacent,
                interrupted_pair_count=sum(gap > 0 for gap in gaps),
                intervening_group_counts=gaps,
            )
        )
    return DockAdjacencyAudit(
        clock_id=event_audit.clock_id,
        completion_group_count=len(event_audit.completion_groups),
        measures=tuple(measures),
    )


def _sequence(
    modality_id: str,
    completion_ticks: tuple[int, ...],
) -> ReceptorTimeSequence:
    geometry_id = f"{modality_id}.geometry.v1"
    frames = tuple(
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
            CommonFieldTime("organism.test", completion_tick - 1, completion_tick),
        )
        for index, completion_tick in enumerate(completion_ticks)
    )
    return ReceptorTimeSequence(
        modality_id,
        geometry_id,
        "organism.test",
        frames,
    )


def run_asynchronous_dock_adjacency_audit(
) -> AsynchronousDockAdjacencyAuditResult:
    """Expose adjacency loss without treating completion groups as field ticks."""

    alternating = audit_asynchronous_dock_adjacency(
        (
            _sequence("auditory", (1, 3, 5)),
            _sequence("visual", (2, 4, 6)),
        )
    )
    auditory_ticks = tuple(range(10, 3101, 10))
    visual_ticks = tuple(round(index * 3100 / 17) for index in range(1, 17))
    rate_skewed = audit_asynchronous_dock_adjacency(
        (
            _sequence("auditory", auditory_ticks),
            _sequence("visual", visual_ticks),
        )
    )
    synchronized = audit_asynchronous_dock_adjacency(
        (
            _sequence("auditory", (1, 2, 3)),
            _sequence("visual", (1, 2, 3)),
        )
    )
    auditory = rate_skewed.measure("auditory")
    visual = rate_skewed.measure("visual")
    return AsynchronousDockAdjacencyAuditResult(
        alternating=alternating,
        rate_skewed=rate_skewed,
        synchronized=synchronized,
        rate_skewed_information_is_asymmetric=(
            auditory.globally_adjacent_pair_fraction
            != visual.globally_adjacent_pair_fraction
        ),
    )


def asynchronous_dock_adjacency_audit_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            DockAdjacencyMeasure,
            DockAdjacencyAudit,
            AsynchronousDockAdjacencyAuditResult,
        )
        for item in fields(contract)
    )
