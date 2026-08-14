"""Synchronous opt-in coupling of E1 and the exact fast S/H field."""

from __future__ import annotations

from dataclasses import dataclass

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
from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import MCMNeuronDrive, MCMNeuronOutput
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    _generator_and_boundary,
    _integrate_activation_afterimage_with_spectrum,
    _step_duration,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import (
    SharedMCMField,
    SharedMCMFieldError,
    _mapped_receptor_contacts,
)


class E1CoupledFastFieldError(ValueError):
    """Raised when one atomic E1/S/H step cannot be completed."""


@dataclass(frozen=True, slots=True)
class E1CoupledFastFieldStepResult:
    """One completed field, E1 end state, and applied midpoint adapter."""

    field: SharedMCMField
    e1_state: E1LocalEdgePlasticityState
    applied_adapter: E1WeightedFieldAdapterResult

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise E1CoupledFastFieldError("coupled result requires one field")
        if not isinstance(self.e1_state, E1LocalEdgePlasticityState):
            raise E1CoupledFastFieldError("coupled result requires one E1 state")
        if not isinstance(self.applied_adapter, E1WeightedFieldAdapterResult):
            raise E1CoupledFastFieldError(
                "coupled result requires the applied E1 adapter"
            )
        try:
            validate_e1_state_for_layer(self.field.layer, self.e1_state)
        except E1LocalEdgePlasticityError as exc:
            raise E1CoupledFastFieldError(str(exc)) from exc
        if (
            self.applied_adapter.edge_inventory_digest
            != self.e1_state.edge_inventory_digest
        ):
            raise E1CoupledFastFieldError(
                "coupled result field and E1 geometry must remain identical"
            )


def _active_generator_and_boundary(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    adapter: E1WeightedFieldAdapterResult,
) -> tuple[np.ndarray, np.ndarray]:
    generator = build_e1_weighted_diffusion_generator(field.layer, adapter)
    boundary = np.zeros(len(field.layer.neurons), dtype=np.float64)
    try:
        contacts = _mapped_receptor_contacts(field.docks, distribution)
    except SharedMCMFieldError as exc:
        raise E1CoupledFastFieldError(str(exc)) from exc
    index = {
        neuron.neuron_id: offset for offset, neuron in enumerate(field.layer.neurons)
    }
    rate = 1.0 / substrate_config.response_time_seconds
    for neuron_id, contact in contacts.items():
        offset = index[neuron_id]
        generator[offset, offset] -= rate
        boundary[offset] += rate * contact
    return generator, boundary


def advance_e1_coupled_fast_shared_field(
    field: SharedMCMField,
    e1_state: E1LocalEdgePlasticityState,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    backreaction_enabled: bool,
) -> E1CoupledFastFieldStepResult:
    """Advance one symmetric half-E1/full-SH/half-E1 interval."""

    if not isinstance(field, SharedMCMField):
        raise E1CoupledFastFieldError("coupled E1 step requires one shared field")
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise E1CoupledFastFieldError(
            "coupled E1 step requires one substrate configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise E1CoupledFastFieldError(
            "coupled E1 step requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise E1CoupledFastFieldError(
            "coupled E1 step dissipation configuration is invalid"
        )
    if not isinstance(backreaction_enabled, bool):
        raise E1CoupledFastFieldError("backreaction_enabled must be boolean")
    try:
        elapsed = _step_duration(distribution, step_time)
        validate_e1_state_for_layer(field.layer, e1_state)
        midpoint_state = advance_e1_local_edge_plasticity(
            field.layer, e1_state, elapsed / 2.0
        )
        adapter = compute_e1_weighted_edge_rates(
            field.layer,
            midpoint_state,
            substrate_config,
            backreaction_enabled=backreaction_enabled,
        )
    except (
        E1LocalEdgePlasticityError,
        E1WeightedFieldAdapterError,
        NeutralLocalFieldSubstrateError,
    ) as exc:
        raise E1CoupledFastFieldError(str(exc)) from exc

    all_base_rate = all(
        item.rate_per_second == adapter.base_rate_per_second
        for item in adapter.edge_rates
    )
    try:
        if all_base_rate:
            generator, boundary = _generator_and_boundary(
                field, distribution, substrate_config
            )
        else:
            generator, boundary = _active_generator_and_boundary(
                field, distribution, substrate_config, adapter
            )
    except (E1WeightedFieldAdapterError, NeutralLocalFieldSubstrateError) as exc:
        raise E1CoupledFastFieldError(str(exc)) from exc

    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    neurons = field.layer.neurons
    leak_rate = (
        0.0
        if dissipation_config is None
        else dissipation_config.leak_rate_per_second
    )
    try:
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
    except NeutralLocalFieldSubstrateError as exc:
        raise E1CoupledFastFieldError(str(exc)) from exc
    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]),
            float(afterimage[index]),
        )
        for index, neuron in enumerate(neurons)
    }

    def exact_coupled_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    try:
        next_field = field.advance(
            distribution,
            exact_coupled_output,
            step_time=step_time,
        )
        next_e1_state = advance_e1_local_edge_plasticity(
            next_field.layer, midpoint_state, elapsed / 2.0
        )
    except (SharedMCMFieldError, E1LocalEdgePlasticityError) as exc:
        raise E1CoupledFastFieldError(str(exc)) from exc
    return E1CoupledFastFieldStepResult(next_field, next_e1_state, adapter)
