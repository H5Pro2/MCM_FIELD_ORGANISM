"""Isolated W7-R P0-S completion-state production for one source segment."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import hashlib
import json
import math

import numpy as np

from .field_step_time import MCMFieldStepTime
from .mcm_f3_controlled_history_source import (
    mcm_f3_receptor_sequences_digest,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff import handoff_receptor_completion_groups
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7p_measurement_compositor import (
    W7PCompletedP0SSample,
    W7PObserverDriver,
    compose_w7p_observer_driver,
)
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamilyError,
    authorize_w7w_source_segment,
)


class W7RP0SCompletionProducerError(ValueError):
    """Raised when isolated P0 completion production leaves W7-Q."""


_PATH_IDS = frozenset({"ab", "ag", "ba", "bg", "ua", "ub", "ug"})
_RESPONSE_TIME_SECONDS = 1.0
_AFTERIMAGE_TIME_SECONDS = 0.5


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_field_vector(values, role: str) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise W7RP0SCompletionProducerError(
            f"{role} must contain numeric values"
        ) from exc
    if not result or any(
        not math.isfinite(value) or value < -1.0 or value > 1.0
        for value in result
    ):
        raise W7RP0SCompletionProducerError(
            f"{role} must be nonempty, finite, and normalized"
        )
    return result


def _state_payload(
    matrix_digest: str,
    source_path_id: str,
    clock_id: str,
    end_tick: int,
    neuron_ids: tuple[str, ...],
    s_values: tuple[float, ...],
    h_values: tuple[float, ...],
    p0_field: SharedMCMField,
) -> dict[str, object]:
    return {
        "matrix_digest": matrix_digest,
        "source_path_id": source_path_id,
        "clock_id": clock_id,
        "end_tick": end_tick,
        "neuron_ids": neuron_ids,
        "s_values": s_values,
        "h_values": h_values,
        "layer_digest": p0_field.layer.digest(),
        "last_distribution_digest": (
            None
            if p0_field.last_distribution is None
            else p0_field.last_distribution.digest()
        ),
        "response_time_seconds": _RESPONSE_TIME_SECONDS,
        "afterimage_time_seconds": _AFTERIMAGE_TIME_SECONDS,
        "leak_rate_per_second": 0.0,
    }


@dataclass(frozen=True, slots=True)
class W7RP0State:
    """Complete private P0 continuation state without M or development."""

    matrix_digest: str
    source_path_id: str
    clock_id: str
    end_tick: int
    neuron_ids: tuple[str, ...]
    s_values: tuple[float, ...]
    h_values: tuple[float, ...]
    state_digest: str
    p0_field: SharedMCMField = field(repr=False)

    def __post_init__(self) -> None:
        if not self.matrix_digest or not self.clock_id:
            raise W7RP0SCompletionProducerError(
                "P0 state bindings must be nonempty"
            )
        if self.source_path_id not in _PATH_IDS:
            raise W7RP0SCompletionProducerError("unknown W7-M source path")
        if (
            isinstance(self.end_tick, bool)
            or not isinstance(self.end_tick, int)
            or self.end_tick < 0
        ):
            raise W7RP0SCompletionProducerError(
                "P0 state end_tick must be a nonnegative integer"
            )
        neuron_ids = tuple(self.neuron_ids)
        if not neuron_ids or len(set(neuron_ids)) != len(neuron_ids):
            raise W7RP0SCompletionProducerError(
                "P0 state neuron identities must be unique"
            )
        s_values = _finite_field_vector(self.s_values, "P0 S")
        h_values = _finite_field_vector(self.h_values, "P0 H")
        if len(s_values) != len(neuron_ids) or len(h_values) != len(neuron_ids):
            raise W7RP0SCompletionProducerError(
                "P0 S/H must match every field location"
            )
        if (
            not isinstance(self.p0_field, SharedMCMField)
            or self.p0_field.substrate is not None
            or self.p0_field.development is not None
        ):
            raise W7RP0SCompletionProducerError(
                "P0 state requires one substrate-free shared field"
            )
        field_ids = tuple(
            neuron.neuron_id for neuron in self.p0_field.layer.neurons
        )
        field_s = tuple(
            float(neuron.activation) for neuron in self.p0_field.layer.neurons
        )
        field_h = tuple(
            float(neuron.afterimage) for neuron in self.p0_field.layer.neurons
        )
        if field_ids != neuron_ids or field_s != s_values or field_h != h_values:
            raise W7RP0SCompletionProducerError(
                "private P0 field and exposed S/H state differ"
            )
        last = self.p0_field.last_distribution
        if last is not None and (
            last.field_time.clock_id != self.clock_id
            or last.field_time.window_end_tick != self.end_tick
        ):
            raise W7RP0SCompletionProducerError(
                "P0 field completion time differs from its state binding"
            )
        expected = _digest(
            _state_payload(
                self.matrix_digest,
                self.source_path_id,
                self.clock_id,
                self.end_tick,
                neuron_ids,
                s_values,
                h_values,
                self.p0_field,
            )
        )
        if self.state_digest != expected:
            raise W7RP0SCompletionProducerError(
                "P0 state digest does not match its content"
            )
        object.__setattr__(self, "neuron_ids", neuron_ids)
        object.__setattr__(self, "s_values", s_values)
        object.__setattr__(self, "h_values", h_values)


def _build_state(
    adapter: W7MCapacityFunctionMatrixAdapter,
    source_path_id: str,
    clock_id: str,
    end_tick: int,
    p0_field: SharedMCMField,
) -> W7RP0State:
    neuron_ids = tuple(neuron.neuron_id for neuron in p0_field.layer.neurons)
    s_values = tuple(float(neuron.activation) for neuron in p0_field.layer.neurons)
    h_values = tuple(float(neuron.afterimage) for neuron in p0_field.layer.neurons)
    payload = _state_payload(
        adapter.matrix_digest,
        source_path_id,
        clock_id,
        end_tick,
        neuron_ids,
        s_values,
        h_values,
        p0_field,
    )
    return W7RP0State(
        adapter.matrix_digest,
        source_path_id,
        clock_id,
        end_tick,
        neuron_ids,
        s_values,
        h_values,
        _digest(payload),
        p0_field,
    )


def build_initial_w7r_p0_state(
    adapter: W7MCapacityFunctionMatrixAdapter,
    source_path_id: str,
    start_tick: int,
) -> W7RP0State:
    """Build one zero fast-state P0 binding on the frozen W7-M geometry."""

    if not isinstance(adapter, W7MCapacityFunctionMatrixAdapter):
        raise W7RP0SCompletionProducerError(
            "initial P0 state requires one frozen W7-M adapter"
        )
    if source_path_id not in {item.path_id for item in adapter.paths}:
        raise W7RP0SCompletionProducerError("unknown W7-M source path")
    if (
        isinstance(start_tick, bool)
        or not isinstance(start_tick, int)
        or start_tick < 0
    ):
        raise W7RP0SCompletionProducerError(
            "initial P0 start_tick must be a nonnegative integer"
        )
    p0_field = replace(
        adapter.initial_field,
        substrate=None,
        development=None,
    )
    if p0_field.last_distribution is not None or any(
        neuron.activation != 0.0 or neuron.afterimage != 0.0
        for neuron in p0_field.layer.neurons
    ):
        raise W7RP0SCompletionProducerError(
            "initial W7-M P0 fast state must be exactly zero"
        )
    return _build_state(
        adapter,
        source_path_id,
        adapter.source.clock_id,
        start_tick,
        p0_field,
    )


@dataclass(frozen=True, slots=True)
class W7RP0SEventState:
    """One P0-S state after an atomic receptor completion group."""

    completion_tick: int
    neuron_ids: tuple[str, ...]
    s_values: tuple[float, ...]

    def __post_init__(self) -> None:
        if (
            isinstance(self.completion_tick, bool)
            or not isinstance(self.completion_tick, int)
            or self.completion_tick < 0
        ):
            raise W7RP0SCompletionProducerError(
                "event completion_tick must be a nonnegative integer"
            )
        neuron_ids = tuple(self.neuron_ids)
        values = _finite_field_vector(self.s_values, "event P0 S")
        if len(neuron_ids) != len(values) or len(set(neuron_ids)) != len(neuron_ids):
            raise W7RP0SCompletionProducerError(
                "event P0 S must match unique field locations"
            )
        object.__setattr__(self, "neuron_ids", neuron_ids)
        object.__setattr__(self, "s_values", values)


@dataclass(frozen=True, slots=True)
class W7RP0SProductionResult:
    """One source-segment production with event and continuation states."""

    matrix_digest: str
    source_digest: str
    source_path_id: str
    interval: tuple[int, int]
    assigned_event_count: int
    initial_state: W7RP0State
    event_states: tuple[W7RP0SEventState, ...]
    end_state: W7RP0State
    production_digest: str

    def __post_init__(self) -> None:
        if self.matrix_digest != self.initial_state.matrix_digest or (
            self.matrix_digest != self.end_state.matrix_digest
        ):
            raise W7RP0SCompletionProducerError(
                "production matrix and P0 state bindings differ"
            )
        if self.source_path_id != self.initial_state.source_path_id or (
            self.source_path_id != self.end_state.source_path_id
        ):
            raise W7RP0SCompletionProducerError(
                "production path and P0 state bindings differ"
            )
        start_tick, end_tick = self.interval
        if (
            start_tick != self.initial_state.end_tick
            or end_tick != self.end_state.end_tick
            or end_tick <= start_tick
        ):
            raise W7RP0SCompletionProducerError(
                "production interval and continuation states differ"
            )
        if (
            isinstance(self.assigned_event_count, bool)
            or not isinstance(self.assigned_event_count, int)
            or self.assigned_event_count < 0
        ):
            raise W7RP0SCompletionProducerError(
                "assigned_event_count must be a nonnegative integer"
            )
        events = tuple(self.event_states)
        ticks = tuple(item.completion_tick for item in events)
        if ticks != tuple(sorted(set(ticks))) or any(
            item.neuron_ids != self.initial_state.neuron_ids for item in events
        ):
            raise W7RP0SCompletionProducerError(
                "production event states must be ordered on one field geometry"
            )
        object.__setattr__(self, "event_states", events)
        if self.production_digest != _production_digest(self):
            raise W7RP0SCompletionProducerError(
                "production digest does not match its content"
            )


def _production_digest(result: W7RP0SProductionResult) -> str:
    return _digest(
        {
            "matrix_digest": result.matrix_digest,
            "source_digest": result.source_digest,
            "source_path_id": result.source_path_id,
            "interval": result.interval,
            "assigned_event_count": result.assigned_event_count,
            "initial_state_digest": result.initial_state.state_digest,
            "event_states": [
                {
                    "completion_tick": item.completion_tick,
                    "neuron_ids": item.neuron_ids,
                    "s_values": item.s_values,
                }
                for item in result.event_states
            ],
            "end_state_digest": result.end_state.state_digest,
        }
    )


def _known_source_digests(
    adapter: W7MCapacityFunctionMatrixAdapter,
) -> frozenset[str]:
    source = adapter.source
    return frozenset(
        (source.contact_a_digest,)
        + source.contact_b_step_digests
        + source.interruption_step_digests
        + source.probe_digests
    )


def produce_w7r_p0_s_completion_states(
    adapter: W7MCapacityFunctionMatrixAdapter,
    source_digest: str,
    sequences,
    interval: tuple[int, int],
    initial_state: W7RP0State,
    *,
    source_authorization: W7WSourceAuthorization | None = None,
    _state_observer=None,
) -> W7RP0SProductionResult:
    """Produce P0-S event states for one explicit frozen source segment."""

    if not isinstance(adapter, W7MCapacityFunctionMatrixAdapter):
        raise W7RP0SCompletionProducerError(
            "P0 production requires one frozen W7-M adapter"
        )
    if not isinstance(initial_state, W7RP0State):
        raise W7RP0SCompletionProducerError(
            "P0 production requires one bound initial state"
        )
    if initial_state.matrix_digest != adapter.matrix_digest:
        raise W7RP0SCompletionProducerError(
            "P0 initial state belongs to another W7-M matrix"
        )
    if _state_observer is not None and not callable(_state_observer):
        raise W7RP0SCompletionProducerError(
            "P0 passive state observer must be callable"
        )
    try:
        start_tick, end_tick = interval
    except (TypeError, ValueError) as exc:
        raise W7RP0SCompletionProducerError(
            "P0 interval must contain two ticks"
        ) from exc
    if (
        isinstance(start_tick, bool)
        or isinstance(end_tick, bool)
        or not isinstance(start_tick, int)
        or not isinstance(end_tick, int)
        or start_tick != initial_state.end_tick
        or end_tick <= start_tick
    ):
        raise W7RP0SCompletionProducerError(
            "P0 interval must continue its initial state exactly"
        )
    if source_digest not in _known_source_digests(adapter):
        if source_authorization is None:
            raise W7RP0SCompletionProducerError(
                "P0 source digest is not bound by W7-M"
            )
        try:
            authorize_w7w_source_segment(
                adapter,
                source_authorization,
                source_digest,
                initial_state.source_path_id,
                (start_tick, end_tick),
            )
        except W7WSymmetricSourceFamilyError as exc:
            raise W7RP0SCompletionProducerError(str(exc)) from exc
    sequences_in = tuple(sequences)
    if len(sequences_in) != 2 or any(
        not isinstance(item, ReceptorTimeSequence) for item in sequences_in
    ):
        raise W7RP0SCompletionProducerError(
            "P0 source segment requires two receptor time sequences"
        )
    canonical_sequences = tuple(
        sorted(sequences_in, key=lambda item: item.modality_id)
    )
    if len({item.modality_id for item in canonical_sequences}) != 2:
        raise W7RP0SCompletionProducerError(
            "P0 source segment modalities must be unique"
        )
    if mcm_f3_receptor_sequences_digest(canonical_sequences) != source_digest:
        raise W7RP0SCompletionProducerError(
            "P0 receptor sequences differ from their W7-M source digest"
        )
    step = MCMFieldStepTime(
        adapter.source.clock_id,
        start_tick,
        end_tick,
        adapter.source.ticks_per_second,
    )
    handoff = handoff_receptor_completion_groups(canonical_sequences, (step,))
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != handoff.source_event_count
        or len(handoff.batches) != 1
    ):
        raise W7RP0SCompletionProducerError(
            "P0 receptor completion handoff is incomplete"
        )
    trajectory = map_proposal_batch_to_transient_docks(
        handoff.batches[0],
        initial_state.p0_field.docks,
    )
    transient_inputs = project_transient_docks_to_neuron_inputs(
        trajectory,
        initial_state.p0_field.docks,
    )
    distribution = ReceptorDistribution(
        CommonFieldTime(adapter.source.clock_id, start_tick, end_tick),
        (),
    )
    observed: dict[int, tuple[tuple[float, ...], tuple[float, ...]]] = {}

    def observe(tick: int, activation: np.ndarray, afterimage: np.ndarray) -> None:
        if tick in observed:
            raise W7RP0SCompletionProducerError(
                "P0 observer produced a duplicate boundary tick"
            )
        s_values = _finite_field_vector(tuple(activation), "observed P0 S")
        h_values = _finite_field_vector(tuple(afterimage), "observed P0 H")
        if len(s_values) != len(initial_state.neuron_ids) or (
            len(h_values) != len(initial_state.neuron_ids)
        ):
            raise W7RP0SCompletionProducerError(
                "observed P0 state differs from field geometry"
            )
        observed[tick] = s_values, h_values
        if _state_observer is not None:
            activation.setflags(write=False)
            afterimage.setflags(write=False)
            if _state_observer(tick, activation, afterimage) is not None:
                raise W7RP0SCompletionProducerError(
                    "P0 passive state observer must not return state"
                )
        return None

    initial_digest = initial_state.state_digest
    next_field = advance_neutral_fast_shared_field_transient(
        initial_state.p0_field,
        distribution,
        transient_inputs,
        NeutralLocalFieldSubstrateConfig(_RESPONSE_TIME_SECONDS),
        NeutralFastAfterimageConfig(_AFTERIMAGE_TIME_SECONDS),
        _state_observer=observe,
    )
    if initial_state.state_digest != initial_digest:
        raise W7RP0SCompletionProducerError("P0 production mutated its input state")
    event_ticks = tuple(
        group.completion_tick
        for group in handoff.batches[0].completion_groups
    )
    if any(tick not in observed for tick in event_ticks):
        raise W7RP0SCompletionProducerError(
            "P0 observer missed a receptor completion boundary"
        )
    event_states = tuple(
        W7RP0SEventState(tick, initial_state.neuron_ids, observed[tick][0])
        for tick in event_ticks
    )
    end_state = _build_state(
        adapter,
        initial_state.source_path_id,
        adapter.source.clock_id,
        end_tick,
        next_field,
    )
    if end_tick in observed and (
        observed[end_tick][0] != end_state.s_values
        or observed[end_tick][1] != end_state.h_values
    ):
        raise W7RP0SCompletionProducerError(
            "observed terminal P0 state differs from committed state"
        )
    values = {
        "matrix_digest": adapter.matrix_digest,
        "source_digest": source_digest,
        "source_path_id": initial_state.source_path_id,
        "interval": (start_tick, end_tick),
        "assigned_event_count": handoff.assigned_event_count,
        "initial_state": initial_state,
        "event_states": event_states,
        "end_state": end_state,
    }
    provisional = W7RP0SProductionResult.__new__(W7RP0SProductionResult)
    for name, value in values.items():
        object.__setattr__(provisional, name, value)
    production_digest = _production_digest(provisional)
    return W7RP0SProductionResult(
        **values,
        production_digest=production_digest,
    )


def compose_w7r_observer_driver(
    adapter: W7MCapacityFunctionMatrixAdapter,
    production: W7RP0SProductionResult,
    *,
    source_authorization: W7WSourceAuthorization | None = None,
) -> W7PObserverDriver:
    """Pass one completed W7-R production into the W7-P compositor."""

    if not isinstance(adapter, W7MCapacityFunctionMatrixAdapter) or not isinstance(
        production,
        W7RP0SProductionResult,
    ):
        raise W7RP0SCompletionProducerError(
            "W7-P handoff requires one adapter and one W7-R production"
        )
    if production.matrix_digest != adapter.matrix_digest:
        raise W7RP0SCompletionProducerError(
            "W7-P handoff matrix binding differs from W7-R"
        )
    samples = [
        W7PCompletedP0SSample(item.completion_tick, item.s_values)
        for item in production.event_states
    ]
    if not samples or samples[-1].completion_tick != production.interval[1]:
        samples.append(
            W7PCompletedP0SSample(
                production.interval[1],
                production.end_state.s_values,
            )
        )
    return compose_w7p_observer_driver(
        adapter,
        production.source_digest,
        production.interval,
        production.initial_state.s_values,
        tuple(samples),
        source_path_id=production.source_path_id,
        source_authorization=source_authorization,
    )
