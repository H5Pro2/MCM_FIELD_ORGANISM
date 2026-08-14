"""Preregistered P2 causal history comparison for the F3 substrate."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields, replace
import math

import numpy as np

from .controlled_audio_video_test_world import controlled_history_holdout_world_family
from .field_step_time import MCMFieldStepTime
from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .mcm_f3_controlled_history_source import (
    MCMF3ControlledHistoryInputs,
    build_mcm_f3_controlled_history_inputs,
)
from .mcm_f3_runtime import (
    MCMF3AdvanceDiagnostics,
    activate_mcm_f3_field,
    advance_mcm_f3_shared_field_transient,
)
from .mcm_substrate_state import (
    MCMSubstrateArmContract,
    MCMSubstrateState,
    build_uniform_mcm_substrate,
)
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
    build_shared_mcm_field,
)
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class MCMF3HistoryRunError(ValueError):
    """Raised when the fixed P2 history comparison loses a causal control."""


@dataclass(frozen=True, slots=True)
class MCMF3HistoryPreregistration:
    preregistration_id: str
    same_world_digest: str
    changed_world_digest: str
    same_history_digest: str
    changed_history_digest: str
    shared_probe_digest: str
    active_arm: MCMSubstrateArmContract
    refinement: int
    history_interval: tuple[int, int]
    probe_interval: tuple[int, int]
    intervention_ids: tuple[str, ...]
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


@dataclass(frozen=True, slots=True)
class MCMF3HistoryArmMeasurement:
    arm_id: str
    snapshot_digest: str
    activation_digest: str
    afterimage_digest: str
    mass_digest: str
    maximum_mass_error: float
    minimum_mass: float
    substep_count: int


@dataclass(frozen=True, slots=True)
class MCMF3HistoryRunResult:
    run_id: str
    preregistration_id: str
    same_history_digest: str
    changed_history_digest: str
    shared_probe_digest: str
    history_support_counts: tuple[int, int]
    probe_support_count: int
    history_mass_linf: float
    history_mass_l2: float
    fast_alignment_exact: bool
    natural_activation_linf: float
    natural_afterimage_linf: float
    neutral_activation_linf: float
    neutral_afterimage_linf: float
    eta_null_activation_linf: float
    eta_null_afterimage_linf: float
    p0_activation_linf: float
    p0_afterimage_linf: float
    swap_same_matches_natural_changed: bool
    swap_changed_matches_natural_same: bool
    controls: tuple[tuple[str, bool], ...]
    decision: str
    arms: tuple[MCMF3HistoryArmMeasurement, ...]
    raw_payload_retained: bool = False
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


def mcm_f3_history_preregistration() -> MCMF3HistoryPreregistration:
    return MCMF3HistoryPreregistration(
        preregistration_id="mcm.f3.p2.controlled-history.v1",
        same_world_digest="3b410299a1f0e23a4bbb45578a538878a481ec31e5ae025f0b0311074a1c0b06",
        changed_world_digest="a4009b3e1845b46169d07bd1bb1b088d3a5dbf48107776e290cd4543d1b85d3c",
        same_history_digest="997f318cf5f43f84a9747fcd5b95e3fe4cbfce68d3d5f851f22895d70504002d",
        changed_history_digest="a263b21d6fefa93389d494cb7d298910caa6f5cfea882aacc74cfb4da4cfba53",
        shared_probe_digest="dba4ae9b51af783ec4abe195eacaac98be94380f1e7125d6cf56f154a15cc927",
        active_arm=MCMSubstrateArmContract("p1.active", 1.0, 0.5, 1.0),
        refinement=4,
        history_interval=(0, 3_000_000),
        probe_interval=(3_000_000, 4_000_000),
        intervention_ids=("natural", "m-neutral", "eta-null", "m-swapped", "p0"),
    )


def align_mcm_f3_fast_state(field: SharedMCMField) -> SharedMCMField:
    """Observer intervention: set only S and H to the shared zero reference."""

    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise MCMF3HistoryRunError("fast alignment requires one substrate field")
    return replace(
        field,
        layer=replace(
            field.layer,
            neurons=tuple(
                replace(neuron, activation=0.0, afterimage=0.0)
                for neuron in field.layer.neurons
            ),
        ),
    )


def neutralize_mcm_f3_mass(field: SharedMCMField) -> SharedMCMField:
    """Observer intervention: restore uniform M without changing S or H."""

    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise MCMF3HistoryRunError("M neutralization requires one substrate field")
    return replace(
        field,
        substrate=build_uniform_mcm_substrate(field.layer, field.substrate.arm),
    )


def transfer_mcm_f3_mass(
    target: SharedMCMField,
    source: SharedMCMField,
) -> SharedMCMField:
    """Observer intervention: transfer the complete M vector between geometries."""

    if (
        not isinstance(target, SharedMCMField)
        or not isinstance(source, SharedMCMField)
        or target.substrate is None
        or source.substrate is None
    ):
        raise MCMF3HistoryRunError("M transfer requires two substrate fields")
    if (
        target.substrate.neuron_ids != source.substrate.neuron_ids
        or target.substrate.edge_inventory_digest
        != source.substrate.edge_inventory_digest
        or target.substrate.arm.initial_total_mass
        != source.substrate.arm.initial_total_mass
    ):
        raise MCMF3HistoryRunError("M transfer geometries or budgets differ")
    return replace(
        target,
        substrate=MCMSubstrateState(
            target.substrate.arm,
            source.substrate.masses,
            target.substrate.edge_inventory_digest,
        ),
    )


def ablate_mcm_f3_eta(field: SharedMCMField) -> SharedMCMField:
    """Observer intervention: retain M and set only its probe backreaction to zero."""

    if not isinstance(field, SharedMCMField) or field.substrate is None:
        raise MCMF3HistoryRunError("eta ablation requires one substrate field")
    arm = field.substrate.arm
    eta_null = MCMSubstrateArmContract(
        "p2.eta-null",
        arm.lambda_sm_per_second,
        arm.kappa,
        0.0,
        arm.initial_total_mass,
    )
    return replace(
        field,
        substrate=MCMSubstrateState(
            eta_null,
            field.substrate.masses,
            field.substrate.edge_inventory_digest,
        ),
    )


def _steps(
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    interval: tuple[int, int],
    ticks_per_second: float,
):
    del sequences
    return (
        MCMFieldStepTime(
            "organism.mcm_f3_history",
            interval[0],
            interval[1],
            ticks_per_second,
        ),
    )


def _advance_sequences(
    field: SharedMCMField,
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence],
    interval: tuple[int, int],
    ticks_per_second: float,
    refinement: int,
) -> tuple[SharedMCMField, tuple[MCMF3AdvanceDiagnostics, ...], int]:
    steps = _steps(sequences, interval, ticks_per_second)
    handoff = handoff_receptor_completion_groups(sequences, steps)
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
    ):
        raise MCMF3HistoryRunError("history handoff is incomplete")
    current = field
    diagnostics = []
    substrate_config = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage_config = NeutralFastAfterimageConfig(0.5)
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
        advanced = advance_mcm_f3_shared_field_transient(
            current,
            distribution,
            local_inputs,
            substrate_config,
            afterimage_config,
            refinement=refinement,
        )
        current = advanced.field
        diagnostics.append(advanced.diagnostics)
    return current, tuple(diagnostics), handoff.assigned_event_count


def _vectors(field: SharedMCMField) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if field.substrate is None:
        raise MCMF3HistoryRunError("measurement requires M")
    return (
        np.asarray([item.activation for item in field.layer.neurons]),
        np.asarray([item.afterimage for item in field.layer.neurons]),
        np.asarray([item.mass for item in field.substrate.masses]),
    )


def _digest(vector: np.ndarray) -> str:
    import hashlib

    return hashlib.sha256(np.asarray(vector, dtype=np.float64).tobytes()).hexdigest()


def _linf(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.max(np.abs(left - right)))


def _same_state(left: SharedMCMField, right: SharedMCMField) -> bool:
    return all(
        np.array_equal(a, b)
        for a, b in zip(_vectors(left), _vectors(right), strict=True)
    )


def _arm_measurement(
    arm_id: str,
    field: SharedMCMField,
    diagnostics: tuple[MCMF3AdvanceDiagnostics, ...],
) -> MCMF3HistoryArmMeasurement:
    activation, afterimage, mass = _vectors(field)
    return MCMF3HistoryArmMeasurement(
        arm_id,
        field.snapshot().digest(),
        _digest(activation),
        _digest(afterimage),
        _digest(mass),
        max(item.maximum_mass_error for item in diagnostics),
        float(np.min(mass)),
        sum(item.substep_count for item in diagnostics),
    )


def _validate_inputs(
    inputs: MCMF3ControlledHistoryInputs,
    plan: MCMF3HistoryPreregistration,
) -> None:
    observed = (
        inputs.same_world_digest,
        inputs.changed_world_digest,
        inputs.same_history_digest,
        inputs.changed_history_digest,
        inputs.shared_probe_digest,
    )
    expected = (
        plan.same_world_digest,
        plan.changed_world_digest,
        plan.same_history_digest,
        plan.changed_history_digest,
        plan.shared_probe_digest,
    )
    if observed != expected:
        raise MCMF3HistoryRunError("controlled P2 inputs differ from preregistration")


def execute_mcm_f3_history_run() -> MCMF3HistoryRunResult:
    """Execute the fixed P2 history comparison exactly as preregistered."""

    plan = mcm_f3_history_preregistration()
    inputs = build_mcm_f3_controlled_history_inputs()
    _validate_inputs(inputs, plan)
    same_world, _ = controlled_history_holdout_world_family()
    reference = tuple(item.frames[0].frame for item in inputs.same_history)
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference[0].carrier_ids),
        visual_grid_columns=same_world.visual_config.grid_columns,
        visual_grid_rows=same_world.visual_config.grid_rows,
    )
    base = build_shared_mcm_field(
        reference,
        anatomies,
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    active_same, active_same_diagnostics, same_supports = _advance_sequences(
        activate_mcm_f3_field(base, plan.active_arm),
        inputs.same_history,
        plan.history_interval,
        inputs.ticks_per_second,
        plan.refinement,
    )
    active_changed, active_changed_diagnostics, changed_supports = _advance_sequences(
        activate_mcm_f3_field(base, plan.active_arm),
        inputs.changed_history,
        plan.history_interval,
        inputs.ticks_per_second,
        plan.refinement,
    )
    p0_arm = MCMSubstrateArmContract("p0.null", 0.0, 0.5, 1.0)
    p0_same, _, _ = _advance_sequences(
        attach_uniform_mcm_substrate(base, p0_arm),
        inputs.same_history,
        plan.history_interval,
        inputs.ticks_per_second,
        1,
    )
    p0_changed, _, _ = _advance_sequences(
        attach_uniform_mcm_substrate(base, p0_arm),
        inputs.changed_history,
        plan.history_interval,
        inputs.ticks_per_second,
        1,
    )

    aligned_same = align_mcm_f3_fast_state(active_same)
    aligned_changed = align_mcm_f3_fast_state(active_changed)
    aligned_p0_same = align_mcm_f3_fast_state(p0_same)
    aligned_p0_changed = align_mcm_f3_fast_state(p0_changed)
    fast_alignment_exact = all(
        np.array_equal(left, right)
        for left, right in zip(
            _vectors(aligned_same)[:2],
            _vectors(aligned_changed)[:2],
            strict=True,
        )
    )

    starts = {
        "natural.same": aligned_same,
        "natural.changed": aligned_changed,
        "m-neutral.same": neutralize_mcm_f3_mass(aligned_same),
        "m-neutral.changed": neutralize_mcm_f3_mass(aligned_changed),
        "eta-null.same": ablate_mcm_f3_eta(aligned_same),
        "eta-null.changed": ablate_mcm_f3_eta(aligned_changed),
        "m-swapped.same": transfer_mcm_f3_mass(aligned_same, aligned_changed),
        "m-swapped.changed": transfer_mcm_f3_mass(aligned_changed, aligned_same),
        "p0.same": aligned_p0_same,
        "p0.changed": aligned_p0_changed,
    }
    completed = {}
    diagnostics = {}
    probe_support_count = None
    for arm_id, start in starts.items():
        refinement = 1 if arm_id.startswith("p0.") else plan.refinement
        field, arm_diagnostics, support_count = _advance_sequences(
            start,
            inputs.shared_probe,
            plan.probe_interval,
            inputs.ticks_per_second,
            refinement,
        )
        completed[arm_id] = field
        diagnostics[arm_id] = arm_diagnostics
        if probe_support_count is None:
            probe_support_count = support_count
        elif probe_support_count != support_count:
            raise MCMF3HistoryRunError("probe support count changed between arms")

    natural_same = completed["natural.same"]
    natural_changed = completed["natural.changed"]
    natural_same_vectors = _vectors(natural_same)
    natural_changed_vectors = _vectors(natural_changed)
    history_same_mass = _vectors(active_same)[2]
    history_changed_mass = _vectors(active_changed)[2]

    neutral_s = _vectors(completed["m-neutral.same"])
    neutral_c = _vectors(completed["m-neutral.changed"])
    eta_s = _vectors(completed["eta-null.same"])
    eta_c = _vectors(completed["eta-null.changed"])
    p0_s = _vectors(completed["p0.same"])
    p0_c = _vectors(completed["p0.changed"])
    swap_same_matches = _same_state(
        completed["m-swapped.same"], natural_changed
    )
    swap_changed_matches = _same_state(
        completed["m-swapped.changed"], natural_same
    )
    controls = (
        ("history_m_differs", not np.array_equal(history_same_mass, history_changed_mass)),
        ("fast_alignment_exact", fast_alignment_exact),
        (
            "natural_probe_effect",
            not np.array_equal(natural_same_vectors[0], natural_changed_vectors[0])
            or not np.array_equal(natural_same_vectors[1], natural_changed_vectors[1]),
        ),
        (
            "m_neutral_effect_removed",
            np.array_equal(neutral_s[0], neutral_c[0])
            and np.array_equal(neutral_s[1], neutral_c[1]),
        ),
        (
            "eta_null_effect_removed",
            np.array_equal(eta_s[0], eta_c[0])
            and np.array_equal(eta_s[1], eta_c[1]),
        ),
        ("m_swap_same_matches_changed", swap_same_matches),
        ("m_swap_changed_matches_same", swap_changed_matches),
        (
            "p0_histories_collapse",
            np.array_equal(p0_s[0], p0_c[0])
            and np.array_equal(p0_s[1], p0_c[1]),
        ),
    )
    all_diagnostics = (*active_same_diagnostics, *active_changed_diagnostics)
    all_diagnostics += tuple(
        item for arm in diagnostics.values() for item in arm
    )
    invariants_hold = (
        max(item.maximum_mass_error for item in all_diagnostics) <= 1e-12
        and min(item.minimum_mass for item in all_diagnostics) >= 0.0
        and all(math.isfinite(item.maximum_abs_activation) for item in all_diagnostics)
        and all(math.isfinite(item.maximum_abs_afterimage) for item in all_diagnostics)
    )
    controls += (("state_invariants_hold", invariants_hold),)
    decision = (
        "CAUSAL_M_HISTORY_CARRIER"
        if all(value for _, value in controls)
        else (
            "NO_CAUSAL_M_HISTORY_EFFECT"
            if not dict(controls)["natural_probe_effect"]
            else "TECHNICALLY_UNDECIDABLE"
        )
    )

    arm_measurements = tuple(
        _arm_measurement(arm_id, completed[arm_id], diagnostics[arm_id])
        for arm_id in starts
    )
    return MCMF3HistoryRunResult(
        run_id="lauf.189.mcm.f3.p2.controlled-history.v1",
        preregistration_id=plan.preregistration_id,
        same_history_digest=inputs.same_history_digest,
        changed_history_digest=inputs.changed_history_digest,
        shared_probe_digest=inputs.shared_probe_digest,
        history_support_counts=(same_supports, changed_supports),
        probe_support_count=probe_support_count or 0,
        history_mass_linf=_linf(history_same_mass, history_changed_mass),
        history_mass_l2=float(np.linalg.norm(history_same_mass - history_changed_mass)),
        fast_alignment_exact=fast_alignment_exact,
        natural_activation_linf=_linf(natural_same_vectors[0], natural_changed_vectors[0]),
        natural_afterimage_linf=_linf(natural_same_vectors[1], natural_changed_vectors[1]),
        neutral_activation_linf=_linf(neutral_s[0], neutral_c[0]),
        neutral_afterimage_linf=_linf(neutral_s[1], neutral_c[1]),
        eta_null_activation_linf=_linf(eta_s[0], eta_c[0]),
        eta_null_afterimage_linf=_linf(eta_s[1], eta_c[1]),
        p0_activation_linf=_linf(p0_s[0], p0_c[0]),
        p0_afterimage_linf=_linf(p0_s[1], p0_c[1]),
        swap_same_matches_natural_changed=swap_same_matches,
        swap_changed_matches_natural_same=swap_changed_matches,
        controls=controls,
        decision=decision,
        arms=arm_measurements,
    )


def mcm_f3_history_run_json_value(result: MCMF3HistoryRunResult) -> dict:
    if not isinstance(result, MCMF3HistoryRunResult):
        raise MCMF3HistoryRunError("P2 result type is invalid")
    return asdict(result)


def mcm_f3_history_run_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            MCMF3HistoryPreregistration,
            MCMF3HistoryArmMeasurement,
            MCMF3HistoryRunResult,
        )
        for item in fields(cls)
    )
