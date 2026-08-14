"""Pure W7-P measurement composition without field-path execution."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from .w7m_capacity_function_matrix import (
    W7MBaselineSpec,
    W7MCapacityFunctionMatrixAdapter,
)
from .w7n_capacity_function_baselines import (
    advance_w7n_local_baseline,
    build_zero_w7n_local_baseline,
)
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamilyError,
    authorize_w7w_source_segment,
)


class W7PMeasurementCompositorError(ValueError):
    """Raised when field and observer measurement roles are mixed."""


FIELD_MODEL_IDS = frozenset(
    {"cap", "p0", "lin", "f3", "const-v", "mob", "eta0", "kappa0", "sign"}
)
OBSERVER_MODEL_IDS = frozenset({"leak", "sat", "norm"})
FIELD_MEASUREMENT_NAMES = (
    "probe_S_linf",
    "probe_H_linf",
    "probe_SH_trajectory_l2",
    "probe_observation_ticks",
)
OBSERVER_MEASUREMENT_NAMES = (
    "observer_output_linf",
    "observer_output_trajectory_l2",
    "observer_state_linf",
    "observer_ticks",
)
OBSERVER_EXPLANATIONS = (
    "NOT_RESOLVED",
    "PROFILE_NOT_MATCHED",
    "PROFILE_EXPLAINED_BY_LEAK",
    "PROFILE_EXPLAINED_BY_SAT",
    "PROFILE_EXPLAINED_BY_NORM",
)
_OBSERVER_PRECEDENCE = ("leak", "sat", "norm")
_PROFILE_SURFACES = frozenset({"field", "observer"})
_PROFILE_DIRECTIONS = frozenset({"ab", "ba"})


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_vector(values, role: str, *, normalized: bool = False) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise W7PMeasurementCompositorError(
            f"{role} must contain numeric values"
        ) from exc
    if not result or any(not math.isfinite(value) for value in result):
        raise W7PMeasurementCompositorError(f"{role} must be nonempty and finite")
    if normalized and any(value < -1.0 or value > 1.0 for value in result):
        raise W7PMeasurementCompositorError(
            f"{role} left the normalized field domain"
        )
    return result


def _nonnegative(value: float, role: str) -> float:
    if isinstance(value, bool):
        raise W7PMeasurementCompositorError(f"{role} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise W7PMeasurementCompositorError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise W7PMeasurementCompositorError(
            f"{role} must be finite and nonnegative"
        )
    return result


def _ticks(values, role: str) -> tuple[int, ...]:
    result = tuple(values)
    if (
        not result
        or any(isinstance(value, bool) or not isinstance(value, int) for value in result)
        or tuple(sorted(set(result))) != result
    ):
        raise W7PMeasurementCompositorError(
            f"{role} must contain unique increasing integer ticks"
        )
    return result


@dataclass(frozen=True, slots=True)
class W7PCompletedP0SSample:
    """One already computed P0-S state at an atomic completion boundary."""

    completion_tick: int
    s_values: tuple[float, ...]

    def __post_init__(self) -> None:
        if (
            isinstance(self.completion_tick, bool)
            or not isinstance(self.completion_tick, int)
            or self.completion_tick < 0
        ):
            raise W7PMeasurementCompositorError(
                "P0-S completion_tick must be a nonnegative integer"
            )
        object.__setattr__(
            self,
            "s_values",
            _finite_vector(self.s_values, "P0-S sample", normalized=True),
        )


@dataclass(frozen=True, slots=True)
class W7PObserverDriverSegment:
    """One left-held P0-S segment shared by every observer model."""

    start_tick: int
    end_tick: int
    s_values: tuple[float, ...]

    def __post_init__(self) -> None:
        if (
            isinstance(self.start_tick, bool)
            or isinstance(self.end_tick, bool)
            or not isinstance(self.start_tick, int)
            or not isinstance(self.end_tick, int)
            or self.start_tick < 0
            or self.end_tick <= self.start_tick
        ):
            raise W7PMeasurementCompositorError(
                "observer driver segments must have positive ordered ticks"
            )
        object.__setattr__(
            self,
            "s_values",
            _finite_vector(self.s_values, "observer driver S", normalized=True),
        )


@dataclass(frozen=True, slots=True)
class W7PObserverDriver:
    """Canonical model-independent P0-S driver bound to W7-M inputs."""

    matrix_digest: str
    source_digest: str
    clock_id: str
    ticks_per_second: float
    neuron_ids: tuple[str, ...]
    segments: tuple[W7PObserverDriverSegment, ...]
    terminal_s_values: tuple[float, ...]
    driver_digest: str

    def __post_init__(self) -> None:
        if not self.matrix_digest or not self.source_digest or not self.clock_id:
            raise W7PMeasurementCompositorError(
                "observer driver bindings must be nonempty"
            )
        rate = _nonnegative(self.ticks_per_second, "ticks_per_second")
        if rate == 0.0:
            raise W7PMeasurementCompositorError(
                "ticks_per_second must be greater than zero"
            )
        object.__setattr__(self, "ticks_per_second", rate)
        neuron_ids = tuple(self.neuron_ids)
        if not neuron_ids or len(set(neuron_ids)) != len(neuron_ids):
            raise W7PMeasurementCompositorError(
                "observer driver neuron identities must be unique"
            )
        segments = tuple(self.segments)
        if not segments:
            raise W7PMeasurementCompositorError(
                "observer driver requires at least one segment"
            )
        if any(len(item.s_values) != len(neuron_ids) for item in segments):
            raise W7PMeasurementCompositorError(
                "observer driver vectors must match field locations"
            )
        for previous, current in zip(segments, segments[1:]):
            if previous.end_tick != current.start_tick:
                raise W7PMeasurementCompositorError(
                    "observer driver segments must be contiguous"
                )
        terminal = _finite_vector(
            self.terminal_s_values,
            "observer driver terminal S",
            normalized=True,
        )
        if len(terminal) != len(neuron_ids):
            raise W7PMeasurementCompositorError(
                "observer driver terminal S must match field locations"
            )
        object.__setattr__(self, "neuron_ids", neuron_ids)
        object.__setattr__(self, "segments", segments)
        object.__setattr__(self, "terminal_s_values", terminal)
        if self.driver_digest != _observer_driver_digest(self):
            raise W7PMeasurementCompositorError(
                "observer driver digest does not match its content"
            )


def _observer_driver_digest(driver: W7PObserverDriver) -> str:
    return _digest(
        {
            "matrix_digest": driver.matrix_digest,
            "source_digest": driver.source_digest,
            "clock_id": driver.clock_id,
            "ticks_per_second": driver.ticks_per_second,
            "neuron_ids": driver.neuron_ids,
            "segments": [
                {
                    "start_tick": item.start_tick,
                    "end_tick": item.end_tick,
                    "s_values": item.s_values,
                }
                for item in driver.segments
            ],
            "terminal_s_values": driver.terminal_s_values,
        }
    )


def _source_digests(adapter: W7MCapacityFunctionMatrixAdapter) -> frozenset[str]:
    source = adapter.source
    return frozenset(
        (source.contact_a_digest,)
        + source.contact_b_step_digests
        + source.interruption_step_digests
        + source.probe_digests
    )


def compose_w7p_observer_driver(
    adapter: W7MCapacityFunctionMatrixAdapter,
    source_digest: str,
    interval: tuple[int, int],
    initial_s_values,
    completed_s_samples,
    *,
    source_path_id: str | None = None,
    source_authorization: W7WSourceAuthorization | None = None,
) -> W7PObserverDriver:
    """Compose left-held segments from precomputed P0-S completion states."""

    if not isinstance(adapter, W7MCapacityFunctionMatrixAdapter):
        raise W7PMeasurementCompositorError(
            "W7-P driver requires one frozen W7-M adapter"
        )
    try:
        start_tick, end_tick = interval
    except (TypeError, ValueError) as exc:
        raise W7PMeasurementCompositorError(
            "observer driver interval must contain two ticks"
        ) from exc
    if (
        isinstance(start_tick, bool)
        or isinstance(end_tick, bool)
        or not isinstance(start_tick, int)
        or not isinstance(end_tick, int)
        or start_tick < 0
        or end_tick <= start_tick
    ):
        raise W7PMeasurementCompositorError(
            "observer driver interval must be positive and ordered"
        )
    if source_digest not in _source_digests(adapter):
        if source_path_id is None or source_authorization is None:
            raise W7PMeasurementCompositorError(
                "observer driver source digest is not bound by W7-M"
            )
        try:
            authorize_w7w_source_segment(
                adapter,
                source_authorization,
                source_digest,
                source_path_id,
                (start_tick, end_tick),
            )
        except W7WSymmetricSourceFamilyError as exc:
            raise W7PMeasurementCompositorError(str(exc)) from exc
    neuron_ids = tuple(neuron.neuron_id for neuron in adapter.initial_field.layer.neurons)
    initial = _finite_vector(initial_s_values, "initial P0-S", normalized=True)
    if len(initial) != len(neuron_ids):
        raise W7PMeasurementCompositorError(
            "initial P0-S must match every W7-M field location"
        )
    samples = tuple(completed_s_samples)
    if any(not isinstance(item, W7PCompletedP0SSample) for item in samples):
        raise W7PMeasurementCompositorError(
            "observer driver accepts only completed P0-S samples"
        )
    sample_ticks = tuple(item.completion_tick for item in samples)
    if sample_ticks != tuple(sorted(set(sample_ticks))):
        raise W7PMeasurementCompositorError(
            "P0-S completion samples must be atomic, unique, and ordered"
        )
    if any(
        not (start_tick < item.completion_tick <= end_tick)
        or len(item.s_values) != len(neuron_ids)
        for item in samples
    ):
        raise W7PMeasurementCompositorError(
            "P0-S completion samples must stay inside the bound interval"
        )
    segments = []
    cursor = start_tick
    held = initial
    for sample in samples:
        if cursor < sample.completion_tick:
            segments.append(W7PObserverDriverSegment(cursor, sample.completion_tick, held))
        cursor = sample.completion_tick
        held = sample.s_values
    if cursor < end_tick:
        segments.append(W7PObserverDriverSegment(cursor, end_tick, held))
    if not segments:
        raise W7PMeasurementCompositorError(
            "observer driver has no positive-duration segment"
        )
    provisional = W7PObserverDriver.__new__(W7PObserverDriver)
    values = {
        "matrix_digest": adapter.matrix_digest,
        "source_digest": source_digest,
        "clock_id": adapter.source.clock_id,
        "ticks_per_second": adapter.source.ticks_per_second,
        "neuron_ids": neuron_ids,
        "segments": tuple(segments),
        "terminal_s_values": held,
    }
    for name, value in values.items():
        object.__setattr__(provisional, name, value)
    digest = _observer_driver_digest(provisional)
    return W7PObserverDriver(**values, driver_digest=digest)


@dataclass(frozen=True, slots=True)
class W7PFieldMeasurement:
    """One field-only probe record; it cannot contain observer values."""

    model_id: str
    path_id: str
    checkpoint: int
    probe_S_linf: float
    probe_H_linf: float
    probe_SH_trajectory_l2: float
    probe_observation_ticks: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.model_id not in FIELD_MODEL_IDS:
            raise W7PMeasurementCompositorError(
                "field measurement requires a causal field model"
            )
        if self.path_id not in {"ab", "ag", "ba", "bg", "ua", "ub", "ug"}:
            raise W7PMeasurementCompositorError("unknown W7-M field path")
        if (
            isinstance(self.checkpoint, bool)
            or not isinstance(self.checkpoint, int)
            or self.checkpoint not in range(5)
        ):
            raise W7PMeasurementCompositorError(
                "field checkpoint must be between zero and four"
            )
        for role in (
            "probe_S_linf",
            "probe_H_linf",
            "probe_SH_trajectory_l2",
        ):
            object.__setattr__(self, role, _nonnegative(getattr(self, role), role))
        object.__setattr__(
            self,
            "probe_observation_ticks",
            _ticks(self.probe_observation_ticks, "probe_observation_ticks"),
        )


@dataclass(frozen=True, slots=True)
class W7PObserverMeasurement:
    """One observer-only record driven by the common P0-S trace."""

    model_id: str
    driver_digest: str
    observer_output_linf: float
    observer_output_trajectory_l2: float
    observer_state_linf: float
    observer_ticks: tuple[int, ...]
    observer_output_trace: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        if self.model_id not in OBSERVER_MODEL_IDS:
            raise W7PMeasurementCompositorError(
                "observer measurement requires LEAK, SAT, or NORM"
            )
        if not self.driver_digest:
            raise W7PMeasurementCompositorError(
                "observer measurement requires one driver digest"
            )
        for role in (
            "observer_output_linf",
            "observer_output_trajectory_l2",
            "observer_state_linf",
        ):
            object.__setattr__(self, role, _nonnegative(getattr(self, role), role))
        ticks = _ticks(self.observer_ticks, "observer_ticks")
        trace = tuple(
            _finite_vector(item, "observer output trace")
            for item in self.observer_output_trace
        )
        if len(trace) != len(ticks) or len({len(item) for item in trace}) != 1:
            raise W7PMeasurementCompositorError(
                "observer trace must contain one equal-size vector per tick"
            )
        object.__setattr__(self, "observer_ticks", ticks)
        object.__setattr__(self, "observer_output_trace", trace)


@dataclass(frozen=True, slots=True)
class W7PCapacityMeasurement:
    """CAP-only M and free-capacity record."""

    model_id: str
    total_mass: float
    total_free_capacity: float
    balance_residual: float

    def __post_init__(self) -> None:
        if self.model_id != "cap":
            raise W7PMeasurementCompositorError(
                "only CAP may expose M and free-capacity measurements"
            )
        object.__setattr__(self, "total_mass", _nonnegative(self.total_mass, "total_mass"))
        object.__setattr__(
            self,
            "total_free_capacity",
            _nonnegative(self.total_free_capacity, "total_free_capacity"),
        )
        object.__setattr__(
            self,
            "balance_residual",
            _nonnegative(self.balance_residual, "balance_residual"),
        )


def compose_w7p_observer_measurement(
    spec: W7MBaselineSpec,
    driver: W7PObserverDriver,
) -> W7PObserverMeasurement:
    """Apply one pure W7-N observer kernel to the shared driver."""

    if not isinstance(spec, W7MBaselineSpec) or spec.model_id not in OBSERVER_MODEL_IDS:
        raise W7PMeasurementCompositorError(
            "observer composition requires a frozen observer specification"
        )
    if not isinstance(driver, W7PObserverDriver):
        raise W7PMeasurementCompositorError(
            "observer composition requires one canonical driver"
        )
    state = build_zero_w7n_local_baseline(spec, len(driver.neuron_ids))
    trace = []
    ticks = []
    for segment in driver.segments:
        result = advance_w7n_local_baseline(
            spec,
            state,
            segment.s_values,
            (segment.end_tick - segment.start_tick) / driver.ticks_per_second,
        )
        state = result.state
        trace.append(result.output)
        ticks.append(segment.end_tick)
    output_linf = max(abs(value) for row in trace for value in row)
    trajectory_l2 = math.sqrt(math.fsum(value * value for row in trace for value in row))
    state_linf = max(abs(value) for value in state.latent)
    return W7PObserverMeasurement(
        model_id=spec.model_id,
        driver_digest=driver.driver_digest,
        observer_output_linf=output_linf,
        observer_output_trajectory_l2=trajectory_l2,
        observer_state_linf=state_linf,
        observer_ticks=tuple(ticks),
        observer_output_trace=tuple(trace),
    )


@dataclass(frozen=True, slots=True)
class W7PLifecycleProfile:
    """Dimensionless profile on exactly one measurement surface."""

    measurement_surface: str
    model_id: str
    direction: str
    resolution: str
    old_b_retention: tuple[float, ...]
    old_g_retention: tuple[float, ...]
    new_b_gain: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.measurement_surface not in _PROFILE_SURFACES:
            raise W7PMeasurementCompositorError("unknown profile surface")
        allowed = (
            FIELD_MODEL_IDS
            if self.measurement_surface == "field"
            else OBSERVER_MODEL_IDS
        )
        if self.model_id not in allowed:
            raise W7PMeasurementCompositorError(
                "profile model and measurement surface differ"
            )
        if self.direction not in _PROFILE_DIRECTIONS:
            raise W7PMeasurementCompositorError("profile direction must be ab or ba")
        if self.resolution not in {"RESOLVED", "NOT_RESOLVED"}:
            raise W7PMeasurementCompositorError("unknown profile resolution")
        curves = (
            tuple(self.old_b_retention),
            tuple(self.old_g_retention),
            tuple(self.new_b_gain),
        )
        if self.resolution == "NOT_RESOLVED":
            if any(curves):
                raise W7PMeasurementCompositorError(
                    "unresolved profiles must not contain epsilon-rescued curves"
                )
            return
        if any(not curve for curve in curves) or len({len(curve) for curve in curves}) != 1:
            raise W7PMeasurementCompositorError(
                "resolved lifecycle curves must be nonempty and equally sized"
            )
        if any(not math.isfinite(value) for curve in curves for value in curve):
            raise W7PMeasurementCompositorError(
                "resolved lifecycle curves must be finite"
            )


def compose_w7p_lifecycle_profile(
    measurement_surface: str,
    model_id: str,
    direction: str,
    old_b_effect,
    old_g_effect,
    new_b_effect,
    numerical_floor: float,
) -> W7PLifecycleProfile:
    """Normalize one model by its own initial resolved effect, without epsilon."""

    old_b = tuple(_nonnegative(value, "old_b_effect") for value in old_b_effect)
    old_g = tuple(_nonnegative(value, "old_g_effect") for value in old_g_effect)
    new_b = tuple(_nonnegative(value, "new_b_effect") for value in new_b_effect)
    if not old_b or not old_g or not new_b or len({len(old_b), len(old_g), len(new_b)}) != 1:
        raise W7PMeasurementCompositorError(
            "lifecycle effects must be nonempty and equally sized"
        )
    floor = _nonnegative(numerical_floor, "numerical_floor")
    denominator = old_b[0]
    if denominator <= floor:
        return W7PLifecycleProfile(
            measurement_surface,
            model_id,
            direction,
            "NOT_RESOLVED",
            (),
            (),
            (),
        )
    return W7PLifecycleProfile(
        measurement_surface,
        model_id,
        direction,
        "RESOLVED",
        tuple(value / denominator for value in old_b),
        tuple(value / denominator for value in old_g),
        tuple(value / denominator for value in new_b),
    )


def select_w7p_observer_explanation(
    *,
    profile_resolved: bool,
    matched_model_ids,
) -> str:
    """Apply the preregistered LEAK, SAT, NORM precedence."""

    if not isinstance(profile_resolved, bool):
        raise W7PMeasurementCompositorError("profile_resolved must be boolean")
    matches = tuple(matched_model_ids)
    if len(set(matches)) != len(matches) or any(
        item not in OBSERVER_MODEL_IDS for item in matches
    ):
        raise W7PMeasurementCompositorError(
            "observer matches must be unique observer model identities"
        )
    if not profile_resolved:
        return "NOT_RESOLVED"
    for model_id in _OBSERVER_PRECEDENCE:
        if model_id in matches:
            return f"PROFILE_EXPLAINED_BY_{model_id.upper()}"
    return "PROFILE_NOT_MATCHED"
