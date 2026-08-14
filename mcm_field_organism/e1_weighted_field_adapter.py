"""Pure opt-in adapter from E1 edge binding to internal field rates."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

import numpy as np

from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    validate_e1_state_for_layer,
)
from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import (
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)
from .neutral_local_field_substrate import NeutralLocalFieldSubstrateConfig


class E1WeightedFieldAdapterError(ValueError):
    """Raised when E1 binding cannot form a valid internal field adapter."""


_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _finite(value: object, role: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise E1WeightedFieldAdapterError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise E1WeightedFieldAdapterError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0 or (positive and result == 0.0):
        qualifier = "positive" if positive else "nonnegative"
        raise E1WeightedFieldAdapterError(f"{role} must be finite and {qualifier}")
    return result


@dataclass(frozen=True, slots=True)
class E1WeightedEdgeRate:
    """One symmetric nonnegative rate for one canonical internal edge."""

    first_neuron_id: str
    second_neuron_id: str
    rate_per_second: float

    def __post_init__(self) -> None:
        if (
            not isinstance(self.first_neuron_id, str)
            or not self.first_neuron_id
            or not isinstance(self.second_neuron_id, str)
            or not self.second_neuron_id
            or self.first_neuron_id >= self.second_neuron_id
        ):
            raise E1WeightedFieldAdapterError(
                "E1 weighted edge identities must be nonempty and canonical"
            )
        object.__setattr__(
            self,
            "rate_per_second",
            _finite(self.rate_per_second, "rate_per_second", positive=True),
        )

    @property
    def edge(self) -> tuple[str, str]:
        return (self.first_neuron_id, self.second_neuron_id)


@dataclass(frozen=True, slots=True)
class E1WeightedFieldAdapterResult:
    """Complete pure edge-rate ledger for one E1 adapter arm."""

    backreaction_enabled: bool
    base_rate_per_second: float
    edge_rates: tuple[E1WeightedEdgeRate, ...]
    edge_inventory_digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.backreaction_enabled, bool):
            raise E1WeightedFieldAdapterError(
                "backreaction_enabled must be boolean"
            )
        object.__setattr__(
            self,
            "base_rate_per_second",
            _finite(
                self.base_rate_per_second,
                "base_rate_per_second",
                positive=True,
            ),
        )
        rates = tuple(self.edge_rates)
        if not rates or any(not isinstance(item, E1WeightedEdgeRate) for item in rates):
            raise E1WeightedFieldAdapterError(
                "E1 adapter result requires weighted edge rates"
            )
        edges = [item.edge for item in rates]
        if len(set(edges)) != len(edges):
            raise E1WeightedFieldAdapterError(
                "E1 weighted edge identities must be unique"
            )
        digest = self.edge_inventory_digest
        if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise E1WeightedFieldAdapterError(
                "edge_inventory_digest must be one lowercase SHA-256 digest"
            )
        object.__setattr__(
            self,
            "edge_rates",
            tuple(sorted(rates, key=lambda item: item.edge)),
        )

    @property
    def edges(self) -> tuple[tuple[str, str], ...]:
        return tuple(item.edge for item in self.edge_rates)


def _validate_result_for_layer(
    layer: MCMNeuronLayer,
    result: E1WeightedFieldAdapterResult,
) -> None:
    if not isinstance(layer, MCMNeuronLayer):
        raise E1WeightedFieldAdapterError(
            "E1 weighted generator requires one MCM neuron layer"
        )
    if not isinstance(result, E1WeightedFieldAdapterResult):
        raise E1WeightedFieldAdapterError(
            "E1 weighted generator requires one adapter result"
        )
    try:
        edges = mcm_substrate_edge_inventory(layer)
        digest = mcm_substrate_edge_inventory_digest(layer)
    except MCMSubstrateStateError as exc:
        raise E1WeightedFieldAdapterError(str(exc)) from exc
    if result.edges != edges:
        raise E1WeightedFieldAdapterError(
            "E1 weighted rates must match the complete field edge inventory"
        )
    if result.edge_inventory_digest != digest:
        raise E1WeightedFieldAdapterError(
            "E1 weighted rate digest does not match the field geometry"
        )


def compute_e1_weighted_edge_rates(
    layer: MCMNeuronLayer,
    state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    *,
    backreaction_enabled: bool,
) -> E1WeightedFieldAdapterResult:
    """Translate one E1 ledger into symmetric internal edge rates."""

    if not isinstance(backreaction_enabled, bool):
        raise E1WeightedFieldAdapterError(
            "backreaction_enabled must be boolean"
        )
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise E1WeightedFieldAdapterError(
            "E1 adapter requires one neutral field substrate configuration"
        )
    try:
        validate_e1_state_for_layer(layer, state)
    except E1LocalEdgePlasticityError as exc:
        raise E1WeightedFieldAdapterError(str(exc)) from exc
    base_rate = 1.0 / substrate_config.response_time_seconds
    capacity = state.contract.node_capacity
    gain = state.contract.backreaction_gain if backreaction_enabled else 0.0
    rates = tuple(
        E1WeightedEdgeRate(
            item.first_neuron_id,
            item.second_neuron_id,
            base_rate * (1.0 + gain * item.binding / capacity),
        )
        for item in state.edge_bindings
    )
    result = E1WeightedFieldAdapterResult(
        backreaction_enabled=backreaction_enabled,
        base_rate_per_second=base_rate,
        edge_rates=rates,
        edge_inventory_digest=state.edge_inventory_digest,
    )
    _validate_result_for_layer(layer, result)
    maximum_rate = 3.0 * base_rate
    if any(item.rate_per_second > maximum_rate for item in result.edge_rates):
        raise E1WeightedFieldAdapterError(
            "E1 weighted rate exceeds the first adapter corridor"
        )
    return result


def build_e1_weighted_diffusion_generator(
    layer: MCMNeuronLayer,
    adapter_result: E1WeightedFieldAdapterResult,
) -> np.ndarray:
    """Build the symmetric internal weighted graph generator."""

    _validate_result_for_layer(layer, adapter_result)
    index = {neuron.neuron_id: offset for offset, neuron in enumerate(layer.neurons)}
    generator = np.zeros((len(index), len(index)), dtype=np.float64)
    for item in adapter_result.edge_rates:
        first = index[item.first_neuron_id]
        second = index[item.second_neuron_id]
        rate = item.rate_per_second
        generator[first, second] += rate
        generator[second, first] += rate
        generator[first, first] -= rate
        generator[second, second] -= rate
    if not np.all(np.isfinite(generator)):
        raise E1WeightedFieldAdapterError(
            "E1 weighted generator contains a non-finite value"
        )
    return generator
