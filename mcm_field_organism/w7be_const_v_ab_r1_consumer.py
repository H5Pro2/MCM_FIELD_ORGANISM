"""Private W7-BE CONST-V consumer for exactly the AB path at R1."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
import hashlib
import json
import math

import numpy as np

from .field_step_time import MCMFieldStepTime
from .mcm_f3_controlled_history_source import mcm_f3_receptor_sequences_digest
from .mcm_f3_history_run import align_mcm_f3_fast_state
from .mcm_f3_runtime import MCMF3AdvanceDiagnostics
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff import handoff_receptor_completion_groups
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs
from .w7bd_const_v_runtime_adapter import (
    W7BDConstVRuntimeAdapter,
    advance_w7bd_const_v_transient,
    prepare_w7bd_const_v_initial_field,
)
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamily,
    W7WSymmetricSourceFamilyError,
    authorize_w7w_source_segment,
)
from .w7y_seven_path_source_plan import (
    W7YSevenPathSourcePlan,
    W7YSourceSegmentRef,
)


class W7BEConstVABR1ConsumerError(ValueError):
    """Raised when the one-path integration leaves the W7-BC boundary."""


_CONSUMER_ID = "w7be.const-v-ab-r1-single-path-consumer.v1"
_PATH_ID = "ab"
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_REFINEMENTS = (1, 2, 4)
_REFINEMENT = 1
_MASS_ABS_TOLERANCE = 1e-12


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _field_digest(current: SharedMCMField) -> str:
    if current.last_distribution is not None:
        return current.snapshot().digest()
    if current.substrate is None:
        raise W7BEConstVABR1ConsumerError("CONST-V state lost its substrate")
    return _digest(
        {
            "role": "w7be.initial-const-v-field.v1",
            "layer_digest": current.layer.digest(),
            "docks": tuple(
                (
                    dock.dock_id,
                    dock.dock_map.modality_id,
                    tuple(dock.dock_map.pairs),
                )
                for dock in current.docks
            ),
            "arm": current.substrate.arm.canonical_payload(),
            "scalar": tuple(item.mass for item in current.substrate.masses),
            "edge_inventory_digest": current.substrate.edge_inventory_digest,
        }
    )


def _state_payload(
    matrix_digest: str,
    runtime_adapter_digest: str,
    path_id: str,
    refinement: int,
    tick: int,
    field_digest: str,
) -> dict[str, object]:
    return {
        "matrix_digest": matrix_digest,
        "runtime_adapter_digest": runtime_adapter_digest,
        "path_id": path_id,
        "refinement": refinement,
        "tick": tick,
        "field_digest": field_digest,
    }


@dataclass(frozen=True, slots=True)
class W7BEConstVState:
    """One private S/H/technical-scalar state on the AB/R1 chain."""

    matrix_digest: str
    runtime_adapter_digest: str
    path_id: str
    refinement: int
    tick: int
    field: SharedMCMField = field(repr=False)
    state_digest: str

    def __post_init__(self) -> None:
        if (
            not self.matrix_digest
            or not self.runtime_adapter_digest
            or self.path_id not in _PATH_IDS
            or self.refinement not in _REFINEMENTS
            or isinstance(self.tick, bool)
            or not isinstance(self.tick, int)
            or self.tick < 0
            or not isinstance(self.field, SharedMCMField)
            or self.field.substrate is None
        ):
            raise W7BEConstVABR1ConsumerError("CONST-V state binding is invalid")
        payload = _state_payload(
            self.matrix_digest,
            self.runtime_adapter_digest,
            self.path_id,
            self.refinement,
            self.tick,
            _field_digest(self.field),
        )
        if self.state_digest != _digest(payload):
            raise W7BEConstVABR1ConsumerError(
                "CONST-V state digest does not match its content"
            )


def _build_state(
    matrix: W7MCapacityFunctionMatrixAdapter,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    path_id: str,
    tick: int,
    current: SharedMCMField,
    refinement: int = _REFINEMENT,
) -> W7BEConstVState:
    payload = _state_payload(
        matrix.matrix_digest,
        runtime_adapter.adapter_digest,
        path_id,
        refinement,
        tick,
        _field_digest(current),
    )
    return W7BEConstVState(
        matrix.matrix_digest,
        runtime_adapter.adapter_digest,
        path_id,
        refinement,
        tick,
        current,
        _digest(payload),
    )


def _assert_invariants(
    matrix: W7MCapacityFunctionMatrixAdapter,
    state: W7BEConstVState,
) -> None:
    substrate = state.field.substrate
    if substrate is None:
        raise W7BEConstVABR1ConsumerError("CONST-V state lost its substrate")
    scalar = tuple(item.mass for item in substrate.masses)
    if (
        substrate.arm.arm_id != "w7n.const-v"
        or substrate.arm.lambda_sm_per_second != 0.5
        or substrate.arm.kappa != 0.5
        or substrate.arm.eta != 1.0
        or abs(math.fsum(scalar) - 1.0) > _MASS_ABS_TOLERANCE
        or min(scalar) < -_MASS_ABS_TOLERANCE
        or substrate.edge_inventory_digest
        != matrix.initial_field.substrate.edge_inventory_digest
        or tuple(item.neuron_id for item in state.field.layer.neurons)
        != tuple(item.neuron_id for item in matrix.initial_field.layer.neurons)
    ):
        raise W7BEConstVABR1ConsumerError(
            "CONST-V model, mass, or geometry invariant failed"
        )


def _known_source_digests(
    matrix: W7MCapacityFunctionMatrixAdapter,
) -> frozenset[str]:
    source = matrix.source
    return frozenset(
        (source.contact_a_digest,)
        + source.contact_b_step_digests
        + source.interruption_step_digests
        + source.probe_digests
    )


def _validate_segment(
    matrix: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    segment: W7YSourceSegmentRef,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    sequences = tuple(sorted(segment.sequences, key=lambda item: item.modality_id))
    if (
        segment.path_id not in _PATH_IDS
        or len(sequences) != 2
        or any(not isinstance(item, ReceptorTimeSequence) for item in sequences)
        or mcm_f3_receptor_sequences_digest(sequences) != segment.source_digest
    ):
        raise W7BEConstVABR1ConsumerError(
            "CONST-V segment differs from its W7-Y source binding"
        )
    if segment.source_digest not in _known_source_digests(matrix):
        try:
            authorize_w7w_source_segment(
                matrix,
                authorization,
                segment.source_digest,
                segment.path_id,
                segment.interval,
            )
        except W7WSymmetricSourceFamilyError as exc:
            raise W7BEConstVABR1ConsumerError(str(exc)) from exc
    elif segment.authorization_role_id is not None:
        raise W7BEConstVABR1ConsumerError(
            "existing CONST-V source cannot carry additive authorization"
        )
    return sequences


def _diagnostics_payload(diagnostics: MCMF3AdvanceDiagnostics) -> dict[str, object]:
    return {
        role: getattr(diagnostics, role)
        for role in diagnostics.__dataclass_fields__
    }


@dataclass(frozen=True, slots=True)
class W7BEConstVProduction:
    """One immutable CONST-V advance over one W7-Y source segment."""

    segment_digest: str
    source_digest: str
    interval: tuple[int, int]
    assigned_event_count: int
    initial_state: W7BEConstVState = field(repr=False)
    end_state: W7BEConstVState = field(repr=False)
    diagnostics: MCMF3AdvanceDiagnostics
    production_digest: str

    def __post_init__(self) -> None:
        payload = {
            "segment_digest": self.segment_digest,
            "source_digest": self.source_digest,
            "interval": self.interval,
            "assigned_event_count": self.assigned_event_count,
            "initial_state_digest": self.initial_state.state_digest,
            "end_state_digest": self.end_state.state_digest,
            "diagnostics": _diagnostics_payload(self.diagnostics),
        }
        if (
            not self.segment_digest
            or not self.source_digest
            or self.interval != (self.initial_state.tick, self.end_state.tick)
            or isinstance(self.assigned_event_count, bool)
            or self.assigned_event_count <= 0
            or not isinstance(self.diagnostics, MCMF3AdvanceDiagnostics)
            or self.diagnostics.method_id != "ssprk33"
            or self.production_digest != _digest(payload)
        ):
            raise W7BEConstVABR1ConsumerError(
                "CONST-V production binding is invalid"
            )


def _produce(
    matrix: W7MCapacityFunctionMatrixAdapter,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    authorization: W7WSourceAuthorization,
    segment: W7YSourceSegmentRef,
    state: W7BEConstVState,
    *,
    state_observer=None,
    refinement: int | None = None,
) -> W7BEConstVProduction:
    if segment.interval[0] != state.tick:
        raise W7BEConstVABR1ConsumerError(
            "CONST-V source segment does not continue its state"
        )
    if segment.path_id != state.path_id:
        raise W7BEConstVABR1ConsumerError(
            "CONST-V source segment belongs to another path"
        )
    sequences = _validate_segment(matrix, authorization, segment)
    start_tick, end_tick = segment.interval
    step = MCMFieldStepTime(
        matrix.source.clock_id,
        start_tick,
        end_tick,
        matrix.source.ticks_per_second,
    )
    handoff = handoff_receptor_completion_groups(sequences, (step,))
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != handoff.source_event_count
        or len(handoff.batches) != 1
    ):
        raise W7BEConstVABR1ConsumerError(
            "CONST-V receptor completion handoff is incomplete"
        )
    trajectory = map_proposal_batch_to_transient_docks(
        handoff.batches[0],
        state.field.docks,
    )
    transient_inputs = project_transient_docks_to_neuron_inputs(
        trajectory,
        state.field.docks,
    )
    distribution = ReceptorDistribution(
        CommonFieldTime(matrix.source.clock_id, start_tick, end_tick),
        (),
    )
    before = state.state_digest
    runtime = advance_w7bd_const_v_transient(
        runtime_adapter,
        state.field,
        distribution,
        transient_inputs,
        refinement=state.refinement if refinement is None else refinement,
        _state_observer=state_observer,
    )
    if state.state_digest != before:
        raise W7BEConstVABR1ConsumerError(
            "CONST-V production mutated its input state"
        )
    end_state = _build_state(
        matrix,
        runtime_adapter,
        state.path_id,
        end_tick,
        runtime.field,
        state.refinement if refinement is None else refinement,
    )
    _assert_invariants(matrix, end_state)
    payload = {
        "segment_digest": segment.segment_digest,
        "source_digest": segment.source_digest,
        "interval": segment.interval,
        "assigned_event_count": handoff.assigned_event_count,
        "initial_state_digest": state.state_digest,
        "end_state_digest": end_state.state_digest,
        "diagnostics": _diagnostics_payload(runtime.diagnostics),
    }
    return W7BEConstVProduction(
        segment.segment_digest,
        segment.source_digest,
        segment.interval,
        handoff.assigned_event_count,
        state,
        end_state,
        runtime.diagnostics,
        _digest(payload),
    )


def _finite_vector(values, role: str) -> tuple[float, ...]:
    result = tuple(float(value) for value in values)
    if not result or any(not math.isfinite(value) for value in result):
        raise W7BEConstVABR1ConsumerError(f"{role} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class W7BEConstVRawSample:
    """One raw S/H/technical-scalar sample at a real runtime boundary."""

    tick: int
    s_values: tuple[float, ...]
    h_values: tuple[float, ...]
    technical_scalar_values: tuple[float, ...]
    sample_digest: str

    def __post_init__(self) -> None:
        s_values = _finite_vector(self.s_values, "sample S")
        h_values = _finite_vector(self.h_values, "sample H")
        scalar = _finite_vector(
            self.technical_scalar_values,
            "sample technical scalar",
        )
        payload = {
            "tick": self.tick,
            "s_values": s_values,
            "h_values": h_values,
            "technical_scalar_values": scalar,
        }
        if (
            isinstance(self.tick, bool)
            or not isinstance(self.tick, int)
            or len({len(s_values), len(h_values), len(scalar)}) != 1
            or self.sample_digest != _digest(payload)
        ):
            raise W7BEConstVABR1ConsumerError("raw sample binding is invalid")
        object.__setattr__(self, "s_values", s_values)
        object.__setattr__(self, "h_values", h_values)
        object.__setattr__(self, "technical_scalar_values", scalar)


@dataclass(frozen=True, slots=True)
class W7BEConstVCheckpointMeasurement:
    """One isolated aligned probe and its raw trajectory samples."""

    plan_checkpoint_digest: str
    checkpoint: int
    tick: int
    main_state: W7BEConstVState = field(repr=False)
    aligned_probe_initial_state: W7BEConstVState = field(repr=False)
    probe_production: W7BEConstVProduction = field(repr=False)
    samples: tuple[W7BEConstVRawSample, ...] = field(repr=False)
    checkpoint_measurement_digest: str

    def __post_init__(self) -> None:
        samples = tuple(self.samples)
        ticks = tuple(item.tick for item in samples)
        payload = {
            "plan_checkpoint_digest": self.plan_checkpoint_digest,
            "checkpoint": self.checkpoint,
            "tick": self.tick,
            "main_state_digest": self.main_state.state_digest,
            "aligned_probe_initial_state_digest": (
                self.aligned_probe_initial_state.state_digest
            ),
            "probe_production_digest": self.probe_production.production_digest,
            "sample_digests": tuple(item.sample_digest for item in samples),
            "probe_returns_to_main": False,
        }
        if (
            not self.plan_checkpoint_digest
            or self.checkpoint not in range(5)
            or self.tick != (self.checkpoint + 4) * 1_000_000
            or self.main_state is self.aligned_probe_initial_state
            or self.main_state.field is self.aligned_probe_initial_state.field
            or self.probe_production.initial_state
            is not self.aligned_probe_initial_state
            or not samples
            or ticks != tuple(sorted(set(ticks)))
            or ticks[-1] != self.probe_production.interval[1]
            or self.checkpoint_measurement_digest != _digest(payload)
        ):
            raise W7BEConstVABR1ConsumerError(
                "CONST-V checkpoint measurement binding is invalid"
            )
        object.__setattr__(self, "samples", samples)


def _aligned_probe_state(
    matrix: W7MCapacityFunctionMatrixAdapter,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    main_state: W7BEConstVState,
) -> W7BEConstVState:
    copied = copy.deepcopy(main_state.field)
    before_scalar = tuple(item.mass for item in copied.substrate.masses)
    aligned = align_mcm_f3_fast_state(copied)
    after_scalar = tuple(item.mass for item in aligned.substrate.masses)
    result = _build_state(
        matrix,
        runtime_adapter,
        main_state.path_id,
        main_state.tick,
        aligned,
        main_state.refinement,
    )
    if (
        before_scalar != after_scalar
        or result.field is main_state.field
        or any(
            item.activation != 0.0 or item.afterimage != 0.0
            for item in result.field.layer.neurons
        )
    ):
        raise W7BEConstVABR1ConsumerError(
            "CONST-V checkpoint alignment changed the technical scalar"
        )
    return result


def _measure_checkpoint(
    matrix: W7MCapacityFunctionMatrixAdapter,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    authorization: W7WSourceAuthorization,
    plan_checkpoint,
    main_state: W7BEConstVState,
    refinement: int | None = None,
) -> W7BEConstVCheckpointMeasurement:
    before = main_state.state_digest
    aligned = _aligned_probe_state(matrix, runtime_adapter, main_state)
    observed: list[W7BEConstVRawSample] = []

    def observe(
        tick: int,
        activation: np.ndarray,
        afterimage: np.ndarray,
        scalar: np.ndarray,
    ) -> None:
        if activation.flags.writeable or afterimage.flags.writeable or scalar.flags.writeable:
            raise W7BEConstVABR1ConsumerError(
                "CONST-V observer received writable arrays"
            )
        s_values = _finite_vector(activation, "observed S")
        h_values = _finite_vector(afterimage, "observed H")
        scalar_values = _finite_vector(scalar, "observed technical scalar")
        payload = {
            "tick": tick,
            "s_values": s_values,
            "h_values": h_values,
            "technical_scalar_values": scalar_values,
        }
        observed.append(
            W7BEConstVRawSample(
                tick,
                s_values,
                h_values,
                scalar_values,
                _digest(payload),
            )
        )

    production = _produce(
        matrix,
        runtime_adapter,
        authorization,
        plan_checkpoint.probe,
        aligned,
        state_observer=observe,
        refinement=refinement,
    )
    if main_state.state_digest != before:
        raise W7BEConstVABR1ConsumerError(
            "CONST-V probe changed the main path state"
        )
    samples = tuple(observed)
    payload = {
        "plan_checkpoint_digest": plan_checkpoint.checkpoint_digest,
        "checkpoint": plan_checkpoint.checkpoint,
        "tick": plan_checkpoint.tick,
        "main_state_digest": main_state.state_digest,
        "aligned_probe_initial_state_digest": aligned.state_digest,
        "probe_production_digest": production.production_digest,
        "sample_digests": tuple(item.sample_digest for item in samples),
        "probe_returns_to_main": False,
    }
    return W7BEConstVCheckpointMeasurement(
        plan_checkpoint.checkpoint_digest,
        plan_checkpoint.checkpoint,
        plan_checkpoint.tick,
        main_state,
        aligned,
        production,
        samples,
        _digest(payload),
    )


@dataclass(frozen=True, slots=True)
class W7BEConstVABR1Result:
    """Complete AB/R1 main chain and five isolated raw measurements."""

    consumer_id: str
    matrix_digest: str
    plan_digest: str
    runtime_adapter_digest: str
    path_plan_digest: str
    path_id: str
    refinement: int
    initial_state: W7BEConstVState = field(repr=False)
    main_productions: tuple[W7BEConstVProduction, ...] = field(repr=False)
    measurements: tuple[W7BEConstVCheckpointMeasurement, ...] = field(repr=False)
    terminal_main_state: W7BEConstVState = field(repr=False)
    result_digest: str

    def __post_init__(self) -> None:
        productions = tuple(self.main_productions)
        measurements = tuple(self.measurements)
        previous = self.initial_state
        for production in productions:
            if production.initial_state is not previous:
                raise W7BEConstVABR1ConsumerError(
                    "CONST-V main path is not contiguous"
                )
            previous = production.end_state
        payload = {
            "consumer_id": self.consumer_id,
            "matrix_digest": self.matrix_digest,
            "plan_digest": self.plan_digest,
            "runtime_adapter_digest": self.runtime_adapter_digest,
            "path_plan_digest": self.path_plan_digest,
            "path_id": self.path_id,
            "refinement": self.refinement,
            "initial_state_digest": self.initial_state.state_digest,
            "main_production_digests": tuple(
                item.production_digest for item in productions
            ),
            "measurement_digests": tuple(
                item.checkpoint_measurement_digest for item in measurements
            ),
            "terminal_main_state_digest": self.terminal_main_state.state_digest,
        }
        if (
            self.consumer_id != _CONSUMER_ID
            or self.path_id != _PATH_ID
            or self.refinement != _REFINEMENT
            or len(productions) != 5
            or len(measurements) != 5
            or tuple(item.checkpoint for item in measurements) != tuple(range(5))
            or previous is not self.terminal_main_state
            or previous.tick != 8_000_000
            or self.result_digest != _digest(payload)
        ):
            raise W7BEConstVABR1ConsumerError(
                "CONST-V AB/R1 result binding is invalid"
            )
        object.__setattr__(self, "main_productions", productions)
        object.__setattr__(self, "measurements", measurements)


def _validate_consumer_bindings(
    matrix: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    runtime_adapter: W7BDConstVRuntimeAdapter,
) -> None:
    if (
        not isinstance(matrix, W7MCapacityFunctionMatrixAdapter)
        or not isinstance(family, W7WSymmetricSourceFamily)
        or not isinstance(authorization, W7WSourceAuthorization)
        or not isinstance(plan, W7YSevenPathSourcePlan)
        or not isinstance(runtime_adapter, W7BDConstVRuntimeAdapter)
        or matrix.matrix_digest != runtime_adapter.matrix_digest
        or plan.matrix_digest != matrix.matrix_digest
        or plan.seven_path_plan_digest
        != "c771a3c28c04e04a61fa24d187416ef65b17597f9af759682deb576a28c25b32"
        or family.symmetric_inventory_digest != plan.symmetric_inventory_digest
        or authorization.authorization_digest != plan.authorization_digest
    ):
        raise W7BEConstVABR1ConsumerError("W7-BE source bindings differ")


def _materialize_const_v_r1_path(
    matrix: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    runtime_adapter: W7BDConstVRuntimeAdapter,
    path_id: str,
    refinement: int = _REFINEMENT,
):
    _validate_consumer_bindings(
        matrix,
        family,
        authorization,
        plan,
        runtime_adapter,
    )
    if path_id not in _PATH_IDS:
        raise W7BEConstVABR1ConsumerError("unknown private CONST-V path")
    matches = tuple(item for item in plan.paths if item.path_id == path_id)
    if len(matches) != 1:
        raise W7BEConstVABR1ConsumerError(
            "private CONST-V R1 path binding is incomplete"
        )
    path = matches[0]
    initial_field = prepare_w7bd_const_v_initial_field(matrix, runtime_adapter)
    start_tick = 4_000_000 if path.prefix is None else 0
    initial = _build_state(
        matrix,
        runtime_adapter,
        path_id,
        start_tick,
        initial_field,
        refinement,
    )
    _assert_invariants(matrix, initial)
    current = initial
    productions = []
    if path.prefix is not None:
        prefix = _produce(
            matrix,
            runtime_adapter,
            authorization,
            path.prefix,
            current,
        )
        productions.append(prefix)
        current = prefix.end_state
    measurements = []
    for index, checkpoint in enumerate(path.checkpoints):
        measurements.append(
            _measure_checkpoint(
                matrix,
                runtime_adapter,
                authorization,
                checkpoint,
                current,
                refinement,
            )
        )
        if index < 4:
            production = _produce(
                matrix,
                runtime_adapter,
                authorization,
                path.continuations[index],
                current,
                refinement=refinement,
            )
            productions.append(production)
            current = production.end_state
    productions_out = tuple(productions)
    measurements_out = tuple(measurements)
    return path, initial, productions_out, measurements_out, current


def consume_w7be_const_v_ab_r1(
    matrix: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    runtime_adapter: W7BDConstVRuntimeAdapter,
) -> W7BEConstVABR1Result:
    """Execute only canonical AB/R1 in memory; no other path is accepted."""

    path, initial, productions_out, measurements_out, current = (
        _materialize_const_v_r1_path(
            matrix,
            family,
            authorization,
            plan,
            runtime_adapter,
            _PATH_ID,
        )
    )
    payload = {
        "consumer_id": _CONSUMER_ID,
        "matrix_digest": matrix.matrix_digest,
        "plan_digest": plan.seven_path_plan_digest,
        "runtime_adapter_digest": runtime_adapter.adapter_digest,
        "path_plan_digest": path.path_plan_digest,
        "path_id": _PATH_ID,
        "refinement": _REFINEMENT,
        "initial_state_digest": initial.state_digest,
        "main_production_digests": tuple(
            item.production_digest for item in productions_out
        ),
        "measurement_digests": tuple(
            item.checkpoint_measurement_digest for item in measurements_out
        ),
        "terminal_main_state_digest": current.state_digest,
    }
    return W7BEConstVABR1Result(
        _CONSUMER_ID,
        matrix.matrix_digest,
        plan.seven_path_plan_digest,
        runtime_adapter.adapter_digest,
        path.path_plan_digest,
        _PATH_ID,
        _REFINEMENT,
        initial,
        productions_out,
        measurements_out,
        current,
        _digest(payload),
    )
