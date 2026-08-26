"""Immutable co-located substrate state for one shared MCM field."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re
from typing import Iterable, Mapping

from .mcm_neuron_layer import MCMNeuronLayer


class MCMSubstrateStateError(ValueError):
    """Raised when the technical M substrate contract is incomplete."""


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_MASS_ABS_TOLERANCE = 1e-12


def _identifier(value: object, role: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise MCMSubstrateStateError(
            f"{role} must be a lowercase technical identifier"
        )
    return value


def _finite(value: object, role: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool):
        raise MCMSubstrateStateError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise MCMSubstrateStateError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < minimum:
        raise MCMSubstrateStateError(
            f"{role} must be finite and at least {minimum}"
        )
    return result


def _payload_mapping(
    value: object,
    role: str,
    keys: set[str],
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise MCMSubstrateStateError(f"{role} must be an object")
    supplied = set(value)
    if supplied != keys:
        raise MCMSubstrateStateError(
            f"{role} fields mismatch; missing={sorted(keys - supplied)}, "
            f"unknown={sorted(supplied - keys)}"
        )
    return value


@dataclass(frozen=True, slots=True)
class MCMSubstrateArmContract:
    """One globally fixed F3 arm contract, not an organism control."""

    arm_id: str
    lambda_sm_per_second: float
    kappa: float
    eta: float
    initial_total_mass: float = 1.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "arm_id", _identifier(self.arm_id, "arm_id"))
        object.__setattr__(
            self,
            "lambda_sm_per_second",
            _finite(self.lambda_sm_per_second, "lambda_sm_per_second"),
        )
        kappa = _finite(self.kappa, "kappa", minimum=-0.5)
        if kappa > 0.5:
            raise MCMSubstrateStateError("kappa must stay within -0.5..0.5")
        object.__setattr__(self, "kappa", kappa)
        object.__setattr__(self, "eta", _finite(self.eta, "eta"))
        total = _finite(
            self.initial_total_mass,
            "initial_total_mass",
            minimum=1.0,
        )
        if total != 1.0:
            raise MCMSubstrateStateError(
                "the first substrate corridor requires initial_total_mass 1"
            )
        object.__setattr__(self, "initial_total_mass", total)

    @property
    def is_null_arm(self) -> bool:
        return self.lambda_sm_per_second == 0.0

    def canonical_payload(self) -> dict[str, object]:
        return {
            "arm_id": self.arm_id,
            "lambda_sm_per_second": self.lambda_sm_per_second,
            "kappa": self.kappa,
            "eta": self.eta,
            "initial_total_mass": self.initial_total_mass,
        }

    @classmethod
    def from_payload(cls, value: object) -> "MCMSubstrateArmContract":
        payload = _payload_mapping(
            value,
            "substrate arm",
            {
                "arm_id",
                "lambda_sm_per_second",
                "kappa",
                "eta",
                "initial_total_mass",
            },
        )
        return cls(**payload)


@dataclass(frozen=True, slots=True)
class MCMSubstrateMass:
    """One nonnegative M quantity co-located with an existing field neuron."""

    neuron_id: str
    mass: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "neuron_id",
            _identifier(self.neuron_id, "substrate neuron_id"),
        )
        object.__setattr__(self, "mass", _finite(self.mass, "substrate mass"))

    def canonical_payload(self) -> dict[str, object]:
        return {"neuron_id": self.neuron_id, "mass": self.mass}

    @classmethod
    def from_payload(cls, value: object) -> "MCMSubstrateMass":
        payload = _payload_mapping(
            value,
            "substrate mass",
            {"neuron_id", "mass"},
        )
        return cls(**payload)


@dataclass(frozen=True, slots=True)
class MCMSubstrateState:
    """Complete current M state without perception or history roles."""

    arm: MCMSubstrateArmContract
    masses: tuple[MCMSubstrateMass, ...]
    edge_inventory_digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.arm, MCMSubstrateArmContract):
            raise MCMSubstrateStateError(
                "substrate state requires one fixed arm contract"
            )
        masses = tuple(self.masses)
        if not masses or any(not isinstance(item, MCMSubstrateMass) for item in masses):
            raise MCMSubstrateStateError(
                "substrate state requires co-located mass values"
            )
        neuron_ids = [item.neuron_id for item in masses]
        if len(set(neuron_ids)) != len(neuron_ids):
            raise MCMSubstrateStateError(
                "substrate neuron identities must be unique"
            )
        digest = self.edge_inventory_digest
        if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise MCMSubstrateStateError(
                "edge_inventory_digest must be one lowercase SHA-256 digest"
            )
        ordered = tuple(sorted(masses, key=lambda item: item.neuron_id))
        total = math.fsum(item.mass for item in ordered)
        if not math.isclose(
            total,
            self.arm.initial_total_mass,
            rel_tol=0.0,
            abs_tol=_MASS_ABS_TOLERANCE,
        ):
            raise MCMSubstrateStateError(
                "substrate masses must equal the declared total mass"
            )
        object.__setattr__(self, "masses", ordered)

    @property
    def neuron_ids(self) -> tuple[str, ...]:
        return tuple(item.neuron_id for item in self.masses)

    @property
    def total_mass(self) -> float:
        return math.fsum(item.mass for item in self.masses)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "arm": self.arm.canonical_payload(),
            "masses": [item.canonical_payload() for item in self.masses],
            "edge_inventory_digest": self.edge_inventory_digest,
        }

    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def from_payload(cls, value: object) -> "MCMSubstrateState":
        payload = _payload_mapping(
            value,
            "substrate state",
            {"arm", "masses", "edge_inventory_digest"},
        )
        mass_values = payload["masses"]
        if not isinstance(mass_values, (list, tuple)):
            raise MCMSubstrateStateError("substrate masses must be an array")
        return cls(
            arm=MCMSubstrateArmContract.from_payload(payload["arm"]),
            masses=tuple(
                MCMSubstrateMass.from_payload(item) for item in mass_values
            ),
            edge_inventory_digest=payload["edge_inventory_digest"],
        )


def mcm_substrate_edge_inventory(
    layer: MCMNeuronLayer,
) -> tuple[tuple[str, str], ...]:
    """Return each existing symmetric local field edge exactly once."""

    if not isinstance(layer, MCMNeuronLayer):
        raise MCMSubstrateStateError(
            "substrate edge inventory requires one MCM neuron layer"
        )
    position_map = {neuron.position: neuron.neuron_id for neuron in layer.neurons}
    directed: set[tuple[str, str]] = set()
    for target in layer.neurons:
        for offset in layer.sample_offsets:
            source_position = [
                coordinate + delta
                for coordinate, delta in zip(
                    target.position,
                    offset,
                    strict=True,
                )
            ]
            for axis in layer.periodic_axes:
                source_position[axis.axis_index] = axis.origin + (
                    (source_position[axis.axis_index] - axis.origin) % axis.size
                )
            source_id = position_map.get(tuple(source_position))
            if source_id is None:
                continue
            if source_id == target.neuron_id:
                raise MCMSubstrateStateError(
                    "substrate edge inventory rejects self edges"
                )
            directed.add((target.neuron_id, source_id))

    if not directed:
        raise MCMSubstrateStateError(
            "substrate corridor requires at least one local field edge"
        )
    if any((source, target) not in directed for target, source in directed):
        raise MCMSubstrateStateError(
            "substrate edge inventory requires symmetric field adjacency"
        )
    edges = tuple(sorted(tuple(sorted(edge)) for edge in directed))
    edges = tuple(dict.fromkeys(edges))

    adjacency = {neuron.neuron_id: set() for neuron in layer.neurons}
    for first, second in edges:
        adjacency[first].add(second)
        adjacency[second].add(first)
    reached = set()
    pending = [next(iter(adjacency))]
    while pending:
        current = pending.pop()
        if current in reached:
            continue
        reached.add(current)
        pending.extend(adjacency[current] - reached)
    if reached != set(adjacency):
        raise MCMSubstrateStateError(
            "the first substrate corridor requires one connected field graph"
        )
    return edges


def mcm_substrate_edge_inventory_digest(layer: MCMNeuronLayer) -> str:
    encoded = json.dumps(
        [list(edge) for edge in mcm_substrate_edge_inventory(layer)],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_uniform_mcm_substrate(
    layer: MCMNeuronLayer,
    arm: MCMSubstrateArmContract,
) -> MCMSubstrateState:
    """Build the declared uniform M reference for the first corridor."""

    if not isinstance(arm, MCMSubstrateArmContract):
        raise MCMSubstrateStateError(
            "uniform substrate initialization requires one arm contract"
        )
    neuron_ids = tuple(neuron.neuron_id for neuron in layer.neurons)
    mass = arm.initial_total_mass / len(neuron_ids)
    return MCMSubstrateState(
        arm=arm,
        masses=tuple(MCMSubstrateMass(neuron_id, mass) for neuron_id in neuron_ids),
        edge_inventory_digest=mcm_substrate_edge_inventory_digest(layer),
    )


def mcm_substrate_state_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            MCMSubstrateArmContract,
            MCMSubstrateMass,
            MCMSubstrateState,
        )
        for item in fields(cls)
    )
