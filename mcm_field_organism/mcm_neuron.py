"""Immutable E0 contract for one local MCM neuron with field perception."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re
from typing import Iterable


class MCMNeuronValidationError(ValueError):
    """Raised when an MCM neuron snapshot violates its causal field contract."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise MCMNeuronValidationError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _tick(value: object, role: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise MCMNeuronValidationError(f"{role} must be a non-negative integer")
    return value


def _position(values: Iterable[int], role: str, *, allow_origin: bool) -> tuple[int, ...]:
    result = tuple(values)
    if not result:
        raise MCMNeuronValidationError(f"{role} cannot be empty")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in result):
        raise MCMNeuronValidationError(f"{role} must contain integers")
    if not allow_origin and all(value == 0 for value in result):
        raise MCMNeuronValidationError(f"{role} cannot address the perceiving neuron itself")
    return result


def _field_value(value: object, role: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise MCMNeuronValidationError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or abs(result) > 1.0:
        raise MCMNeuronValidationError(
            f"{role} must stay within the normalized -1..1 field domain"
        )
    return result


@dataclass(frozen=True, slots=True)
class MCMFieldSample:
    """One spatially local field sample, not a stored edge or synaptic weight."""

    sample_id: str
    source_field_id: str
    source_tick: int
    relative_position: tuple[int, ...]
    activation: float
    afterimage: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "sample_id", _identifier(self.sample_id, "sample_id"))
        object.__setattr__(
            self,
            "source_field_id",
            _identifier(self.source_field_id, "source_field_id"),
        )
        object.__setattr__(self, "source_tick", _tick(self.source_tick, "source_tick"))
        object.__setattr__(
            self,
            "relative_position",
            _position(self.relative_position, "relative_position", allow_origin=False),
        )
        object.__setattr__(
            self, "activation", _field_value(self.activation, "activation")
        )
        object.__setattr__(
            self, "afterimage", _field_value(self.afterimage, "afterimage")
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "sample_id": self.sample_id,
            "source_field_id": self.source_field_id,
            "source_tick": self.source_tick,
            "relative_position": list(self.relative_position),
            "activation": self.activation,
            "afterimage": self.afterimage,
        }


@dataclass(frozen=True, slots=True)
class MCMFieldPerception:
    """Causally separated world contact and local prior-field perception."""

    tick: int
    receptor_contact: float | None
    local_samples: tuple[MCMFieldSample, ...]

    def __post_init__(self) -> None:
        tick = _tick(self.tick, "tick")
        object.__setattr__(self, "tick", tick)
        if self.receptor_contact is not None:
            object.__setattr__(
                self,
                "receptor_contact",
                _field_value(self.receptor_contact, "receptor_contact"),
            )

        samples = tuple(self.local_samples)
        if any(not isinstance(sample, MCMFieldSample) for sample in samples):
            raise MCMNeuronValidationError(
                "local_samples must contain only completed MCM field samples"
            )
        sample_ids = [sample.sample_id for sample in samples]
        if len(set(sample_ids)) != len(sample_ids):
            raise MCMNeuronValidationError(
                "local field samples must have unique sample identities"
            )
        expected_source_tick = tick - 1
        if samples and tick == 0:
            raise MCMNeuronValidationError("tick zero cannot perceive an earlier field")
        if any(sample.source_tick != expected_source_tick for sample in samples):
            raise MCMNeuronValidationError(
                "local field samples must come from the completed previous tick"
            )
        ordered = tuple(
            sorted(
                samples,
                key=lambda sample: (
                    sample.relative_position,
                    sample.source_field_id,
                    sample.sample_id,
                ),
            )
        )
        object.__setattr__(self, "local_samples", ordered)

    @property
    def has_receptor_dock(self) -> bool:
        return self.receptor_contact is not None

    def canonical_payload(self) -> dict[str, object]:
        return {
            "tick": self.tick,
            "receptor_contact": self.receptor_contact,
            "local_samples": [sample.canonical_payload() for sample in self.local_samples],
        }


@dataclass(frozen=True, slots=True)
class MCMNeuron:
    """One local field participant; this contract defines no update equation."""

    neuron_id: str
    field_id: str
    modality_id: str
    geometry_id: str
    position: tuple[int, ...]
    activation: float
    afterimage: float
    perception: MCMFieldPerception

    def __post_init__(self) -> None:
        for role in ("neuron_id", "field_id", "modality_id", "geometry_id"):
            object.__setattr__(self, role, _identifier(getattr(self, role), role))
        position = _position(self.position, "position", allow_origin=True)
        object.__setattr__(self, "position", position)
        object.__setattr__(
            self, "activation", _field_value(self.activation, "activation")
        )
        object.__setattr__(
            self, "afterimage", _field_value(self.afterimage, "afterimage")
        )
        if not isinstance(self.perception, MCMFieldPerception):
            raise MCMNeuronValidationError(
                "perception must be a completed MCM field perception"
            )
        if any(
            len(sample.relative_position) != len(position)
            for sample in self.perception.local_samples
        ):
            raise MCMNeuronValidationError(
                "field samples and neuron position must use the same geometry dimension"
            )

    @property
    def tick(self) -> int:
        return self.perception.tick

    def canonical_payload(self) -> dict[str, object]:
        return {
            "neuron_id": self.neuron_id,
            "field_id": self.field_id,
            "modality_id": self.modality_id,
            "geometry_id": self.geometry_id,
            "position": list(self.position),
            "activation": self.activation,
            "afterimage": self.afterimage,
            "perception": self.perception.canonical_payload(),
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def mcm_neuron_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(MCMNeuron))
