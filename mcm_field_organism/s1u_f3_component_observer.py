"""Passive SSPRK stage ledger for one preregistered S1-T cell."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

import numpy as np

from ._synthetic_av_field_fixture import SYNTHETIC_AV_TICKS_PER_SECOND
from .mcm_f3_coupling import MCMF3CouplingResult, compute_mcm_f3_coupling
from .mcm_substrate_state import (
    MCMSubstrateArmContract,
    mcm_substrate_edge_inventory,
)
from .s1j_f3_av_compatibility import (
    S1J_ACTIVE_ARM,
    S1J_SUPPORT_TICKS,
    advance_s1j_f3_av_sequences,
)
from .s1o_exposure_retention_matrix import _initial_field, _model
from .s1r_phase_separation_matrix import (
    _delay_sequences,
    build_s1r_cell_source_contract,
)


class S1UF3ComponentObserverError(ValueError):
    """Raised when the passive component ledger loses exact accounting."""


@dataclass(frozen=True, slots=True)
class S1UComponentLedgerResult:
    cell_id: str
    model_id: str
    refinement: int
    source_role: str
    neuron_ids: tuple[str, ...]
    mass_start: tuple[float, ...]
    mass_end: tuple[float, ...]
    delta_transport: tuple[float, ...]
    delta_activation_forcing: tuple[float, ...]
    delta_total_rate: tuple[float, ...]
    delta_mass: tuple[float, ...]
    closure_vector: tuple[float, ...]
    transport_sum: float
    activation_forcing_sum: float
    total_rate_sum: float
    delta_mass_sum: float
    stage_count: int
    integrated_weight_seconds: float
    argmax_start_neuron_id: str
    argmax_end_neuron_id: str
    observed_end_digest: str
    reference_end_digest: str
    observer_transparent: bool
    raw_payload_retained: bool = False
    classification_allowed: bool = False
    runtime_writeback_allowed: bool = False
    memory_claim_allowed: bool = False
    field_time_claim_allowed: bool = False

    @property
    def closure_linf(self) -> float:
        return max((abs(value) for value in self.closure_vector), default=0.0)


class _ComponentAccumulator:
    def __init__(self, field, model_id: str) -> None:
        if field.substrate is None:
            raise S1UF3ComponentObserverError("S1-U requires one M state")
        self._neuron_ids = tuple(
            neuron.neuron_id for neuron in field.layer.neurons
        )
        self._index = {
            neuron_id: index
            for index, neuron_id in enumerate(self._neuron_ids)
        }
        self._edges = mcm_substrate_edge_inventory(field.layer)
        self._arm = field.substrate.arm
        self._model_id = model_id
        self.transport = np.zeros(len(self._neuron_ids), dtype=np.float64)
        self.activation_forcing = np.zeros(
            len(self._neuron_ids),
            dtype=np.float64,
        )
        self.total_rate = np.zeros(len(self._neuron_ids), dtype=np.float64)
        self.stage_count = 0
        self.integrated_weight_seconds = 0.0

    def __call__(
        self,
        integration_weight_seconds: float,
        activation: np.ndarray,
        mass: np.ndarray,
        coupling: MCMF3CouplingResult,
    ) -> None:
        if (
            not math.isfinite(integration_weight_seconds)
            or integration_weight_seconds <= 0.0
        ):
            raise S1UF3ComponentObserverError(
                "S1-U requires one positive finite stage weight"
            )
        if activation.flags.writeable or mass.flags.writeable:
            raise S1UF3ComponentObserverError(
                "S1-U stage vectors must be read-only copies"
            )
        transport_rate = np.zeros(len(self._neuron_ids), dtype=np.float64)
        forcing_rate = np.zeros(len(self._neuron_ids), dtype=np.float64)
        neutral = self._arm.initial_total_mass / len(self._neuron_ids)
        for first_id, second_id in self._edges:
            first = self._index[first_id]
            second = self._index[second_id]
            activation_delta = activation[second] - activation[first]
            transport_change = self._arm.lambda_sm_per_second * (
                mass[second] - mass[first]
            )
            if self._model_id == "linear-coupled-field":
                forcing_change = (
                    -2.0
                    * self._arm.lambda_sm_per_second
                    * self._arm.kappa
                    * neutral
                    * activation_delta
                )
            else:
                forcing_change = (
                    -self._arm.lambda_sm_per_second
                    * self._arm.kappa
                    * (mass[first] + mass[second])
                    * activation_delta
                )
            transport_rate[first] += transport_change
            transport_rate[second] -= transport_change
            forcing_rate[first] += forcing_change
            forcing_rate[second] -= forcing_change

        total_rate = np.asarray(coupling.mass_rate, dtype=np.float64)
        if not np.allclose(
            transport_rate + forcing_rate,
            total_rate,
            rtol=0.0,
            atol=1e-12,
        ):
            raise S1UF3ComponentObserverError(
                "S1-U direct rates do not reconstruct the coupling"
            )
        self.transport += integration_weight_seconds * transport_rate
        self.activation_forcing += integration_weight_seconds * forcing_rate
        self.total_rate += integration_weight_seconds * total_rate
        self.stage_count += 1
        self.integrated_weight_seconds += integration_weight_seconds


def _mass_vector(field) -> tuple[float, ...]:
    if field.substrate is None:
        raise S1UF3ComponentObserverError("S1-U field lost M")
    return tuple(item.mass for item in field.substrate.masses)


def _argmax_centered_mass(field, mass: tuple[float, ...]) -> str:
    if field.substrate is None:
        raise S1UF3ComponentObserverError("S1-U field lost M")
    neutral = field.substrate.arm.initial_total_mass / len(mass)
    index = max(range(len(mass)), key=lambda item: abs(mass[item] - neutral))
    return field.substrate.neuron_ids[index]


def _bound_model(model_id: str):
    if model_id == "kappa-null":
        return (
            MCMSubstrateArmContract(
                "s1v.kappa-null",
                S1J_ACTIVE_ARM.lambda_sm_per_second,
                0.0,
                S1J_ACTIVE_ARM.eta,
                S1J_ACTIVE_ARM.initial_total_mass,
            ),
            compute_mcm_f3_coupling,
        )
    return _model(model_id)


def _observe_interval(
    cell_id: str,
    model_id: str,
    refinement: int,
    source_role: str,
    formed,
    sequences,
    calculator,
) -> S1UComponentLedgerResult:
    mass_start = _mass_vector(formed)
    accumulator = _ComponentAccumulator(formed, model_id)
    observed = advance_s1j_f3_av_sequences(
        formed,
        sequences,
        coupling_calculator=calculator,
        refinement=refinement,
        coupling_stage_observer=accumulator,
    ).field
    reference = advance_s1j_f3_av_sequences(
        formed,
        sequences,
        coupling_calculator=calculator,
        refinement=refinement,
    ).field
    mass_end = _mass_vector(observed)
    delta_mass = tuple(
        end - start
        for start, end in zip(mass_start, mass_end, strict=True)
    )
    delta_transport = tuple(float(value) for value in accumulator.transport)
    delta_forcing = tuple(
        float(value) for value in accumulator.activation_forcing
    )
    delta_total = tuple(float(value) for value in accumulator.total_rate)
    closure = tuple(
        actual - transport - forcing
        for actual, transport, forcing in zip(
            delta_mass,
            delta_transport,
            delta_forcing,
            strict=True,
        )
    )
    observed_digest = observed.snapshot().digest()
    reference_digest = reference.snapshot().digest()
    neuron_ids = tuple(neuron.neuron_id for neuron in observed.layer.neurons)
    return S1UComponentLedgerResult(
        cell_id=cell_id,
        model_id=model_id,
        refinement=refinement,
        source_role=source_role,
        neuron_ids=neuron_ids,
        mass_start=mass_start,
        mass_end=mass_end,
        delta_transport=delta_transport,
        delta_activation_forcing=delta_forcing,
        delta_total_rate=delta_total,
        delta_mass=delta_mass,
        closure_vector=closure,
        transport_sum=math.fsum(delta_transport),
        activation_forcing_sum=math.fsum(delta_forcing),
        total_rate_sum=math.fsum(delta_total),
        delta_mass_sum=math.fsum(delta_mass),
        stage_count=accumulator.stage_count,
        integrated_weight_seconds=accumulator.integrated_weight_seconds,
        argmax_start_neuron_id=_argmax_centered_mass(formed, mass_start),
        argmax_end_neuron_id=_argmax_centered_mass(observed, mass_end),
        observed_end_digest=observed_digest,
        reference_end_digest=reference_digest,
        observer_transparent=observed_digest == reference_digest,
    )


def run_s1u_component_cell(
    model_id: str,
    dose_count: int,
    source_form: str,
    delay_seconds: float,
    refinement: int,
    *,
    source_role: str = "exposed",
) -> S1UComponentLedgerResult:
    """Observe one delay interval without classifying the S1-T curves."""

    if model_id not in {
        "f3",
        "linear-coupled-field",
        "kappa-null",
        "eta-null",
        "p0",
    }:
        raise S1UF3ComponentObserverError("S1-U model is not bound")
    if source_role not in {"exposed", "uniform-null"}:
        raise S1UF3ComponentObserverError("S1-U source role is not bound")
    source = build_s1r_cell_source_contract(
        dose_count,
        source_form,
        delay_seconds,
    )
    if source.delay is None:
        raise S1UF3ComponentObserverError(
            "S1-U requires one positive null-contact interval"
        )
    arm, calculator = _bound_model(model_id)
    exposure = (
        source.exposure
        if source_role == "exposed"
        else source.exposure_zero
    )
    initial = _initial_field(exposure, arm)
    formed = advance_s1j_f3_av_sequences(
        initial,
        exposure,
        coupling_calculator=calculator,
        refinement=refinement,
    ).field
    return _observe_interval(
        source.cell.cell_id,
        model_id,
        refinement,
        source_role,
        formed,
        source.delay,
        calculator,
    )


def run_s1u_component_late_interval(
    model_id: str,
    dose_count: int,
    source_form: str,
    start_seconds: float,
    end_seconds: float,
    refinement: int,
) -> S1UComponentLedgerResult:
    """Observe one causally nested late S1-T interval."""

    allowed_intervals = {(0.2, 0.4), (0.4, 0.8), (0.8, 1.6)}
    if (start_seconds, end_seconds) not in allowed_intervals:
        raise S1UF3ComponentObserverError(
            "S1-U late interval is not causally nested"
        )
    if model_id not in {
        "f3",
        "linear-coupled-field",
        "kappa-null",
        "eta-null",
    }:
        raise S1UF3ComponentObserverError("S1-U late model is not bound")
    source = build_s1r_cell_source_contract(
        dose_count,
        source_form,
        end_seconds,
    )
    arm, calculator = _bound_model(model_id)
    initial = _initial_field(source.exposure, arm)
    formed = advance_s1j_f3_av_sequences(
        initial,
        source.exposure,
        coupling_calculator=calculator,
        refinement=refinement,
    ).field
    exposure_end = dose_count * S1J_SUPPORT_TICKS
    start_ticks = round(start_seconds * SYNTHETIC_AV_TICKS_PER_SECOND)
    end_ticks = round(end_seconds * SYNTHETIC_AV_TICKS_PER_SECOND)
    prefix = _delay_sequences(
        f"{source.cell.cell_id}.ledger-prefix",
        exposure_end,
        start_ticks,
    )
    if prefix is None:
        raise S1UF3ComponentObserverError("S1-U late prefix is missing")
    formed = advance_s1j_f3_av_sequences(
        formed,
        prefix,
        coupling_calculator=calculator,
        refinement=refinement,
    ).field
    interval = _delay_sequences(
        f"{source.cell.cell_id}.ledger-interval",
        exposure_end + start_ticks,
        end_ticks - start_ticks,
    )
    if interval is None:
        raise S1UF3ComponentObserverError("S1-U late interval is empty")
    return _observe_interval(
        (
            f"s1u.d{dose_count}.{source_form}."
            f"interval-{start_seconds}-{end_seconds}"
        ),
        model_id,
        refinement,
        "exposed",
        formed,
        interval,
        calculator,
    )


def s1u_component_observer_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(S1UComponentLedgerResult))
