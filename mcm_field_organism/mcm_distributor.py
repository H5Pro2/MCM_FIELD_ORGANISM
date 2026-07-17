"""Historical distributor for completed separate-field experiment windows.

The current architecture uses ``receptor_distributor.ReceptorDistributor``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
import re
from typing import Iterable


class MCMDistributionError(ValueError):
    pass


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise MCMDistributionError(f"{role} must be a lowercase technical identifier")
    return value


def _vector(values: Iterable[float], role: str) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise MCMDistributionError(f"{role} must contain numeric values") from exc
    if any(not math.isfinite(value) for value in result):
        raise MCMDistributionError(f"{role} must contain finite values")
    return result


@dataclass(frozen=True, slots=True)
class MCMDock:
    dock_id: str
    modality_id: str
    geometry_id: str
    clock_id: str

    def __post_init__(self) -> None:
        for role in ("dock_id", "modality_id", "geometry_id", "clock_id"):
            object.__setattr__(self, role, _identifier(getattr(self, role), role))


@dataclass(frozen=True, slots=True)
class MCMFieldWindow:
    dock_id: str
    modality_id: str
    field_id: str
    geometry_id: str
    snapshot_id: str
    clock_id: str
    window_start_tick: int
    window_end_tick: int
    carrier_ids: tuple[str, ...]
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]

    def __post_init__(self) -> None:
        for role in ("dock_id", "modality_id", "field_id", "geometry_id", "snapshot_id", "clock_id"):
            object.__setattr__(self, role, _identifier(getattr(self, role), role))
        if (
            isinstance(self.window_start_tick, bool)
            or isinstance(self.window_end_tick, bool)
            or not isinstance(self.window_start_tick, int)
            or not isinstance(self.window_end_tick, int)
            or self.window_start_tick < 0
            or self.window_end_tick <= self.window_start_tick
        ):
            raise MCMDistributionError("field window ticks must form a positive non-negative interval")
        carriers = tuple(self.carrier_ids)
        if not carriers:
            raise MCMDistributionError("field window requires at least one carrier")
        for carrier_id in carriers:
            _identifier(carrier_id, "carrier_id")
        if len(set(carriers)) != len(carriers):
            raise MCMDistributionError("carrier_ids must be unique")
        activation = _vector(self.activation, "activation")
        afterimage = _vector(self.afterimage, "afterimage")
        if len(activation) != len(carriers) or len(afterimage) != len(carriers):
            raise MCMDistributionError("field vectors must match carrier geometry")
        object.__setattr__(self, "carrier_ids", carriers)
        object.__setattr__(self, "activation", activation)
        object.__setattr__(self, "afterimage", afterimage)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "dock_id": self.dock_id,
            "modality_id": self.modality_id,
            "field_id": self.field_id,
            "geometry_id": self.geometry_id,
            "snapshot_id": self.snapshot_id,
            "clock_id": self.clock_id,
            "window_start_tick": self.window_start_tick,
            "window_end_tick": self.window_end_tick,
            "carrier_ids": list(self.carrier_ids),
            "activation": list(self.activation),
            "afterimage": list(self.afterimage),
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
class DistributedMCMConstellation:
    clock_id: str
    states: tuple[MCMFieldWindow, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "clock_id", _identifier(self.clock_id, "clock_id"))
        states = tuple(self.states)
        if not states:
            raise MCMDistributionError("distributed constellation requires at least one field state")
        if any(state.clock_id != self.clock_id for state in states):
            raise MCMDistributionError("constellation states must match its clock")
        dock_ids = [state.dock_id for state in states]
        modalities = [state.modality_id for state in states]
        if len(set(dock_ids)) != len(dock_ids) or len(set(modalities)) != len(modalities):
            raise MCMDistributionError("constellation requires unique docks and modalities")
        object.__setattr__(
            self,
            "states",
            tuple(sorted(states, key=lambda state: (state.dock_id, state.modality_id))),
        )

    @property
    def dock_ids(self) -> tuple[str, ...]:
        return tuple(state.dock_id for state in self.states)

    @property
    def modality_ids(self) -> tuple[str, ...]:
        return tuple(state.modality_id for state in self.states)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "clock_id": self.clock_id,
            "states": [state.canonical_payload() for state in self.states],
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(slots=True)
class MCMDistributor:
    _docks: dict[str, MCMDock] = field(default_factory=dict, init=False, repr=False)

    @property
    def docks(self) -> tuple[MCMDock, ...]:
        return tuple(sorted(self._docks.values(), key=lambda dock: dock.dock_id))

    def attach(self, dock: MCMDock) -> None:
        if dock.dock_id in self._docks:
            raise MCMDistributionError(f"dock already attached: {dock.dock_id}")
        if any(existing.modality_id == dock.modality_id for existing in self._docks.values()):
            raise MCMDistributionError(f"modality already has a dock: {dock.modality_id}")
        self._docks[dock.dock_id] = dock

    def detach(self, dock_id: str) -> MCMDock:
        dock_id = _identifier(dock_id, "dock_id")
        try:
            return self._docks.pop(dock_id)
        except KeyError as exc:
            raise MCMDistributionError(f"unknown dock: {dock_id}") from exc

    def distribute(self, states: Iterable[MCMFieldWindow]) -> DistributedMCMConstellation:
        field_states = tuple(states)
        if not field_states:
            raise MCMDistributionError("distribution requires at least one docked field state")

        dock_ids = [state.dock_id for state in field_states]
        field_ids = [state.field_id for state in field_states]
        snapshot_ids = [state.snapshot_id for state in field_states]
        if len(set(dock_ids)) != len(dock_ids):
            raise MCMDistributionError("a distribution can contain at most one state per dock")
        if len(set(field_ids)) != len(field_ids):
            raise MCMDistributionError("field_id values must be unique within a distribution")
        if len(set(snapshot_ids)) != len(snapshot_ids):
            raise MCMDistributionError("snapshot_id values must be unique within a distribution")

        clocks = {state.clock_id for state in field_states}
        if len(clocks) != 1:
            raise MCMDistributionError("all distributed field states must use the same clock")
        clock_id = next(iter(clocks))

        for state in field_states:
            dock = self._docks.get(state.dock_id)
            if dock is None:
                raise MCMDistributionError(f"unknown dock: {state.dock_id}")
            if state.modality_id != dock.modality_id:
                raise MCMDistributionError(f"modality does not match dock: {state.dock_id}")
            if state.geometry_id != dock.geometry_id:
                raise MCMDistributionError(f"geometry does not match dock: {state.dock_id}")
            if state.clock_id != dock.clock_id:
                raise MCMDistributionError(f"clock does not match dock: {state.dock_id}")

        ordered = tuple(sorted(field_states, key=lambda state: (state.dock_id, state.modality_id)))
        return DistributedMCMConstellation(clock_id=clock_id, states=ordered)
