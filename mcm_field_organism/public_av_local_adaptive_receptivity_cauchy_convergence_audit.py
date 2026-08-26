"""Preregistered Cauchy-refinement audit for local receptivity coupling."""

from __future__ import annotations

from pathlib import Path

from .local_adaptive_receptivity import (
    ADAPTIVE_RECEPTIVITY_ALPHA_AXIS,
    LocalAdaptiveReceptivityConfig,
    LocalReceptivityState,
    run_adaptive_receptivity_field,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
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


CAUCHY_AUDIT_DURATION_TICKS = (2_000_000_000, 10_000_000_000, 20_000_000_000)
CAUCHY_AUDIT_PARTITION_COUNTS = (20, 40, 80, 160)
CAUCHY_AUDIT_CONTACT_TICKS = 500_000_000
CAUCHY_AUDIT_LEAK_RATE_PER_SECOND = 0.0
CAUCHY_AUDIT_VECTOR_ROLES = ("activation", "afterimage", "local_energy", "receptivity")


class PublicAVLocalAdaptiveReceptivityCauchyConvergenceError(ValueError):
    pass


def _validated_alpha_axis(selected_alpha=None):
    if selected_alpha is None:
        return ADAPTIVE_RECEPTIVITY_ALPHA_AXIS
    alpha = float(selected_alpha)
    if alpha not in ADAPTIVE_RECEPTIVITY_ALPHA_AXIS:
        raise PublicAVLocalAdaptiveReceptivityCauchyConvergenceError(
            "alpha shard must belong to the preregistered axis"
        )
    return (alpha,)


def _successive_pairs(counts=CAUCHY_AUDIT_PARTITION_COUNTS):
    counts = tuple(counts)
    if len(counts) < 3 or any(fine != 2 * coarse for coarse, fine in zip(counts, counts[1:])):
        raise PublicAVLocalAdaptiveReceptivityCauchyConvergenceError(
            "partition axis must use successive doubling"
        )
    return tuple(zip(counts, counts[1:]))


def _numeric_ratio(numerator, denominator):
    numerator = float(numerator)
    denominator = float(denominator)
    if denominator == 0.0:
        return None
    return numerator / denominator


def _cauchy_records(vectors_by_count):
    pairs = _successive_pairs(tuple(vectors_by_count))
    distances = {
        (coarse, fine): {
            role: _linf(vectors_by_count[coarse][role], vectors_by_count[fine][role])
            for role in CAUCHY_AUDIT_VECTOR_ROLES
        }
        for coarse, fine in pairs
    }
    records = []
    for index, (coarse, fine) in enumerate(pairs):
        next_pair = pairs[index + 1] if index + 1 < len(pairs) else None
        records.append({
            "coarse_partition_count": coarse,
            "fine_partition_count": fine,
            "linf_distance": distances[(coarse, fine)],
            "refinement_quotient_to_next_pair": None if next_pair is None else {
                role: _numeric_ratio(
                    distances[(coarse, fine)][role], distances[next_pair][role]
                )
                for role in CAUCHY_AUDIT_VECTOR_ROLES
            },
        })
    return records


def _execute_cauchy_convergence_axis(path, contract, alpha_axis):
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
    contact_steps = _steps(sequences, 0, CAUCHY_AUDIT_CONTACT_TICKS)
    groups = []
    for alpha in alpha_axis:
        config = LocalAdaptiveReceptivityConfig(alpha)
        initial_field = _fresh_field(sequences)
        contact = run_adaptive_receptivity_field(
            initial_field, LocalReceptivityState.fresh(initial_field), sequences,
            contact_steps, substrate, afterimage, config, dissipation,
        )
        start_field = contact.field
        start_receptivity = contact.receptivity
        start_layer_digest = start_field.layer.digest()
        start_snapshot_digest = start_field.snapshot().digest()
        for duration in CAUCHY_AUDIT_DURATION_TICKS:
            runs = {}
            for scheme in COUPLING_AUDIT_SCHEMES:
                for count in CAUCHY_AUDIT_PARTITION_COUNTS:
                    field, receptivity, trace = _run_coupled_gap(
                        start_field, start_receptivity, CAUCHY_AUDIT_CONTACT_TICKS,
                        duration, count, scheme, substrate, afterimage, config, dissipation,
                    )
                    runs[(scheme, count)] = {
                        "field": field,
                        "receptivity": receptivity,
                        "trace": trace,
                        "vectors": _component_vectors(field, receptivity),
                    }
            scheme_results = []
            for scheme in COUPLING_AUDIT_SCHEMES:
                vectors_by_count = {
                    count: runs[(scheme, count)]["vectors"]
                    for count in CAUCHY_AUDIT_PARTITION_COUNTS
                }
                scheme_results.append({
                    "scheme": scheme,
                    "runs": [{
                        "partition_count": count,
                        "trace": runs[(scheme, count)]["trace"],
                        "final": _state_record(
                            runs[(scheme, count)]["field"],
                            runs[(scheme, count)]["receptivity"], duration,
                        ),
                        "linf_to_other_scheme_same_partition": {
                            role: _linf(
                                runs[(scheme, count)]["vectors"][role],
                                runs[(next(
                                    item for item in COUPLING_AUDIT_SCHEMES
                                    if item != scheme
                                ), count)]["vectors"][role],
                            )
                            for role in CAUCHY_AUDIT_VECTOR_ROLES
                        },
                    } for count in CAUCHY_AUDIT_PARTITION_COUNTS],
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
        "audit_id": "public.av.nasa-earthrise.local-adaptive-receptivity-cauchy-convergence-audit.v1",
        "source_id": contract.source_id,
        "alpha_axis": list(alpha_axis),
        "duration_ticks": list(CAUCHY_AUDIT_DURATION_TICKS),
        "partition_counts": list(CAUCHY_AUDIT_PARTITION_COUNTS),
        "schemes": list(COUPLING_AUDIT_SCHEMES),
        "fixed_leak_rate_per_second": CAUCHY_AUDIT_LEAK_RATE_PER_SECOND,
        "groups": groups,
        "threshold_defined": False,
        "convergence_order_selected": False,
        "preferred_scheme_selected": False,
        "preferred_partition_selected": False,
        "memory_claim_allowed": False,
        "meaning_claim_allowed": False,
        "organization_claim_allowed": False,
        "ai_claim_allowed": False,
    }


def execute_public_av_local_adaptive_receptivity_cauchy_convergence_audit(
    path: Path, contract: PublicMediaSourceContract
) -> dict[str, object]:
    return _execute_cauchy_convergence_axis(
        path, contract, _validated_alpha_axis()
    )


def execute_public_av_local_adaptive_receptivity_cauchy_convergence_shard(
    path: Path, contract: PublicMediaSourceContract, alpha: float
) -> dict[str, object]:
    payload = _execute_cauchy_convergence_axis(
        path, contract, _validated_alpha_axis(alpha)
    )
    payload["audit_id"] = (
        "public.av.nasa-earthrise.local-adaptive-receptivity-"
        "cauchy-convergence-alpha-shard.v1"
    )
    payload["shard_axis"] = "alpha"
    payload["shard_value"] = float(alpha)
    return payload
