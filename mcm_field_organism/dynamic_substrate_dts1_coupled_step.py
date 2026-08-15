"""Private atomic first-order coupling of DTS-1 and the fast S/H field."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math

import numpy as np

from .dynamic_substrate_dts1_backreaction import (
    DTS1BackreactionError,
    DTS1BackreactionResult,
    build_dts1_diffusion_generator,
    compute_dts1_edge_rates,
)
from .dynamic_substrate_dts1_step import (
    DTS1EdgeParticipation,
    DTS1EdgeTransfer,
    DTS1StepError,
    DTS1StepRates,
    compute_dts1_closed_prestate_step,
)
from .dynamic_substrate_s1hi_resource_anatomy import DTS1ResourceAnatomy
from .dynamic_substrate_s1hk_edge_participation_contract import (
    DTS1S1HKEdgeParticipationContractError,
    compute_dts1_s1hk_edge_participation,
)
from .field_step_time import MCMFieldStepTime
from .mcm_neuron_layer import MCMNeuronDrive, MCMNeuronOutput
from .mcm_substrate_state import (
    MCMSubstrateStateError,
    mcm_substrate_edge_inventory,
    mcm_substrate_edge_inventory_digest,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    _diffusion_generator,
    _generator_and_boundary,
    _integrate_activation_afterimage_with_spectrum,
    _step_duration,
    advance_neutral_fast_shared_field,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError


class DTS1CoupledStepError(ValueError):
    """Raised before output when one atomic DTS-1/S/H step is invalid."""


S1_HW_IMPLEMENTATION_ID = "dynamic-substrate.coupled-step.s1hw.v1"
S1_HW_SOURCE_S1HV_CONTRACT_DIGEST = (
    "440ecb022f7684f5938f8df584c5dff8c5abbd4a92bdfdffb83cb4ee89216327"
)
S1_HW_MATRIX_CASE_IDS = tuple(f"T{index:02d}" for index in range(1, 21))
S1_HW_DECISION = "DTS1_PRIVATE_COUPLED_STEP_IMPLEMENTED_TECHNICALLY_ACCEPTED"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _finite_positive(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise DTS1CoupledStepError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DTS1CoupledStepError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result <= 0.0:
        raise DTS1CoupledStepError(f"{role} must be finite and positive")
    return result


def _geometry_edges(field: SharedMCMField) -> tuple[tuple[str, str], ...]:
    try:
        return mcm_substrate_edge_inventory(field.layer)
    except MCMSubstrateStateError as exc:
        raise DTS1CoupledStepError(str(exc)) from exc


@dataclass(frozen=True, slots=True)
class DTS1CoupledFastFieldStepResult:
    """One complete field/anatomy pair plus passive prestate ledgers."""

    field: SharedMCMField
    anatomy: DTS1ResourceAnatomy
    elapsed_time: float
    participations: tuple[DTS1EdgeParticipation, ...]
    resource_transfers: tuple[DTS1EdgeTransfer, ...]
    applied_adapter: DTS1BackreactionResult

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise DTS1CoupledStepError("coupled result requires one complete field")
        if not isinstance(self.anatomy, DTS1ResourceAnatomy):
            raise DTS1CoupledStepError("coupled result requires one complete anatomy")
        object.__setattr__(
            self,
            "elapsed_time",
            _finite_positive(self.elapsed_time, "elapsed_time"),
        )
        participations = tuple(self.participations)
        transfers = tuple(self.resource_transfers)
        if not participations or any(
            not isinstance(item, DTS1EdgeParticipation) for item in participations
        ):
            raise DTS1CoupledStepError(
                "coupled result requires one complete participation ledger"
            )
        if not transfers or any(
            not isinstance(item, DTS1EdgeTransfer) for item in transfers
        ):
            raise DTS1CoupledStepError(
                "coupled result requires one complete transfer ledger"
            )
        if not isinstance(self.applied_adapter, DTS1BackreactionResult):
            raise DTS1CoupledStepError("coupled result requires one applied adapter")
        edges = _geometry_edges(self.field)
        anatomy_edges = tuple(item.edge for item in self.anatomy.edge_resources)
        participation_edges = tuple(sorted(item.edge for item in participations))
        transfer_edges = tuple(sorted(item.edge for item in transfers))
        if (
            anatomy_edges != edges
            or participation_edges != edges
            or transfer_edges != edges
            or self.applied_adapter.edges != edges
        ):
            raise DTS1CoupledStepError(
                "coupled result ledgers must share the complete field geometry"
            )
        try:
            digest = mcm_substrate_edge_inventory_digest(self.field.layer)
        except MCMSubstrateStateError as exc:
            raise DTS1CoupledStepError(str(exc)) from exc
        if self.applied_adapter.edge_inventory_digest != digest:
            raise DTS1CoupledStepError(
                "coupled result adapter digest must match the field geometry"
            )
        object.__setattr__(self, "participations", tuple(sorted(participations, key=lambda x: x.edge)))
        object.__setattr__(self, "resource_transfers", tuple(sorted(transfers, key=lambda x: x.edge)))


@dataclass(frozen=True, slots=True)
class DTS1S1HWImplementationReceipt:
    implementation_id: str
    source_s1hv_contract_digest: str
    matrix_case_ids: tuple[str, ...]
    private_coupled_step_implemented: bool
    existing_neutral_integrator_reused: bool
    exact_neutral_delegation_implemented: bool
    atomic_pair_result_implemented: bool
    technical_matrix_execution_only: bool
    runtime_integration_present: bool
    material_rate_values_selected: bool
    research_execution_permitted: bool
    research_field_steps_executed: int
    functional_effect_proven: bool
    claims_permitted: bool
    decision: str
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "receipt_digest"
        }
        if (
            self.implementation_id != S1_HW_IMPLEMENTATION_ID
            or self.source_s1hv_contract_digest
            != S1_HW_SOURCE_S1HV_CONTRACT_DIGEST
            or self.matrix_case_ids != S1_HW_MATRIX_CASE_IDS
            or any(
                value is not True
                for value in (
                    self.private_coupled_step_implemented,
                    self.existing_neutral_integrator_reused,
                    self.exact_neutral_delegation_implemented,
                    self.atomic_pair_result_implemented,
                    self.technical_matrix_execution_only,
                )
            )
            or any(
                value is not False
                for value in (
                    self.runtime_integration_present,
                    self.material_rate_values_selected,
                    self.research_execution_permitted,
                    self.functional_effect_proven,
                    self.claims_permitted,
                )
            )
            or self.research_field_steps_executed != 0
            or self.decision != S1_HW_DECISION
            or self.receipt_digest != _digest(payload)
        ):
            raise DTS1CoupledStepError(
                "S1-HW implementation receipt violates the technical-only boundary"
            )


def build_dts1_s1hw_implementation_receipt() -> DTS1S1HWImplementationReceipt:
    """Return the static S1-HW receipt without advancing any field."""

    values = {
        "implementation_id": S1_HW_IMPLEMENTATION_ID,
        "source_s1hv_contract_digest": S1_HW_SOURCE_S1HV_CONTRACT_DIGEST,
        "matrix_case_ids": S1_HW_MATRIX_CASE_IDS,
        "private_coupled_step_implemented": True,
        "existing_neutral_integrator_reused": True,
        "exact_neutral_delegation_implemented": True,
        "atomic_pair_result_implemented": True,
        "technical_matrix_execution_only": True,
        "runtime_integration_present": False,
        "material_rate_values_selected": False,
        "research_execution_permitted": False,
        "research_field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_HW_DECISION,
    }
    return DTS1S1HWImplementationReceipt(
        **values,
        receipt_digest=_digest(values),
    )


def _participation_ledger(
    field: SharedMCMField,
    edges: tuple[tuple[str, str], ...],
) -> tuple[DTS1EdgeParticipation, ...]:
    activation = {
        neuron.neuron_id: neuron.activation for neuron in field.layer.neurons
    }
    try:
        return tuple(
            DTS1EdgeParticipation(
                first,
                second,
                compute_dts1_s1hk_edge_participation(
                    activation[first], activation[second]
                ),
            )
            for first, second in edges
        )
    except (DTS1StepError, DTS1S1HKEdgeParticipationContractError, KeyError) as exc:
        raise DTS1CoupledStepError(str(exc)) from exc


def _advance_active_field(
    field: SharedMCMField,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
    adapter: DTS1BackreactionResult,
    elapsed: float,
) -> SharedMCMField:
    try:
        generator = build_dts1_diffusion_generator(field.layer, adapter)
        neutral_generator, boundary = _generator_and_boundary(
            field,
            distribution,
            substrate_config,
        )
        neutral_internal = _diffusion_generator(field, substrate_config)
        generator = generator + (neutral_generator - neutral_internal)
        eigenvalues, eigenvectors = np.linalg.eigh(generator)
        leak_rate = (
            0.0
            if dissipation_config is None
            else dissipation_config.leak_rate_per_second
        )
        neurons = field.layer.neurons
        activation, afterimage = _integrate_activation_afterimage_with_spectrum(
            np.asarray(
                [neuron.activation for neuron in neurons], dtype=np.float64
            ),
            np.asarray(
                [neuron.afterimage for neuron in neurons], dtype=np.float64
            ),
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

        def exact_dts1_output(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            return outputs[drive.previous.neuron_id]

        return field.advance(
            distribution,
            exact_dts1_output,
            step_time=step_time,
        )
    except (
        DTS1BackreactionError,
        NeutralLocalFieldSubstrateError,
        SharedMCMFieldError,
        np.linalg.LinAlgError,
    ) as exc:
        raise DTS1CoupledStepError(str(exc)) from exc


def advance_dts1_coupled_fast_shared_field(
    field: SharedMCMField,
    anatomy: DTS1ResourceAnatomy,
    distribution: ReceptorDistribution,
    step_time: MCMFieldStepTime,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dts1_rates: DTS1StepRates,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    backreaction_enabled: bool,
) -> DTS1CoupledFastFieldStepResult:
    """Advance one positive closed-prestate DTS-1/S/H interval atomically."""

    if not isinstance(field, SharedMCMField):
        raise DTS1CoupledStepError("coupled step requires one shared field")
    if not isinstance(anatomy, DTS1ResourceAnatomy):
        raise DTS1CoupledStepError("coupled step requires one DTS-1 anatomy")
    if not isinstance(distribution, ReceptorDistribution):
        raise DTS1CoupledStepError("coupled step requires one receptor distribution")
    if not isinstance(step_time, MCMFieldStepTime):
        raise DTS1CoupledStepError("coupled step requires one positive field step")
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise DTS1CoupledStepError("coupled step substrate config is invalid")
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise DTS1CoupledStepError("coupled step afterimage config is invalid")
    if not isinstance(dts1_rates, DTS1StepRates):
        raise DTS1CoupledStepError("coupled step requires one DTS1StepRates value")
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise DTS1CoupledStepError("coupled step dissipation config is invalid")
    if not isinstance(backreaction_enabled, bool):
        raise DTS1CoupledStepError("backreaction_enabled must be boolean")

    try:
        elapsed = _step_duration(distribution, step_time)
        edges = _geometry_edges(field)
        adapter = compute_dts1_edge_rates(
            field.layer,
            anatomy,
            substrate_config,
            backreaction_enabled=backreaction_enabled,
        )
        participations = _participation_ledger(field, edges)
        resource_result = compute_dts1_closed_prestate_step(
            anatomy,
            participations,
            elapsed,
            dts1_rates,
        )
    except (
        DTS1BackreactionError,
        DTS1StepError,
        NeutralLocalFieldSubstrateError,
    ) as exc:
        raise DTS1CoupledStepError(str(exc)) from exc

    all_base_rate = all(
        item.rate_per_second == adapter.base_rate_per_second
        for item in adapter.edge_rates
    )
    try:
        if all_base_rate:
            next_field = advance_neutral_fast_shared_field(
                field,
                distribution,
                step_time,
                substrate_config,
                afterimage_config,
                dissipation_config,
            )
        else:
            next_field = _advance_active_field(
                field,
                distribution,
                step_time,
                substrate_config,
                afterimage_config,
                dissipation_config,
                adapter,
                elapsed,
            )
    except (NeutralLocalFieldSubstrateError, DTS1CoupledStepError) as exc:
        raise DTS1CoupledStepError(str(exc)) from exc

    return DTS1CoupledFastFieldStepResult(
        field=next_field,
        anatomy=resource_result.next_anatomy,
        elapsed_time=elapsed,
        participations=participations,
        resource_transfers=resource_result.edge_transfers,
        applied_adapter=adapter,
    )
