"""Preregistered E3 trajectory comparison against three fixed baselines."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math

import numpy as np

from .controlled_audio_video_test_world import controlled_history_holdout_world_family
from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .field_step_time import MCMFieldStepTime
from .mcm_f3_baseline_coupling import mcm_f3_e3_baseline_calculators
from .mcm_f3_controlled_history_source import build_mcm_f3_controlled_history_inputs
from .mcm_f3_coupling import compute_mcm_f3_coupling
from .mcm_f3_geometry_interventions import (
    mcm_f3_geometry_contract,
    neutralize_mcm_f3_local_mask_balanced,
    permute_mcm_f3_mass_by_geometry,
)
from .mcm_f3_history_run import (
    align_mcm_f3_fast_state,
    mcm_f3_history_preregistration,
)
from .mcm_f3_runtime import activate_mcm_f3_field, advance_mcm_f3_shared_field_transient
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff_audit import handoff_receptor_completion_groups
from .shared_mcm_field import build_shared_mcm_field
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class MCMF3E3BaselineRunError(ValueError):
    """Raised when the fixed E3 comparison loses a preregistered control."""


@dataclass(frozen=True, slots=True)
class MCMF3E3Preregistration:
    preregistration_id: str
    baseline_ids: tuple[str, ...]
    intervention_ids: tuple[str, ...]
    relative_residual_limit: float
    refinement: int
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


@dataclass(frozen=True, slots=True)
class MCMF3E3BaselineMeasurement:
    baseline_id: str
    history_activation_relative_residual: float
    history_afterimage_relative_residual: float
    probe_activation_relative_residual: float
    probe_afterimage_relative_residual: float
    maximum_effect_relative_residual: float
    minimum_effect_scale: float
    observation_ticks_match: bool
    effects_present: bool
    invariants_hold: bool
    explains_effect: bool


@dataclass(frozen=True, slots=True)
class MCMF3E3BaselineRunResult:
    run_id: str
    preregistration_id: str
    same_history_digest: str
    changed_history_digest: str
    shared_probe_digest: str
    measurements: tuple[MCMF3E3BaselineMeasurement, ...]
    decision: str
    raw_payload_retained: bool = False
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


@dataclass(frozen=True, slots=True)
class _Sample:
    tick: int
    activation: np.ndarray
    afterimage: np.ndarray


def mcm_f3_e3_preregistration() -> MCMF3E3Preregistration:
    return MCMF3E3Preregistration(
        "mcm.f3.e3.fixed-baselines.v1",
        tuple(name for name, _ in mcm_f3_e3_baseline_calculators()),
        ("natural", "reflected", "neutral-left", "neutral-right"),
        0.05,
        4,
    )


def _advance_observed(field, sequences, interval, ticks_per_second, refinement, calculator):
    handoff = handoff_receptor_completion_groups(
        sequences,
        (
            MCMFieldStepTime(
                sequences[0].clock_id,
                interval[0],
                interval[1],
                ticks_per_second,
            ),
        ),
    )
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
    ):
        raise MCMF3E3BaselineRunError("E3 source handoff is incomplete")
    current = field
    diagnostics = []
    samples = []

    def observe(tick, activation, afterimage, mass):
        del mass
        samples.append(_Sample(tick, activation, afterimage))

    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, current.docks)
        inputs = project_transient_docks_to_neuron_inputs(trajectory, current.docks)
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
            inputs,
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
            refinement=refinement,
            _coupling_calculator=calculator,
            _state_observer=observe,
        )
        current = result.field
        diagnostics.append(result.diagnostics)
    return current, tuple(samples), tuple(diagnostics)


def _ticks_match(left, right) -> bool:
    return tuple(item.tick for item in left) == tuple(item.tick for item in right)


def _component(samples, role: str) -> np.ndarray:
    return np.stack([getattr(item, role) for item in samples])


def _relative_residual(reference: np.ndarray, compared: np.ndarray) -> float:
    scale = float(np.max(np.abs(reference)))
    residual = float(np.max(np.abs(reference - compared)))
    return residual / scale if scale > 0.0 else (0.0 if residual == 0.0 else math.inf)


def _effect_metric(candidate_natural, candidate_variant, baseline_natural, baseline_variant):
    if not (
        _ticks_match(candidate_natural, candidate_variant)
        and _ticks_match(candidate_natural, baseline_natural)
        and _ticks_match(candidate_natural, baseline_variant)
    ):
        return math.inf, 0.0, False
    ratios = []
    scales = []
    present = False
    for role in ("activation", "afterimage"):
        candidate_effect = _component(candidate_natural, role) - _component(
            candidate_variant, role
        )
        baseline_effect = _component(baseline_natural, role) - _component(
            baseline_variant, role
        )
        scale = float(np.max(np.abs(candidate_effect)))
        residual = float(np.max(np.abs(candidate_effect - baseline_effect)))
        if scale > 0.0:
            ratios.append(residual / scale)
            scales.append(scale)
            present = present or bool(np.max(np.abs(baseline_effect)) > 0.0)
    return max(ratios, default=math.inf), min(scales, default=0.0), present


def execute_mcm_f3_e3_baseline_run() -> MCMF3E3BaselineRunResult:
    """Execute the fixed E3 baseline matrix once."""

    plan = mcm_f3_e3_preregistration()
    history_plan = mcm_f3_history_preregistration()
    source = build_mcm_f3_controlled_history_inputs()
    if (
        source.same_history_digest != history_plan.same_history_digest
        or source.changed_history_digest != history_plan.changed_history_digest
        or source.shared_probe_digest != history_plan.shared_probe_digest
    ):
        raise MCMF3E3BaselineRunError("E3 source digests changed")

    same_world, _ = controlled_history_holdout_world_family()
    reference = tuple(item.frames[0].frame for item in source.same_history)
    base = build_shared_mcm_field(
        reference,
        audio_video_dock_anatomies(
            auditory_carrier_count=len(reference[0].carrier_ids),
            visual_grid_columns=same_world.visual_config.grid_columns,
            visual_grid_rows=same_world.visual_config.grid_rows,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    models = (("f3-candidate", compute_mcm_f3_coupling),) + mcm_f3_e3_baseline_calculators()
    model_histories = {}
    model_history_trajectories = {}
    model_diagnostics = {}
    for model_id, calculator in models:
        for history_id, sequences in (("same", source.same_history), ("changed", source.changed_history)):
            field, trajectory, diagnostics = _advance_observed(
                activate_mcm_f3_field(base, history_plan.active_arm),
                sequences,
                history_plan.history_interval,
                source.ticks_per_second,
                plan.refinement,
                calculator,
            )
            model_histories[(model_id, history_id)] = align_mcm_f3_fast_state(field)
            model_history_trajectories[(model_id, history_id)] = trajectory
            model_diagnostics[(model_id, history_id, "history")] = diagnostics

    geometry = mcm_f3_geometry_contract(model_histories[("f3-candidate", "same")])
    probe_trajectories = {}
    for model_id, calculator in models:
        for history_id in ("same", "changed"):
            natural = model_histories[(model_id, history_id)]
            starts = {
                "natural": natural,
                "reflected": permute_mcm_f3_mass_by_geometry(natural, geometry),
                "neutral-left": neutralize_mcm_f3_local_mask_balanced(
                    natural, geometry, target_mask="left"
                ),
                "neutral-right": neutralize_mcm_f3_local_mask_balanced(
                    natural, geometry, target_mask="right"
                ),
            }
            for intervention_id, start in starts.items():
                _, trajectory, diagnostics = _advance_observed(
                    start,
                    source.shared_probe,
                    history_plan.probe_interval,
                    source.ticks_per_second,
                    plan.refinement,
                    calculator,
                )
                probe_trajectories[(model_id, history_id, intervention_id)] = trajectory
                model_diagnostics[(model_id, history_id, intervention_id)] = diagnostics

    candidate_id = "f3-candidate"
    measurements = []
    for baseline_id, _ in mcm_f3_e3_baseline_calculators():
        ticks_match = True
        history_ratios = {"activation": [], "afterimage": []}
        probe_ratios = {"activation": [], "afterimage": []}
        for history_id in ("same", "changed"):
            candidate = model_history_trajectories[(candidate_id, history_id)]
            baseline = model_history_trajectories[(baseline_id, history_id)]
            ticks_match = ticks_match and _ticks_match(candidate, baseline)
            for role in history_ratios:
                history_ratios[role].append(
                    _relative_residual(_component(candidate, role), _component(baseline, role))
                )
            for intervention_id in plan.intervention_ids:
                candidate_probe = probe_trajectories[(candidate_id, history_id, intervention_id)]
                baseline_probe = probe_trajectories[(baseline_id, history_id, intervention_id)]
                ticks_match = ticks_match and _ticks_match(candidate_probe, baseline_probe)
                for role in probe_ratios:
                    probe_ratios[role].append(
                        _relative_residual(
                            _component(candidate_probe, role),
                            _component(baseline_probe, role),
                        )
                    )

        effect_ratios = []
        effect_scales = []
        effects_present = True
        for history_id in ("same", "changed"):
            for intervention_id in ("reflected", "neutral-left", "neutral-right"):
                ratio, scale, present = _effect_metric(
                    probe_trajectories[(candidate_id, history_id, "natural")],
                    probe_trajectories[(candidate_id, history_id, intervention_id)],
                    probe_trajectories[(baseline_id, history_id, "natural")],
                    probe_trajectories[(baseline_id, history_id, intervention_id)],
                )
                effect_ratios.append(ratio)
                effect_scales.append(scale)
                effects_present = effects_present and present
        ratio, scale, present = _effect_metric(
            probe_trajectories[(candidate_id, "same", "natural")],
            probe_trajectories[(candidate_id, "changed", "natural")],
            probe_trajectories[(baseline_id, "same", "natural")],
            probe_trajectories[(baseline_id, "changed", "natural")],
        )
        effect_ratios.append(ratio)
        effect_scales.append(scale)
        effects_present = effects_present and present

        diagnostics = tuple(
            item
            for key, values in model_diagnostics.items()
            if key[0] == baseline_id
            for item in values
        )
        invariants = (
            max(item.maximum_mass_error for item in diagnostics) <= 1e-12
            and min(item.minimum_mass for item in diagnostics) >= 0.0
        )
        maximum_effect_ratio = max(effect_ratios)
        explains = (
            ticks_match
            and effects_present
            and invariants
            and maximum_effect_ratio <= plan.relative_residual_limit
        )
        measurements.append(
            MCMF3E3BaselineMeasurement(
                baseline_id,
                max(history_ratios["activation"]),
                max(history_ratios["afterimage"]),
                max(probe_ratios["activation"]),
                max(probe_ratios["afterimage"]),
                maximum_effect_ratio,
                min(effect_scales),
                ticks_match,
                effects_present,
                invariants,
                explains,
            )
        )

    decision = (
        "E3_EXPLAINED_BY_NARROW_BASELINE"
        if any(item.explains_effect for item in measurements)
        else (
            "TECHNICALLY_UNDECIDABLE"
            if not all(item.observation_ticks_match and item.invariants_hold for item in measurements)
            else "E3_RESIDUAL_REQUIRES_MORE_BASELINES"
        )
    )
    return MCMF3E3BaselineRunResult(
        "lauf.192.mcm.f3.e3.fixed-baselines.v1",
        plan.preregistration_id,
        source.same_history_digest,
        source.changed_history_digest,
        source.shared_probe_digest,
        tuple(measurements),
        decision,
    )


def mcm_f3_e3_baseline_run_json_value(result: MCMF3E3BaselineRunResult) -> dict:
    if not isinstance(result, MCMF3E3BaselineRunResult):
        raise MCMF3E3BaselineRunError("E3 result type is invalid")
    return asdict(result)


def mcm_f3_e3_baseline_run_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (MCMF3E3Preregistration, MCMF3E3BaselineMeasurement, MCMF3E3BaselineRunResult)
        for item in fields(cls)
    )
