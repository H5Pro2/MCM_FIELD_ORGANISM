"""Private S1-DO canonical two-partition frozen-state transfer producer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .audio_video_field_geometry import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .e1_frozen_state_transfer import (
    LoadedE1FrozenStates,
    _distance,
    _fresh_field_digest,
    load_e1_frozen_states,
)
from .e1_frozen_state_transfer_contract import (
    S1_DK_ARMS,
    S1_DK_METRICS,
    S1_DK_PROBE_DIGEST,
    S1_DK_REQUIRED_IDENTITIES,
    _fixed_probe_sequences,
    _probe_digest,
)
from .e1_frozen_state_transfer_one_shot_contract import S1_DM_PARTITIONS
from .e1_frozen_state_transfer_one_shot_execution import (
    E1FrozenStateTransferExecutionResult,
    E1FrozenStateTransferPartitionResult,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
    advance_frozen_e1_fast_shared_field_transient,
)
from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    validate_e1_state_for_layer,
)
from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff import handoff_receptor_completion_groups
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField, build_shared_mcm_field
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1FrozenStateTransferCanonicalProducerError(ValueError):
    """Raised when the canonical S1-DO bridge is incomplete or changed."""


@dataclass(frozen=True, slots=True)
class E1FrozenStateTransferCanonicalPlan:
    history_report_path: str
    loaded_states: LoadedE1FrozenStates
    probe_sequences: tuple[ReceptorTimeSequence, ...]
    probe_digest: str
    geometry_digest: str
    initial_field_digest: str
    partitions: tuple[tuple[str, tuple[int, ...]], ...]
    arms: tuple[str, ...]
    source_support_count: int
    field_node_count: int
    edge_count: int
    execution_permitted: bool

    def __post_init__(self) -> None:
        if self.probe_digest != S1_DK_PROBE_DIGEST:
            raise E1FrozenStateTransferCanonicalProducerError(
                "canonical probe digest changed"
            )
        if self.partitions != S1_DM_PARTITIONS or self.arms != S1_DK_ARMS:
            raise E1FrozenStateTransferCanonicalProducerError(
                "canonical partition or arm boundary changed"
            )
        if (
            self.source_support_count != 110
            or self.field_node_count != 84
            or self.edge_count != 145
        ):
            raise E1FrozenStateTransferCanonicalProducerError(
                "canonical source or geometry inventory changed"
            )
        if self.execution_permitted is not False:
            raise E1FrozenStateTransferCanonicalProducerError(
                "S1-DO preflight cannot release canonical execution"
            )


def _fresh_canonical_field(
    sequences: tuple[ReceptorTimeSequence, ...],
) -> SharedMCMField:
    auditory, visual = sequences
    return build_shared_mcm_field(
        (auditory.frames[0].frame, visual.frames[0].frame),
        audio_video_dock_anatomies(
            auditory_carrier_count=12,
            visual_grid_columns=6,
            visual_grid_rows=4,
            visual_channel_count=3,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )


def prepare_e1_frozen_state_transfer_canonical_plan(
    history_report_path: Path,
) -> E1FrozenStateTransferCanonicalPlan:
    """Bind canonical inputs and geometry without advancing any field."""

    path = Path(history_report_path).resolve()
    loaded = load_e1_frozen_states(path)
    sequences = _fixed_probe_sequences()
    if _probe_digest(sequences) != S1_DK_PROBE_DIGEST:
        raise E1FrozenStateTransferCanonicalProducerError(
            "canonical reduced A probe changed"
        )
    if tuple(
        (item.modality_id, len(item.frames)) for item in sequences
    ) != (("auditory", 100), ("visual", 10)):
        raise E1FrozenStateTransferCanonicalProducerError(
            "canonical probe frame inventory changed"
        )
    try:
        field = _fresh_canonical_field(sequences)
        validate_e1_state_for_layer(field.layer, loaded.b_ab)
        validate_e1_state_for_layer(field.layer, loaded.b_ba)
    except (ValueError, E1LocalEdgePlasticityError) as exc:
        raise E1FrozenStateTransferCanonicalProducerError(str(exc)) from exc
    return E1FrozenStateTransferCanonicalPlan(
        history_report_path=str(path),
        loaded_states=loaded,
        probe_sequences=sequences,
        probe_digest=S1_DK_PROBE_DIGEST,
        geometry_digest=field.layer.digest(),
        initial_field_digest=_fresh_field_digest(field),
        partitions=S1_DM_PARTITIONS,
        arms=S1_DK_ARMS,
        source_support_count=sum(len(item.frames) for item in sequences),
        field_node_count=len(field.layer.neurons),
        edge_count=len(loaded.b_ab.edge_bindings),
        execution_permitted=False,
    )


def _proposal_steps(
    partition_id: str,
    boundaries: tuple[int, ...],
) -> tuple[MCMFieldStepTime, ...]:
    expected = dict(S1_DM_PARTITIONS).get(partition_id)
    if expected is None or boundaries != expected:
        raise E1FrozenStateTransferCanonicalProducerError(
            "canonical proposal partition changed"
        )
    return tuple(
        MCMFieldStepTime(
            "organism.e1.av-history",
            start,
            end,
            1_000_000.0,
        )
        for start, end in zip(boundaries, boundaries[1:])
    )


def _partition_run(
    plan: E1FrozenStateTransferCanonicalPlan,
    partition_id: str,
    boundaries: tuple[int, ...],
) -> tuple[
    E1FrozenStateTransferPartitionResult,
    tuple[SharedMCMField, ...],
    dict[str, float],
]:
    fields = tuple(_fresh_canonical_field(plan.probe_sequences) for _ in S1_DK_ARMS)
    if len({id(item) for item in fields}) != len(S1_DK_ARMS):
        raise E1FrozenStateTransferCanonicalProducerError(
            "canonical arm fields are not separate"
        )
    initial_digests = tuple(_fresh_field_digest(item) for item in fields)
    if len(set(initial_digests)) != 1 or initial_digests[0] != plan.initial_field_digest:
        raise E1FrozenStateTransferCanonicalProducerError(
            "canonical arm fields are not initially identical"
        )
    steps = _proposal_steps(partition_id, boundaries)
    handoff = handoff_receptor_completion_groups(plan.probe_sequences, steps)
    if (
        handoff.assigned_event_count != 110
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
    ):
        raise E1FrozenStateTransferCanonicalProducerError(
            "canonical probe supports are not assigned exactly once"
        )
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    current = list(fields)
    left = plan.loaded_states.b_ab
    right = plan.loaded_states.b_ba
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, current[0].docks)
        transient_inputs = project_transient_docks_to_neuron_inputs(
            trajectory, current[0].docks
        )
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        current[0] = advance_neutral_fast_shared_field_transient(
            current[0], distribution, transient_inputs, substrate, afterimage
        )
        ab0 = advance_frozen_e1_fast_shared_field_transient(
            current[1], left, distribution, transient_inputs, substrate,
            afterimage, backreaction_enabled=False,
        )
        ba0 = advance_frozen_e1_fast_shared_field_transient(
            current[2], right, distribution, transient_inputs, substrate,
            afterimage, backreaction_enabled=False,
        )
        ab1 = advance_frozen_e1_fast_shared_field_transient(
            current[3], left, distribution, transient_inputs, substrate,
            afterimage, backreaction_enabled=True,
        )
        ba1 = advance_frozen_e1_fast_shared_field_transient(
            current[4], right, distribution, transient_inputs, substrate,
            afterimage, backreaction_enabled=True,
        )
        current[1], current[2], current[3], current[4] = (
            ab0.field, ba0.field, ab1.field, ba1.field
        )
        current[5] = advance_fixed_e1_adapter_fast_shared_field_transient(
            current[5], ab1.applied_adapter, distribution, transient_inputs,
            substrate, afterimage,
        )
        current[6] = advance_fixed_e1_adapter_fast_shared_field_transient(
            current[6], ba1.applied_adapter, distribution, transient_inputs,
            substrate, afterimage,
        )
        if (
            ab0.e1_state is not left
            or ab1.e1_state is not left
            or ba0.e1_state is not right
            or ba1.e1_state is not right
        ):
            raise E1FrozenStateTransferCanonicalProducerError(
                "canonical frozen state object changed"
            )
    final = tuple(current)
    d_ablation = max(
        *(_distance(final[0], final[1], role) for role in ("s", "h")),
        *(_distance(final[0], final[2], role) for role in ("s", "h")),
    )
    d_fixed = max(
        *(_distance(final[3], final[5], role) for role in ("s", "h")),
        *(_distance(final[4], final[6], role) for role in ("s", "h")),
    )
    metrics = {
        "d_pre_s": 0.0,
        "d_pre_h": 0.0,
        "d_active_s": _distance(final[3], final[4], "s"),
        "d_active_h": _distance(final[3], final[4], "h"),
        "d_ablation": d_ablation,
        "d_fixed_adapter": d_fixed,
        "frozen_state_change": 0.0,
    }
    result = E1FrozenStateTransferPartitionResult(
        partition_id=partition_id,
        boundaries=boundaries,
        arm_field_digests=tuple(
            (role, field.snapshot().digest())
            for role, field in zip(S1_DK_ARMS, final, strict=True)
        ),
    )
    return result, final, metrics


def _technical_status(active: float, partition: float) -> str:
    if active > partition:
        return "REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE"
    if active == 0.0 and partition == 0.0:
        return "NO_REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE"
    return "TECHNICALLY_UNDECIDABLE"


def produce_e1_frozen_state_transfer(
    history_report_path: Path,
) -> E1FrozenStateTransferExecutionResult:
    """Execute the exact S1-DO source; do not call before final release."""

    plan = prepare_e1_frozen_state_transfer_canonical_plan(history_report_path)
    runs = tuple(
        _partition_run(plan, partition_id, boundaries)
        for partition_id, boundaries in S1_DM_PARTITIONS
    )
    coarse_result, coarse_fields, coarse_metrics = runs[0]
    split_result, split_fields, split_metrics = runs[1]
    partition_residual = max(
        _distance(first, second, role)
        for first, second in zip(coarse_fields, split_fields, strict=True)
        for role in ("s", "h")
    )
    metric_values = {
        "d_pre_s": max(coarse_metrics["d_pre_s"], split_metrics["d_pre_s"]),
        "d_pre_h": max(coarse_metrics["d_pre_h"], split_metrics["d_pre_h"]),
        "d_active_s": split_metrics["d_active_s"],
        "d_active_h": split_metrics["d_active_h"],
        "d_ablation": max(
            coarse_metrics["d_ablation"], split_metrics["d_ablation"]
        ),
        "d_fixed_adapter": max(
            coarse_metrics["d_fixed_adapter"],
            split_metrics["d_fixed_adapter"],
        ),
        "d_probe_partition": partition_residual,
        "frozen_state_change": 0.0,
    }
    active = max(metric_values["d_active_s"], metric_values["d_active_h"])
    return E1FrozenStateTransferExecutionResult(
        partitions=(coarse_result, split_result),
        metrics=tuple((role, metric_values[role]) for role in S1_DK_METRICS),
        controls=tuple((role, True) for role in S1_DK_REQUIRED_IDENTITIES),
        technical_status=_technical_status(active, partition_residual),
    )
