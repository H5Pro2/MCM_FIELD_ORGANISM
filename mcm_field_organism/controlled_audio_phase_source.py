"""Deterministic external sound-mute-sound source for finite field probes."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Iterable

from .auditory_baselines import AuditoryProbeConfig
from .controlled_audio_source import AudioCaptureError, AudioFrameSource


_PHASE_ID = re.compile(r"^[a-z][a-z0-9_.-]*$")


@dataclass(frozen=True, slots=True)
class AudioGainPhase:
    phase_id: str
    duration_seconds: float
    gain: float

    def __post_init__(self) -> None:
        if not isinstance(self.phase_id, str) or not _PHASE_ID.fullmatch(self.phase_id):
            raise AudioCaptureError("phase_id must be a lowercase technical identifier")
        duration = float(self.duration_seconds)
        gain = float(self.gain)
        if not math.isfinite(duration) or duration <= 0.0:
            raise AudioCaptureError("phase duration must be finite and greater than zero")
        if not math.isfinite(gain) or gain < 0.0 or gain > 1.0:
            raise AudioCaptureError("phase gain must stay within 0..1")
        object.__setattr__(self, "duration_seconds", duration)
        object.__setattr__(self, "gain", gain)


class ControlledAudioPhaseSource:
    """Generate phase-local signal chunks without retaining generated audio."""

    __slots__ = (
        "config",
        "phases",
        "frequencies",
        "component_amplitude",
        "_phase_frame_counts",
        "_cursor",
    )

    def __init__(
        self,
        *,
        config: AuditoryProbeConfig,
        phases: Iterable[AudioGainPhase],
        frequencies: Iterable[float] = (250.0, 1000.0, 4000.0),
        component_amplitude: float = 0.2,
    ) -> None:
        phase_set = tuple(phases)
        if not phase_set:
            raise AudioCaptureError("controlled source requires at least one phase")
        if len({phase.phase_id for phase in phase_set}) != len(phase_set):
            raise AudioCaptureError("phase identifiers must be unique")

        try:
            frequency_set = tuple(float(value) for value in frequencies)
        except (TypeError, ValueError) as exc:
            raise AudioCaptureError("frequencies must contain numeric values") from exc
        if not frequency_set or any(not math.isfinite(value) for value in frequency_set):
            raise AudioCaptureError("frequencies must be finite and non-empty")
        if any(value <= 0.0 or value >= config.sample_rate / 2.0 for value in frequency_set):
            raise AudioCaptureError("frequencies must lie between zero and Nyquist")
        if len(set(frequency_set)) != len(frequency_set):
            raise AudioCaptureError("frequencies must be unique")

        amplitude = float(component_amplitude)
        if not math.isfinite(amplitude) or amplitude <= 0.0:
            raise AudioCaptureError("component_amplitude must be finite and greater than zero")
        if amplitude * len(frequency_set) > 1.0:
            raise AudioCaptureError("summed component amplitudes must not exceed one")

        frame_counts = []
        for phase in phase_set:
            exact_count = phase.duration_seconds / config.dt
            rounded_count = round(exact_count)
            if rounded_count <= 0 or not math.isclose(exact_count, rounded_count, abs_tol=1e-9):
                raise AudioCaptureError("each phase duration must contain whole audio chunks")
            frame_counts.append(rounded_count)

        self.config = config
        self.phases = phase_set
        self.frequencies = frequency_set
        self.component_amplitude = amplitude
        self._phase_frame_counts = tuple(frame_counts)
        self._cursor = 0

    @property
    def phase_frame_counts(self) -> tuple[int, ...]:
        return self._phase_frame_counts

    @property
    def total_frames(self) -> int:
        return sum(self._phase_frame_counts)

    @property
    def frames_read(self) -> int:
        return self._cursor

    def reset(self) -> None:
        self._cursor = 0

    def phase_for_frame(self, frame_index: int) -> tuple[int, int]:
        if isinstance(frame_index, bool) or not isinstance(frame_index, int):
            raise AudioCaptureError("frame_index must be an integer")
        if frame_index < 0 or frame_index >= self.total_frames:
            raise AudioCaptureError("frame_index lies outside the controlled phase schedule")
        remaining = frame_index
        for phase_index, count in enumerate(self._phase_frame_counts):
            if remaining < count:
                return phase_index, remaining
            remaining -= count
        raise AudioCaptureError("cannot resolve controlled phase frame")

    def read_frame(self) -> tuple[float, ...]:
        if self._cursor >= self.total_frames:
            raise AudioCaptureError("controlled phase source is exhausted")
        phase_index, local_frame_index = self.phase_for_frame(self._cursor)
        phase = self.phases[phase_index]
        self._cursor += 1
        if phase.gain == 0.0:
            return (0.0,) * self.config.frame_size

        start_sample = local_frame_index * self.config.frame_size
        scale = phase.gain * self.component_amplitude
        return tuple(
            scale
            * sum(
                math.sin(
                    2.0
                    * math.pi
                    * frequency
                    * (start_sample + offset)
                    / self.config.sample_rate
                )
                for frequency in self.frequencies
            )
            for offset in range(self.config.frame_size)
        )


class ControlledAudioGateSource:
    """Drain a live source continuously while applying an external binary gate."""

    __slots__ = (
        "source",
        "config",
        "phases",
        "_phase_frame_counts",
        "_cursor",
    )

    def __init__(
        self,
        *,
        source: AudioFrameSource,
        config: AuditoryProbeConfig,
        phases: Iterable[AudioGainPhase],
    ) -> None:
        phase_set = tuple(phases)
        if not phase_set:
            raise AudioCaptureError("controlled gate requires at least one phase")
        if len({phase.phase_id for phase in phase_set}) != len(phase_set):
            raise AudioCaptureError("gate phase identifiers must be unique")
        if any(phase.gain not in {0.0, 1.0} for phase in phase_set):
            raise AudioCaptureError("controlled gate phases must be binary pass or mute")

        frame_counts = []
        for phase in phase_set:
            exact_count = phase.duration_seconds / config.dt
            rounded_count = round(exact_count)
            if rounded_count <= 0 or not math.isclose(exact_count, rounded_count, abs_tol=1e-9):
                raise AudioCaptureError("each gate phase duration must contain whole audio chunks")
            frame_counts.append(rounded_count)

        self.source = source
        self.config = config
        self.phases = phase_set
        self._phase_frame_counts = tuple(frame_counts)
        self._cursor = 0

    @property
    def phase_frame_counts(self) -> tuple[int, ...]:
        return self._phase_frame_counts

    @property
    def total_frames(self) -> int:
        return sum(self._phase_frame_counts)

    @property
    def frames_read(self) -> int:
        return self._cursor

    @property
    def overflow_count(self) -> int:
        return int(getattr(self.source, "overflow_count", 0))

    def phase_for_frame(self, frame_index: int) -> tuple[int, int]:
        if isinstance(frame_index, bool) or not isinstance(frame_index, int):
            raise AudioCaptureError("frame_index must be an integer")
        if frame_index < 0 or frame_index >= self.total_frames:
            raise AudioCaptureError("frame_index lies outside the controlled gate schedule")
        remaining = frame_index
        for phase_index, count in enumerate(self._phase_frame_counts):
            if remaining < count:
                return phase_index, remaining
            remaining -= count
        raise AudioCaptureError("cannot resolve controlled gate frame")

    def read_frame(self) -> tuple[float, ...]:
        if self._cursor >= self.total_frames:
            raise AudioCaptureError("controlled gate source is exhausted")
        phase_index, _ = self.phase_for_frame(self._cursor)
        try:
            frame = tuple(float(value) for value in self.source.read_frame())
        except (TypeError, ValueError) as exc:
            raise AudioCaptureError("live gate source returned non-numeric samples") from exc
        if len(frame) != self.config.frame_size:
            raise AudioCaptureError("live gate source returned an incompatible frame size")
        if any(not math.isfinite(value) or abs(value) > 1.0 for value in frame):
            raise AudioCaptureError("live gate source returned samples outside the finite -1..1 domain")

        phase = self.phases[phase_index]
        self._cursor += 1
        if phase.gain == 0.0:
            return (0.0,) * self.config.frame_size
        return frame


def sound_mute_sound_20s_source(
    *,
    config: AuditoryProbeConfig | None = None,
) -> ControlledAudioPhaseSource:
    source_config = config or AuditoryProbeConfig(sample_rate=48000, frame_size=480)
    return ControlledAudioPhaseSource(
        config=source_config,
        phases=(
            AudioGainPhase("contact.1", 20.0, 1.0),
            AudioGainPhase("mute", 20.0, 0.0),
            AudioGainPhase("contact.2", 20.0, 1.0),
        ),
    )


def shifted_sound_mute_sound_20s_source(
    *,
    config: AuditoryProbeConfig | None = None,
) -> ControlledAudioPhaseSource:
    """Return the fixed frequency-shifted Z4-A independent audio control."""

    source_config = config or AuditoryProbeConfig(sample_rate=48000, frame_size=480)
    return ControlledAudioPhaseSource(
        config=source_config,
        phases=(
            AudioGainPhase("contact.1", 20.0, 1.0),
            AudioGainPhase("mute", 20.0, 0.0),
            AudioGainPhase("contact.2", 20.0, 1.0),
        ),
        frequencies=(375.0, 1500.0, 6000.0),
    )


def pass_mute_pass_20s_gate(
    source: AudioFrameSource,
    *,
    config: AuditoryProbeConfig | None = None,
) -> ControlledAudioGateSource:
    source_config = config or AuditoryProbeConfig(sample_rate=48000, frame_size=480)
    return ControlledAudioGateSource(
        source=source,
        config=source_config,
        phases=(
            AudioGainPhase("pass.1", 20.0, 1.0),
            AudioGainPhase("mute", 20.0, 0.0),
            AudioGainPhase("pass.2", 20.0, 1.0),
        ),
    )
