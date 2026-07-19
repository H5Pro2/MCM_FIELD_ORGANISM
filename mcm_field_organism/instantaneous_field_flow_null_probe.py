"""Passive redundancy audit for instantaneous local field flow."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

import numpy as np

from .field_step_time import MCMFieldStepTime
from .mcm_neuron import MCMNeuron
from .mcm_neuron_layer import receptor_projection_baseline
from .neutral_local_field_substrate import (
    NeutralLocalFieldSubstrateConfig,
    _diffusion_generator,
    advance_neutral_shared_field,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)


class InstantaneousFieldFlowNullProbeError(ValueError):
    """Raised when the passive flow identity cannot be audited."""


@dataclass(frozen=True, slots=True)
class InstantaneousEdgeFlow:
    target_neuron_id: str
    source_neuron_id: str
    relative_position: tuple[int, ...]
    signed_flow: float


@dataclass(frozen=True, slots=True)
class InstantaneousNodeFlow:
    neuron_id: str
    activation: float
    local_divergence: float
    generator_diffusion: float
    perception_reconstruction: float


@dataclass(frozen=True, slots=True)
class InstantaneousFieldFlowObservation:
    source_layer_digest: str
    response_time_seconds: float
    edges: tuple[InstantaneousEdgeFlow, ...]
    nodes: tuple[InstantaneousNodeFlow, ...]


@dataclass(frozen=True, slots=True)
class InstantaneousFieldFlowNullProbeResult:
    observation: InstantaneousFieldFlowObservation
    edge_antisymmetry_error: float
    total_divergence_error: float
    generator_identity_error: float
    perception_identity_error: float
    order_invariant: bool
    fast_matched_full_states_distinct: bool
    fast_matched_flow_equal: bool
    observer_preserved_source_digest: bool
    observer_writeback_performed: bool
    accumulation_performed: bool
    new_runtime_state_added: bool
    runtime_candidate_released: bool


_CLOCK_ID = "organism.instantaneous_flow_null"
_GEOMETRY_ID = "auditory.flow_line.v1"
_SAMPLE_OFFSETS = ((-1,), (1,))
_VALUES = (0.9, -0.2, 0.5, -0.7)
_TOLERANCE = 1e-12


def _mapped_position(
    field: SharedMCMField,
    target: MCMNeuron,
    offset: tuple[int, ...],
) -> tuple[int, ...]:
    values = [
        coordinate + delta
        for coordinate, delta in zip(target.position, offset, strict=True)
    ]
    for axis in field.layer.periodic_axes:
        values[axis.axis_index] = axis.origin + (
            (values[axis.axis_index] - axis.origin) % axis.size
        )
    return tuple(values)


def _observe_in_order(
    field: SharedMCMField,
    config: NeutralLocalFieldSubstrateConfig,
    neurons: Iterable[MCMNeuron],
    *,
    perception_field: SharedMCMField | None = None,
) -> InstantaneousFieldFlowObservation:
    if not isinstance(field, SharedMCMField):
        raise InstantaneousFieldFlowNullProbeError(
            "flow observation requires one completed shared field"
        )
    if not isinstance(config, NeutralLocalFieldSubstrateConfig):
        raise InstantaneousFieldFlowNullProbeError(
            "flow observation requires the existing substrate configuration"
        )
    ordered_field_neurons = tuple(field.layer.neurons)
    observed_neurons = tuple(neurons)
    if {item.neuron_id for item in observed_neurons} != {
        item.neuron_id for item in ordered_field_neurons
    }:
        raise InstantaneousFieldFlowNullProbeError(
            "flow observation must cover every field neuron exactly once"
        )

    rate = 1.0 / config.response_time_seconds
    position_map = {item.position: item for item in ordered_field_neurons}
    index_by_id = {
        item.neuron_id: index for index, item in enumerate(ordered_field_neurons)
    }
    activation = np.asarray(
        [item.activation for item in ordered_field_neurons],
        dtype=np.float64,
    )
    generator_diffusion = _diffusion_generator(field, config) @ activation
    perception_by_id = (
        {}
        if perception_field is None
        else {
            item.neuron_id: item.perception
            for item in perception_field.layer.neurons
        }
    )

    edges: list[InstantaneousEdgeFlow] = []
    nodes: list[InstantaneousNodeFlow] = []
    for target in observed_neurons:
        local_divergence = 0.0
        for offset in field.layer.sample_offsets:
            source = position_map.get(_mapped_position(field, target, offset))
            if source is None:
                continue
            signed_flow = rate * (source.activation - target.activation)
            local_divergence += signed_flow
            edges.append(
                InstantaneousEdgeFlow(
                    target_neuron_id=target.neuron_id,
                    source_neuron_id=source.neuron_id,
                    relative_position=offset,
                    signed_flow=signed_flow,
                )
            )

        perception = perception_by_id.get(target.neuron_id)
        perception_reconstruction = local_divergence
        if perception is not None:
            perception_reconstruction = sum(
                rate * (sample.activation - target.activation)
                for sample in perception.local_samples
            )
        nodes.append(
            InstantaneousNodeFlow(
                neuron_id=target.neuron_id,
                activation=target.activation,
                local_divergence=local_divergence,
                generator_diffusion=float(
                    generator_diffusion[index_by_id[target.neuron_id]]
                ),
                perception_reconstruction=perception_reconstruction,
            )
        )

    return InstantaneousFieldFlowObservation(
        source_layer_digest=field.layer.digest(),
        response_time_seconds=config.response_time_seconds,
        edges=tuple(
            sorted(
                edges,
                key=lambda item: (
                    item.target_neuron_id,
                    item.source_neuron_id,
                    item.relative_position,
                ),
            )
        ),
        nodes=tuple(sorted(nodes, key=lambda item: item.neuron_id)),
    )


def observe_instantaneous_field_flow(
    field: SharedMCMField,
    config: NeutralLocalFieldSubstrateConfig,
    *,
    perception_field: SharedMCMField | None = None,
) -> InstantaneousFieldFlowObservation:
    """Read instantaneous flow without accumulation or field writeback."""

    return _observe_in_order(
        field,
        config,
        field.layer.neurons,
        perception_field=perception_field,
    )


def _frame(
    snapshot_id: str,
    values: tuple[float, ...],
    *,
    start_tick: int = 0,
    end_tick: int = 10,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id=_GEOMETRY_ID,
        snapshot_id=snapshot_id,
        clock_id="auditory.source",
        window_start_tick=start_tick,
        window_end_tick=end_tick,
        carrier_ids=tuple(
            f"auditory.carrier.{index}" for index in range(len(values))
        ),
        values=values,
    )


def _field_and_distributor() -> tuple[SharedMCMField, ReceptorDistributor]:
    reference = _frame("auditory.reference", tuple(0.0 for _ in _VALUES))
    field = build_shared_mcm_field(
        (reference,),
        {
            "auditory": ReceptorDockAnatomy(
                modality_id="auditory",
                dock_id="dock.auditory",
                positions=tuple((index,) for index in range(len(_VALUES))),
            )
        },
        sample_offsets=_SAMPLE_OFFSETS,
    )
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock("dock.auditory", "auditory", _GEOMETRY_ID)
    )
    return field, distributor


def _distribution(
    distributor: ReceptorDistributor,
    start_tick: int,
    end_tick: int,
    frame: ReceptorContactFrame | None,
):
    return distributor.distribute(
        () if frame is None else (frame,),
        CommonFieldTime(_CLOCK_ID, start_tick, end_tick),
    )


def _maximum(values: Iterable[float]) -> float:
    return max((abs(value) for value in values), default=0.0)


def run_instantaneous_field_flow_null_probe(
) -> InstantaneousFieldFlowNullProbeResult:
    """Verify that instantaneous flow adds no state beyond the fast field."""

    config = NeutralLocalFieldSubstrateConfig(1.0)
    initial, distributor = _field_and_distributor()
    seeded = advance_neutral_shared_field(
        initial,
        _distribution(distributor, 0, 10, _frame("auditory.seed", _VALUES)),
        MCMFieldStepTime(_CLOCK_ID, 0, 10, 10.0),
        config,
    )
    before_digest = seeded.snapshot().digest()
    next_field = advance_neutral_shared_field(
        seeded,
        _distribution(distributor, 10, 20, None),
        MCMFieldStepTime(_CLOCK_ID, 10, 20, 10.0),
        config,
    )
    observation = observe_instantaneous_field_flow(
        seeded,
        config,
        perception_field=next_field,
    )
    reversed_observation = _observe_in_order(
        seeded,
        config,
        reversed(seeded.layer.neurons),
        perception_field=next_field,
    )
    first_history = initial.advance(
        _distribution(
            distributor,
            0,
            10,
            _frame("history.first", _VALUES),
        ),
        receptor_projection_baseline,
    )
    second_history = initial.advance(
        _distribution(
            distributor,
            0,
            10,
            _frame("history.second", tuple(reversed(_VALUES))),
        ),
        receptor_projection_baseline,
    )
    matched_zero_frame = _frame(
        "history.match",
        tuple(0.0 for _ in _VALUES),
        start_tick=10,
        end_tick=20,
    )
    first_matched = first_history.advance(
        _distribution(distributor, 10, 20, matched_zero_frame),
        receptor_projection_baseline,
    )
    second_matched = second_history.advance(
        _distribution(distributor, 10, 20, matched_zero_frame),
        receptor_projection_baseline,
    )
    first_matched_observation = observe_instantaneous_field_flow(
        first_matched,
        config,
    )
    second_matched_observation = observe_instantaneous_field_flow(
        second_matched,
        config,
    )

    edge_lookup = {
        (edge.target_neuron_id, edge.source_neuron_id): edge.signed_flow
        for edge in observation.edges
    }
    edge_error = _maximum(
        flow + edge_lookup[(source_id, target_id)]
        for (target_id, source_id), flow in edge_lookup.items()
    )
    generator_error = _maximum(
        node.local_divergence - node.generator_diffusion
        for node in observation.nodes
    )
    perception_error = _maximum(
        node.local_divergence - node.perception_reconstruction
        for node in observation.nodes
    )
    total_divergence_error = abs(
        sum(node.local_divergence for node in observation.nodes)
    )
    after_digest = seeded.snapshot().digest()

    if max(
        edge_error,
        generator_error,
        perception_error,
        total_divergence_error,
    ) > _TOLERANCE:
        raise InstantaneousFieldFlowNullProbeError(
            "instantaneous local flow failed its passive identity boundary"
        )

    return InstantaneousFieldFlowNullProbeResult(
        observation=observation,
        edge_antisymmetry_error=edge_error,
        total_divergence_error=total_divergence_error,
        generator_identity_error=generator_error,
        perception_identity_error=perception_error,
        order_invariant=observation == reversed_observation,
        fast_matched_full_states_distinct=(
            first_matched.layer.digest() != second_matched.layer.digest()
        ),
        fast_matched_flow_equal=(
            first_matched_observation.edges == second_matched_observation.edges
            and first_matched_observation.nodes
            == second_matched_observation.nodes
        ),
        observer_preserved_source_digest=before_digest == after_digest,
        observer_writeback_performed=False,
        accumulation_performed=False,
        new_runtime_state_added=False,
        runtime_candidate_released=False,
    )


def instantaneous_field_flow_null_probe_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            InstantaneousEdgeFlow,
            InstantaneousNodeFlow,
            InstantaneousFieldFlowObservation,
            InstantaneousFieldFlowNullProbeResult,
        )
        for item in fields(contract)
    )
