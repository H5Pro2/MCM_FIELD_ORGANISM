"""Exact integration of the neutral fast S/H dynamics.

"Substrate" is a historical technical module name here. This module provides
the current field response and optional fast passive afterimage, not an MCM
memory substrate.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
from typing import Callable

import numpy as np

from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import MCMNeuronDrive, MCMNeuronOutput
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import (
    SharedMCMField,
    SharedMCMFieldError,
    _mapped_receptor_contacts,
)
from .transient_neuron_input import TransientNeuronInputSet


_FastStateObserver = Callable[[int, np.ndarray, np.ndarray], None]


class NeutralLocalFieldSubstrateError(ValueError):
    """Raised when the neutral local field generator cannot advance exactly."""


@dataclass(frozen=True, slots=True)
class NeutralLocalFieldSubstrateConfig:
    """One S/H response time, without semantic, modal, or memory roles."""

    response_time_seconds: float

    def __post_init__(self) -> None:
        value = float(self.response_time_seconds)
        if not math.isfinite(value) or value <= 0.0:
            raise NeutralLocalFieldSubstrateError(
                "response_time_seconds must be finite and greater than zero"
            )
        object.__setattr__(self, "response_time_seconds", value)


@dataclass(frozen=True, slots=True)
class NeutralFastAfterimageConfig:
    """One exposed fast-trace time without adaptive or semantic roles."""

    time_constant_seconds: float

    def __post_init__(self) -> None:
        value = float(self.time_constant_seconds)
        if not math.isfinite(value) or value <= 0.0:
            raise NeutralLocalFieldSubstrateError(
                "afterimage time_constant_seconds must be finite and greater than zero"
            )
        object.__setattr__(self, "time_constant_seconds", value)


@dataclass(frozen=True, slots=True)
class NeutralFieldDissipationConfig:
    """One content-neutral local loss rate shared by activation and afterimage."""

    leak_rate_per_second: float

    def __post_init__(self) -> None:
        value = float(self.leak_rate_per_second)
        if not math.isfinite(value) or value < 0.0:
            raise NeutralLocalFieldSubstrateError(
                "leak_rate_per_second must be finite and nonnegative"
            )
        object.__setattr__(self, "leak_rate_per_second", value)


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


def _diffusion_generator(
    field: SharedMCMField,
    config: NeutralLocalFieldSubstrateConfig,
) -> np.ndarray:
    adjacency = _neighbor_matrix(field)
    rate = 1.0 / config.response_time_seconds
    generator = rate * adjacency
    for index in range(len(field.layer.neurons)):
        generator[index, index] -= rate * float(np.sum(adjacency[index]))
    return generator


def _integrate_exactly(
    previous: np.ndarray,
    generator: np.ndarray,
    boundary: np.ndarray,
    elapsed_seconds: float,
) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    return _integrate_with_spectrum(
        previous,
        eigenvalues,
        eigenvectors,
        boundary,
        elapsed_seconds,
    )


def _integrate_with_spectrum(
    previous: np.ndarray,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
    boundary: np.ndarray,
    elapsed_seconds: float,
) -> np.ndarray:
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


def _integrate_activation_afterimage_with_spectrum(
    previous_activation: np.ndarray,
    previous_afterimage: np.ndarray,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray,
    boundary: np.ndarray,
    elapsed_seconds: float,
    afterimage_time_seconds: float,
    leak_rate_per_second: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    if leak_rate_per_second != 0.0:
        eigenvalues = eigenvalues - leak_rate_per_second
    projected_activation = eigenvectors.T @ previous_activation
    projected_afterimage = eigenvectors.T @ previous_afterimage
    projected_boundary = eigenvectors.T @ boundary
    tracking_rate = 1.0 / afterimage_time_seconds
    rate = tracking_rate + leak_rate_per_second
    activation_exponent = np.exp(eigenvalues * elapsed_seconds)
    afterimage_exponent = math.exp(-rate * elapsed_seconds)

    activation_integral = np.empty_like(eigenvalues)
    zero_eigenvalue = np.isclose(
        eigenvalues,
        0.0,
        rtol=0.0,
        atol=1e-14,
    )
    activation_integral[zero_eigenvalue] = elapsed_seconds
    activation_integral[~zero_eigenvalue] = np.expm1(
        eigenvalues[~zero_eigenvalue] * elapsed_seconds
    ) / eigenvalues[~zero_eigenvalue]

    activation_to_afterimage = np.empty_like(eigenvalues)
    resonance = np.isclose(
        eigenvalues + rate,
        0.0,
        rtol=0.0,
        atol=1e-14,
    )
    activation_to_afterimage[resonance] = (
        tracking_rate * elapsed_seconds * afterimage_exponent
    )
    activation_to_afterimage[~resonance] = tracking_rate * (
        activation_exponent[~resonance] - afterimage_exponent
    ) / (eigenvalues[~resonance] + rate)

    boundary_to_afterimage = np.empty_like(eigenvalues)
    if leak_rate_per_second == 0.0:
        boundary_to_afterimage[zero_eigenvalue] = (
            elapsed_seconds - (1.0 - afterimage_exponent) / rate
        )
        boundary_to_afterimage[~zero_eigenvalue] = (
            activation_to_afterimage[~zero_eigenvalue]
            - (1.0 - afterimage_exponent)
        ) / eigenvalues[~zero_eigenvalue]
    else:
        boundary_to_afterimage[zero_eigenvalue] = tracking_rate * (
            elapsed_seconds / rate
            - (1.0 - afterimage_exponent) / (rate * rate)
        )
        boundary_to_afterimage[~zero_eigenvalue] = (
            activation_to_afterimage[~zero_eigenvalue]
            - (tracking_rate / rate) * (1.0 - afterimage_exponent)
        ) / eigenvalues[~zero_eigenvalue]

    projected_next_activation = (
        activation_exponent * projected_activation
        + activation_integral * projected_boundary
    )
    projected_next_afterimage = (
        afterimage_exponent * projected_afterimage
        + activation_to_afterimage * projected_activation
        + boundary_to_afterimage * projected_boundary
    )
    activation = eigenvectors @ projected_next_activation
    afterimage = eigenvectors @ projected_next_afterimage
    if not np.all(np.isfinite(activation)) or not np.all(np.isfinite(afterimage)):
        raise NeutralLocalFieldSubstrateError(
            "neutral fast field integration produced a non-finite state"
        )
    if (
        np.any(activation < -1.0 - 1e-12)
        or np.any(activation > 1.0 + 1e-12)
        or np.any(afterimage < -1.0 - 1e-12)
        or np.any(afterimage > 1.0 + 1e-12)
    ):
        raise NeutralLocalFieldSubstrateError(
            "neutral fast field integration left the normalized field domain"
        )
    return (
        np.clip(activation, -1.0, 1.0),
        np.clip(afterimage, -1.0, 1.0),
    )


def _advance_projected_activation(
    projected_activation: np.ndarray,
    eigenvalues: np.ndarray,
    elapsed_seconds: float,
) -> np.ndarray:
    """Advance a contact-free state without leaving the spectral basis."""

    return np.exp(eigenvalues * elapsed_seconds) * projected_activation


def _advance_projected_activation_afterimage(
    projected_activation: np.ndarray,
    projected_afterimage: np.ndarray,
    eigenvalues: np.ndarray,
    elapsed_seconds: float,
    afterimage_time_seconds: float,
    leak_rate_per_second: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Advance the contact-free fast field in its unchanged spectral basis."""

    if leak_rate_per_second != 0.0:
        eigenvalues = eigenvalues - leak_rate_per_second
    tracking_rate = 1.0 / afterimage_time_seconds
    rate = tracking_rate + leak_rate_per_second
    activation_exponent = np.exp(eigenvalues * elapsed_seconds)
    afterimage_exponent = math.exp(-rate * elapsed_seconds)
    activation_to_afterimage = np.empty_like(eigenvalues)
    resonance = np.isclose(
        eigenvalues + rate,
        0.0,
        rtol=0.0,
        atol=1e-14,
    )
    activation_to_afterimage[resonance] = (
        tracking_rate * elapsed_seconds * afterimage_exponent
    )
    activation_to_afterimage[~resonance] = tracking_rate * (
        activation_exponent[~resonance] - afterimage_exponent
    ) / (eigenvalues[~resonance] + rate)
    return (
        activation_exponent * projected_activation,
        afterimage_exponent * projected_afterimage
        + activation_to_afterimage * projected_activation,
    )


def _apply_projected_point_contacts(
    projected_activation: np.ndarray,
    eigenvectors: np.ndarray,
    grouped: list[tuple[int, float, float]],
    response_time_seconds: float,
    leak_rate_per_second: float = 0.0,
) -> np.ndarray:
    """Apply simultaneous local contacts without a full basis round trip."""

    indices = tuple(dict.fromkeys(index for index, _, _ in grouped))
    before = {
        index: float(eigenvectors[index] @ projected_activation)
        for index in indices
    }
    next_values: dict[int, float] = {}
    for index, read_duration, value in grouped:
        response_rate = 1.0 / response_time_seconds
        if leak_rate_per_second == 0.0:
            retention = math.exp(-read_duration / response_time_seconds)
            next_values[index] = retention * before[index] + (1.0 - retention) * value
        else:
            total_rate = response_rate + leak_rate_per_second
            retention = math.exp(-total_rate * read_duration)
            equilibrium = response_rate * value / total_rate
            next_values[index] = retention * before[index] + (1.0 - retention) * equilibrium
    updated = np.array(projected_activation, copy=True)
    for index, next_value in next_values.items():
        updated += eigenvectors[index] * (next_value - before[index])
    return updated


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


def advance_neutral_shared_field_transient(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    config: NeutralLocalFieldSubstrateConfig,
) -> SharedMCMField:
    """Advance lossless asynchronous completions without sensor-driven ticks."""

    if not isinstance(field, SharedMCMField):
        raise NeutralLocalFieldSubstrateError(
            "transient substrate requires one shared MCM field"
        )
    if not isinstance(config, NeutralLocalFieldSubstrateConfig):
        raise NeutralLocalFieldSubstrateError(
            "transient substrate requires an explicit configuration"
        )
    if not isinstance(transient_inputs, TransientNeuronInputSet):
        raise NeutralLocalFieldSubstrateError(
            "transient substrate requires one complete local input set"
        )
    if distribution.contacts:
        raise NeutralLocalFieldSubstrateError(
            "transient substrate requires a contact-free boundary distribution"
        )
    step_time = transient_inputs.step_time
    _step_duration(distribution, step_time)
    expected_ids = set(field.layer.docked_neuron_ids)
    actual_ids = {
        item.neuron_id for item in transient_inputs.neuron_inputs
    }
    if actual_ids != expected_ids:
        raise NeutralLocalFieldSubstrateError(
            "transient inputs must cover every receptor dock neuron"
        )

    neurons = field.layer.neurons
    neuron_index = {
        neuron.neuron_id: index for index, neuron in enumerate(neurons)
    }
    events: dict[int, list[tuple[int, float, float]]] = {}
    ticks_per_second = step_time.ticks_per_second
    for neuron_input in transient_inputs.neuron_inputs:
        index = neuron_index[neuron_input.neuron_id]
        for contact in neuron_input.contacts:
            read_duration = (
                contact.organism_read_time.window_end_tick
                - contact.organism_read_time.window_start_tick
            ) / ticks_per_second
            events.setdefault(contact.completion_tick, []).append(
                (index, read_duration, contact.value)
            )

    generator = _diffusion_generator(field, config)
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    activation = np.asarray(
        [neuron.activation for neuron in neurons],
        dtype=np.float64,
    )
    projected_activation = eigenvectors.T @ activation
    current_tick = step_time.start_tick
    for completion_tick, grouped in sorted(events.items()):
        elapsed = (completion_tick - current_tick) / ticks_per_second
        projected_activation = _advance_projected_activation(
            projected_activation,
            eigenvalues,
            elapsed,
        )
        projected_activation = _apply_projected_point_contacts(
            projected_activation,
            eigenvectors,
            grouped,
            config.response_time_seconds,
        )
        current_tick = completion_tick
    remaining = (step_time.end_tick - current_tick) / ticks_per_second
    projected_activation = _advance_projected_activation(
        projected_activation,
        eigenvalues,
        remaining,
    )
    activation = eigenvectors @ projected_activation
    if not np.all(np.isfinite(activation)):
        raise NeutralLocalFieldSubstrateError(
            "neutral local field integration produced a non-finite state"
        )
    if np.any(activation < -1.0 - 1e-12) or np.any(activation > 1.0 + 1e-12):
        raise NeutralLocalFieldSubstrateError(
            "neutral local field integration left the normalized field domain"
        )
    activation = np.clip(activation, -1.0, 1.0)

    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]),
            neuron.afterimage,
        )
        for index, neuron in enumerate(neurons)
    }

    def exact_transient_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    try:
        return field.advance(
            distribution,
            exact_transient_output,
            transient_neuron_inputs=transient_inputs,
        )
    except SharedMCMFieldError as exc:
        raise NeutralLocalFieldSubstrateError(str(exc)) from exc


def advance_neutral_fast_shared_field(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> SharedMCMField:
    """Advance activation and its local fast trace over one real interval."""

    if not isinstance(field, SharedMCMField):
        raise NeutralLocalFieldSubstrateError(
            "neutral fast field requires one shared MCM field"
        )
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise NeutralLocalFieldSubstrateError(
            "neutral fast field requires one substrate configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise NeutralLocalFieldSubstrateError(
            "neutral fast field requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise NeutralLocalFieldSubstrateError("neutral fast field dissipation config is invalid")
    leak_rate = 0.0 if dissipation_config is None else dissipation_config.leak_rate_per_second
    elapsed = _step_duration(distribution, step_time)
    generator, boundary = _generator_and_boundary(
        field,
        distribution,
        substrate_config,
    )
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    neurons = field.layer.neurons
    activation, afterimage = _integrate_activation_afterimage_with_spectrum(
        np.asarray([neuron.activation for neuron in neurons], dtype=np.float64),
        np.asarray([neuron.afterimage for neuron in neurons], dtype=np.float64),
        eigenvalues,
        eigenvectors,
        boundary,
        elapsed,
        afterimage_config.time_constant_seconds,
        leak_rate,
    )
    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]),
            float(afterimage[index]),
        )
        for index, neuron in enumerate(neurons)
    }

    def exact_fast_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    try:
        return field.advance(
            distribution,
            exact_fast_output,
            step_time=step_time,
        )
    except SharedMCMFieldError as exc:
        raise NeutralLocalFieldSubstrateError(str(exc)) from exc
def advance_neutral_fast_shared_field_transient(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    _state_observer: _FastStateObserver | None = None,
) -> SharedMCMField:
    """Advance asynchronous activation and fast trace on the same field."""

    if not isinstance(field, SharedMCMField):
        raise NeutralLocalFieldSubstrateError(
            "transient fast field requires one shared MCM field"
        )
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise NeutralLocalFieldSubstrateError(
            "transient fast field requires one substrate configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise NeutralLocalFieldSubstrateError(
            "transient fast field requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise NeutralLocalFieldSubstrateError("transient fast field dissipation config is invalid")
    if _state_observer is not None and not callable(_state_observer):
        raise NeutralLocalFieldSubstrateError(
            "transient fast field state observer must be callable"
        )
    leak_rate = 0.0 if dissipation_config is None else dissipation_config.leak_rate_per_second
    if not isinstance(transient_inputs, TransientNeuronInputSet):
        raise NeutralLocalFieldSubstrateError(
            "transient fast field requires one complete local input set"
        )
    if distribution.contacts:
        raise NeutralLocalFieldSubstrateError(
            "transient fast field requires a contact-free boundary distribution"
        )
    step_time = transient_inputs.step_time
    _step_duration(distribution, step_time)
    expected_ids = set(field.layer.docked_neuron_ids)
    actual_ids = {item.neuron_id for item in transient_inputs.neuron_inputs}
    if actual_ids != expected_ids:
        raise NeutralLocalFieldSubstrateError(
            "transient fast inputs must cover every receptor dock neuron"
        )

    neurons = field.layer.neurons
    neuron_index = {
        neuron.neuron_id: index for index, neuron in enumerate(neurons)
    }
    events: dict[int, list[tuple[int, float, float]]] = {}
    ticks_per_second = step_time.ticks_per_second
    for neuron_input in transient_inputs.neuron_inputs:
        index = neuron_index[neuron_input.neuron_id]
        for contact in neuron_input.contacts:
            read_duration = (
                contact.organism_read_time.window_end_tick
                - contact.organism_read_time.window_start_tick
            ) / ticks_per_second
            events.setdefault(contact.completion_tick, []).append(
                (index, read_duration, contact.value)
            )

    generator = _diffusion_generator(field, substrate_config)
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    activation = np.asarray(
        [neuron.activation for neuron in neurons],
        dtype=np.float64,
    )
    afterimage = np.asarray(
        [neuron.afterimage for neuron in neurons],
        dtype=np.float64,
    )
    projected_activation = eigenvectors.T @ activation
    projected_afterimage = eigenvectors.T @ afterimage
    current_tick = step_time.start_tick
    for completion_tick, grouped in sorted(events.items()):
        elapsed = (completion_tick - current_tick) / ticks_per_second
        projected_activation, projected_afterimage = (
            _advance_projected_activation_afterimage(
                projected_activation,
                projected_afterimage,
                eigenvalues,
                elapsed,
                afterimage_config.time_constant_seconds,
                leak_rate,
            )
        )
        projected_activation = _apply_projected_point_contacts(
            projected_activation,
            eigenvectors,
            grouped,
            substrate_config.response_time_seconds,
            leak_rate,
        )
        if _state_observer is not None:
            _state_observer(
                completion_tick,
                np.array(eigenvectors @ projected_activation, copy=True),
                np.array(eigenvectors @ projected_afterimage, copy=True),
            )
        current_tick = completion_tick
    remaining = (step_time.end_tick - current_tick) / ticks_per_second
    projected_activation, projected_afterimage = (
        _advance_projected_activation_afterimage(
            projected_activation,
            projected_afterimage,
            eigenvalues,
            remaining,
            afterimage_config.time_constant_seconds,
            leak_rate,
        )
    )
    if _state_observer is not None and current_tick != step_time.end_tick:
        _state_observer(
            step_time.end_tick,
            np.array(eigenvectors @ projected_activation, copy=True),
            np.array(eigenvectors @ projected_afterimage, copy=True),
        )
    activation = eigenvectors @ projected_activation
    afterimage = eigenvectors @ projected_afterimage
    if not np.all(np.isfinite(activation)) or not np.all(np.isfinite(afterimage)):
        raise NeutralLocalFieldSubstrateError(
            "neutral fast field integration produced a non-finite state"
        )
    if (
        np.any(activation < -1.0 - 1e-12)
        or np.any(activation > 1.0 + 1e-12)
        or np.any(afterimage < -1.0 - 1e-12)
        or np.any(afterimage > 1.0 + 1e-12)
    ):
        raise NeutralLocalFieldSubstrateError(
            "neutral fast field integration left the normalized field domain"
        )
    activation = np.clip(activation, -1.0, 1.0)
    afterimage = np.clip(afterimage, -1.0, 1.0)

    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]),
            float(afterimage[index]),
        )
        for index, neuron in enumerate(neurons)
    }

    def exact_transient_fast_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    try:
        return field.advance(
            distribution,
            exact_transient_fast_output,
            transient_neuron_inputs=transient_inputs,
        )
    except SharedMCMFieldError as exc:
        raise NeutralLocalFieldSubstrateError(str(exc)) from exc


def neutral_local_field_substrate_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for config in (
            NeutralLocalFieldSubstrateConfig,
            NeutralFastAfterimageConfig,
        )
        for item in fields(config)
    )
