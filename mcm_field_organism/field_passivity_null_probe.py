"""Passive quadratic balance audit for the existing neutral field."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

import numpy as np

from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralLocalFieldSubstrateConfig,
    _diffusion_generator,
    _generator_and_boundary,
    advance_neutral_shared_field,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import (
    ReceptorDistribution,
    ReceptorDistributor,
    ReceptorDock,
)
from .shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)


class FieldPassivityNullProbeError(ValueError):
    """Raised when the existing field fails its passive balance identity."""


@dataclass(frozen=True, slots=True)
class QuadraticFieldBalanceObservation:
    source_field_digest: str
    distribution_digest: str
    quadratic_storage: float
    storage_rate: float
    receptor_supply_rate: float
    neighbor_dissipation_rate: float
    receptor_dissipation_rate: float
    balance_error: float
    maximum_generator_eigenvalue: float

    def __post_init__(self) -> None:
        numeric = (
            self.quadratic_storage,
            self.storage_rate,
            self.receptor_supply_rate,
            self.neighbor_dissipation_rate,
            self.receptor_dissipation_rate,
            self.balance_error,
            self.maximum_generator_eigenvalue,
        )
        if any(not math.isfinite(value) for value in numeric):
            raise FieldPassivityNullProbeError(
                "quadratic balance observation must remain finite"
            )
        if self.quadratic_storage < 0.0:
            raise FieldPassivityNullProbeError(
                "quadratic storage must remain nonnegative"
            )
        if self.neighbor_dissipation_rate < -1e-12:
            raise FieldPassivityNullProbeError(
                "neighbor dissipation must remain nonnegative"
            )
        if self.receptor_dissipation_rate < -1e-12:
            raise FieldPassivityNullProbeError(
                "receptor dissipation must remain nonnegative"
            )


@dataclass(frozen=True, slots=True)
class FieldPassivityNullProbeResult:
    contact_free: QuadraticFieldBalanceObservation
    receptor_driven: QuadraticFieldBalanceObservation
    contact_free_storage_nonincreasing: bool
    receptor_balance_closed: bool
    field_digest_preserved: bool
    distribution_digests_preserved: bool
    observer_writeback_performed: bool
    accumulation_performed: bool
    physical_energy_claimed: bool
    new_runtime_state_added: bool
    runtime_candidate_released: bool


_CLOCK_ID = "organism.field_passivity_null"
_GEOMETRY_ID = "auditory.passivity_line.v1"
_SAMPLE_OFFSETS = ((-1,), (1,))
_SEED_VALUES = (0.9, -0.2, 0.5, -0.7)
_DRIVE_VALUES = (0.4, -0.8, 0.2, 0.6)
_TOLERANCE = 1e-12


def observe_quadratic_field_balance(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    config: NeutralLocalFieldSubstrateConfig,
) -> QuadraticFieldBalanceObservation:
    """Observe one exact local balance without accumulation or writeback."""

    if not isinstance(field, SharedMCMField):
        raise FieldPassivityNullProbeError(
            "quadratic balance requires one completed shared field"
        )
    if not isinstance(distribution, ReceptorDistribution):
        raise FieldPassivityNullProbeError(
            "quadratic balance requires one receptor distribution"
        )
    if not isinstance(config, NeutralLocalFieldSubstrateConfig):
        raise FieldPassivityNullProbeError(
            "quadratic balance requires the existing substrate configuration"
        )

    generator, boundary = _generator_and_boundary(
        field,
        distribution,
        config,
    )
    diffusion = _diffusion_generator(field, config)
    receptor_sink = generator - diffusion
    activation = np.asarray(
        [neuron.activation for neuron in field.layer.neurons],
        dtype=np.float64,
    )
    derivative = generator @ activation + boundary
    quadratic_storage = 0.5 * float(activation @ activation)
    storage_rate = float(activation @ derivative)
    receptor_supply_rate = float(activation @ boundary)
    neighbor_dissipation_rate = -float(
        activation @ (diffusion @ activation)
    )
    receptor_dissipation_rate = -float(
        activation @ (receptor_sink @ activation)
    )
    predicted_rate = (
        receptor_supply_rate
        - neighbor_dissipation_rate
        - receptor_dissipation_rate
    )
    balance_error = abs(storage_rate - predicted_rate)
    maximum_generator_eigenvalue = float(
        np.max(np.linalg.eigvalsh(generator))
    )

    if balance_error > _TOLERANCE:
        raise FieldPassivityNullProbeError(
            "existing field failed its quadratic balance identity"
        )
    if maximum_generator_eigenvalue > _TOLERANCE:
        raise FieldPassivityNullProbeError(
            "existing field generator is not dissipative"
        )

    return QuadraticFieldBalanceObservation(
        source_field_digest=field.snapshot().digest(),
        distribution_digest=distribution.digest(),
        quadratic_storage=quadratic_storage,
        storage_rate=storage_rate,
        receptor_supply_rate=receptor_supply_rate,
        neighbor_dissipation_rate=neighbor_dissipation_rate,
        receptor_dissipation_rate=receptor_dissipation_rate,
        balance_error=balance_error,
        maximum_generator_eigenvalue=maximum_generator_eigenvalue,
    )


def _frame(
    snapshot_id: str,
    values: tuple[float, ...],
    *,
    start_tick: int,
    end_tick: int,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id=_GEOMETRY_ID,
        snapshot_id=snapshot_id,
        clock_id="auditory.source",
        window_start_tick=start_tick,
        window_end_tick=end_tick,
        carrier_ids=tuple(
            f"auditory.carrier.{index}" for index in range(len(values))
        ),
        values=values,
    )


def _field_and_distributor() -> tuple[SharedMCMField, ReceptorDistributor]:
    reference = _frame(
        "auditory.reference",
        (0.0,) * len(_SEED_VALUES),
        start_tick=0,
        end_tick=10,
    )
    field = build_shared_mcm_field(
        (reference,),
        {
            "auditory": ReceptorDockAnatomy(
                modality_id="auditory",
                dock_id="dock.auditory",
                positions=tuple((index,) for index in range(len(_SEED_VALUES))),
            )
        },
        sample_offsets=_SAMPLE_OFFSETS,
    )
    distributor = ReceptorDistributor()
    distributor.attach(
        ReceptorDock("dock.auditory", "auditory", _GEOMETRY_ID)
    )
    return field, distributor


def _distribution(
    distributor: ReceptorDistributor,
    start_tick: int,
    end_tick: int,
    frame: ReceptorContactFrame | None,
) -> ReceptorDistribution:
    return distributor.distribute(
        () if frame is None else (frame,),
        CommonFieldTime(_CLOCK_ID, start_tick, end_tick),
    )


def run_field_passivity_null_probe() -> FieldPassivityNullProbeResult:
    """Show that passivity adds no state to the existing neutral field."""

    config = NeutralLocalFieldSubstrateConfig(1.0)
    initial, distributor = _field_and_distributor()
    seeded = advance_neutral_shared_field(
        initial,
        _distribution(
            distributor,
            0,
            10,
            _frame(
                "auditory.seed",
                _SEED_VALUES,
                start_tick=0,
                end_tick=10,
            ),
        ),
        MCMFieldStepTime(_CLOCK_ID, 0, 10, 10.0),
        config,
    )
    contact_free_distribution = _distribution(distributor, 10, 20, None)
    receptor_distribution = _distribution(
        distributor,
        10,
        20,
        _frame(
            "auditory.drive",
            _DRIVE_VALUES,
            start_tick=10,
            end_tick=20,
        ),
    )
    field_digest = seeded.snapshot().digest()
    contact_free_digest = contact_free_distribution.digest()
    receptor_digest = receptor_distribution.digest()

    contact_free = observe_quadratic_field_balance(
        seeded,
        contact_free_distribution,
        config,
    )
    receptor_driven = observe_quadratic_field_balance(
        seeded,
        receptor_distribution,
        config,
    )

    return FieldPassivityNullProbeResult(
        contact_free=contact_free,
        receptor_driven=receptor_driven,
        contact_free_storage_nonincreasing=(
            contact_free.storage_rate <= _TOLERANCE
            and contact_free.receptor_supply_rate == 0.0
        ),
        receptor_balance_closed=(
            receptor_driven.balance_error <= _TOLERANCE
            and receptor_driven.storage_rate
            <= receptor_driven.receptor_supply_rate + _TOLERANCE
        ),
        field_digest_preserved=field_digest == seeded.snapshot().digest(),
        distribution_digests_preserved=(
            contact_free_digest == contact_free_distribution.digest()
            and receptor_digest == receptor_distribution.digest()
        ),
        observer_writeback_performed=False,
        accumulation_performed=False,
        physical_energy_claimed=False,
        new_runtime_state_added=False,
        runtime_candidate_released=False,
    )


def field_passivity_null_probe_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for contract in (
            QuadraticFieldBalanceObservation,
            FieldPassivityNullProbeResult,
        )
        for item in fields(contract)
    )
