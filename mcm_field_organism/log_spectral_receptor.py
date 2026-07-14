"""Passive logarithmic audio receptor surface for Methodik 007."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np

from .carrier_baselines import BaselineValidationError


@dataclass(frozen=True, slots=True)
class LogSpectralConfig:
    sample_rate: int = 48000
    window_size: int = 4800
    hop_size: int = 480
    min_frequency: float = 50.0
    max_frequency: float = 18000.0
    band_count: int = 48

    def __post_init__(self) -> None:
        if isinstance(self.sample_rate, bool) or not isinstance(self.sample_rate, int) or self.sample_rate <= 0:
            raise BaselineValidationError("sample_rate must be a positive integer")
        if isinstance(self.window_size, bool) or not isinstance(self.window_size, int) or self.window_size <= 2:
            raise BaselineValidationError("window_size must be an integer greater than two")
        if isinstance(self.hop_size, bool) or not isinstance(self.hop_size, int) or self.hop_size <= 0:
            raise BaselineValidationError("hop_size must be a positive integer")
        if self.hop_size > self.window_size or self.window_size % self.hop_size != 0:
            raise BaselineValidationError("hop_size must divide window_size without exceeding it")
        if isinstance(self.band_count, bool) or not isinstance(self.band_count, int) or self.band_count < 2:
            raise BaselineValidationError("band_count must be an integer of at least two")
        minimum = float(self.min_frequency)
        maximum = float(self.max_frequency)
        if not math.isfinite(minimum) or not math.isfinite(maximum):
            raise BaselineValidationError("frequency bounds must be finite")
        if minimum <= 0.0 or maximum <= minimum or maximum >= self.sample_rate / 2.0:
            raise BaselineValidationError("frequency bounds must be ordered within Nyquist")
        object.__setattr__(self, "min_frequency", minimum)
        object.__setattr__(self, "max_frequency", maximum)

    @property
    def window_seconds(self) -> float:
        return self.window_size / self.sample_rate

    @property
    def hop_seconds(self) -> float:
        return self.hop_size / self.sample_rate

    @property
    def warmup_hops(self) -> int:
        return self.window_size // self.hop_size


@dataclass(frozen=True, slots=True)
class LogFrequencyBand:
    channel_id: str
    lower_frequency: float
    center_frequency: float
    upper_frequency: float


def logarithmic_bands(config: LogSpectralConfig) -> tuple[LogFrequencyBand, ...]:
    centers = np.geomspace(config.min_frequency, config.max_frequency, config.band_count)
    bands = []
    for index, center in enumerate(centers):
        lower = centers[index - 1] if index else centers[index]
        upper = centers[index + 1] if index + 1 < len(centers) else centers[index]
        bands.append(
            LogFrequencyBand(
                channel_id=f"auditory.log_hz.{float(center):.6f}",
                lower_frequency=float(lower),
                center_frequency=float(center),
                upper_frequency=float(upper),
            )
        )
    return tuple(bands)


def _validated_samples(values: Iterable[float], expected_size: int, role: str) -> np.ndarray:
    try:
        samples = np.asarray(tuple(values), dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise BaselineValidationError(f"{role} must contain numeric values") from exc
    if samples.ndim != 1 or len(samples) != expected_size:
        raise BaselineValidationError(f"{role} must contain exactly {expected_size} samples")
    if not np.all(np.isfinite(samples)) or np.any(np.abs(samples) > 1.0):
        raise BaselineValidationError(f"{role} must be finite and within -1..1")
    return samples


class LogSpectralReceptor:
    """Fixed FFT filterbank; all state is immutable after construction."""

    def __init__(self, config: LogSpectralConfig = LogSpectralConfig()) -> None:
        self.config = config
        self.bands = logarithmic_bands(config)
        self._window = np.hanning(config.window_size)
        self._window_gain = float(np.sum(self._window))
        frequencies = np.fft.rfftfreq(config.window_size, d=1.0 / config.sample_rate)
        weights = np.zeros((config.band_count, len(frequencies)), dtype=np.float64)
        for index, band in enumerate(self.bands):
            center = band.center_frequency
            if index == 0:
                weights[index, np.isclose(frequencies, center, rtol=0.0, atol=1e-12)] = 1.0
            else:
                mask = (frequencies >= band.lower_frequency) & (frequencies <= center)
                weights[index, mask] = (
                    (frequencies[mask] - band.lower_frequency)
                    / (center - band.lower_frequency)
                )
            if index == len(self.bands) - 1:
                weights[index, np.isclose(frequencies, center, rtol=0.0, atol=1e-12)] = 1.0
            else:
                mask = (frequencies >= center) & (frequencies <= band.upper_frequency)
                weights[index, mask] = np.maximum(
                    weights[index, mask],
                    (band.upper_frequency - frequencies[mask])
                    / (band.upper_frequency - center),
                )
        self._weights = weights

    @property
    def channel_ids(self) -> tuple[str, ...]:
        return tuple(band.channel_id for band in self.bands)

    def analyze(self, samples: Iterable[float]) -> tuple[float, ...]:
        values = _validated_samples(samples, self.config.window_size, "analysis window")
        spectrum = (2.0 / self._window_gain) * np.abs(np.fft.rfft(values * self._window))
        energy = np.sqrt(np.sum(np.square(self._weights * spectrum), axis=1))
        return tuple(float(value) for value in energy)


class RollingLogSpectralReceptor:
    """Explicit finite input window with no state beyond window_size samples."""

    def __init__(self, receptor: LogSpectralReceptor) -> None:
        self.receptor = receptor
        self._buffer = np.zeros(receptor.config.window_size, dtype=np.float64)
        self._filled = 0
        self._output_count = 0

    @property
    def filled_samples(self) -> int:
        return self._filled

    @property
    def output_count(self) -> int:
        return self._output_count

    def reset(self) -> None:
        self._buffer.fill(0.0)
        self._filled = 0
        self._output_count = 0

    def push(self, samples: Iterable[float]) -> tuple[float, ...] | None:
        chunk = _validated_samples(samples, self.receptor.config.hop_size, "audio chunk")
        hop = self.receptor.config.hop_size
        self._buffer[:-hop] = self._buffer[hop:]
        self._buffer[-hop:] = chunk
        self._filled = min(self.receptor.config.window_size, self._filled + hop)
        if self._filled < self.receptor.config.window_size:
            return None
        self._output_count += 1
        return self.receptor.analyze(self._buffer)
