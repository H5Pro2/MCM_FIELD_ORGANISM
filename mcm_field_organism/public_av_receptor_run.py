"""Bounded public AV receptor reduction without field attachment."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
from pathlib import Path

from .broadband_hearing_path import BroadbandHearingPath
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .public_av_container_source import (
    PUBLIC_MEDIA_CLOCK_ID,
    PUBLIC_MEDIA_TICKS_PER_SECOND,
    decode_audited_public_av_sources,
)
from .public_av_receptor_preflight import run_public_av_receptor_preflight
from .public_media_source_contract import PublicMediaSourceContract


class PublicAVReceptorRunError(ValueError):
    """Raised when a public AV receptor run would cross the field boundary."""


@dataclass(frozen=True, slots=True)
class PublicAVReducedFrame:
    modality_id: str
    geometry_id: str
    sequence_index: int
    window_start_tick: int
    window_end_tick: int
    receptor_state_digest: str

    def __post_init__(self) -> None:
        if self.modality_id not in {"auditory", "visual"}:
            raise PublicAVReceptorRunError("modality_id must be auditory or visual")
        if not isinstance(self.geometry_id, str) or not self.geometry_id:
            raise PublicAVReceptorRunError("geometry_id must be non-empty")
        if (
            isinstance(self.sequence_index, bool)
            or not isinstance(self.sequence_index, int)
            or self.sequence_index < 0
        ):
            raise PublicAVReceptorRunError("sequence_index must be non-negative")
        if (
            isinstance(self.window_start_tick, bool)
            or isinstance(self.window_end_tick, bool)
            or not isinstance(self.window_start_tick, int)
            or not isinstance(self.window_end_tick, int)
            or self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
        ):
            raise PublicAVReceptorRunError("frame ticks must advance")
        if not isinstance(self.receptor_state_digest, str) or not self.receptor_state_digest:
            raise PublicAVReceptorRunError("receptor_state_digest must be non-empty")


@dataclass(frozen=True, slots=True)
class PublicAVReceptorRun:
    source_id: str
    clock_id: str
    ticks_per_second: float
    source_start_tick: int
    source_end_tick: int
    duration_limit_ticks: int
    auditory_geometry_id: str
    visual_geometry_id: str
    auditory_frames: tuple[PublicAVReducedFrame, ...]
    visual_frames: tuple[PublicAVReducedFrame, ...]
    auditory_sequence_digest: str
    visual_sequence_digest: str
    repeated_auditory_sequence_digest: str
    repeated_visual_sequence_digest: str
    repeatable: bool
    raw_payload_retained: bool = False
    metadata_used_by_receptor: bool = False
    field_run_allowed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.source_id, str) or not self.source_id:
            raise PublicAVReceptorRunError("source_id must be non-empty")
        if self.clock_id != PUBLIC_MEDIA_CLOCK_ID:
            raise PublicAVReceptorRunError("unexpected clock_id")
        if float(self.ticks_per_second) != PUBLIC_MEDIA_TICKS_PER_SECOND:
            raise PublicAVReceptorRunError("unexpected tick rate")
        if (
            isinstance(self.source_start_tick, bool)
            or not isinstance(self.source_start_tick, int)
            or self.source_start_tick < 0
            or isinstance(self.source_end_tick, bool)
            or not isinstance(self.source_end_tick, int)
            or self.source_end_tick <= self.source_start_tick
        ):
            raise PublicAVReceptorRunError("absolute source interval is invalid")
        if (
            isinstance(self.duration_limit_ticks, bool)
            or not isinstance(self.duration_limit_ticks, int)
            or self.duration_limit_ticks < 1
        ):
            raise PublicAVReceptorRunError("duration_limit_ticks must be positive")
        auditory = tuple(self.auditory_frames)
        visual = tuple(self.visual_frames)
        if not auditory or not visual:
            raise PublicAVReceptorRunError("both modalities require reduced frames")
        if any(frame.modality_id != "auditory" for frame in auditory) or any(
            frame.modality_id != "visual" for frame in visual
        ):
            raise PublicAVReceptorRunError("frame modalities do not match their sequence")
        if (
            self.raw_payload_retained
            or self.metadata_used_by_receptor
            or self.field_run_allowed
        ):
            raise PublicAVReceptorRunError(
                "receptor run cannot retain payloads, metadata, or release fields"
            )
        if self.repeatable != (
            self.auditory_sequence_digest == self.repeated_auditory_sequence_digest
            and self.visual_sequence_digest == self.repeated_visual_sequence_digest
        ):
            raise PublicAVReceptorRunError("repeatability flag is inconsistent")
        object.__setattr__(self, "auditory_frames", auditory)
        object.__setattr__(self, "visual_frames", visual)


def _sequence_digest(frames: tuple[PublicAVReducedFrame, ...]) -> str:
    payload = [
        {
            "modality_id": frame.modality_id,
            "geometry_id": frame.geometry_id,
            "sequence_index": frame.sequence_index,
            "window_start_tick": frame.window_start_tick,
            "window_end_tick": frame.window_end_tick,
            "receptor_state_digest": frame.receptor_state_digest,
        }
        for frame in frames
    ]
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()


def _reduce_once(
    path: Path,
    contract: PublicMediaSourceContract,
    auditory_config: LogSpectralConfig,
    visual_config: VisualGridConfig,
    duration_seconds: float,
    start_tick: int,
) -> tuple[str, tuple[PublicAVReducedFrame, ...], tuple[PublicAVReducedFrame, ...]]:
    sources = decode_audited_public_av_sources(
        path,
        contract,
        duration_seconds=duration_seconds,
        start_tick=start_tick,
        audio_frame_samples=auditory_config.hop_size,
    )
    auditory_path = BroadbandHearingPath(LogSpectralReceptor(auditory_config))
    visual_receptor = LocalChannelGridReceptor(visual_config)
    auditory_frames = []
    window_ticks = round(auditory_config.window_seconds * 1_000_000_000)
    for _ in range(sources.audio.frame_count):
        samples, _, end_tick = sources.audio.read_timed_frame()
        state = auditory_path.push(samples)
        if state is None:
            continue
        auditory_frames.append(
            PublicAVReducedFrame(
                modality_id="auditory",
                geometry_id=state.geometry_id,
                sequence_index=state.snapshot_index,
                window_start_tick=end_tick - window_ticks,
                window_end_tick=end_tick,
                receptor_state_digest=state.digest(),
            )
        )
    visual_frames = []
    for index in range(sources.video.frame_count):
        frame, start_tick, end_tick = sources.video.read_timed_frame()
        state = visual_receptor.analyze(frame, frame_index=index)
        visual_frames.append(
            PublicAVReducedFrame(
                modality_id="visual",
                geometry_id=state.geometry_id,
                sequence_index=state.frame_index,
                window_start_tick=start_tick,
                window_end_tick=end_tick,
                receptor_state_digest=state.digest(),
            )
        )
    return sources.source_audit.source_id, tuple(auditory_frames), tuple(visual_frames)


def run_public_av_receptor_run(
    path: Path,
    contract: PublicMediaSourceContract,
    auditory_config: LogSpectralConfig,
    visual_config: VisualGridConfig,
    *,
    duration_seconds: float = 0.5,
    start_tick: int = 0,
) -> PublicAVReceptorRun:
    """Run one bounded receptor reduction; never build or advance a field."""

    preflight = run_public_av_receptor_preflight(
        path,
        contract,
        auditory_config,
        visual_config,
        duration_seconds=duration_seconds,
        start_tick=start_tick,
    )
    if not preflight.receptor_prerequisites_met:
        raise PublicAVReceptorRunError("public AV receptor prerequisites failed")
    source_id, auditory, visual = _reduce_once(
        path,
        contract,
        auditory_config,
        visual_config,
        duration_seconds,
        start_tick,
    )
    _, repeated_auditory, repeated_visual = _reduce_once(
        path,
        contract,
        auditory_config,
        visual_config,
        duration_seconds,
        start_tick,
    )
    auditory_digest = _sequence_digest(auditory)
    visual_digest = _sequence_digest(visual)
    repeated_auditory_digest = _sequence_digest(repeated_auditory)
    repeated_visual_digest = _sequence_digest(repeated_visual)
    return PublicAVReceptorRun(
        source_id=source_id,
        clock_id=PUBLIC_MEDIA_CLOCK_ID,
        ticks_per_second=PUBLIC_MEDIA_TICKS_PER_SECOND,
        source_start_tick=start_tick,
        source_end_tick=start_tick
        + round(float(duration_seconds) * 1_000_000_000),
        duration_limit_ticks=round(float(duration_seconds) * 1_000_000_000),
        auditory_geometry_id=auditory[0].geometry_id,
        visual_geometry_id=visual[0].geometry_id,
        auditory_frames=auditory,
        visual_frames=visual,
        auditory_sequence_digest=auditory_digest,
        visual_sequence_digest=visual_digest,
        repeated_auditory_sequence_digest=repeated_auditory_digest,
        repeated_visual_sequence_digest=repeated_visual_digest,
        repeatable=(
            auditory_digest == repeated_auditory_digest
            and visual_digest == repeated_visual_digest
        ),
    )


def public_av_receptor_event_timeline(
    result: PublicAVReceptorRun,
) -> tuple[list[dict[str, object]], str]:
    """Describe reduced receptor completions without constructing a field."""

    if not isinstance(result, PublicAVReceptorRun):
        raise PublicAVReceptorRunError("public AV receptor run result is required")
    ordered = sorted(
        (*result.auditory_frames, *result.visual_frames),
        key=lambda frame: (
            frame.window_end_tick,
            frame.modality_id,
            frame.sequence_index,
        ),
    )
    timeline = [
        {
            "sequence_index": index,
            "sensor_path": frame.modality_id,
            "elapsed_ticks": frame.window_end_tick,
        }
        for index, frame in enumerate(ordered)
    ]
    digest = hashlib.sha256(
        json.dumps(
            timeline,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()
    return timeline, digest


def public_av_receptor_run_json_value(result: PublicAVReceptorRun) -> dict:
    if not isinstance(result, PublicAVReceptorRun):
        raise PublicAVReceptorRunError("public AV receptor run result is required")

    def convert(value):
        if hasattr(value, "__dataclass_fields__"):
            return {
                role: convert(getattr(value, role))
                for role in value.__dataclass_fields__
            }
        if isinstance(value, tuple):
            return [convert(item) for item in value]
        return value

    return convert(result)


def public_av_receptor_run_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (PublicAVReducedFrame, PublicAVReceptorRun)
        for item in fields(cls)
    )
