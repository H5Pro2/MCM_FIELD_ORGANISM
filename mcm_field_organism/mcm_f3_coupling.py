"""Pure local F3 mass-rate and activation-backreaction calculation."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import (
    MCMSubstrateState,
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)


class MCMF3CouplingError(ValueError):
    """Raised when a pure F3 derivative would violate its static contract."""


@dataclass(frozen=True, slots=True)
class MCMF3LocalRate:
    """One co-located C/R pair, not a stored field state or observation."""

    neuron_id: str
    mass_rate: float
    activation_backreaction: float

    def __post_init__(self) -> None:
        if not isinstance(self.neuron_id, str) or not self.neuron_id:
            raise MCMF3CouplingError("local F3 rate requires one neuron identity")
        for role in ("mass_rate", "activation_backreaction"):
            value = getattr(self, role)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise MCMF3CouplingError(f"{role} must be numeric")
            value = float(value)
            if not math.isfinite(value):
                raise MCMF3CouplingError(f"{role} must be finite")
            object.__setattr__(self, role, value)


@dataclass(frozen=True, slots=True)
class MCMF3CouplingResult:
    """Complete derivative contribution from one atomic S/M evaluation."""

    rates: tuple[MCMF3LocalRate, ...]

    def __post_init__(self) -> None:
        rates = tuple(self.rates)
        if not rates or any(not isinstance(item, MCMF3LocalRate) for item in rates):
            raise MCMF3CouplingError("F3 result requires local C/R rates")
        neuron_ids = [item.neuron_id for item in rates]
        if len(set(neuron_ids)) != len(neuron_ids):
            raise MCMF3CouplingError("F3 result neuron identities must be unique")
        object.__setattr__(
            self,
            "rates",
            tuple(sorted(rates, key=lambda item: item.neuron_id)),
        )

    @property
    def neuron_ids(self) -> tuple[str, ...]:
        return tuple(item.neuron_id for item in self.rates)

    @property
    def mass_rate(self) -> tuple[float, ...]:
        return tuple(item.mass_rate for item in self.rates)

    @property
    def activation_backreaction(self) -> tuple[float, ...]:
        return tuple(item.activation_backreaction for item in self.rates)


def compute_mcm_f3_coupling(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
) -> MCMF3CouplingResult:
    """Compute C and its tied R once from one unchanged current S/M state."""

    if not isinstance(layer, MCMNeuronLayer):
        raise MCMF3CouplingError("F3 coupling requires one MCM neuron layer")
    if not isinstance(substrate, MCMSubstrateState):
        raise MCMF3CouplingError("F3 coupling requires one complete M state")

    neuron_ids = tuple(neuron.neuron_id for neuron in layer.neurons)
    if substrate.neuron_ids != neuron_ids:
        raise MCMF3CouplingError(
            "F3 substrate masses must match every field neuron exactly"
        )
    try:
        edges = mcm_substrate_edge_inventory(layer)
        edge_digest = mcm_substrate_edge_inventory_digest(layer)
    except MCMSubstrateStateError as exc:
        raise MCMF3CouplingError(str(exc)) from exc
    if substrate.edge_inventory_digest != edge_digest:
        raise MCMF3CouplingError(
            "F3 substrate edge inventory does not match field geometry"
        )

    arm = substrate.arm
    if arm.is_null_arm:
        return MCMF3CouplingResult(
            tuple(MCMF3LocalRate(neuron_id, 0.0, 0.0) for neuron_id in neuron_ids)
        )

    index = {neuron_id: offset for offset, neuron_id in enumerate(neuron_ids)}
    activation = tuple(float(neuron.activation) for neuron in layer.neurons)
    mass = tuple(float(item.mass) for item in substrate.masses)
    mass_rate = [0.0] * len(neuron_ids)

    for first_id, second_id in edges:
        first = index[first_id]
        second = index[second_id]
        activation_delta = activation[second] - activation[first]
        first_factor = 1.0 + arm.kappa * activation_delta
        second_factor = 1.0 - arm.kappa * activation_delta
        if first_factor < 0.0 or second_factor < 0.0:
            raise MCMF3CouplingError(
                "F3 directed mass factors must remain nonnegative"
            )

        first_to_second = (
            arm.lambda_sm_per_second * mass[first] * first_factor
        )
        second_to_first = (
            arm.lambda_sm_per_second * mass[second] * second_factor
        )
        first_change = second_to_first - first_to_second
        mass_rate[first] += first_change
        mass_rate[second] -= first_change

    total_mass = substrate.arm.initial_total_mass
    rates = []
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
        rates.append(
            MCMF3LocalRate(
                neuron_id=neuron_id,
                mass_rate=current_mass_rate,
                activation_backreaction=backreaction,
            )
        )
    return MCMF3CouplingResult(tuple(rates))


def mcm_f3_coupling_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (MCMF3LocalRate, MCMF3CouplingResult)
        for item in fields(cls)
    )
