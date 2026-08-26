"""Local, bounded, content-neutral receptivity for neutral field contacts."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math

from .neutral_asynchronous_field_runtime import (
    _validate_unique_source_supports,
)
from .neutral_local_field_substrate import (
    NeutralFieldDissipationConfig,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff_audit import handoff_receptor_completion_groups
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import (
    TransientNeuronInputSet,
    project_transient_docks_to_neuron_inputs,
)


ADAPTIVE_RECEPTIVITY_ALPHA_AXIS = (0.0, 0.5, 1.0)
ADAPTIVE_RECEPTIVITY_BETA_PER_SECOND = 0.25
ADAPTIVE_RECEPTIVITY_FLOOR = 0.25


class LocalAdaptiveReceptivityError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class LocalAdaptiveReceptivityConfig:
    alpha_per_amplitude_second: float
    beta_per_second: float = ADAPTIVE_RECEPTIVITY_BETA_PER_SECOND
    floor: float = ADAPTIVE_RECEPTIVITY_FLOOR

    def __post_init__(self) -> None:
        alpha = float(self.alpha_per_amplitude_second)
        beta = float(self.beta_per_second)
        floor = float(self.floor)
        if alpha not in ADAPTIVE_RECEPTIVITY_ALPHA_AXIS:
            raise LocalAdaptiveReceptivityError("alpha axis is preregistered")
        if beta != ADAPTIVE_RECEPTIVITY_BETA_PER_SECOND:
            raise LocalAdaptiveReceptivityError("beta is preregistered")
        if floor != ADAPTIVE_RECEPTIVITY_FLOOR:
            raise LocalAdaptiveReceptivityError("receptivity floor is preregistered")
        object.__setattr__(self, "alpha_per_amplitude_second", alpha)
        object.__setattr__(self, "beta_per_second", beta)
        object.__setattr__(self, "floor", floor)


@dataclass(frozen=True, slots=True)
class LocalReceptivityState:
    neuron_ids: tuple[str, ...]
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.neuron_ids or len(self.neuron_ids) != len(self.values):
            raise LocalAdaptiveReceptivityError("receptivity state must align")
        if len(set(self.neuron_ids)) != len(self.neuron_ids):
            raise LocalAdaptiveReceptivityError("receptivity neuron ids must be unique")
        values = tuple(float(value) for value in self.values)
        if any(not math.isfinite(value) or not ADAPTIVE_RECEPTIVITY_FLOOR <= value <= 1.0
               for value in values):
            raise LocalAdaptiveReceptivityError("receptivity left its local bounds")
        object.__setattr__(self, "values", values)

    @classmethod
    def fresh(cls, field) -> "LocalReceptivityState":
        ids = tuple(neuron.neuron_id for neuron in field.layer.neurons)
        return cls(ids, (1.0,) * len(ids))

    def for_neuron(self, neuron_id: str) -> float:
        return self.values[self.neuron_ids.index(neuron_id)]


def advance_local_receptivity(value, energy, elapsed_seconds, config):
    value = float(value)
    energy = float(energy)
    elapsed = float(elapsed_seconds)
    if not config.floor <= value <= 1.0 or energy < 0.0 or elapsed < 0.0:
        raise LocalAdaptiveReceptivityError("invalid local receptivity transition")
    if config.alpha_per_amplitude_second == 0.0 or elapsed == 0.0:
        return value
    rate = config.beta_per_second + config.alpha_per_amplitude_second * energy
    equilibrium = config.beta_per_second / rate
    next_value = equilibrium + (value - equilibrium) * math.exp(-rate * elapsed)
    return min(1.0, max(config.floor, next_value))


def advance_receptivity_state(state, field, elapsed_seconds, config):
    neurons = field.layer.neurons
    if state.neuron_ids != tuple(neuron.neuron_id for neuron in neurons):
        raise LocalAdaptiveReceptivityError("receptivity anatomy changed")
    return LocalReceptivityState(
        state.neuron_ids,
        tuple(
            advance_local_receptivity(
                value,
                abs(neuron.activation) + abs(neuron.afterimage),
                elapsed_seconds,
                config,
            )
            for value, neuron in zip(state.values, neurons, strict=True)
        ),
    )


def scale_local_receptor_inputs(inputs, state):
    scaled = []
    for item in inputs.neuron_inputs:
        receptivity = state.for_neuron(item.neuron_id)
        scaled.append(replace(
            item,
            contacts=tuple(
                replace(contact, value=contact.value * receptivity)
                for contact in item.contacts
            ),
        ))
    return TransientNeuronInputSet(inputs.step_time, tuple(scaled))


@dataclass(frozen=True, slots=True)
class AdaptiveReceptivityRun:
    field: object
    receptivity: LocalReceptivityState
    source_support_count: int


def run_adaptive_receptivity_field(
    field, receptivity, sequences, proposal_steps, substrate_config,
    afterimage_config, receptivity_config,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
):
    sequences_in = tuple(sequences)
    steps_in = tuple(proposal_steps)
    source_support_count = _validate_unique_source_supports(sequences_in)
    handoff = handoff_receptor_completion_groups(sequences_in, steps_in)
    current = field
    local_state = receptivity
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, current.docks)
        inputs = project_transient_docks_to_neuron_inputs(trajectory, current.docks)
        scaled = scale_local_receptor_inputs(inputs, local_state)
        distribution = ReceptorDistribution(
            CommonFieldTime(batch.step_time.clock_id, batch.step_time.start_tick,
                            batch.step_time.end_tick), ()
        )
        current = advance_neutral_fast_shared_field_transient(
            current, distribution, scaled, substrate_config, afterimage_config,
            dissipation_config,
        )
        local_state = advance_receptivity_state(
            local_state, current, batch.step_time.elapsed_seconds, receptivity_config
        )
    return AdaptiveReceptivityRun(current, local_state, source_support_count)
