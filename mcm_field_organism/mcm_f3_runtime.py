"""Event-aligned SSPRK(3,3) runtime for the coupled K2/F3 field."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import math
from typing import Callable

import numpy as np

from .mcm_f3_coupling import MCMF3CouplingResult, compute_mcm_f3_coupling
from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_neuron_layer import MCMNeuronDrive, MCMNeuronOutput
from .mcm_substrate_state import (
    MCMSubstrateArmContract,
    MCMSubstrateMass,
    MCMSubstrateState,
    MCMSubstrateStateError,
    build_uniform_mcm_substrate,
    mcm_substrate_edge_inventory,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    _diffusion_generator,
    _generator_and_boundary,
    _step_duration,
    advance_neutral_fast_shared_field,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError
from .transient_neuron_input import TransientNeuronInputSet


class MCMF3RuntimeError(ValueError):
    """Raised when coupled integration would leave its fixed contract."""


_MASS_ABS_TOLERANCE = 1e-12
_SAFETY_MARGIN = 0.5

_CouplingCalculator = Callable[
    [MCMNeuronLayer, MCMSubstrateState],
    MCMF3CouplingResult,
]
_StateObserver = Callable[[int, np.ndarray, np.ndarray, np.ndarray], None]
_CouplingStageObserver = Callable[
    [float, np.ndarray, np.ndarray, MCMF3CouplingResult],
    None,
]
_StageValidator = Callable[[np.ndarray, np.ndarray, np.ndarray], None]


@dataclass(frozen=True, slots=True)
class MCMF3AdvanceDiagnostics:
    """Technical integration diagnostics, never persisted as field state."""

    method_id: str
    substep_count: int
    refinement: int
    safe_step_seconds: float | None
    maximum_step_seconds: float
    maximum_mass_error: float
    minimum_mass: float
    maximum_abs_activation: float
    maximum_abs_afterimage: float

    def __post_init__(self) -> None:
        if self.method_id not in {"p0.exact", "ssprk33"}:
            raise MCMF3RuntimeError("unknown F3 integration method")
        for role in ("substep_count", "refinement"):
            value = getattr(self, role)
            minimum = 0 if role == "substep_count" else 1
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                raise MCMF3RuntimeError(f"{role} is outside its technical domain")
        if self.safe_step_seconds is not None:
            if (
                isinstance(self.safe_step_seconds, bool)
                or not math.isfinite(float(self.safe_step_seconds))
                or self.safe_step_seconds <= 0.0
            ):
                raise MCMF3RuntimeError("safe_step_seconds must be positive")
        for role in (
            "maximum_step_seconds",
            "maximum_mass_error",
            "minimum_mass",
            "maximum_abs_activation",
            "maximum_abs_afterimage",
        ):
            value = getattr(self, role)
            if isinstance(value, bool) or not math.isfinite(float(value)) or value < 0.0:
                raise MCMF3RuntimeError(f"{role} must be finite and nonnegative")


@dataclass(frozen=True, slots=True)
class MCMF3AdvanceResult:
    """One completed field boundary plus non-persistent diagnostics."""

    field: SharedMCMField
    diagnostics: MCMF3AdvanceDiagnostics

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise MCMF3RuntimeError("F3 advance result requires one shared field")
        if not isinstance(self.diagnostics, MCMF3AdvanceDiagnostics):
            raise MCMF3RuntimeError("F3 advance result requires diagnostics")


@dataclass(slots=True)
class _DiagnosticAccumulator:
    substep_count: int = 0
    maximum_step_seconds: float = 0.0
    maximum_mass_error: float = 0.0
    minimum_mass: float = math.inf
    maximum_abs_activation: float = 0.0
    maximum_abs_afterimage: float = 0.0


def activate_mcm_f3_field(
    field: SharedMCMField,
    arm: MCMSubstrateArmContract,
) -> SharedMCMField:
    """Attach the explicit uniform active M reference for scheme C."""

    if not isinstance(field, SharedMCMField):
        raise MCMF3RuntimeError("F3 activation requires one shared MCM field")
    if field.substrate is not None:
        raise MCMF3RuntimeError("shared field already contains a substrate")
    if not isinstance(arm, MCMSubstrateArmContract) or arm.is_null_arm:
        raise MCMF3RuntimeError("scheme C requires one active F3 arm")
    try:
        substrate = build_uniform_mcm_substrate(field.layer, arm)
    except MCMSubstrateStateError as exc:
        raise MCMF3RuntimeError(str(exc)) from exc
    return SharedMCMField(
        layer=field.layer,
        docks=field.docks,
        last_distribution=field.last_distribution,
        substrate=substrate,
    )


def _validated_refinement(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise MCMF3RuntimeError("F3 refinement must be a positive integer")
    return value


def _validate_configs(
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
) -> None:
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise MCMF3RuntimeError(
            "F3 integration requires one substrate configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise MCMF3RuntimeError(
            "F3 integration requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config,
        NeutralFieldDissipationConfig,
    ):
        raise MCMF3RuntimeError(
            "F3 integration received an invalid dissipation configuration"
        )


def _active_substrate(field: SharedMCMField) -> MCMSubstrateState:
    if not isinstance(field, SharedMCMField):
        raise MCMF3RuntimeError("F3 integration requires one shared MCM field")
    if not isinstance(field.substrate, MCMSubstrateState):
        raise MCMF3RuntimeError("F3 integration requires one complete M state")
    if field.substrate.arm.is_null_arm:
        raise MCMF3RuntimeError("internal active F3 path received the null arm")
    return field.substrate


def _maximum_degree(field: SharedMCMField) -> int:
    try:
        edges = mcm_substrate_edge_inventory(field.layer)
    except MCMSubstrateStateError as exc:
        raise MCMF3RuntimeError(str(exc)) from exc
    degree = {neuron.neuron_id: 0 for neuron in field.layer.neurons}
    for first, second in edges:
        degree[first] += 1
        degree[second] += 1
    return max(degree.values())


def _safe_step_seconds(
    field: SharedMCMField,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
    *,
    continuous_dock_boundary: bool,
) -> float:
    substrate = _active_substrate(field)
    degree = _maximum_degree(field)
    response_rate = 1.0 / substrate_config.response_time_seconds
    leak_rate = (
        0.0
        if dissipation_config is None
        else dissipation_config.leak_rate_per_second
    )
    arm = substrate.arm
    dock_rate = 1 if continuous_dock_boundary else 0
    rho_s = (
        response_rate * (degree + dock_rate)
        + leak_rate
        + 4.0 * arm.eta * arm.lambda_sm_per_second * degree
    )
    rho_h = 1.0 / afterimage_config.time_constant_seconds + leak_rate
    rho_m = 2.0 * arm.lambda_sm_per_second * degree
    limiting_rate = max(rho_s, rho_h, rho_m)
    if not math.isfinite(limiting_rate) or limiting_rate <= 0.0:
        raise MCMF3RuntimeError("F3 safe-step rate must be finite and positive")
    return _SAFETY_MARGIN / limiting_rate


def _vectors(field: SharedMCMField) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    substrate = _active_substrate(field)
    return (
        np.asarray(
            [neuron.activation for neuron in field.layer.neurons],
            dtype=np.float64,
        ),
        np.asarray(
            [neuron.afterimage for neuron in field.layer.neurons],
            dtype=np.float64,
        ),
        np.asarray([item.mass for item in substrate.masses], dtype=np.float64),
    )


def _record_and_validate(
    activation: np.ndarray,
    afterimage: np.ndarray,
    mass: np.ndarray,
    declared_total_mass: float,
    accumulator: _DiagnosticAccumulator,
) -> None:
    if not (
        np.all(np.isfinite(activation))
        and np.all(np.isfinite(afterimage))
        and np.all(np.isfinite(mass))
    ):
        raise MCMF3RuntimeError("F3 integration produced a non-finite state")
    if np.any(activation < -1.0) or np.any(activation > 1.0):
        raise MCMF3RuntimeError("F3 activation left the normalized field domain")
    if np.any(afterimage < -1.0) or np.any(afterimage > 1.0):
        raise MCMF3RuntimeError("F3 afterimage left the normalized field domain")
    if np.any(mass < 0.0):
        raise MCMF3RuntimeError("F3 integration produced negative substrate mass")
    mass_error = abs(math.fsum(float(value) for value in mass) - declared_total_mass)
    if mass_error > _MASS_ABS_TOLERANCE:
        raise MCMF3RuntimeError("F3 integration violated total substrate mass")
    accumulator.maximum_mass_error = max(
        accumulator.maximum_mass_error,
        mass_error,
    )
    accumulator.minimum_mass = min(
        accumulator.minimum_mass,
        float(np.min(mass)),
    )
    accumulator.maximum_abs_activation = max(
        accumulator.maximum_abs_activation,
        float(np.max(np.abs(activation))),
    )
    accumulator.maximum_abs_afterimage = max(
        accumulator.maximum_abs_afterimage,
        float(np.max(np.abs(afterimage))),
    )


def _stage_coupling(
    field: SharedMCMField,
    activation: np.ndarray,
    mass: np.ndarray,
    coupling_calculator: _CouplingCalculator,
):
    substrate = _active_substrate(field)
    stage_layer = replace(
        field.layer,
        neurons=tuple(
            replace(neuron, activation=float(activation[index]))
            for index, neuron in enumerate(field.layer.neurons)
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
    return coupling_calculator(stage_layer, stage_substrate)


def _rhs(
    field: SharedMCMField,
    state: np.ndarray,
    generator: np.ndarray,
    boundary: np.ndarray,
    afterimage_config: NeutralFastAfterimageConfig,
    leak_rate: float,
    coupling_calculator: _CouplingCalculator,
    coupling_stage_observer: _CouplingStageObserver | None,
    integration_weight_seconds: float,
) -> np.ndarray:
    count = len(field.layer.neurons)
    activation = state[:count]
    afterimage = state[count : 2 * count]
    mass = state[2 * count :]
    coupling = _stage_coupling(
        field,
        activation,
        mass,
        coupling_calculator,
    )
    if coupling_stage_observer is not None:
        observer_activation = np.array(activation, copy=True)
        observer_mass = np.array(mass, copy=True)
        observer_activation.flags.writeable = False
        observer_mass.flags.writeable = False
        observer_result = coupling_stage_observer(
            integration_weight_seconds,
            observer_activation,
            observer_mass,
            coupling,
        )
        if observer_result is not None:
            raise MCMF3RuntimeError(
                "F3 coupling stage observer must not return state"
            )
    activation_rate = (
        generator @ activation
        + boundary
        - leak_rate * activation
        + np.asarray(coupling.activation_backreaction, dtype=np.float64)
    )
    tracking_rate = 1.0 / afterimage_config.time_constant_seconds
    afterimage_rate = (
        tracking_rate * (activation - afterimage) - leak_rate * afterimage
    )
    return np.concatenate(
        (
            activation_rate,
            afterimage_rate,
            np.asarray(coupling.mass_rate, dtype=np.float64),
        )
    )


def _split(field: SharedMCMField, state: np.ndarray):
    count = len(field.layer.neurons)
    return (
        state[:count],
        state[count : 2 * count],
        state[2 * count :],
    )


def _validate_stage(
    field: SharedMCMField,
    state: np.ndarray,
    accumulator: _DiagnosticAccumulator,
    stage_validator: _StageValidator | None = None,
) -> None:
    activation, afterimage, mass = _split(field, state)
    _record_and_validate(
        activation,
        afterimage,
        mass,
        _active_substrate(field).arm.initial_total_mass,
        accumulator,
    )
    if stage_validator is not None:
        values = tuple(
            np.array(item, copy=True)
            for item in (activation, afterimage, mass)
        )
        for item in values:
            item.flags.writeable = False
        validator_result = stage_validator(*values)
        if validator_result is not None:
            raise MCMF3RuntimeError("F3 stage validator must not return state")


def _ssprk33_step(
    field: SharedMCMField,
    state: np.ndarray,
    step_seconds: float,
    generator: np.ndarray,
    boundary: np.ndarray,
    afterimage_config: NeutralFastAfterimageConfig,
    leak_rate: float,
    accumulator: _DiagnosticAccumulator,
    coupling_calculator: _CouplingCalculator,
    coupling_stage_observer: _CouplingStageObserver | None,
    stage_validator: _StageValidator | None,
) -> np.ndarray:
    first_rate = _rhs(
        field,
        state,
        generator,
        boundary,
        afterimage_config,
        leak_rate,
        coupling_calculator,
        coupling_stage_observer,
        step_seconds / 6.0,
    )
    first = state + step_seconds * first_rate
    _validate_stage(field, first, accumulator, stage_validator)
    second_rate = _rhs(
        field,
        first,
        generator,
        boundary,
        afterimage_config,
        leak_rate,
        coupling_calculator,
        coupling_stage_observer,
        step_seconds / 6.0,
    )
    second_euler = first + step_seconds * second_rate
    second = 0.75 * state + 0.25 * second_euler
    _validate_stage(field, second, accumulator, stage_validator)
    third_rate = _rhs(
        field,
        second,
        generator,
        boundary,
        afterimage_config,
        leak_rate,
        coupling_calculator,
        coupling_stage_observer,
        2.0 * step_seconds / 3.0,
    )
    third_euler = second + step_seconds * third_rate
    result = (1.0 / 3.0) * state + (2.0 / 3.0) * third_euler
    _validate_stage(field, result, accumulator, stage_validator)
    return result


def _integrate_interval(
    field: SharedMCMField,
    state: np.ndarray,
    duration_seconds: float,
    safe_step_seconds: float,
    refinement: int,
    generator: np.ndarray,
    boundary: np.ndarray,
    afterimage_config: NeutralFastAfterimageConfig,
    leak_rate: float,
    accumulator: _DiagnosticAccumulator,
    coupling_calculator: _CouplingCalculator,
    coupling_stage_observer: _CouplingStageObserver | None,
    stage_validator: _StageValidator | None,
) -> np.ndarray:
    if duration_seconds == 0.0:
        return state
    base_substeps = max(1, math.ceil(duration_seconds / safe_step_seconds))
    substeps = base_substeps * refinement
    step_seconds = duration_seconds / substeps
    accumulator.maximum_step_seconds = max(
        accumulator.maximum_step_seconds,
        step_seconds,
    )
    current = state
    for _ in range(substeps):
        current = _ssprk33_step(
            field,
            current,
            step_seconds,
            generator,
            boundary,
            afterimage_config,
            leak_rate,
            accumulator,
            coupling_calculator,
            coupling_stage_observer,
            stage_validator,
        )
    accumulator.substep_count += substeps
    return current


def _apply_point_contacts(
    activation: np.ndarray,
    grouped: list[tuple[int, float, float]],
    response_time_seconds: float,
    leak_rate: float,
) -> np.ndarray:
    before = np.array(activation, copy=True)
    updated = np.array(activation, copy=True)
    response_rate = 1.0 / response_time_seconds
    for index, read_duration, value in grouped:
        if leak_rate == 0.0:
            retention = math.exp(-read_duration / response_time_seconds)
            updated[index] = retention * before[index] + (1.0 - retention) * value
        else:
            total_rate = response_rate + leak_rate
            retention = math.exp(-total_rate * read_duration)
            equilibrium = response_rate * value / total_rate
            updated[index] = (
                retention * before[index] + (1.0 - retention) * equilibrium
            )
    return updated


def _commit(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    state: np.ndarray,
    *,
    step_time=None,
    transient_inputs: TransientNeuronInputSet | None = None,
) -> SharedMCMField:
    substrate = _active_substrate(field)
    activation, afterimage, mass = _split(field, state)
    next_substrate = MCMSubstrateState(
        arm=substrate.arm,
        masses=tuple(
            MCMSubstrateMass(item.neuron_id, float(mass[index]))
            for index, item in enumerate(substrate.masses)
        ),
        edge_inventory_digest=substrate.edge_inventory_digest,
    )
    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]),
            float(afterimage[index]),
        )
        for index, neuron in enumerate(field.layer.neurons)
    }

    def coupled_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    shell = SharedMCMField(
        layer=field.layer,
        docks=field.docks,
        last_distribution=field.last_distribution,
    )
    try:
        next_shell = shell.advance(
            distribution,
            coupled_output,
            step_time=step_time,
            transient_neuron_inputs=transient_inputs,
        )
    except SharedMCMFieldError as exc:
        raise MCMF3RuntimeError(str(exc)) from exc
    return SharedMCMField(
        layer=next_shell.layer,
        docks=next_shell.docks,
        last_distribution=next_shell.last_distribution,
        substrate=next_substrate,
    )


def _diagnostics(
    method_id: str,
    refinement: int,
    safe_step_seconds: float | None,
    accumulator: _DiagnosticAccumulator,
) -> MCMF3AdvanceDiagnostics:
    return MCMF3AdvanceDiagnostics(
        method_id=method_id,
        substep_count=accumulator.substep_count,
        refinement=refinement,
        safe_step_seconds=safe_step_seconds,
        maximum_step_seconds=accumulator.maximum_step_seconds,
        maximum_mass_error=accumulator.maximum_mass_error,
        minimum_mass=accumulator.minimum_mass,
        maximum_abs_activation=accumulator.maximum_abs_activation,
        maximum_abs_afterimage=accumulator.maximum_abs_afterimage,
    )


def advance_mcm_f3_shared_field(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    step_time,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    refinement: int = 1,
    _coupling_calculator: _CouplingCalculator = compute_mcm_f3_coupling,
    _coupling_stage_observer: _CouplingStageObserver | None = None,
    _stage_validator: _StageValidator | None = None,
) -> MCMF3AdvanceResult:
    """Advance one continuous boundary interval through P0 or active F3."""

    refinement = _validated_refinement(refinement)
    _validate_configs(
        substrate_config,
        afterimage_config,
        dissipation_config,
    )
    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise MCMF3RuntimeError("F3 advance requires one substrate field")
    if field.substrate.arm.is_null_arm:
        next_field = advance_neutral_fast_shared_field(
            field,
            distribution,
            step_time,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
        activation, afterimage, mass = _vectors_for_any_substrate(next_field)
        accumulator = _DiagnosticAccumulator()
        _record_and_validate(
            activation,
            afterimage,
            mass,
            next_field.substrate.arm.initial_total_mass,
            accumulator,
        )
        return MCMF3AdvanceResult(
            next_field,
            _diagnostics("p0.exact", refinement, None, accumulator),
        )

    elapsed = _step_duration(distribution, step_time)
    generator, boundary = _generator_and_boundary(
        field,
        distribution,
        substrate_config,
    )
    leak_rate = (
        0.0
        if dissipation_config is None
        else dissipation_config.leak_rate_per_second
    )
    safe_step = _safe_step_seconds(
        field,
        substrate_config,
        afterimage_config,
        dissipation_config,
        continuous_dock_boundary=True,
    )
    activation, afterimage, mass = _vectors(field)
    state = np.concatenate((activation, afterimage, mass))
    accumulator = _DiagnosticAccumulator()
    _validate_stage(field, state, accumulator, _stage_validator)
    state = _integrate_interval(
        field,
        state,
        elapsed,
        safe_step,
        refinement,
        generator,
        boundary,
        afterimage_config,
        leak_rate,
        accumulator,
        _coupling_calculator,
        _coupling_stage_observer,
        _stage_validator,
    )
    _validate_stage(field, state, accumulator, _stage_validator)
    next_field = _commit(
        field,
        distribution,
        state,
        step_time=step_time,
    )
    return MCMF3AdvanceResult(
        next_field,
        _diagnostics("ssprk33", refinement, safe_step, accumulator),
    )


def _vectors_for_any_substrate(
    field: SharedMCMField,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if field.substrate is None:
        raise MCMF3RuntimeError("F3 diagnostics require a substrate state")
    return (
        np.asarray([item.activation for item in field.layer.neurons], dtype=np.float64),
        np.asarray([item.afterimage for item in field.layer.neurons], dtype=np.float64),
        np.asarray([item.mass for item in field.substrate.masses], dtype=np.float64),
    )


def advance_mcm_f3_shared_field_transient(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    refinement: int = 1,
    _coupling_calculator: _CouplingCalculator = compute_mcm_f3_coupling,
    _state_observer: _StateObserver | None = None,
    _coupling_stage_observer: _CouplingStageObserver | None = None,
    _stage_validator: _StageValidator | None = None,
) -> MCMF3AdvanceResult:
    """Advance active F3 between existing asynchronous receptor events."""

    refinement = _validated_refinement(refinement)
    _validate_configs(
        substrate_config,
        afterimage_config,
        dissipation_config,
    )
    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise MCMF3RuntimeError("transient F3 advance requires one substrate field")
    if field.substrate.arm.is_null_arm:
        next_field = advance_neutral_fast_shared_field_transient(
            field,
            distribution,
            transient_inputs,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
        activation, afterimage, mass = _vectors_for_any_substrate(next_field)
        accumulator = _DiagnosticAccumulator()
        _record_and_validate(
            activation,
            afterimage,
            mass,
            next_field.substrate.arm.initial_total_mass,
            accumulator,
        )
        return MCMF3AdvanceResult(
            next_field,
            _diagnostics("p0.exact", refinement, None, accumulator),
        )

    if not isinstance(transient_inputs, TransientNeuronInputSet):
        raise MCMF3RuntimeError(
            "transient F3 advance requires one complete local input set"
        )
    if distribution.contacts:
        raise MCMF3RuntimeError(
            "transient F3 advance requires a contact-free distribution"
        )
    step_time = transient_inputs.step_time
    _step_duration(distribution, step_time)
    expected_ids = set(field.layer.docked_neuron_ids)
    actual_ids = {item.neuron_id for item in transient_inputs.neuron_inputs}
    if actual_ids != expected_ids:
        raise MCMF3RuntimeError(
            "transient F3 inputs must cover every receptor dock neuron"
        )

    neuron_index = {
        neuron.neuron_id: index for index, neuron in enumerate(field.layer.neurons)
    }
    ticks_per_second = step_time.ticks_per_second
    events: dict[int, list[tuple[int, float, float]]] = {}
    for neuron_input in transient_inputs.neuron_inputs:
        index = neuron_index[neuron_input.neuron_id]
        for contact in neuron_input.contacts:
            read_duration = (
                contact.organism_read_time.window_end_tick
                - contact.organism_read_time.window_start_tick
            ) / ticks_per_second
            events.setdefault(contact.completion_tick, []).append(
                (index, read_duration, contact.value)
            )

    generator = _diffusion_generator(field, substrate_config)
    boundary = np.zeros(len(field.layer.neurons), dtype=np.float64)
    leak_rate = (
        0.0
        if dissipation_config is None
        else dissipation_config.leak_rate_per_second
    )
    safe_step = _safe_step_seconds(
        field,
        substrate_config,
        afterimage_config,
        dissipation_config,
        continuous_dock_boundary=False,
    )
    activation, afterimage, mass = _vectors(field)
    state = np.concatenate((activation, afterimage, mass))
    accumulator = _DiagnosticAccumulator()
    _validate_stage(field, state, accumulator, _stage_validator)
    current_tick = step_time.start_tick
    for completion_tick, grouped in sorted(events.items()):
        duration = (completion_tick - current_tick) / ticks_per_second
        state = _integrate_interval(
            field,
            state,
            duration,
            safe_step,
            refinement,
            generator,
            boundary,
            afterimage_config,
            leak_rate,
            accumulator,
            _coupling_calculator,
            _coupling_stage_observer,
            _stage_validator,
        )
        current_activation, current_afterimage, current_mass = _split(field, state)
        current_activation = _apply_point_contacts(
            current_activation,
            grouped,
            substrate_config.response_time_seconds,
            leak_rate,
        )
        state = np.concatenate(
            (current_activation, current_afterimage, current_mass)
        )
        _validate_stage(field, state, accumulator, _stage_validator)
        if _state_observer is not None:
            _state_observer(
                completion_tick,
                np.array(current_activation, copy=True),
                np.array(current_afterimage, copy=True),
                np.array(current_mass, copy=True),
            )
        current_tick = completion_tick
    remaining = (step_time.end_tick - current_tick) / ticks_per_second
    state = _integrate_interval(
        field,
        state,
        remaining,
        safe_step,
        refinement,
        generator,
        boundary,
        afterimage_config,
        leak_rate,
        accumulator,
        _coupling_calculator,
        _coupling_stage_observer,
        _stage_validator,
    )
    if _state_observer is not None and current_tick != step_time.end_tick:
        final_activation, final_afterimage, final_mass = _split(field, state)
        _state_observer(
            step_time.end_tick,
            np.array(final_activation, copy=True),
            np.array(final_afterimage, copy=True),
            np.array(final_mass, copy=True),
        )
    _validate_stage(field, state, accumulator, _stage_validator)
    next_field = _commit(
        field,
        distribution,
        state,
        transient_inputs=transient_inputs,
    )
    return MCMF3AdvanceResult(
        next_field,
        _diagnostics("ssprk33", refinement, safe_step, accumulator),
    )


def mcm_f3_runtime_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (MCMF3AdvanceDiagnostics, MCMF3AdvanceResult)
        for item in fields(cls)
    )
