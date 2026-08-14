"""Technical F3 compatibility composition for the current synthetic AV field."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math
from typing import Callable

from ._synthetic_av_field_fixture import (
    SYNTHETIC_AUDITORY_CARRIER_IDS,
    SYNTHETIC_AV_CLOCK_ID,
    SYNTHETIC_AV_TICKS_PER_SECOND,
    SYNTHETIC_VISUAL_CONFIG,
    build_synthetic_av_field,
    synthetic_av_sequences,
)
from .field_step_time import MCMFieldStepTime
from .mcm_f3_baseline_coupling import (
    compute_mcm_f3_linear_coupled_baseline,
)
from .mcm_f3_coupling import MCMF3CouplingResult, compute_mcm_f3_coupling
from .mcm_f3_runtime import (
    MCMF3AdvanceDiagnostics,
    activate_mcm_f3_field,
    advance_mcm_f3_shared_field_transient,
)
from .mcm_neuron_layer import MCMNeuronLayer
from .mcm_substrate_state import MCMSubstrateArmContract, MCMSubstrateState
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff_audit import handoff_receptor_completion_groups
from .receptor_time_alignment import ReceptorTimeSequence
from .shared_mcm_field import (
    SharedMCMField,
    attach_uniform_mcm_substrate,
)
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class S1JF3AVCompatibilityError(ValueError):
    """Raised when the fixed S1-J technical composition loses its boundary."""


S1J_ACTIVE_ARM = MCMSubstrateArmContract("p1.active", 1.0, 0.5, 1.0)
S1J_ETA_NULL_ARM = MCMSubstrateArmContract("b.eta-null", 1.0, 0.5, 0.0)
S1J_P0_ARM = MCMSubstrateArmContract("p0.null", 0.0, 0.5, 1.0)
S1J_SUBSTRATE_CONFIG = NeutralLocalFieldSubstrateConfig(1.0)
S1J_AFTERIMAGE_CONFIG = NeutralFastAfterimageConfig(0.5)
S1J_SUPPORT_TICKS = 100_000_000

_CouplingCalculator = Callable[
    [MCMNeuronLayer, MCMSubstrateState],
    MCMF3CouplingResult,
]
_ALLOWED_CALCULATORS = {
    compute_mcm_f3_coupling: "f3",
    compute_mcm_f3_linear_coupled_baseline: "linear-coupled-field",
}


@dataclass(frozen=True, slots=True)
class S1JF3AVSequenceAdvance:
    """One completed technical sequence handoff without an output artifact."""

    field: SharedMCMField
    diagnostics: tuple[MCMF3AdvanceDiagnostics, ...]
    source_event_count: int


@dataclass(frozen=True, slots=True)
class S1JF3AVArmObservation:
    """Compact scalar observation of one technical compatibility arm."""

    arm_id: str
    coupling_id: str
    method_ids: tuple[str, ...]
    field_neuron_count: int
    source_event_count: int
    minimum_mass: float
    total_mass: float
    mass_deviation_linf: float
    activation_linf: float
    afterimage_linf: float
    endpoint_digest: str
    fast_state_projection_digest: str


@dataclass(frozen=True, slots=True)
class S1JF3AVCompatibility:
    """Fixed four-arm S1-J compatibility result with explicit claim limits."""

    active: S1JF3AVArmObservation
    linear_baseline: S1JF3AVArmObservation
    eta_null: S1JF3AVArmObservation
    p0: S1JF3AVArmObservation
    neutral_fast_endpoint_digest: str
    p0_matches_neutral_fast: bool
    raw_payload_retained: bool = False
    memory_claim_allowed: bool = False
    learning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


def _validate_av_field(field: SharedMCMField) -> None:
    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise S1JF3AVCompatibilityError(
            "S1-J requires one shared field with an explicit M state"
        )
    if len(field.layer.neurons) != 26:
        raise S1JF3AVCompatibilityError(
            "S1-J is bound to the current 26-neuron AV geometry"
        )
    modalities = {dock.dock_map.modality_id for dock in field.docks}
    if modalities != {"auditory", "visual"}:
        raise S1JF3AVCompatibilityError(
            "S1-J requires the separate auditory and visual docks"
        )


def advance_s1j_f3_av_sequences(
    field: SharedMCMField,
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    *,
    coupling_calculator: _CouplingCalculator = compute_mcm_f3_coupling,
    refinement: int = 1,
    coupling_stage_observer=None,
) -> S1JF3AVSequenceAdvance:
    """Advance one fixed synthetic AV interval through an allowed F3 arm."""

    _validate_av_field(field)
    if coupling_calculator not in _ALLOWED_CALCULATORS:
        raise S1JF3AVCompatibilityError(
            "S1-J permits only F3 or its fixed linear coupled baseline"
        )
    if (
        not isinstance(sequences, tuple)
        or len(sequences) != 2
        or {sequence.modality_id for sequence in sequences}
        != {"auditory", "visual"}
    ):
        raise S1JF3AVCompatibilityError(
            "S1-J requires one auditory and one visual receptor sequence"
        )
    starts = {item.field_time.window_start_tick for sequence in sequences for item in sequence.frames}
    ends = {item.field_time.window_end_tick for sequence in sequences for item in sequence.frames}
    start_tick = min(starts)
    end_tick = max(ends)
    step = MCMFieldStepTime(
        SYNTHETIC_AV_CLOCK_ID,
        start_tick,
        end_tick,
        SYNTHETIC_AV_TICKS_PER_SECOND,
    )
    handoff = handoff_receptor_completion_groups(sequences, (step,))
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
    ):
        raise S1JF3AVCompatibilityError("S1-J receptor handoff is incomplete")

    current = field
    diagnostics = []
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, current.docks)
        local_inputs = project_transient_docks_to_neuron_inputs(
            trajectory,
            current.docks,
        )
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        result = advance_mcm_f3_shared_field_transient(
            current,
            distribution,
            local_inputs,
            S1J_SUBSTRATE_CONFIG,
            S1J_AFTERIMAGE_CONFIG,
            refinement=refinement,
            _coupling_calculator=coupling_calculator,
            _coupling_stage_observer=coupling_stage_observer,
        )
        current = result.field
        diagnostics.append(result.diagnostics)
    return S1JF3AVSequenceAdvance(
        current,
        tuple(diagnostics),
        handoff.assigned_event_count,
    )


def _source_intervals():
    auditory_contact = tuple(
        -0.7 + 0.2 * index for index in range(len(SYNTHETIC_AUDITORY_CARRIER_IDS))
    )
    visual_contact = tuple(
        -0.5 + (index % 6) * 0.2
        for index in range(len(SYNTHETIC_VISUAL_CONFIG.carrier_ids))
    )
    zeros_auditory = tuple(0.0 for _ in SYNTHETIC_AUDITORY_CARRIER_IDS)
    zeros_visual = tuple(0.0 for _ in SYNTHETIC_VISUAL_CONFIG.carrier_ids)
    return (
        synthetic_av_sequences(
            "s1j.contact",
            0,
            S1J_SUPPORT_TICKS,
            auditory_contact,
            visual_contact,
        ),
        synthetic_av_sequences(
            "s1j.null",
            S1J_SUPPORT_TICKS,
            2 * S1J_SUPPORT_TICKS,
            zeros_auditory,
            zeros_visual,
        ),
    )


def _run_arm(
    arm: MCMSubstrateArmContract,
    coupling_calculator: _CouplingCalculator,
) -> tuple[SharedMCMField, tuple[MCMF3AdvanceDiagnostics, ...], int]:
    intervals = _source_intervals()
    base = build_synthetic_av_field(intervals[0])
    current = (
        attach_uniform_mcm_substrate(base, arm)
        if arm.is_null_arm
        else activate_mcm_f3_field(base, arm)
    )
    diagnostics = []
    source_event_count = 0
    for sequences in intervals:
        advanced = advance_s1j_f3_av_sequences(
            current,
            sequences,
            coupling_calculator=coupling_calculator,
        )
        current = advanced.field
        diagnostics.extend(advanced.diagnostics)
        source_event_count += advanced.source_event_count
    return current, tuple(diagnostics), source_event_count


def _observation(
    arm_id: str,
    coupling_id: str,
    field: SharedMCMField,
    diagnostics: tuple[MCMF3AdvanceDiagnostics, ...],
    source_event_count: int,
) -> S1JF3AVArmObservation:
    if field.substrate is None:
        raise S1JF3AVCompatibilityError("S1-J observation lost the M state")
    masses = tuple(item.mass for item in field.substrate.masses)
    neutral = field.substrate.arm.initial_total_mass / len(masses)
    snapshot = field.snapshot()
    return S1JF3AVArmObservation(
        arm_id=arm_id,
        coupling_id=coupling_id,
        method_ids=tuple(item.method_id for item in diagnostics),
        field_neuron_count=len(field.layer.neurons),
        source_event_count=source_event_count,
        minimum_mass=min(masses),
        total_mass=math.fsum(masses),
        mass_deviation_linf=max(abs(value - neutral) for value in masses),
        activation_linf=max(abs(value) for value in snapshot.activation),
        afterimage_linf=max(abs(value) for value in snapshot.afterimage),
        endpoint_digest=snapshot.digest(),
        fast_state_projection_digest=snapshot.fast_state_projection_digest(),
    )


def _run_neutral_fast_endpoint_digest() -> str:
    intervals = _source_intervals()
    current = build_synthetic_av_field(intervals[0])
    for sequences in intervals:
        start_tick = sequences[0].frames[0].field_time.window_start_tick
        end_tick = sequences[0].frames[-1].field_time.window_end_tick
        run = run_neutral_asynchronous_field(
            current,
            sequences,
            (
                MCMFieldStepTime(
                    SYNTHETIC_AV_CLOCK_ID,
                    start_tick,
                    end_tick,
                    SYNTHETIC_AV_TICKS_PER_SECOND,
                ),
            ),
            S1J_SUBSTRATE_CONFIG,
            afterimage_config=S1J_AFTERIMAGE_CONFIG,
        )
        current = run.field
    return current.snapshot().digest()


def run_s1j_f3_av_compatibility() -> S1JF3AVCompatibility:
    """Run only the fixed technical four-arm S1-J compatibility matrix."""

    active = _run_arm(S1J_ACTIVE_ARM, compute_mcm_f3_coupling)
    linear = _run_arm(
        S1J_ACTIVE_ARM,
        compute_mcm_f3_linear_coupled_baseline,
    )
    eta_null = _run_arm(S1J_ETA_NULL_ARM, compute_mcm_f3_coupling)
    p0 = _run_arm(S1J_P0_ARM, compute_mcm_f3_coupling)
    neutral_digest = _run_neutral_fast_endpoint_digest()
    p0_observation = _observation(
        S1J_P0_ARM.arm_id,
        "p0-exact",
        *p0,
    )
    return S1JF3AVCompatibility(
        active=_observation(S1J_ACTIVE_ARM.arm_id, "f3", *active),
        linear_baseline=_observation(
            S1J_ACTIVE_ARM.arm_id,
            "linear-coupled-field",
            *linear,
        ),
        eta_null=_observation(
            S1J_ETA_NULL_ARM.arm_id,
            "f3-eta-null",
            *eta_null,
        ),
        p0=p0_observation,
        neutral_fast_endpoint_digest=neutral_digest,
        p0_matches_neutral_fast=(
            p0_observation.fast_state_projection_digest == neutral_digest
        ),
    )


def s1j_f3_av_compatibility_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            S1JF3AVSequenceAdvance,
            S1JF3AVArmObservation,
            S1JF3AVCompatibility,
        )
        for item in fields(cls)
    )
