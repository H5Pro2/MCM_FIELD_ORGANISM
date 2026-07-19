"""Passive comparison of local two-timescale memory with simpler baselines."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
from typing import Mapping

from .controlled_audio_video_test_world import (
    ControlledAudioVideoTestWorld,
    controlled_history_holdout_world_family,
    run_controlled_test_world_phases,
)
from .local_synaptic_memory_candidate import (
    LocalSynapticMemoryConfig,
    LocalSynapticMemoryState,
    advance_local_synaptic_memory,
    initialize_local_synaptic_memory,
    local_relation_evidence,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)


class PassiveSynapticMemoryComparisonError(ValueError):
    """Raised when histories cannot be compared under one common probe."""


@dataclass(frozen=True, slots=True)
class PassiveSynapticMemoryComparison:
    relation_count: int
    common_prefix_max_error: float
    history_evidence_l1: float
    common_probe_digest: str
    null_baseline_l1: float
    instantaneous_baseline_l1: float
    fixed_baseline_l1: float
    leaky_baseline_l1: float
    two_stage_leaky_baseline_l1: float
    candidate_flexible_l1: float
    candidate_stabilized_l1: float
    raw_sensor_payload_retained: bool
    writes_back: bool


def _values(
    evidence: Mapping[str, tuple[str, str, float]],
) -> dict[str, float]:
    return {
        relation_id: float(item[2])
        for relation_id, item in evidence.items()
    }


def _l1(first: Mapping[str, float], second: Mapping[str, float]) -> float:
    if set(first) != set(second):
        raise PassiveSynapticMemoryComparisonError(
            "comparison requires one unchanged local relation topology"
        )
    if not first:
        raise PassiveSynapticMemoryComparisonError(
            "comparison requires at least one local relation"
        )
    return sum(abs(first[key] - second[key]) for key in first) / len(first)


def _evidence_digest(
    evidence: Mapping[str, tuple[str, str, float]],
) -> str:
    payload = [
        [relation_id, source_id, target_id, value]
        for relation_id, (source_id, target_id, value) in sorted(
            evidence.items()
        )
    ]
    encoded = json.dumps(
        payload,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _state_values(
    state: LocalSynapticMemoryState,
    role: str,
) -> dict[str, float]:
    return {
        relation.relation_id: float(getattr(relation, role))
        for relation in state.relations
    }


def _advance_leaky(
    trace: Mapping[str, float],
    evidence: Mapping[str, tuple[str, str, float]],
    rate: float,
) -> dict[str, float]:
    current = _values(evidence)
    if set(trace) != set(current):
        raise PassiveSynapticMemoryComparisonError(
            "leaky baseline requires one unchanged local relation topology"
        )
    return {
        relation_id: trace[relation_id]
        + rate * (current[relation_id] - trace[relation_id])
        for relation_id in trace
    }


def _advance_two_stage_leaky(
    fast: Mapping[str, float],
    slow: Mapping[str, float],
    evidence: Mapping[str, tuple[str, str, float]],
    fast_rate: float,
    slow_rate: float,
) -> tuple[dict[str, float], dict[str, float]]:
    fast_next = _advance_leaky(fast, evidence, fast_rate)
    if set(slow) != set(fast_next):
        raise PassiveSynapticMemoryComparisonError(
            "two-stage baseline requires one unchanged local relation topology"
        )
    slow_next = {
        relation_id: slow[relation_id]
        + slow_rate * (fast_next[relation_id] - slow[relation_id])
        for relation_id in slow
    }
    return fast_next, slow_next


def _common_probe_world(
    source: ControlledAudioVideoTestWorld,
) -> ControlledAudioVideoTestWorld:
    return ControlledAudioVideoTestWorld(
        "world.probe.common",
        (source.phases[-1],),
        source.audio_config,
        source.visual_config,
        source.background_channels,
    )


def run_passive_synaptic_memory_comparison(
    memory_config: LocalSynapticMemoryConfig,
    *,
    field_config: NeutralLocalFieldSubstrateConfig | None = None,
    afterimage_config: NeutralFastAfterimageConfig | None = None,
) -> PassiveSynapticMemoryComparison:
    """Compare two histories after exact fast-field separation."""

    if not isinstance(memory_config, LocalSynapticMemoryConfig):
        raise PassiveSynapticMemoryComparisonError(
            "comparison requires one explicit memory candidate configuration"
        )
    field_config_in = field_config or NeutralLocalFieldSubstrateConfig(1.0)
    afterimage_config_in = (
        afterimage_config or NeutralFastAfterimageConfig(0.5)
    )
    same_world, changed_world = controlled_history_holdout_world_family()
    same_runs = run_controlled_test_world_phases(
        same_world,
        field_config_in,
        afterimage_config=afterimage_config_in,
    )
    changed_runs = run_controlled_test_world_phases(
        changed_world,
        field_config_in,
        afterimage_config=afterimage_config_in,
    )
    same_history = tuple(
        local_relation_evidence(run.field_run.field)
        for run in same_runs[:3]
    )
    changed_history = tuple(
        local_relation_evidence(run.field_run.field)
        for run in changed_runs[:3]
    )
    if any(
        set(first) != set(second)
        for first, second in zip(same_history, changed_history, strict=True)
    ):
        raise PassiveSynapticMemoryComparisonError(
            "world histories produced incompatible local relation topologies"
        )

    prefix_errors = [
        _l1(_values(same_history[index]), _values(changed_history[index]))
        for index in (0, 1)
    ]
    state_same = initialize_local_synaptic_memory(same_history[0])
    state_changed = initialize_local_synaptic_memory(changed_history[0])
    zero = {key: 0.0 for key in same_history[0]}
    leaky_same = dict(zero)
    leaky_changed = dict(zero)
    two_stage_fast_same = dict(zero)
    two_stage_fast_changed = dict(zero)
    two_stage_slow_same = dict(zero)
    two_stage_slow_changed = dict(zero)
    fixed_same = _values(same_history[0])
    fixed_changed = _values(changed_history[0])
    for same_evidence, changed_evidence in zip(
        same_history,
        changed_history,
        strict=True,
    ):
        state_same = advance_local_synaptic_memory(
            state_same,
            same_evidence,
            memory_config,
        )
        state_changed = advance_local_synaptic_memory(
            state_changed,
            changed_evidence,
            memory_config,
        )
        leaky_same = _advance_leaky(
            leaky_same,
            same_evidence,
            memory_config.flexible_rate,
        )
        leaky_changed = _advance_leaky(
            leaky_changed,
            changed_evidence,
            memory_config.flexible_rate,
        )
        two_stage_fast_same, two_stage_slow_same = _advance_two_stage_leaky(
            two_stage_fast_same,
            two_stage_slow_same,
            same_evidence,
            memory_config.flexible_rate,
            memory_config.stabilization_rate,
        )
        (
            two_stage_fast_changed,
            two_stage_slow_changed,
        ) = _advance_two_stage_leaky(
            two_stage_fast_changed,
            two_stage_slow_changed,
            changed_evidence,
            memory_config.flexible_rate,
            memory_config.stabilization_rate,
        )

    probe_run = run_controlled_test_world_phases(
        _common_probe_world(same_world),
        field_config_in,
        afterimage_config=afterimage_config_in,
    )
    probe_evidence = local_relation_evidence(
        probe_run[0].field_run.field
    )
    state_same = advance_local_synaptic_memory(
        state_same,
        probe_evidence,
        memory_config,
    )
    state_changed = advance_local_synaptic_memory(
        state_changed,
        probe_evidence,
        memory_config,
    )
    leaky_same = _advance_leaky(
        leaky_same,
        probe_evidence,
        memory_config.flexible_rate,
    )
    leaky_changed = _advance_leaky(
        leaky_changed,
        probe_evidence,
        memory_config.flexible_rate,
    )
    two_stage_fast_same, two_stage_slow_same = _advance_two_stage_leaky(
        two_stage_fast_same,
        two_stage_slow_same,
        probe_evidence,
        memory_config.flexible_rate,
        memory_config.stabilization_rate,
    )
    (
        two_stage_fast_changed,
        two_stage_slow_changed,
    ) = _advance_two_stage_leaky(
        two_stage_fast_changed,
        two_stage_slow_changed,
        probe_evidence,
        memory_config.flexible_rate,
        memory_config.stabilization_rate,
    )
    probe_values = _values(probe_evidence)

    return PassiveSynapticMemoryComparison(
        relation_count=len(probe_evidence),
        common_prefix_max_error=max(prefix_errors),
        history_evidence_l1=_l1(
            _values(same_history[2]),
            _values(changed_history[2]),
        ),
        common_probe_digest=_evidence_digest(probe_evidence),
        null_baseline_l1=_l1(zero, zero),
        instantaneous_baseline_l1=_l1(probe_values, probe_values),
        fixed_baseline_l1=_l1(fixed_same, fixed_changed),
        leaky_baseline_l1=_l1(leaky_same, leaky_changed),
        two_stage_leaky_baseline_l1=_l1(
            two_stage_slow_same,
            two_stage_slow_changed,
        ),
        candidate_flexible_l1=_l1(
            _state_values(state_same, "flexible"),
            _state_values(state_changed, "flexible"),
        ),
        candidate_stabilized_l1=_l1(
            _state_values(state_same, "stabilized"),
            _state_values(state_changed, "stabilized"),
        ),
        raw_sensor_payload_retained=False,
        writes_back=False,
    )


def passive_synaptic_memory_comparison_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(PassiveSynapticMemoryComparison))
