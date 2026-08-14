"""Pure W7-T observer-state continuation across explicit P0-S segments."""

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
    W7NLocalBaselineState,
    advance_w7n_local_baseline,
    build_zero_w7n_local_baseline,
)
from .w7p_measurement_compositor import (
    OBSERVER_MODEL_IDS,
    W7PObserverDriver,
    W7PObserverMeasurement,
)
from .w7r_p0_s_completion_producer import W7RP0SProductionResult


class W7TObserverContinuationError(ValueError):
    """Raised when an observer continuation crosses model or path roles."""


_PATH_IDS = frozenset({"ab", "ag", "ba", "bg", "ua", "ub", "ug"})
_ZERO_START = "w7t.zero-start.v1"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _specification(
    adapter: W7MCapacityFunctionMatrixAdapter,
    model_id: str,
) -> W7MBaselineSpec:
    if not isinstance(adapter, W7MCapacityFunctionMatrixAdapter):
        raise W7TObserverContinuationError(
            "observer continuation requires one frozen W7-M adapter"
        )
    specs = {item.model_id: item for item in adapter.baselines}
    spec = specs.get(model_id)
    if spec is None or model_id not in OBSERVER_MODEL_IDS:
        raise W7TObserverContinuationError(
            "observer continuation requires LEAK, SAT, or NORM"
        )
    return spec


def _parameter_digest(spec: W7MBaselineSpec) -> str:
    return _digest(
        {
            "model_id": spec.model_id,
            "equation_id": spec.equation_id,
            "equation_contract": spec.equation_contract,
            "parameter_bindings": spec.parameter_bindings,
        }
    )


def _state_payload(
    *,
    matrix_digest: str,
    source_path_id: str,
    model_id: str,
    equation_id: str,
    parameter_digest: str,
    clock_id: str,
    end_tick: int,
    neuron_ids: tuple[str, ...],
    baseline_state: W7NLocalBaselineState,
    predecessor_state_digest: str,
    branch_source_state_digest: str | None,
    processed_driver_digests: tuple[str, ...],
) -> dict[str, object]:
    return {
        "matrix_digest": matrix_digest,
        "source_path_id": source_path_id,
        "model_id": model_id,
        "equation_id": equation_id,
        "parameter_digest": parameter_digest,
        "clock_id": clock_id,
        "end_tick": end_tick,
        "neuron_ids": neuron_ids,
        "latent": baseline_state.latent,
        "predecessor_state_digest": predecessor_state_digest,
        "branch_source_state_digest": branch_source_state_digest,
        "processed_driver_digests": processed_driver_digests,
    }


@dataclass(frozen=True, slots=True)
class W7TObserverContinuationState:
    """One model- and path-specific external observer continuation state."""

    matrix_digest: str
    source_path_id: str
    model_id: str
    equation_id: str
    parameter_digest: str
    clock_id: str
    end_tick: int
    neuron_ids: tuple[str, ...]
    baseline_state: W7NLocalBaselineState
    predecessor_state_digest: str
    branch_source_state_digest: str | None
    processed_driver_digests: tuple[str, ...]
    state_digest: str

    def __post_init__(self) -> None:
        if (
            not self.matrix_digest
            or not self.equation_id
            or not self.parameter_digest
            or not self.clock_id
            or not self.predecessor_state_digest
        ):
            raise W7TObserverContinuationError(
                "observer state bindings must be nonempty"
            )
        if self.source_path_id not in _PATH_IDS:
            raise W7TObserverContinuationError("unknown observer source path")
        if self.model_id not in OBSERVER_MODEL_IDS:
            raise W7TObserverContinuationError("unknown observer model")
        if (
            isinstance(self.end_tick, bool)
            or not isinstance(self.end_tick, int)
            or self.end_tick < 0
        ):
            raise W7TObserverContinuationError(
                "observer end_tick must be a nonnegative integer"
            )
        neuron_ids = tuple(self.neuron_ids)
        if not neuron_ids or len(set(neuron_ids)) != len(neuron_ids):
            raise W7TObserverContinuationError(
                "observer neuron identities must be unique"
            )
        if (
            not isinstance(self.baseline_state, W7NLocalBaselineState)
            or self.baseline_state.model_id != self.model_id
            or len(self.baseline_state.latent) != len(neuron_ids)
        ):
            raise W7TObserverContinuationError(
                "observer baseline state differs from its model or geometry"
            )
        drivers = tuple(self.processed_driver_digests)
        if len(set(drivers)) != len(drivers) or any(not item for item in drivers):
            raise W7TObserverContinuationError(
                "processed observer driver digests must be unique"
            )
        if self.branch_source_state_digest is not None and (
            not self.branch_source_state_digest
        ):
            raise W7TObserverContinuationError(
                "branch source digest must be nonempty when present"
            )
        expected = _digest(
            _state_payload(
                matrix_digest=self.matrix_digest,
                source_path_id=self.source_path_id,
                model_id=self.model_id,
                equation_id=self.equation_id,
                parameter_digest=self.parameter_digest,
                clock_id=self.clock_id,
                end_tick=self.end_tick,
                neuron_ids=neuron_ids,
                baseline_state=self.baseline_state,
                predecessor_state_digest=self.predecessor_state_digest,
                branch_source_state_digest=self.branch_source_state_digest,
                processed_driver_digests=drivers,
            )
        )
        if self.state_digest != expected:
            raise W7TObserverContinuationError(
                "observer state digest does not match its content"
            )
        object.__setattr__(self, "neuron_ids", neuron_ids)
        object.__setattr__(self, "processed_driver_digests", drivers)


def _build_state(
    *,
    adapter: W7MCapacityFunctionMatrixAdapter,
    source_path_id: str,
    spec: W7MBaselineSpec,
    end_tick: int,
    baseline_state: W7NLocalBaselineState,
    predecessor_state_digest: str,
    branch_source_state_digest: str | None,
    processed_driver_digests: tuple[str, ...],
) -> W7TObserverContinuationState:
    neuron_ids = tuple(
        neuron.neuron_id for neuron in adapter.initial_field.layer.neurons
    )
    values = {
        "matrix_digest": adapter.matrix_digest,
        "source_path_id": source_path_id,
        "model_id": spec.model_id,
        "equation_id": spec.equation_id,
        "parameter_digest": _parameter_digest(spec),
        "clock_id": adapter.source.clock_id,
        "end_tick": end_tick,
        "neuron_ids": neuron_ids,
        "baseline_state": baseline_state,
        "predecessor_state_digest": predecessor_state_digest,
        "branch_source_state_digest": branch_source_state_digest,
        "processed_driver_digests": processed_driver_digests,
    }
    return W7TObserverContinuationState(
        **values,
        state_digest=_digest(_state_payload(**values)),
    )


def build_initial_w7t_observer_state(
    adapter: W7MCapacityFunctionMatrixAdapter,
    source_path_id: str,
    model_id: str,
    start_tick: int,
) -> W7TObserverContinuationState:
    """Build the single allowed zero start for one observer model and path."""

    spec = _specification(adapter, model_id)
    if source_path_id not in {item.path_id for item in adapter.paths}:
        raise W7TObserverContinuationError("unknown observer source path")
    if (
        isinstance(start_tick, bool)
        or not isinstance(start_tick, int)
        or start_tick < 0
    ):
        raise W7TObserverContinuationError(
            "observer start_tick must be a nonnegative integer"
        )
    state = build_zero_w7n_local_baseline(
        spec,
        len(adapter.initial_field.layer.neurons),
    )
    return _build_state(
        adapter=adapter,
        source_path_id=source_path_id,
        spec=spec,
        end_tick=start_tick,
        baseline_state=state,
        predecessor_state_digest=_ZERO_START,
        branch_source_state_digest=None,
        processed_driver_digests=(),
    )


@dataclass(frozen=True, slots=True)
class W7TObserverContinuationResult:
    """One observer segment result with immutable predecessor and successor."""

    production_digest: str
    driver_digest: str
    previous_state: W7TObserverContinuationState
    measurement: W7PObserverMeasurement
    next_state: W7TObserverContinuationState
    continuation_digest: str

    def __post_init__(self) -> None:
        if not self.production_digest or not self.driver_digest:
            raise W7TObserverContinuationError(
                "observer continuation bindings must be nonempty"
            )
        if self.measurement.driver_digest != self.driver_digest:
            raise W7TObserverContinuationError(
                "observer measurement and continuation driver differ"
            )
        if (
            self.previous_state.model_id != self.next_state.model_id
            or self.previous_state.source_path_id
            != self.next_state.source_path_id
            or self.next_state.predecessor_state_digest
            != self.previous_state.state_digest
        ):
            raise W7TObserverContinuationError(
                "observer predecessor and successor bindings differ"
            )
        if self.continuation_digest != _continuation_digest(self):
            raise W7TObserverContinuationError(
                "observer continuation digest does not match its content"
            )


def _continuation_digest(result: W7TObserverContinuationResult) -> str:
    return _digest(
        {
            "production_digest": result.production_digest,
            "driver_digest": result.driver_digest,
            "previous_state_digest": result.previous_state.state_digest,
            "measurement": {
                "model_id": result.measurement.model_id,
                "observer_output_linf": result.measurement.observer_output_linf,
                "observer_output_trajectory_l2": (
                    result.measurement.observer_output_trajectory_l2
                ),
                "observer_state_linf": result.measurement.observer_state_linf,
                "observer_ticks": result.measurement.observer_ticks,
                "observer_output_trace": result.measurement.observer_output_trace,
            },
            "next_state_digest": result.next_state.state_digest,
        }
    )


def advance_w7t_observer_continuation(
    adapter: W7MCapacityFunctionMatrixAdapter,
    state: W7TObserverContinuationState,
    production: W7RP0SProductionResult,
    driver: W7PObserverDriver,
) -> W7TObserverContinuationResult:
    """Advance one observer state over one explicit W7-R/W7-P segment."""

    if not isinstance(state, W7TObserverContinuationState):
        raise W7TObserverContinuationError(
            "observer continuation requires one previous state"
        )
    if not isinstance(production, W7RP0SProductionResult) or not isinstance(
        driver,
        W7PObserverDriver,
    ):
        raise W7TObserverContinuationError(
            "observer continuation requires W7-R production and W7-P driver"
        )
    spec = _specification(adapter, state.model_id)
    start_tick = driver.segments[0].start_tick
    end_tick = driver.segments[-1].end_tick
    if (
        state.matrix_digest != adapter.matrix_digest
        or production.matrix_digest != adapter.matrix_digest
        or driver.matrix_digest != adapter.matrix_digest
    ):
        raise W7TObserverContinuationError(
            "observer continuation matrix bindings differ"
        )
    if (
        state.source_path_id != production.source_path_id
        or production.source_digest != driver.source_digest
    ):
        raise W7TObserverContinuationError(
            "observer continuation source path or digest differs"
        )
    if driver.driver_digest in state.processed_driver_digests:
        raise W7TObserverContinuationError(
            "observer driver was already processed in this chain"
        )
    if (
        state.end_tick != production.interval[0]
        or production.interval != (start_tick, end_tick)
        or state.clock_id != driver.clock_id
    ):
        raise W7TObserverContinuationError(
            "observer continuation intervals are not contiguous"
        )
    if state.neuron_ids != driver.neuron_ids:
        raise W7TObserverContinuationError(
            "observer continuation neuron order differs from its driver"
        )
    if (
        state.equation_id != spec.equation_id
        or state.parameter_digest != _parameter_digest(spec)
    ):
        raise W7TObserverContinuationError(
            "observer equation or parameters changed between segments"
        )
    previous_digest = state.state_digest
    current = state.baseline_state
    trace = []
    ticks = []
    for segment in driver.segments:
        result = advance_w7n_local_baseline(
            spec,
            current,
            segment.s_values,
            (segment.end_tick - segment.start_tick) / driver.ticks_per_second,
        )
        current = result.state
        trace.append(result.output)
        ticks.append(segment.end_tick)
    output_linf = max(abs(value) for row in trace for value in row)
    output_l2 = math.sqrt(
        math.fsum(value * value for row in trace for value in row)
    )
    state_linf = max(abs(value) for value in current.latent)
    measurement = W7PObserverMeasurement(
        model_id=state.model_id,
        driver_digest=driver.driver_digest,
        observer_output_linf=output_linf,
        observer_output_trajectory_l2=output_l2,
        observer_state_linf=state_linf,
        observer_ticks=tuple(ticks),
        observer_output_trace=tuple(trace),
    )
    next_state = _build_state(
        adapter=adapter,
        source_path_id=state.source_path_id,
        spec=spec,
        end_tick=end_tick,
        baseline_state=current,
        predecessor_state_digest=state.state_digest,
        branch_source_state_digest=state.branch_source_state_digest,
        processed_driver_digests=(
            state.processed_driver_digests + (driver.driver_digest,)
        ),
    )
    if state.state_digest != previous_digest:
        raise W7TObserverContinuationError(
            "observer continuation mutated its predecessor"
        )
    values = {
        "production_digest": production.production_digest,
        "driver_digest": driver.driver_digest,
        "previous_state": state,
        "measurement": measurement,
        "next_state": next_state,
    }
    provisional = W7TObserverContinuationResult.__new__(
        W7TObserverContinuationResult
    )
    for name, value in values.items():
        object.__setattr__(provisional, name, value)
    return W7TObserverContinuationResult(
        **values,
        continuation_digest=_continuation_digest(provisional),
    )


@dataclass(frozen=True, slots=True)
class W7TObserverCheckpoint:
    """Passive checkpoint reference that contains no mutable observer state."""

    source_path_id: str
    model_id: str
    checkpoint: int
    end_tick: int
    state_digest: str

    def __post_init__(self) -> None:
        if self.source_path_id not in _PATH_IDS or self.model_id not in OBSERVER_MODEL_IDS:
            raise W7TObserverContinuationError("checkpoint role is invalid")
        if (
            isinstance(self.checkpoint, bool)
            or not isinstance(self.checkpoint, int)
            or self.checkpoint not in range(5)
        ):
            raise W7TObserverContinuationError(
                "checkpoint must be between zero and four"
            )
        if not self.state_digest:
            raise W7TObserverContinuationError(
                "checkpoint requires one observer state digest"
            )


def checkpoint_w7t_observer_state(
    state: W7TObserverContinuationState,
    checkpoint: int,
) -> W7TObserverCheckpoint:
    """Record one passive checkpoint without changing observer state."""

    if not isinstance(state, W7TObserverContinuationState):
        raise W7TObserverContinuationError(
            "checkpoint requires one observer state"
        )
    return W7TObserverCheckpoint(
        state.source_path_id,
        state.model_id,
        checkpoint,
        state.end_tick,
        state.state_digest,
    )


def branch_w7t_observer_state(
    adapter: W7MCapacityFunctionMatrixAdapter,
    state: W7TObserverContinuationState,
    target_path_ids,
) -> tuple[W7TObserverContinuationState, ...]:
    """Clone one immutable prefix state into independent target paths."""

    if not isinstance(state, W7TObserverContinuationState):
        raise W7TObserverContinuationError(
            "observer branch requires one source state"
        )
    spec = _specification(adapter, state.model_id)
    targets = tuple(target_path_ids)
    allowed = {item.path_id for item in adapter.paths}
    if (
        not targets
        or len(set(targets)) != len(targets)
        or state.source_path_id in targets
        or any(item not in allowed for item in targets)
    ):
        raise W7TObserverContinuationError(
            "observer branch targets must be unique new W7-M paths"
        )
    if state.matrix_digest != adapter.matrix_digest:
        raise W7TObserverContinuationError(
            "observer branch matrix binding differs"
        )
    return tuple(
        _build_state(
            adapter=adapter,
            source_path_id=target,
            spec=spec,
            end_tick=state.end_tick,
            baseline_state=state.baseline_state,
            predecessor_state_digest=state.state_digest,
            branch_source_state_digest=state.state_digest,
            processed_driver_digests=state.processed_driver_digests,
        )
        for target in targets
    )
