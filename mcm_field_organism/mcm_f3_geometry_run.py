"""Preregistered E2 comparison of M assignment to fixed field geometry."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math

import numpy as np

from .controlled_audio_video_test_world import controlled_history_holdout_world_family
from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .mcm_f3_controlled_history_source import build_mcm_f3_controlled_history_inputs
from .mcm_f3_geometry_interventions import (
    MCMF3GeometryContract,
    mcm_f3_geometry_contract,
    neutralize_mcm_f3_local_mask_balanced,
    permute_mcm_f3_mass_by_geometry,
)
from .mcm_f3_history_run import (
    _advance_sequences,
    _vectors,
    ablate_mcm_f3_eta,
    align_mcm_f3_fast_state,
    mcm_f3_history_preregistration,
)
from .mcm_f3_runtime import activate_mcm_f3_field
from .shared_mcm_field import SharedMCMField, build_shared_mcm_field


class MCMF3GeometryRunError(ValueError):
    """Raised when the fixed E2 comparison loses a geometry control."""


@dataclass(frozen=True, slots=True)
class MCMF3GeometryPreregistration:
    preregistration_id: str
    reflection_digest: str
    left_mask_digest: str
    right_mask_digest: str
    reflection_pair_count: int
    mask_size: int
    refinement: int
    arm_suffixes: tuple[str, ...]
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


@dataclass(frozen=True, slots=True)
class MCMF3GeometryArmMeasurement:
    arm_id: str
    snapshot_digest: str
    activation_digest: str
    afterimage_digest: str
    mass_digest: str
    maximum_mass_error: float
    minimum_mass: float


@dataclass(frozen=True, slots=True)
class MCMF3GeometryHistoryMeasurement:
    history_id: str
    reflection_mass_linf: float
    reflected_activation_linf: float
    reflected_afterimage_linf: float
    left_activation_linf: float
    left_afterimage_linf: float
    right_activation_linf: float
    right_afterimage_linf: float
    left_right_activation_linf: float
    left_right_afterimage_linf: float
    eta_null_activation_linf: float
    eta_null_afterimage_linf: float


@dataclass(frozen=True, slots=True)
class MCMF3GeometryRunResult:
    run_id: str
    preregistration_id: str
    shared_probe_digest: str
    reflection_digest: str
    left_mask_digest: str
    right_mask_digest: str
    histories: tuple[MCMF3GeometryHistoryMeasurement, ...]
    arms: tuple[MCMF3GeometryArmMeasurement, ...]
    controls: tuple[tuple[str, bool], ...]
    decision: str
    raw_payload_retained: bool = False
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


_REFLECTION_DIGEST = "603db647df0717d7c94747e90f98dd907717e08f9830e23c5aa038e4d82d2ffb"
_LEFT_MASK_DIGEST = "c6221c5edee311f8795bdda1de10a30828e5a712e0355d29c1f4faf614217a24"
_RIGHT_MASK_DIGEST = "77485ba0a8cd50f54bc83b6e0d00459c5935fb0e346ed95e27a799af5ca9d8d5"
_ARM_SUFFIXES = (
    "natural",
    "reflected",
    "neutral-left",
    "neutral-right",
    "eta-null-natural",
    "eta-null-reflected",
)


def mcm_f3_geometry_preregistration() -> MCMF3GeometryPreregistration:
    return MCMF3GeometryPreregistration(
        "mcm.f3.e2.geometry.v1",
        _REFLECTION_DIGEST,
        _LEFT_MASK_DIGEST,
        _RIGHT_MASK_DIGEST,
        84,
        36,
        4,
        _ARM_SUFFIXES,
    )


def _digest(vector: np.ndarray) -> str:
    import hashlib

    return hashlib.sha256(np.asarray(vector, dtype=np.float64).tobytes()).hexdigest()


def _linf(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.max(np.abs(left - right)))


def _same_fast(left: SharedMCMField, right: SharedMCMField) -> bool:
    left_vectors = _vectors(left)
    right_vectors = _vectors(right)
    return np.array_equal(left_vectors[0], right_vectors[0]) and np.array_equal(
        left_vectors[1], right_vectors[1]
    )


def _measure_arm(arm_id, field, diagnostics) -> MCMF3GeometryArmMeasurement:
    activation, afterimage, mass = _vectors(field)
    return MCMF3GeometryArmMeasurement(
        arm_id,
        field.snapshot().digest(),
        _digest(activation),
        _digest(afterimage),
        _digest(mass),
        max(item.maximum_mass_error for item in diagnostics),
        float(np.min(mass)),
    )


def _validate_geometry(
    contract: MCMF3GeometryContract,
    plan: MCMF3GeometryPreregistration,
) -> None:
    if (
        contract.reflection_digest != plan.reflection_digest
        or contract.left_mask_digest != plan.left_mask_digest
        or contract.right_mask_digest != plan.right_mask_digest
        or len(contract.reflection_pairs) != plan.reflection_pair_count
        or len(contract.left_mask_neuron_ids) != plan.mask_size
        or len(contract.right_mask_neuron_ids) != plan.mask_size
    ):
        raise MCMF3GeometryRunError("E2 geometry differs from preregistration")


def _normalized_controls(controls) -> tuple[tuple[str, bool], ...]:
    return tuple((key, bool(value)) for key, value in controls)


def execute_mcm_f3_geometry_run() -> MCMF3GeometryRunResult:
    """Execute the fixed E2 geometry comparison once."""

    plan = mcm_f3_geometry_preregistration()
    history_plan = mcm_f3_history_preregistration()
    inputs = build_mcm_f3_controlled_history_inputs()
    if (
        inputs.same_history_digest != history_plan.same_history_digest
        or inputs.changed_history_digest != history_plan.changed_history_digest
        or inputs.shared_probe_digest != history_plan.shared_probe_digest
    ):
        raise MCMF3GeometryRunError("E2 source inputs changed")

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
    history_fields = {}
    history_diagnostics = []
    for history_id, sequences in (
        ("same", inputs.same_history),
        ("changed", inputs.changed_history),
    ):
        field, diagnostics, _ = _advance_sequences(
            activate_mcm_f3_field(base, history_plan.active_arm),
            sequences,
            history_plan.history_interval,
            inputs.ticks_per_second,
            plan.refinement,
        )
        history_fields[history_id] = align_mcm_f3_fast_state(field)
        history_diagnostics.extend(diagnostics)

    geometry = mcm_f3_geometry_contract(history_fields["same"])
    _validate_geometry(geometry, plan)
    starts = {}
    pre_controls = []
    for history_id, natural in history_fields.items():
        reflected = permute_mcm_f3_mass_by_geometry(natural, geometry)
        restored = permute_mcm_f3_mass_by_geometry(reflected, geometry)
        neutral_left = neutralize_mcm_f3_local_mask_balanced(
            natural, geometry, target_mask="left"
        )
        neutral_right = neutralize_mcm_f3_local_mask_balanced(
            natural, geometry, target_mask="right"
        )
        natural_mass = _vectors(natural)[2]
        reflected_mass = _vectors(reflected)[2]
        pre_controls.extend(
            (
                (
                    f"{history_id}.reflection_multiset_exact",
                    sorted(natural_mass.tolist()) == sorted(reflected_mass.tolist()),
                ),
                (
                    f"{history_id}.reflection_involutive",
                    np.array_equal(natural_mass, _vectors(restored)[2]),
                ),
                (
                    f"{history_id}.local_mass_balanced",
                    abs(math.fsum(_vectors(neutral_left)[2]) - 1.0) <= 1e-12
                    and abs(math.fsum(_vectors(neutral_right)[2]) - 1.0) <= 1e-12
                    and min(_vectors(neutral_left)[2]) >= 0.0
                    and min(_vectors(neutral_right)[2]) >= 0.0,
                ),
                (
                    f"{history_id}.fast_alignment_exact",
                    all(value == 0.0 for vector in _vectors(natural)[:2] for value in vector),
                ),
            )
        )
        starts.update(
            {
                f"{history_id}.natural": natural,
                f"{history_id}.reflected": reflected,
                f"{history_id}.neutral-left": neutral_left,
                f"{history_id}.neutral-right": neutral_right,
                f"{history_id}.eta-null-natural": ablate_mcm_f3_eta(natural),
                f"{history_id}.eta-null-reflected": ablate_mcm_f3_eta(reflected),
            }
        )

    completed = {}
    diagnostics_by_arm = {}
    for arm_id, start in starts.items():
        field, diagnostics, _ = _advance_sequences(
            start,
            inputs.shared_probe,
            history_plan.probe_interval,
            inputs.ticks_per_second,
            plan.refinement,
        )
        completed[arm_id] = field
        diagnostics_by_arm[arm_id] = diagnostics

    history_measurements = []
    controls = list(pre_controls)
    for history_id in ("same", "changed"):
        natural = _vectors(completed[f"{history_id}.natural"])
        reflected = _vectors(completed[f"{history_id}.reflected"])
        left = _vectors(completed[f"{history_id}.neutral-left"])
        right = _vectors(completed[f"{history_id}.neutral-right"])
        eta_natural = completed[f"{history_id}.eta-null-natural"]
        eta_reflected = completed[f"{history_id}.eta-null-reflected"]
        reflected_effect = not np.array_equal(natural[0], reflected[0]) or not np.array_equal(
            natural[1], reflected[1]
        )
        left_effect = not np.array_equal(natural[0], left[0]) or not np.array_equal(
            natural[1], left[1]
        )
        right_effect = not np.array_equal(natural[0], right[0]) or not np.array_equal(
            natural[1], right[1]
        )
        local_masks_differ = not np.array_equal(left[0], right[0]) or not np.array_equal(
            left[1], right[1]
        )
        eta_removed = _same_fast(eta_natural, eta_reflected)
        controls.extend(
            (
                (f"{history_id}.reflection_changes_effect", reflected_effect),
                (f"{history_id}.eta_null_removes_reflection_effect", eta_removed),
                (f"{history_id}.left_neutralization_changes_effect", left_effect),
                (f"{history_id}.right_neutralization_changes_effect", right_effect),
                (f"{history_id}.local_masks_differ", local_masks_differ),
            )
        )
        history_measurements.append(
            MCMF3GeometryHistoryMeasurement(
                history_id,
                _linf(_vectors(history_fields[history_id])[2], _vectors(starts[f"{history_id}.reflected"])[2]),
                _linf(natural[0], reflected[0]),
                _linf(natural[1], reflected[1]),
                _linf(natural[0], left[0]),
                _linf(natural[1], left[1]),
                _linf(natural[0], right[0]),
                _linf(natural[1], right[1]),
                _linf(left[0], right[0]),
                _linf(left[1], right[1]),
                _linf(_vectors(eta_natural)[0], _vectors(eta_reflected)[0]),
                _linf(_vectors(eta_natural)[1], _vectors(eta_reflected)[1]),
            )
        )

    all_diagnostics = tuple(history_diagnostics) + tuple(
        item for values in diagnostics_by_arm.values() for item in values
    )
    invariants_hold = (
        max(item.maximum_mass_error for item in all_diagnostics) <= 1e-12
        and min(item.minimum_mass for item in all_diagnostics) >= 0.0
    )
    controls.append(("state_invariants_hold", invariants_hold))
    controls_out = _normalized_controls(controls)
    decision = (
        "GEOMETRIC_M_CAUSALITY"
        if all(value for _, value in controls_out)
        else (
            "NO_GEOMETRIC_M_EFFECT"
            if not any(
                value
                for key, value in controls_out
                if key.endswith("reflection_changes_effect")
            )
            else "TECHNICALLY_UNDECIDABLE"
        )
    )
    arms = tuple(
        _measure_arm(arm_id, completed[arm_id], diagnostics_by_arm[arm_id])
        for arm_id in starts
    )
    return MCMF3GeometryRunResult(
        "lauf.191.mcm.f3.e2.geometry.corrected.v1",
        plan.preregistration_id,
        inputs.shared_probe_digest,
        geometry.reflection_digest,
        geometry.left_mask_digest,
        geometry.right_mask_digest,
        tuple(history_measurements),
        arms,
        controls_out,
        decision,
    )


def mcm_f3_geometry_run_json_value(result: MCMF3GeometryRunResult) -> dict:
    if not isinstance(result, MCMF3GeometryRunResult):
        raise MCMF3GeometryRunError("E2 result type is invalid")
    return asdict(result)


def mcm_f3_geometry_run_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            MCMF3GeometryPreregistration,
            MCMF3GeometryArmMeasurement,
            MCMF3GeometryHistoryMeasurement,
            MCMF3GeometryRunResult,
        )
        for item in fields(cls)
    )
