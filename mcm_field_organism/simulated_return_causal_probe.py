"""Synthetic causal baselines for the simulated world-to-field return path."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

from .mcm_neuron_layer import receptor_projection_baseline
from .sensor_mcm_field import CommonFieldTime, build_receptor_aligned_mcm_field
from .simulated_effector_world import (
    InterventionCause,
    SimulatedWorldState,
    WorldIntervention,
    advance_simulated_world,
    receptor_frame_from_world,
)
from .simulated_world_mcm_path import simulated_world_receptor_to_contact_frame


ReturnArm = Literal["original", "neutral", "interrupted", "swapped"]
TwoStepArm = Literal["original", "interrupted", "swapped"]
RETURN_ARMS: tuple[ReturnArm, ...] = (
    "original",
    "neutral",
    "interrupted",
    "swapped",
)


@dataclass(frozen=True, slots=True)
class SimulatedReturnMeasurement:
    start_position: int
    requested_delta: int
    arm: ReturnArm
    applied_delta: int
    world_position: int
    world_digest: str
    receptor_values: tuple[float, ...]
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    field_window_digest: str


@dataclass(frozen=True, slots=True)
class SimulatedReturnCausalResult:
    measurements: tuple[SimulatedReturnMeasurement, ...]
    case_count: int
    observation_count: int
    neutral_world_difference_count: int
    interrupted_world_equality_count: int
    interrupted_field_difference_count: int
    swapped_world_equality_count: int
    swapped_receptor_difference_count: int
    swapped_field_difference_count: int
    all_afterimages_zero: bool
    deterministic_reproduction: bool
    connects_field_to_effector: bool = False

    def __post_init__(self) -> None:
        if self.connects_field_to_effector:
            raise ValueError("this probe cannot connect the MCM field to the effector")


@dataclass(frozen=True, slots=True)
class SimulatedTwoStepMeasurement:
    start_position: int
    requested_delta: int
    arm: TwoStepArm
    second_world_digest: str
    first_activation: tuple[float, ...]
    second_receptor_values: tuple[float, ...]
    second_activation: tuple[float, ...]
    second_afterimage: tuple[float, ...]
    second_layer_digest: str
    local_samples_match_first_state: bool


@dataclass(frozen=True, slots=True)
class SimulatedTwoStepCausalResult:
    measurements: tuple[SimulatedTwoStepMeasurement, ...]
    case_count: int
    observation_count: int
    second_worlds_equal_count: int
    second_fast_states_equal_count: int
    interrupted_layer_difference_count: int
    swapped_layer_difference_count: int
    all_second_activations_match_contact: bool
    all_second_afterimages_zero: bool
    all_local_samples_match_first_state: bool
    deterministic_reproduction: bool
    connects_field_to_effector: bool = False

    def __post_init__(self) -> None:
        if self.connects_field_to_effector:
            raise ValueError("this probe cannot connect the MCM field to the effector")


def _measure(start_position: int, requested_delta: int, arm: ReturnArm) -> SimulatedReturnMeasurement:
    applied_delta = 0 if arm == "neutral" else requested_delta
    transition = advance_simulated_world(
        SimulatedWorldState(tick=0, position=start_position),
        WorldIntervention(
            source_tick=0,
            delta=applied_delta,
            cause=InterventionCause.EXTERNAL,
        ),
    )
    simulated = receptor_frame_from_world(transition.next_world)
    contact = simulated_world_receptor_to_contact_frame(simulated)
    if arm == "interrupted":
        contact = replace(contact, values=(0.0,) * len(contact.values))
    elif arm == "swapped":
        contact = replace(contact, values=tuple(reversed(contact.values)))

    field = build_receptor_aligned_mcm_field(
        contact,
        positions=tuple((position,) for position in range(7)),
        sample_offsets=((-1,), (1,)),
        dock_id="simulated",
        layer_id="simulated.return.layer",
        field_id="simulated.return.field",
        field_geometry_id="simulated.return.line7.v1",
    ).advance(
        contact,
        CommonFieldTime("organism.simulated.return", 1, 2),
        receptor_projection_baseline,
    )
    window = field.field_window()
    return SimulatedReturnMeasurement(
        start_position=start_position,
        requested_delta=requested_delta,
        arm=arm,
        applied_delta=applied_delta,
        world_position=transition.next_world.position,
        world_digest=transition.next_world.digest(),
        receptor_values=contact.values,
        activation=window.activation,
        afterimage=window.afterimage,
        field_window_digest=window.digest(),
    )


def _measure_all() -> tuple[SimulatedReturnMeasurement, ...]:
    return tuple(
        _measure(start_position, requested_delta, arm)
        for start_position in range(7)
        for requested_delta in (-1, 1)
        for arm in RETURN_ARMS
    )


def run_simulated_return_causal_probe() -> SimulatedReturnCausalResult:
    measurements = _measure_all()
    by_case = {
        (item.start_position, item.requested_delta, item.arm): item
        for item in measurements
    }
    comparisons = []
    for start_position in range(7):
        for requested_delta in (-1, 1):
            comparisons.append(tuple(
                by_case[(start_position, requested_delta, arm)] for arm in RETURN_ARMS
            ))

    repeated = _measure_all()
    return SimulatedReturnCausalResult(
        measurements=measurements,
        case_count=len(comparisons),
        observation_count=len(measurements),
        neutral_world_difference_count=sum(
            original.world_digest != neutral.world_digest
            for original, neutral, _, _ in comparisons
        ),
        interrupted_world_equality_count=sum(
            original.world_digest == interrupted.world_digest
            for original, _, interrupted, _ in comparisons
        ),
        interrupted_field_difference_count=sum(
            original.field_window_digest != interrupted.field_window_digest
            for original, _, interrupted, _ in comparisons
        ),
        swapped_world_equality_count=sum(
            original.world_digest == swapped.world_digest
            for original, _, _, swapped in comparisons
        ),
        swapped_receptor_difference_count=sum(
            original.receptor_values != swapped.receptor_values
            for original, _, _, swapped in comparisons
        ),
        swapped_field_difference_count=sum(
            original.field_window_digest != swapped.field_window_digest
            for original, _, _, swapped in comparisons
        ),
        all_afterimages_zero=all(
            item.afterimage == (0.0,) * 7 for item in measurements
        ),
        deterministic_reproduction=(measurements == repeated),
    )


def _two_step_measure(
    start_position: int,
    requested_delta: int,
    arm: TwoStepArm,
) -> SimulatedTwoStepMeasurement:
    first_transition = advance_simulated_world(
        SimulatedWorldState(tick=0, position=start_position),
        WorldIntervention(0, requested_delta, InterventionCause.EXTERNAL),
    )
    first_contact = simulated_world_receptor_to_contact_frame(
        receptor_frame_from_world(first_transition.next_world)
    )
    if arm == "interrupted":
        first_contact = replace(first_contact, values=(0.0,) * 7)
    elif arm == "swapped":
        first_contact = replace(first_contact, values=tuple(reversed(first_contact.values)))

    field = build_receptor_aligned_mcm_field(
        first_contact,
        positions=tuple((position,) for position in range(7)),
        sample_offsets=((-1,), (1,)),
        dock_id="simulated",
        layer_id="simulated.return.layer",
        field_id="simulated.return.field",
        field_geometry_id="simulated.return.line7.v1",
    ).advance(
        first_contact,
        CommonFieldTime("organism.simulated.return", 1, 2),
        receptor_projection_baseline,
    )
    first_activation = field.field_window().activation

    second_transition = advance_simulated_world(
        first_transition.next_world,
        WorldIntervention(1, 0, InterventionCause.EXTERNAL),
    )
    second_contact = simulated_world_receptor_to_contact_frame(
        receptor_frame_from_world(second_transition.next_world)
    )
    field = field.advance(
        second_contact,
        CommonFieldTime("organism.simulated.return", 2, 3),
        receptor_projection_baseline,
    )
    window = field.field_window()
    local_samples_match = all(
        all(
            sample.activation == first_activation[int(sample.sample_id.rsplit("n", 1)[1])]
            and sample.afterimage == 0.0
            and sample.source_tick == 1
            for sample in neuron.perception.local_samples
        )
        for neuron in field.layer.neurons
    )
    return SimulatedTwoStepMeasurement(
        start_position=start_position,
        requested_delta=requested_delta,
        arm=arm,
        second_world_digest=second_transition.next_world.digest(),
        first_activation=first_activation,
        second_receptor_values=second_contact.values,
        second_activation=window.activation,
        second_afterimage=window.afterimage,
        second_layer_digest=field.layer.digest(),
        local_samples_match_first_state=local_samples_match,
    )


def _measure_all_two_step() -> tuple[SimulatedTwoStepMeasurement, ...]:
    return tuple(
        _two_step_measure(start_position, requested_delta, arm)
        for start_position in range(7)
        for requested_delta in (-1, 1)
        for arm in ("original", "interrupted", "swapped")
    )


def run_simulated_two_step_causal_probe() -> SimulatedTwoStepCausalResult:
    measurements = _measure_all_two_step()
    by_case = {
        (item.start_position, item.requested_delta, item.arm): item
        for item in measurements
    }
    comparisons = [
        tuple(
            by_case[(start_position, requested_delta, arm)]
            for arm in ("original", "interrupted", "swapped")
        )
        for start_position in range(7)
        for requested_delta in (-1, 1)
    ]
    return SimulatedTwoStepCausalResult(
        measurements=measurements,
        case_count=len(comparisons),
        observation_count=len(measurements),
        second_worlds_equal_count=sum(
            original.second_world_digest
            == interrupted.second_world_digest
            == swapped.second_world_digest
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
        all_second_activations_match_contact=all(
            item.second_activation == item.second_receptor_values
            for item in measurements
        ),
        all_second_afterimages_zero=all(
            item.second_afterimage == (0.0,) * 7 for item in measurements
        ),
        all_local_samples_match_first_state=all(
            item.local_samples_match_first_state for item in measurements
        ),
        deterministic_reproduction=(measurements == _measure_all_two_step()),
    )
