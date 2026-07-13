"""Controlled auditory receptor and spike baselines for Methodik 004.

All transforms are deterministic and channel-local. Spikes in this module are
technical comparison outputs, not MCM neurons or a connected field.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from .carrier_baselines import BaselineValidationError, decay_factor


@dataclass(frozen=True, slots=True)
class AuditoryProbeConfig:
    sample_rate: int = 8000
    frame_size: int = 80
    frequencies: tuple[float, ...] = (200.0, 400.0, 800.0)

    def __post_init__(self) -> None:
        if isinstance(self.sample_rate, bool) or not isinstance(self.sample_rate, int) or self.sample_rate <= 0:
            raise BaselineValidationError("sample_rate must be a positive integer")
        if isinstance(self.frame_size, bool) or not isinstance(self.frame_size, int) or self.frame_size <= 1:
            raise BaselineValidationError("frame_size must be an integer greater than one")
        frequencies = tuple(float(frequency) for frequency in self.frequencies)
        if not frequencies or any(not math.isfinite(frequency) for frequency in frequencies):
            raise BaselineValidationError("frequencies must be finite and non-empty")
        if any(frequency <= 0.0 or frequency >= self.sample_rate / 2.0 for frequency in frequencies):
            raise BaselineValidationError("frequencies must lie between zero and Nyquist")
        if len(set(frequencies)) != len(frequencies):
            raise BaselineValidationError("frequencies must be unique")
        object.__setattr__(self, "frequencies", frequencies)

    @property
    def dt(self) -> float:
        return self.frame_size / self.sample_rate

    @property
    def channel_ids(self) -> tuple[str, ...]:
        return tuple(f"frequency.{int(frequency)}hz" for frequency in self.frequencies)


@dataclass(frozen=True, slots=True)
class IntegrateFireFrame:
    energy: tuple[float, ...]
    membrane: tuple[float, ...]
    spikes: tuple[int, ...]


def _samples(values: Iterable[float], config: AuditoryProbeConfig) -> tuple[float, ...]:
    try:
        samples = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise BaselineValidationError("samples must contain numeric values") from exc
    if len(samples) != config.frame_size:
        raise BaselineValidationError("sample frame must match configured frame_size")
    if any(not math.isfinite(value) or abs(value) > 1.0 for value in samples):
        raise BaselineValidationError("samples must be finite and within -1..1")
    return samples


def _energy_vector(values: Iterable[float], role: str) -> tuple[float, ...]:
    try:
        vector = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise BaselineValidationError(f"{role} must contain numeric values") from exc
    if not vector:
        raise BaselineValidationError(f"{role} cannot be empty")
    if any(not math.isfinite(value) or value < 0.0 for value in vector):
        raise BaselineValidationError(f"{role} must contain finite non-negative values")
    return vector


def synthesize_tone_frame(
    config: AuditoryProbeConfig,
    components: Iterable[tuple[float, float, float]],
) -> tuple[float, ...]:
    """Generate one deterministic frame from (frequency, amplitude, phase)."""

    components = tuple((float(frequency), float(amplitude), float(phase)) for frequency, amplitude, phase in components)
    if any(
        not math.isfinite(frequency)
        or not math.isfinite(amplitude)
        or not math.isfinite(phase)
        or frequency <= 0.0
        or frequency >= config.sample_rate / 2.0
        or amplitude < 0.0
        for frequency, amplitude, phase in components
    ):
        raise BaselineValidationError("tone components are outside the controlled probe domain")
    samples = tuple(
        sum(
            amplitude * math.sin((2.0 * math.pi * frequency * index / config.sample_rate) + phase)
            for frequency, amplitude, phase in components
        )
        for index in range(config.frame_size)
    )
    if any(abs(value) > 1.0 + 1e-12 for value in samples):
        raise BaselineValidationError("combined tone frame exceeds the normalized sample domain")
    return tuple(max(-1.0, min(1.0, value)) for value in samples)


def project_frequency_amplitude(
    samples: Iterable[float],
    *,
    sample_rate: int,
    frequency: float,
) -> float:
    sample_values = tuple(float(value) for value in samples)
    if not sample_values:
        raise BaselineValidationError("samples cannot be empty")
    if any(not math.isfinite(value) for value in sample_values):
        raise BaselineValidationError("samples must be finite")
    frequency = float(frequency)
    if not math.isfinite(frequency) or frequency <= 0.0 or frequency >= sample_rate / 2.0:
        raise BaselineValidationError("frequency must lie between zero and Nyquist")
    cosine = sum(
        value * math.cos(2.0 * math.pi * frequency * index / sample_rate)
        for index, value in enumerate(sample_values)
    )
    sine = sum(
        value * math.sin(2.0 * math.pi * frequency * index / sample_rate)
        for index, value in enumerate(sample_values)
    )
    return (2.0 / len(sample_values)) * math.hypot(cosine, sine)


def auditory_receptor_frame(
    samples: Iterable[float],
    config: AuditoryProbeConfig,
) -> tuple[float, ...]:
    sample_values = _samples(samples, config)
    return tuple(
        project_frequency_amplitude(
            sample_values,
            sample_rate=config.sample_rate,
            frequency=frequency,
        )
        for frequency in config.frequencies
    )


def threshold_events(
    previous_energy: Iterable[float],
    current_energy: Iterable[float],
    *,
    threshold: float,
) -> tuple[int, ...]:
    previous = _energy_vector(previous_energy, "previous_energy")
    current = _energy_vector(current_energy, "current_energy")
    if len(previous) != len(current):
        raise BaselineValidationError("energy vectors must have equal geometry")
    threshold = float(threshold)
    if not math.isfinite(threshold) or not 0.0 < threshold <= 1.0:
        raise BaselineValidationError("threshold must be within (0, 1]")
    events = []
    for old_value, new_value in zip(previous, current, strict=True):
        if old_value < threshold <= new_value:
            events.append(1)
        elif old_value >= threshold > new_value:
            events.append(-1)
        else:
            events.append(0)
    return tuple(events)


def integrate_and_fire_step(
    previous_membrane: Iterable[float],
    energy: Iterable[float],
    *,
    dt: float,
    tau: float,
    threshold: float,
) -> IntegrateFireFrame:
    previous = _energy_vector(previous_membrane, "previous_membrane")
    current = _energy_vector(energy, "energy")
    if len(previous) != len(current):
        raise BaselineValidationError("membrane and energy vectors must have equal geometry")
    threshold = float(threshold)
    if not math.isfinite(threshold) or not 0.0 < threshold <= 1.0:
        raise BaselineValidationError("threshold must be within (0, 1]")
    if any(value >= threshold for value in previous):
        raise BaselineValidationError("previous_membrane must be below threshold after reset")
    decay = decay_factor(dt=dt, tau=tau)
    membrane = []
    spike_counts = []
    for old_value, energy_value in zip(previous, current, strict=True):
        charge = (decay * old_value) + ((1.0 - decay) * energy_value)
        spike_count = int(math.floor(charge / threshold))
        membrane.append(charge - (threshold * spike_count))
        spike_counts.append(spike_count)
    return IntegrateFireFrame(energy=current, membrane=tuple(membrane), spikes=tuple(spike_counts))


def run_integrate_and_fire(
    energy_history: Iterable[Iterable[float]],
    *,
    dt: float,
    tau: float,
    threshold: float,
) -> tuple[IntegrateFireFrame, ...]:
    history = tuple(tuple(energy) for energy in energy_history)
    if not history:
        raise BaselineValidationError("energy_history cannot be empty")
    membrane = (0.0,) * len(history[0])
    frames = []
    for energy in history:
        frame = integrate_and_fire_step(
            membrane,
            energy,
            dt=dt,
            tau=tau,
            threshold=threshold,
        )
        frames.append(frame)
        membrane = frame.membrane
    return tuple(frames)
