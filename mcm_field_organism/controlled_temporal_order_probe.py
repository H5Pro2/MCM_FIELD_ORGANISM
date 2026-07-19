"""Passive temporal-order probe over controlled shared-field contact."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import math

from .controlled_audio_video_test_world import (
    ControlledAudioVideoTestWorld,
    ControlledWorldPhase,
    controlled_reentry_world_family,
    run_controlled_test_world_phases,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class ControlledTemporalOrderProbeError(ValueError):
    """Raised when the passive order comparison loses a required control."""


@dataclass(frozen=True, slots=True)
class ControlledTemporalOrderProbeResult:
    phase_count_per_branch: int
    directed_relation_count: int
    independent_local_pair_count: int
    same_phase_multiset: bool
    forward_nonzero_relation_count: int
    reverse_nonzero_relation_count: int
    opposed_sign_relation_count: int
    same_sign_relation_count: int
    forward_mean_absolute_moment: float
    reverse_mean_absolute_moment: float
    reversal_residual_mean_absolute: float
    reversal_relative_residual: float
    every_local_relation_affected: bool
    reciprocal_antisymmetry_exact: bool
    exact_time_reversal_antisymmetry: bool
    observer_width: int
    observer_is_fixed_one_step_reader: bool
    selective_relation_source_shown: bool
    raw_sensor_payload_retained: bool
    writes_back: bool
    releases_memory_candidate: bool


def _phase_signature(phase: ControlledWorldPhase) -> tuple[object, ...]:
    return (
        phase.duration_seconds,
        phase.auditory_frequency,
        phase.auditory_amplitude,
        phase.visual_origin,
        phase.visual_velocity,
        phase.visual_extent,
        phase.visual_channels,
    )


def _order_worlds(
) -> tuple[ControlledAudioVideoTestWorld, ControlledAudioVideoTestWorld]:
    same, changed = controlled_reentry_world_family()
    phase_a = same.phases[0]
    phase_b = changed.phases[2]

    def build(
        world_id: str,
        phases: tuple[ControlledWorldPhase, ControlledWorldPhase],
    ) -> ControlledAudioVideoTestWorld:
        return ControlledAudioVideoTestWorld(
            world_id,
            tuple(
                replace(phase, phase_id=f"order.{index}")
                for index, phase in enumerate(phases)
            ),
            same.audio_config,
            same.visual_config,
            same.background_channels,
        )

    return (
        build("world.temporal_order.forward", (phase_a, phase_b)),
        build("world.temporal_order.reverse", (phase_b, phase_a)),
    )


def _activation_by_neuron(field: SharedMCMField) -> dict[str, float]:
    return {
        neuron.neuron_id: float(neuron.activation)
        for neuron in field.layer.neurons
    }


def _directed_temporal_moments(
    previous: SharedMCMField,
    current: SharedMCMField,
) -> dict[tuple[str, str], float]:
    previous_activation = _activation_by_neuron(previous)
    current_activation = _activation_by_neuron(current)
    if set(previous_activation) != set(current_activation):
        raise ControlledTemporalOrderProbeError(
            "temporal comparison requires one unchanged neuron layer"
        )

    moments: dict[tuple[str, str], float] = {}
    for target in current.layer.neurons:
        for sample in target.perception.local_samples:
            if not sample.sample_id.startswith("sample."):
                raise ControlledTemporalOrderProbeError(
                    "local sample identity cannot resolve its source neuron"
                )
            source_id = sample.sample_id[len("sample.") :]
            if source_id not in current_activation:
                raise ControlledTemporalOrderProbeError(
                    "local sample references an unknown source neuron"
                )
            relation = (source_id, target.neuron_id)
            moments[relation] = (
                previous_activation[source_id]
                * current_activation[target.neuron_id]
                - previous_activation[target.neuron_id]
                * current_activation[source_id]
            )
    return dict(sorted(moments.items()))


def _reciprocal_antisymmetry_exact(
    moments: dict[tuple[str, str], float],
) -> bool:
    return all(
        reverse in moments and moments[relation] == -moments[reverse]
        for relation in moments
        for reverse in ((relation[1], relation[0]),)
    )


def run_controlled_temporal_order_probe(
    *,
    field_config: NeutralLocalFieldSubstrateConfig | None = None,
    afterimage_config: NeutralFastAfterimageConfig | None = None,
) -> ControlledTemporalOrderProbeResult:
    """Compare A->B with B->A without adding state or field writeback."""

    forward_world, reverse_world = _order_worlds()
    config = field_config or NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = afterimage_config or NeutralFastAfterimageConfig(0.5)
    forward_runs = run_controlled_test_world_phases(
        forward_world,
        config,
        afterimage_config=afterimage,
    )
    reverse_runs = run_controlled_test_world_phases(
        reverse_world,
        config,
        afterimage_config=afterimage,
    )
    if len(forward_runs) != 2 or len(reverse_runs) != 2:
        raise ControlledTemporalOrderProbeError(
            "order branches require exactly two completed field phases"
        )

    forward = _directed_temporal_moments(
        forward_runs[0].field_run.field,
        forward_runs[1].field_run.field,
    )
    reverse = _directed_temporal_moments(
        reverse_runs[0].field_run.field,
        reverse_runs[1].field_run.field,
    )
    if set(forward) != set(reverse):
        raise ControlledTemporalOrderProbeError(
            "order branches require one unchanged local relation anatomy"
        )
    relation_ids = tuple(forward)
    if not relation_ids:
        raise ControlledTemporalOrderProbeError(
            "order probe requires local field relationships"
        )

    forward_nonzero = sum(forward[item] != 0.0 for item in relation_ids)
    reverse_nonzero = sum(reverse[item] != 0.0 for item in relation_ids)
    opposed = sum(
        forward[item] * reverse[item] < 0.0 for item in relation_ids
    )
    forward_mean = sum(abs(forward[item]) for item in relation_ids) / len(
        relation_ids
    )
    reverse_mean = sum(abs(reverse[item]) for item in relation_ids) / len(
        relation_ids
    )
    residual = sum(
        abs(forward[item] + reverse[item]) for item in relation_ids
    ) / len(relation_ids)
    reference = (forward_mean + reverse_mean) / 2.0
    exact_reversal = all(
        math.isclose(
            forward[item],
            -reverse[item],
            rel_tol=0.0,
            abs_tol=1e-15,
        )
        for item in relation_ids
    )
    phase_multiset_equal = sorted(
        _phase_signature(item) for item in forward_world.phases
    ) == sorted(_phase_signature(item) for item in reverse_world.phases)

    return ControlledTemporalOrderProbeResult(
        phase_count_per_branch=2,
        directed_relation_count=len(relation_ids),
        independent_local_pair_count=len(relation_ids) // 2,
        same_phase_multiset=phase_multiset_equal,
        forward_nonzero_relation_count=forward_nonzero,
        reverse_nonzero_relation_count=reverse_nonzero,
        opposed_sign_relation_count=opposed,
        same_sign_relation_count=len(relation_ids) - opposed,
        forward_mean_absolute_moment=forward_mean,
        reverse_mean_absolute_moment=reverse_mean,
        reversal_residual_mean_absolute=residual,
        reversal_relative_residual=residual / reference,
        every_local_relation_affected=(
            forward_nonzero == len(relation_ids)
            and reverse_nonzero == len(relation_ids)
        ),
        reciprocal_antisymmetry_exact=(
            _reciprocal_antisymmetry_exact(forward)
            and _reciprocal_antisymmetry_exact(reverse)
        ),
        exact_time_reversal_antisymmetry=exact_reversal,
        observer_width=1,
        observer_is_fixed_one_step_reader=True,
        selective_relation_source_shown=False,
        raw_sensor_payload_retained=False,
        writes_back=False,
        releases_memory_candidate=False,
    )


def controlled_temporal_order_probe_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(ControlledTemporalOrderProbeResult))
