"""Lifecycle probe for the unchanged passive local synaptic candidate."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Mapping

from .controlled_audio_video_test_world import (
    controlled_memory_lifecycle_world,
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


class SynapticMemoryLifecycleProbeError(ValueError):
    """Raised when the passive lifecycle cannot be compared fairly."""


@dataclass(frozen=True, slots=True)
class SynapticMemoryLifecycleProbeResult:
    phase_count: int
    relation_count: int
    built_relation_count: int
    candidate_build_l1: float
    candidate_after_interruption_l1: float
    candidate_old_residual_ratio: float
    candidate_old_relations_exactly_resolved: bool
    candidate_rebinding_change_l1: float
    candidate_max_local_budget_use: float
    two_stage_build_l1: float
    two_stage_after_interruption_l1: float
    two_stage_old_residual_ratio: float
    two_stage_old_relations_exactly_resolved: bool
    two_stage_rebinding_change_l1: float
    candidate_complete_lifecycle: bool
    raw_sensor_payload_retained: bool
    writes_back: bool


def _evidence_values(
    evidence: Mapping[str, tuple[str, str, float]],
) -> dict[str, float]:
    return {
        relation_id: float(item[2])
        for relation_id, item in evidence.items()
    }


def _state_values(
    state: LocalSynapticMemoryState,
) -> dict[str, float]:
    return {
        relation.relation_id: relation.stabilized
        for relation in state.relations
    }


def _mean_abs(
    values: Mapping[str, float],
    relation_ids: tuple[str, ...] | None = None,
) -> float:
    ids = tuple(values) if relation_ids is None else relation_ids
    if not ids:
        raise SynapticMemoryLifecycleProbeError(
            "lifecycle measurement requires at least one relation"
        )
    return sum(abs(values[relation_id]) for relation_id in ids) / len(ids)


def _l1(first: Mapping[str, float], second: Mapping[str, float]) -> float:
    if set(first) != set(second):
        raise SynapticMemoryLifecycleProbeError(
            "lifecycle states require one unchanged local topology"
        )
    return sum(abs(first[key] - second[key]) for key in first) / len(first)


def _advance_two_stage(
    fast: Mapping[str, float],
    slow: Mapping[str, float],
    evidence: Mapping[str, tuple[str, str, float]],
    config: LocalSynapticMemoryConfig,
) -> tuple[dict[str, float], dict[str, float]]:
    current = _evidence_values(evidence)
    if set(fast) != set(current) or set(slow) != set(current):
        raise SynapticMemoryLifecycleProbeError(
            "two-stage baseline requires one unchanged local topology"
        )
    fast_next = {
        key: fast[key]
        + config.flexible_rate * (current[key] - fast[key])
        for key in fast
    }
    slow_next = {
        key: slow[key]
        + config.stabilization_rate * (fast_next[key] - slow[key])
        for key in slow
    }
    return fast_next, slow_next


def _max_local_budget_use(state: LocalSynapticMemoryState) -> float:
    totals: dict[str, float] = {}
    for relation in state.relations:
        totals[relation.target_neuron_id] = (
            totals.get(relation.target_neuron_id, 0.0)
            + abs(relation.stabilized)
        )
    return max(totals.values(), default=0.0)


def run_synaptic_memory_lifecycle_probe(
    memory_config: LocalSynapticMemoryConfig,
    *,
    field_config: NeutralLocalFieldSubstrateConfig | None = None,
    afterimage_config: NeutralFastAfterimageConfig | None = None,
) -> SynapticMemoryLifecycleProbeResult:
    """Observe build, interruption, and different re-exposure without writeback."""

    if not isinstance(memory_config, LocalSynapticMemoryConfig):
        raise SynapticMemoryLifecycleProbeError(
            "lifecycle probe requires one explicit candidate configuration"
        )
    world = controlled_memory_lifecycle_world()
    runs = run_controlled_test_world_phases(
        world,
        field_config or NeutralLocalFieldSubstrateConfig(1.0),
        afterimage_config=(
            afterimage_config or NeutralFastAfterimageConfig(0.5)
        ),
    )
    evidence_sequence = tuple(
        local_relation_evidence(run.field_run.field) for run in runs
    )
    if len(evidence_sequence) != 16:
        raise SynapticMemoryLifecycleProbeError(
            "lifecycle world must contain exactly sixteen completed phases"
        )

    state = initialize_local_synaptic_memory(evidence_sequence[0])
    zero = {key: 0.0 for key in evidence_sequence[0]}
    two_stage_fast = dict(zero)
    two_stage_slow = dict(zero)
    candidate_snapshots: dict[int, dict[str, float]] = {}
    baseline_snapshots: dict[int, dict[str, float]] = {}
    max_budget_use = 0.0
    for index, evidence in enumerate(evidence_sequence):
        state = advance_local_synaptic_memory(
            state,
            evidence,
            memory_config,
        )
        two_stage_fast, two_stage_slow = _advance_two_stage(
            two_stage_fast,
            two_stage_slow,
            evidence,
            memory_config,
        )
        max_budget_use = max(max_budget_use, _max_local_budget_use(state))
        if index in {3, 11, 15}:
            candidate_snapshots[index] = _state_values(state)
            baseline_snapshots[index] = dict(two_stage_slow)

    candidate_build = candidate_snapshots[3]
    candidate_interrupted = candidate_snapshots[11]
    candidate_rebound = candidate_snapshots[15]
    baseline_build = baseline_snapshots[3]
    baseline_interrupted = baseline_snapshots[11]
    baseline_rebound = baseline_snapshots[15]
    built_ids = tuple(
        relation_id
        for relation_id, value in candidate_build.items()
        if value != 0.0
    )
    if not built_ids:
        raise SynapticMemoryLifecycleProbeError(
            "candidate did not build any relation during repeated contact"
        )

    candidate_build_l1 = _mean_abs(candidate_build, built_ids)
    candidate_interrupted_l1 = _mean_abs(
        candidate_interrupted,
        built_ids,
    )
    baseline_built_ids = tuple(
        relation_id
        for relation_id, value in baseline_build.items()
        if value != 0.0
    )
    baseline_build_l1 = _mean_abs(baseline_build, baseline_built_ids)
    baseline_interrupted_l1 = _mean_abs(
        baseline_interrupted,
        baseline_built_ids,
    )
    candidate_resolved = all(
        candidate_interrupted[relation_id] == 0.0
        for relation_id in built_ids
    )
    baseline_resolved = all(
        baseline_interrupted[relation_id] == 0.0
        for relation_id in baseline_built_ids
    )
    candidate_rebinding_change = _l1(
        candidate_interrupted,
        candidate_rebound,
    )

    return SynapticMemoryLifecycleProbeResult(
        phase_count=len(runs),
        relation_count=len(candidate_build),
        built_relation_count=len(built_ids),
        candidate_build_l1=candidate_build_l1,
        candidate_after_interruption_l1=candidate_interrupted_l1,
        candidate_old_residual_ratio=(
            candidate_interrupted_l1 / candidate_build_l1
        ),
        candidate_old_relations_exactly_resolved=candidate_resolved,
        candidate_rebinding_change_l1=candidate_rebinding_change,
        candidate_max_local_budget_use=max_budget_use,
        two_stage_build_l1=baseline_build_l1,
        two_stage_after_interruption_l1=baseline_interrupted_l1,
        two_stage_old_residual_ratio=(
            baseline_interrupted_l1 / baseline_build_l1
        ),
        two_stage_old_relations_exactly_resolved=baseline_resolved,
        two_stage_rebinding_change_l1=_l1(
            baseline_interrupted,
            baseline_rebound,
        ),
        candidate_complete_lifecycle=(
            candidate_resolved and candidate_rebinding_change > 0.0
        ),
        raw_sensor_payload_retained=False,
        writes_back=False,
    )


def synaptic_memory_lifecycle_probe_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(SynapticMemoryLifecycleProbeResult))
