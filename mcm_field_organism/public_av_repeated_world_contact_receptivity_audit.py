"""Preregistered repeated-world-contact audit for adaptive receptivity."""

from __future__ import annotations

from pathlib import Path

from .local_adaptive_receptivity import (
    LocalAdaptiveReceptivityConfig,
    LocalReceptivityState,
    run_adaptive_receptivity_field,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .public_av_local_adaptive_receptivity_cauchy_convergence_audit import (
    CAUCHY_AUDIT_CONTACT_TICKS,
    CAUCHY_AUDIT_DURATION_TICKS,
    CAUCHY_AUDIT_LEAK_RATE_PER_SECOND,
    CAUCHY_AUDIT_VECTOR_ROLES,
)
from .public_av_local_adaptive_receptivity_coupling_scheme_audit import (
    COUPLING_AUDIT_SCHEMES,
    _run_coupled_gap,
)
from .public_av_local_adaptive_receptivity_partition_audit import (
    _component_vectors,
    _linf,
    _state_record,
)
from .public_av_return_resolution_curve import _shift_sequences
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract


REPEATED_CONTACT_ALPHA_AXIS = (0.0, 0.5, 1.0)
REPEATED_CONTACT_PARTITION_COUNT = 320
REPEATED_CONTACT_ARM_IDS = ("continued_adaptive", "frozen_receptivity_baseline")
REPEATED_CONTACT_MEASUREMENT_ROLES = tuple(CAUCHY_AUDIT_VECTOR_ROLES)


class PublicAVRepeatedWorldContactReceptivityError(ValueError):
    pass


def _validated_axes(alpha: float, scheme: str) -> tuple[float, str]:
    alpha = float(alpha)
    if alpha not in REPEATED_CONTACT_ALPHA_AXIS:
        raise PublicAVRepeatedWorldContactReceptivityError(
            "alpha must belong to the preregistered repeated-contact axis"
        )
    if scheme not in COUPLING_AUDIT_SCHEMES:
        raise PublicAVRepeatedWorldContactReceptivityError(
            "scheme must belong to the preregistered coupling axis"
        )
    return alpha, scheme


def _arm_record(run, start_field, start_receptivity, duration_ticks):
    return {
        "event_count": run.source_support_count,
        "start_layer_digest": start_field.layer.digest(),
        "start_snapshot_digest": start_field.snapshot().digest(),
        "start_receptivity": _state_record(start_field, start_receptivity, 0)[
            "receptivity"
        ],
        "final": _state_record(run.field, run.receptivity, duration_ticks),
    }


def _validate_identity_control_differences(
    alpha: float, differences: dict[str, float]
) -> bool:
    if alpha != 0.0:
        return False
    if set(differences) != set(REPEATED_CONTACT_MEASUREMENT_ROLES):
        raise PublicAVRepeatedWorldContactReceptivityError(
            "identity control must contain every measurement role"
        )
    if any(value != 0.0 for value in differences.values()):
        raise PublicAVRepeatedWorldContactReceptivityError(
            "alpha=0 identity control produced unequal arm end states"
        )
    return True


def execute_public_av_repeated_world_contact_receptivity_shard(
    path: Path, contract: PublicMediaSourceContract, alpha: float, scheme: str
) -> dict[str, object]:
    alpha, scheme = _validated_axes(alpha, scheme)
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVRepeatedWorldContactReceptivityError(
            "audited media file is required"
        )
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVRepeatedWorldContactReceptivityError(
            "source contract is required"
        )

    sequences = _sequences(path, contract)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    dissipation = NeutralFieldDissipationConfig(CAUCHY_AUDIT_LEAK_RATE_PER_SECOND)
    adaptive_config = LocalAdaptiveReceptivityConfig(alpha)
    frozen_config = LocalAdaptiveReceptivityConfig(0.0)
    first_steps = _steps(sequences, 0, CAUCHY_AUDIT_CONTACT_TICKS)
    initial_field = _fresh_field(sequences)
    first_contact = run_adaptive_receptivity_field(
        initial_field,
        LocalReceptivityState.fresh(initial_field),
        sequences,
        first_steps,
        substrate,
        afterimage,
        adaptive_config,
        dissipation,
    )

    groups = []
    for gap_ticks in CAUCHY_AUDIT_DURATION_TICKS:
        gap_field, gap_receptivity, gap_trace = _run_coupled_gap(
            first_contact.field,
            first_contact.receptivity,
            CAUCHY_AUDIT_CONTACT_TICKS,
            gap_ticks,
            REPEATED_CONTACT_PARTITION_COUNT,
            scheme,
            substrate,
            afterimage,
            adaptive_config,
            dissipation,
        )
        second_start = CAUCHY_AUDIT_CONTACT_TICKS + gap_ticks
        shifted = _shift_sequences(sequences, second_start)
        second_steps = _steps(
            shifted, second_start, second_start + CAUCHY_AUDIT_CONTACT_TICKS
        )
        adaptive = run_adaptive_receptivity_field(
            gap_field, gap_receptivity, shifted, second_steps, substrate, afterimage,
            adaptive_config, dissipation,
        )
        frozen = run_adaptive_receptivity_field(
            gap_field, gap_receptivity, shifted, second_steps, substrate, afterimage,
            frozen_config, dissipation,
        )
        adaptive_vectors = _component_vectors(adaptive.field, adaptive.receptivity)
        frozen_vectors = _component_vectors(frozen.field, frozen.receptivity)
        differences = {
            role: _linf(adaptive_vectors[role], frozen_vectors[role])
            for role in REPEATED_CONTACT_MEASUREMENT_ROLES
        }
        identity_control_passed = _validate_identity_control_differences(
            alpha, differences
        )
        groups.append({
            "alpha_per_amplitude_second": alpha,
            "scheme": scheme,
            "gap_ticks": gap_ticks,
            "partition_count": REPEATED_CONTACT_PARTITION_COUNT,
            "first_contact": _state_record(
                first_contact.field, first_contact.receptivity,
                CAUCHY_AUDIT_CONTACT_TICKS,
            ),
            "gap_trace": gap_trace,
            "second_contact_start": _state_record(
                gap_field, gap_receptivity, second_start
            ),
            "arms": [
                {
                    "arm_id": REPEATED_CONTACT_ARM_IDS[0],
                    **_arm_record(
                        adaptive, gap_field, gap_receptivity,
                        CAUCHY_AUDIT_CONTACT_TICKS,
                    ),
                },
                {
                    "arm_id": REPEATED_CONTACT_ARM_IDS[1],
                    **_arm_record(
                        frozen, gap_field, gap_receptivity,
                        CAUCHY_AUDIT_CONTACT_TICKS,
                    ),
                },
            ],
            "adaptive_to_frozen_linf": differences,
            "identity_control_passed": identity_control_passed,
        })

    return {
        "audit_id": (
            "public.av.nasa-earthrise.repeated-world-contact-"
            "adaptive-receptivity-alpha-scheme-shard.v1"
        ),
        "source_id": contract.source_id,
        "alpha_axis": [alpha],
        "schemes": [scheme],
        "gap_duration_ticks": list(CAUCHY_AUDIT_DURATION_TICKS),
        "partition_count": REPEATED_CONTACT_PARTITION_COUNT,
        "contact_ticks": CAUCHY_AUDIT_CONTACT_TICKS,
        "arm_ids": list(REPEATED_CONTACT_ARM_IDS),
        "measurement_roles": list(REPEATED_CONTACT_MEASUREMENT_ROLES),
        "second_contact_sensor_events_identical": True,
        "second_contact_start_shared_between_arms": True,
        "frozen_baseline_uses_carried_receptivity_for_input_scaling": True,
        "frozen_baseline_updates_receptivity": False,
        "identity_control_alpha": 0.0,
        "identity_control_is_technical_invariant": True,
        "groups": groups,
        "shard_axes": ["alpha", "scheme"],
        "shard_values": {"alpha": alpha, "scheme": scheme},
        "threshold_defined": False,
        "preferred_scheme_selected": False,
        "preferred_alpha_selected": False,
        "memory_claim_allowed": False,
        "meaning_claim_allowed": False,
        "organization_claim_allowed": False,
        "consciousness_claim_allowed": False,
        "ai_claim_allowed": False,
    }
