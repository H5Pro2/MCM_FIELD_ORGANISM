"""Audited public AV container to neutral timed raw-source adapter."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import math

import numpy as np

from .controlled_audio_source import AudioCaptureError
from .finite_video_path import VisualCaptureError
from .public_media_source_contract import (
    PublicMediaSourceAudit,
    PublicMediaSourceContract,
    audit_public_media_source,
)


PUBLIC_MEDIA_CLOCK_ID = "public.media.pts_ns"
PUBLIC_MEDIA_TICKS_PER_SECOND = 1_000_000_000.0


class PublicAVContainerSourceError(RuntimeError):
    """Raised when an audited container cannot provide neutral raw sources."""


class TimedPublicAudioSource:
    overflow_count = 0
    capture_clock_id = PUBLIC_MEDIA_CLOCK_ID
    capture_ticks_per_second = PUBLIC_MEDIA_TICKS_PER_SECOND

    def __init__(self, frames: list[tuple[tuple[float, ...], int, int]]) -> None:
        self._frames = tuple(frames)
        self._cursor = 0

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    def read_frame(self) -> tuple[float, ...]:
        samples, _, _ = self.read_timed_frame()
        return samples

    def read_timed_frame(self) -> tuple[tuple[float, ...], int, int]:
        if self._cursor >= len(self._frames):
            raise AudioCaptureError("public audio source ended")
        item = self._frames[self._cursor]
        self._cursor += 1
        return item


class TimedPublicVideoSource:
    capture_clock_id = PUBLIC_MEDIA_CLOCK_ID
    capture_ticks_per_second = PUBLIC_MEDIA_TICKS_PER_SECOND

    def __init__(self, frames: list[tuple[np.ndarray, int, int]]) -> None:
        stored = []
        for frame, start, end in frames:
            immutable = np.array(frame, copy=True)
            immutable.setflags(write=False)
            stored.append((immutable, start, end))
        self._frames = tuple(stored)
        self._cursor = 0

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    def read_frame(self) -> np.ndarray:
        frame, _, _ = self.read_timed_frame()
        return frame

    def read_timed_frame(self) -> tuple[np.ndarray, int, int]:
        if self._cursor >= len(self._frames):
            raise VisualCaptureError("public video source ended")
        item = self._frames[self._cursor]
        self._cursor += 1
        return item


@dataclass(frozen=True, slots=True)
class PublicAVRawSources:
    source_audit: PublicMediaSourceAudit
    clock_id: str
    source_start_tick: int
    source_end_tick: int
    sample_rate: int
    audio_frame_samples: int
    audio: TimedPublicAudioSource
    video: TimedPublicVideoSource


def _nanoseconds(pts: int, time_base: Fraction) -> int:
    return round(Fraction(pts) * time_base * 1_000_000_000)


def decode_audited_public_av_sources(
    path: Path,
    contract: PublicMediaSourceContract,
    *,
    duration_seconds: float,
    start_tick: int = 0,
    audio_frame_samples: int = 480,
) -> PublicAVRawSources:
    """Decode a bounded interval after integrity audit; ignore all metadata streams."""

    duration = float(duration_seconds)
    if not math.isfinite(duration) or duration <= 0.0 or duration > 10.0:
        raise PublicAVContainerSourceError(
            "duration_seconds must be finite and within 10 seconds"
        )
    if (
        isinstance(start_tick, bool)
        or not isinstance(start_tick, int)
        or start_tick < 0
    ):
        raise PublicAVContainerSourceError("start_tick must be a non-negative integer")
    if (
        isinstance(audio_frame_samples, bool)
        or not isinstance(audio_frame_samples, int)
        or audio_frame_samples <= 0
    ):
        raise PublicAVContainerSourceError("audio_frame_samples must be positive")
    audit = audit_public_media_source(path, contract)
    if not audit.accepted:
        raise PublicAVContainerSourceError("public source integrity audit failed")

    try:
        import av
    except ImportError as exc:
        raise PublicAVContainerSourceError("optional dependency 'av' is unavailable") from exc

    duration_ns = round(duration * 1_000_000_000)
    end_tick = start_tick + duration_ns
    audio_values: list[float] = []
    audio_origin_ns: int | None = None
    video_frames: list[tuple[np.ndarray, int, int]] = []
    with av.open(str(path), mode="r") as container:
        if not container.streams.audio or not container.streams.video:
            raise PublicAVContainerSourceError(
                "container must provide at least one audio and one video stream"
            )
        audio_stream = container.streams.audio[0]
        video_stream = container.streams.video[0]
        sample_rate = int(audio_stream.codec_context.sample_rate)
        if sample_rate <= 0:
            raise PublicAVContainerSourceError("audio sample rate is unavailable")

        for frame in container.decode(audio=0, video=0):
            if frame.pts is None or frame.time_base is None:
                raise PublicAVContainerSourceError("decoded frame lacks source time")
            start_ns = _nanoseconds(frame.pts, frame.time_base)
            if start_ns >= end_tick:
                continue
            if isinstance(frame, av.audio.frame.AudioFrame):
                values = frame.to_ndarray().astype(np.float64, copy=False)
                mono = values.mean(axis=0) if values.ndim == 2 else values
                if audio_origin_ns is None:
                    audio_origin_ns = start_ns
                audio_values.extend(float(value) for value in mono)
            elif isinstance(frame, av.video.frame.VideoFrame):
                duration_ticks = frame.duration or 1
                absolute_end_ns = _nanoseconds(
                    frame.pts + duration_ticks, frame.time_base
                )
                if absolute_end_ns > start_tick and start_ns < end_tick:
                    video_frames.append(
                        (
                            frame.to_ndarray(format="bgr24"),
                            max(start_ns, start_tick) - start_tick,
                            min(absolute_end_ns, end_tick) - start_tick,
                        )
                    )

    if audio_origin_ns is None or not audio_values or not video_frames:
        raise PublicAVContainerSourceError("bounded decode produced incomplete AV sources")
    audio_frames = []
    for offset in range(0, len(audio_values) - audio_frame_samples + 1, audio_frame_samples):
        absolute_start_ns = audio_origin_ns + round(
            offset * 1_000_000_000 / sample_rate
        )
        absolute_end_ns = audio_origin_ns + round(
            (offset + audio_frame_samples) * 1_000_000_000 / sample_rate
        )
        if absolute_end_ns > end_tick:
            break
        if absolute_start_ns < start_tick:
            continue
        audio_frames.append(
            (
                tuple(audio_values[offset : offset + audio_frame_samples]),
                absolute_start_ns - start_tick,
                absolute_end_ns - start_tick,
            )
        )
    if not audio_frames:
        raise PublicAVContainerSourceError("bounded decode produced no complete audio frame")
    return PublicAVRawSources(
        source_audit=audit,
        clock_id=PUBLIC_MEDIA_CLOCK_ID,
        source_start_tick=start_tick,
        source_end_tick=end_tick,
        sample_rate=sample_rate,
        audio_frame_samples=audio_frame_samples,
        audio=TimedPublicAudioSource(audio_frames),
        video=TimedPublicVideoSource(video_frames),
    )
