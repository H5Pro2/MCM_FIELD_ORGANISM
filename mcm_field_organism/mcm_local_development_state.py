"""Immutable co-located L state for the S1-B reference substrate."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re
from typing import Iterable, Mapping

from .mcm_neuron_layer import MCMNeuronLayer


class MCMLocalDevelopmentStateError(ValueError):
    """Raised when the technical local development state is invalid."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")
_EQUATION_ID = "mcm.s1b.capacity-weighted-reciprocal-accommodation.v1"
_BOUND_TOLERANCE = 1e-12


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise MCMLocalDevelopmentStateError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _finite(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise MCMLocalDevelopmentStateError(f"{role} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise MCMLocalDevelopmentStateError(f"{role} must be numeric") from exc
    if not math.isfinite(result):
        raise MCMLocalDevelopmentStateError(f"{role} must be finite")
    return result


def _payload_mapping(
    value: object,
    role: str,
    keys: set[str],
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise MCMLocalDevelopmentStateError(f"{role} must be an object")
    supplied = set(value)
    if supplied != keys:
        raise MCMLocalDevelopmentStateError(
            f"{role} fields mismatch; missing={sorted(keys - supplied)}, "
            f"unknown={sorted(supplied - keys)}"
        )
    return value


@dataclass(frozen=True, slots=True)
class MCMLocalDevelopmentContract:
    """Fixed content-neutral S1-B nature parameters."""

    equation_id: str
    capacity_ratio: float
    coupling_rate_per_second: float

    def __post_init__(self) -> None:
        equation_id = _identifier(self.equation_id, "development equation_id")
        if equation_id != _EQUATION_ID:
            raise MCMLocalDevelopmentStateError(
                "development equation_id does not match the S1-B contract"
            )
        capacity_ratio = _finite(self.capacity_ratio, "capacity_ratio")
        if capacity_ratio <= 1.0:
            raise MCMLocalDevelopmentStateError(
                "capacity_ratio must be greater than one"
            )
        coupling_rate = _finite(
            self.coupling_rate_per_second,
            "coupling_rate_per_second",
        )
        if coupling_rate < 0.0:
            raise MCMLocalDevelopmentStateError(
                "coupling_rate_per_second must be nonnegative"
            )
        object.__setattr__(self, "equation_id", equation_id)
        object.__setattr__(self, "capacity_ratio", capacity_ratio)
        object.__setattr__(self, "coupling_rate_per_second", coupling_rate)

    @property
    def is_null_arm(self) -> bool:
        return self.coupling_rate_per_second == 0.0

    def canonical_payload(self) -> dict[str, object]:
        return {
            "equation_id": self.equation_id,
            "capacity_ratio": self.capacity_ratio,
            "coupling_rate_per_second": self.coupling_rate_per_second,
        }

    @classmethod
    def from_payload(cls, value: object) -> "MCMLocalDevelopmentContract":
        payload = _payload_mapping(
            value,
            "development contract",
            {
                "equation_id",
                "capacity_ratio",
                "coupling_rate_per_second",
            },
        )
        return cls(**payload)


@dataclass(frozen=True, slots=True)
class MCMLocalDevelopmentValue:
    """One signed L disposition co-located with an existing field neuron."""

    neuron_id: str
    value: float

    def __post_init__(self) -> None:
        neuron_id = _identifier(self.neuron_id, "development neuron_id")
        value = _finite(self.value, "development value")
        if value < -1.0 - _BOUND_TOLERANCE or value > 1.0 + _BOUND_TOLERANCE:
            raise MCMLocalDevelopmentStateError(
                "development value must stay within -1..1"
            )
        object.__setattr__(self, "neuron_id", neuron_id)
        object.__setattr__(self, "value", min(1.0, max(-1.0, value)))

    def canonical_payload(self) -> dict[str, object]:
        return {"neuron_id": self.neuron_id, "value": self.value}

    @classmethod
    def from_payload(cls, value: object) -> "MCMLocalDevelopmentValue":
        payload = _payload_mapping(
            value,
            "development value",
            {"neuron_id", "value"},
        )
        return cls(**payload)


@dataclass(frozen=True, slots=True)
class MCMLocalDevelopmentState:
    """Complete current L state without content, history, or reader roles."""

    contract: MCMLocalDevelopmentContract
    values: tuple[MCMLocalDevelopmentValue, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.contract, MCMLocalDevelopmentContract):
            raise MCMLocalDevelopmentStateError(
                "development state requires one fixed nature contract"
            )
        values = tuple(self.values)
        if not values or any(
            not isinstance(item, MCMLocalDevelopmentValue) for item in values
        ):
            raise MCMLocalDevelopmentStateError(
                "development state requires co-located values"
            )
        neuron_ids = [item.neuron_id for item in values]
        if len(set(neuron_ids)) != len(neuron_ids):
            raise MCMLocalDevelopmentStateError(
                "development neuron identities must be unique"
            )
        object.__setattr__(
            self,
            "values",
            tuple(sorted(values, key=lambda item: item.neuron_id)),
        )

    @property
    def neuron_ids(self) -> tuple[str, ...]:
        return tuple(item.neuron_id for item in self.values)

    @property
    def dispositions(self) -> tuple[float, ...]:
        return tuple(item.value for item in self.values)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract": self.contract.canonical_payload(),
            "values": [item.canonical_payload() for item in self.values],
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def from_payload(cls, value: object) -> "MCMLocalDevelopmentState":
        payload = _payload_mapping(
            value,
            "development state",
            {"contract", "values"},
        )
        raw_values = payload["values"]
        if not isinstance(raw_values, (list, tuple)):
            raise MCMLocalDevelopmentStateError(
                "development values must be an array"
            )
        return cls(
            contract=MCMLocalDevelopmentContract.from_payload(
                payload["contract"]
            ),
            values=tuple(
                MCMLocalDevelopmentValue.from_payload(item)
                for item in raw_values
            ),
        )


def build_zero_mcm_local_development(
    layer: MCMNeuronLayer,
    contract: MCMLocalDevelopmentContract,
) -> MCMLocalDevelopmentState:
    if not isinstance(layer, MCMNeuronLayer):
        raise MCMLocalDevelopmentStateError(
            "development initialization requires one MCM neuron layer"
        )
    if not isinstance(contract, MCMLocalDevelopmentContract):
        raise MCMLocalDevelopmentStateError(
            "development initialization requires one nature contract"
        )
    return MCMLocalDevelopmentState(
        contract=contract,
        values=tuple(
            MCMLocalDevelopmentValue(neuron.neuron_id, 0.0)
            for neuron in layer.neurons
        ),
    )


def build_mcm_local_development(
    layer: MCMNeuronLayer,
    contract: MCMLocalDevelopmentContract,
    values: Iterable[float],
) -> MCMLocalDevelopmentState:
    if not isinstance(layer, MCMNeuronLayer):
        raise MCMLocalDevelopmentStateError(
            "development construction requires one MCM neuron layer"
        )
    supplied = tuple(values)
    if len(supplied) != len(layer.neurons):
        raise MCMLocalDevelopmentStateError(
            "development values must match every field neuron exactly"
        )
    return MCMLocalDevelopmentState(
        contract=contract,
        values=tuple(
            MCMLocalDevelopmentValue(neuron.neuron_id, value)
            for neuron, value in zip(layer.neurons, supplied, strict=True)
        ),
    )


def mcm_local_development_state_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            MCMLocalDevelopmentContract,
            MCMLocalDevelopmentValue,
            MCMLocalDevelopmentState,
        )
        for item in fields(cls)
    )
