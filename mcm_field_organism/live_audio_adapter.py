"""Finite passive audio adapter boundary for Methodik 005.

Raw samples are consumed frame by frame and never appear in observations or
summaries. The optional hardware source requires an explicit device.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from typing import Callable, Iterable, Protocol

from .auditory_baselines import (
    AuditoryProbeConfig,
    auditory_receptor_frame,
    integrate_and_fire_step,
    threshold_events,
)
from .carrier_baselines import BaselineValidationError


class AudioCaptureError(RuntimeError):
    """Raised when a finite source cannot satisfy the capture contract."""


class AudioFrameSource(Protocol):
    overflow_count: int

    def read_frame(self) -> tuple[float, ...]: ...


@dataclass(frozen=True, slots=True)
class AuditoryObservation:
    frame_index: int
    timestamp_seconds: float
    energy: tuple[float, ...]
    events: tuple[int, ...]
    spike_counts: tuple[int, ...]
    membrane: tuple[float, ...]

    def canonical_payload(self) -> dict[str, object]:
        return {
            "frame_index": self.frame_index,
            "timestamp_seconds": self.timestamp_seconds,
            "energy": list(self.energy),
            "events": list(self.events),
            "spike_counts": list(self.spike_counts),
            "membrane": list(self.membrane),
        }


@dataclass(frozen=True, slots=True)
class AuditoryCaptureSummary:
    channel_ids: tuple[str, ...]
    frame_count: int
    duration_seconds: float
    energy_min: tuple[float, ...]
    energy_max: tuple[float, ...]
    energy_mean: tuple[float, ...]
    onset_counts: tuple[int, ...]
    offset_counts: tuple[int, ...]
    spike_counts: tuple[int, ...]
    overflow_count: int
    observation_digest: str


@dataclass(slots=True)
class SyntheticAudioFrameSource:
    """Deterministic S0 source used to prove the finite adapter contract."""

    frames: tuple[tuple[float, ...], ...]
    overflow_count: int = 0
    _cursor: int = 0

    def __init__(self, frames: Iterable[Iterable[float]]) -> None:
        self.frames = tuple(tuple(float(sample) for sample in frame) for frame in frames)
        self.overflow_count = 0
        self._cursor = 0

    @property
    def read_count(self) -> int:
        return self._cursor

    def read_frame(self) -> tuple[float, ...]:
        if self._cursor >= len(self.frames):
            raise AudioCaptureError("audio source ended before the finite capture completed")
        frame = self.frames[self._cursor]
        self._cursor += 1
        return frame


class SoundDeviceInputSource:
    """Optional S1 source; it never guesses or selects a default input device."""

    def __init__(self, *, device: int | str, config: AuditoryProbeConfig) -> None:
        if device is None or device == "":
            raise AudioCaptureError("an explicit input device is required")
        self.device = device
        self.config = config
        self.overflow_count = 0
        self._stream = None

    def __enter__(self) -> "SoundDeviceInputSource":
        try:
            import sounddevice  # type: ignore[import-not-found]
        except ImportError as exc:
            raise AudioCaptureError("optional dependency 'sounddevice' is not installed") from exc
        stream = None
        try:
            sounddevice.check_input_settings(
                device=self.device,
                channels=1,
                dtype="float32",
                samplerate=self.config.sample_rate,
            )
            stream = sounddevice.InputStream(
                device=self.device,
                channels=1,
                dtype="float32",
                samplerate=self.config.sample_rate,
                blocksize=self.config.frame_size,
            )
            stream.start()
            self._stream = stream
        except Exception as exc:
            self._stream = None
            if stream is not None:
                try:
                    stream.stop()
                except Exception:
                    pass
                try:
                    stream.close()
                except Exception:
                    pass
            raise AudioCaptureError(f"cannot open explicit input device {self.device!r}") from exc
        return self

    def read_frame(self) -> tuple[float, ...]:
        if self._stream is None:
            raise AudioCaptureError("input stream is not open")
        try:
            data, overflowed = self._stream.read(self.config.frame_size)
        except Exception as exc:
            raise AudioCaptureError("input stream read failed") from exc
        if overflowed:
            self.overflow_count += 1
        return tuple(float(row[0]) for row in data)

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        stream = self._stream
        self._stream = None
        if stream is not None:
            try:
                stream.stop()
            finally:
                stream.close()


Observer = Callable[[AuditoryObservation], object]


def _frame_count(duration_seconds: float, config: AuditoryProbeConfig, max_duration_seconds: float) -> int:
    duration_seconds = float(duration_seconds)
    max_duration_seconds = float(max_duration_seconds)
    if not math.isfinite(max_duration_seconds) or max_duration_seconds <= 0.0:
        raise AudioCaptureError("max_duration_seconds must be finite and greater than zero")
    if not math.isfinite(duration_seconds) or duration_seconds <= 0.0:
        raise AudioCaptureError("duration_seconds must be finite and greater than zero")
    if duration_seconds > max_duration_seconds:
        raise AudioCaptureError("requested capture exceeds the finite duration limit")
    exact_count = duration_seconds / config.dt
    rounded_count = round(exact_count)
    if rounded_count <= 0 or not math.isclose(exact_count, rounded_count, rel_tol=0.0, abs_tol=1e-10):
        raise AudioCaptureError("duration_seconds must contain a whole number of configured frames")
    return rounded_count


def capture_finite_audio(
    source: AudioFrameSource,
    config: AuditoryProbeConfig,
    *,
    duration_seconds: float,
    event_threshold: float = 0.5,
    spike_tau: float = 0.05,
    spike_threshold: float = 0.5,
    max_duration_seconds: float = 10.0,
    observer: Observer | None = None,
) -> AuditoryCaptureSummary:
    """Consume exactly one finite run and return aggregate technical state."""

    count = _frame_count(duration_seconds, config, max_duration_seconds)
    width = len(config.frequencies)
    previous_energy = (0.0,) * width
    membrane = (0.0,) * width
    minima = [math.inf] * width
    maxima = [-math.inf] * width
    totals = [0.0] * width
    onsets = [0] * width
    offsets = [0] * width
    spikes = [0] * width
    digest = hashlib.sha256()

    for frame_index in range(count):
        try:
            samples = source.read_frame()
            energy = auditory_receptor_frame(samples, config)
            events = threshold_events(previous_energy, energy, threshold=event_threshold)
            spike_frame = integrate_and_fire_step(
                membrane,
                energy,
                dt=config.dt,
                tau=spike_tau,
                threshold=spike_threshold,
            )
        except (BaselineValidationError, AudioCaptureError) as exc:
            raise AudioCaptureError(f"capture failed at frame {frame_index}") from exc

        observation = AuditoryObservation(
            frame_index=frame_index,
            timestamp_seconds=frame_index * config.dt,
            energy=energy,
            events=events,
            spike_counts=spike_frame.spikes,
            membrane=spike_frame.membrane,
        )
        encoded = json.dumps(
            observation.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        digest.update(encoded)
        if observer is not None:
            observer(observation)

        for index in range(width):
            minima[index] = min(minima[index], energy[index])
            maxima[index] = max(maxima[index], energy[index])
            totals[index] += energy[index]
            onsets[index] += 1 if events[index] > 0 else 0
            offsets[index] += 1 if events[index] < 0 else 0
            spikes[index] += spike_frame.spikes[index]
        previous_energy = energy
        membrane = spike_frame.membrane

    return AuditoryCaptureSummary(
        channel_ids=config.channel_ids,
        frame_count=count,
        duration_seconds=count * config.dt,
        energy_min=tuple(minima),
        energy_max=tuple(maxima),
        energy_mean=tuple(total / count for total in totals),
        onset_counts=tuple(onsets),
        offset_counts=tuple(offsets),
        spike_counts=tuple(spikes),
        overflow_count=int(getattr(source, "overflow_count", 0)),
        observation_digest=digest.hexdigest(),
    )


def public_result_roles() -> tuple[str, ...]:
    """Expose summary roles for privacy-boundary tests without an instance."""

    return tuple(item.name for item in fields(AuditoryCaptureSummary))
