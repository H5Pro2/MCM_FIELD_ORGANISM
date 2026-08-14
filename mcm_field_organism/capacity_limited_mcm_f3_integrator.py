"""Isolated SSPRK(3,3) integration of the capacity-limited coupling only."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import math

import numpy as np

from .capacity_limited_mcm_f3_coupling import (
    MCMCapacityLimitedCouplingContract,
    MCMCapacityLimitedCouplingError,
    compute_capacity_limited_mcm_f3_coupling,
)
from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import (
    MCMSubstrateMass,
    MCMSubstrateState,
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory,
)


_MASS_ABS_TOLERANCE = 1e-12
_SAFETY_MARGIN = 0.5
_METHOD_ID = "w7i.capacity-limited-coupling.ssprk33.v1"


class MCMCapacityLimitedIntegratorError(ValueError):
    """Raised when the isolated vector integration violates W7-H."""


def _finite(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise MCMCapacityLimitedIntegratorError(
            f"{role} must be numeric, not boolean"
        )
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise MCMCapacityLimitedIntegratorError(f"{role} must be numeric") from exc
    if not math.isfinite(result):
        raise MCMCapacityLimitedIntegratorError(f"{role} must be finite")
    return result


def _contract_digest(contract: MCMCapacityLimitedCouplingContract) -> str:
    encoded = json.dumps(
        {
            "equation_id": _METHOD_ID,
            "site_capacity": contract.site_capacity,
        },
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class MCMCapacityLimitedIntegrationDiagnostics:
    """Passive scalar diagnostics, never an input to the integrated state."""

    method_id: str
    substep_count: int
    stage_count: int
    refinement: int
    safe_step_seconds: float | None
    maximum_step_seconds: float
    maximum_mass_error: float
    minimum_mass: float
    maximum_mass: float
    minimum_free_capacity: float
    maximum_capacity_excess: float
    maximum_abs_activation: float
    maximum_abs_afterimage: float
    capacity_contract_digest: str


@dataclass(frozen=True, slots=True)
class MCMCapacityLimitedIntegrationResult:
    """Final technical vectors without a committed shared field state."""

    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    mass: tuple[float, ...]
    diagnostics: MCMCapacityLimitedIntegrationDiagnostics


@dataclass(slots=True)
class _Accumulator:
    stage_count: int = 0
    maximum_mass_error: float = 0.0
    minimum_mass: float = math.inf
    maximum_mass: float = 0.0
    minimum_free_capacity: float = math.inf
    maximum_capacity_excess: float = 0.0
    maximum_abs_activation: float = 0.0
    maximum_abs_afterimage: float = 0.0


def _maximum_degree(layer: MCMNeuronLayer) -> int:
    try:
        edges = mcm_substrate_edge_inventory(layer)
    except MCMSubstrateStateError as exc:
        raise MCMCapacityLimitedIntegratorError(str(exc)) from exc
    degree = {neuron.neuron_id: 0 for neuron in layer.neurons}
    for first, second in edges:
        degree[first] += 1
        degree[second] += 1
    return max(degree.values())


def _safe_step_seconds(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
) -> float:
    degree = _maximum_degree(layer)
    arm = substrate.arm
    rho_s = 4.0 * arm.eta * arm.lambda_sm_per_second * degree
    rho_m = 2.0 * arm.lambda_sm_per_second * degree
    limiting_rate = max(rho_s, rho_m)
    if not math.isfinite(limiting_rate) or limiting_rate <= 0.0:
        raise MCMCapacityLimitedIntegratorError(
            "active capacity-limited safe-step rate must be positive"
        )
    return _SAFETY_MARGIN / limiting_rate


def _split(state: np.ndarray, count: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return state[:count], state[count : 2 * count], state[2 * count :]


def _validate_and_record(
    state: np.ndarray,
    count: int,
    total_mass: float,
    site_capacity: float,
    accumulator: _Accumulator,
    *,
    count_stage: bool,
) -> None:
    activation, afterimage, mass = _split(state, count)
    if not (
        np.all(np.isfinite(activation))
        and np.all(np.isfinite(afterimage))
        and np.all(np.isfinite(mass))
    ):
        raise MCMCapacityLimitedIntegratorError(
            "capacity-limited integration produced a non-finite state"
        )
    if np.any(activation < -1.0) or np.any(activation > 1.0):
        raise MCMCapacityLimitedIntegratorError(
            "capacity-limited activation left the normalized field domain"
        )
    if np.any(afterimage < -1.0) or np.any(afterimage > 1.0):
        raise MCMCapacityLimitedIntegratorError(
            "capacity-limited afterimage left the normalized field domain"
        )
    minimum_mass = float(np.min(mass))
    maximum_mass = float(np.max(mass))
    if minimum_mass < 0.0:
        raise MCMCapacityLimitedIntegratorError(
            "capacity-limited integration produced negative mass"
        )
    if maximum_mass > site_capacity:
        raise MCMCapacityLimitedIntegratorError(
            "capacity-limited integration exceeded site_capacity"
        )
    mass_error = abs(math.fsum(float(value) for value in mass) - total_mass)
    if mass_error > _MASS_ABS_TOLERANCE:
        raise MCMCapacityLimitedIntegratorError(
            "capacity-limited integration violated total mass"
        )
    accumulator.maximum_mass_error = max(
        accumulator.maximum_mass_error,
        mass_error,
    )
    accumulator.minimum_mass = min(accumulator.minimum_mass, minimum_mass)
    accumulator.maximum_mass = max(accumulator.maximum_mass, maximum_mass)
    accumulator.minimum_free_capacity = min(
        accumulator.minimum_free_capacity,
        site_capacity - maximum_mass,
    )
    accumulator.maximum_capacity_excess = max(
        accumulator.maximum_capacity_excess,
        max(0.0, maximum_mass - site_capacity),
    )
    accumulator.maximum_abs_activation = max(
        accumulator.maximum_abs_activation,
        float(np.max(np.abs(activation))),
    )
    accumulator.maximum_abs_afterimage = max(
        accumulator.maximum_abs_afterimage,
        float(np.max(np.abs(afterimage))),
    )
    if count_stage:
        accumulator.stage_count += 1


def _rhs(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
    contract: MCMCapacityLimitedCouplingContract,
    state: np.ndarray,
) -> np.ndarray:
    count = len(layer.neurons)
    activation, afterimage, mass = _split(state, count)
    stage_layer = replace(
        layer,
        neurons=tuple(
            replace(
                neuron,
                activation=float(activation[index]),
                afterimage=float(afterimage[index]),
            )
            for index, neuron in enumerate(layer.neurons)
        ),
    )
    stage_substrate = MCMSubstrateState(
        arm=substrate.arm,
        masses=tuple(
            MCMSubstrateMass(item.neuron_id, float(mass[index]))
            for index, item in enumerate(substrate.masses)
        ),
        edge_inventory_digest=substrate.edge_inventory_digest,
    )
    try:
        coupling = compute_capacity_limited_mcm_f3_coupling(
            stage_layer,
            stage_substrate,
            contract,
        )
    except MCMCapacityLimitedCouplingError as exc:
        raise MCMCapacityLimitedIntegratorError(str(exc)) from exc
    return np.concatenate(
        (
            np.asarray(coupling.activation_backreaction, dtype=np.float64),
            np.zeros(count, dtype=np.float64),
            np.asarray(coupling.mass_rate, dtype=np.float64),
        )
    )


def _ssprk33_step(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
    contract: MCMCapacityLimitedCouplingContract,
    state: np.ndarray,
    step_seconds: float,
    accumulator: _Accumulator,
) -> np.ndarray:
    count = len(layer.neurons)
    total_mass = substrate.arm.initial_total_mass
    capacity = contract.site_capacity

    first = state + step_seconds * _rhs(layer, substrate, contract, state)
    _validate_and_record(
        first,
        count,
        total_mass,
        capacity,
        accumulator,
        count_stage=True,
    )
    second_euler = first + step_seconds * _rhs(
        layer, substrate, contract, first
    )
    second = 0.75 * state + 0.25 * second_euler
    _validate_and_record(
        second,
        count,
        total_mass,
        capacity,
        accumulator,
        count_stage=True,
    )
    third_euler = second + step_seconds * _rhs(
        layer, substrate, contract, second
    )
    result = (1.0 / 3.0) * state + (2.0 / 3.0) * third_euler
    _validate_and_record(
        result,
        count,
        total_mass,
        capacity,
        accumulator,
        count_stage=True,
    )
    return result


def integrate_capacity_limited_mcm_f3_coupling(
    layer: MCMNeuronLayer,
    substrate: MCMSubstrateState,
    contract: MCMCapacityLimitedCouplingContract,
    duration_seconds: float,
    *,
    refinement: int = 1,
) -> MCMCapacityLimitedIntegrationResult:
    """Integrate only W7-G coupling vectors; do not commit a field runtime."""

    if not isinstance(layer, MCMNeuronLayer):
        raise MCMCapacityLimitedIntegratorError(
            "capacity-limited integration requires one MCM neuron layer"
        )
    if not isinstance(substrate, MCMSubstrateState):
        raise MCMCapacityLimitedIntegratorError(
            "capacity-limited integration requires one complete M state"
        )
    if not isinstance(contract, MCMCapacityLimitedCouplingContract):
        raise MCMCapacityLimitedIntegratorError(
            "capacity-limited integration requires one capacity contract"
        )
    duration = _finite(duration_seconds, "duration_seconds")
    if duration < 0.0:
        raise MCMCapacityLimitedIntegratorError(
            "duration_seconds must be nonnegative"
        )
    if (
        isinstance(refinement, bool)
        or not isinstance(refinement, int)
        or refinement < 1
    ):
        raise MCMCapacityLimitedIntegratorError(
            "refinement must be a positive integer"
        )

    count = len(layer.neurons)
    state = np.asarray(
        [
            *(neuron.activation for neuron in layer.neurons),
            *(neuron.afterimage for neuron in layer.neurons),
            *(item.mass for item in substrate.masses),
        ],
        dtype=np.float64,
    )
    accumulator = _Accumulator()
    _validate_and_record(
        state,
        count,
        substrate.arm.initial_total_mass,
        contract.site_capacity,
        accumulator,
        count_stage=False,
    )

    try:
        compute_capacity_limited_mcm_f3_coupling(layer, substrate, contract)
    except MCMCapacityLimitedCouplingError as exc:
        raise MCMCapacityLimitedIntegratorError(str(exc)) from exc

    safe_step = None
    substeps = 0
    maximum_step = 0.0
    method_id = "p0.exact" if substrate.arm.is_null_arm else _METHOD_ID
    if duration > 0.0 and not substrate.arm.is_null_arm:
        safe_step = _safe_step_seconds(layer, substrate)
        base_substeps = max(1, math.ceil(duration / safe_step))
        substeps = base_substeps * refinement
        maximum_step = duration / substeps
        for _ in range(substeps):
            state = _ssprk33_step(
                layer,
                substrate,
                contract,
                state,
                maximum_step,
                accumulator,
            )

    activation, afterimage, mass = _split(state, count)
    diagnostics = MCMCapacityLimitedIntegrationDiagnostics(
        method_id=method_id,
        substep_count=substeps,
        stage_count=accumulator.stage_count,
        refinement=refinement,
        safe_step_seconds=safe_step,
        maximum_step_seconds=maximum_step,
        maximum_mass_error=accumulator.maximum_mass_error,
        minimum_mass=accumulator.minimum_mass,
        maximum_mass=accumulator.maximum_mass,
        minimum_free_capacity=accumulator.minimum_free_capacity,
        maximum_capacity_excess=accumulator.maximum_capacity_excess,
        maximum_abs_activation=accumulator.maximum_abs_activation,
        maximum_abs_afterimage=accumulator.maximum_abs_afterimage,
        capacity_contract_digest=_contract_digest(contract),
    )
    return MCMCapacityLimitedIntegrationResult(
        activation=tuple(float(value) for value in activation),
        afterimage=tuple(float(value) for value in afterimage),
        mass=tuple(float(value) for value in mass),
        diagnostics=diagnostics,
    )
