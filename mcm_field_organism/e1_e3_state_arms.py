"""Private E1 E3 release and competing-resource state-arm preparation."""

from __future__ import annotations

import copy
from dataclasses import dataclass, fields
import math

import numpy as np

from .e1_coupled_fast_field import (
    E1CoupledFastFieldError,
    advance_e1_coupled_fast_shared_field,
)
from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    advance_e1_local_edge_plasticity,
    build_neutral_e1_state,
    e1_free_node_resources,
    validate_e1_state_for_layer,
)
from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import DistributedReceptorContact, ReceptorDistribution
from .shared_mcm_field import SharedMCMField


class E1E3StateArmsError(ValueError):
    """Raised when the pre-registered E3 state arms cannot be prepared."""


E1_E3_ABSOLUTE_TOLERANCE = 1e-12
E1_E3_RELEASE_TIMES_SECONDS = (0.0, 1.0, 4.0, 8.0)
E1_E3_COMPETING_INTERVALS = 8
E1_E3_TICKS_PER_INTERVAL = 10
E1_E3_TICKS_PER_SECOND = 10.0
_RIGHT_CONTACT = (0.0, 0.0, 1.0)


def _finite(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise E1E3StateArmsError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise E1E3StateArmsError(f"{role} must be numeric") from exc
    if not math.isfinite(result):
        raise E1E3StateArmsError(f"{role} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class E1ReleaseCheckpoint:
    """One elapsed-time state from the uniform no-contact release arm."""

    elapsed_seconds: float
    state: E1LocalEdgePlasticityState
    analytic_linf: float

    def __post_init__(self) -> None:
        elapsed = _finite(self.elapsed_seconds, "elapsed_seconds")
        error = _finite(self.analytic_linf, "analytic_linf")
        if elapsed < 0.0 or error < 0.0:
            raise E1E3StateArmsError("release checkpoint values must be nonnegative")
        if not isinstance(self.state, E1LocalEdgePlasticityState):
            raise E1E3StateArmsError("release checkpoint requires one E1 state")
        object.__setattr__(self, "elapsed_seconds", elapsed)
        object.__setattr__(self, "analytic_linf", error)


@dataclass(frozen=True, slots=True)
class E1E3StateArmMetrics:
    """Raw state-arm values without a final E3 interpretation."""

    release_analytic_linf: float
    resource_budget_linf: float
    release_total_binding_drop: float
    compete_release_binding_linf: float
    compete_total_binding_rebound: float
    compete_neutral_binding_linf: float

    def __post_init__(self) -> None:
        for item in fields(self):
            object.__setattr__(self, item.name, _finite(getattr(self, item.name), item.name))


@dataclass(frozen=True, slots=True)
class E1E3StateArmsResult:
    """Four private E1 state arms before the later identical probe."""

    hold_state: E1LocalEdgePlasticityState
    release_checkpoints: tuple[E1ReleaseCheckpoint, ...]
    release_state: E1LocalEdgePlasticityState
    compete_field: SharedMCMField
    compete_state: E1LocalEdgePlasticityState
    neutral_field: SharedMCMField
    neutral_state: E1LocalEdgePlasticityState
    metrics: E1E3StateArmMetrics

    def __post_init__(self) -> None:
        for role in ("hold_state", "release_state", "compete_state", "neutral_state"):
            if not isinstance(getattr(self, role), E1LocalEdgePlasticityState):
                raise E1E3StateArmsError(f"{role} must be one E1 state")
        checkpoints = tuple(self.release_checkpoints)
        if tuple(item.elapsed_seconds for item in checkpoints) != E1_E3_RELEASE_TIMES_SECONDS:
            raise E1E3StateArmsError("release checkpoints do not match the registered times")
        if checkpoints[2].state != self.release_state:
            raise E1E3StateArmsError("release_state must be the four-second checkpoint")
        if not isinstance(self.compete_field, SharedMCMField) or not isinstance(
            self.neutral_field, SharedMCMField
        ):
            raise E1E3StateArmsError("competing arms require completed fields")
        if not isinstance(self.metrics, E1E3StateArmMetrics):
            raise E1E3StateArmsError("state arms require raw metrics")
        object.__setattr__(self, "release_checkpoints", checkpoints)


def _bindings(state: E1LocalEdgePlasticityState) -> np.ndarray:
    return np.asarray([item.binding for item in state.edge_bindings], dtype=np.float64)


def _linf(first: E1LocalEdgePlasticityState, second: E1LocalEdgePlasticityState) -> float:
    return float(np.max(np.abs(_bindings(first) - _bindings(second))))


def _total_binding(state: E1LocalEdgePlasticityState) -> float:
    return math.fsum(item.binding for item in state.edge_bindings)


def _resource_budget_error(field: SharedMCMField, state: E1LocalEdgePlasticityState) -> float:
    free = math.fsum(value for _, value in e1_free_node_resources(field.layer, state))
    expected = len(field.layer.neurons) * state.contract.node_capacity
    return abs(free + _total_binding(state) - expected)


def produce_e1_uniform_release_checkpoints(
    uniform_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
) -> tuple[E1ReleaseCheckpoint, ...]:
    """Advance only E1 at the four registered uniform no-contact times."""

    if not isinstance(uniform_field, SharedMCMField):
        raise E1E3StateArmsError("release requires one shared field")
    activation = tuple(neuron.activation for neuron in uniform_field.layer.neurons)
    if len(activation) != 3 or max(activation) != min(activation):
        raise E1E3StateArmsError("release requires a uniform three-neuron field")
    try:
        validate_e1_state_for_layer(uniform_field.layer, initial_state)
    except E1LocalEdgePlasticityError as exc:
        raise E1E3StateArmsError(str(exc)) from exc
    initial_bindings = _bindings(initial_state)
    rate = initial_state.contract.release_rate_per_second
    current = copy.deepcopy(initial_state)
    previous_time = 0.0
    checkpoints = []
    for elapsed in E1_E3_RELEASE_TIMES_SECONDS:
        if elapsed > previous_time:
            try:
                current = advance_e1_local_edge_plasticity(
                    uniform_field.layer, current, elapsed - previous_time
                )
            except E1LocalEdgePlasticityError as exc:
                raise E1E3StateArmsError(str(exc)) from exc
        expected = initial_bindings * math.exp(-rate * elapsed)
        error = float(np.max(np.abs(_bindings(current) - expected)))
        checkpoints.append(E1ReleaseCheckpoint(elapsed, current, error))
        previous_time = elapsed
    return tuple(checkpoints)


def _position_ids(field: SharedMCMField) -> tuple[str, ...]:
    ordered = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    if len(ordered) != 3 or len(field.docks) != 1:
        raise E1E3StateArmsError("E3 state arms require one dock and three neurons")
    return tuple(item.neuron_id for item in ordered)


def _right_distribution(
    field: SharedMCMField,
    position_ids: tuple[str, ...],
    index: int,
) -> tuple[ReceptorDistribution, MCMFieldStepTime]:
    dock = field.docks[0]
    value_by_neuron = dict(zip(position_ids, _RIGHT_CONTACT, strict=True))
    neuron_by_carrier = dict(dock.dock_map.pairs)
    start = index * E1_E3_TICKS_PER_INTERVAL
    end = start + E1_E3_TICKS_PER_INTERVAL
    frame = ReceptorContactFrame(
        modality_id=dock.dock_map.modality_id,
        geometry_id=dock.dock_map.receptor_geometry_id,
        snapshot_id=f"e1.e3.compete.{index}",
        clock_id="e1.e3.source",
        window_start_tick=start,
        window_end_tick=end,
        carrier_ids=dock.dock_map.carrier_ids,
        values=tuple(
            value_by_neuron[neuron_by_carrier[carrier_id]]
            for carrier_id in dock.dock_map.carrier_ids
        ),
    )
    return (
        ReceptorDistribution(
            CommonFieldTime("e1.e3.organism", start, end),
            (DistributedReceptorContact(dock.dock_id, frame),),
        ),
        MCMFieldStepTime("e1.e3.organism", start, end, E1_E3_TICKS_PER_SECOND),
    )


def _run_competing_arm(
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
) -> tuple[SharedMCMField, E1LocalEdgePlasticityState]:
    return produce_e1_competing_checkpoints(
        initial_field,
        initial_state,
        substrate_config,
        afterimage_config,
        dissipation_config,
    )[-1]


def produce_e1_competing_checkpoints(
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> tuple[tuple[SharedMCMField, E1LocalEdgePlasticityState], ...]:
    """Return the eight existing right-contact states instead of only C8."""

    field = copy.deepcopy(initial_field)
    state = copy.deepcopy(initial_state)
    position_ids = _position_ids(field)
    checkpoints = []
    try:
        for index in range(E1_E3_COMPETING_INTERVALS):
            distribution, interval = _right_distribution(field, position_ids, index)
            result = advance_e1_coupled_fast_shared_field(
                field,
                state,
                distribution,
                interval,
                substrate_config,
                afterimage_config,
                dissipation_config,
                backreaction_enabled=False,
            )
            field, state = result.field, result.e1_state
            checkpoints.append((field, state))
    except E1CoupledFastFieldError as exc:
        raise E1E3StateArmsError(str(exc)) from exc
    return tuple(checkpoints)


def build_e1_e3_state_arms(
    fresh_uniform_field: SharedMCMField,
    left_history_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> E1E3StateArmsResult:
    """Build HOLD, RELEASE, COMPETE, and NEUTRAL without the later probe."""

    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise E1E3StateArmsError("state arms require one substrate configuration")
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise E1E3StateArmsError("state arms require one afterimage configuration")
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise E1E3StateArmsError("state arms dissipation configuration is invalid")
    if fresh_uniform_field.last_distribution is not None or fresh_uniform_field.layer.tick != 0:
        raise E1E3StateArmsError("state arms require one fresh unadvanced field")
    checkpoints = produce_e1_uniform_release_checkpoints(
        fresh_uniform_field, left_history_state
    )
    hold = copy.deepcopy(left_history_state)
    release = checkpoints[2].state
    compete_field, compete = _run_competing_arm(
        fresh_uniform_field,
        release,
        substrate_config,
        afterimage_config,
        dissipation_config,
    )
    neutral_initial = build_neutral_e1_state(
        fresh_uniform_field.layer, left_history_state.contract
    )
    neutral_field, neutral = _run_competing_arm(
        fresh_uniform_field,
        neutral_initial,
        substrate_config,
        afterimage_config,
        dissipation_config,
    )
    all_states = (hold, *(item.state for item in checkpoints), compete, neutral)
    budget_error = max(
        _resource_budget_error(fresh_uniform_field, state) for state in all_states
    )
    metrics = E1E3StateArmMetrics(
        release_analytic_linf=max(item.analytic_linf for item in checkpoints),
        resource_budget_linf=budget_error,
        release_total_binding_drop=_total_binding(hold) - _total_binding(release),
        compete_release_binding_linf=_linf(compete, release),
        compete_total_binding_rebound=_total_binding(compete) - _total_binding(release),
        compete_neutral_binding_linf=_linf(compete, neutral),
    )
    return E1E3StateArmsResult(
        hold,
        checkpoints,
        release,
        compete_field,
        compete,
        neutral_field,
        neutral,
        metrics,
    )


def evaluate_e1_e3_state_arms(result: E1E3StateArmsResult) -> str:
    """Evaluate readiness for the later probe, not the final E3 result."""

    if not isinstance(result, E1E3StateArmsResult):
        raise E1E3StateArmsError("state-arm evaluation requires one complete result")
    m = result.metrics
    if (
        m.release_analytic_linf > E1_E3_ABSOLUTE_TOLERANCE
        or m.resource_budget_linf > E1_E3_ABSOLUTE_TOLERANCE
        or m.release_total_binding_drop <= E1_E3_ABSOLUTE_TOLERANCE
    ):
        return "INVALID_E3_STATE_ARMS"
    if (
        m.compete_release_binding_linf > E1_E3_ABSOLUTE_TOLERANCE
        and m.compete_total_binding_rebound > E1_E3_ABSOLUTE_TOLERANCE
    ):
        return "E3_STATE_ARMS_READY_FOR_PROBE"
    return "NO_RESOURCE_REUSE_IN_FIRST_CORRIDOR"
