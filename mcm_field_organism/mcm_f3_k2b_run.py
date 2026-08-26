"""Preregistered K2-B characterization of F3 loss and state reuse."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math

import numpy as np

from .controlled_audio_video_test_world import controlled_history_holdout_world_family
from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .mcm_f3_baseline_coupling import compute_mcm_f3_linear_coupled_baseline
from .mcm_f3_coupling import compute_mcm_f3_coupling
from .mcm_f3_e3_baseline_run import _advance_observed, _component, _ticks_match
from .mcm_f3_history_run import _vectors, align_mcm_f3_fast_state, mcm_f3_history_preregistration
from .mcm_f3_k2b_source import build_mcm_f3_k2b_source
from .mcm_f3_runtime import activate_mcm_f3_field
from .shared_mcm_field import build_shared_mcm_field


class MCMF3K2BRunError(ValueError):
    """Raised when the fixed K2-B characterization loses a control."""


@dataclass(frozen=True, slots=True)
class MCMF3K2BPreregistration:
    preregistration_id: str
    model_ids: tuple[str, ...]
    checkpoint_count: int
    functional_loss_limit: float
    competitive_advantage_factor: float
    numerical_effect_floor: float
    refinement: int
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


@dataclass(frozen=True, slots=True)
class MCMF3K2BCheckpointMeasurement:
    model_id: str
    checkpoint: int
    old_b_fast_linf: float
    old_gap_fast_linf: float
    new_b_fast_linf: float
    old_b_mass_linf: float
    old_gap_mass_linf: float
    new_b_mass_linf: float
    old_b_retention: float
    old_gap_retention: float
    observation_ticks_match: bool


@dataclass(frozen=True, slots=True)
class MCMF3K2BRunResult:
    run_id: str
    preregistration_id: str
    contact_a_digest: str
    contact_b_step_digests: tuple[str, ...]
    interruption_step_digests: tuple[str, ...]
    probe_digests: tuple[str, ...]
    checkpoints: tuple[MCMF3K2BCheckpointMeasurement, ...]
    linear_curve_relative_residual: float
    controls: tuple[tuple[str, bool], ...]
    decision: str
    raw_payload_retained: bool = False
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


def mcm_f3_k2b_preregistration() -> MCMF3K2BPreregistration:
    return MCMF3K2BPreregistration(
        "mcm.f3.k2b.loss-reuse.v1",
        ("f3-candidate", "linear-coupled-field"),
        5,
        0.05,
        0.50,
        4.2090677451738585e-09,
        4,
    )


def _fast_contrast(left, right):
    if not _ticks_match(left, right):
        return math.inf, False
    return max(
        float(np.max(np.abs(_component(left, role) - _component(right, role))))
        for role in ("activation", "afterimage")
    ), True


def _mass_linf(left, right) -> float:
    return float(np.max(np.abs(_vectors(left)[2] - _vectors(right)[2])))


def _advance(field, sequences, interval, source, plan, calculator):
    result, _, diagnostics = _advance_observed(
        field,
        sequences,
        interval,
        source.ticks_per_second,
        plan.refinement,
        calculator,
    )
    return result, diagnostics


def _probe(field, sequences, interval, source, plan, calculator):
    _, trajectory, diagnostics = _advance_observed(
        align_mcm_f3_fast_state(field),
        sequences,
        interval,
        source.ticks_per_second,
        plan.refinement,
        calculator,
    )
    return trajectory, diagnostics


def execute_mcm_f3_k2b_run() -> MCMF3K2BRunResult:
    """Execute the fixed K2-B functional characterization once."""

    plan = mcm_f3_k2b_preregistration()
    source = build_mcm_f3_k2b_source()
    history_plan = mcm_f3_history_preregistration()
    same_world, _ = controlled_history_holdout_world_family()
    reference = tuple(item.frames[0].frame for item in source.contact_a)
    base = build_shared_mcm_field(
        reference,
        audio_video_dock_anatomies(
            auditory_carrier_count=len(reference[0].carrier_ids),
            visual_grid_columns=same_world.visual_config.grid_columns,
            visual_grid_rows=same_world.visual_config.grid_rows,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    models = (
        ("f3-candidate", compute_mcm_f3_coupling),
        ("linear-coupled-field", compute_mcm_f3_linear_coupled_baseline),
    )
    measurements = []
    all_diagnostics = []
    for model_id, calculator in models:
        uniform = activate_mcm_f3_field(base, history_plan.active_arm)
        a_field, diagnostics = _advance(
            uniform,
            source.contact_a,
            (0, 4_000_000),
            source,
            plan,
            calculator,
        )
        all_diagnostics.extend(diagnostics)
        ab = align_mcm_f3_fast_state(a_field)
        ag = ab
        ub = uniform
        ug = uniform
        initial_old_contrast = None

        for checkpoint in range(plan.checkpoint_count):
            if checkpoint > 0:
                interval = (
                    (3 + checkpoint) * 1_000_000,
                    (4 + checkpoint) * 1_000_000,
                )
                step_index = checkpoint - 1
                ab, diagnostics = _advance(
                    ab,
                    source.contact_b_steps[step_index],
                    interval,
                    source,
                    plan,
                    calculator,
                )
                all_diagnostics.extend(diagnostics)
                ub, diagnostics = _advance(
                    ub,
                    source.contact_b_steps[step_index],
                    interval,
                    source,
                    plan,
                    calculator,
                )
                all_diagnostics.extend(diagnostics)
                ag, diagnostics = _advance(
                    ag,
                    source.interruption_steps[step_index],
                    interval,
                    source,
                    plan,
                    calculator,
                )
                all_diagnostics.extend(diagnostics)
                ug, diagnostics = _advance(
                    ug,
                    source.interruption_steps[step_index],
                    interval,
                    source,
                    plan,
                    calculator,
                )
                all_diagnostics.extend(diagnostics)

            probe_interval = (
                (4 + checkpoint) * 1_000_000,
                (5 + checkpoint) * 1_000_000,
            )
            trajectories = {}
            for arm_id, field in (("ab", ab), ("ub", ub), ("ag", ag), ("ug", ug)):
                trajectory, diagnostics = _probe(
                    field,
                    source.probes[checkpoint],
                    probe_interval,
                    source,
                    plan,
                    calculator,
                )
                trajectories[arm_id] = trajectory
                all_diagnostics.extend(diagnostics)

            old_b, old_b_ticks = _fast_contrast(trajectories["ab"], trajectories["ub"])
            old_gap, old_gap_ticks = _fast_contrast(trajectories["ag"], trajectories["ug"])
            new_b, new_b_ticks = _fast_contrast(trajectories["ub"], trajectories["ug"])
            if initial_old_contrast is None:
                initial_old_contrast = old_b
            if initial_old_contrast <= 0.0 or not math.isfinite(initial_old_contrast):
                raise MCMF3K2BRunError("K2-B initial A contrast is not measurable")
            measurements.append(
                MCMF3K2BCheckpointMeasurement(
                    model_id,
                    checkpoint,
                    old_b,
                    old_gap,
                    new_b,
                    _mass_linf(ab, ub),
                    _mass_linf(ag, ug),
                    _mass_linf(ub, ug),
                    old_b / initial_old_contrast,
                    old_gap / initial_old_contrast,
                    old_b_ticks and old_gap_ticks and new_b_ticks,
                )
            )

    candidate = tuple(item for item in measurements if item.model_id == "f3-candidate")
    baseline = tuple(
        item for item in measurements if item.model_id == "linear-coupled-field"
    )
    candidate_curve = np.asarray(
        [
            value
            for item in candidate
            for value in (item.old_b_fast_linf, item.old_gap_fast_linf, item.new_b_fast_linf)
        ]
    )
    baseline_curve = np.asarray(
        [
            value
            for item in baseline
            for value in (item.old_b_fast_linf, item.old_gap_fast_linf, item.new_b_fast_linf)
        ]
    )
    curve_scale = float(np.max(np.abs(candidate_curve)))
    linear_residual = float(np.max(np.abs(candidate_curve - baseline_curve))) / curve_scale
    invariants_hold = (
        max(item.maximum_mass_error for item in all_diagnostics) <= 1e-12
        and min(item.minimum_mass for item in all_diagnostics) >= 0.0
        and all(math.isfinite(item.maximum_abs_activation) for item in all_diagnostics)
        and all(math.isfinite(item.maximum_abs_afterimage) for item in all_diagnostics)
    )
    ticks_match = all(item.observation_ticks_match for item in measurements)
    final = candidate[-1]
    reusable_b = final.new_b_fast_linf > plan.numerical_effect_floor
    functional_loss = final.old_b_retention <= plan.functional_loss_limit
    competitive = (
        functional_loss
        and final.old_b_retention
        <= plan.competitive_advantage_factor * final.old_gap_retention
    )
    controls = (
        ("source_digests_fixed", True),
        ("observation_ticks_match", ticks_match),
        ("state_invariants_hold", invariants_hold),
        ("initial_a_effect_present", candidate[0].old_b_fast_linf > plan.numerical_effect_floor),
        ("final_b_effect_present", reusable_b),
    )
    if not all(value for key, value in controls if key != "final_b_effect_present"):
        decision = "TECHNICALLY_UNDECIDABLE"
    elif not reusable_b:
        decision = "NO_REUSABLE_B_EFFECT"
    elif competitive:
        decision = "COMPETITIVE_DISPLACEMENT_AND_REUSE"
    elif functional_loss:
        decision = "PASSIVE_LOSS_AND_REUSE"
    else:
        decision = "SUPERPOSITION_WITHOUT_FUNCTIONAL_LOSS"
    return MCMF3K2BRunResult(
        "lauf.194.mcm.f3.k2b.loss-reuse.corrected.v1",
        plan.preregistration_id,
        source.contact_a_digest,
        source.contact_b_step_digests,
        source.interruption_step_digests,
        source.probe_digests,
        tuple(measurements),
        linear_residual,
        controls,
        decision,
    )


def mcm_f3_k2b_run_json_value(result: MCMF3K2BRunResult) -> dict:
    if not isinstance(result, MCMF3K2BRunResult):
        raise MCMF3K2BRunError("K2-B result type is invalid")
    return asdict(result)


def mcm_f3_k2b_run_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            MCMF3K2BPreregistration,
            MCMF3K2BCheckpointMeasurement,
            MCMF3K2BRunResult,
        )
        for item in fields(cls)
    )
