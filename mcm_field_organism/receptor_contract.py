"""Neutral receptor contracts shared by every MCM dock."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
import re
from typing import Iterable

from .broadband_hearing_path import AuditoryReceptorState
from .finite_video_path import VisualReceptorState


class ReceptorContractError(ValueError):
    """Raised when a completed receptor state violates the dock contract."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


def technical_identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ReceptorContractError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _normalized_values(
    values: Iterable[float],
    role: str,
) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise ReceptorContractError(
            f"{role} must contain numeric values"
        ) from exc
    if not result or any(
        not math.isfinite(value) or abs(value) > 1.0 for value in result
    ):
        raise ReceptorContractError(
            f"{role} must be non-empty and stay within the normalized -1..1 domain"
        )
    return result


@dataclass(frozen=True, slots=True)
class ReceptorContactFrame:
    """One completed receptor state without raw sensor payload."""

    modality_id: str
    geometry_id: str
    snapshot_id: str
    clock_id: str
    window_start_tick: int
    window_end_tick: int
    carrier_ids: tuple[str, ...]
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        for role in ("modality_id", "geometry_id", "snapshot_id", "clock_id"):
            object.__setattr__(
                self,
                role,
                technical_identifier(getattr(self, role), role),
            )
        if (
            isinstance(self.window_start_tick, bool)
            or isinstance(self.window_end_tick, bool)
            or not isinstance(self.window_start_tick, int)
            or not isinstance(self.window_end_tick, int)
            or self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
        ):
            raise ReceptorContractError(
                "receptor frame ticks must form a positive non-negative interval"
            )
        carriers = tuple(self.carrier_ids)
        if not carriers or len(set(carriers)) != len(carriers):
            raise ReceptorContractError(
                "receptor carrier identities must be non-empty and unique"
            )
        for carrier_id in carriers:
            technical_identifier(carrier_id, "carrier_id")
        values = _normalized_values(self.values, "receptor values")
        if len(values) != len(carriers):
            raise ReceptorContractError(
                "receptor values must match carrier geometry"
            )
        object.__setattr__(self, "carrier_ids", carriers)
        object.__setattr__(self, "values", values)


@dataclass(frozen=True, slots=True)
class CommonFieldTime:
    """One explicit interval on the shared organism clock."""

    clock_id: str
    window_start_tick: int
    window_end_tick: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "clock_id",
            technical_identifier(self.clock_id, "clock_id"),
        )
        if (
            isinstance(self.window_start_tick, bool)
            or isinstance(self.window_end_tick, bool)
            or not isinstance(self.window_start_tick, int)
            or not isinstance(self.window_end_tick, int)
            or self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
        ):
            raise ReceptorContractError(
                "common field ticks must form a positive non-negative interval"
            )


@dataclass(frozen=True, slots=True)
class ReceptorNeuronDockMap:
    """Lossless one-to-one technical mapping without weights or fusion."""

    modality_id: str
    receptor_geometry_id: str
    pairs: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "modality_id",
            technical_identifier(self.modality_id, "modality_id"),
        )
        object.__setattr__(
            self,
            "receptor_geometry_id",
            technical_identifier(
                self.receptor_geometry_id,
                "receptor_geometry_id",
            ),
        )
        pairs = tuple(tuple(pair) for pair in self.pairs)
        if not pairs or any(len(pair) != 2 for pair in pairs):
            raise ReceptorContractError(
                "dock map requires carrier-to-neuron pairs"
            )
        for carrier_id, neuron_id in pairs:
            technical_identifier(carrier_id, "carrier_id")
            technical_identifier(neuron_id, "neuron_id")
        carrier_ids = [pair[0] for pair in pairs]
        neuron_ids = [pair[1] for pair in pairs]
        if len(set(carrier_ids)) != len(carrier_ids):
            raise ReceptorContractError(
                "one receptor carrier cannot be copied to multiple docks"
            )
        if len(set(neuron_ids)) != len(neuron_ids):
            raise ReceptorContractError(
                "one neuron cannot receive multiple receptor carriers"
            )
        object.__setattr__(self, "pairs", tuple(sorted(pairs)))

    @property
    def carrier_ids(self) -> tuple[str, ...]:
        return tuple(pair[0] for pair in self.pairs)

    @property
    def neuron_ids(self) -> tuple[str, ...]:
        return tuple(pair[1] for pair in self.pairs)

    def contacts_for(self, frame: ReceptorContactFrame) -> dict[str, float]:
        if frame.modality_id != self.modality_id:
            raise ReceptorContractError(
                "receptor modality does not match dock map"
            )
        if frame.geometry_id != self.receptor_geometry_id:
            raise ReceptorContractError(
                "receptor geometry does not match dock map"
            )
        values_by_carrier = dict(
            zip(frame.carrier_ids, frame.values, strict=True)
        )
        expected = set(self.carrier_ids)
        supplied = set(values_by_carrier)
        if supplied != expected:
            raise ReceptorContractError(
                f"receptor carriers mismatch; missing={sorted(expected - supplied)}, "
                f"unknown={sorted(supplied - expected)}"
            )
        return {
            neuron_id: values_by_carrier[carrier_id]
            for carrier_id, neuron_id in self.pairs
        }


def from_auditory_receptor_state(
    state: AuditoryReceptorState,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=state.modality_id,
        geometry_id=state.geometry_id,
        snapshot_id=f"auditory.receptor.{state.snapshot_index}",
        clock_id="audio.sample",
        window_start_tick=state.window_start_sample,
        window_end_tick=state.window_end_sample,
        carrier_ids=state.carrier_ids,
        values=state.energy,
    )


def from_visual_receptor_state(
    state: VisualReceptorState,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=state.modality_id,
        geometry_id=state.geometry_id,
        snapshot_id=f"visual.receptor.{state.frame_index}",
        clock_id="video.frame",
        window_start_tick=state.frame_index,
        window_end_tick=state.frame_index + 1,
        carrier_ids=state.carrier_ids,
        values=state.channel_values,
    )


def receptor_contract_public_roles() -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(item.name for item in fields(ReceptorContactFrame)),
        tuple(item.name for item in fields(CommonFieldTime)),
    )
