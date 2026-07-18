"""Passive completion-event audit for asynchronous receptor sequences."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

from .receptor_time_alignment import ReceptorTimeSequence


class AsynchronousReceptorEventError(ValueError):
    """Raised when receptor completion events cannot share one audit clock."""


@dataclass(frozen=True, slots=True)
class ReceptorCompletionEvent:
    modality_id: str
    snapshot_id: str
    read_start_tick: int
    completion_tick: int


@dataclass(frozen=True, slots=True)
class ReceptorCompletionGroup:
    completion_tick: int
    events: tuple[ReceptorCompletionEvent, ...]

    @property
    def modality_ids(self) -> tuple[str, ...]:
        return tuple(event.modality_id for event in self.events)


@dataclass(frozen=True, slots=True)
class AsynchronousReceptorEventAudit:
    clock_id: str
    modality_ids: tuple[str, ...]
    event_counts: tuple[tuple[str, int], ...]
    completion_groups: tuple[ReceptorCompletionGroup, ...]
    mixed_completion_group_count: int
    exclusive_completion_group_counts: tuple[tuple[str, int], ...]

    @property
    def total_event_count(self) -> int:
        return sum(count for _, count in self.event_counts)

    def event_share(self, modality_id: str) -> float:
        counts = dict(self.event_counts)
        if modality_id not in counts:
            raise KeyError(modality_id)
        return counts[modality_id] / self.total_event_count


def audit_asynchronous_receptor_events(
    sequences: Iterable[ReceptorTimeSequence],
) -> AsynchronousReceptorEventAudit:
    """Group native states by measured completion without inventing field ticks."""

    sequences_in = tuple(sequences)
    if not sequences_in or any(
        not isinstance(sequence, ReceptorTimeSequence)
        for sequence in sequences_in
    ):
        raise AsynchronousReceptorEventError(
            "event audit requires receptor time sequences"
        )
    clocks = {sequence.clock_id for sequence in sequences_in}
    if len(clocks) != 1:
        raise AsynchronousReceptorEventError(
            "event audit requires one organism clock"
        )
    modality_ids = tuple(sorted(sequence.modality_id for sequence in sequences_in))
    if len(set(modality_ids)) != len(modality_ids):
        raise AsynchronousReceptorEventError(
            "event audit requires unique receptor modalities"
        )

    events = tuple(
        ReceptorCompletionEvent(
            modality_id=sequence.modality_id,
            snapshot_id=item.frame.snapshot_id,
            read_start_tick=item.field_time.window_start_tick,
            completion_tick=item.field_time.window_end_tick,
        )
        for sequence in sequences_in
        for item in sequence.frames
    )
    by_completion: dict[int, list[ReceptorCompletionEvent]] = {}
    for event in events:
        by_completion.setdefault(event.completion_tick, []).append(event)
    groups = tuple(
        ReceptorCompletionGroup(
            completion_tick,
            tuple(
                sorted(
                    grouped,
                    key=lambda event: (
                        event.modality_id,
                        event.snapshot_id,
                        event.read_start_tick,
                    ),
                )
            ),
        )
        for completion_tick, grouped in sorted(by_completion.items())
    )
    event_counts = tuple(
        (
            modality_id,
            sum(event.modality_id == modality_id for event in events),
        )
        for modality_id in modality_ids
    )
    mixed_count = sum(len(set(group.modality_ids)) > 1 for group in groups)
    exclusive_counts = tuple(
        (
            modality_id,
            sum(group.modality_ids == (modality_id,) for group in groups),
        )
        for modality_id in modality_ids
    )
    return AsynchronousReceptorEventAudit(
        clock_id=next(iter(clocks)),
        modality_ids=modality_ids,
        event_counts=event_counts,
        completion_groups=groups,
        mixed_completion_group_count=mixed_count,
        exclusive_completion_group_counts=exclusive_counts,
    )


def asynchronous_receptor_event_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            ReceptorCompletionEvent,
            ReceptorCompletionGroup,
            AsynchronousReceptorEventAudit,
        )
        for item in fields(cls)
    )
