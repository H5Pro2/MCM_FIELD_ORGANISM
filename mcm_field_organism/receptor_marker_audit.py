"""Reporting-only transient audit for reduced multimodal receptor states."""

from __future__ import annotations

from dataclasses import dataclass

from .receptor_time_alignment import ReceptorTimeSequence


@dataclass(frozen=True, slots=True)
class ReceptorTransient:
    modality_id: str
    organism_tick: int
    score: float


@dataclass(frozen=True, slots=True)
class ReceptorMarkerAudit:
    clock_id: str
    baseline_end_tick: int
    marker_start_tick: int
    thresholds: tuple[tuple[str, float], ...]
    responses: tuple[tuple[str, tuple[ReceptorTransient, ...]], ...]
    visual_minus_auditory_nanoseconds: tuple[int, ...]
    complete_order_pairing: bool


def _transients(sequence: ReceptorTimeSequence) -> tuple[ReceptorTransient, ...]:
    result = []
    for earlier, later in zip(sequence.frames, sequence.frames[1:]):
        if len(earlier.frame.values) != len(later.frame.values):
            raise ValueError("receptor geometry changed within one sequence")
        score = sum(
            abs(right - left)
            for left, right in zip(earlier.frame.values, later.frame.values)
        ) / len(later.frame.values)
        result.append(
            ReceptorTransient(
                modality_id=sequence.modality_id,
                organism_tick=later.field_time.window_start_tick,
                score=score,
            )
        )
    return tuple(result)


def _separated_strongest(
    candidates: tuple[ReceptorTransient, ...],
    *,
    threshold: float,
    count: int,
    minimum_separation_nanoseconds: int,
) -> tuple[ReceptorTransient, ...]:
    selected: list[ReceptorTransient] = []
    for candidate in sorted(candidates, key=lambda item: item.score, reverse=True):
        if candidate.score <= threshold:
            continue
        if all(
            abs(candidate.organism_tick - item.organism_tick)
            >= minimum_separation_nanoseconds
            for item in selected
        ):
            selected.append(candidate)
        if len(selected) == count:
            break
    return tuple(sorted(selected, key=lambda item: item.organism_tick))


def audit_receptor_markers(
    sequences: tuple[ReceptorTimeSequence, ...],
    *,
    baseline_seconds: float,
    marker_delay_seconds: float,
    expected_marker_count: int,
    minimum_separation_seconds: float,
) -> ReceptorMarkerAudit:
    """Find independently strong reduced-state changes after a quiet baseline."""
    if len(sequences) != 2 or {item.modality_id for item in sequences} != {
        "auditory",
        "visual",
    }:
        raise ValueError("marker audit requires one auditory and one visual sequence")
    if baseline_seconds <= 0 or marker_delay_seconds < 0:
        raise ValueError("audit phase durations are invalid")
    if expected_marker_count <= 0 or minimum_separation_seconds <= 0:
        raise ValueError("marker selection parameters must be positive")
    clock_ids = {item.clock_id for item in sequences}
    if len(clock_ids) != 1:
        raise ValueError("marker audit requires one organism clock")

    origin = min(item.frames[0].field_time.window_start_tick for item in sequences)
    baseline_end = origin + int(baseline_seconds * 1_000_000_000)
    marker_start = baseline_end + int(marker_delay_seconds * 1_000_000_000)
    separation = int(minimum_separation_seconds * 1_000_000_000)
    thresholds = []
    responses = []
    by_modality: dict[str, tuple[ReceptorTransient, ...]] = {}
    for sequence in sorted(sequences, key=lambda item: item.modality_id):
        transients = _transients(sequence)
        baseline = tuple(item for item in transients if item.organism_tick <= baseline_end)
        if not baseline:
            raise ValueError(f"{sequence.modality_id} baseline has no transitions")
        threshold = max(item.score for item in baseline)
        selected = _separated_strongest(
            tuple(item for item in transients if item.organism_tick >= marker_start),
            threshold=threshold,
            count=expected_marker_count,
            minimum_separation_nanoseconds=separation,
        )
        thresholds.append((sequence.modality_id, threshold))
        responses.append((sequence.modality_id, selected))
        by_modality[sequence.modality_id] = selected

    auditory = by_modality["auditory"]
    visual = by_modality["visual"]
    complete = len(auditory) == len(visual) == expected_marker_count
    offsets = (
        tuple(
            visual_item.organism_tick - auditory_item.organism_tick
            for auditory_item, visual_item in zip(auditory, visual)
        )
        if complete
        else ()
    )
    return ReceptorMarkerAudit(
        clock_id=next(iter(clock_ids)),
        baseline_end_tick=baseline_end,
        marker_start_tick=marker_start,
        thresholds=tuple(thresholds),
        responses=tuple(responses),
        visual_minus_auditory_nanoseconds=offsets,
        complete_order_pairing=complete,
    )
