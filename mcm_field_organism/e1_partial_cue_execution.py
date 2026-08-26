"""Private S1-CP world arms and result roles without a real cue run."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import math
from typing import Mapping

from .e1_e3_state_arms import produce_e1_uniform_release_checkpoints
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_mirrored_history import produce_e1_mirrored_histories
from .e1_partial_cue_contract import (
    E1PartialCueContract,
    S1_CO_DECISIONS,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1PartialCueExecutionError(ValueError):
    """Raised when an S1-CP technical role leaves the S1-CO contract."""


S1_CP_CUE_IDS = ("left-full", "right-full", "left-partial", "right-partial")


def _finite_tuple(values: object, role: str) -> tuple[float, float, float]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise E1PartialCueExecutionError(f"{role} must be numeric") from exc
    if len(result) != 3 or any(not math.isfinite(value) for value in result):
        raise E1PartialCueExecutionError(f"{role} must contain three finite values")
    return result


def _vector(observation: "E1PartialCueObservation") -> tuple[float, ...]:
    return observation.delta_s + observation.delta_h


def _control_vector(observation: "E1PartialCueObservation") -> tuple[float, ...]:
    return observation.control_delta_s + observation.control_delta_h


def _subtract(first: tuple[float, ...], second: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(a - b for a, b in zip(first, second, strict=True))


def _add(first: tuple[float, ...], second: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(a + b for a, b in zip(first, second, strict=True))


def _scale(values: tuple[float, ...], factor: float) -> tuple[float, ...]:
    return tuple(factor * value for value in values)


def _mirror(values: tuple[float, ...]) -> tuple[float, ...]:
    if len(values) != 6:
        raise E1PartialCueExecutionError("partial-cue mirror requires six S/H values")
    return tuple(reversed(values[:3])) + tuple(reversed(values[3:]))


def _linf(values: tuple[float, ...]) -> float:
    return max(abs(value) for value in values)


@dataclass(frozen=True, slots=True)
class E1PartialCueWorldArms:
    """Three slow states after mirrored H8 histories and the fixed G4 gap."""

    left_g4_state: E1LocalEdgePlasticityState
    right_g4_state: E1LocalEdgePlasticityState
    neutral_state: E1LocalEdgePlasticityState
    maximum_mirror_binding_error: float

    def __post_init__(self) -> None:
        for role in ("left_g4_state", "right_g4_state", "neutral_state"):
            if not isinstance(getattr(self, role), E1LocalEdgePlasticityState):
                raise E1PartialCueExecutionError(f"{role} must be one E1 state")
        error = float(self.maximum_mirror_binding_error)
        if not math.isfinite(error) or error < 0.0:
            raise E1PartialCueExecutionError("mirror binding error must be nonnegative")
        object.__setattr__(self, "maximum_mirror_binding_error", error)


@dataclass(frozen=True, slots=True)
class E1PartialCueObservation:
    """One injected signed S/H effect and its n=2 control effect."""

    model_id: str
    history_id: str
    cue_id: str
    delta_s: tuple[float, float, float]
    delta_h: tuple[float, float, float]
    control_delta_s: tuple[float, float, float]
    control_delta_h: tuple[float, float, float]
    schedule_matches: bool
    invariants_hold: bool

    def __post_init__(self) -> None:
        if self.model_id not in ("e1", "p0", "b1-static-h8"):
            raise E1PartialCueExecutionError("unknown partial-cue model")
        if self.history_id not in ("left-g4", "right-g4", "neutral"):
            raise E1PartialCueExecutionError("unknown partial-cue history")
        if self.cue_id not in S1_CP_CUE_IDS:
            raise E1PartialCueExecutionError("unknown partial-cue identity")
        for role in ("delta_s", "delta_h", "control_delta_s", "control_delta_h"):
            object.__setattr__(self, role, _finite_tuple(getattr(self, role), role))
        if not isinstance(self.schedule_matches, bool) or not isinstance(
            self.invariants_hold, bool
        ):
            raise E1PartialCueExecutionError("partial-cue controls must be boolean")


@dataclass(frozen=True, slots=True)
class E1PartialCueMetrics:
    partial_history_cue_interaction_linf: float
    full_history_cue_interaction_linf: float
    partial_full_direction_dot: float
    p0_interaction_linf: float
    b1_static_interaction_linf: float
    crossed_history_linf: float
    mirror_error_linf: float
    relative_refinement_linf: float

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            value = float(getattr(self, name))
            if not math.isfinite(value) or (name != "partial_full_direction_dot" and value < 0.0):
                raise E1PartialCueExecutionError(f"{name} is invalid")
            object.__setattr__(self, name, value)


@dataclass(frozen=True, slots=True)
class E1PartialCueRunResult:
    """Complete raw S1-CP observation matrix without embedded decision."""

    contract_digest: str
    observations: tuple[E1PartialCueObservation, ...]
    metrics: E1PartialCueMetrics
    controls_hold: bool

    def __post_init__(self) -> None:
        if not isinstance(self.contract_digest, str) or len(self.contract_digest) != 64:
            raise E1PartialCueExecutionError("partial-cue result needs a contract digest")
        if not isinstance(self.metrics, E1PartialCueMetrics):
            raise E1PartialCueExecutionError("partial-cue result needs metrics")
        if not isinstance(self.controls_hold, bool):
            raise E1PartialCueExecutionError("controls_hold must be boolean")
        object.__setattr__(self, "observations", tuple(self.observations))


def build_e1_partial_cue_world_arms(
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1PartialCueWorldArms:
    """Build mirrored G4 states only; do not apply any partial or full cue."""

    history = produce_e1_mirrored_histories(
        initial_field, initial_state, substrate_config, afterimage_config
    )
    left = produce_e1_uniform_release_checkpoints(
        initial_field, history.left_e1_state
    )[2].state
    right = produce_e1_uniform_release_checkpoints(
        initial_field, history.right_e1_state
    )[2].state
    left_values = tuple(item.binding for item in left.edge_bindings)
    right_values = tuple(item.binding for item in right.edge_bindings)
    mirror_error = max(
        abs(a - b) for a, b in zip(left_values, reversed(right_values), strict=True)
    )
    return E1PartialCueWorldArms(
        left,
        right,
        copy.deepcopy(initial_state),
        mirror_error,
    )


def _expected_keys(contract: E1PartialCueContract) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (model_id, history_id, cue_id)
        for model_id in contract.model_arms
        for history_id in contract.history_arms
        for cue_id in S1_CP_CUE_IDS
    )


def _interaction(
    by_key: Mapping[tuple[str, str, str], E1PartialCueObservation],
    model_id: str,
    level: str,
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    left = _subtract(
        _vector(by_key[(model_id, "left-g4", f"left-{level}")]),
        _vector(by_key[(model_id, "right-g4", f"left-{level}")]),
    )
    right = _mirror(
        _subtract(
            _vector(by_key[(model_id, "right-g4", f"right-{level}")]),
            _vector(by_key[(model_id, "left-g4", f"right-{level}")]),
        )
    )
    return _scale(_add(left, right), 0.5), left, right


def compose_e1_partial_cue_result(
    contract: E1PartialCueContract,
    observations: Mapping[tuple[str, str, str], E1PartialCueObservation],
) -> E1PartialCueRunResult:
    """Compose injected observations without executing a world or cue runner."""

    if not isinstance(contract, E1PartialCueContract):
        raise E1PartialCueExecutionError("partial-cue composition requires its contract")
    keys = _expected_keys(contract)
    if set(observations) != set(keys) or len(observations) != len(keys):
        raise E1PartialCueExecutionError("partial-cue observation matrix is incomplete")
    ordered = tuple(observations[key] for key in keys)
    if any((item.model_id, item.history_id, item.cue_id) != key for key, item in zip(keys, ordered, strict=True)):
        raise E1PartialCueExecutionError("partial-cue observation identity changed")
    by_key = dict(zip(keys, ordered, strict=True))
    partial, partial_left, partial_right = _interaction(by_key, "e1", "partial")
    full, _, _ = _interaction(by_key, "e1", "full")
    p0, _, _ = _interaction(by_key, "p0", "partial")
    b1, _, _ = _interaction(by_key, "b1-static-h8", "partial")
    refinements = []
    for item in ordered:
        primary = _vector(item)
        control = _control_vector(item)
        scale = _linf(primary)
        residual = _linf(_subtract(primary, control))
        refinements.append(0.0 if scale == 0.0 and residual == 0.0 else residual / scale if scale > 0.0 else math.inf)
    metrics = E1PartialCueMetrics(
        partial_history_cue_interaction_linf=_linf(partial),
        full_history_cue_interaction_linf=_linf(full),
        partial_full_direction_dot=math.fsum(a * b for a, b in zip(partial, full, strict=True)),
        p0_interaction_linf=_linf(p0),
        b1_static_interaction_linf=_linf(b1),
        crossed_history_linf=max(_linf(partial_left), _linf(partial_right)),
        mirror_error_linf=_linf(_subtract(partial_left, partial_right)),
        relative_refinement_linf=max(refinements),
    )
    controls = all(item.schedule_matches and item.invariants_hold for item in ordered)
    return E1PartialCueRunResult(contract.digest(), ordered, metrics, controls)


def evaluate_e1_partial_cue_result(
    contract: E1PartialCueContract,
    result: E1PartialCueRunResult,
) -> str:
    """Apply only the fixed S1-CO technical decision order."""

    if (
        not isinstance(result, E1PartialCueRunResult)
        or result.contract_digest != contract.digest()
    ):
        raise E1PartialCueExecutionError("partial-cue result contract changed")
    metric = result.metrics
    if (
        not result.controls_hold
        or metric.relative_refinement_linf > contract.relative_refinement_limit
        or metric.mirror_error_linf > contract.absolute_tolerance
    ):
        return S1_CO_DECISIONS[0]
    numerical_floor = max(
        contract.absolute_tolerance,
        metric.relative_refinement_linf * metric.full_history_cue_interaction_linf,
    )
    if metric.partial_history_cue_interaction_linf <= numerical_floor:
        return S1_CO_DECISIONS[1]
    baseline_floor = max(metric.p0_interaction_linf, metric.b1_static_interaction_linf)
    if metric.partial_history_cue_interaction_linf <= baseline_floor + numerical_floor:
        return S1_CO_DECISIONS[2]
    if metric.partial_full_direction_dot > 0.0 and metric.crossed_history_linf > numerical_floor:
        return S1_CO_DECISIONS[3]
    return S1_CO_DECISIONS[1]
