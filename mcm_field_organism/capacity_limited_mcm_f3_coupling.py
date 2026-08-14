"""Pure opt-in capacity-limited extension of the K2/F3 edge coupling."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .mcm_f3_coupling import MCMF3LocalRate
from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import (
    MCMSubstrateState,
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)


class MCMCapacityLimitedCouplingError(ValueError):
    """Raised when the opt-in capacity-limited derivative is invalid."""


def _finite(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise MCMCapacityLimitedCouplingError(
            f"{role} must be numeric, not boolean"
        )
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise MCMCapacityLimitedCouplingError(f"{role} must be numeric") from exc
    if not math.isfinite(result):
        raise MCMCapacityLimitedCouplingError(f"{role} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class MCMCapacityLimitedCouplingContract:
    """One fixed site capacity outside the persisted substrate state."""

    site_capacity: float

    def __post_init__(self) -> None:
        capacity = _finite(self.site_capacity, "site_capacity")
        if capacity <= 0.0:
            raise MCMCapacityLimitedCouplingError(
                "site_capacity must be greater than zero"
            )
        object.__setattr__(self, "site_capacity", capacity)


@dataclass(frozen=True, slots=True)
class MCMCapacityLimitedEdgeRate:
    """Two nonnegative directed rates for one canonical field edge."""

    first_neuron_id: str
    second_neuron_id: str
    first_to_second: float
    second_to_first: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.first_neuron_id, str)
            or not self.first_neuron_id
            or not isinstance(self.second_neuron_id, str)
            or not self.second_neuron_id
            or self.first_neuron_id >= self.second_neuron_id
        ):
            raise MCMCapacityLimitedCouplingError(
                "capacity-limited edge identities must be canonical"
            )
        for role in ("first_to_second", "second_to_first"):
            value = _finite(getattr(self, role), role)
            if value < 0.0:
                raise MCMCapacityLimitedCouplingError(
                    f"{role} must be nonnegative"
                )
            object.__setattr__(self, role, value)

    @property
    def net_first_to_second(self) -> float:
        return self.first_to_second - self.second_to_first


@dataclass(frozen=True, slots=True)
class MCMCapacityLimitedCouplingResult:
    """Complete edge ledger and co-located derivative from one pre-state."""

    site_capacity: float
    edge_rates: tuple[MCMCapacityLimitedEdgeRate, ...]
    local_rates: tuple[MCMF3LocalRate, ...]

    def __post_init__(self) -> None:
        capacity = _finite(self.site_capacity, "site_capacity")
        if capacity <= 0.0:
            raise MCMCapacityLimitedCouplingError(
                "result site_capacity must be greater than zero"
            )
        edge_rates = tuple(self.edge_rates)
        local_rates = tuple(self.local_rates)
        if not edge_rates or any(
            not isinstance(item, MCMCapacityLimitedEdgeRate)
            for item in edge_rates
        ):
            raise MCMCapacityLimitedCouplingError(
                "capacity-limited result requires edge rates"
            )
        if not local_rates or any(
            not isinstance(item, MCMF3LocalRate) for item in local_rates
        ):
            raise MCMCapacityLimitedCouplingError(
                "capacity-limited result requires local rates"
            )
        edges = [
            (item.first_neuron_id, item.second_neuron_id) for item in edge_rates
        ]
        if len(set(edges)) != len(edges):
            raise MCMCapacityLimitedCouplingError(
                "capacity-limited result edge identities must be unique"
            )
        neuron_ids = [item.neuron_id for item in local_rates]
        if len(set(neuron_ids)) != len(neuron_ids):
            raise MCMCapacityLimitedCouplingError(
                "capacity-limited result neuron identities must be unique"
            )
        object.__setattr__(self, "site_capacity", capacity)
        object.__setattr__(
            self,
            "edge_rates",
            tuple(
                sorted(
                    edge_rates,
                    key=lambda item: (
                        item.first_neuron_id,
                        item.second_neuron_id,
                    ),
                )
            ),
        )
        object.__setattr__(
            self,
            "local_rates",
            tuple(sorted(local_rates, key=lambda item: item.neuron_id)),
        )

    @property
    def neuron_ids(self) -> tuple[str, ...]:
        return tuple(item.neuron_id for item in self.local_rates)

    @property
    def mass_rate(self) -> tuple[float, ...]:
        return tuple(item.mass_rate for item in self.local_rates)

    @property
    def activation_backreaction(self) -> tuple[float, ...]:
        return tuple(item.activation_backreaction for item in self.local_rates)


def compute_capacity_limited_mcm_f3_coupling(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
    contract: MCMCapacityLimitedCouplingContract,
) -> MCMCapacityLimitedCouplingResult:
    """Evaluate vacancy-limited edge exchange from one immutable S/M state."""

    if not isinstance(layer, MCMNeuronLayer):
        raise MCMCapacityLimitedCouplingError(
            "capacity-limited coupling requires one MCM neuron layer"
        )
    if not isinstance(substrate, MCMSubstrateState):
        raise MCMCapacityLimitedCouplingError(
            "capacity-limited coupling requires one complete M state"
        )
    if not isinstance(contract, MCMCapacityLimitedCouplingContract):
        raise MCMCapacityLimitedCouplingError(
            "capacity-limited coupling requires one capacity contract"
        )

    neuron_ids = tuple(neuron.neuron_id for neuron in layer.neurons)
    if substrate.neuron_ids != neuron_ids:
        raise MCMCapacityLimitedCouplingError(
            "capacity-limited substrate masses must match every field neuron"
        )
    try:
        edges = mcm_substrate_edge_inventory(layer)
        edge_digest = mcm_substrate_edge_inventory_digest(layer)
    except MCMSubstrateStateError as exc:
        raise MCMCapacityLimitedCouplingError(str(exc)) from exc
    if substrate.edge_inventory_digest != edge_digest:
        raise MCMCapacityLimitedCouplingError(
            "capacity-limited substrate edge inventory does not match geometry"
        )

    total_mass = substrate.arm.initial_total_mass
    capacity = contract.site_capacity
    mean_mass = total_mass / len(neuron_ids)
    if capacity <= mean_mass:
        raise MCMCapacityLimitedCouplingError(
            "site_capacity must exceed the homogeneous mean mass"
        )
    if capacity > total_mass:
        raise MCMCapacityLimitedCouplingError(
            "site_capacity cannot exceed the declared total mass"
        )

    activation = tuple(float(neuron.activation) for neuron in layer.neurons)
    mass = tuple(float(item.mass) for item in substrate.masses)
    if any(value > capacity for value in mass):
        raise MCMCapacityLimitedCouplingError(
            "substrate mass exceeds the declared site_capacity"
        )
    vacancy = tuple(1.0 - value / capacity for value in mass)
    index = {neuron_id: offset for offset, neuron_id in enumerate(neuron_ids)}
    mass_rate = [0.0] * len(neuron_ids)
    edge_rates = []
    arm = substrate.arm

    for first_id, second_id in edges:
        first = index[first_id]
        second = index[second_id]
        activation_delta = activation[second] - activation[first]
        first_factor = 1.0 + arm.kappa * activation_delta
        second_factor = 1.0 - arm.kappa * activation_delta
        if first_factor < 0.0 or second_factor < 0.0:
            raise MCMCapacityLimitedCouplingError(
                "directed field factors must remain nonnegative"
            )

        first_to_second = (
            arm.lambda_sm_per_second
            * mass[first]
            * vacancy[second]
            * first_factor
        )
        second_to_first = (
            arm.lambda_sm_per_second
            * mass[second]
            * vacancy[first]
            * second_factor
        )
        edge_rate = MCMCapacityLimitedEdgeRate(
            first_neuron_id=first_id,
            second_neuron_id=second_id,
            first_to_second=first_to_second,
            second_to_first=second_to_first,
        )
        edge_rates.append(edge_rate)
        mass_rate[first] -= edge_rate.net_first_to_second
        mass_rate[second] += edge_rate.net_first_to_second

    local_rates = []
    for neuron_id, current_activation, current_mass_rate in zip(
        neuron_ids,
        activation,
        mass_rate,
        strict=True,
    ):
        backreaction = (
            -arm.eta
            * (1.0 - current_activation * current_activation)
            * current_mass_rate
            / total_mass
        )
        local_rates.append(
            MCMF3LocalRate(
                neuron_id=neuron_id,
                mass_rate=current_mass_rate,
                activation_backreaction=backreaction,
            )
        )

    return MCMCapacityLimitedCouplingResult(
        site_capacity=capacity,
        edge_rates=tuple(edge_rates),
        local_rates=tuple(local_rates),
    )
