"""Exact opt-in S/H/L integration for the S1-B reference substrate."""

from __future__ import annotations

import math
from typing import Callable

import numpy as np

from .field_step_time import MCMFieldStepTime
from .mcm_local_development_state import (
    MCMLocalDevelopmentState,
    MCMLocalDevelopmentStateError,
    build_mcm_local_development,
)
from .mcm_neuron_layer import MCMNeuronDrive, MCMNeuronOutput
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    _diffusion_generator,
    _generator_and_boundary,
    _step_duration,
    advance_neutral_fast_shared_field,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import (
    SharedMCMField,
    SharedMCMFieldError,
    _mapped_receptor_contacts,
    _validated_transient_inputs,
)
from .transient_neuron_input import TransientNeuronInputSet


class S1BReciprocalAccommodationError(ValueError):
    """Raised when the S1-B reference path violates its bound contract."""


_StateObserver = Callable[[int, np.ndarray, np.ndarray, np.ndarray], None]
_BOUND_TOLERANCE = 1e-12
_EIGENVALUE_TOLERANCE = 1e-14


def _mode_integral(eigenvalues: np.ndarray, elapsed: float) -> np.ndarray:
    result = np.empty_like(eigenvalues)
    zero = np.isclose(
        eigenvalues,
        0.0,
        rtol=0.0,
        atol=_EIGENVALUE_TOLERANCE,
    )
    result[zero] = elapsed
    result[~zero] = np.expm1(eigenvalues[~zero] * elapsed) / eigenvalues[~zero]
    return result


def _afterimage_coefficients(
    eigenvalues: np.ndarray,
    elapsed: float,
    tracking_rate: float,
    total_afterimage_rate: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    fast_decay = math.exp(-total_afterimage_rate * elapsed)
    mode_exponent = np.exp(eigenvalues * elapsed)
    denominator = eigenvalues + total_afterimage_rate
    resonance = np.isclose(
        denominator,
        0.0,
        rtol=0.0,
        atol=_EIGENVALUE_TOLERANCE,
    )
    state_coeff = np.empty_like(eigenvalues)
    state_coeff[resonance] = tracking_rate * elapsed * fast_decay
    state_coeff[~resonance] = tracking_rate * (
        mode_exponent[~resonance] - fast_decay
    ) / denominator[~resonance]

    boundary_coeff = np.empty_like(eigenvalues)
    zero = np.isclose(
        eigenvalues,
        0.0,
        rtol=0.0,
        atol=_EIGENVALUE_TOLERANCE,
    )
    boundary_coeff[zero] = tracking_rate * (
        elapsed / total_afterimage_rate
        - (1.0 - fast_decay) / (total_afterimage_rate**2)
    )
    boundary_coeff[~zero] = (
        state_coeff[~zero]
        - (tracking_rate / total_afterimage_rate) * (1.0 - fast_decay)
    ) / eigenvalues[~zero]
    return state_coeff, boundary_coeff, fast_decay


def _bounded(values: np.ndarray, role: str) -> np.ndarray:
    if not np.all(np.isfinite(values)):
        raise S1BReciprocalAccommodationError(
            f"S1-B {role} produced a non-finite state"
        )
    if np.any(values < -1.0 - _BOUND_TOLERANCE) or np.any(
        values > 1.0 + _BOUND_TOLERANCE
    ):
        raise S1BReciprocalAccommodationError(
            f"S1-B {role} left the normalized field domain"
        )
    return np.clip(values, -1.0, 1.0)


def _validate_previous_time(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
) -> None:
    if field.last_distribution is None:
        return
    previous = field.last_distribution.field_time
    current = distribution.field_time
    if current.clock_id != previous.clock_id:
        raise S1BReciprocalAccommodationError("organism clock cannot change")
    if current.window_end_tick <= previous.window_end_tick:
        raise S1BReciprocalAccommodationError(
            "common field time must advance"
        )


def _without_development(field: SharedMCMField) -> SharedMCMField:
    return SharedMCMField(
        layer=field.layer,
        docks=field.docks,
        last_distribution=field.last_distribution,
    )


def advance_s1b_reciprocal_shared_field(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    field_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    observer: _StateObserver | None = None,
) -> SharedMCMField:
    """Advance one interval through the exact opt-in S1-B reference law."""

    if not isinstance(field, SharedMCMField):
        raise S1BReciprocalAccommodationError(
            "S1-B requires one shared MCM field"
        )
    if field.substrate is not None:
        raise S1BReciprocalAccommodationError(
            "the first S1-B corridor keeps M and L states separate"
        )
    development = field.development
    if not isinstance(development, MCMLocalDevelopmentState):
        raise S1BReciprocalAccommodationError(
            "S1-B requires one attached local development state"
        )
    if not isinstance(field_config, NeutralLocalFieldSubstrateConfig):
        raise S1BReciprocalAccommodationError(
            "S1-B requires one fast field configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise S1BReciprocalAccommodationError(
            "S1-B requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config,
        NeutralFieldDissipationConfig,
    ):
        raise S1BReciprocalAccommodationError(
            "S1-B dissipation configuration is invalid"
        )
    if observer is not None and not callable(observer):
        raise S1BReciprocalAccommodationError("S1-B observer must be callable")

    _validate_previous_time(field, distribution)
    elapsed = _step_duration(distribution, step_time)
    contract = development.contract
    coupling_rate = contract.coupling_rate_per_second
    if contract.is_null_arm:
        fast_next = advance_neutral_fast_shared_field(
            _without_development(field),
            distribution,
            step_time,
            field_config,
            afterimage_config,
            dissipation_config,
        )
        result = SharedMCMField(
            layer=fast_next.layer,
            docks=fast_next.docks,
            last_distribution=fast_next.last_distribution,
            development=development,
        )
        if observer is not None:
            activation = np.asarray(
                [item.activation for item in result.layer.neurons],
                dtype=np.float64,
            )
            afterimage = np.asarray(
                [item.afterimage for item in result.layer.neurons],
                dtype=np.float64,
            )
            local = np.asarray(result.development.dispositions, dtype=np.float64)
            observer(result.layer.tick, activation.copy(), afterimage.copy(), local.copy())
        return result

    generator, boundary = _generator_and_boundary(
        _without_development(field),
        distribution,
        field_config,
    )
    leak_rate = (
        0.0
        if dissipation_config is None
        else dissipation_config.leak_rate_per_second
    )
    count = len(field.layer.neurons)
    identity = np.eye(count, dtype=np.float64)
    capacity_ratio = contract.capacity_ratio
    root_capacity = math.sqrt(capacity_ratio)
    scaled_coupling = coupling_rate / root_capacity
    combined_generator = np.block(
        [
            [
                generator - (leak_rate + coupling_rate) * identity,
                scaled_coupling * identity,
            ],
            [
                scaled_coupling * identity,
                -(coupling_rate / capacity_ratio) * identity,
            ],
        ]
    )
    combined_boundary = np.concatenate(
        (boundary, np.zeros(count, dtype=np.float64))
    )
    eigenvalues, eigenvectors = np.linalg.eigh(combined_generator)

    previous_activation = np.asarray(
        [item.activation for item in field.layer.neurons],
        dtype=np.float64,
    )
    previous_afterimage = np.asarray(
        [item.afterimage for item in field.layer.neurons],
        dtype=np.float64,
    )
    previous_local = np.asarray(development.dispositions, dtype=np.float64)
    previous_combined = np.concatenate(
        (previous_activation, root_capacity * previous_local)
    )
    projected_state = eigenvectors.T @ previous_combined
    projected_boundary = eigenvectors.T @ combined_boundary
    exponent = np.exp(eigenvalues * elapsed)
    integrated_boundary = _mode_integral(eigenvalues, elapsed)
    projected_next = (
        exponent * projected_state
        + integrated_boundary * projected_boundary
    )
    combined_next = eigenvectors @ projected_next
    activation = _bounded(combined_next[:count], "activation")
    local = _bounded(combined_next[count:] / root_capacity, "development")

    tracking_rate = 1.0 / afterimage_config.time_constant_seconds
    afterimage_rate = tracking_rate + leak_rate
    state_coeff, boundary_coeff, fast_decay = _afterimage_coefficients(
        eigenvalues,
        elapsed,
        tracking_rate,
        afterimage_rate,
    )
    activation_projection = eigenvectors[:count, :]
    afterimage = (
        fast_decay * previous_afterimage
        + activation_projection
        @ (
            state_coeff * projected_state
            + boundary_coeff * projected_boundary
        )
    )
    afterimage = _bounded(afterimage, "afterimage")

    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]),
            float(afterimage[index]),
        )
        for index, neuron in enumerate(field.layer.neurons)
    }

    def exact_s1b_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    try:
        receptor_contacts = _mapped_receptor_contacts(field.docks, distribution)
        next_layer = field.layer.advance(
            receptor_contacts,
            exact_s1b_output,
            allow_missing_contacts=True,
            step_time=step_time,
        )
        next_development = build_mcm_local_development(
            next_layer,
            contract,
            (float(value) for value in local),
        )
    except (
        SharedMCMFieldError,
        MCMLocalDevelopmentStateError,
        ValueError,
    ) as exc:
        raise S1BReciprocalAccommodationError(str(exc)) from exc

    result = SharedMCMField(
        layer=next_layer,
        docks=field.docks,
        last_distribution=distribution,
        development=next_development,
    )
    if observer is not None:
        observer(
            result.layer.tick,
            activation.copy(),
            afterimage.copy(),
            local.copy(),
        )
    return result


def advance_s1b_reciprocal_shared_field_transient(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    field_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    observer: _StateObserver | None = None,
) -> SharedMCMField:
    """Advance one asynchronous batch with the exact S1-B free dynamics."""

    if not isinstance(field, SharedMCMField):
        raise S1BReciprocalAccommodationError(
            "transient S1-B requires one shared MCM field"
        )
    if field.substrate is not None:
        raise S1BReciprocalAccommodationError(
            "the first transient S1-B corridor keeps M and L states separate"
        )
    development = field.development
    if not isinstance(development, MCMLocalDevelopmentState):
        raise S1BReciprocalAccommodationError(
            "transient S1-B requires one attached local development state"
        )
    if not isinstance(distribution, ReceptorDistribution) or distribution.contacts:
        raise S1BReciprocalAccommodationError(
            "transient S1-B requires a contact-free boundary distribution"
        )
    if not isinstance(transient_inputs, TransientNeuronInputSet):
        raise S1BReciprocalAccommodationError(
            "transient S1-B requires one complete local input set"
        )
    if not isinstance(field_config, NeutralLocalFieldSubstrateConfig):
        raise S1BReciprocalAccommodationError(
            "transient S1-B requires one fast field configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise S1BReciprocalAccommodationError(
            "transient S1-B requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise S1BReciprocalAccommodationError(
            "transient S1-B dissipation configuration is invalid"
        )
    if observer is not None and not callable(observer):
        raise S1BReciprocalAccommodationError(
            "transient S1-B observer must be callable"
        )
    step_time = transient_inputs.step_time
    _validate_previous_time(field, distribution)
    _step_duration(distribution, step_time)
    try:
        local_inputs = _validated_transient_inputs(
            field.docks,
            distribution,
            transient_inputs,
        )
    except SharedMCMFieldError as exc:
        raise S1BReciprocalAccommodationError(str(exc)) from exc

    contract = development.contract
    if contract.is_null_arm:
        local = np.asarray(development.dispositions, dtype=np.float64)

        def fast_observer(
            tick: int,
            activation: np.ndarray,
            afterimage: np.ndarray,
        ) -> None:
            if observer is not None:
                observer(
                    tick,
                    activation.copy(),
                    afterimage.copy(),
                    local.copy(),
                )

        fast_next = advance_neutral_fast_shared_field_transient(
            _without_development(field),
            distribution,
            transient_inputs,
            field_config,
            afterimage_config,
            dissipation_config,
            _state_observer=fast_observer if observer is not None else None,
        )
        return SharedMCMField(
            layer=fast_next.layer,
            docks=fast_next.docks,
            last_distribution=fast_next.last_distribution,
            development=development,
        )

    neurons = field.layer.neurons
    count = len(neurons)
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

    leak_rate = (
        0.0
        if dissipation_config is None
        else dissipation_config.leak_rate_per_second
    )
    coupling_rate = contract.coupling_rate_per_second
    capacity_ratio = contract.capacity_ratio
    root_capacity = math.sqrt(capacity_ratio)
    identity = np.eye(count, dtype=np.float64)
    generator = _diffusion_generator(_without_development(field), field_config)
    scaled_coupling = coupling_rate / root_capacity
    combined_generator = np.block(
        [
            [
                generator - (leak_rate + coupling_rate) * identity,
                scaled_coupling * identity,
            ],
            [
                scaled_coupling * identity,
                -(coupling_rate / capacity_ratio) * identity,
            ],
        ]
    )
    eigenvalues, eigenvectors = np.linalg.eigh(combined_generator)
    tracking_rate = 1.0 / afterimage_config.time_constant_seconds
    afterimage_rate = tracking_rate + leak_rate
    activation_projection = eigenvectors[:count, :]
    activation = np.asarray(
        [item.activation for item in neurons], dtype=np.float64
    )
    afterimage = np.asarray(
        [item.afterimage for item in neurons], dtype=np.float64
    )
    local = np.asarray(development.dispositions, dtype=np.float64)

    def advance_free(elapsed: float) -> None:
        nonlocal activation, afterimage, local
        if elapsed == 0.0:
            return
        combined = np.concatenate((activation, root_capacity * local))
        projected = eigenvectors.T @ combined
        state_coeff, _, fast_decay = _afterimage_coefficients(
            eigenvalues,
            elapsed,
            tracking_rate,
            afterimage_rate,
        )
        afterimage = _bounded(
            fast_decay * afterimage
            + activation_projection @ (state_coeff * projected),
            "transient afterimage",
        )
        combined = eigenvectors @ (np.exp(eigenvalues * elapsed) * projected)
        activation = _bounded(combined[:count], "transient activation")
        local = _bounded(
            combined[count:] / root_capacity,
            "transient development",
        )

    current_tick = step_time.start_tick
    for completion_tick, grouped in sorted(events.items()):
        advance_free((completion_tick - current_tick) / ticks_per_second)
        before = np.array(activation, copy=True)
        next_values: dict[int, float] = {}
        for index, read_duration, value in grouped:
            response_rate = 1.0 / field_config.response_time_seconds
            total_rate = response_rate + leak_rate
            retention = math.exp(-total_rate * read_duration)
            equilibrium = response_rate * value / total_rate
            next_values[index] = (
                retention * before[index] + (1.0 - retention) * equilibrium
            )
        for index, value in next_values.items():
            activation[index] = value
        activation = _bounded(activation, "transient receptor activation")
        if observer is not None:
            observer(
                completion_tick,
                activation.copy(),
                afterimage.copy(),
                local.copy(),
            )
        current_tick = completion_tick
    advance_free((step_time.end_tick - current_tick) / ticks_per_second)
    if observer is not None and current_tick != step_time.end_tick:
        observer(
            step_time.end_tick,
            activation.copy(),
            afterimage.copy(),
            local.copy(),
        )

    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]),
            float(afterimage[index]),
        )
        for index, neuron in enumerate(neurons)
    }

    def exact_transient_s1b_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    try:
        next_layer = field.layer.advance(
            {},
            exact_transient_s1b_output,
            allow_missing_contacts=True,
            step_time=step_time,
            transient_receptor_inputs=local_inputs,
        )
        next_development = build_mcm_local_development(
            next_layer,
            contract,
            (float(value) for value in local),
        )
    except (
        MCMLocalDevelopmentStateError,
        SharedMCMFieldError,
        ValueError,
    ) as exc:
        raise S1BReciprocalAccommodationError(str(exc)) from exc
    return SharedMCMField(
        layer=next_layer,
        docks=field.docks,
        last_distribution=distribution,
        development=next_development,
    )


def replace_mcm_local_development(
    field: SharedMCMField,
    development: MCMLocalDevelopmentState,
) -> SharedMCMField:
    """External test intervention replacing only the complete L state."""

    if not isinstance(field, SharedMCMField):
        raise S1BReciprocalAccommodationError(
            "development replacement requires one shared field"
        )
    if not isinstance(development, MCMLocalDevelopmentState):
        raise S1BReciprocalAccommodationError(
            "development replacement requires one complete L state"
        )
    if field.development is None:
        raise S1BReciprocalAccommodationError(
            "development replacement requires an existing L corridor"
        )
    if field.development.contract != development.contract:
        raise S1BReciprocalAccommodationError(
            "development replacement cannot change the nature contract"
        )
    try:
        return SharedMCMField(
            layer=field.layer,
            docks=field.docks,
            last_distribution=field.last_distribution,
            development=development,
        )
    except SharedMCMFieldError as exc:
        raise S1BReciprocalAccommodationError(str(exc)) from exc


def neutralize_mcm_local_development(field: SharedMCMField) -> SharedMCMField:
    """External test intervention setting L to its exact neutral state."""

    if field.development is None:
        raise S1BReciprocalAccommodationError(
            "development neutralization requires an existing L corridor"
        )
    try:
        neutral = build_mcm_local_development(
            field.layer,
            field.development.contract,
            (0.0 for _ in field.layer.neurons),
        )
    except MCMLocalDevelopmentStateError as exc:
        raise S1BReciprocalAccommodationError(str(exc)) from exc
    return replace_mcm_local_development(field, neutral)


def swap_mcm_local_development(
    first: SharedMCMField,
    second: SharedMCMField,
) -> tuple[SharedMCMField, SharedMCMField]:
    """External test intervention swapping only compatible complete L states."""

    if first.development is None or second.development is None:
        raise S1BReciprocalAccommodationError(
            "development swap requires two complete L corridors"
        )
    if first.geometry_id != second.geometry_id:
        raise S1BReciprocalAccommodationError(
            "development swap requires identical field geometry"
        )
    return (
        replace_mcm_local_development(first, second.development),
        replace_mcm_local_development(second, first.development),
    )
