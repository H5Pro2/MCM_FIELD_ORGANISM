"""Preregistered coupling-scheme convergence audit for local receptivity."""

from __future__ import annotations

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
from .public_av_continuous_dissipation_viability import _continuous_gap
from .public_av_local_adaptive_receptivity_partition_audit import (
    _component_vectors,
    _linf,
    _partition_ticks,
    _state_record,
)
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract


COUPLING_AUDIT_DURATION_TICKS = (2_000_000_000, 10_000_000_000, 20_000_000_000)
COUPLING_AUDIT_PARTITION_COUNTS = (10, 20, 40, 80)
COUPLING_AUDIT_SCHEMES = ("endpoint_energy", "midpoint_coupling")
COUPLING_AUDIT_CONTACT_TICKS = 500_000_000
COUPLING_AUDIT_LEAK_RATE_PER_SECOND = 0.0
_VECTOR_ROLES = ("activation", "afterimage", "local_energy", "receptivity")


class PublicAVLocalAdaptiveReceptivityCouplingSchemeError(ValueError):
    pass


def _advance_gap_interval(
    field, receptivity, interval_start, interval_end, scheme,
    substrate, afterimage, receptivity_config, dissipation,
):
    elapsed_seconds = (interval_end - interval_start) / 1_000_000_000
    if scheme == "endpoint_energy":
        final_field = _continuous_gap(
            field, interval_start, interval_end, substrate, afterimage, dissipation
        )
        final_receptivity = advance_receptivity_state(
            receptivity, final_field, elapsed_seconds, receptivity_config
        )
        return final_field, final_receptivity, interval_end
    if scheme == "midpoint_coupling":
        midpoint_tick = interval_start + (interval_end - interval_start) // 2
        if midpoint_tick * 2 != interval_start + interval_end:
            raise PublicAVLocalAdaptiveReceptivityCouplingSchemeError(
                "midpoint must be represented exactly"
            )
        midpoint_field = _continuous_gap(
            field, interval_start, midpoint_tick, substrate, afterimage, dissipation
        )
        final_receptivity = advance_receptivity_state(
            receptivity, midpoint_field, elapsed_seconds, receptivity_config
        )
        final_field = _continuous_gap(
            midpoint_field, midpoint_tick, interval_end, substrate, afterimage, dissipation
        )
        return final_field, final_receptivity, midpoint_tick
    raise PublicAVLocalAdaptiveReceptivityCouplingSchemeError("unknown coupling scheme")


def _run_coupled_gap(
    start_field, start_receptivity, start_tick, duration_ticks, partition_count, scheme,
    substrate, afterimage, receptivity_config, dissipation,
):
    field = start_field
    receptivity = start_receptivity
    trace = []
    for interval_start, interval_end in _partition_ticks(
        start_tick, duration_ticks, partition_count
    ):
        field, receptivity, energy_sample_tick = _advance_gap_interval(
            field, receptivity, interval_start, interval_end, scheme,
            substrate, afterimage, receptivity_config, dissipation,
        )
        record = _state_record(field, receptivity, interval_end - start_tick)
        record["energy_sample_tick"] = energy_sample_tick
        trace.append(record)
    return field, receptivity, trace


def execute_public_av_local_adaptive_receptivity_coupling_scheme_audit(
    path: Path, contract: PublicMediaSourceContract
) -> dict[str, object]:
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVLocalAdaptiveReceptivityCouplingSchemeError(
            "audited media file is required"
        )
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVLocalAdaptiveReceptivityCouplingSchemeError(
            "source contract is required"
        )
    sequences = _sequences(path, contract)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    dissipation = NeutralFieldDissipationConfig(COUPLING_AUDIT_LEAK_RATE_PER_SECOND)
    contact_steps = _steps(sequences, 0, COUPLING_AUDIT_CONTACT_TICKS)
    points = []
    for alpha in ADAPTIVE_RECEPTIVITY_ALPHA_AXIS:
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
        for duration in COUPLING_AUDIT_DURATION_TICKS:
            runs = {}
            for scheme in COUPLING_AUDIT_SCHEMES:
                for count in COUPLING_AUDIT_PARTITION_COUNTS:
                    field, receptivity, trace = _run_coupled_gap(
                        start_field, start_receptivity, COUPLING_AUDIT_CONTACT_TICKS,
                        duration, count, scheme, substrate, afterimage, config, dissipation,
                    )
                    runs[(scheme, count)] = {
                        "field": field,
                        "receptivity": receptivity,
                        "trace": trace,
                        "vectors": _component_vectors(field, receptivity),
                    }
            finest = max(COUPLING_AUDIT_PARTITION_COUNTS)
            for scheme in COUPLING_AUDIT_SCHEMES:
                reference = runs[(scheme, finest)]["vectors"]
                for count in COUPLING_AUDIT_PARTITION_COUNTS:
                    run = runs[(scheme, count)]
                    other_scheme = next(item for item in COUPLING_AUDIT_SCHEMES if item != scheme)
                    other = runs[(other_scheme, count)]["vectors"]
                    points.append({
                        "alpha_per_amplitude_second": alpha,
                        "duration_ticks": duration,
                        "partition_count": count,
                        "scheme": scheme,
                        "start_layer_digest": start_layer_digest,
                        "start_snapshot_digest": start_snapshot_digest,
                        "trace": run["trace"],
                        "final": _state_record(run["field"], run["receptivity"], duration),
                        "linf_to_own_80_partition": {
                            role: _linf(run["vectors"][role], reference[role])
                            for role in _VECTOR_ROLES
                        },
                        "linf_to_other_scheme_same_partition": {
                            role: _linf(run["vectors"][role], other[role])
                            for role in _VECTOR_ROLES
                        },
                    })
    return {
        "audit_id": "public.av.nasa-earthrise.local-adaptive-receptivity-coupling-scheme-audit.v1",
        "source_id": contract.source_id,
        "alpha_axis": list(ADAPTIVE_RECEPTIVITY_ALPHA_AXIS),
        "duration_ticks": list(COUPLING_AUDIT_DURATION_TICKS),
        "partition_counts": list(COUPLING_AUDIT_PARTITION_COUNTS),
        "schemes": list(COUPLING_AUDIT_SCHEMES),
        "fixed_leak_rate_per_second": COUPLING_AUDIT_LEAK_RATE_PER_SECOND,
        "points": points,
        "threshold_defined": False,
        "preferred_scheme_selected": False,
        "preferred_partition_selected": False,
        "memory_claim_allowed": False,
        "meaning_claim_allowed": False,
        "organization_claim_allowed": False,
        "ai_claim_allowed": False,
    }
