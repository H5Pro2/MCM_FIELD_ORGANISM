"""Private S2-JT time projection and observed neutral field arm."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Iterable, Mapping

import numpy as np

from mcm_field_organism.asynchronous_receptor_events import (
    audit_asynchronous_receptor_events,
)
from mcm_field_organism.audio_video_field_geometry import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from mcm_field_organism.field_time_partition import (
    partition_receptor_completion_time,
)
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.neutral_asynchronous_field_runtime import (
    NeutralAsynchronousFieldRun,
    run_neutral_asynchronous_field,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from mcm_field_organism.receptor_distributor import ReceptorDistribution
from mcm_field_organism.receptor_proposal_handoff import (
    ReceptorProposalHandoff,
    handoff_receptor_completion_groups,
)
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from mcm_field_organism.shared_mcm_field import (
    ReceptorDockAnatomy,
    SharedMCMField,
    build_shared_mcm_field,
)
from mcm_field_organism.transient_dock_trajectory import (
    map_proposal_batch_to_transient_docks,
)
from mcm_field_organism.transient_neuron_input import (
    project_transient_docks_to_neuron_inputs,
)
from tools._s2jo_private_canonical_av_boundary import (
    CanonicalInputBindingV1,
    CanonicalReducedReceptorSequenceReceiptV1,
    CanonicalReductionResultV1,
    S2JO_AUDIO_CONFIG,
    S2JO_AUDIO_STATE_COUNT,
    S2JO_CLOCK_ID,
    S2JO_DURATION_TICKS,
    S2JO_FRAME_COUNT,
    S2JO_HOP_COUNT,
    S2JO_TICKS_PER_SECOND,
    S2JO_VISUAL_CONFIG,
    StreamingResourceLedgerV1,
)


S2JT_PROJECTION_SCHEMA = "s2jt.timed-sequence-projection.v1"
S2JT_TRAJECTORY_SCHEMA = "s2jt.observed-field-trajectory.v1"
S2JT_FULL_EXECUTION_ENABLED = False


class S2JTProjectionError(ValueError):
    """One fail-closed S2-JT projection or observed-field violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    ).hexdigest()


def _visual_window(index: int) -> tuple[int, int]:
    return (
        math.floor(index * S2JO_TICKS_PER_SECOND / 30),
        math.floor((index + 1) * S2JO_TICKS_PER_SECOND / 30),
    )


def _audio_window(index: int) -> tuple[int, int]:
    return index * 10_000_000, (index + 1) * 10_000_000


def _expected_binding_roles() -> tuple[tuple[str, int], ...]:
    roles = [("VISUAL_FRAME", index) for index in range(S2JO_FRAME_COUNT)]
    roles.extend(("AUDIO_HOP", index) for index in range(S2JO_HOP_COUNT))
    return tuple(
        sorted(
            roles,
            key=lambda item: (
                _visual_window(item[1])[0]
                if item[0] == "VISUAL_FRAME"
                else _audio_window(item[1])[0],
                0 if item[0] == "VISUAL_FRAME" else 1,
                item[1],
            ),
        )
    )


@dataclass(frozen=True, slots=True)
class S2JTTimedSequenceProjection:
    schema: str
    input_episode_digest: str
    reduced_sequence_digest: str
    clock_id: str
    sequences: tuple[ReceptorTimeSequence, ReceptorTimeSequence]
    auditory_trigger_hops: tuple[int, ...]
    completion_ticks: tuple[int, ...]
    mixed_completion_ticks: tuple[int, ...]
    event_count: int
    projection_digest: str

    def __post_init__(self) -> None:
        sequences = tuple(self.sequences)
        payload = {
            "schema": self.schema,
            "input_episode_digest": self.input_episode_digest,
            "reduced_sequence_digest": self.reduced_sequence_digest,
            "clock_id": self.clock_id,
            "sequence_digests": [_sequence_digest(item) for item in sequences],
            "auditory_trigger_hops": list(self.auditory_trigger_hops),
            "completion_ticks": list(self.completion_ticks),
            "mixed_completion_ticks": list(self.mixed_completion_ticks),
            "event_count": self.event_count,
        }
        if (
            self.schema != S2JT_PROJECTION_SCHEMA
            or len(sequences) != 2
            or tuple(item.modality_id for item in sequences)
            != ("auditory", "visual")
            or tuple(len(item.frames) for item in sequences)
            != (S2JO_AUDIO_STATE_COUNT, S2JO_FRAME_COUNT)
            or self.clock_id != S2JO_CLOCK_ID
            or self.auditory_trigger_hops != tuple(range(9, 20))
            or len(self.completion_ticks) != 15
            or self.mixed_completion_ticks != (100_000_000, 200_000_000)
            or self.event_count != 17
            or self.projection_digest != _digest(payload)
        ):
            raise S2JTProjectionError(
                "S2JT_TIME_PROJECTION_INVALID",
                "timed sequence projection differs from the bound episode",
            )
        object.__setattr__(self, "sequences", sequences)


def _sequence_digest(sequence: ReceptorTimeSequence) -> str:
    return _digest(
        {
            "modality_id": sequence.modality_id,
            "geometry_id": sequence.geometry_id,
            "clock_id": sequence.clock_id,
            "frames": [
                {
                    "snapshot_id": item.frame.snapshot_id,
                    "source_clock_id": item.frame.clock_id,
                    "source_window": [
                        item.frame.window_start_tick,
                        item.frame.window_end_tick,
                    ],
                    "field_window": [
                        item.field_time.window_start_tick,
                        item.field_time.window_end_tick,
                    ],
                    "carrier_ids": list(item.frame.carrier_ids),
                    "values": list(item.frame.values),
                }
                for item in sequence.frames
            ],
        }
    )


def _bindings_by_role(
    bindings: tuple[CanonicalInputBindingV1, ...],
) -> dict[str, dict[int, CanonicalInputBindingV1]]:
    expected = _expected_binding_roles()
    actual = tuple((item.role, item.position) for item in bindings)
    if actual != expected or len(set(actual)) != len(actual):
        raise S2JTProjectionError(
            "S2JT_INPUT_BINDING_INVALID",
            "canonical bindings are missing, duplicated, or out of order",
        )
    result = {"VISUAL_FRAME": {}, "AUDIO_HOP": {}}
    for binding in bindings:
        expected_window = (
            _visual_window(binding.position)
            if binding.role == "VISUAL_FRAME"
            else _audio_window(binding.position)
        )
        if (binding.window_start_tick, binding.window_end_tick) != expected_window:
            raise S2JTProjectionError(
                "S2JT_INPUT_TIME_INVALID", "canonical input time changed"
            )
        result[binding.role][binding.position] = binding
    return result


def project_s2jo_reduction_to_time_sequences(
    reduction: CanonicalReductionResultV1,
) -> S2JTTimedSequenceProjection:
    """Project validated reduced S2-JO states onto their triggering input windows."""

    if not isinstance(reduction, CanonicalReductionResultV1):
        raise S2JTProjectionError(
            "S2JT_REDUCTION_INVALID", "one canonical reduction result is required"
        )
    if not isinstance(reduction.ledger, StreamingResourceLedgerV1):
        raise S2JTProjectionError(
            "S2JT_REDUCTION_INVALID", "streaming ledger is missing"
        )
    episode = reduction.episode_receipt
    reduced = reduction.reduced_receipt
    if reduced.input_episode_digest != episode.functional_episode_digest:
        raise S2JTProjectionError(
            "S2JT_DIGEST_BINDING_INVALID", "reduced and input episode differ"
        )
    rebuilt = CanonicalReducedReceptorSequenceReceiptV1.build(
        episode.functional_episode_digest,
        tuple(reduction.visual_states),
        tuple(reduction.auditory_states),
    )
    if rebuilt != reduced:
        raise S2JTProjectionError(
            "S2JT_REDUCED_STATE_INVALID", "reduced states differ from their receipt"
        )
    bindings = _bindings_by_role(tuple(episode.bindings))

    visual_timed = []
    for index, state in enumerate(reduction.visual_states):
        if (
            state.frame_index != index
            or state.geometry_id != episode.visual_geometry_id
            or tuple(state.carrier_ids) != S2JO_VISUAL_CONFIG.carrier_ids
        ):
            raise S2JTProjectionError(
                "S2JT_VISUAL_STATE_INVALID", "visual state identity or geometry changed"
            )
        binding = bindings["VISUAL_FRAME"][index]
        visual_timed.append(
            OrganismTimedReceptorFrame(
                from_visual_receptor_state(state),
                CommonFieldTime(
                    episode.clock_id,
                    binding.window_start_tick,
                    binding.window_end_tick,
                ),
            )
        )

    auditory_timed = []
    auditory_trigger_hops = []
    for index, state in enumerate(reduction.auditory_states):
        trigger_hop = index + S2JO_AUDIO_CONFIG.warmup_hops - 1
        if (
            state.snapshot_index != index
            or state.geometry_id != episode.audio_geometry_id
            or tuple(state.carrier_ids) == ()
            or len(state.carrier_ids) != S2JO_AUDIO_CONFIG.band_count
            or state.window_start_sample != index * S2JO_AUDIO_CONFIG.hop_size
            or state.window_end_sample
            != (index + S2JO_AUDIO_CONFIG.warmup_hops)
            * S2JO_AUDIO_CONFIG.hop_size
        ):
            raise S2JTProjectionError(
                "S2JT_AUDITORY_STATE_INVALID",
                "auditory state is not bound to its complete source window",
            )
        binding = bindings["AUDIO_HOP"].get(trigger_hop)
        if binding is None:
            raise S2JTProjectionError(
                "S2JT_AUDITORY_TRIGGER_INVALID", "triggering audio hop is missing"
            )
        auditory_trigger_hops.append(trigger_hop)
        auditory_timed.append(
            OrganismTimedReceptorFrame(
                from_auditory_receptor_state(state),
                CommonFieldTime(
                    episode.clock_id,
                    binding.window_start_tick,
                    binding.window_end_tick,
                ),
            )
        )

    sequences = (
        ReceptorTimeSequence(
            "auditory", episode.audio_geometry_id, episode.clock_id, tuple(auditory_timed)
        ),
        ReceptorTimeSequence(
            "visual", episode.visual_geometry_id, episode.clock_id, tuple(visual_timed)
        ),
    )
    audit = audit_asynchronous_receptor_events(sequences)
    ticks = tuple(group.completion_tick for group in audit.completion_groups)
    mixed = tuple(
        group.completion_tick
        for group in audit.completion_groups
        if len(group.events) == 2
    )
    payload = {
        "schema": S2JT_PROJECTION_SCHEMA,
        "input_episode_digest": episode.functional_episode_digest,
        "reduced_sequence_digest": reduced.reduced_sequence_digest,
        "clock_id": episode.clock_id,
        "sequence_digests": [_sequence_digest(item) for item in sequences],
        "auditory_trigger_hops": auditory_trigger_hops,
        "completion_ticks": list(ticks),
        "mixed_completion_ticks": list(mixed),
        "event_count": audit.total_event_count,
    }
    return S2JTTimedSequenceProjection(
        S2JT_PROJECTION_SCHEMA,
        episode.functional_episode_digest,
        reduced.reduced_sequence_digest,
        episode.clock_id,
        sequences,
        tuple(auditory_trigger_hops),
        ticks,
        mixed,
        audit.total_event_count,
        _digest(payload),
    )


def s2jt_default_dock_anatomies() -> dict[str, ReceptorDockAnatomy]:
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=S2JO_AUDIO_CONFIG.band_count,
        visual_grid_columns=S2JO_VISUAL_CONFIG.grid_columns,
        visual_grid_rows=S2JO_VISUAL_CONFIG.grid_rows,
    )
    positions = tuple(
        position for anatomy in anatomies.values() for position in anatomy.positions
    )
    if (
        len(anatomies["auditory"].positions) != 48
        or len(anatomies["visual"].positions) != 288
        or len(positions) != 336
        or len(set(positions)) != 336
        or {row for row, _ in anatomies["auditory"].positions} != {0}
        or {row for row, _ in anatomies["visual"].positions} != set(range(1, 9))
    ):
        raise S2JTProjectionError(
            "S2JT_DOCK_GEOMETRY_INVALID", "default AV dock geometry changed"
        )
    return anatomies


@dataclass(frozen=True, slots=True)
class S2JTFieldTrajectoryPoint:
    batch_index: int
    completion_tick: int
    snapshot_ids: tuple[str, ...]
    modality_ids: tuple[str, ...]
    cumulative_support: int
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    point_digest: str


@dataclass(frozen=True, slots=True)
class S2JTObservedFieldResult:
    schema: str
    handoff: ReceptorProposalHandoff
    trajectory: tuple[S2JTFieldTrajectoryPoint, ...]
    observed_field: SharedMCMField
    direct_run: NeutralAsynchronousFieldRun
    initial_fields_distinct: bool
    initial_fields_zero: bool
    final_components_equal: bool
    final_digests_equal: bool
    result_digest: str


def _field_components(field: SharedMCMField) -> tuple[tuple[float, ...], tuple[float, ...]]:
    return (
        tuple(neuron.activation for neuron in field.layer.neurons),
        tuple(neuron.afterimage for neuron in field.layer.neurons),
    )


def _trajectory_point(
    *,
    batch_index: int,
    completion_tick: int,
    snapshot_ids: tuple[str, ...],
    modality_ids: tuple[str, ...],
    cumulative_support: int,
    activation: tuple[float, ...],
    afterimage: tuple[float, ...],
) -> S2JTFieldTrajectoryPoint:
    payload = {
        "batch_index": batch_index,
        "completion_tick": completion_tick,
        "snapshot_ids": list(snapshot_ids),
        "modality_ids": list(modality_ids),
        "cumulative_support": cumulative_support,
        "activation": list(activation),
        "afterimage": list(afterimage),
    }
    return S2JTFieldTrajectoryPoint(
        batch_index,
        completion_tick,
        snapshot_ids,
        modality_ids,
        cumulative_support,
        activation,
        afterimage,
        _digest(payload),
    )


def run_observed_field_pair(
    sequences: Iterable[ReceptorTimeSequence],
    steps: Iterable[MCMFieldStepTime],
    anatomies: Mapping[str, ReceptorDockAnatomy],
    *,
    expected_dock_count: int,
    field_config: NeutralLocalFieldSubstrateConfig = NeutralLocalFieldSubstrateConfig(1.0),
    afterimage_config: NeutralFastAfterimageConfig = NeutralFastAfterimageConfig(0.5),
    sample_offsets: Iterable[Iterable[int]] = ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
) -> S2JTObservedFieldResult:
    """Run one observed arm and one unchanged direct arm from separate zero fields."""

    sequences_in = tuple(sequences)
    steps_in = tuple(steps)
    anatomies_in = dict(anatomies)
    offsets = tuple(tuple(item) for item in sample_offsets)
    if (
        len(sequences_in) != 2
        or tuple(item.modality_id for item in sequences_in) != ("auditory", "visual")
        or not steps_in
        or isinstance(expected_dock_count, bool)
        or not isinstance(expected_dock_count, int)
        or expected_dock_count <= 0
    ):
        raise S2JTProjectionError(
            "S2JT_FIELD_INPUT_INVALID", "field pair input is incomplete"
        )
    reference_frames = tuple(sequence.frames[0].frame for sequence in sequences_in)
    try:
        observed = build_shared_mcm_field(
            reference_frames, anatomies_in, sample_offsets=offsets
        )
        direct = build_shared_mcm_field(
            reference_frames, anatomies_in, sample_offsets=offsets
        )
    except ValueError as exc:
        raise S2JTProjectionError(
            "S2JT_DOCK_GEOMETRY_INVALID", str(exc)
        ) from exc
    initial_fields_distinct = observed is not direct
    initial_components = (_field_components(observed), _field_components(direct))
    initial_fields_zero = all(
        all(value == 0.0 for component in pair for value in component)
        for pair in initial_components
    )
    if (
        not initial_fields_distinct
        or not initial_fields_zero
        or len(observed.layer.neurons) != expected_dock_count
        or len(direct.layer.neurons) != expected_dock_count
    ):
        raise S2JTProjectionError(
            "S2JT_INITIAL_FIELD_INVALID", "field arms are not separate matching zero states"
        )

    try:
        direct_run = run_neutral_asynchronous_field(
            direct,
            sequences_in,
            steps_in,
            field_config,
            afterimage_config=afterimage_config,
        )
        handoff = handoff_receptor_completion_groups(sequences_in, steps_in)
    except ValueError as exc:
        raise S2JTProjectionError(
            "S2JT_HANDOFF_INVALID", str(exc)
        ) from exc
    if (
        not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != handoff.source_event_count
        or len(handoff.batches) != len(steps_in)
        or any(len(batch.completion_groups) != 1 for batch in handoff.batches)
    ):
        raise S2JTProjectionError(
            "S2JT_EVENT_ASSIGNMENT_INVALID",
            "every fine field step must contain exactly one completion group",
        )

    trajectory_points = []
    cumulative_support = 0
    current = observed
    for batch in handoff.batches:
        group = batch.completion_groups[0]
        if group.completion_tick != batch.step_time.end_tick:
            raise S2JTProjectionError(
                "S2JT_EVENT_TIME_INVALID", "completion escaped its fine field step"
            )
        trajectory = map_proposal_batch_to_transient_docks(batch, current.docks)
        local_inputs = project_transient_docks_to_neuron_inputs(
            trajectory, current.docks
        )
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        observations: list[tuple[int, tuple[float, ...], tuple[float, ...]]] = []

        def observe(tick: int, activation: np.ndarray, afterimage: np.ndarray) -> None:
            observations.append(
                (
                    tick,
                    tuple(float(item) for item in activation),
                    tuple(float(item) for item in afterimage),
                )
            )

        current = advance_neutral_fast_shared_field_transient(
            current,
            distribution,
            local_inputs,
            field_config,
            afterimage_config,
            _state_observer=observe,
        )
        if len(observations) != 1 or observations[0][0] != group.completion_tick:
            raise S2JTProjectionError(
                "S2JT_OBSERVER_INVALID", "observer cardinality or time changed"
            )
        activation, afterimage = _field_components(current)
        if observations[0][1:] != (activation, afterimage):
            raise S2JTProjectionError(
                "S2JT_OBSERVER_INVALID", "observer changed or misreported field state"
            )
        cumulative_support += len(group.timed_frames)
        trajectory_points.append(
            _trajectory_point(
                batch_index=batch.batch_index,
                completion_tick=group.completion_tick,
                snapshot_ids=tuple(item.frame.snapshot_id for item in group.timed_frames),
                modality_ids=tuple(item.frame.modality_id for item in group.timed_frames),
                cumulative_support=cumulative_support,
                activation=activation,
                afterimage=afterimage,
            )
        )

    final_components_equal = _field_components(current) == _field_components(
        direct_run.field
    )
    final_digests_equal = current.snapshot().digest() == direct_run.field.snapshot().digest()
    if not final_components_equal or not final_digests_equal:
        raise S2JTProjectionError(
            "S2JT_DIRECT_FIELD_MISMATCH",
            "observed and direct field arms diverged",
        )
    payload = {
        "schema": S2JT_TRAJECTORY_SCHEMA,
        "source_event_count": handoff.source_event_count,
        "point_digests": [item.point_digest for item in trajectory_points],
        "observed_final_digest": current.snapshot().digest(),
        "direct_final_digest": direct_run.field.snapshot().digest(),
        "initial_fields_distinct": initial_fields_distinct,
        "initial_fields_zero": initial_fields_zero,
        "final_components_equal": final_components_equal,
        "final_digests_equal": final_digests_equal,
    }
    return S2JTObservedFieldResult(
        S2JT_TRAJECTORY_SCHEMA,
        handoff,
        tuple(trajectory_points),
        current,
        direct_run,
        initial_fields_distinct,
        initial_fields_zero,
        final_components_equal,
        final_digests_equal,
        _digest(payload),
    )


def run_s2jt_observed_field(
    projection: S2JTTimedSequenceProjection,
) -> S2JTObservedFieldResult:
    """Materialize the bound full-profile field path; execution remains separately gated."""

    if not S2JT_FULL_EXECUTION_ENABLED:
        raise S2JTProjectionError(
            "S2JT_FULL_EXECUTION_LOCKED",
            "the complete 200 ms field run requires separate authorization",
        )
    if not isinstance(projection, S2JTTimedSequenceProjection):
        raise S2JTProjectionError(
            "S2JT_TIME_PROJECTION_INVALID", "validated timed projection is required"
        )
    partition = partition_receptor_completion_time(
        projection.sequences,
        horizon_start_tick=0,
        horizon_end_tick=S2JO_DURATION_TICKS,
        ticks_per_second=float(S2JO_TICKS_PER_SECOND),
    )
    if len(partition.slices) != 15 or partition.eventful_slice_count != 15:
        raise S2JTProjectionError(
            "S2JT_TIME_PARTITION_INVALID", "full episode must have 15 fine slices"
        )
    return run_observed_field_pair(
        projection.sequences,
        tuple(item.step_time for item in partition.slices),
        s2jt_default_dock_anatomies(),
        expected_dock_count=336,
    )
