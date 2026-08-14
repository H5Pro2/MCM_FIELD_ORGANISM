"""Organism-clock audit for reduced receptor states without forced pairing."""

from __future__ import annotations

from dataclasses import dataclass, fields
import time

from .broadband_hearing_path import BroadbandHearingPath
from .finite_video_path import LocalChannelGridReceptor, VideoFrameSource
from .controlled_audio_source import AudioFrameSource
from .controlled_receptor_capture import (
    Clock,
    capture_timed_audio_video_receptor_sequences,
)
from .receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeAlignmentError,
    ReceptorTimeSequence,
)


@dataclass(frozen=True, slots=True)
class ReceptorTimeOverlap:
    """One measured interval intersection, not a selected field pair."""

    first_snapshot_id: str
    second_snapshot_id: str
    window_start_tick: int
    window_end_tick: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.first_snapshot_id, str)
            or not self.first_snapshot_id
            or not isinstance(self.second_snapshot_id, str)
            or not self.second_snapshot_id
        ):
            raise ReceptorTimeAlignmentError(
                "time overlap requires two snapshot identities"
            )
        if (
            isinstance(self.window_start_tick, bool)
            or isinstance(self.window_end_tick, bool)
            or not isinstance(self.window_start_tick, int)
            or not isinstance(self.window_end_tick, int)
            or self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
        ):
            raise ReceptorTimeAlignmentError(
                "time overlap must contain a positive interval"
            )


@dataclass(frozen=True, slots=True)
class ReceptorTimeAlignmentAudit:
    """Complete pairwise overlap audit without interpolation or selection."""

    clock_id: str
    modality_ids: tuple[str, str]
    frame_counts: tuple[int, int]
    overlaps: tuple[ReceptorTimeOverlap, ...]
    unambiguous_overlaps: tuple[ReceptorTimeOverlap, ...]
    ambiguous_snapshot_ids: tuple[str, ...]
    unmatched_snapshot_ids: tuple[str, ...]

    @property
    def has_complete_one_to_one_alignment(self) -> bool:
        return (
            not self.ambiguous_snapshot_ids
            and not self.unmatched_snapshot_ids
            and len(self.unambiguous_overlaps) == min(self.frame_counts)
            and self.frame_counts[0] == self.frame_counts[1]
        )


@dataclass(frozen=True, slots=True)
class CapturedReceptorTimeAudit:
    """Two reduced time sequences and their selection-free audit."""

    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    audit: ReceptorTimeAlignmentAudit

    def __post_init__(self) -> None:
        sequences = tuple(self.sequences)
        if len(sequences) != 2:
            raise ReceptorTimeAlignmentError(
                "captured time audit requires exactly two receptor sequences"
            )
        if tuple(item.modality_id for item in sequences) != self.audit.modality_ids:
            raise ReceptorTimeAlignmentError(
                "captured sequences must match the audited modalities"
            )
        object.__setattr__(self, "sequences", sequences)


def audit_receptor_time_alignment(
    first: ReceptorTimeSequence,
    second: ReceptorTimeSequence,
) -> ReceptorTimeAlignmentAudit:
    """Report every real overlap and reject hidden post-capture pairing."""

    if not isinstance(first, ReceptorTimeSequence) or not isinstance(
        second, ReceptorTimeSequence
    ):
        raise ReceptorTimeAlignmentError(
            "alignment audit requires two receptor time sequences"
        )
    if first.modality_id == second.modality_id:
        raise ReceptorTimeAlignmentError(
            "alignment audit requires two different modalities"
        )
    if first.clock_id != second.clock_id:
        raise ReceptorTimeAlignmentError(
            "alignment audit requires one organism clock"
        )
    ordered = tuple(
        sorted((first, second), key=lambda item: item.modality_id)
    )
    left, right = ordered
    overlaps = []
    degree: dict[str, int] = {
        item.frame.snapshot_id: 0
        for sequence in ordered
        for item in sequence.frames
    }
    for left_item in left.frames:
        for right_item in right.frames:
            start = max(
                left_item.field_time.window_start_tick,
                right_item.field_time.window_start_tick,
            )
            end = min(
                left_item.field_time.window_end_tick,
                right_item.field_time.window_end_tick,
            )
            if start >= end:
                continue
            overlap = ReceptorTimeOverlap(
                first_snapshot_id=left_item.frame.snapshot_id,
                second_snapshot_id=right_item.frame.snapshot_id,
                window_start_tick=start,
                window_end_tick=end,
            )
            overlaps.append(overlap)
            degree[overlap.first_snapshot_id] += 1
            degree[overlap.second_snapshot_id] += 1

    unambiguous = tuple(
        item
        for item in overlaps
        if degree[item.first_snapshot_id] == 1
        and degree[item.second_snapshot_id] == 1
    )
    ambiguous = {
        snapshot_id
        for item in overlaps
        if degree[item.first_snapshot_id] > 1
        or degree[item.second_snapshot_id] > 1
        for snapshot_id in (
            item.first_snapshot_id,
            item.second_snapshot_id,
        )
    }
    return ReceptorTimeAlignmentAudit(
        clock_id=left.clock_id,
        modality_ids=(left.modality_id, right.modality_id),
        frame_counts=(len(left.frames), len(right.frames)),
        overlaps=tuple(overlaps),
        unambiguous_overlaps=unambiguous,
        ambiguous_snapshot_ids=tuple(sorted(ambiguous)),
        unmatched_snapshot_ids=tuple(
            sorted(snapshot_id for snapshot_id, count in degree.items() if count == 0)
        ),
    )


def capture_timed_audio_video_receptors(
    audio_source: AudioFrameSource,
    video_source: VideoFrameSource,
    auditory_path: BroadbandHearingPath,
    visual_receptor: LocalChannelGridReceptor,
    *,
    nominal_duration_seconds: float,
    clock: Clock = time.monotonic_ns,
    clock_id: str = "organism.monotonic_ns",
) -> CapturedReceptorTimeAudit:
    """Audit the neutral concurrent receptor sequences without pairing them."""

    sequences = capture_timed_audio_video_receptor_sequences(
        audio_source,
        video_source,
        auditory_path,
        visual_receptor,
        nominal_duration_seconds=nominal_duration_seconds,
        clock=clock,
        clock_id=clock_id,
    )
    audit = audit_receptor_time_alignment(sequences[0], sequences[1])
    return CapturedReceptorTimeAudit(sequences, audit)


def receptor_time_alignment_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            OrganismTimedReceptorFrame,
            ReceptorTimeSequence,
            ReceptorTimeOverlap,
            ReceptorTimeAlignmentAudit,
            CapturedReceptorTimeAudit,
        )
        for item in fields(cls)
    )
