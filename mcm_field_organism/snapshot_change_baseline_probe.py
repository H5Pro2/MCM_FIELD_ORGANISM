"""Passive change baselines for ordered immutable receptor snapshots."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math


class SnapshotChangeBaselineProbeError(ValueError):
    """Raised when a controlled snapshot history is malformed."""


@dataclass(frozen=True, slots=True)
class TimedSnapshotValue:
    completion_tick: int
    value: float

    def __post_init__(self) -> None:
        if (
            isinstance(self.completion_tick, bool)
            or not isinstance(self.completion_tick, int)
            or self.completion_tick < 0
        ):
            raise SnapshotChangeBaselineProbeError(
                "completion_tick must be a non-negative integer"
            )
        value = float(self.value)
        if not math.isfinite(value) or abs(value) > 1.0:
            raise SnapshotChangeBaselineProbeError(
                "snapshot value must remain within -1..1"
            )
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, slots=True)
class SnapshotValueSequence:
    sequence_id: str
    tick_seconds: float
    snapshots: tuple[TimedSnapshotValue, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.sequence_id, str) or not self.sequence_id:
            raise SnapshotChangeBaselineProbeError(
                "sequence_id must not be empty"
            )
        tick_seconds = float(self.tick_seconds)
        if not math.isfinite(tick_seconds) or tick_seconds <= 0.0:
            raise SnapshotChangeBaselineProbeError(
                "tick_seconds must be finite and positive"
            )
        snapshots = tuple(self.snapshots)
        if len(snapshots) < 2 or any(
            not isinstance(item, TimedSnapshotValue) for item in snapshots
        ):
            raise SnapshotChangeBaselineProbeError(
                "snapshot sequence requires at least two timed values"
            )
        ticks = tuple(item.completion_tick for item in snapshots)
        if ticks[0] != 0 or any(
            later <= earlier for earlier, later in zip(ticks, ticks[1:])
        ):
            raise SnapshotChangeBaselineProbeError(
                "snapshot completion ticks must increase strictly from zero"
            )
        object.__setattr__(self, "tick_seconds", tick_seconds)
        object.__setattr__(self, "snapshots", snapshots)


@dataclass(frozen=True, slots=True)
class SnapshotChangeObservation:
    sequence_id: str
    snapshot_count: int
    observation_span_seconds: float
    signed_change_sum: float
    absolute_change_sum: float
    endpoint_change: float


@dataclass(frozen=True, slots=True)
class SnapshotChangeComparison:
    comparison_id: str
    first: SnapshotChangeObservation
    second: SnapshotChangeObservation
    signed_change_difference: float
    absolute_change_difference: float
    span_difference_seconds: float


@dataclass(frozen=True, slots=True)
class SnapshotChangeBaselineProbeResult:
    monotonic_rate_split: SnapshotChangeComparison
    return_path_rate_split: SnapshotChangeComparison
    duplicate_density: SnapshotChangeComparison
    omitted_oscillation: SnapshotChangeComparison
    unequal_dwell: SnapshotChangeComparison


def observe_snapshot_changes(
    sequence: SnapshotValueSequence,
) -> SnapshotChangeObservation:
    """Measure deltas without retaining or extending the last snapshot."""

    if not isinstance(sequence, SnapshotValueSequence):
        raise SnapshotChangeBaselineProbeError(
            "change observation requires one snapshot sequence"
        )
    values = tuple(item.value for item in sequence.snapshots)
    changes = tuple(later - earlier for earlier, later in zip(values, values[1:]))
    return SnapshotChangeObservation(
        sequence_id=sequence.sequence_id,
        snapshot_count=len(sequence.snapshots),
        observation_span_seconds=(
            sequence.snapshots[-1].completion_tick
            - sequence.snapshots[0].completion_tick
        )
        * sequence.tick_seconds,
        signed_change_sum=sum(changes),
        absolute_change_sum=sum(abs(change) for change in changes),
        endpoint_change=values[-1] - values[0],
    )


def compare_snapshot_changes(
    comparison_id: str,
    first: SnapshotValueSequence,
    second: SnapshotValueSequence,
) -> SnapshotChangeComparison:
    if not comparison_id:
        raise SnapshotChangeBaselineProbeError("comparison_id must not be empty")
    if first.tick_seconds != second.tick_seconds:
        raise SnapshotChangeBaselineProbeError(
            "compared sequences must share one tick scale"
        )
    left = observe_snapshot_changes(first)
    right = observe_snapshot_changes(second)
    return SnapshotChangeComparison(
        comparison_id=comparison_id,
        first=left,
        second=right,
        signed_change_difference=abs(
            left.signed_change_sum - right.signed_change_sum
        ),
        absolute_change_difference=abs(
            left.absolute_change_sum - right.absolute_change_sum
        ),
        span_difference_seconds=abs(
            left.observation_span_seconds - right.observation_span_seconds
        ),
    )


def _sequence(
    sequence_id: str,
    ticks: tuple[int, ...],
    values: tuple[float, ...],
) -> SnapshotValueSequence:
    return SnapshotValueSequence(
        sequence_id,
        0.1,
        tuple(
            TimedSnapshotValue(tick, value)
            for tick, value in zip(ticks, values, strict=True)
        ),
    )


def run_snapshot_change_baseline_probe() -> SnapshotChangeBaselineProbeResult:
    """Compare change measures across five controlled history pairs."""

    return SnapshotChangeBaselineProbeResult(
        monotonic_rate_split=compare_snapshot_changes(
            "monotonic_rate_split",
            _sequence("ramp.dense", (0, 1, 2, 3, 4), (0.0, 0.25, 0.5, 0.75, 1.0)),
            _sequence("ramp.sparse", (0, 4), (0.0, 1.0)),
        ),
        return_path_rate_split=compare_snapshot_changes(
            "return_path_rate_split",
            _sequence("return.dense", (0, 1, 2, 3, 4), (0.0, 0.5, 1.0, 0.5, 0.0)),
            _sequence("return.sparse", (0, 2, 4), (0.0, 1.0, 0.0)),
        ),
        duplicate_density=compare_snapshot_changes(
            "duplicate_density",
            _sequence(
                "duplicate.dense",
                (0, 1, 2, 3, 4, 5, 6),
                (0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0),
            ),
            _sequence("duplicate.sparse", (0, 3, 6), (0.0, 1.0, 0.0)),
        ),
        omitted_oscillation=compare_snapshot_changes(
            "omitted_oscillation",
            _sequence("oscillation.visible", (0, 1, 2, 3, 4), (0.0, 1.0, 0.0, 1.0, 0.0)),
            _sequence("oscillation.omitted", (0, 4), (0.0, 0.0)),
        ),
        unequal_dwell=compare_snapshot_changes(
            "unequal_dwell",
            _sequence("dwell.short", (0, 1, 2), (0.0, 1.0, 0.0)),
            _sequence("dwell.long", (0, 5, 10), (0.0, 1.0, 0.0)),
        ),
    )


def snapshot_change_baseline_probe_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            TimedSnapshotValue,
            SnapshotValueSequence,
            SnapshotChangeObservation,
            SnapshotChangeComparison,
            SnapshotChangeBaselineProbeResult,
        )
        for item in fields(contract)
    )
