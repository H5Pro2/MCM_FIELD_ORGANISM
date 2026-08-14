"""Private research intervention on the fast-field initial condition."""

from __future__ import annotations

from dataclasses import replace

import numpy as np

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
    advance_neutral_fast_shared_field,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError


def apply_previous_state_operator(
    field: SharedMCMField,
    *,
    previous_state_operator: str | None = None,
) -> SharedMCMField:
    """Apply the private intervention before an unchanged runtime step."""

    if previous_state_operator not in {None, "identity", "zero"}:
        raise NeutralLocalFieldSubstrateError(
            "previous_state_operator must be None, identity, or zero"
        )
    if not isinstance(field, SharedMCMField):
        raise NeutralLocalFieldSubstrateError(
            "previous-state intervention requires one shared MCM field"
        )
    if previous_state_operator in {None, "identity"}:
        return field
    neurons = tuple(
        replace(neuron, activation=0.0, afterimage=0.0)
        for neuron in field.layer.neurons
    )
    return replace(field, layer=replace(field.layer, neurons=neurons))


def advance_with_previous_state_operator(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    previous_state_operator: str | None = None,
) -> SharedMCMField:
    """Advance one research comparison without exposing a production switch."""

    if previous_state_operator not in {None, "identity", "zero"}:
        raise NeutralLocalFieldSubstrateError(
            "previous_state_operator must be None, identity, or zero"
        )
    if previous_state_operator in {None, "identity"}:
        return advance_neutral_fast_shared_field(
            field,
            distribution,
            step_time,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
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
        raise NeutralLocalFieldSubstrateError(
            "neutral fast field dissipation config is invalid"
        )

    elapsed = _step_duration(distribution, step_time)
    generator, boundary = _generator_and_boundary(
        field, distribution, substrate_config
    )
    eigenvalues, eigenvectors = np.linalg.eigh(generator)
    neurons = field.layer.neurons
    zero = np.zeros(len(neurons), dtype=np.float64)
    leak_rate = (
        0.0
        if dissipation_config is None
        else dissipation_config.leak_rate_per_second
    )
    activation, afterimage = _integrate_activation_afterimage_with_spectrum(
        zero,
        zero,
        eigenvalues,
        eigenvectors,
        boundary,
        elapsed,
        afterimage_config.time_constant_seconds,
        leak_rate,
    )
    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]), float(afterimage[index])
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
