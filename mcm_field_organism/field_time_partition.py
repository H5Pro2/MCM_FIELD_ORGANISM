"""Lossless time partition from asynchronous receptor completion boundaries."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
from typing import Iterable

from .asynchronous_receptor_events import (
    ReceptorCompletionEvent,
    audit_asynchronous_receptor_events,
)
from .field_step_time import MCMFieldStepTime
from .receptor_time_alignment import ReceptorTimeSequence


class FieldTimePartitionError(ValueError):
    """Raised when completion events cannot form one bounded time partition."""


@dataclass(frozen=True, slots=True)
class FieldTimeSlice:
    slice_index: int
    step_time: MCMFieldStepTime
    completion_events: tuple[ReceptorCompletionEvent, ...]

    def __post_init__(self) -> None:
        if (
            isinstance(self.slice_index, bool)
            or not isinstance(self.slice_index, int)
            or self.slice_index < 0
        ):
            raise FieldTimePartitionError("slice_index must be non-negative")
        if not isinstance(self.step_time, MCMFieldStepTime):
            raise FieldTimePartitionError(
                "field time slice requires one passive step-time contract"
            )
        events = tuple(self.completion_events)
        if any(
            not isinstance(event, ReceptorCompletionEvent) for event in events
        ):
            raise FieldTimePartitionError(
                "completion_events must contain measured receptor events"
            )
        if any(event.completion_tick != self.step_time.end_tick for event in events):
            raise FieldTimePartitionError(
                "events must remain attached to their measured completion boundary"
            )
        object.__setattr__(
            self,
            "completion_events",
            tuple(sorted(events, key=lambda event: (event.modality_id, event.snapshot_id))),
        )


@dataclass(frozen=True, slots=True)
class FieldTimePartition:
    clock_id: str
    horizon_start_tick: int
    horizon_end_tick: int
    ticks_per_second: float
    slices: tuple[FieldTimeSlice, ...]
    completed_before_or_at_start_snapshot_ids: tuple[str, ...]
    completed_after_horizon_snapshot_ids: tuple[str, ...]

    @property
    def eventful_slice_count(self) -> int:
        return sum(bool(item.completion_events) for item in self.slices)

    @property
    def empty_slice_count(self) -> int:
        return len(self.slices) - self.eventful_slice_count

    @property
    def covered_ticks(self) -> int:
        return sum(item.step_time.elapsed_ticks for item in self.slices)


def partition_receptor_completion_time(
    sequences: Iterable[ReceptorTimeSequence],
    *,
    horizon_start_tick: int,
    horizon_end_tick: int,
    ticks_per_second: float,
) -> FieldTimePartition:
    """Partition one horizon without turning the slices into field updates."""

    if (
        isinstance(horizon_start_tick, bool)
        or isinstance(horizon_end_tick, bool)
        or not isinstance(horizon_start_tick, int)
        or not isinstance(horizon_end_tick, int)
        or horizon_start_tick < 0
        or horizon_end_tick <= horizon_start_tick
    ):
        raise FieldTimePartitionError(
            "partition horizon must be one positive ordered interval"
        )
    rate = float(ticks_per_second)
    if not math.isfinite(rate) or rate <= 0.0:
        raise FieldTimePartitionError(
            "ticks_per_second must be finite and greater than zero"
        )
    event_audit = audit_asynchronous_receptor_events(sequences)
    all_events = tuple(
        event
        for group in event_audit.completion_groups
        for event in group.events
    )
    before = tuple(
        sorted(
            event.snapshot_id
            for event in all_events
            if event.completion_tick <= horizon_start_tick
        )
    )
    after = tuple(
        sorted(
            event.snapshot_id
            for event in all_events
            if event.completion_tick > horizon_end_tick
        )
    )
    in_horizon: dict[int, tuple[ReceptorCompletionEvent, ...]] = {
        group.completion_tick: group.events
        for group in event_audit.completion_groups
        if horizon_start_tick < group.completion_tick <= horizon_end_tick
    }
    boundaries = tuple(sorted(set(in_horizon) | {horizon_end_tick}))
    cursor = horizon_start_tick
    slices = []
    for boundary in boundaries:
        slices.append(
            FieldTimeSlice(
                slice_index=len(slices),
                step_time=MCMFieldStepTime(
                    event_audit.clock_id,
                    cursor,
                    boundary,
                    rate,
                ),
                completion_events=in_horizon.get(boundary, ()),
            )
        )
        cursor = boundary
    partition = FieldTimePartition(
        clock_id=event_audit.clock_id,
        horizon_start_tick=horizon_start_tick,
        horizon_end_tick=horizon_end_tick,
        ticks_per_second=rate,
        slices=tuple(slices),
        completed_before_or_at_start_snapshot_ids=before,
        completed_after_horizon_snapshot_ids=after,
    )
    if partition.covered_ticks != horizon_end_tick - horizon_start_tick:
        raise FieldTimePartitionError("field time partition must cover the horizon")
    return partition


def field_time_partition_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (FieldTimeSlice, FieldTimePartition)
        for item in fields(cls)
    )
