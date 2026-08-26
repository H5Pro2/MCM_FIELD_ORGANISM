"""Finite passive broadband hearing path before the auditory MCM field gate."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
import hashlib
import json
import math
from typing import Callable

from .carrier_baselines import BaselineValidationError
from .controlled_audio_source import AudioCaptureError, AudioFrameSource
from .log_spectral_receptor import LogSpectralReceptor, RollingLogSpectralReceptor


class AuditoryReceptorContact(str, Enum):
    ACTIVE_ZERO = "active_zero"
    ACTIVE_ENERGY = "active_energy"


@dataclass(frozen=True, slots=True)
class AuditoryReceptorState:
    modality_id: str
    geometry_id: str
    snapshot_index: int
    window_start_sample: int
    window_end_sample: int
    carrier_ids: tuple[str, ...]
    energy: tuple[float, ...]
    contact: AuditoryReceptorContact

    def canonical_payload(self) -> dict[str, object]:
        return {
            "modality_id": self.modality_id,
            "geometry_id": self.geometry_id,
            "snapshot_index": self.snapshot_index,
            "window_start_sample": self.window_start_sample,
            "window_end_sample": self.window_end_sample,
            "carrier_ids": list(self.carrier_ids),
            "energy": list(self.energy),
            "contact": self.contact.value,
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class BroadbandHearingSummary:
    geometry_id: str
    carrier_ids: tuple[str, ...]
    input_chunks: int
    output_snapshots: int
    duration_seconds: float
    energy_min: tuple[float, ...]
    energy_max: tuple[float, ...]
    energy_mean: tuple[float, ...]
    active_zero_count: int
    active_energy_count: int
    overflow_count: int
    sequence_digest: str


class BroadbandHearingPath:
    """Transforms fixed-size chunks into immutable pre-field receptor states."""

    def __init__(self, receptor: LogSpectralReceptor) -> None:
        self.receptor = receptor
        self._rolling = RollingLogSpectralReceptor(receptor)
        self._input_chunks = 0
        self._snapshot_count = 0

    @property
    def geometry_id(self) -> str:
        config = self.receptor.config
        return (
            f"auditory.log{config.band_count}."
            f"{config.min_frequency:g}-{config.max_frequency:g}."
            f"w{config.window_size}.h{config.hop_size}.v1"
        )

    @property
    def input_chunks(self) -> int:
        return self._input_chunks

    @property
    def snapshot_count(self) -> int:
        return self._snapshot_count

    @property
    def is_fresh(self) -> bool:
        return self._input_chunks == 0 and self._snapshot_count == 0

    def reset(self) -> None:
        self._rolling.reset()
        self._input_chunks = 0
        self._snapshot_count = 0

    def push(self, samples: tuple[float, ...]) -> AuditoryReceptorState | None:
        energy = self._rolling.push(samples)
        self._input_chunks += 1
        if energy is None:
            return None
        end_sample = self._input_chunks * self.receptor.config.hop_size
        contact = (
            AuditoryReceptorContact.ACTIVE_ENERGY
            if any(value != 0.0 for value in energy)
            else AuditoryReceptorContact.ACTIVE_ZERO
        )
        state = AuditoryReceptorState(
            modality_id="auditory",
            geometry_id=self.geometry_id,
            snapshot_index=self._snapshot_count,
            window_start_sample=end_sample - self.receptor.config.window_size,
            window_end_sample=end_sample,
            carrier_ids=self.receptor.channel_ids,
            energy=energy,
            contact=contact,
        )
        self._snapshot_count += 1
        return state


Observer = Callable[[AuditoryReceptorState], object]


def _capture_chunk_count(
    duration_seconds: float,
    path: BroadbandHearingPath,
    max_duration_seconds: float,
) -> int:
    duration = float(duration_seconds)
    maximum = float(max_duration_seconds)
    if not math.isfinite(maximum) or maximum <= 0.0:
        raise AudioCaptureError("max_duration_seconds must be finite and greater than zero")
    if not math.isfinite(duration) or duration <= 0.0:
        raise AudioCaptureError("duration_seconds must be finite and greater than zero")
    if duration > maximum:
        raise AudioCaptureError("requested capture exceeds the finite duration limit")
    exact = duration / path.receptor.config.hop_seconds
    count = round(exact)
    if count <= 0 or not math.isclose(exact, count, rel_tol=0.0, abs_tol=1e-10):
        raise AudioCaptureError("duration_seconds must contain whole receptor chunks")
    if count < path.receptor.config.warmup_hops:
        raise AudioCaptureError("duration_seconds is shorter than one complete receptor window")
    return count


def capture_finite_broadband_hearing(
    source: AudioFrameSource,
    path: BroadbandHearingPath,
    *,
    duration_seconds: float,
    max_duration_seconds: float = 10.0,
    observer: Observer | None = None,
) -> BroadbandHearingSummary:
    """Run one fresh finite path without exposing or storing source samples."""

    count = _capture_chunk_count(duration_seconds, path, max_duration_seconds)
    if not path.is_fresh:
        raise AudioCaptureError("hearing path must be fresh or explicitly reset before capture")

    width = path.receptor.config.band_count
    minima = [math.inf] * width
    maxima = [-math.inf] * width
    totals = [0.0] * width
    zero_count = 0
    energy_count = 0
    output_count = 0
    digest = hashlib.sha256()

    for chunk_index in range(count):
        try:
            samples = source.read_frame()
            state = path.push(samples)
        except (AudioCaptureError, BaselineValidationError) as exc:
            raise AudioCaptureError(f"broadband capture failed at chunk {chunk_index}") from exc
        if state is None:
            continue

        before = state.digest()
        if observer is not None:
            observer(state)
        if state.digest() != before:
            raise AudioCaptureError("observer changed an immutable auditory receptor state")
        digest.update(before.encode("ascii"))
        output_count += 1
        zero_count += state.contact is AuditoryReceptorContact.ACTIVE_ZERO
        energy_count += state.contact is AuditoryReceptorContact.ACTIVE_ENERGY
        for index, value in enumerate(state.energy):
            minima[index] = min(minima[index], value)
            maxima[index] = max(maxima[index], value)
            totals[index] += value

    if output_count == 0:
        raise AudioCaptureError("finite capture produced no complete auditory receptor state")

    return BroadbandHearingSummary(
        geometry_id=path.geometry_id,
        carrier_ids=path.receptor.channel_ids,
        input_chunks=count,
        output_snapshots=output_count,
        duration_seconds=count * path.receptor.config.hop_seconds,
        energy_min=tuple(minima),
        energy_max=tuple(maxima),
        energy_mean=tuple(total / output_count for total in totals),
        active_zero_count=zero_count,
        active_energy_count=energy_count,
        overflow_count=int(getattr(source, "overflow_count", 0)),
        sequence_digest=digest.hexdigest(),
    )


def broadband_public_roles() -> tuple[str, ...]:
    state_roles = tuple(item.name for item in fields(AuditoryReceptorState))
    summary_roles = tuple(item.name for item in fields(BroadbandHearingSummary))
    return state_roles + summary_roles
