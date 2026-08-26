"""Preregistered partition audit for coupled contact-free receptivity dynamics."""

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
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract


PARTITION_AUDIT_DURATION_TICKS = (2_000_000_000, 10_000_000_000, 20_000_000_000)
PARTITION_AUDIT_COUNTS = (1, 2, 10, 20)
PARTITION_AUDIT_CONTACT_TICKS = 500_000_000
PARTITION_AUDIT_LEAK_RATE_PER_SECOND = 0.0


class PublicAVLocalAdaptiveReceptivityPartitionError(ValueError):
    pass


def _linf(left, right):
    if not left or len(left) != len(right):
        raise PublicAVLocalAdaptiveReceptivityPartitionError("vectors must align")
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def _component_vectors(field, receptivity):
    activation, afterimage = _field_components(field)
    energy = tuple(abs(a) + abs(h) for a, h in zip(activation, afterimage, strict=True))
    return {
        "activation": activation,
        "afterimage": afterimage,
        "local_energy": energy,
        "receptivity": receptivity.values,
    }


def _metrics(values):
    return {
        "minimum": min(values),
        "maximum": max(values),
        "mean": math.fsum(values) / len(values),
        "l2": math.sqrt(math.fsum(value * value for value in values)),
        "linf": max(abs(value) for value in values),
    }


def _state_record(field, receptivity, elapsed_ticks):
    vectors = _component_vectors(field, receptivity)
    return {
        "elapsed_ticks": elapsed_ticks,
        "activation": _metrics(vectors["activation"]),
        "afterimage": _metrics(vectors["afterimage"]),
        "local_energy": _metrics(vectors["local_energy"]),
        "receptivity": _metrics(vectors["receptivity"]),
        "layer_digest": field.layer.digest(),
        "snapshot_digest": field.snapshot().digest(),
    }


def _partition_ticks(start_tick, duration_ticks, partition_count):
    if duration_ticks % partition_count:
        raise PublicAVLocalAdaptiveReceptivityPartitionError(
            "duration must divide into equal integer partitions"
        )
    width = duration_ticks // partition_count
    return tuple(
        (start_tick + index * width, start_tick + (index + 1) * width)
        for index in range(partition_count)
    )


def _run_partitioned_gap(
    start_field, start_receptivity, start_tick, duration_ticks, partition_count,
    substrate, afterimage, receptivity_config, dissipation,
):
    field = start_field
    receptivity = start_receptivity
    trace = []
    for interval_start, interval_end in _partition_ticks(
        start_tick, duration_ticks, partition_count
    ):
        field = _continuous_gap(
            field, interval_start, interval_end, substrate, afterimage, dissipation
        )
        receptivity = advance_receptivity_state(
            receptivity,
            field,
            (interval_end - interval_start) / 1_000_000_000,
            receptivity_config,
        )
        trace.append(_state_record(field, receptivity, interval_end - start_tick))
    return field, receptivity, trace


def execute_public_av_local_adaptive_receptivity_partition_audit(
    path: Path, contract: PublicMediaSourceContract
) -> dict[str, object]:
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVLocalAdaptiveReceptivityPartitionError("audited media file is required")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVLocalAdaptiveReceptivityPartitionError("source contract is required")
    sequences = _sequences(path, contract)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    dissipation = NeutralFieldDissipationConfig(PARTITION_AUDIT_LEAK_RATE_PER_SECOND)
    contact_steps = _steps(sequences, 0, PARTITION_AUDIT_CONTACT_TICKS)
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
        for duration in PARTITION_AUDIT_DURATION_TICKS:
            runs = {}
            for count in PARTITION_AUDIT_COUNTS:
                field, receptivity, trace = _run_partitioned_gap(
                    start_field, start_receptivity, PARTITION_AUDIT_CONTACT_TICKS,
                    duration, count, substrate, afterimage, config, dissipation,
                )
                runs[count] = {
                    "field": field,
                    "receptivity": receptivity,
                    "trace": trace,
                    "vectors": _component_vectors(field, receptivity),
                }
            reference = runs[max(PARTITION_AUDIT_COUNTS)]["vectors"]
            for count in PARTITION_AUDIT_COUNTS:
                run = runs[count]
                points.append({
                    "alpha_per_amplitude_second": alpha,
                    "duration_ticks": duration,
                    "partition_count": count,
                    "start_layer_digest": start_layer_digest,
                    "start_snapshot_digest": start_snapshot_digest,
                    "trace": run["trace"],
                    "final": _state_record(run["field"], run["receptivity"], duration),
                    "linf_to_finest_partition": {
                        role: _linf(run["vectors"][role], reference[role])
                        for role in ("activation", "afterimage", "local_energy", "receptivity")
                    },
                })
    return {
        "audit_id": "public.av.nasa-earthrise.local-adaptive-receptivity-partition-audit.v1",
        "source_id": contract.source_id,
        "alpha_axis": list(ADAPTIVE_RECEPTIVITY_ALPHA_AXIS),
        "duration_ticks": list(PARTITION_AUDIT_DURATION_TICKS),
        "partition_counts": list(PARTITION_AUDIT_COUNTS),
        "fixed_leak_rate_per_second": PARTITION_AUDIT_LEAK_RATE_PER_SECOND,
        "points": points,
        "threshold_defined": False,
        "preferred_partition_selected": False,
        "memory_claim_allowed": False,
        "meaning_claim_allowed": False,
        "organization_claim_allowed": False,
        "ai_claim_allowed": False,
    }
