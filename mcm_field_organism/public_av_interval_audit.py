"""Observer-side interval audit for audited public AV raw sources."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path

import numpy as np

from .public_av_container_source import (
    PUBLIC_MEDIA_CLOCK_ID,
    PUBLIC_MEDIA_TICKS_PER_SECOND,
    PublicAVContainerSourceError,
    decode_audited_public_av_sources,
)
from .public_media_source_contract import PublicMediaSourceContract


class PublicAVIntervalAuditError(ValueError):
    """Raised when an AV interval audit cannot remain observer-side."""


@dataclass(frozen=True, slots=True)
class PublicAVModalityIntervalAudit:
    modality_id: str
    frame_count: int
    first_start_tick: int
    last_end_tick: int
    monotonic: bool
    non_overlapping: bool
    gap_count: int
    max_gap_ticks: int
    bounded_to_limit: bool
    interval_digest: str

    def __post_init__(self) -> None:
        if self.modality_id not in {"auditory", "visual"}:
            raise PublicAVIntervalAuditError("modality_id must be auditory or visual")
        for role in (
            "frame_count",
            "first_start_tick",
            "last_end_tick",
            "gap_count",
            "max_gap_ticks",
        ):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise PublicAVIntervalAuditError(f"{role} must be non-negative integer")
        if self.frame_count < 1:
            raise PublicAVIntervalAuditError("frame_count must be positive")
        if (
            isinstance(self.first_start_tick, bool)
            or isinstance(self.last_end_tick, bool)
            or not isinstance(self.first_start_tick, int)
            or not isinstance(self.last_end_tick, int)
            or self.first_start_tick < 0
            or self.last_end_tick <= self.first_start_tick
        ):
            raise PublicAVIntervalAuditError("interval bounds must advance")
        for role in ("monotonic", "non_overlapping", "bounded_to_limit"):
            if not isinstance(getattr(self, role), bool):
                raise PublicAVIntervalAuditError(f"{role} must be boolean")
        if not isinstance(self.interval_digest, str) or not self.interval_digest:
            raise PublicAVIntervalAuditError("interval_digest must be non-empty")


@dataclass(frozen=True, slots=True)
class PublicAVCommonIntervalAudit:
    clock_id: str
    ticks_per_second: float
    source_start_tick: int
    source_end_tick: int
    duration_limit_ticks: int
    audio: PublicAVModalityIntervalAudit
    video: PublicAVModalityIntervalAudit
    shared_clock: bool
    common_axis_overlap_ticks: int
    repeated_audio_interval_digest: str
    repeated_video_interval_digest: str
    repeatable: bool
    accepted_for_receptor_run: bool = False
    field_run_allowed: bool = False
    metadata_used_by_receptor: bool = False
    raw_payload_retained: bool = False

    def __post_init__(self) -> None:
        if self.clock_id != PUBLIC_MEDIA_CLOCK_ID:
            raise PublicAVIntervalAuditError("unexpected public media clock")
        if float(self.ticks_per_second) != PUBLIC_MEDIA_TICKS_PER_SECOND:
            raise PublicAVIntervalAuditError("unexpected public media tick rate")
        if (
            isinstance(self.source_start_tick, bool)
            or not isinstance(self.source_start_tick, int)
            or self.source_start_tick < 0
            or isinstance(self.source_end_tick, bool)
            or not isinstance(self.source_end_tick, int)
            or self.source_end_tick <= self.source_start_tick
            or self.source_end_tick - self.source_start_tick
            != self.duration_limit_ticks
        ):
            raise PublicAVIntervalAuditError("absolute source interval is invalid")
        if (
            isinstance(self.duration_limit_ticks, bool)
            or not isinstance(self.duration_limit_ticks, int)
            or self.duration_limit_ticks < 1
        ):
            raise PublicAVIntervalAuditError("duration_limit_ticks must be positive")
        if not isinstance(self.audio, PublicAVModalityIntervalAudit) or not isinstance(
            self.video,
            PublicAVModalityIntervalAudit,
        ):
            raise PublicAVIntervalAuditError("audio and video interval audits are required")
        for role in (
            "shared_clock",
            "repeatable",
            "accepted_for_receptor_run",
            "field_run_allowed",
            "metadata_used_by_receptor",
            "raw_payload_retained",
        ):
            if not isinstance(getattr(self, role), bool):
                raise PublicAVIntervalAuditError(f"{role} must be boolean")
        if (
            isinstance(self.common_axis_overlap_ticks, bool)
            or not isinstance(self.common_axis_overlap_ticks, int)
            or self.common_axis_overlap_ticks < 0
        ):
            raise PublicAVIntervalAuditError(
                "common_axis_overlap_ticks must be non-negative"
            )
        if (
            not self.shared_clock
            or self.accepted_for_receptor_run
            or self.field_run_allowed
            or self.metadata_used_by_receptor
            or self.raw_payload_retained
        ):
            raise PublicAVIntervalAuditError(
                "interval audit cannot release receptors, fields, or metadata"
            )


def _json_value(value):
    if hasattr(value, "__dataclass_fields__"):
        return {
            role: _json_value(getattr(value, role))
            for role in value.__dataclass_fields__
        }
    return value


def public_av_interval_audit_json_value(
    result: PublicAVCommonIntervalAudit,
) -> dict:
    if not isinstance(result, PublicAVCommonIntervalAudit):
        raise PublicAVIntervalAuditError("public AV interval audit is required")
    return _json_value(result)


def _interval_digest(records: list[dict[str, object]]) -> str:
    return hashlib.sha256(
        json.dumps(
            records,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()


def _audit_records(
    modality_id: str,
    records: list[dict[str, object]],
    *,
    duration_limit_ticks: int,
) -> PublicAVModalityIntervalAudit:
    if not records:
        raise PublicAVIntervalAuditError("interval records cannot be empty")
    starts = [int(item["start_tick"]) for item in records]
    ends = [int(item["end_tick"]) for item in records]
    monotonic = all(
        later_start > earlier_start
        for earlier_start, later_start in zip(starts, starts[1:])
    )
    non_overlapping = all(
        later_start >= earlier_end
        for earlier_end, later_start in zip(ends, starts[1:])
    )
    gaps = [
        later_start - earlier_end
        for earlier_end, later_start in zip(ends, starts[1:])
        if later_start > earlier_end
    ]
    return PublicAVModalityIntervalAudit(
        modality_id=modality_id,
        frame_count=len(records),
        first_start_tick=starts[0],
        last_end_tick=ends[-1],
        monotonic=monotonic,
        non_overlapping=non_overlapping,
        gap_count=len(gaps),
        max_gap_ticks=max(gaps, default=0),
        bounded_to_limit=(starts[0] >= 0 and ends[-1] <= duration_limit_ticks),
        interval_digest=_interval_digest(records),
    )


def _collect_records(
    path: Path,
    contract: PublicMediaSourceContract,
    duration_seconds: float,
    start_tick: int,
):
    sources = decode_audited_public_av_sources(
        path,
        contract,
        duration_seconds=duration_seconds,
        start_tick=start_tick,
    )
    audio_records: list[dict[str, object]] = []
    for _ in range(sources.audio.frame_count):
        samples, start, end = sources.audio.read_timed_frame()
        audio_records.append(
            {
                "start_tick": start,
                "end_tick": end,
                "sample_count": len(samples),
            }
        )
    video_records: list[dict[str, object]] = []
    for _ in range(sources.video.frame_count):
        frame, start, end = sources.video.read_timed_frame()
        if not isinstance(frame, np.ndarray):
            raise PublicAVContainerSourceError("video source yielded non-array frame")
        video_records.append(
            {
                "start_tick": start,
                "end_tick": end,
                "shape": tuple(int(value) for value in frame.shape),
                "dtype": str(frame.dtype),
            }
        )
    return sources, audio_records, video_records


def run_public_av_interval_audit(
    path: Path,
    contract: PublicMediaSourceContract,
    *,
    duration_seconds: float,
    start_tick: int = 0,
) -> PublicAVCommonIntervalAudit:
    """Audit raw-source intervals only; do not feed receptors or fields."""

    duration_limit_ticks = round(float(duration_seconds) * 1_000_000_000)
    if duration_limit_ticks <= 0:
        raise PublicAVIntervalAuditError("duration_seconds must be positive")
    first_sources, first_audio_records, first_video_records = _collect_records(
        path,
        contract,
        duration_seconds,
        start_tick,
    )
    second_sources, second_audio_records, second_video_records = _collect_records(
        path,
        contract,
        duration_seconds,
        start_tick,
    )
    audio = _audit_records(
        "auditory",
        first_audio_records,
        duration_limit_ticks=duration_limit_ticks,
    )
    video = _audit_records(
        "visual",
        first_video_records,
        duration_limit_ticks=duration_limit_ticks,
    )
    repeated_audio_digest = _interval_digest(second_audio_records)
    repeated_video_digest = _interval_digest(second_video_records)
    overlap_start = max(audio.first_start_tick, video.first_start_tick)
    overlap_end = min(audio.last_end_tick, video.last_end_tick)
    return PublicAVCommonIntervalAudit(
        clock_id=first_sources.clock_id,
        ticks_per_second=PUBLIC_MEDIA_TICKS_PER_SECOND,
        source_start_tick=first_sources.source_start_tick,
        source_end_tick=first_sources.source_end_tick,
        duration_limit_ticks=duration_limit_ticks,
        audio=audio,
        video=video,
        shared_clock=(
            first_sources.clock_id == second_sources.clock_id == PUBLIC_MEDIA_CLOCK_ID
        ),
        common_axis_overlap_ticks=max(0, overlap_end - overlap_start),
        repeated_audio_interval_digest=repeated_audio_digest,
        repeated_video_interval_digest=repeated_video_digest,
        repeatable=(
            audio.interval_digest == repeated_audio_digest
            and video.interval_digest == repeated_video_digest
        ),
    )


def public_av_interval_audit_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVModalityIntervalAudit, PublicAVCommonIntervalAudit)
        for item in fields(cls)
    )
