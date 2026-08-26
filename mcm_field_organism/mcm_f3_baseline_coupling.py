"""Fixed equal-budget coupling baselines for the F3 E3 comparison."""

from __future__ import annotations

from dataclasses import fields
from typing import Callable

import numpy as np

from .mcm_f3_coupling import MCMF3CouplingResult, MCMF3LocalRate
from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import (
    MCMSubstrateState,
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)


class MCMF3BaselineCouplingError(ValueError):
    """Raised when an E3 baseline receives a state outside its fixed budget."""


MCMF3BaselineCalculator = Callable[
    [MCMNeuronLayer, MCMSubstrateState],
    MCMF3CouplingResult,
]


def _vectors_and_laplacian(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
) -> tuple[tuple[str, ...], np.ndarray, np.ndarray, np.ndarray]:
    if not isinstance(layer, MCMNeuronLayer):
        raise MCMF3BaselineCouplingError("baseline requires one MCM neuron layer")
    if not isinstance(substrate, MCMSubstrateState):
        raise MCMF3BaselineCouplingError("baseline requires one scalar state per node")
    neuron_ids = tuple(neuron.neuron_id for neuron in layer.neurons)
    if substrate.neuron_ids != neuron_ids:
        raise MCMF3BaselineCouplingError("baseline state and field nodes differ")
    if substrate.edge_inventory_digest != mcm_substrate_edge_inventory_digest(layer):
        raise MCMF3BaselineCouplingError("baseline geometry differs from the field")

    index = {neuron_id: offset for offset, neuron_id in enumerate(neuron_ids)}
    laplacian = np.zeros((len(neuron_ids), len(neuron_ids)), dtype=np.float64)
    for first_id, second_id in mcm_substrate_edge_inventory(layer):
        first = index[first_id]
        second = index[second_id]
        laplacian[first, second] += 1.0
        laplacian[first, first] -= 1.0
        laplacian[second, first] += 1.0
        laplacian[second, second] -= 1.0
    activation = np.asarray(
        [neuron.activation for neuron in layer.neurons],
        dtype=np.float64,
    )
    state = np.asarray([item.mass for item in substrate.masses], dtype=np.float64)
    return neuron_ids, activation, state, laplacian


def _result(
    neuron_ids: tuple[str, ...],
    state_rate: np.ndarray,
    backreaction: np.ndarray,
) -> MCMF3CouplingResult:
    return MCMF3CouplingResult(
        tuple(
            MCMF3LocalRate(neuron_id, state_rate[index], backreaction[index])
            for index, neuron_id in enumerate(neuron_ids)
        )
    )


def _local_trace_rate(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
) -> tuple[tuple[str, ...], np.ndarray, np.ndarray]:
    neuron_ids, activation, state, laplacian = _vectors_and_laplacian(
        layer,
        substrate,
    )
    arm = substrate.arm
    neutral = arm.initial_total_mass / len(neuron_ids)
    state_rate = (
        -arm.lambda_sm_per_second * (state - neutral)
        - 2.0
        * arm.lambda_sm_per_second
        * arm.kappa
        * neutral
        * (laplacian @ activation)
    )
    return neuron_ids, state - neutral, state_rate


def compute_mcm_f3_local_leaky_baseline(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
) -> MCMF3CouplingResult:
    """Independent local leaky state with a fixed direct state reader."""

    neuron_ids, centered_state, state_rate = _local_trace_rate(layer, substrate)
    arm = substrate.arm
    backreaction = arm.eta * arm.lambda_sm_per_second * centered_state
    return _result(neuron_ids, state_rate, backreaction)


def compute_mcm_f3_local_countervariable_baseline(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
) -> MCMF3CouplingResult:
    """Independent local linear state with backreaction tied to its rate."""

    neuron_ids, _, state_rate = _local_trace_rate(layer, substrate)
    return _result(neuron_ids, state_rate, -substrate.arm.eta * state_rate)


def compute_mcm_f3_linear_coupled_baseline(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
) -> MCMF3CouplingResult:
    """Exact first-order F3 linearization around uniform M and neutral S."""

    neuron_ids, activation, state, laplacian = _vectors_and_laplacian(
        layer,
        substrate,
    )
    arm = substrate.arm
    neutral = arm.initial_total_mass / len(neuron_ids)
    state_rate = (
        arm.lambda_sm_per_second * (laplacian @ (state - neutral))
        - 2.0
        * arm.lambda_sm_per_second
        * arm.kappa
        * neutral
        * (laplacian @ activation)
    )
    return _result(neuron_ids, state_rate, -arm.eta * state_rate)


_BASELINES: tuple[tuple[str, MCMF3BaselineCalculator], ...] = (
    ("local-leaky", compute_mcm_f3_local_leaky_baseline),
    ("local-countervariable", compute_mcm_f3_local_countervariable_baseline),
    ("linear-coupled-field", compute_mcm_f3_linear_coupled_baseline),
)


def mcm_f3_e3_baseline_calculators(
) -> tuple[tuple[str, MCMF3BaselineCalculator], ...]:
    """Return the immutable E3 baseline inventory in preregistered order."""

    return _BASELINES


def mcm_f3_baseline_coupling_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(MCMF3LocalRate))
