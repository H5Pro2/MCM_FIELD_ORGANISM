"""W7-AI P0 zero-start measurement references without CAP comparison."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

import numpy as np

from .w7aa_p0_seven_path_consumer import W7AAP0SevenPathResult
from .w7ac_observer_seven_path_consumer import W7ACObserverSevenPathResult
from .w7ae_cap_seven_path_consumer import W7AECAPSevenPathResult
from .w7ag_passive_cap_measurement_handoff import (
    W7AGPassiveCAPMeasurementHandoff,
)
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7p_measurement_compositor import W7PFieldMeasurement
from .w7r_p0_s_completion_producer import (
    W7RP0SProductionResult,
    W7RP0State,
    build_initial_w7r_p0_state,
    produce_w7r_p0_s_completion_states,
)
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamily,
)
from .w7y_seven_path_source_plan import (
    W7YCheckpointPlan,
    W7YSevenPathSourcePlan,
    build_w7y_seven_path_source_plan,
)


class W7AIP0MeasurementReferenceError(ValueError):
    """Raised when P0 measurement references leave the W7-AH contract."""


_REFERENCE_ID = "w7ai.p0-zero-start-measurement-reference.v1"
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_vector(values, role: str) -> tuple[float, ...]:
    result = tuple(float(item) for item in values)
    if not result or any(not math.isfinite(item) for item in result):
        raise W7AIP0MeasurementReferenceError(f"{role} must be finite")
    return result


def _sample_payload(
    tick: int,
    s_values: tuple[float, ...],
    h_values: tuple[float, ...],
) -> dict[str, object]:
    return {
        "tick": tick,
        "s_values": s_values,
        "h_values": h_values,
    }


@dataclass(frozen=True, slots=True)
class W7AIP0TrajectorySample:
    """One passive P0 S/H sample at an actual completion boundary."""

    tick: int
    s_values: tuple[float, ...]
    h_values: tuple[float, ...]
    sample_digest: str

    def __post_init__(self) -> None:
        if isinstance(self.tick, bool) or not isinstance(self.tick, int):
            raise W7AIP0MeasurementReferenceError(
                "P0 sample tick must be an integer"
            )
        s_values = _finite_vector(self.s_values, "P0 sample S")
        h_values = _finite_vector(self.h_values, "P0 sample H")
        if len(s_values) != len(h_values):
            raise W7AIP0MeasurementReferenceError(
                "P0 sample S/H geometry differs"
            )
        payload = _sample_payload(self.tick, s_values, h_values)
        if self.sample_digest != _digest(payload):
            raise W7AIP0MeasurementReferenceError(
                "P0 sample digest does not match its content"
            )
        object.__setattr__(self, "s_values", s_values)
        object.__setattr__(self, "h_values", h_values)


def _field_measurement(
    path_id: str,
    checkpoint: int,
    samples: tuple[W7AIP0TrajectorySample, ...],
) -> W7PFieldMeasurement:
    return W7PFieldMeasurement(
        "p0",
        path_id,
        checkpoint,
        max(abs(value) for sample in samples for value in sample.s_values),
        max(abs(value) for sample in samples for value in sample.h_values),
        math.sqrt(
            math.fsum(
                value * value
                for sample in samples
                for values in (sample.s_values, sample.h_values)
                for value in values
            )
        ),
        tuple(item.tick for item in samples),
    )


def _reference_payload(
    plan_checkpoint_digest: str,
    path_id: str,
    checkpoint: int,
    initial_state_digest: str,
    sample_digests: tuple[str, ...],
    observed_production_digest: str,
    unobserved_production_digest: str,
    reversed_production_digest: str,
    equivalence_digest: str,
    field_measurement: W7PFieldMeasurement,
) -> dict[str, object]:
    return {
        "plan_checkpoint_digest": plan_checkpoint_digest,
        "path_id": path_id,
        "checkpoint": checkpoint,
        "initial_state_digest": initial_state_digest,
        "sample_digests": sample_digests,
        "observed_production_digest": observed_production_digest,
        "unobserved_production_digest": unobserved_production_digest,
        "reversed_production_digest": reversed_production_digest,
        "equivalence_digest": equivalence_digest,
        "field_measurement": {
            "model_id": field_measurement.model_id,
            "path_id": field_measurement.path_id,
            "checkpoint": field_measurement.checkpoint,
            "probe_S_linf": field_measurement.probe_S_linf,
            "probe_H_linf": field_measurement.probe_H_linf,
            "probe_SH_trajectory_l2": field_measurement.probe_SH_trajectory_l2,
            "probe_observation_ticks": field_measurement.probe_observation_ticks,
        },
        "substrate_present": False,
        "returns_to_p0_main": False,
    }


@dataclass(frozen=True, slots=True)
class W7AIP0MeasurementReferenceResult:
    """One P0 zero-start measurement and its W7-R equivalence evidence."""

    plan_checkpoint_digest: str
    path_id: str
    checkpoint: int
    initial_state: W7RP0State = field(repr=False)
    samples: tuple[W7AIP0TrajectorySample, ...] = field(repr=False)
    observed_production: W7RP0SProductionResult = field(repr=False)
    unobserved_production: W7RP0SProductionResult = field(repr=False)
    reversed_production: W7RP0SProductionResult = field(repr=False)
    equivalence_digest: str
    field_measurement: W7PFieldMeasurement
    measurement_reference_digest: str

    def __post_init__(self) -> None:
        samples = tuple(self.samples)
        ticks = tuple(item.tick for item in samples)
        if (
            not self.plan_checkpoint_digest
            or self.path_id not in _PATH_IDS
            or self.checkpoint not in range(5)
            or self.initial_state.source_path_id != self.path_id
            or self.initial_state.end_tick != (self.checkpoint + 4) * 1_000_000
            or self.initial_state.p0_field.substrate is not None
            or self.initial_state.p0_field.development is not None
            or any(self.initial_state.s_values)
            or any(self.initial_state.h_values)
            or not samples
            or ticks != tuple(sorted(set(ticks)))
            or self.observed_production.initial_state is not self.initial_state
            or self.field_measurement.model_id != "p0"
            or self.field_measurement.path_id != self.path_id
            or self.field_measurement.checkpoint != self.checkpoint
            or self.field_measurement.probe_observation_ticks != ticks
        ):
            raise W7AIP0MeasurementReferenceError(
                "P0 measurement reference binding is invalid"
            )
        payload = _reference_payload(
            self.plan_checkpoint_digest,
            self.path_id,
            self.checkpoint,
            self.initial_state.state_digest,
            tuple(item.sample_digest for item in samples),
            self.observed_production.production_digest,
            self.unobserved_production.production_digest,
            self.reversed_production.production_digest,
            self.equivalence_digest,
            self.field_measurement,
        )
        if self.measurement_reference_digest != _digest(payload):
            raise W7AIP0MeasurementReferenceError(
                "P0 measurement reference digest does not match its content"
            )
        object.__setattr__(self, "samples", samples)


def _observed_production(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    checkpoint: W7YCheckpointPlan,
    initial: W7RP0State,
    *,
    reverse_modalities: bool = False,
) -> tuple[W7RP0SProductionResult, tuple[W7AIP0TrajectorySample, ...]]:
    observed: list[W7AIP0TrajectorySample] = []

    def observe(
        tick: int,
        activation: np.ndarray,
        afterimage: np.ndarray,
    ) -> None:
        if activation.flags.writeable or afterimage.flags.writeable:
            raise W7AIP0MeasurementReferenceError(
                "P0 observer received writable arrays"
            )
        s_values = _finite_vector(activation, "observed P0 S")
        h_values = _finite_vector(afterimage, "observed P0 H")
        payload = _sample_payload(tick, s_values, h_values)
        observed.append(
            W7AIP0TrajectorySample(
                tick,
                s_values,
                h_values,
                _digest(payload),
            )
        )
        return None

    sequences = (
        tuple(reversed(checkpoint.probe.sequences))
        if reverse_modalities
        else checkpoint.probe.sequences
    )
    production = produce_w7r_p0_s_completion_states(
        adapter,
        checkpoint.probe.source_digest,
        sequences,
        checkpoint.probe.interval,
        initial,
        source_authorization=authorization,
        _state_observer=observe,
    )
    samples = tuple(observed)
    if (
        not samples
        or samples[-1].tick != checkpoint.probe.interval[1]
        or tuple(item.tick for item in samples)
        != tuple(sorted({item.tick for item in samples}))
    ):
        raise W7AIP0MeasurementReferenceError(
            "P0 measurement boundaries are incomplete"
        )
    return production, samples


def _equivalence_payload(
    observed: W7RP0SProductionResult,
    unobserved: W7RP0SProductionResult,
    reversed_result: W7RP0SProductionResult,
    samples: tuple[W7AIP0TrajectorySample, ...],
) -> dict[str, object]:
    return {
        "assigned_event_count": observed.assigned_event_count,
        "event_ticks": tuple(item.completion_tick for item in observed.event_states),
        "event_s_digests": tuple(
            _digest(item.s_values) for item in observed.event_states
        ),
        "sample_ticks": tuple(item.tick for item in samples),
        "observed_end_state_digest": observed.end_state.state_digest,
        "unobserved_end_state_digest": unobserved.end_state.state_digest,
        "reversed_end_state_digest": reversed_result.end_state.state_digest,
        "observed_field_digest": observed.end_state.p0_field.snapshot().digest(),
        "unobserved_field_digest": unobserved.end_state.p0_field.snapshot().digest(),
        "reversed_field_digest": reversed_result.end_state.p0_field.snapshot().digest(),
    }


def _reference(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    checkpoint: W7YCheckpointPlan,
) -> W7AIP0MeasurementReferenceResult:
    initial = build_initial_w7r_p0_state(
        adapter,
        checkpoint.path_id,
        checkpoint.tick,
    )
    observed, samples = _observed_production(
        adapter,
        authorization,
        checkpoint,
        initial,
    )
    unobserved_initial = build_initial_w7r_p0_state(
        adapter,
        checkpoint.path_id,
        checkpoint.tick,
    )
    unobserved = produce_w7r_p0_s_completion_states(
        adapter,
        checkpoint.probe.source_digest,
        checkpoint.probe.sequences,
        checkpoint.probe.interval,
        unobserved_initial,
        source_authorization=authorization,
    )
    reversed_initial = build_initial_w7r_p0_state(
        adapter,
        checkpoint.path_id,
        checkpoint.tick,
    )
    reversed_result, reversed_samples = _observed_production(
        adapter,
        authorization,
        checkpoint,
        reversed_initial,
        reverse_modalities=True,
    )
    sample_by_tick = {item.tick: item for item in samples}
    event_ticks = tuple(item.completion_tick for item in observed.event_states)
    if (
        observed.production_digest != unobserved.production_digest
        or observed.production_digest != reversed_result.production_digest
        or observed.event_states != unobserved.event_states
        or observed.event_states != reversed_result.event_states
        or observed.end_state.state_digest != unobserved.end_state.state_digest
        or observed.end_state.state_digest != reversed_result.end_state.state_digest
        or samples != reversed_samples
        or any(
            sample_by_tick[item.completion_tick].s_values != item.s_values
            for item in observed.event_states
        )
        or samples[-1].s_values != observed.end_state.s_values
        or samples[-1].h_values != observed.end_state.h_values
        or any(tick not in sample_by_tick for tick in event_ticks)
    ):
        raise W7AIP0MeasurementReferenceError(
            "P0 passive measurement differs from W7-R"
        )
    equivalence_payload = _equivalence_payload(
        observed,
        unobserved,
        reversed_result,
        samples,
    )
    equivalence_digest = _digest(equivalence_payload)
    measurement = _field_measurement(
        checkpoint.path_id,
        checkpoint.checkpoint,
        samples,
    )
    payload = _reference_payload(
        checkpoint.checkpoint_digest,
        checkpoint.path_id,
        checkpoint.checkpoint,
        initial.state_digest,
        tuple(item.sample_digest for item in samples),
        observed.production_digest,
        unobserved.production_digest,
        reversed_result.production_digest,
        equivalence_digest,
        measurement,
    )
    return W7AIP0MeasurementReferenceResult(
        checkpoint.checkpoint_digest,
        checkpoint.path_id,
        checkpoint.checkpoint,
        initial,
        samples,
        observed,
        unobserved,
        reversed_result,
        equivalence_digest,
        measurement,
        _digest(payload),
    )


def _result_payload(
    plan_digest: str,
    p0_digest: str,
    observer_digest: str,
    cap_digest: str,
    cap_measurement_digest: str,
    references: tuple[W7AIP0MeasurementReferenceResult, ...],
    order_countercontrol_digest: str,
) -> dict[str, object]:
    return {
        "reference_id": _REFERENCE_ID,
        "plan_digest": plan_digest,
        "p0_consumption_digest": p0_digest,
        "observer_consumption_digest": observer_digest,
        "cap_consumption_digest": cap_digest,
        "cap_measurement_handoff_digest": cap_measurement_digest,
        "reference_digests": tuple(
            item.measurement_reference_digest for item in references
        ),
        "order_countercontrol_digest": order_countercontrol_digest,
        "p0_absolute_comparison_ready": True,
    }


@dataclass(frozen=True, slots=True)
class W7AIP0ZeroStartMeasurementReferences:
    """Complete P0 measurement references without CAP/P0 evaluation."""

    reference_id: str
    plan_digest: str
    p0_consumption_digest: str
    observer_consumption_digest: str
    cap_consumption_digest: str
    cap_measurement_handoff_digest: str
    references: tuple[W7AIP0MeasurementReferenceResult, ...] = field(repr=False)
    order_countercontrol_digest: str
    p0_absolute_comparison_ready: bool
    p0_zero_start_measurement_reference_digest: str

    def __post_init__(self) -> None:
        references = tuple(self.references)
        expected_roles = tuple(
            (path_id, checkpoint)
            for path_id in _PATH_IDS
            for checkpoint in range(5)
        )
        if (
            self.reference_id != _REFERENCE_ID
            or tuple((item.path_id, item.checkpoint) for item in references)
            != expected_roles
            or not self.plan_digest
            or not self.p0_consumption_digest
            or not self.observer_consumption_digest
            or not self.cap_consumption_digest
            or not self.cap_measurement_handoff_digest
            or not self.order_countercontrol_digest
            or self.p0_absolute_comparison_ready is not True
        ):
            raise W7AIP0MeasurementReferenceError(
                "P0 zero-start reference binding is invalid"
            )
        payload = _result_payload(
            self.plan_digest,
            self.p0_consumption_digest,
            self.observer_consumption_digest,
            self.cap_consumption_digest,
            self.cap_measurement_handoff_digest,
            references,
            self.order_countercontrol_digest,
        )
        if self.p0_zero_start_measurement_reference_digest != _digest(payload):
            raise W7AIP0MeasurementReferenceError(
                "P0 zero-start reference digest does not match its content"
            )
        object.__setattr__(self, "references", references)


def compose_w7ai_p0_zero_start_measurement_references(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    p0_result: W7AAP0SevenPathResult,
    observer_result: W7ACObserverSevenPathResult,
    cap_result: W7AECAPSevenPathResult,
    cap_measurements: W7AGPassiveCAPMeasurementHandoff,
) -> W7AIP0ZeroStartMeasurementReferences:
    """Build 35 P0 zero-start references and W7-R equivalence evidence."""

    if (
        not isinstance(adapter, W7MCapacityFunctionMatrixAdapter)
        or not isinstance(family, W7WSymmetricSourceFamily)
        or not isinstance(authorization, W7WSourceAuthorization)
        or not isinstance(plan, W7YSevenPathSourcePlan)
        or not isinstance(p0_result, W7AAP0SevenPathResult)
        or not isinstance(observer_result, W7ACObserverSevenPathResult)
        or not isinstance(cap_result, W7AECAPSevenPathResult)
        or not isinstance(cap_measurements, W7AGPassiveCAPMeasurementHandoff)
    ):
        raise W7AIP0MeasurementReferenceError(
            "P0 reference requires complete W7-M/W/Y/AA/AC/AE/AG bindings"
        )
    expected_plan = build_w7y_seven_path_source_plan(
        adapter,
        family,
        authorization,
    )
    if (
        plan.paths != expected_plan.paths
        or plan.seven_path_plan_digest != expected_plan.seven_path_plan_digest
        or p0_result.plan_digest != plan.seven_path_plan_digest
        or observer_result.p0_consumption_digest
        != p0_result.p0_seven_path_consumption_digest
        or cap_result.p0_consumption_digest
        != p0_result.p0_seven_path_consumption_digest
        or cap_result.observer_consumption_digest
        != observer_result.observer_seven_path_consumption_digest
        or cap_measurements.cap_consumption_digest
        != cap_result.cap_seven_path_consumption_digest
        or cap_measurements.p0_absolute_comparison_ready is not False
    ):
        raise W7AIP0MeasurementReferenceError(
            "P0 reference input digests differ"
        )
    input_digests = (
        p0_result.p0_seven_path_consumption_digest,
        observer_result.observer_seven_path_consumption_digest,
        cap_result.cap_seven_path_consumption_digest,
        cap_measurements.measurement_handoff_digest,
    )
    checkpoints = tuple(
        checkpoint
        for path in plan.paths
        for checkpoint in path.checkpoints
    )
    references = tuple(
        _reference(adapter, authorization, checkpoint)
        for checkpoint in checkpoints
    )
    reversed_references = tuple(
        _reference(adapter, authorization, checkpoint)
        for checkpoint in reversed(checkpoints)
    )
    actual = {
        (item.path_id, item.checkpoint): item.measurement_reference_digest
        for item in references
    }
    if any(
        actual[(item.path_id, item.checkpoint)]
        != item.measurement_reference_digest
        for item in reversed_references
    ):
        raise W7AIP0MeasurementReferenceError(
            "P0 reference processing order changed a result"
        )
    for checkpoint in range(5):
        starts = tuple(
            item.initial_state
            for item in references
            if item.checkpoint == checkpoint
        )
        if (
            len(starts) != 7
            or len({item.s_values for item in starts}) != 1
            or len({item.h_values for item in starts}) != 1
            or len({id(item) for item in starts}) != 7
            or len({id(item.p0_field) for item in starts}) != 7
        ):
            raise W7AIP0MeasurementReferenceError(
                "P0 checkpoint null starts are not equal and independent"
            )
    order_digest = _digest(
        {
            "canonical_reference_digests": tuple(
                item.measurement_reference_digest for item in references
            ),
            "reverse_role_digests": tuple(
                actual[(item.path_id, item.checkpoint)]
                for item in reversed(references)
            ),
        }
    )
    if input_digests != (
        p0_result.p0_seven_path_consumption_digest,
        observer_result.observer_seven_path_consumption_digest,
        cap_result.cap_seven_path_consumption_digest,
        cap_measurements.measurement_handoff_digest,
    ):
        raise W7AIP0MeasurementReferenceError(
            "P0 reference mutated an input result"
        )
    payload = _result_payload(
        plan.seven_path_plan_digest,
        input_digests[0],
        input_digests[1],
        input_digests[2],
        input_digests[3],
        references,
        order_digest,
    )
    return W7AIP0ZeroStartMeasurementReferences(
        _REFERENCE_ID,
        plan.seven_path_plan_digest,
        input_digests[0],
        input_digests[1],
        input_digests[2],
        input_digests[3],
        references,
        order_digest,
        True,
        _digest(payload),
    )
