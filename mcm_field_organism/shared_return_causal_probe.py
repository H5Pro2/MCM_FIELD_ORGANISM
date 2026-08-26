"""Two-step causal baselines in the active shared MCM field."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .mcm_neuron_layer import receptor_projection_baseline
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import ReceptorDistributor, ReceptorDock
from .shared_mcm_field import ReceptorDockAnatomy, build_shared_mcm_field
from .simulated_effector_world import (
    InterventionCause,
    SimulatedWorldState,
    WorldIntervention,
    advance_simulated_world,
    receptor_frame_from_world,
)
from .simulated_world_mcm_path import simulated_world_receptor_to_contact_frame


SharedReturnArm = Literal["original", "interrupted", "swapped"]
_ARMS: tuple[SharedReturnArm, ...] = ("original", "interrupted", "swapped")
_CLOCK_ID = "organism.shared.return"


@dataclass(frozen=True, slots=True)
class SharedReturnMeasurement:
    start_position: int
    requested_delta: int
    arm: SharedReturnArm
    second_world_digest: str
    first_activation: tuple[float, ...]
    second_receptor_values: tuple[float, ...]
    second_activation: tuple[float, ...]
    second_afterimage: tuple[float, ...]
    second_layer_digest: str
    second_snapshot_digest: str
    local_samples_match_first_state: bool


@dataclass(frozen=True, slots=True)
class SharedReturnCausalResult:
    measurements: tuple[SharedReturnMeasurement, ...]
    case_count: int
    observation_count: int
    second_worlds_equal_count: int
    second_fast_states_equal_count: int
    interrupted_layer_difference_count: int
    swapped_layer_difference_count: int
    interrupted_snapshot_difference_count: int
    swapped_snapshot_difference_count: int
    all_second_activations_match_contact: bool
    all_second_afterimages_zero: bool
    all_local_samples_match_first_state: bool
    deterministic_reproduction: bool
    connects_field_to_effector: bool = False

    def __post_init__(self) -> None:
        if self.connects_field_to_effector:
            raise ValueError("this probe cannot connect the MCM field to the effector")


def _contact_frames(
    values: tuple[float, ...],
    step: int,
) -> tuple[ReceptorContactFrame, ...]:
    return tuple(
        ReceptorContactFrame(
            modality_id=f"modality.{index}",
            geometry_id=f"geometry.{index}",
            snapshot_id=f"shared.return.s{step}.m{index}",
            clock_id=f"source.{index}",
            window_start_tick=step * 10,
            window_end_tick=(step + 1) * 10,
            carrier_ids=(f"carrier.{index}",),
            values=(value,),
        )
        for index, value in enumerate(values)
    )


def _build_field_and_distributor():
    references = _contact_frames((0.0,) * 7, 0)
    anatomies = {
        f"modality.{index}": ReceptorDockAnatomy(
            f"modality.{index}", f"dock.{index}", ((0, index),)
        )
        for index in range(7)
    }
    field = build_shared_mcm_field(
        references,
        anatomies,
        sample_offsets=((0, -1), (0, 1)),
        field_id="organism.shared.return.field",
        layer_id="organism.shared.return.layer",
        geometry_id="organism.shared.return.line7.v1",
    )
    distributor = ReceptorDistributor()
    for index in range(7):
        distributor.attach(
            ReceptorDock(f"dock.{index}", f"modality.{index}", f"geometry.{index}")
        )
    return field, distributor


def _measure(
    start_position: int,
    requested_delta: int,
    arm: SharedReturnArm,
) -> SharedReturnMeasurement:
    first_transition = advance_simulated_world(
        SimulatedWorldState(tick=0, position=start_position),
        WorldIntervention(0, requested_delta, InterventionCause.EXTERNAL),
    )
    first_values = simulated_world_receptor_to_contact_frame(
        receptor_frame_from_world(first_transition.next_world)
    ).values
    if arm == "interrupted":
        first_values = (0.0,) * 7
    elif arm == "swapped":
        first_values = tuple(reversed(first_values))

    field, distributor = _build_field_and_distributor()
    first_distribution = distributor.distribute(
        _contact_frames(first_values, 1),
        CommonFieldTime(_CLOCK_ID, 10, 20),
    )
    field = field.advance(first_distribution, receptor_projection_baseline)
    first_activation = field.snapshot().activation

    second_transition = advance_simulated_world(
        first_transition.next_world,
        WorldIntervention(1, 0, InterventionCause.EXTERNAL),
    )
    second_values = simulated_world_receptor_to_contact_frame(
        receptor_frame_from_world(second_transition.next_world)
    ).values
    second_distribution = distributor.distribute(
        _contact_frames(second_values, 2),
        CommonFieldTime(_CLOCK_ID, 20, 30),
    )
    field = field.advance(second_distribution, receptor_projection_baseline)
    snapshot = field.snapshot()
    first_by_neuron = dict(zip(snapshot.neuron_ids, first_activation, strict=True))
    samples_match = all(
        all(
            sample.activation == first_by_neuron[sample.sample_id.removeprefix("sample.")]
            and sample.afterimage == 0.0
            and sample.source_tick == 1
            for sample in neuron.perception.local_samples
        )
        for neuron in snapshot.layer.neurons
    )
    return SharedReturnMeasurement(
        start_position=start_position,
        requested_delta=requested_delta,
        arm=arm,
        second_world_digest=second_transition.next_world.digest(),
        first_activation=first_activation,
        second_receptor_values=second_values,
        second_activation=snapshot.activation,
        second_afterimage=snapshot.afterimage,
        second_layer_digest=snapshot.layer.digest(),
        second_snapshot_digest=snapshot.digest(),
        local_samples_match_first_state=samples_match,
    )


def _measure_all() -> tuple[SharedReturnMeasurement, ...]:
    return tuple(
        _measure(start_position, requested_delta, arm)
        for start_position in range(7)
        for requested_delta in (-1, 1)
        for arm in _ARMS
    )


def run_shared_return_causal_probe() -> SharedReturnCausalResult:
    measurements = _measure_all()
    by_case = {
        (item.start_position, item.requested_delta, item.arm): item
        for item in measurements
    }
    comparisons = [
        tuple(by_case[(start, delta, arm)] for arm in _ARMS)
        for start in range(7)
        for delta in (-1, 1)
    ]
    return SharedReturnCausalResult(
        measurements=measurements,
        case_count=len(comparisons),
        observation_count=len(measurements),
        second_worlds_equal_count=sum(
            original.second_world_digest == interrupted.second_world_digest == swapped.second_world_digest
            for original, interrupted, swapped in comparisons
        ),
        second_fast_states_equal_count=sum(
            item.second_activation == original.second_activation
            and item.second_afterimage == original.second_afterimage
            for original, interrupted, swapped in comparisons
            for item in (interrupted, swapped)
        ),
        interrupted_layer_difference_count=sum(
            original.second_layer_digest != interrupted.second_layer_digest
            for original, interrupted, _ in comparisons
        ),
        swapped_layer_difference_count=sum(
            original.second_layer_digest != swapped.second_layer_digest
            for original, _, swapped in comparisons
        ),
        interrupted_snapshot_difference_count=sum(
            original.second_snapshot_digest != interrupted.second_snapshot_digest
            for original, interrupted, _ in comparisons
        ),
        swapped_snapshot_difference_count=sum(
            original.second_snapshot_digest != swapped.second_snapshot_digest
            for original, _, swapped in comparisons
        ),
        all_second_activations_match_contact=all(
            item.second_activation == item.second_receptor_values for item in measurements
        ),
        all_second_afterimages_zero=all(
            item.second_afterimage == (0.0,) * 7 for item in measurements
        ),
        all_local_samples_match_first_state=all(
            item.local_samples_match_first_state for item in measurements
        ),
        deterministic_reproduction=measurements == _measure_all(),
    )
