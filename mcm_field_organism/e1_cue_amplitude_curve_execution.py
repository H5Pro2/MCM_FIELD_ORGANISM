"""Private S1-CV amplitude runner and synthetic curve result core."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

from .e1_cue_amplitude_curve_contract import (
    E1CueAmplitudeCurveContract,
    S1_CU_DECISIONS,
)
from .e1_partial_cue_runners import (
    E1PartialCueRunnerInputs,
    _advance_partition,
    _difference,
    _position_ids,
    _values,
)
from .e1_weighted_field_adapter import compute_e1_weighted_edge_rates
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1CueAmplitudeCurveExecutionError(ValueError):
    """Raised when an S1-CV execution role leaves the S1-CU contract."""


@dataclass(frozen=True, slots=True)
class E1CueAmplitudeObservation:
    model_id: str
    history_id: str
    cue_side: str
    amplitude: float
    delta_s: tuple[float, float, float]
    delta_h: tuple[float, float, float]
    control_delta_s: tuple[float, float, float]
    control_delta_h: tuple[float, float, float]
    schedule_matches: bool
    invariants_hold: bool

    def __post_init__(self) -> None:
        amplitude = float(self.amplitude)
        if not math.isfinite(amplitude) or amplitude <= 0.0:
            raise E1CueAmplitudeCurveExecutionError("cue amplitude must be positive")
        object.__setattr__(self, "amplitude", amplitude)
        for role in ("delta_s", "delta_h", "control_delta_s", "control_delta_h"):
            values = tuple(float(value) for value in getattr(self, role))
            if len(values) != 3 or any(not math.isfinite(value) for value in values):
                raise E1CueAmplitudeCurveExecutionError(f"{role} must be finite")
            object.__setattr__(self, role, values)
        if not isinstance(self.schedule_matches, bool) or not isinstance(
            self.invariants_hold, bool
        ):
            raise E1CueAmplitudeCurveExecutionError("curve controls must be boolean")


@dataclass(frozen=True, slots=True)
class E1CueAmplitudeCurveMetrics:
    interaction_linf_by_amplitude: tuple[tuple[float, float], ...]
    linear_residual_linf_by_amplitude: tuple[tuple[float, float], ...]
    maximum_relative_linear_residual: float
    p0_interaction_floor: float
    b1_static_interaction_floor: float
    mirror_error_linf: float
    relative_refinement_linf: float
    s1ct_anchor_error_linf: float

    def __post_init__(self) -> None:
        for role in (
            "maximum_relative_linear_residual",
            "p0_interaction_floor",
            "b1_static_interaction_floor",
            "mirror_error_linf",
            "relative_refinement_linf",
            "s1ct_anchor_error_linf",
        ):
            value = float(getattr(self, role))
            if not math.isfinite(value) or value < 0.0:
                raise E1CueAmplitudeCurveExecutionError(f"{role} is invalid")
            object.__setattr__(self, role, value)


@dataclass(frozen=True, slots=True)
class E1CueAmplitudeCurveResult:
    contract_digest: str
    observations: tuple[E1CueAmplitudeObservation, ...]
    metrics: E1CueAmplitudeCurveMetrics
    controls_hold: bool

    def __post_init__(self) -> None:
        if not isinstance(self.contract_digest, str) or len(self.contract_digest) != 64:
            raise E1CueAmplitudeCurveExecutionError("curve result needs contract digest")
        if len(tuple(self.observations)) != 72:
            raise E1CueAmplitudeCurveExecutionError("curve result needs 72 observations")
        if not isinstance(self.metrics, E1CueAmplitudeCurveMetrics):
            raise E1CueAmplitudeCurveExecutionError("curve result needs metrics")
        if not isinstance(self.controls_hold, bool):
            raise E1CueAmplitudeCurveExecutionError("controls_hold must be boolean")
        object.__setattr__(self, "observations", tuple(self.observations))


def _key(item: E1CueAmplitudeObservation) -> tuple[str, str, str, float]:
    return item.model_id, item.history_id, item.cue_side, item.amplitude


def _expected_keys(
    contract: E1CueAmplitudeCurveContract,
) -> tuple[tuple[str, str, str, float], ...]:
    return tuple(
        (model, history, side, amplitude)
        for model in contract.model_arms
        for history in contract.history_arms
        for side in contract.cue_sides
        for amplitude in contract.amplitudes
    )


def _vector(item: E1CueAmplitudeObservation) -> tuple[float, ...]:
    return item.delta_s + item.delta_h


def _control_vector(item: E1CueAmplitudeObservation) -> tuple[float, ...]:
    return item.control_delta_s + item.control_delta_h


def _subtract(first: tuple[float, ...], second: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(a - b for a, b in zip(first, second, strict=True))


def _mirror(values: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(reversed(values[:3])) + tuple(reversed(values[3:]))


def _linf(values: tuple[float, ...]) -> float:
    return max(abs(value) for value in values)


def _interaction(
    by_key: Mapping[tuple[str, str, str, float], E1CueAmplitudeObservation],
    model: str,
    amplitude: float,
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    left = _subtract(
        _vector(by_key[(model, "left-g4", "left", amplitude)]),
        _vector(by_key[(model, "right-g4", "left", amplitude)]),
    )
    right = _mirror(
        _subtract(
            _vector(by_key[(model, "right-g4", "right", amplitude)]),
            _vector(by_key[(model, "left-g4", "right", amplitude)]),
        )
    )
    average = tuple(0.5 * (a + b) for a, b in zip(left, right, strict=True))
    return average, left, right


def run_e1_cue_amplitude_observation(
    contract: E1CueAmplitudeCurveContract,
    initial_field: SharedMCMField,
    inputs: E1PartialCueRunnerInputs,
    model_id: str,
    history_id: str,
    cue_side: str,
    amplitude: float,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1CueAmplitudeObservation:
    """Run one amplitude arm only, never the 72-observation matrix."""

    _position_ids(initial_field)
    if (
        model_id not in contract.model_arms
        or history_id not in contract.history_arms
        or cue_side not in contract.cue_sides
        or amplitude not in contract.amplitudes
    ):
        raise E1CueAmplitudeCurveExecutionError("unknown amplitude arm")
    values = contract.cue(cue_side, amplitude)
    states = {
        "left-g4": inputs.world_arms.left_g4_state,
        "right-g4": inputs.world_arms.right_g4_state,
        "neutral": inputs.world_arms.neutral_state,
    }
    if model_id == "e1":
        adapter = compute_e1_weighted_edge_rates(
            initial_field.layer,
            states[history_id],
            substrate_config,
            backreaction_enabled=True,
        )
    elif model_id == "b1-static-h8":
        adapter = inputs.b1_static_h8_adapter
    else:
        adapter = None
    identity = f"s1-cv.{model_id}.{history_id}.{cue_side}.{amplitude}"
    p0_n2 = _advance_partition(initial_field, None, values, 2, identity + ".p0", contract, substrate_config, afterimage_config)
    p0_n4 = _advance_partition(initial_field, None, values, 4, identity + ".p0", contract, substrate_config, afterimage_config)
    active_n2 = _advance_partition(initial_field, adapter, values, 2, identity, contract, substrate_config, afterimage_config)
    active_n4 = _advance_partition(initial_field, adapter, values, 4, identity, contract, substrate_config, afterimage_config)
    return E1CueAmplitudeObservation(
        model_id,
        history_id,
        cue_side,
        amplitude,
        _difference(_values(active_n4, "activation"), _values(p0_n4, "activation")),
        _difference(_values(active_n4, "afterimage"), _values(p0_n4, "afterimage")),
        _difference(_values(active_n2, "activation"), _values(p0_n2, "activation")),
        _difference(_values(active_n2, "afterimage"), _values(p0_n2, "afterimage")),
        active_n2.layer.tick == 2 and active_n4.layer.tick == 4,
        initial_field.layer.tick == 0 and initial_field.last_distribution is None,
    )


def compose_e1_cue_amplitude_curve_result(
    contract: E1CueAmplitudeCurveContract,
    observations: Mapping[tuple[str, str, str, float], E1CueAmplitudeObservation],
) -> E1CueAmplitudeCurveResult:
    """Compose injected curve observations without running an arm."""

    keys = _expected_keys(contract)
    if set(observations) != set(keys) or len(observations) != 72:
        raise E1CueAmplitudeCurveExecutionError("amplitude matrix is incomplete")
    ordered = tuple(observations[key] for key in keys)
    if any(_key(item) != key for key, item in zip(keys, ordered, strict=True)):
        raise E1CueAmplitudeCurveExecutionError("amplitude observation identity changed")
    by_key = dict(zip(keys, ordered, strict=True))
    interactions = {}
    p0_floor = 0.0
    b1_floor = 0.0
    mirror_error = 0.0
    for amplitude in contract.amplitudes:
        interaction, left, right = _interaction(by_key, "e1", amplitude)
        interactions[amplitude] = interaction
        p0_floor = max(p0_floor, _linf(_interaction(by_key, "p0", amplitude)[0]))
        b1_floor = max(b1_floor, _linf(_interaction(by_key, "b1-static-h8", amplitude)[0]))
        mirror_error = max(mirror_error, _linf(_subtract(left, right)))
    full = interactions[1.0]
    full_scale = _linf(full)
    residuals = tuple(
        (
            amplitude,
            _linf(
                _subtract(
                    interactions[amplitude],
                    tuple(amplitude * value for value in full),
                )
            ),
        )
        for amplitude in contract.amplitudes
    )
    refinements = []
    for item in ordered:
        primary = _vector(item)
        control = _control_vector(item)
        scale = _linf(primary)
        residual = _linf(_subtract(primary, control))
        refinements.append(0.0 if scale == 0.0 and residual == 0.0 else residual / scale if scale > 0.0 else math.inf)
    metrics = E1CueAmplitudeCurveMetrics(
        interaction_linf_by_amplitude=tuple(
            (amplitude, _linf(interactions[amplitude]))
            for amplitude in contract.amplitudes
        ),
        linear_residual_linf_by_amplitude=residuals,
        maximum_relative_linear_residual=(
            max(value for _, value in residuals) / full_scale if full_scale > 0.0 else 0.0
        ),
        p0_interaction_floor=p0_floor,
        b1_static_interaction_floor=b1_floor,
        mirror_error_linf=mirror_error,
        relative_refinement_linf=max(refinements),
        s1ct_anchor_error_linf=abs(full_scale - contract.s1ct_full_interaction_linf),
    )
    controls = all(item.schedule_matches and item.invariants_hold for item in ordered)
    return E1CueAmplitudeCurveResult(contract.digest(), ordered, metrics, controls)


def evaluate_e1_cue_amplitude_curve_result(
    contract: E1CueAmplitudeCurveContract,
    result: E1CueAmplitudeCurveResult,
) -> str:
    """Apply only the fixed S1-CU technical decision order."""

    if result.contract_digest != contract.digest():
        raise E1CueAmplitudeCurveExecutionError("curve result contract changed")
    metric = result.metrics
    if (
        not result.controls_hold
        or metric.relative_refinement_linf > contract.relative_refinement_limit
        or metric.mirror_error_linf > contract.absolute_tolerance
        or metric.s1ct_anchor_error_linf > contract.absolute_tolerance
        or metric.p0_interaction_floor > contract.absolute_tolerance
        or metric.b1_static_interaction_floor > contract.absolute_tolerance
    ):
        return S1_CU_DECISIONS[0]
    full = dict(metric.interaction_linf_by_amplitude)[1.0]
    if full <= contract.absolute_tolerance:
        return S1_CU_DECISIONS[1]
    if metric.maximum_relative_linear_residual <= contract.relative_linearity_limit:
        return S1_CU_DECISIONS[2]
    return S1_CU_DECISIONS[3]
