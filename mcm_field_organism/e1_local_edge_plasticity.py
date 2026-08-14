"""Isolated opt-in E1 local edge plasticity state.

This module does not advance the shared S/H field and is intentionally absent
from the package-level and current APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import (
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)


class E1LocalEdgePlasticityError(ValueError):
    """Raised when an isolated E1 state or transition is invalid."""


E1_CONTRACT_ID = "e1.resource-conserving-local-edge-plasticity.v1"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _finite(value: object, role: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool):
        raise E1LocalEdgePlasticityError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise E1LocalEdgePlasticityError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < minimum:
        raise E1LocalEdgePlasticityError(
            f"{role} must be finite and at least {minimum}"
        )
    return result


@dataclass(frozen=True, slots=True)
class E1LocalEdgePlasticityContract:
    """One global content-free contract for the isolated E1 corridor."""

    contract_id: str
    node_capacity: float
    binding_rate_per_second: float
    release_rate_per_second: float
    backreaction_gain: float

    def __post_init__(self) -> None:
        if self.contract_id != E1_CONTRACT_ID:
            raise E1LocalEdgePlasticityError(
                f"contract_id must be {E1_CONTRACT_ID}"
            )
        capacity = _finite(self.node_capacity, "node_capacity")
        if capacity <= 0.0:
            raise E1LocalEdgePlasticityError(
                "node_capacity must be greater than zero"
            )
        object.__setattr__(self, "node_capacity", capacity)
        object.__setattr__(
            self,
            "binding_rate_per_second",
            _finite(self.binding_rate_per_second, "binding_rate_per_second"),
        )
        object.__setattr__(
            self,
            "release_rate_per_second",
            _finite(self.release_rate_per_second, "release_rate_per_second"),
        )
        gain = _finite(self.backreaction_gain, "backreaction_gain")
        if gain > 1.0:
            raise E1LocalEdgePlasticityError(
                "backreaction_gain must not exceed one"
            )
        object.__setattr__(self, "backreaction_gain", gain)


@dataclass(frozen=True, slots=True)
class E1EdgeBinding:
    """One nonnegative binding on one canonical existing field edge."""

    first_neuron_id: str
    second_neuron_id: str
    binding: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.first_neuron_id, str)
            or not self.first_neuron_id
            or not isinstance(self.second_neuron_id, str)
            or not self.second_neuron_id
            or self.first_neuron_id >= self.second_neuron_id
        ):
            raise E1LocalEdgePlasticityError(
                "E1 edge identities must be nonempty and canonical"
            )
        object.__setattr__(self, "binding", _finite(self.binding, "binding"))

    @property
    def edge(self) -> tuple[str, str]:
        return (self.first_neuron_id, self.second_neuron_id)


@dataclass(frozen=True, slots=True)
class E1LocalEdgePlasticityState:
    """Complete isolated E1 edge state without free-resource duplication."""

    contract: E1LocalEdgePlasticityContract
    edge_bindings: tuple[E1EdgeBinding, ...]
    edge_inventory_digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.contract, E1LocalEdgePlasticityContract):
            raise E1LocalEdgePlasticityError(
                "E1 state requires one E1 contract"
            )
        bindings = tuple(self.edge_bindings)
        if not bindings or any(not isinstance(item, E1EdgeBinding) for item in bindings):
            raise E1LocalEdgePlasticityError(
                "E1 state requires canonical edge bindings"
            )
        edges = [item.edge for item in bindings]
        if len(set(edges)) != len(edges):
            raise E1LocalEdgePlasticityError(
                "E1 state edge identities must be unique"
            )
        digest = self.edge_inventory_digest
        if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise E1LocalEdgePlasticityError(
                "edge_inventory_digest must be one lowercase SHA-256 digest"
            )
        incident: dict[str, list[float]] = {}
        for item in bindings:
            incident.setdefault(item.first_neuron_id, []).append(item.binding)
            incident.setdefault(item.second_neuron_id, []).append(item.binding)
        capacity = self.contract.node_capacity
        if any(0.5 * math.fsum(values) > capacity for values in incident.values()):
            raise E1LocalEdgePlasticityError(
                "E1 edge bindings exceed one or more node capacities"
            )
        object.__setattr__(
            self,
            "edge_bindings",
            tuple(sorted(bindings, key=lambda item: item.edge)),
        )

    @property
    def edges(self) -> tuple[tuple[str, str], ...]:
        return tuple(item.edge for item in self.edge_bindings)


def _inventory(layer: MCMNeuronLayer) -> tuple[tuple[tuple[str, str], ...], str]:
    if not isinstance(layer, MCMNeuronLayer):
        raise E1LocalEdgePlasticityError("E1 requires one MCM neuron layer")
    try:
        return (
            mcm_substrate_edge_inventory(layer),
            mcm_substrate_edge_inventory_digest(layer),
        )
    except MCMSubstrateStateError as exc:
        raise E1LocalEdgePlasticityError(str(exc)) from exc


def validate_e1_state_for_layer(
    layer: MCMNeuronLayer,
    state: E1LocalEdgePlasticityState,
) -> None:
    """Validate one complete E1 state against the current field geometry."""

    if not isinstance(state, E1LocalEdgePlasticityState):
        raise E1LocalEdgePlasticityError("E1 requires one complete E1 state")
    edges, digest = _inventory(layer)
    if state.edges != edges:
        raise E1LocalEdgePlasticityError(
            "E1 state edges must match the complete field edge inventory"
        )
    if state.edge_inventory_digest != digest:
        raise E1LocalEdgePlasticityError(
            "E1 state edge inventory digest does not match the field geometry"
        )
    e1_free_node_resources(layer, state, _validated=True)


def build_neutral_e1_state(
    layer: MCMNeuronLayer,
    contract: E1LocalEdgePlasticityContract,
) -> E1LocalEdgePlasticityState:
    """Build zero binding on every existing field edge."""

    if not isinstance(contract, E1LocalEdgePlasticityContract):
        raise E1LocalEdgePlasticityError(
            "neutral E1 initialization requires one E1 contract"
        )
    edges, digest = _inventory(layer)
    return E1LocalEdgePlasticityState(
        contract=contract,
        edge_bindings=tuple(E1EdgeBinding(first, second, 0.0) for first, second in edges),
        edge_inventory_digest=digest,
    )


def e1_free_node_resources(
    layer: MCMNeuronLayer,
    state: E1LocalEdgePlasticityState,
    *,
    _validated: bool = False,
) -> tuple[tuple[str, float], ...]:
    """Derive each node's free resource from the edge ledger."""

    if not _validated:
        if not isinstance(state, E1LocalEdgePlasticityState):
            raise E1LocalEdgePlasticityError("E1 requires one complete E1 state")
        edges, digest = _inventory(layer)
        if state.edges != edges or state.edge_inventory_digest != digest:
            raise E1LocalEdgePlasticityError(
                "E1 state does not match the complete field geometry"
            )
    capacity = state.contract.node_capacity
    incident = {neuron.neuron_id: [] for neuron in layer.neurons}
    for item in state.edge_bindings:
        incident[item.first_neuron_id].append(item.binding)
        incident[item.second_neuron_id].append(item.binding)
    result = []
    for neuron in layer.neurons:
        free = capacity - 0.5 * math.fsum(incident[neuron.neuron_id])
        if not math.isfinite(free) or free < 0.0:
            raise E1LocalEdgePlasticityError(
                "E1 state produces a negative free node resource"
            )
        result.append((neuron.neuron_id, free))
    return tuple(result)


def advance_e1_local_edge_plasticity(
    layer: MCMNeuronLayer,
    state: E1LocalEdgePlasticityState,
    elapsed_seconds: float,
) -> E1LocalEdgePlasticityState:
    """Advance only the isolated E1 edge ledger over explicit elapsed time."""

    elapsed = _finite(elapsed_seconds, "elapsed_seconds")
    if elapsed <= 0.0:
        raise E1LocalEdgePlasticityError(
            "elapsed_seconds must be greater than zero"
        )
    validate_e1_state_for_layer(layer, state)
    contract = state.contract
    capacity = contract.node_capacity
    half_release = math.exp(-contract.release_rate_per_second * elapsed / 2.0)
    released = {
        item.edge: item.binding * half_release for item in state.edge_bindings
    }
    neuron_ids = tuple(neuron.neuron_id for neuron in layer.neurons)
    incident: dict[str, list[float]] = {neuron_id: [] for neuron_id in neuron_ids}
    for (first, second), binding in released.items():
        incident[first].append(binding)
        incident[second].append(binding)
    free = {
        neuron_id: capacity - 0.5 * math.fsum(incident[neuron_id])
        for neuron_id in neuron_ids
    }
    activation = {neuron.neuron_id: neuron.activation for neuron in layer.neurons}
    demand: dict[tuple[str, str], float] = {}
    for first, second in state.edges:
        participation = ((activation[first] - activation[second]) / 2.0) ** 2
        demand[(first, second)] = (
            capacity
            * -math.expm1(
                -contract.binding_rate_per_second * participation * elapsed
            )
            * (free[first] / capacity)
            * (free[second] / capacity)
        )
    local_demand = {
        neuron_id: 0.5
        * math.fsum(
            value for edge, value in demand.items() if neuron_id in edge
        )
        for neuron_id in neuron_ids
    }
    allocation = {
        neuron_id: (
            1.0
            if local_demand[neuron_id] == 0.0
            else min(1.0, free[neuron_id] / local_demand[neuron_id])
        )
        for neuron_id in neuron_ids
    }
    next_bindings = []
    for first, second in state.edges:
        increment = demand[(first, second)] * min(
            allocation[first], allocation[second]
        )
        binding = (released[(first, second)] + increment) * half_release
        if not math.isfinite(binding) or binding < 0.0:
            raise E1LocalEdgePlasticityError(
                "E1 transition produced an invalid edge binding"
            )
        next_bindings.append(E1EdgeBinding(first, second, binding))
    result = E1LocalEdgePlasticityState(
        contract=contract,
        edge_bindings=tuple(next_bindings),
        edge_inventory_digest=state.edge_inventory_digest,
    )
    validate_e1_state_for_layer(layer, result)
    return result
