"""Audit source-window meaning against measured organism read intervals."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
import statistics

from .receptor_time_alignment import ReceptorTimeSequence


class ReceptorTemporalSupportError(ValueError):
    """Raised when a receptor sequence has inconsistent source-window timing."""


@dataclass(frozen=True, slots=True)
class ReceptorTemporalSupportAudit:
    modality_id: str
    source_clock_id: str
    source_window_role: str
    source_window_width_ticks: int
    source_stride_ticks: int
    source_window_seconds: float | None
    nominal_output_period_seconds: float
    source_overlap_fraction: float | None
    organism_clock_id: str
    organism_read_minimum_seconds: float
    organism_read_median_seconds: float
    organism_read_maximum_seconds: float
    organism_support_is_mapped: bool
    organism_read_interval_is_world_support: bool


def _source_geometry(sequence: ReceptorTimeSequence) -> tuple[int, int]:
    widths = {
        item.frame.window_end_tick - item.frame.window_start_tick
        for item in sequence.frames
    }
    if len(widths) != 1:
        raise ReceptorTemporalSupportError(
            "receptor source windows must have one stable width"
        )
    starts = [item.frame.window_start_tick for item in sequence.frames]
    strides = {
        later - earlier for earlier, later in zip(starts, starts[1:])
    }
    if not strides:
        raise ReceptorTemporalSupportError(
            "temporal support audit requires at least two receptor states"
        )
    if len(strides) != 1 or next(iter(strides)) <= 0:
        raise ReceptorTemporalSupportError(
            "receptor source windows must advance by one stable positive stride"
        )
    return next(iter(widths)), next(iter(strides))


def _read_durations_seconds(
    sequence: ReceptorTimeSequence,
    organism_ticks_per_second: float,
) -> tuple[float, float, float]:
    rate = float(organism_ticks_per_second)
    if not math.isfinite(rate) or rate <= 0.0:
        raise ReceptorTemporalSupportError(
            "organism_ticks_per_second must be finite and positive"
        )
    durations = tuple(
        (
            item.field_time.window_end_tick
            - item.field_time.window_start_tick
        )
        / rate
        for item in sequence.frames
    )
    return min(durations), float(statistics.median(durations)), max(durations)


def audit_auditory_temporal_support(
    sequence: ReceptorTimeSequence,
    *,
    sample_rate: int,
    organism_ticks_per_second: float = 1_000_000_000.0,
) -> ReceptorTemporalSupportAudit:
    """Describe rolling audio support without mapping it onto organism time."""

    if sequence.modality_id != "auditory" or any(
        item.frame.clock_id != "audio.sample" for item in sequence.frames
    ):
        raise ReceptorTemporalSupportError(
            "auditory support audit requires audio.sample receptor states"
        )
    if isinstance(sample_rate, bool) or not isinstance(sample_rate, int) or sample_rate <= 0:
        raise ReceptorTemporalSupportError("sample_rate must be a positive integer")
    width, stride = _source_geometry(sequence)
    read_minimum, read_median, read_maximum = _read_durations_seconds(
        sequence,
        organism_ticks_per_second,
    )
    return ReceptorTemporalSupportAudit(
        modality_id="auditory",
        source_clock_id="audio.sample",
        source_window_role="rolling_analysis_window",
        source_window_width_ticks=width,
        source_stride_ticks=stride,
        source_window_seconds=width / sample_rate,
        nominal_output_period_seconds=stride / sample_rate,
        source_overlap_fraction=1.0 - (stride / width),
        organism_clock_id=sequence.clock_id,
        organism_read_minimum_seconds=read_minimum,
        organism_read_median_seconds=read_median,
        organism_read_maximum_seconds=read_maximum,
        organism_support_is_mapped=False,
        organism_read_interval_is_world_support=False,
    )


def audit_visual_temporal_support(
    sequence: ReceptorTimeSequence,
    *,
    nominal_frames_per_second: float,
    organism_ticks_per_second: float = 1_000_000_000.0,
) -> ReceptorTemporalSupportAudit:
    """Describe frame identity timing without claiming exposure duration."""

    if sequence.modality_id != "visual" or any(
        item.frame.clock_id != "video.frame" for item in sequence.frames
    ):
        raise ReceptorTemporalSupportError(
            "visual support audit requires video.frame receptor states"
        )
    rate = float(nominal_frames_per_second)
    if not math.isfinite(rate) or rate <= 0.0:
        raise ReceptorTemporalSupportError(
            "nominal_frames_per_second must be finite and positive"
        )
    width, stride = _source_geometry(sequence)
    if width != 1 or stride != 1:
        raise ReceptorTemporalSupportError(
            "visual frame identity windows must advance one frame at a time"
        )
    read_minimum, read_median, read_maximum = _read_durations_seconds(
        sequence,
        organism_ticks_per_second,
    )
    return ReceptorTemporalSupportAudit(
        modality_id="visual",
        source_clock_id="video.frame",
        source_window_role="frame_identity_interval",
        source_window_width_ticks=width,
        source_stride_ticks=stride,
        source_window_seconds=None,
        nominal_output_period_seconds=1.0 / rate,
        source_overlap_fraction=None,
        organism_clock_id=sequence.clock_id,
        organism_read_minimum_seconds=read_minimum,
        organism_read_median_seconds=read_median,
        organism_read_maximum_seconds=read_maximum,
        organism_support_is_mapped=False,
        organism_read_interval_is_world_support=False,
    )


def receptor_temporal_support_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(ReceptorTemporalSupportAudit))
