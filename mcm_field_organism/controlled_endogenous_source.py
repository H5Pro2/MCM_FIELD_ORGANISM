"""Deterministic, meaning-free endogenous contact for controlled field worlds."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
from typing import Iterable

from .endogenous_receptor import (
    EndogenousReceptorError,
    EndogenousReceptorSurface,
    audit_endogenous_contact_continuity,
)
from .receptor_contract import ReceptorContactFrame, technical_identifier


class ControlledEndogenousSourceError(ValueError):
    """Raised when a controlled endogenous source loses its explicit boundary."""


def _identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise ControlledEndogenousSourceError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class ControlledEndogenousStep:
    """One explicit test interval and its complete local contact values."""

    duration_ticks: int
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if (
            isinstance(self.duration_ticks, bool)
            or not isinstance(self.duration_ticks, int)
            or self.duration_ticks < 1
        ):
            raise ControlledEndogenousSourceError(
                "controlled endogenous duration must be a positive integer"
            )
        try:
            values = tuple(float(value) for value in self.values)
        except (TypeError, ValueError) as exc:
            raise ControlledEndogenousSourceError(
                "controlled endogenous values must be numeric"
            ) from exc
        object.__setattr__(self, "values", values)


@dataclass(frozen=True, slots=True)
class ControlledEndogenousSource:
    """Finite explicit source; it generates no noise and stores no field state."""

    source_id: str
    geometry_id: str
    clock_id: str
    carrier_ids: tuple[str, ...]
    start_tick: int
    steps: tuple[ControlledEndogenousStep, ...]

    def __post_init__(self) -> None:
        for role in ("source_id", "geometry_id", "clock_id"):
            object.__setattr__(
                self,
                role,
                _identifier(getattr(self, role), role),
            )
        if (
            isinstance(self.start_tick, bool)
            or not isinstance(self.start_tick, int)
            or self.start_tick < 0
        ):
            raise ControlledEndogenousSourceError(
                "controlled endogenous start_tick must be non-negative"
            )
        carriers = tuple(self.carrier_ids)
        try:
            surface = EndogenousReceptorSurface(
                self.source_id,
                self.geometry_id,
                carriers,
            )
        except EndogenousReceptorError as exc:
            raise ControlledEndogenousSourceError(str(exc)) from exc
        steps = tuple(self.steps)
        if not steps or any(
            not isinstance(item, ControlledEndogenousStep) for item in steps
        ):
            raise ControlledEndogenousSourceError(
                "controlled endogenous source requires explicit steps"
            )
        if any(len(item.values) != len(carriers) for item in steps):
            raise ControlledEndogenousSourceError(
                "every controlled step must match the receptor geometry"
            )
        for index, step in enumerate(steps):
            try:
                surface.complete_contact(
                    step.values,
                    snapshot_id=f"endogenous.{self.source_id}.validation.{index}",
                    clock_id=self.clock_id,
                    window_start_tick=0,
                    window_end_tick=step.duration_ticks,
                )
            except EndogenousReceptorError as exc:
                raise ControlledEndogenousSourceError(str(exc)) from exc
        object.__setattr__(self, "carrier_ids", carriers)
        object.__setattr__(self, "steps", steps)

    @property
    def frame_count(self) -> int:
        return len(self.steps)

    @property
    def end_tick(self) -> int:
        return self.start_tick + sum(item.duration_ticks for item in self.steps)

    def frames(self) -> tuple[ReceptorContactFrame, ...]:
        surface = EndogenousReceptorSurface(
            self.source_id,
            self.geometry_id,
            self.carrier_ids,
        )
        tick = self.start_tick
        completed = []
        for index, step in enumerate(self.steps):
            end_tick = tick + step.duration_ticks
            completed.append(
                surface.complete_contact(
                    step.values,
                    snapshot_id=f"endogenous.{self.source_id}.{index}",
                    clock_id=self.clock_id,
                    window_start_tick=tick,
                    window_end_tick=end_tick,
                )
            )
            tick = end_tick
        frames = tuple(completed)
        audit = audit_endogenous_contact_continuity(frames)
        if not audit.is_contiguous:
            raise ControlledEndogenousSourceError(
                "controlled endogenous source unexpectedly contains a gap"
            )
        return frames

    def canonical_payload(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "geometry_id": self.geometry_id,
            "clock_id": self.clock_id,
            "carrier_ids": list(self.carrier_ids),
            "start_tick": self.start_tick,
            "steps": [
                {
                    "duration_ticks": item.duration_ticks,
                    "values": list(item.values),
                }
                for item in self.steps
            ],
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def controlled_multiscale_endogenous_source(
    *,
    start_tick: int = 0,
    duration_ticks: int = 1,
) -> ControlledEndogenousSource:
    """Reference source with two technical carriers at distinct time scales."""

    slow = (0.0, 0.25, 0.5, 0.75, 1.0, 0.75, 0.5, 0.25)
    fast = (0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0)
    return ControlledEndogenousSource(
        source_id="controlled",
        geometry_id="endogenous.controlled.v1",
        clock_id="organism.controlled",
        carrier_ids=("c0", "c1"),
        start_tick=start_tick,
        steps=tuple(
            ControlledEndogenousStep(duration_ticks, values)
            for values in zip(slow, fast, strict=True)
        ),
    )


def controlled_endogenous_source_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            ControlledEndogenousStep,
            ControlledEndogenousSource,
        )
        for item in fields(contract)
    )
