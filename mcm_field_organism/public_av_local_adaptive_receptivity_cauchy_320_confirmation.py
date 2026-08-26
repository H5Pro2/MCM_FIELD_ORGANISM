"""Preregistered 160-to-320 confirmation audit for receptivity refinement."""

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
    PublicAVLocalAdaptiveReceptivityCauchyConvergenceError,
    _cauchy_records,
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
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract


CONFIRMATION_ALPHA_AXIS = (0.5, 1.0)
CONFIRMATION_PARTITION_COUNTS = (80, 160, 320)


def _validated_confirmation_alpha(alpha: float) -> float:
    value = float(alpha)
    if value not in CONFIRMATION_ALPHA_AXIS:
        raise PublicAVLocalAdaptiveReceptivityCauchyConvergenceError(
            "confirmation alpha must belong to the preregistered axis"
        )
    return value


def execute_public_av_local_adaptive_receptivity_cauchy_320_confirmation_shard(
    path: Path, contract: PublicMediaSourceContract, alpha: float
) -> dict[str, object]:
    alpha = _validated_confirmation_alpha(alpha)
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVLocalAdaptiveReceptivityCauchyConvergenceError(
            "audited media file is required"
        )
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVLocalAdaptiveReceptivityCauchyConvergenceError(
            "source contract is required"
        )

    sequences = _sequences(path, contract)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    dissipation = NeutralFieldDissipationConfig(CAUCHY_AUDIT_LEAK_RATE_PER_SECOND)
    config = LocalAdaptiveReceptivityConfig(alpha)
    initial_field = _fresh_field(sequences)
    contact = run_adaptive_receptivity_field(
        initial_field,
        LocalReceptivityState.fresh(initial_field),
        sequences,
        _steps(sequences, 0, CAUCHY_AUDIT_CONTACT_TICKS),
        substrate,
        afterimage,
        config,
        dissipation,
    )
    start_field = contact.field
    start_receptivity = contact.receptivity
    start_layer_digest = start_field.layer.digest()
    start_snapshot_digest = start_field.snapshot().digest()

    groups = []
    for duration in CAUCHY_AUDIT_DURATION_TICKS:
        runs = {}
        for scheme in COUPLING_AUDIT_SCHEMES:
            for count in CONFIRMATION_PARTITION_COUNTS:
                field, receptivity, trace = _run_coupled_gap(
                    start_field,
                    start_receptivity,
                    CAUCHY_AUDIT_CONTACT_TICKS,
                    duration,
                    count,
                    scheme,
                    substrate,
                    afterimage,
                    config,
                    dissipation,
                )
                runs[(scheme, count)] = {
                    "field": field,
                    "receptivity": receptivity,
                    "trace": trace,
                    "vectors": _component_vectors(field, receptivity),
                }

        scheme_results = []
        for scheme in COUPLING_AUDIT_SCHEMES:
            other_scheme = next(item for item in COUPLING_AUDIT_SCHEMES if item != scheme)
            vectors_by_count = {
                count: runs[(scheme, count)]["vectors"]
                for count in CONFIRMATION_PARTITION_COUNTS
            }
            scheme_results.append({
                "scheme": scheme,
                "runs": [{
                    "partition_count": count,
                    "trace": runs[(scheme, count)]["trace"],
                    "final": _state_record(
                        runs[(scheme, count)]["field"],
                        runs[(scheme, count)]["receptivity"],
                        duration,
                    ),
                    "linf_to_other_scheme_same_partition": {
                        role: _linf(
                            runs[(scheme, count)]["vectors"][role],
                            runs[(other_scheme, count)]["vectors"][role],
                        )
                        for role in CAUCHY_AUDIT_VECTOR_ROLES
                    },
                } for count in CONFIRMATION_PARTITION_COUNTS],
                "successive_cauchy_comparisons": _cauchy_records(vectors_by_count),
            })
        groups.append({
            "alpha_per_amplitude_second": alpha,
            "duration_ticks": duration,
            "start_layer_digest": start_layer_digest,
            "start_snapshot_digest": start_snapshot_digest,
            "scheme_results": scheme_results,
        })

    return {
        "audit_id": (
            "public.av.nasa-earthrise.local-adaptive-receptivity-"
            "cauchy-320-confirmation-alpha-shard.v1"
        ),
        "source_id": contract.source_id,
        "alpha_axis": [alpha],
        "duration_ticks": list(CAUCHY_AUDIT_DURATION_TICKS),
        "partition_counts": list(CONFIRMATION_PARTITION_COUNTS),
        "schemes": list(COUPLING_AUDIT_SCHEMES),
        "fixed_leak_rate_per_second": CAUCHY_AUDIT_LEAK_RATE_PER_SECOND,
        "groups": groups,
        "shard_axis": "alpha",
        "shard_value": alpha,
        "threshold_defined": False,
        "convergence_order_selected": False,
        "preferred_scheme_selected": False,
        "preferred_partition_selected": False,
        "memory_claim_allowed": False,
        "meaning_claim_allowed": False,
        "organization_claim_allowed": False,
        "ai_claim_allowed": False,
    }
