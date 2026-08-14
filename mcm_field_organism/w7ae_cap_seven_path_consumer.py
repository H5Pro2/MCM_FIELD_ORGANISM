"""Isolated in-memory CAP consumer for the frozen W7-Y seven-path plan."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
import hashlib
import json
import math

from .capacity_limited_mcm_f3_runtime import (
    MCMCapacityLimitedContinuationBinding,
    MCMCapacityLimitedRuntimeDiagnostics,
    advance_capacity_limited_mcm_f3_shared_field_transient,
)
from .field_step_time import MCMFieldStepTime
from .mcm_f3_controlled_history_source import mcm_f3_receptor_sequences_digest
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff import handoff_receptor_completion_groups
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs
from .w7aa_p0_seven_path_consumer import W7AAP0SevenPathResult
from .w7ac_observer_seven_path_consumer import W7ACObserverSevenPathResult
from .w7m_capacity_function_matrix import W7MCapacityFunctionMatrixAdapter
from .w7w_symmetric_source_family import (
    W7WSourceAuthorization,
    W7WSymmetricSourceFamily,
    W7WSymmetricSourceFamilyError,
    authorize_w7w_source_segment,
)
from .w7y_seven_path_source_plan import (
    W7YCheckpointPlan,
    W7YPathPlan,
    W7YSevenPathSourcePlan,
    W7YSourceSegmentRef,
    build_w7y_seven_path_source_plan,
)


class W7AECAPSevenPathConsumerError(ValueError):
    """Raised when CAP consumption leaves the W7-AD contract."""


_CONSUMER_ID = "w7ae.cap-seven-path-consumer.v1"
_PATH_IDS = ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
_RESPONSE_TIME_SECONDS = 1.0
_AFTERIMAGE_TIME_SECONDS = 0.5
_MASS_ABS_TOLERANCE = 1e-12


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _binding_payload(
    binding: MCMCapacityLimitedContinuationBinding | None,
) -> tuple[str, str] | None:
    if binding is None:
        return None
    return binding.snapshot_digest, binding.configuration_digest


def _field_state_digest(current_field: SharedMCMField) -> str:
    if current_field.last_distribution is not None:
        return current_field.snapshot().digest()
    substrate = current_field.substrate
    if substrate is None:
        raise W7AECAPSevenPathConsumerError(
            "initial CAP field requires its substrate"
        )
    payload = {
        "role": "w7ae.initial-cap-field.v1",
        "layer_digest": current_field.layer.digest(),
        "docks": tuple(
            (
                dock.dock_id,
                dock.dock_map.modality_id,
                tuple(dock.dock_map.pairs),
            )
            for dock in current_field.docks
        ),
        "substrate_arm": (
            substrate.arm.arm_id,
            substrate.arm.eta,
            substrate.arm.kappa,
            substrate.arm.lambda_sm_per_second,
            substrate.arm.initial_total_mass,
        ),
        "substrate_mass": tuple(item.mass for item in substrate.masses),
        "edge_inventory_digest": substrate.edge_inventory_digest,
    }
    return _digest(payload)


def _state_payload(
    matrix_digest: str,
    path_id: str,
    tick: int,
    field_snapshot_digest: str,
    binding: MCMCapacityLimitedContinuationBinding | None,
    configuration_digest: str,
) -> dict[str, object]:
    return {
        "matrix_digest": matrix_digest,
        "path_id": path_id,
        "tick": tick,
        "field_snapshot_digest": field_snapshot_digest,
        "continuation_binding": _binding_payload(binding),
        "configuration_digest": configuration_digest,
    }


@dataclass(frozen=True, slots=True)
class W7AECAPState:
    """One coupled S/H/M field paired with its exact continuation binding."""

    matrix_digest: str
    path_id: str
    tick: int
    field: SharedMCMField = field(repr=False)
    continuation_binding: MCMCapacityLimitedContinuationBinding | None
    configuration_digest: str
    state_digest: str

    def __post_init__(self) -> None:
        if (
            not self.matrix_digest
            or self.path_id not in _PATH_IDS
            or isinstance(self.tick, bool)
            or not isinstance(self.tick, int)
            or self.tick < 0
            or not isinstance(self.field, SharedMCMField)
            or self.field.substrate is None
            or not self.configuration_digest
        ):
            raise W7AECAPSevenPathConsumerError("CAP state binding is invalid")
        snapshot_digest = _field_state_digest(self.field)
        initial = self.field.last_distribution is None
        if initial:
            if self.continuation_binding is not None:
                raise W7AECAPSevenPathConsumerError(
                    "initial CAP state cannot carry a continuation binding"
                )
        elif (
            not isinstance(
                self.continuation_binding,
                MCMCapacityLimitedContinuationBinding,
            )
            or self.continuation_binding.snapshot_digest != snapshot_digest
            or self.continuation_binding.configuration_digest
            != self.configuration_digest
        ):
            raise W7AECAPSevenPathConsumerError(
                "completed CAP state requires its exact continuation binding"
            )
        expected = _digest(
            _state_payload(
                self.matrix_digest,
                self.path_id,
                self.tick,
                snapshot_digest,
                self.continuation_binding,
                self.configuration_digest,
            )
        )
        if self.state_digest != expected:
            raise W7AECAPSevenPathConsumerError(
                "CAP state digest does not match its content"
            )


def _build_state(
    adapter: W7MCapacityFunctionMatrixAdapter,
    path_id: str,
    tick: int,
    current_field: SharedMCMField,
    binding: MCMCapacityLimitedContinuationBinding | None,
) -> W7AECAPState:
    configuration_digest = adapter.runtime_contract.configuration_digest
    payload = _state_payload(
        adapter.matrix_digest,
        path_id,
        tick,
        _field_state_digest(current_field),
        binding,
        configuration_digest,
    )
    return W7AECAPState(
        adapter.matrix_digest,
        path_id,
        tick,
        current_field,
        binding,
        configuration_digest,
        _digest(payload),
    )


def _initial_state(
    adapter: W7MCapacityFunctionMatrixAdapter,
    path_id: str,
    tick: int,
) -> W7AECAPState:
    initial = copy.deepcopy(adapter.initial_field)
    if initial.last_distribution is not None or initial.substrate is None:
        raise W7AECAPSevenPathConsumerError(
            "CAP path requires one fresh substrate field"
        )
    return _build_state(adapter, path_id, tick, initial, None)


def _clone_state(
    adapter: W7MCapacityFunctionMatrixAdapter,
    state: W7AECAPState,
) -> W7AECAPState:
    cloned_field = copy.deepcopy(state.field)
    binding = None
    if state.continuation_binding is not None:
        binding = MCMCapacityLimitedContinuationBinding(
            _field_state_digest(cloned_field),
            state.configuration_digest,
        )
    clone = _build_state(adapter, state.path_id, state.tick, cloned_field, binding)
    if (
        clone.state_digest != state.state_digest
        or clone is state
        or clone.field is state.field
        or clone.field.layer is state.field.layer
        or clone.field.docks is state.field.docks
        or clone.field.substrate is state.field.substrate
        or (
            state.continuation_binding is not None
            and clone.continuation_binding is state.continuation_binding
        )
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP checkpoint copy is not structurally independent"
        )
    return clone


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


def _validate_segment_source(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    segment: W7YSourceSegmentRef,
) -> tuple[ReceptorTimeSequence, ReceptorTimeSequence]:
    sequences = tuple(sorted(segment.sequences, key=lambda item: item.modality_id))
    if (
        len(sequences) != 2
        or any(not isinstance(item, ReceptorTimeSequence) for item in sequences)
        or len({item.modality_id for item in sequences}) != 2
        or mcm_f3_receptor_sequences_digest(sequences) != segment.source_digest
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP segment sequences differ from their source binding"
        )
    if segment.source_digest not in _known_source_digests(adapter):
        try:
            authorize_w7w_source_segment(
                adapter,
                authorization,
                segment.source_digest,
                segment.path_id,
                segment.interval,
            )
        except W7WSymmetricSourceFamilyError as exc:
            raise W7AECAPSevenPathConsumerError(str(exc)) from exc
    elif segment.authorization_role_id is not None:
        raise W7AECAPSevenPathConsumerError(
            "existing CAP source cannot carry additive authorization"
        )
    return sequences


def _production_payload(
    matrix_digest: str,
    segment_digest: str,
    source_digest: str,
    path_id: str,
    interval: tuple[int, int],
    assigned_event_count: int,
    initial_state_digest: str,
    end_state_digest: str,
    diagnostics: MCMCapacityLimitedRuntimeDiagnostics,
) -> dict[str, object]:
    return {
        "matrix_digest": matrix_digest,
        "segment_digest": segment_digest,
        "source_digest": source_digest,
        "path_id": path_id,
        "interval": interval,
        "assigned_event_count": assigned_event_count,
        "initial_state_digest": initial_state_digest,
        "end_state_digest": end_state_digest,
        "diagnostics": {
            "method_id": diagnostics.method_id,
            "validation_count": diagnostics.validation_count,
            "maximum_mass": diagnostics.maximum_mass,
            "minimum_free_capacity": diagnostics.minimum_free_capacity,
            "maximum_capacity_excess": diagnostics.maximum_capacity_excess,
            "configuration_digest": diagnostics.configuration_digest,
        },
    }


@dataclass(frozen=True, slots=True)
class W7AECAPProductionResult:
    """One CAP advance over exactly one W7-Y source segment."""

    matrix_digest: str
    segment_digest: str
    source_digest: str
    path_id: str
    interval: tuple[int, int]
    assigned_event_count: int
    initial_state: W7AECAPState = field(repr=False)
    end_state: W7AECAPState = field(repr=False)
    diagnostics: MCMCapacityLimitedRuntimeDiagnostics
    production_digest: str

    def __post_init__(self) -> None:
        if (
            not self.matrix_digest
            or not self.segment_digest
            or not self.source_digest
            or self.path_id not in _PATH_IDS
            or self.interval != (self.initial_state.tick, self.end_state.tick)
            or self.initial_state.path_id != self.path_id
            or self.end_state.path_id != self.path_id
            or self.initial_state.matrix_digest != self.matrix_digest
            or self.end_state.matrix_digest != self.matrix_digest
            or isinstance(self.assigned_event_count, bool)
            or self.assigned_event_count <= 0
            or not isinstance(
                self.diagnostics,
                MCMCapacityLimitedRuntimeDiagnostics,
            )
            or self.diagnostics.method_id
            != "w7k.capacity-limited-shared-mcm-field.v1"
            or self.diagnostics.maximum_capacity_excess != 0.0
        ):
            raise W7AECAPSevenPathConsumerError(
                "CAP production binding is invalid"
            )
        expected = _digest(
            _production_payload(
                self.matrix_digest,
                self.segment_digest,
                self.source_digest,
                self.path_id,
                self.interval,
                self.assigned_event_count,
                self.initial_state.state_digest,
                self.end_state.state_digest,
                self.diagnostics,
            )
        )
        if self.production_digest != expected:
            raise W7AECAPSevenPathConsumerError(
                "CAP production digest does not match its content"
            )


def _assert_invariants(
    adapter: W7MCapacityFunctionMatrixAdapter,
    state: W7AECAPState,
) -> None:
    substrate = state.field.substrate
    if substrate is None:
        raise W7AECAPSevenPathConsumerError("CAP state lost its substrate")
    masses = tuple(item.mass for item in substrate.masses)
    if (
        substrate.arm.arm_id != "w7m.cap"
        or substrate.arm.eta != 1.0
        or substrate.arm.kappa != 0.5
        or substrate.arm.lambda_sm_per_second != 1.0
        or abs(math.fsum(masses) - 1.0) > _MASS_ABS_TOLERANCE
        or min(masses) < -_MASS_ABS_TOLERANCE
        or max(masses) > adapter.runtime_contract.site_capacity
        + _MASS_ABS_TOLERANCE
        or substrate.edge_inventory_digest
        != adapter.initial_field.substrate.edge_inventory_digest
        or tuple(item.neuron_id for item in state.field.layer.neurons)
        != tuple(item.neuron_id for item in adapter.initial_field.layer.neurons)
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP field violated model, mass, capacity, or geometry invariants"
        )


def _produce(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    segment: W7YSourceSegmentRef,
    state: W7AECAPState,
    *,
    _refinement: int = 1,
    _state_observer=None,
    _integration_observer=None,
) -> W7AECAPProductionResult:
    if _refinement not in {1, 2, 4} or isinstance(_refinement, bool):
        raise W7AECAPSevenPathConsumerError(
            "CAP refinement must be one of 1, 2, or 4"
        )
    if _integration_observer is not None and not callable(
        _integration_observer
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP integration observer must be callable"
        )
    if segment.path_id != state.path_id or segment.interval[0] != state.tick:
        raise W7AECAPSevenPathConsumerError(
            "CAP segment does not continue its path state"
        )
    sequences = _validate_segment_source(adapter, authorization, segment)
    start_tick, end_tick = segment.interval
    step = MCMFieldStepTime(
        adapter.source.clock_id,
        start_tick,
        end_tick,
        adapter.source.ticks_per_second,
    )
    handoff = handoff_receptor_completion_groups(sequences, (step,))
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != handoff.source_event_count
        or len(handoff.batches) != 1
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP receptor completion handoff is incomplete"
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
        CommonFieldTime(adapter.source.clock_id, start_tick, end_tick),
        (),
    )
    before = state.state_digest
    runtime = advance_capacity_limited_mcm_f3_shared_field_transient(
        state.field,
        distribution,
        transient_inputs,
        NeutralLocalFieldSubstrateConfig(_RESPONSE_TIME_SECONDS),
        NeutralFastAfterimageConfig(_AFTERIMAGE_TIME_SECONDS),
        adapter.runtime_contract,
        refinement=_refinement,
        continuation_binding=state.continuation_binding,
        _state_observer=_state_observer,
    )
    if state.state_digest != before:
        raise W7AECAPSevenPathConsumerError(
            "CAP production mutated its input state"
        )
    end_state = _build_state(
        adapter,
        state.path_id,
        end_tick,
        runtime.field,
        runtime.continuation_binding,
    )
    _assert_invariants(adapter, end_state)
    payload = _production_payload(
        adapter.matrix_digest,
        segment.segment_digest,
        segment.source_digest,
        state.path_id,
        segment.interval,
        handoff.assigned_event_count,
        state.state_digest,
        end_state.state_digest,
        runtime.capacity_diagnostics,
    )
    result = W7AECAPProductionResult(
        adapter.matrix_digest,
        segment.segment_digest,
        segment.source_digest,
        state.path_id,
        segment.interval,
        handoff.assigned_event_count,
        state,
        end_state,
        runtime.capacity_diagnostics,
        _digest(payload),
    )
    if _integration_observer is not None and _integration_observer(
        segment,
        result,
        runtime.advance.diagnostics,
    ) is not None:
        raise W7AECAPSevenPathConsumerError(
            "CAP integration observer must not return state"
        )
    return result


def _checkpoint_payload(
    plan_checkpoint_digest: str,
    path_id: str,
    checkpoint: int,
    tick: int,
    main_predecessor_digest: str,
    main_state_digest: str,
    probe_initial_state_digest: str,
    probe_segment_digest: str,
    probe_production_digest: str,
) -> dict[str, object]:
    return {
        "plan_checkpoint_digest": plan_checkpoint_digest,
        "path_id": path_id,
        "checkpoint": checkpoint,
        "tick": tick,
        "main_predecessor_digest": main_predecessor_digest,
        "main_state_digest": main_state_digest,
        "probe_initial_state_digest": probe_initial_state_digest,
        "probe_segment_digest": probe_segment_digest,
        "probe_production_digest": probe_production_digest,
        "probe_returns_to_main": False,
    }


@dataclass(frozen=True, slots=True)
class W7AECAPCheckpointResult:
    """One CAP checkpoint and its completed isolated probe."""

    plan_checkpoint_digest: str
    path_id: str
    checkpoint: int
    tick: int
    main_predecessor_digest: str
    main_state: W7AECAPState = field(repr=False)
    probe_initial_state: W7AECAPState = field(repr=False)
    probe_segment_digest: str
    probe_production: W7AECAPProductionResult = field(repr=False)
    checkpoint_result_digest: str

    def __post_init__(self) -> None:
        if (
            not self.plan_checkpoint_digest
            or self.path_id not in _PATH_IDS
            or self.checkpoint not in range(5)
            or self.tick != (self.checkpoint + 4) * 1_000_000
            or self.main_state.state_digest
            != self.probe_initial_state.state_digest
            or self.main_state is self.probe_initial_state
            or self.main_state.field is self.probe_initial_state.field
            or self.probe_production.initial_state is not self.probe_initial_state
            or self.probe_production.end_state is self.main_state
        ):
            raise W7AECAPSevenPathConsumerError(
                "CAP checkpoint isolation is invalid"
            )
        payload = _checkpoint_payload(
            self.plan_checkpoint_digest,
            self.path_id,
            self.checkpoint,
            self.tick,
            self.main_predecessor_digest,
            self.main_state.state_digest,
            self.probe_initial_state.state_digest,
            self.probe_segment_digest,
            self.probe_production.production_digest,
        )
        if self.checkpoint_result_digest != _digest(payload):
            raise W7AECAPSevenPathConsumerError(
                "CAP checkpoint digest does not match its content"
            )


def _checkpoint_result(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    checkpoint_plan: W7YCheckpointPlan,
    main_state: W7AECAPState,
    main_predecessor_digest: str,
    *,
    _refinement: int = 1,
    _integration_observer=None,
) -> W7AECAPCheckpointResult:
    before = main_state.state_digest
    probe_initial = _clone_state(adapter, main_state)
    probe = _produce(
        adapter,
        authorization,
        checkpoint_plan.probe,
        probe_initial,
        _refinement=_refinement,
        _integration_observer=_integration_observer,
    )
    if main_state.state_digest != before:
        raise W7AECAPSevenPathConsumerError(
            "CAP probe changed the main checkpoint state"
        )
    payload = _checkpoint_payload(
        checkpoint_plan.checkpoint_digest,
        checkpoint_plan.path_id,
        checkpoint_plan.checkpoint,
        checkpoint_plan.tick,
        main_predecessor_digest,
        main_state.state_digest,
        probe_initial.state_digest,
        checkpoint_plan.probe.segment_digest,
        probe.production_digest,
    )
    return W7AECAPCheckpointResult(
        checkpoint_plan.checkpoint_digest,
        checkpoint_plan.path_id,
        checkpoint_plan.checkpoint,
        checkpoint_plan.tick,
        main_predecessor_digest,
        main_state,
        probe_initial,
        checkpoint_plan.probe.segment_digest,
        probe,
        _digest(payload),
    )


def _path_payload(
    path_plan_digest: str,
    path_id: str,
    initial_state_digest: str,
    main_productions: tuple[W7AECAPProductionResult, ...],
    checkpoints: tuple[W7AECAPCheckpointResult, ...],
    terminal_state_digest: str,
) -> dict[str, object]:
    return {
        "path_plan_digest": path_plan_digest,
        "path_id": path_id,
        "initial_state_digest": initial_state_digest,
        "main_production_digests": tuple(
            item.production_digest for item in main_productions
        ),
        "checkpoint_result_digests": tuple(
            item.checkpoint_result_digest for item in checkpoints
        ),
        "probe_production_digests": tuple(
            item.probe_production.production_digest for item in checkpoints
        ),
        "terminal_state_digest": terminal_state_digest,
    }


@dataclass(frozen=True, slots=True)
class W7AECAPPathResult:
    """One complete CAP main chain and its five isolated probes."""

    path_plan_digest: str
    path_id: str
    initial_state: W7AECAPState = field(repr=False)
    main_productions: tuple[W7AECAPProductionResult, ...] = field(repr=False)
    checkpoints: tuple[W7AECAPCheckpointResult, ...] = field(repr=False)
    terminal_main_state: W7AECAPState = field(repr=False)
    cap_path_consumption_digest: str

    def __post_init__(self) -> None:
        productions = tuple(self.main_productions)
        checkpoints = tuple(self.checkpoints)
        expected_count = 4 if self.path_id.startswith("u") else 5
        if (
            self.path_id not in _PATH_IDS
            or len(productions) != expected_count
            or len(checkpoints) != 5
            or productions[0].initial_state is not self.initial_state
        ):
            raise W7AECAPSevenPathConsumerError(
                "CAP path result binding is invalid"
            )
        previous = self.initial_state
        for production in productions:
            if production.initial_state is not previous:
                raise W7AECAPSevenPathConsumerError(
                    "CAP main production chain is not contiguous"
                )
            previous = production.end_state
        if previous is not self.terminal_main_state or previous.tick != 8_000_000:
            raise W7AECAPSevenPathConsumerError(
                "CAP terminal state is not the path endpoint"
            )
        offset = 0 if self.path_id.startswith("u") else 1
        expected_states = (self.initial_state if offset == 0 else productions[0].end_state,) + tuple(
            productions[index + offset].end_state for index in range(4)
        )
        if tuple(item.main_state for item in checkpoints) != expected_states:
            raise W7AECAPSevenPathConsumerError(
                "CAP checkpoints do not bind the main path states"
            )
        payload = _path_payload(
            self.path_plan_digest,
            self.path_id,
            self.initial_state.state_digest,
            productions,
            checkpoints,
            self.terminal_main_state.state_digest,
        )
        if self.cap_path_consumption_digest != _digest(payload):
            raise W7AECAPSevenPathConsumerError(
                "CAP path consumption digest does not match its content"
            )
        object.__setattr__(self, "main_productions", productions)
        object.__setattr__(self, "checkpoints", checkpoints)


def _consume_path(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    path_plan: W7YPathPlan,
    *,
    _refinement: int = 1,
    _integration_observer=None,
) -> W7AECAPPathResult:
    start_tick = 4_000_000 if path_plan.prefix is None else 0
    initial = _initial_state(adapter, path_plan.path_id, start_tick)
    _assert_invariants(adapter, initial)
    current = initial
    productions = []
    if path_plan.prefix is not None:
        prefix = _produce(
            adapter,
            authorization,
            path_plan.prefix,
            current,
            _refinement=_refinement,
            _integration_observer=_integration_observer,
        )
        productions.append(prefix)
        current = prefix.end_state
        predecessor_digest = prefix.production_digest
    else:
        predecessor_digest = path_plan.uniform_start.start_digest
    checkpoints = []
    for index, checkpoint_plan in enumerate(path_plan.checkpoints):
        checkpoints.append(
            _checkpoint_result(
                adapter,
                authorization,
                checkpoint_plan,
                current,
                predecessor_digest,
                _refinement=_refinement,
                _integration_observer=_integration_observer,
            )
        )
        if index < 4:
            production = _produce(
                adapter,
                authorization,
                path_plan.continuations[index],
                current,
                _refinement=_refinement,
                _integration_observer=_integration_observer,
            )
            productions.append(production)
            current = production.end_state
            predecessor_digest = production.production_digest
    productions_out = tuple(productions)
    checkpoints_out = tuple(checkpoints)
    payload = _path_payload(
        path_plan.path_plan_digest,
        path_plan.path_id,
        initial.state_digest,
        productions_out,
        checkpoints_out,
        current.state_digest,
    )
    return W7AECAPPathResult(
        path_plan.path_plan_digest,
        path_plan.path_id,
        initial,
        productions_out,
        checkpoints_out,
        current,
        _digest(payload),
    )


def _countercontrol_payload(
    path_digests: tuple[str, ...],
    main_digest: str,
    probe_digest: str,
) -> dict[str, object]:
    return {
        "path_digests": path_digests,
        "reverse_path_digests": path_digests,
        "ab_checkpoint": 0,
        "main_production_digest": main_digest,
        "probe_production_digest": probe_digest,
    }


@dataclass(frozen=True, slots=True)
class W7AECAPCountercontrols:
    """Digest evidence for path-order and branch-order independence."""

    path_digests: tuple[str, ...]
    main_production_digest: str
    probe_production_digest: str
    countercontrol_digest: str

    def __post_init__(self) -> None:
        paths = tuple(self.path_digests)
        if len(paths) != 7 or any(not item for item in paths):
            raise W7AECAPSevenPathConsumerError(
                "CAP countercontrol path binding is invalid"
            )
        payload = _countercontrol_payload(
            paths,
            self.main_production_digest,
            self.probe_production_digest,
        )
        if self.countercontrol_digest != _digest(payload):
            raise W7AECAPSevenPathConsumerError(
                "CAP countercontrol digest does not match its content"
            )
        object.__setattr__(self, "path_digests", paths)


@dataclass(frozen=True, slots=True)
class _W7AECAPPathOrderAudit:
    path_digests: tuple[str, ...]
    refinement: int

    def __post_init__(self) -> None:
        paths = tuple(self.path_digests)
        if (
            len(paths) != 7
            or any(not item for item in paths)
            or self.refinement not in {1, 2, 4}
            or isinstance(self.refinement, bool)
        ):
            raise W7AECAPSevenPathConsumerError(
                "CAP path-order audit binding is invalid"
            )
        object.__setattr__(self, "path_digests", paths)


@dataclass(frozen=True, slots=True)
class _W7AECAPBranchOrderAudit:
    main_production_digest: str
    probe_production_digest: str
    refinement: int

    def __post_init__(self) -> None:
        if (
            not self.main_production_digest
            or not self.probe_production_digest
            or self.refinement not in {1, 2, 4}
            or isinstance(self.refinement, bool)
        ):
            raise W7AECAPSevenPathConsumerError(
                "CAP branch-order audit binding is invalid"
            )


def _audit_w7ae_path_order(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    paths: tuple[W7AECAPPathResult, ...],
    *,
    _refinement: int = 1,
) -> _W7AECAPPathOrderAudit:
    reverse = tuple(
        _consume_path(
            adapter,
            authorization,
            path_plan,
            _refinement=_refinement,
        )
        for path_plan in reversed(plan.paths)
    )
    canonical = {item.path_id: item for item in paths}
    if any(
        canonical[item.path_id].cap_path_consumption_digest
        != item.cap_path_consumption_digest
        for item in reverse
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP path execution order changed a path result"
        )
    return _W7AECAPPathOrderAudit(
        tuple(item.cap_path_consumption_digest for item in paths),
        _refinement,
    )


def _audit_w7ae_branch_order(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    paths: tuple[W7AECAPPathResult, ...],
    *,
    _refinement: int = 1,
) -> _W7AECAPBranchOrderAudit:
    ab = paths[0]
    checkpoint = ab.checkpoints[0]
    main_segment = plan.paths[0].continuations[0]
    probe_segment = plan.paths[0].checkpoints[0].probe
    probe_first = _produce(
        adapter,
        authorization,
        probe_segment,
        _clone_state(adapter, checkpoint.main_state),
        _refinement=_refinement,
    )
    main_after_probe = _produce(
        adapter,
        authorization,
        main_segment,
        _clone_state(adapter, checkpoint.main_state),
        _refinement=_refinement,
    )
    main_first = _produce(
        adapter,
        authorization,
        main_segment,
        _clone_state(adapter, checkpoint.main_state),
        _refinement=_refinement,
    )
    probe_after_main = _produce(
        adapter,
        authorization,
        probe_segment,
        _clone_state(adapter, checkpoint.main_state),
        _refinement=_refinement,
    )
    if (
        main_first.production_digest != main_after_probe.production_digest
        or probe_first.production_digest != probe_after_main.production_digest
        or main_first.production_digest != ab.main_productions[1].production_digest
        or probe_first.production_digest
        != checkpoint.probe_production.production_digest
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP main/probe execution order changed a branch result"
        )
    return _W7AECAPBranchOrderAudit(
        main_first.production_digest,
        probe_first.production_digest,
        _refinement,
    )


def _finalize_w7ae_countercontrols(
    paths: tuple[W7AECAPPathResult, ...],
    path_audit: _W7AECAPPathOrderAudit,
    branch_audit: _W7AECAPBranchOrderAudit,
) -> W7AECAPCountercontrols:
    path_digests = tuple(item.cap_path_consumption_digest for item in paths)
    if (
        not isinstance(path_audit, _W7AECAPPathOrderAudit)
        or not isinstance(branch_audit, _W7AECAPBranchOrderAudit)
        or path_audit.path_digests != path_digests
        or path_audit.refinement != branch_audit.refinement
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP split countercontrol audits differ"
        )
    payload = _countercontrol_payload(
        path_digests,
        branch_audit.main_production_digest,
        branch_audit.probe_production_digest,
    )
    return W7AECAPCountercontrols(
        path_digests,
        branch_audit.main_production_digest,
        branch_audit.probe_production_digest,
        _digest(payload),
    )


def _countercontrols(
    adapter: W7MCapacityFunctionMatrixAdapter,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    paths: tuple[W7AECAPPathResult, ...],
    *,
    _refinement: int = 1,
) -> W7AECAPCountercontrols:
    path_audit = _audit_w7ae_path_order(
        adapter,
        authorization,
        plan,
        paths,
        _refinement=_refinement,
    )
    branch_audit = _audit_w7ae_branch_order(
        adapter,
        authorization,
        plan,
        paths,
        _refinement=_refinement,
    )
    return _finalize_w7ae_countercontrols(paths, path_audit, branch_audit)


def _result_payload(
    plan_digest: str,
    p0_digest: str,
    observer_digest: str,
    paths: tuple[W7AECAPPathResult, ...],
    countercontrol_digest: str,
) -> dict[str, object]:
    return {
        "consumer_id": _CONSUMER_ID,
        "plan_digest": plan_digest,
        "p0_consumption_digest": p0_digest,
        "observer_consumption_digest": observer_digest,
        "path_consumption_digests": tuple(
            item.cap_path_consumption_digest for item in paths
        ),
        "countercontrol_digest": countercontrol_digest,
    }


@dataclass(frozen=True, slots=True)
class W7AECAPSevenPathResult:
    """Complete CAP result without comparisons or interpretation."""

    consumer_id: str
    plan_digest: str
    p0_consumption_digest: str
    observer_consumption_digest: str
    path_results: tuple[W7AECAPPathResult, ...] = field(repr=False)
    countercontrols: W7AECAPCountercontrols
    cap_seven_path_consumption_digest: str

    def __post_init__(self) -> None:
        paths = tuple(self.path_results)
        if (
            self.consumer_id != _CONSUMER_ID
            or tuple(item.path_id for item in paths) != _PATH_IDS
            or not self.plan_digest
            or not self.p0_consumption_digest
            or not self.observer_consumption_digest
            or not isinstance(self.countercontrols, W7AECAPCountercontrols)
        ):
            raise W7AECAPSevenPathConsumerError(
                "CAP seven-path result binding is invalid"
            )
        payload = _result_payload(
            self.plan_digest,
            self.p0_consumption_digest,
            self.observer_consumption_digest,
            paths,
            self.countercontrols.countercontrol_digest,
        )
        if self.cap_seven_path_consumption_digest != _digest(payload):
            raise W7AECAPSevenPathConsumerError(
                "CAP seven-path consumption digest does not match its content"
            )
        object.__setattr__(self, "path_results", paths)


@dataclass(frozen=True, slots=True)
class _W7AECAPPathMaterialization:
    """Private canonical path phase before countercontrol execution."""

    plan_digest: str
    p0_digest: str
    observer_digest: str
    initial_field_digest: str
    refinement: int
    path_results: tuple[W7AECAPPathResult, ...] = field(repr=False)

    def __post_init__(self) -> None:
        paths = tuple(self.path_results)
        if (
            not self.plan_digest
            or not self.p0_digest
            or not self.observer_digest
            or not self.initial_field_digest
            or self.refinement not in {1, 2, 4}
            or isinstance(self.refinement, bool)
            or tuple(item.path_id for item in paths) != _PATH_IDS
        ):
            raise W7AECAPSevenPathConsumerError(
                "CAP path materialization binding is invalid"
            )
        object.__setattr__(self, "path_results", paths)


def _validate_w7ae_inputs(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    p0_result: W7AAP0SevenPathResult,
    observer_result: W7ACObserverSevenPathResult,
    *,
    _refinement: int = 1,
    _integration_observer=None,
) -> None:
    if (
        not isinstance(adapter, W7MCapacityFunctionMatrixAdapter)
        or not isinstance(family, W7WSymmetricSourceFamily)
        or not isinstance(authorization, W7WSourceAuthorization)
        or not isinstance(plan, W7YSevenPathSourcePlan)
        or not isinstance(p0_result, W7AAP0SevenPathResult)
        or not isinstance(observer_result, W7ACObserverSevenPathResult)
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP consumption requires complete W7-M/W/Y/AA/AC bindings"
        )
    if _refinement not in {1, 2, 4} or isinstance(_refinement, bool):
        raise W7AECAPSevenPathConsumerError(
            "CAP refinement must be one of 1, 2, or 4"
        )
    if _integration_observer is not None and not callable(
        _integration_observer
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP integration observer must be callable"
        )
    expected_plan = build_w7y_seven_path_source_plan(
        adapter,
        family,
        authorization,
    )
    if (
        plan.seven_path_plan_digest != expected_plan.seven_path_plan_digest
        or plan.paths != expected_plan.paths
        or p0_result.plan_digest != plan.seven_path_plan_digest
        or observer_result.p0_consumption_digest
        != p0_result.p0_seven_path_consumption_digest
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP consumption input digests differ"
        )


def _materialize_w7ae_cap_paths(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    p0_result: W7AAP0SevenPathResult,
    observer_result: W7ACObserverSevenPathResult,
    *,
    _refinement: int = 1,
    _integration_observer=None,
) -> _W7AECAPPathMaterialization:
    """Materialize only the 67 canonical CAP productions."""

    _validate_w7ae_inputs(
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        _refinement=_refinement,
        _integration_observer=_integration_observer,
    )
    p0_digest = p0_result.p0_seven_path_consumption_digest
    observer_digest = observer_result.observer_seven_path_consumption_digest
    initial_digest = _field_state_digest(adapter.initial_field)
    paths = tuple(
        _consume_path(
            adapter,
            authorization,
            path_plan,
            _refinement=_refinement,
            _integration_observer=_integration_observer,
        )
        for path_plan in plan.paths
    )
    if (
        p0_result.p0_seven_path_consumption_digest != p0_digest
        or observer_result.observer_seven_path_consumption_digest
        != observer_digest
        or _field_state_digest(adapter.initial_field) != initial_digest
        or adapter.initial_field.last_distribution is not None
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP path materialization mutated an input"
        )
    return _W7AECAPPathMaterialization(
        plan.seven_path_plan_digest,
        p0_digest,
        observer_digest,
        initial_digest,
        _refinement,
        paths,
    )


def _audit_w7ae_cap_materialization(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    p0_result: W7AAP0SevenPathResult,
    observer_result: W7ACObserverSevenPathResult,
    materialization: _W7AECAPPathMaterialization,
) -> W7AECAPSevenPathResult:
    """Run CAP countercontrols and finalize one materialization."""

    if not isinstance(materialization, _W7AECAPPathMaterialization):
        raise W7AECAPSevenPathConsumerError(
            "CAP audit requires a path materialization"
        )
    _validate_w7ae_inputs(
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        _refinement=materialization.refinement,
    )
    paths = materialization.path_results
    countercontrols = _countercontrols(
        adapter,
        authorization,
        plan,
        paths,
        _refinement=materialization.refinement,
    )
    return _finalize_w7ae_cap_materialization(
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        materialization,
        countercontrols,
    )


def _finalize_w7ae_cap_materialization(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    p0_result: W7AAP0SevenPathResult,
    observer_result: W7ACObserverSevenPathResult,
    materialization: _W7AECAPPathMaterialization,
    countercontrols: W7AECAPCountercontrols,
) -> W7AECAPSevenPathResult:
    """Finalize already executed CAP phases without another integration."""

    if (
        not isinstance(materialization, _W7AECAPPathMaterialization)
        or not isinstance(countercontrols, W7AECAPCountercontrols)
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP finalization requires materialization and countercontrols"
        )
    _validate_w7ae_inputs(
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        _refinement=materialization.refinement,
    )
    paths = materialization.path_results
    if (
        materialization.plan_digest != plan.seven_path_plan_digest
        or p0_result.p0_seven_path_consumption_digest
        != materialization.p0_digest
        or observer_result.observer_seven_path_consumption_digest
        != materialization.observer_digest
        or _field_state_digest(adapter.initial_field)
        != materialization.initial_field_digest
        or adapter.initial_field.last_distribution is not None
    ):
        raise W7AECAPSevenPathConsumerError(
            "CAP consumption mutated an input or counterbaseline"
        )
    payload = _result_payload(
        plan.seven_path_plan_digest,
        materialization.p0_digest,
        materialization.observer_digest,
        paths,
        countercontrols.countercontrol_digest,
    )
    return W7AECAPSevenPathResult(
        _CONSUMER_ID,
        plan.seven_path_plan_digest,
        materialization.p0_digest,
        materialization.observer_digest,
        paths,
        countercontrols,
        _digest(payload),
    )


def consume_w7ae_cap_seven_path_plan(
    adapter: W7MCapacityFunctionMatrixAdapter,
    family: W7WSymmetricSourceFamily,
    authorization: W7WSourceAuthorization,
    plan: W7YSevenPathSourcePlan,
    p0_result: W7AAP0SevenPathResult,
    observer_result: W7ACObserverSevenPathResult,
    *,
    _refinement: int = 1,
    _integration_observer=None,
) -> W7AECAPSevenPathResult:
    """Consume W7-Y only through isolated capacity-limited CAP fields."""

    materialization = _materialize_w7ae_cap_paths(
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        _refinement=_refinement,
        _integration_observer=_integration_observer,
    )
    return _audit_w7ae_cap_materialization(
        adapter,
        family,
        authorization,
        plan,
        p0_result,
        observer_result,
        materialization,
    )
