"""Private frozen E1 and fixed-adapter probes for transient field input."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
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


class FrozenTransientE1ProbeError(ValueError):
    """Raised when a frozen transient probe is incomplete or inconsistent."""


@dataclass(frozen=True, slots=True)
class FrozenTransientE1ProbeResult:
    """One transient field result with the exact unchanged E1 state."""

    field: SharedMCMField
    e1_state: E1LocalEdgePlasticityState
    applied_adapter: E1WeightedFieldAdapterResult

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise FrozenTransientE1ProbeError("result requires one shared field")
        if not isinstance(self.e1_state, E1LocalEdgePlasticityState):
            raise FrozenTransientE1ProbeError("result requires one E1 state")
        if not isinstance(self.applied_adapter, E1WeightedFieldAdapterResult):
            raise FrozenTransientE1ProbeError("result requires one adapter")
        try:
            validate_e1_state_for_layer(self.field.layer, self.e1_state)
        except E1LocalEdgePlasticityError as exc:
            raise FrozenTransientE1ProbeError(str(exc)) from exc
        if (
            self.applied_adapter.edge_inventory_digest
            != self.e1_state.edge_inventory_digest
        ):
            raise FrozenTransientE1ProbeError(
                "field, frozen state, and adapter geometry must match"
            )


def _validate_common_inputs(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
) -> None:
    if not isinstance(field, SharedMCMField):
        raise FrozenTransientE1ProbeError("probe requires one shared field")
    if not isinstance(transient_inputs, TransientNeuronInputSet):
        raise FrozenTransientE1ProbeError(
            "probe requires one complete transient input set"
        )
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise FrozenTransientE1ProbeError(
            "probe requires one substrate configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise FrozenTransientE1ProbeError(
            "probe requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise FrozenTransientE1ProbeError(
            "probe dissipation configuration is invalid"
        )
    if distribution.contacts:
        raise FrozenTransientE1ProbeError(
            "transient probe requires a contact-free boundary distribution"
        )
    try:
        _step_duration(distribution, transient_inputs.step_time)
    except NeutralLocalFieldSubstrateError as exc:
        raise FrozenTransientE1ProbeError(str(exc)) from exc
    expected_ids = set(field.layer.docked_neuron_ids)
    actual_ids = {item.neuron_id for item in transient_inputs.neuron_inputs}
    if actual_ids != expected_ids:
        raise FrozenTransientE1ProbeError(
            "transient probe inputs must cover every receptor dock neuron"
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
            raise FrozenTransientE1ProbeError(
                "transient probe input contains an unknown field neuron"
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


def _advance_with_fixed_adapter(
    field: SharedMCMField,
    fixed_adapter: E1WeightedFieldAdapterResult,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
) -> SharedMCMField:
    _validate_common_inputs(
        field,
        distribution,
        transient_inputs,
        substrate_config,
        afterimage_config,
        dissipation_config,
    )
    if not isinstance(fixed_adapter, E1WeightedFieldAdapterResult):
        raise FrozenTransientE1ProbeError("probe requires one fixed adapter")
    expected_base_rate = 1.0 / substrate_config.response_time_seconds
    if fixed_adapter.base_rate_per_second != expected_base_rate:
        raise FrozenTransientE1ProbeError(
            "fixed adapter base rate must match the probe field configuration"
        )
    try:
        generator = build_e1_weighted_diffusion_generator(
            field.layer, fixed_adapter
        )
    except E1WeightedFieldAdapterError as exc:
        raise FrozenTransientE1ProbeError(str(exc)) from exc
    if all(
        item.rate_per_second == fixed_adapter.base_rate_per_second
        for item in fixed_adapter.edge_rates
    ):
        try:
            return advance_neutral_fast_shared_field_transient(
                field,
                distribution,
                transient_inputs,
                substrate_config,
                afterimage_config,
                dissipation_config,
            )
        except NeutralLocalFieldSubstrateError as exc:
            raise FrozenTransientE1ProbeError(str(exc)) from exc

    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    activation = np.asarray(
        [neuron.activation for neuron in field.layer.neurons], dtype=np.float64
    )
    afterimage = np.asarray(
        [neuron.afterimage for neuron in field.layer.neurons], dtype=np.float64
    )
    projected_activation = eigenvectors.T @ activation
    projected_afterimage = eigenvectors.T @ afterimage
    events = _event_groups(field, transient_inputs)
    step_time = transient_inputs.step_time
    rate = step_time.ticks_per_second
    leak_rate = (
        0.0
        if dissipation_config is None
        else dissipation_config.leak_rate_per_second
    )
    current_tick = step_time.start_tick
    for completion_tick, grouped in sorted(events.items()):
        elapsed = (completion_tick - current_tick) / rate
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
        current_tick = completion_tick
    remaining = (step_time.end_tick - current_tick) / rate
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
    activation = eigenvectors @ projected_activation
    afterimage = eigenvectors @ projected_afterimage
    if not np.all(np.isfinite(activation)) or not np.all(np.isfinite(afterimage)):
        raise FrozenTransientE1ProbeError(
            "frozen transient integration produced a non-finite state"
        )
    if (
        np.any(np.abs(activation) > 1.0 + 1e-12)
        or np.any(np.abs(afterimage) > 1.0 + 1e-12)
    ):
        raise FrozenTransientE1ProbeError(
            "frozen transient integration left the normalized field domain"
        )
    activation = np.clip(activation, -1.0, 1.0)
    afterimage = np.clip(afterimage, -1.0, 1.0)
    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]), float(afterimage[index])
        )
        for index, neuron in enumerate(field.layer.neurons)
    }

    def exact_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    try:
        return field.advance(
            distribution,
            exact_output,
            transient_neuron_inputs=transient_inputs,
        )
    except SharedMCMFieldError as exc:
        raise FrozenTransientE1ProbeError(str(exc)) from exc


def advance_frozen_e1_fast_shared_field_transient(
    field: SharedMCMField,
    frozen_e1_state: E1LocalEdgePlasticityState,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    backreaction_enabled: bool,
) -> FrozenTransientE1ProbeResult:
    """Advance transient S/H while keeping the E1 state exactly frozen."""

    if not isinstance(backreaction_enabled, bool):
        raise FrozenTransientE1ProbeError("backreaction_enabled must be boolean")
    try:
        validate_e1_state_for_layer(field.layer, frozen_e1_state)
        adapter = compute_e1_weighted_edge_rates(
            field.layer,
            frozen_e1_state,
            substrate_config,
            backreaction_enabled=backreaction_enabled,
        )
    except (E1LocalEdgePlasticityError, E1WeightedFieldAdapterError) as exc:
        raise FrozenTransientE1ProbeError(str(exc)) from exc
    next_field = _advance_with_fixed_adapter(
        field,
        adapter,
        distribution,
        transient_inputs,
        substrate_config,
        afterimage_config,
        dissipation_config,
    )
    return FrozenTransientE1ProbeResult(
        next_field, frozen_e1_state, adapter
    )


def advance_fixed_e1_adapter_fast_shared_field_transient(
    field: SharedMCMField,
    fixed_adapter: E1WeightedFieldAdapterResult,
    distribution: ReceptorDistribution,
    transient_inputs: TransientNeuronInputSet,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> SharedMCMField:
    """Advance transient S/H with a fixed adapter and no E1 state role."""

    return _advance_with_fixed_adapter(
        field,
        fixed_adapter,
        distribution,
        transient_inputs,
        substrate_config,
        afterimage_config,
        dissipation_config,
    )
