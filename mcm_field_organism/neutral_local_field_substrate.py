"""Exact integration of one neutral local generator on the shared MCM field."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

import numpy as np

from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import MCMNeuronDrive, MCMNeuronOutput
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import (
    SharedMCMField,
    SharedMCMFieldError,
    _mapped_receptor_contacts,
)


class NeutralLocalFieldSubstrateError(ValueError):
    """Raised when the neutral local field generator cannot advance exactly."""


@dataclass(frozen=True, slots=True)
class NeutralLocalFieldSubstrateConfig:
    """One exposed interaction time, without semantic or modal weights."""

    response_time_seconds: float

    def __post_init__(self) -> None:
        value = float(self.response_time_seconds)
        if not math.isfinite(value) or value <= 0.0:
            raise NeutralLocalFieldSubstrateError(
                "response_time_seconds must be finite and greater than zero"
            )
        object.__setattr__(self, "response_time_seconds", value)


def _step_duration(
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
) -> float:
    if not isinstance(distribution, ReceptorDistribution):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires one receptor distribution"
        )
    if not isinstance(step_time, MCMFieldStepTime):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires one explicit field step"
        )
    field_time = distribution.field_time
    if (
        step_time.clock_id != field_time.clock_id
        or step_time.start_tick != field_time.window_start_tick
        or step_time.end_tick != field_time.window_end_tick
    ):
        raise NeutralLocalFieldSubstrateError(
            "field step must match the distributed organism interval"
        )
    return step_time.elapsed_seconds


def _neighbor_matrix(field: SharedMCMField) -> np.ndarray:
    layer = field.layer
    neurons = layer.neurons
    position_index = {
        neuron.position: index for index, neuron in enumerate(neurons)
    }
    matrix = np.zeros((len(neurons), len(neurons)), dtype=np.float64)
    for target_index, neuron in enumerate(neurons):
        for offset in layer.sample_offsets:
            source_position = [
                coordinate + delta
                for coordinate, delta in zip(
                    neuron.position,
                    offset,
                    strict=True,
                )
            ]
            for axis in layer.periodic_axes:
                source_position[axis.axis_index] = axis.origin + (
                    (source_position[axis.axis_index] - axis.origin)
                    % axis.size
                )
            source_index = position_index.get(tuple(source_position))
            if source_index is not None:
                matrix[target_index, source_index] = 1.0
    if not np.array_equal(matrix, matrix.T):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires symmetric field adjacency"
        )
    return matrix


def _generator_and_boundary(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    config: NeutralLocalFieldSubstrateConfig,
) -> tuple[np.ndarray, np.ndarray]:
    try:
        receptor_contacts = _mapped_receptor_contacts(
            field.docks,
            distribution,
        )
    except SharedMCMFieldError as exc:
        raise NeutralLocalFieldSubstrateError(str(exc)) from exc

    neurons = field.layer.neurons
    neuron_index = {
        neuron.neuron_id: index for index, neuron in enumerate(neurons)
    }
    adjacency = _neighbor_matrix(field)
    rate = 1.0 / config.response_time_seconds
    generator = rate * adjacency
    boundary = np.zeros(len(neurons), dtype=np.float64)
    for index in range(len(neurons)):
        generator[index, index] -= rate * float(np.sum(adjacency[index]))
    for neuron_id, contact in receptor_contacts.items():
        index = neuron_index[neuron_id]
        generator[index, index] -= rate
        boundary[index] += rate * contact
    return generator, boundary


def _integrate_exactly(
    previous: np.ndarray,
    generator: np.ndarray,
    boundary: np.ndarray,
    elapsed_seconds: float,
) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    projected_state = eigenvectors.T @ previous
    projected_boundary = eigenvectors.T @ boundary
    exponent = np.exp(eigenvalues * elapsed_seconds)
    integral = np.empty_like(eigenvalues)
    zero = np.isclose(eigenvalues, 0.0, rtol=0.0, atol=1e-14)
    integral[zero] = elapsed_seconds
    integral[~zero] = np.expm1(
        eigenvalues[~zero] * elapsed_seconds
    ) / eigenvalues[~zero]
    result = eigenvectors @ (
        exponent * projected_state + integral * projected_boundary
    )
    if not np.all(np.isfinite(result)):
        raise NeutralLocalFieldSubstrateError(
            "neutral local field integration produced a non-finite state"
        )
    if np.any(result < -1.0 - 1e-12) or np.any(result > 1.0 + 1e-12):
        raise NeutralLocalFieldSubstrateError(
            "neutral local field integration left the normalized field domain"
        )
    return np.clip(result, -1.0, 1.0)


def advance_neutral_shared_field(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    config: NeutralLocalFieldSubstrateConfig,
) -> SharedMCMField:
    """Advance one field interval through an exact uniform local generator."""

    if not isinstance(field, SharedMCMField):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires one shared MCM field"
        )
    if not isinstance(config, NeutralLocalFieldSubstrateConfig):
        raise NeutralLocalFieldSubstrateError(
            "neutral local substrate requires an explicit configuration"
        )
    elapsed = _step_duration(distribution, step_time)
    generator, boundary = _generator_and_boundary(
        field,
        distribution,
        config,
    )
    neurons = field.layer.neurons
    previous = np.asarray(
        [neuron.activation for neuron in neurons],
        dtype=np.float64,
    )
    activation = _integrate_exactly(
        previous,
        generator,
        boundary,
        elapsed,
    )
    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]),
            neuron.afterimage,
        )
        for index, neuron in enumerate(neurons)
    }

    def exact_local_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    try:
        return field.advance(
            distribution,
            exact_local_output,
            step_time=step_time,
        )
    except SharedMCMFieldError as exc:
        raise NeutralLocalFieldSubstrateError(str(exc)) from exc


def neutral_local_field_substrate_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(NeutralLocalFieldSubstrateConfig))
