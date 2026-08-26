"""Preregistered two-contact audit for local adaptive receptivity."""

from __future__ import annotations

import math
from pathlib import Path

from .local_adaptive_receptivity import (
    ADAPTIVE_RECEPTIVITY_ALPHA_AXIS,
    LocalAdaptiveReceptivityConfig,
    LocalReceptivityState,
    advance_receptivity_state,
    run_adaptive_receptivity_field,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .public_av_continuous_dissipation_viability import _continuous_gap, _field_components
from .public_av_return_resolution_curve import _shift_sequences
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract


ADAPTIVE_RECEPTIVITY_ARM_IDS = (
    "continued_adaptive",
    "fresh_adaptive",
    "receptivity_reset_control",
    "disabled_identity_control",
)
ADAPTIVE_RECEPTIVITY_GAP_TICKS = 2_000_000_000
ADAPTIVE_RECEPTIVITY_CONTACT_TICKS = 500_000_000
ADAPTIVE_RECEPTIVITY_FIXED_LEAK_RATE = 0.0


class PublicAVLocalAdaptiveReceptivityError(ValueError):
    pass


def _metrics(values):
    return {
        "minimum": min(values),
        "maximum": max(values),
        "mean": math.fsum(values) / len(values),
        "l2": math.sqrt(math.fsum(value * value for value in values)),
        "linf": max(abs(value) for value in values),
    }


def _measurement(field, receptivity):
    activation, afterimage = _field_components(field)
    return {
        "activation": _metrics(activation),
        "afterimage": _metrics(afterimage),
        "receptivity": _metrics(receptivity.values),
        "layer_digest": field.layer.digest(),
        "snapshot_digest": field.snapshot().digest(),
    }


def _advance_gap(field, receptivity, start_tick, end_tick, substrate, afterimage,
                 receptivity_config, dissipation):
    next_field = _continuous_gap(
        field, start_tick, end_tick, substrate, afterimage, dissipation
    )
    next_receptivity = advance_receptivity_state(
        receptivity, next_field, (end_tick - start_tick) / 1_000_000_000,
        receptivity_config,
    )
    return next_field, next_receptivity


def execute_public_av_local_adaptive_receptivity(
    path: Path, contract: PublicMediaSourceContract
) -> dict[str, object]:
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVLocalAdaptiveReceptivityError("audited media file is required")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVLocalAdaptiveReceptivityError("source contract is required")
    sequences = _sequences(path, contract)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    dissipation = NeutralFieldDissipationConfig(ADAPTIVE_RECEPTIVITY_FIXED_LEAK_RATE)
    stage_one_steps = _steps(sequences, 0, ADAPTIVE_RECEPTIVITY_CONTACT_TICKS)
    return_start = ADAPTIVE_RECEPTIVITY_CONTACT_TICKS + ADAPTIVE_RECEPTIVITY_GAP_TICKS
    shifted = _shift_sequences(sequences, return_start)
    stage_two_steps = _steps(
        shifted, return_start, return_start + ADAPTIVE_RECEPTIVITY_CONTACT_TICKS
    )
    identity_config = LocalAdaptiveReceptivityConfig(0.0)
    identity_initial_field = _fresh_field(sequences)
    identity_stage_one = run_adaptive_receptivity_field(
        identity_initial_field, LocalReceptivityState.fresh(identity_initial_field),
        sequences, stage_one_steps, substrate, afterimage, identity_config, dissipation,
    )
    identity_carried_field, identity_carried_state = _advance_gap(
        identity_stage_one.field, identity_stage_one.receptivity,
        ADAPTIVE_RECEPTIVITY_CONTACT_TICKS, return_start,
        substrate, afterimage, identity_config, dissipation,
    )
    points = []
    for alpha in ADAPTIVE_RECEPTIVITY_ALPHA_AXIS:
        config = LocalAdaptiveReceptivityConfig(alpha)
        initial_field = _fresh_field(sequences)
        initial_state = LocalReceptivityState.fresh(initial_field)
        stage_one = run_adaptive_receptivity_field(
            initial_field, initial_state, sequences, stage_one_steps, substrate,
            afterimage, config, dissipation,
        )
        carried_field, carried_state = _advance_gap(
            stage_one.field, stage_one.receptivity,
            ADAPTIVE_RECEPTIVITY_CONTACT_TICKS, return_start,
            substrate, afterimage, config, dissipation,
        )
        fresh_field = _fresh_field(sequences)
        arm_starts = (
            (carried_field, carried_state),
            (fresh_field, LocalReceptivityState.fresh(fresh_field)),
            (carried_field, LocalReceptivityState.fresh(carried_field)),
            (identity_carried_field, identity_carried_state),
        )
        arms = []
        for arm_id, (start_field, start_state) in zip(
            ADAPTIVE_RECEPTIVITY_ARM_IDS, arm_starts, strict=True
        ):
            arm_config = (
                LocalAdaptiveReceptivityConfig(0.0)
                if arm_id == "disabled_identity_control" else config
            )
            run = run_adaptive_receptivity_field(
                start_field, start_state, shifted, stage_two_steps, substrate,
                afterimage, arm_config, dissipation,
            )
            arms.append({
                "arm_id": arm_id,
                "event_count": run.source_support_count,
                "measurement": _measurement(run.field, run.receptivity),
            })
        points.append({
            "alpha_per_amplitude_second": alpha,
            "stage_one_event_count": stage_one.source_support_count,
            "stage_one": _measurement(stage_one.field, stage_one.receptivity),
            "post_gap": _measurement(carried_field, carried_state),
            "arms": arms,
        })
    return {
        "audit_id": "public.av.nasa-earthrise.local-adaptive-receptivity.v1",
        "source_id": contract.source_id,
        "alpha_axis": list(ADAPTIVE_RECEPTIVITY_ALPHA_AXIS),
        "beta_per_second": 0.25,
        "receptivity_floor": 0.25,
        "fixed_leak_rate_per_second": ADAPTIVE_RECEPTIVITY_FIXED_LEAK_RATE,
        "receptivity_ode": "dr_i/dt=beta*(1-r_i)-alpha*e_i*r_i",
        "local_energy": "e_i=abs(activation_i)+abs(afterimage_i)",
        "contact_intervention": "local_receptor_value_times_r_i_only",
        "arm_ids": list(ADAPTIVE_RECEPTIVITY_ARM_IDS),
        "points": points,
        "threshold_defined": False,
        "preferred_rate_selected": False,
        "memory_claim_allowed": False,
        "meaning_claim_allowed": False,
        "organization_claim_allowed": False,
        "ai_claim_allowed": False,
    }
