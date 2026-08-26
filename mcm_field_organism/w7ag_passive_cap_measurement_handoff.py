"""Passive W7-AG measurement handoff from isolated W7-AE CAP states."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math

import numpy as np

from .w7ae_cap_seven_path_consumer import (
    W7AECAPCheckpointResult,
    W7AECAPProductionResult,
    W7AECAPSevenPathResult,
    W7AECAPState,
    _build_state,
    _clone_state,
    _produce,
)
from .w7m_capacity_function_matrix import (
    W7MCapacityFunctionMatrixAdapter,
    W7MRegionalCapacityLedger,
    align_w7m_fast_state,
    measure_w7m_regional_capacity,
)
from .w7p_measurement_compositor import (
    W7PCapacityMeasurement,
    W7PFieldMeasurement,
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


class W7AGPassiveCAPMeasurementError(ValueError):
    """Raised when passive CAP measurement leaves the W7-AF contract."""


_HANDOFF_ID = "w7ag.passive-cap-measurement-handoff.v1"
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_MASS_ABS_TOLERANCE = 1e-12


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
        raise W7AGPassiveCAPMeasurementError(f"{role} must be finite")
    return result


def _sample_payload(
    tick: int,
    s_values: tuple[float, ...],
    h_values: tuple[float, ...],
    m_values: tuple[float, ...],
) -> dict[str, object]:
    return {
        "tick": tick,
        "s_values": s_values,
        "h_values": h_values,
        "m_values": m_values,
    }


@dataclass(frozen=True, slots=True)
class W7AGCAPTrajectorySample:
    """One read-only S/H/M sample at an actual receptor completion boundary."""

    tick: int
    s_values: tuple[float, ...]
    h_values: tuple[float, ...]
    m_values: tuple[float, ...]
    sample_digest: str

    def __post_init__(self) -> None:
        if isinstance(self.tick, bool) or not isinstance(self.tick, int):
            raise W7AGPassiveCAPMeasurementError("sample tick must be an integer")
        s_values = _finite_vector(self.s_values, "sample S")
        h_values = _finite_vector(self.h_values, "sample H")
        m_values = _finite_vector(self.m_values, "sample M")
        if len({len(s_values), len(h_values), len(m_values)}) != 1:
            raise W7AGPassiveCAPMeasurementError(
                "sample components differ from field geometry"
            )
        payload = _sample_payload(self.tick, s_values, h_values, m_values)
        if self.sample_digest != _digest(payload):
            raise W7AGPassiveCAPMeasurementError(
                "trajectory sample digest does not match its content"
            )
        object.__setattr__(self, "s_values", s_values)
        object.__setattr__(self, "h_values", h_values)
        object.__setattr__(self, "m_values", m_values)


def _measurement_payload(
    plan_checkpoint_digest: str,
    cap_checkpoint_digest: str,
    path_id: str,
    checkpoint: int,
    main_state_digest: str,
    aligned_state_digest: str,
    sample_digests: tuple[str, ...],
    measurement_production_digest: str,
    field_measurement: W7PFieldMeasurement,
    capacity_measurement: W7PCapacityMeasurement,
    regional_ledger: W7MRegionalCapacityLedger,
) -> dict[str, object]:
    return {
        "plan_checkpoint_digest": plan_checkpoint_digest,
        "cap_checkpoint_digest": cap_checkpoint_digest,
        "path_id": path_id,
        "checkpoint": checkpoint,
        "main_state_digest": main_state_digest,
        "aligned_state_digest": aligned_state_digest,
        "sample_digests": sample_digests,
        "measurement_production_digest": measurement_production_digest,
        "field_measurement": {
            "model_id": field_measurement.model_id,
            "path_id": field_measurement.path_id,
            "checkpoint": field_measurement.checkpoint,
            "probe_S_linf": field_measurement.probe_S_linf,
            "probe_H_linf": field_measurement.probe_H_linf,
            "probe_SH_trajectory_l2": (
                field_measurement.probe_SH_trajectory_l2
            ),
            "probe_observation_ticks": field_measurement.probe_observation_ticks,
        },
        "capacity_measurement": {
            "model_id": capacity_measurement.model_id,
            "total_mass": capacity_measurement.total_mass,
            "total_free_capacity": capacity_measurement.total_free_capacity,
            "balance_residual": capacity_measurement.balance_residual,
        },
        "regional_ledger": {
            role: getattr(regional_ledger, role)
            for role in regional_ledger.__dataclass_fields__
        },
        "returns_to_main": False,
    }


@dataclass(frozen=True, slots=True)
class W7AGCAPMeasurementResult:
    """One aligned CAP measurement branch without path interpretation."""

    plan_checkpoint_digest: str
    cap_checkpoint_digest: str
    path_id: str
    checkpoint: int
    main_state: W7AECAPState = field(repr=False)
    aligned_state: W7AECAPState = field(repr=False)
    samples: tuple[W7AGCAPTrajectorySample, ...] = field(repr=False)
    measurement_production: W7AECAPProductionResult = field(repr=False)
    field_measurement: W7PFieldMeasurement
    capacity_measurement: W7PCapacityMeasurement
    regional_ledger: W7MRegionalCapacityLedger
    measurement_result_digest: str

    def __post_init__(self) -> None:
        samples = tuple(self.samples)
        ticks = tuple(item.tick for item in samples)
        if (
            not self.plan_checkpoint_digest
            or not self.cap_checkpoint_digest
            or self.path_id not in _PATH_IDS
            or self.checkpoint not in range(5)
            or self.main_state.path_id != self.path_id
            or self.aligned_state.path_id != self.path_id
            or self.main_state is self.aligned_state
            or self.main_state.field is self.aligned_state.field
            or not samples
            or ticks != tuple(sorted(set(ticks)))
            or self.measurement_production.initial_state is not self.aligned_state
            or self.measurement_production.path_id != self.path_id
            or self.field_measurement.model_id != "cap"
            or self.field_measurement.path_id != self.path_id
            or self.field_measurement.checkpoint != self.checkpoint
            or self.field_measurement.probe_observation_ticks != ticks
            or self.capacity_measurement.model_id != "cap"
        ):
            raise W7AGPassiveCAPMeasurementError(
                "CAP measurement result binding is invalid"
            )
        payload = _measurement_payload(
            self.plan_checkpoint_digest,
            self.cap_checkpoint_digest,
            self.path_id,
            self.checkpoint,
            self.main_state.state_digest,
            self.aligned_state.state_digest,
            tuple(item.sample_digest for item in samples),
            self.measurement_production.production_digest,
            self.field_measurement,
            self.capacity_measurement,
            self.regional_ledger,
        )
        if self.measurement_result_digest != _digest(payload):
            raise W7AGPassiveCAPMeasurementError(
                "CAP measurement result digest does not match its content"
            )
        object.__setattr__(self, "samples", samples)


def _aligned_measurement_state(
    adapter: W7MCapacityFunctionMatrixAdapter,
    checkpoint: W7AECAPCheckpointResult,
) -> W7AECAPState:
    copied = _clone_state(adapter, checkpoint.main_state)
    before_mass = tuple(item.mass for item in copied.field.substrate.masses)
    if copied.field.last_distribution is None:
        if (
            checkpoint.path_id not in {"ua", "ub", "ug"}
            or checkpoint.checkpoint != 0
            or copied.continuation_binding is not None
            or any(
                item.activation != 0.0 or item.afterimage != 0.0
                for item in copied.field.layer.neurons
            )
        ):
            raise W7AGPassiveCAPMeasurementError(
                "only U checkpoint zero may remain an initial measurement state"
            )
        aligned = copied
    else:
        intervention = align_w7m_fast_state(
            copied.field,
            adapter.runtime_contract,
        )
        aligned = _build_state(
            adapter,
            checkpoint.path_id,
            checkpoint.tick,
            intervention.field,
            intervention.continuation_binding,
        )
    after_mass = tuple(item.mass for item in aligned.field.substrate.masses)
    if (
        before_mass != after_mass
        or any(
            item.activation != 0.0 or item.afterimage != 0.0
            for item in aligned.field.layer.neurons
        )
        or aligned.field is checkpoint.main_state.field
        or aligned.field is checkpoint.probe_initial_state.field
    ):
        raise W7AGPassiveCAPMeasurementError(
            "fast-state measurement alignment changed M or crossed branch roles"
        )
    return aligned


def _capacity_measurement(
    adapter: W7MCapacityFunctionMatrixAdapter,
    state: W7AECAPState,
) -> tuple[W7PCapacityMeasurement, W7MRegionalCapacityLedger]:
    ledger = measure_w7m_regional_capacity(
        state.field,
        adapter.regions,
        adapter.runtime_contract,
    )
    total_capacity = (
        len(state.field.layer.neurons) * adapter.runtime_contract.site_capacity
    )
    residual = abs(ledger.total_mass + ledger.total_free_capacity - total_capacity)
    return (
        W7PCapacityMeasurement(
            "cap",
            ledger.total_mass,
            ledger.total_free_capacity,
            residual,
        ),
        ledger,
    )


def _field_measurement(
    path_id: str,
    checkpoint: int,
    samples: tuple[W7AGCAPTrajectorySample, ...],
) -> W7PFieldMeasurement:
    s_linf = max(abs(value) for sample in samples for value in sample.s_values)
    h_linf = max(abs(value) for sample in samples for value in sample.h_values)
    trajectory_l2 = math.sqrt(
        math.fsum(
            value * value
            for sample in samples
            for values in (sample.s_values, sample.h_values)
            for value in values
        )
    )
    return W7PFieldMeasurement(
        "cap",
        path_id,
        checkpoint,
        s_linf,
        h_linf,
        trajectory_l2,
        tuple(item.tick for item in samples),
    )


def _measure_checkpoint(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    plan_checkpoint: W7YCheckpointPlan,
    cap_checkpoint: W7AECAPCheckpointResult,
    *,
    _refinement: int = 1,
    _integration_observer=None,
) -> W7AGCAPMeasurementResult:
    if (
        plan_checkpoint.path_id != cap_checkpoint.path_id
        or plan_checkpoint.checkpoint != cap_checkpoint.checkpoint
        or plan_checkpoint.checkpoint_digest
        != cap_checkpoint.plan_checkpoint_digest
    ):
        raise W7AGPassiveCAPMeasurementError(
            "CAP measurement checkpoint differs from W7-Y"
        )
    aligned = _aligned_measurement_state(adapter, cap_checkpoint)
    capacity, ledger = _capacity_measurement(adapter, aligned)
    observed: list[W7AGCAPTrajectorySample] = []

    def observe(
        tick: int,
        activation: np.ndarray,
        afterimage: np.ndarray,
        mass: np.ndarray,
    ) -> None:
        if activation.flags.writeable or afterimage.flags.writeable or mass.flags.writeable:
            raise W7AGPassiveCAPMeasurementError(
                "CAP trajectory observer received writable arrays"
            )
        s_values = _finite_vector(activation, "observed S")
        h_values = _finite_vector(afterimage, "observed H")
        m_values = _finite_vector(mass, "observed M")
        payload = _sample_payload(tick, s_values, h_values, m_values)
        observed.append(
            W7AGCAPTrajectorySample(
                tick,
                s_values,
                h_values,
                m_values,
                _digest(payload),
            )
        )
        return None

    production = _produce(
        adapter,
        authorization,
        plan_checkpoint.probe,
        aligned,
        _refinement=_refinement,
        _state_observer=observe,
        _integration_observer=_integration_observer,
    )
    samples = tuple(observed)
    if (
        not samples
        or samples[-1].tick != plan_checkpoint.probe.interval[1]
        or tuple(item.tick for item in samples)
        != tuple(sorted({item.tick for item in samples}))
    ):
        raise W7AGPassiveCAPMeasurementError(
            "CAP trajectory observation boundaries are incomplete"
        )
    field_measurement = _field_measurement(
        cap_checkpoint.path_id,
        cap_checkpoint.checkpoint,
        samples,
    )
    payload = _measurement_payload(
        plan_checkpoint.checkpoint_digest,
        cap_checkpoint.checkpoint_result_digest,
        cap_checkpoint.path_id,
        cap_checkpoint.checkpoint,
        cap_checkpoint.main_state.state_digest,
        aligned.state_digest,
        tuple(item.sample_digest for item in samples),
        production.production_digest,
        field_measurement,
        capacity,
        ledger,
    )
    return W7AGCAPMeasurementResult(
        plan_checkpoint.checkpoint_digest,
        cap_checkpoint.checkpoint_result_digest,
        cap_checkpoint.path_id,
        cap_checkpoint.checkpoint,
        cap_checkpoint.main_state,
        aligned,
        samples,
        production,
        field_measurement,
        capacity,
        ledger,
        _digest(payload),
    )


def _result_payload(
    plan_digest: str,
    cap_consumption_digest: str,
    measurements: tuple[W7AGCAPMeasurementResult, ...],
    order_countercontrol_digest: str,
    observer_passivity_digest: str,
) -> dict[str, object]:
    return {
        "handoff_id": _HANDOFF_ID,
        "plan_digest": plan_digest,
        "cap_consumption_digest": cap_consumption_digest,
        "measurement_result_digests": tuple(
            item.measurement_result_digest for item in measurements
        ),
        "order_countercontrol_digest": order_countercontrol_digest,
        "observer_passivity_digest": observer_passivity_digest,
        "p0_absolute_comparison_ready": False,
    }


@dataclass(frozen=True, slots=True)
class W7AGPassiveCAPMeasurementHandoff:
    """Complete passive CAP measurement handoff without evaluation."""

    handoff_id: str
    plan_digest: str
    cap_consumption_digest: str
    measurements: tuple[W7AGCAPMeasurementResult, ...] = field(repr=False)
    order_countercontrol_digest: str
    observer_passivity_digest: str
    p0_absolute_comparison_ready: bool
    measurement_handoff_digest: str

    def __post_init__(self) -> None:
        measurements = tuple(self.measurements)
        expected_roles = tuple(
            (path_id, checkpoint)
            for path_id in _PATH_IDS
            for checkpoint in range(5)
        )
        if (
            self.handoff_id != _HANDOFF_ID
            or not self.plan_digest
            or not self.cap_consumption_digest
            or tuple((item.path_id, item.checkpoint) for item in measurements)
            != expected_roles
            or not self.order_countercontrol_digest
            or not self.observer_passivity_digest
            or self.p0_absolute_comparison_ready is not False
        ):
            raise W7AGPassiveCAPMeasurementError(
                "CAP measurement handoff binding is invalid"
            )
        payload = _result_payload(
            self.plan_digest,
            self.cap_consumption_digest,
            measurements,
            self.order_countercontrol_digest,
            self.observer_passivity_digest,
        )
        if self.measurement_handoff_digest != _digest(payload):
            raise W7AGPassiveCAPMeasurementError(
                "CAP measurement handoff digest does not match its content"
            )
        object.__setattr__(self, "measurements", measurements)


@dataclass(frozen=True, slots=True)
class _W7AGMeasurementMaterialization:
    """Private canonical measurement phase before its audits."""

    plan_digest: str
    cap_digest: str
    refinement: int
    measurements: tuple[W7AGCAPMeasurementResult, ...] = field(repr=False)

    def __post_init__(self) -> None:
        measurements = tuple(self.measurements)
        expected = tuple(
            (path_id, checkpoint)
            for path_id in _PATH_IDS
            for checkpoint in range(5)
        )
        if (
            not self.plan_digest
            or not self.cap_digest
            or self.refinement not in {1, 2, 4}
            or isinstance(self.refinement, bool)
            or tuple(
                (item.path_id, item.checkpoint) for item in measurements
            )
            != expected
        ):
            raise W7AGPassiveCAPMeasurementError(
                "CAP measurement materialization binding is invalid"
            )
        object.__setattr__(self, "measurements", measurements)


@dataclass(frozen=True, slots=True)
class _W7AGMeasurementOrderAudit:
    order_countercontrol_digest: str
    refinement: int

    def __post_init__(self) -> None:
        if (
            not self.order_countercontrol_digest
            or self.refinement not in {1, 2, 4}
            or isinstance(self.refinement, bool)
        ):
            raise W7AGPassiveCAPMeasurementError(
                "CAP measurement-order audit binding is invalid"
            )


@dataclass(frozen=True, slots=True)
class _W7AGObserverPassivityAudit:
    observer_passivity_digest: str
    refinement: int

    def __post_init__(self) -> None:
        if (
            not self.observer_passivity_digest
            or self.refinement not in {1, 2, 4}
            or isinstance(self.refinement, bool)
        ):
            raise W7AGPassiveCAPMeasurementError(
                "CAP observer-passivity audit binding is invalid"
            )


def _validate_w7ag_inputs(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    cap_result: W7AECAPSevenPathResult,
    *,
    _refinement: int = 1,
    _integration_observer=None,
) -> None:
    if (
        not isinstance(adapter, W7MCapacityFunctionMatrixAdapter)
        or not isinstance(family, W7WSymmetricSourceFamily)
        or not isinstance(authorization, W7WSourceAuthorization)
        or not isinstance(plan, W7YSevenPathSourcePlan)
        or not isinstance(cap_result, W7AECAPSevenPathResult)
    ):
        raise W7AGPassiveCAPMeasurementError(
            "CAP measurement requires complete W7-M/W/Y/AE bindings"
        )
    if _refinement not in {1, 2, 4} or isinstance(_refinement, bool):
        raise W7AGPassiveCAPMeasurementError(
            "CAP refinement must be one of 1, 2, or 4"
        )
    if _integration_observer is not None and not callable(
        _integration_observer
    ):
        raise W7AGPassiveCAPMeasurementError(
            "CAP integration observer must be callable"
        )
    expected_plan = build_w7y_seven_path_source_plan(
        adapter,
        family,
        authorization,
    )
    if (
        plan.paths != expected_plan.paths
        or plan.seven_path_plan_digest != expected_plan.seven_path_plan_digest
        or cap_result.plan_digest != plan.seven_path_plan_digest
    ):
        raise W7AGPassiveCAPMeasurementError(
            "CAP measurement input digests differ"
        )


def _measurement_tasks(
    plan: W7YSevenPathSourcePlan,
    cap_result: W7AECAPSevenPathResult,
):
    return tuple(
        (plan_checkpoint, cap_checkpoint)
        for plan_path, cap_path in zip(
            plan.paths,
            cap_result.path_results,
            strict=True,
        )
        for plan_checkpoint, cap_checkpoint in zip(
            plan_path.checkpoints,
            cap_path.checkpoints,
            strict=True,
        )
    )


def _materialize_w7ag_measurements(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    cap_result: W7AECAPSevenPathResult,
    *,
    _refinement: int = 1,
    _integration_observer=None,
) -> _W7AGMeasurementMaterialization:
    """Materialize only the 35 canonical CAP measurement branches."""

    _validate_w7ag_inputs(
        adapter,
        family,
        authorization,
        plan,
        cap_result,
        _refinement=_refinement,
        _integration_observer=_integration_observer,
    )
    cap_digest = cap_result.cap_seven_path_consumption_digest
    tasks = _measurement_tasks(plan, cap_result)
    measurements = tuple(
        _measure_checkpoint(
            adapter,
            authorization,
            plan_item,
            cap_item,
            _refinement=_refinement,
            _integration_observer=_integration_observer,
        )
        for plan_item, cap_item in tasks
    )
    if cap_result.cap_seven_path_consumption_digest != cap_digest:
        raise W7AGPassiveCAPMeasurementError(
            "CAP measurement materialization mutated the W7-AE result"
        )
    return _W7AGMeasurementMaterialization(
        plan.seven_path_plan_digest,
        cap_digest,
        _refinement,
        measurements,
    )


def _audit_w7ag_measurement_order(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    tasks,
    materialization: _W7AGMeasurementMaterialization,
) -> _W7AGMeasurementOrderAudit:
    measurements = materialization.measurements
    reversed_measurements = tuple(
        _measure_checkpoint(
            adapter,
            authorization,
            plan_item,
            cap_item,
            _refinement=materialization.refinement,
        )
        for plan_item, cap_item in reversed(tasks)
    )
    actual = {
        (item.path_id, item.checkpoint): item.measurement_result_digest
        for item in measurements
    }
    if any(
        actual[(item.path_id, item.checkpoint)] != item.measurement_result_digest
        for item in reversed_measurements
    ):
        raise W7AGPassiveCAPMeasurementError(
            "CAP measurement order changed a result"
        )
    order_payload = {
        "canonical_measurement_digests": tuple(
            item.measurement_result_digest for item in measurements
        ),
        "reverse_role_digests": tuple(
            actual[(path_id, checkpoint)]
            for path_id, checkpoint in reversed(
                tuple(actual)
            )
        ),
    }
    return _W7AGMeasurementOrderAudit(
        _digest(order_payload),
        materialization.refinement,
    )


def _audit_w7ag_observer_passivity(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    materialization: _W7AGMeasurementMaterialization,
) -> _W7AGObserverPassivityAudit:
    measurements = materialization.measurements
    first = measurements[0]
    unobserved = _produce(
        adapter,
        authorization,
        plan.paths[0].checkpoints[0].probe,
        _clone_state(adapter, first.aligned_state),
        _refinement=materialization.refinement,
    )
    if (
        unobserved.production_digest
        != first.measurement_production.production_digest
        or unobserved.end_state.state_digest
        != first.measurement_production.end_state.state_digest
    ):
        raise W7AGPassiveCAPMeasurementError(
            "passive observer changed CAP production"
        )
    passivity_digest = _digest(
        {
            "path_id": first.path_id,
            "checkpoint": first.checkpoint,
            "observed_production_digest": (
                first.measurement_production.production_digest
            ),
            "unobserved_production_digest": unobserved.production_digest,
            "end_state_digest": unobserved.end_state.state_digest,
        }
    )
    return _W7AGObserverPassivityAudit(
        passivity_digest,
        materialization.refinement,
    )


def _finalize_w7ag_measurement_audits(
    plan: W7YSevenPathSourcePlan,
    cap_result: W7AECAPSevenPathResult,
    materialization: _W7AGMeasurementMaterialization,
    order_audit: _W7AGMeasurementOrderAudit,
    passivity_audit: _W7AGObserverPassivityAudit,
) -> W7AGPassiveCAPMeasurementHandoff:
    if (
        not isinstance(order_audit, _W7AGMeasurementOrderAudit)
        or not isinstance(passivity_audit, _W7AGObserverPassivityAudit)
        or order_audit.refinement != materialization.refinement
        or passivity_audit.refinement != materialization.refinement
    ):
        raise W7AGPassiveCAPMeasurementError(
            "CAP split measurement audits differ"
        )
    measurements = materialization.measurements
    if (
        materialization.plan_digest != plan.seven_path_plan_digest
        or cap_result.cap_seven_path_consumption_digest
        != materialization.cap_digest
    ):
        raise W7AGPassiveCAPMeasurementError(
            "CAP measurement mutated the W7-AE result"
        )
    payload = _result_payload(
        plan.seven_path_plan_digest,
        materialization.cap_digest,
        measurements,
        order_audit.order_countercontrol_digest,
        passivity_audit.observer_passivity_digest,
    )
    return W7AGPassiveCAPMeasurementHandoff(
        _HANDOFF_ID,
        plan.seven_path_plan_digest,
        materialization.cap_digest,
        measurements,
        order_audit.order_countercontrol_digest,
        passivity_audit.observer_passivity_digest,
        False,
        _digest(payload),
    )


def _audit_w7ag_measurements(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    cap_result: W7AECAPSevenPathResult,
    materialization: _W7AGMeasurementMaterialization,
) -> W7AGPassiveCAPMeasurementHandoff:
    """Run split measurement controls and finalize one materialization."""

    if not isinstance(materialization, _W7AGMeasurementMaterialization):
        raise W7AGPassiveCAPMeasurementError(
            "CAP measurement audit requires a materialization"
        )
    _validate_w7ag_inputs(
        adapter,
        family,
        authorization,
        plan,
        cap_result,
        _refinement=materialization.refinement,
    )
    tasks = _measurement_tasks(plan, cap_result)
    order_audit = _audit_w7ag_measurement_order(
        adapter,
        authorization,
        tasks,
        materialization,
    )
    passivity_audit = _audit_w7ag_observer_passivity(
        adapter,
        authorization,
        plan,
        materialization,
    )
    return _finalize_w7ag_measurement_audits(
        plan,
        cap_result,
        materialization,
        order_audit,
        passivity_audit,
    )


def compose_w7ag_passive_cap_measurement_handoff(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    cap_result: W7AECAPSevenPathResult,
    *,
    _refinement: int = 1,
    _integration_observer=None,
) -> W7AGPassiveCAPMeasurementHandoff:
    """Build 35 aligned passive CAP measurement branches in memory."""

    materialization = _materialize_w7ag_measurements(
        adapter,
        family,
        authorization,
        plan,
        cap_result,
        _refinement=_refinement,
        _integration_observer=_integration_observer,
    )
    return _audit_w7ag_measurements(
        adapter,
        family,
        authorization,
        plan,
        cap_result,
        materialization,
    )
