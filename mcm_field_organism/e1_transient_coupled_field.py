"""Private transient coupling of E1 to asynchronous fast S/H field input."""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    advance_e1_local_edge_plasticity,
    validate_e1_state_for_layer,
)
from .e1_weighted_field_adapter import (
    E1WeightedFieldAdapterError,
    E1WeightedFieldAdapterResult,
    build_e1_weighted_diffusion_generator,
    compute_e1_weighted_edge_rates,
)
from .mcm_neuron_layer import MCMNeuronDrive, MCMNeuronOutput
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    _advance_projected_activation_afterimage,
    _apply_projected_point_contacts,
    _step_duration,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError
from .transient_neuron_input import TransientNeuronInputSet


class E1TransientCoupledFieldError(ValueError):
    """Raised when one transient E1/S/H step is not causally well-defined."""


@dataclass(frozen=True, slots=True)
class E1TransientCoupledFieldStepResult:
    """One completed transient field step and its interval adapters."""

    field: SharedMCMField
    e1_state: E1LocalEdgePlasticityState
    applied_adapters: tuple[E1WeightedFieldAdapterResult, ...]
    interval_end_ticks: tuple[int, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise E1TransientCoupledFieldError("result requires one shared field")
        if not isinstance(self.e1_state, E1LocalEdgePlasticityState):
            raise E1TransientCoupledFieldError("result requires one E1 state")
        adapters = tuple(self.applied_adapters)
        ticks = tuple(self.interval_end_ticks)
        if (
            not adapters
            or any(not isinstance(item, E1WeightedFieldAdapterResult) for item in adapters)
            or len(adapters) != len(ticks)
            or list(ticks) != sorted(set(ticks))
        ):
            raise E1TransientCoupledFieldError(
                "result requires one ordered adapter per positive interval"
            )
        try:
            validate_e1_state_for_layer(self.field.layer, self.e1_state)
        except E1LocalEdgePlasticityError as exc:
            raise E1TransientCoupledFieldError(str(exc)) from exc
        digest = self.e1_state.edge_inventory_digest
        if any(item.edge_inventory_digest != digest for item in adapters):
            raise E1TransientCoupledFieldError(
                "every transient adapter must match the E1 field geometry"
            )
        object.__setattr__(self, "applied_adapters", adapters)
        object.__setattr__(self, "interval_end_ticks", ticks)


def _layer_with_fast_state(
    field: SharedMCMField,
    activation: np.ndarray,
    afterimage: np.ndarray,
):
    neurons = field.layer.neurons
    if activation.shape != (len(neurons),) or afterimage.shape != (len(neurons),):
        raise E1TransientCoupledFieldError("fast state shape must match the field")
    return replace(
        field.layer,
        neurons=tuple(
            replace(
                neuron,
                activation=float(activation[index]),
                afterimage=float(afterimage[index]),
            )
            for index, neuron in enumerate(neurons)
        ),
    )


def _event_groups(
    field: SharedMCMField,
    transient_inputs: TransientNeuronInputSet,
) -> dict[int, list[tuple[int, float, float]]]:
    index = {
        neuron.neuron_id: offset
        for offset, neuron in enumerate(field.layer.neurons)
    }
    rate = transient_inputs.step_time.ticks_per_second
    events: dict[int, list[tuple[int, float, float]]] = {}
    for neuron_input in transient_inputs.neuron_inputs:
        offset = index.get(neuron_input.neuron_id)
        if offset is None:
            raise E1TransientCoupledFieldError(
                "transient E1 input contains an unknown field neuron"
            )
        for contact in neuron_input.contacts:
            duration = (
                contact.organism_read_time.window_end_tick
                - contact.organism_read_time.window_start_tick
            ) / rate
            events.setdefault(contact.completion_tick, []).append(
                (offset, duration, contact.value)
            )
    return events


def _interval_ends(
    transient_inputs: TransientNeuronInputSet,
    events: dict[int, list[tuple[int, float, float]]],
) -> tuple[int, ...]:
    end_tick = transient_inputs.step_time.end_tick
    return tuple(sorted(set(events) | {end_tick}))


def _advance_e1_over_observed_boundaries(
    field: SharedMCMField,
    state: E1LocalEdgePlasticityState,
    observed: tuple[tuple[int, np.ndarray, np.ndarray, float], ...],
    substrate_config: NeutralLocalFieldSubstrateConfig,
    *,
    backreaction_enabled: bool,
) -> tuple[
    E1LocalEdgePlasticityState,
    tuple[E1WeightedFieldAdapterResult, ...],
]:
    current_tick = observed[0][0]
    activation = observed[0][1]
    afterimage = observed[0][2]
    current_state = state
    adapters = []
    for end_tick, end_activation, end_afterimage, _ in observed[1:]:
        elapsed = (end_tick - current_tick) / observed[0][3]
        start_layer = _layer_with_fast_state(field, activation, afterimage)
        midpoint = advance_e1_local_edge_plasticity(
            start_layer, current_state, elapsed / 2.0
        )
        adapters.append(
            compute_e1_weighted_edge_rates(
                start_layer,
                midpoint,
                substrate_config,
                backreaction_enabled=backreaction_enabled,
            )
        )
        end_layer = _layer_with_fast_state(field, end_activation, end_afterimage)
        current_state = advance_e1_local_edge_plasticity(
            end_layer, midpoint, elapsed / 2.0
        )
        current_tick = end_tick
        activation = end_activation
        afterimage = end_afterimage
    return current_state, tuple(adapters)


def advance_e1_coupled_fast_shared_field_transient(
    field: SharedMCMField,
    e1_state: E1LocalEdgePlasticityState,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    backreaction_enabled: bool,
) -> E1TransientCoupledFieldStepResult:
    """Advance E1 and transient S/H on the same ordered completion timeline."""

    if not isinstance(field, SharedMCMField):
        raise E1TransientCoupledFieldError("transient E1 step requires one field")
    if not isinstance(transient_inputs, TransientNeuronInputSet):
        raise E1TransientCoupledFieldError(
            "transient E1 step requires one complete local input set"
        )
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise E1TransientCoupledFieldError(
            "transient E1 step requires one substrate configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise E1TransientCoupledFieldError(
            "transient E1 step requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise E1TransientCoupledFieldError(
            "transient E1 step dissipation configuration is invalid"
        )
    if not isinstance(backreaction_enabled, bool):
        raise E1TransientCoupledFieldError("backreaction_enabled must be boolean")
    if distribution.contacts:
        raise E1TransientCoupledFieldError(
            "transient E1 step requires a contact-free boundary distribution"
        )
    try:
        _step_duration(distribution, transient_inputs.step_time)
        validate_e1_state_for_layer(field.layer, e1_state)
    except (NeutralLocalFieldSubstrateError, E1LocalEdgePlasticityError) as exc:
        raise E1TransientCoupledFieldError(str(exc)) from exc

    expected_ids = set(field.layer.docked_neuron_ids)
    actual_ids = {item.neuron_id for item in transient_inputs.neuron_inputs}
    if actual_ids != expected_ids:
        raise E1TransientCoupledFieldError(
            "transient E1 inputs must cover every receptor dock neuron"
        )

    events = _event_groups(field, transient_inputs)
    interval_ends = _interval_ends(transient_inputs, events)
    start_tick = transient_inputs.step_time.start_tick
    rate = transient_inputs.step_time.ticks_per_second
    initial_activation = np.asarray(
        [neuron.activation for neuron in field.layer.neurons], dtype=np.float64
    )
    initial_afterimage = np.asarray(
        [neuron.afterimage for neuron in field.layer.neurons], dtype=np.float64
    )

    neutral_field_path = (
        not backreaction_enabled
        or e1_state.contract.backreaction_gain == 0.0
    )
    if neutral_field_path:
        observations: list[tuple[int, np.ndarray, np.ndarray]] = [
            (start_tick, initial_activation, initial_afterimage)
        ]

        def observe(tick: int, activation: np.ndarray, afterimage: np.ndarray) -> None:
            observations.append((tick, activation, afterimage))

        try:
            next_field = advance_neutral_fast_shared_field_transient(
                field,
                distribution,
                transient_inputs,
                substrate_config,
                afterimage_config,
                dissipation_config,
                _state_observer=observe,
            )
            expanded = tuple(
                (tick, activation, afterimage, rate)
                for tick, activation, afterimage in observations
            )
            next_state, adapters = _advance_e1_over_observed_boundaries(
                field,
                e1_state,
                expanded,
                substrate_config,
                backreaction_enabled=backreaction_enabled,
            )
        except (
            ValueError,
            E1LocalEdgePlasticityError,
            E1WeightedFieldAdapterError,
        ) as exc:
            raise E1TransientCoupledFieldError(str(exc)) from exc
        return E1TransientCoupledFieldStepResult(
            next_field,
            next_state,
            adapters,
            tuple(item[0] for item in observations[1:]),
        )

    activation = initial_activation
    afterimage = initial_afterimage
    current_state = e1_state
    current_tick = start_tick
    adapters = []
    leak_rate = (
        0.0
        if dissipation_config is None
        else dissipation_config.leak_rate_per_second
    )
    try:
        for end_tick in interval_ends:
            elapsed = (end_tick - current_tick) / rate
            start_layer = _layer_with_fast_state(field, activation, afterimage)
            midpoint = advance_e1_local_edge_plasticity(
                start_layer, current_state, elapsed / 2.0
            )
            adapter = compute_e1_weighted_edge_rates(
                start_layer,
                midpoint,
                substrate_config,
                backreaction_enabled=True,
            )
            generator = build_e1_weighted_diffusion_generator(start_layer, adapter)
            eigenvalues, eigenvectors = np.linalg.eigh(generator)
            projected_activation = eigenvectors.T @ activation
            projected_afterimage = eigenvectors.T @ afterimage
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
            grouped = events.get(end_tick)
            if grouped:
                projected_activation = _apply_projected_point_contacts(
                    projected_activation,
                    eigenvectors,
                    grouped,
                    substrate_config.response_time_seconds,
                    leak_rate,
                )
            activation = eigenvectors @ projected_activation
            afterimage = eigenvectors @ projected_afterimage
            if not np.all(np.isfinite(activation)) or not np.all(
                np.isfinite(afterimage)
            ):
                raise E1TransientCoupledFieldError(
                    "transient E1 integration produced a non-finite state"
                )
            if (
                np.any(np.abs(activation) > 1.0 + 1e-12)
                or np.any(np.abs(afterimage) > 1.0 + 1e-12)
            ):
                raise E1TransientCoupledFieldError(
                    "transient E1 integration left the normalized field domain"
                )
            activation = np.clip(activation, -1.0, 1.0)
            afterimage = np.clip(afterimage, -1.0, 1.0)
            end_layer = _layer_with_fast_state(field, activation, afterimage)
            current_state = advance_e1_local_edge_plasticity(
                end_layer, midpoint, elapsed / 2.0
            )
            adapters.append(adapter)
            current_tick = end_tick
    except (
        E1LocalEdgePlasticityError,
        E1WeightedFieldAdapterError,
        NeutralLocalFieldSubstrateError,
    ) as exc:
        raise E1TransientCoupledFieldError(str(exc)) from exc

    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]), float(afterimage[index])
        )
        for index, neuron in enumerate(field.layer.neurons)
    }

    def exact_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    try:
        next_field = field.advance(
            distribution,
            exact_output,
            transient_neuron_inputs=transient_inputs,
        )
    except SharedMCMFieldError as exc:
        raise E1TransientCoupledFieldError(str(exc)) from exc
    return E1TransientCoupledFieldStepResult(
        next_field,
        current_state,
        tuple(adapters),
        interval_ends,
    )
