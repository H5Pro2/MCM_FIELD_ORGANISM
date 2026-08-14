"""Frozen E1 intervention for one identical synchronous S/H probe."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .e1_coupled_fast_field import (
    E1CoupledFastFieldError,
    _active_generator_and_boundary,
)
from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    validate_e1_state_for_layer,
)
from .e1_weighted_field_adapter import (
    E1WeightedFieldAdapterError,
    E1WeightedFieldAdapterResult,
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
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError


class FrozenE1ProbeError(ValueError):
    """Raised when a frozen E1 or fixed-adapter probe is invalid."""


@dataclass(frozen=True, slots=True)
class FrozenE1ProbeResult:
    """One completed field with the identical frozen E1 state and adapter."""

    field: SharedMCMField
    e1_state: E1LocalEdgePlasticityState
    applied_adapter: E1WeightedFieldAdapterResult

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise FrozenE1ProbeError("frozen probe result requires one field")
        if not isinstance(self.e1_state, E1LocalEdgePlasticityState):
            raise FrozenE1ProbeError("frozen probe result requires one E1 state")
        if not isinstance(self.applied_adapter, E1WeightedFieldAdapterResult):
            raise FrozenE1ProbeError(
                "frozen probe result requires one applied adapter"
            )
        try:
            validate_e1_state_for_layer(self.field.layer, self.e1_state)
        except E1LocalEdgePlasticityError as exc:
            raise FrozenE1ProbeError(str(exc)) from exc
        if (
            self.applied_adapter.edge_inventory_digest
            != self.e1_state.edge_inventory_digest
        ):
            raise FrozenE1ProbeError(
                "frozen probe field, state, and adapter geometry must match"
            )


def _validated_interval(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
) -> float:
    if not isinstance(field, SharedMCMField):
        raise FrozenE1ProbeError("frozen E1 probe requires one shared field")
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise FrozenE1ProbeError(
            "frozen E1 probe requires one substrate configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise FrozenE1ProbeError(
            "frozen E1 probe requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise FrozenE1ProbeError(
            "frozen E1 probe dissipation configuration is invalid"
        )
    try:
        return _step_duration(distribution, step_time)
    except NeutralLocalFieldSubstrateError as exc:
        raise FrozenE1ProbeError(str(exc)) from exc


def _advance_with_fixed_adapter(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
    adapter: E1WeightedFieldAdapterResult,
    elapsed: float,
) -> SharedMCMField:
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
    except (
        E1CoupledFastFieldError,
        E1WeightedFieldAdapterError,
        NeutralLocalFieldSubstrateError,
    ) as exc:
        raise FrozenE1ProbeError(str(exc)) from exc
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
        raise FrozenE1ProbeError(str(exc)) from exc
    outputs = {
        neuron.neuron_id: MCMNeuronOutput(
            float(activation[index]),
            float(afterimage[index]),
        )
        for index, neuron in enumerate(neurons)
    }

    def exact_frozen_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
        return outputs[drive.previous.neuron_id]

    try:
        return field.advance(
            distribution,
            exact_frozen_output,
            step_time=step_time,
        )
    except SharedMCMFieldError as exc:
        raise FrozenE1ProbeError(str(exc)) from exc


def advance_frozen_e1_probe(
    field: SharedMCMField,
    frozen_e1_state: E1LocalEdgePlasticityState,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    backreaction_enabled: bool,
) -> FrozenE1ProbeResult:
    """Advance S/H once while returning the exact same E1 state object."""

    if not isinstance(backreaction_enabled, bool):
        raise FrozenE1ProbeError("backreaction_enabled must be boolean")
    elapsed = _validated_interval(
        field,
        distribution,
        step_time,
        substrate_config,
        afterimage_config,
        dissipation_config,
    )
    try:
        validate_e1_state_for_layer(field.layer, frozen_e1_state)
        adapter = compute_e1_weighted_edge_rates(
            field.layer,
            frozen_e1_state,
            substrate_config,
            backreaction_enabled=backreaction_enabled,
        )
    except (E1LocalEdgePlasticityError, E1WeightedFieldAdapterError) as exc:
        raise FrozenE1ProbeError(str(exc)) from exc
    next_field = _advance_with_fixed_adapter(
        field,
        distribution,
        step_time,
        substrate_config,
        afterimage_config,
        dissipation_config,
        adapter,
        elapsed,
    )
    return FrozenE1ProbeResult(next_field, frozen_e1_state, adapter)


def advance_fixed_e1_adapter_probe(
    field: SharedMCMField,
    fixed_adapter: E1WeightedFieldAdapterResult,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> SharedMCMField:
    """Advance S/H with one precomputed fixed spatial edge-rate ledger."""

    if not isinstance(fixed_adapter, E1WeightedFieldAdapterResult):
        raise FrozenE1ProbeError(
            "fixed E1 adapter probe requires one adapter result"
        )
    elapsed = _validated_interval(
        field,
        distribution,
        step_time,
        substrate_config,
        afterimage_config,
        dissipation_config,
    )
    return _advance_with_fixed_adapter(
        field,
        distribution,
        step_time,
        substrate_config,
        afterimage_config,
        dissipation_config,
        fixed_adapter,
        elapsed,
    )
