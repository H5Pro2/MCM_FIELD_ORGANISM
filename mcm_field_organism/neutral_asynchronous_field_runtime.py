"""Bounded asynchronous receptor execution on the neutral shared field."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Iterable

from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_shared_field_transient,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff_audit import (
    ReceptorProposalHandoff,
    handoff_receptor_completion_groups,
)
from .receptor_time_alignment import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class NeutralAsynchronousFieldRuntimeError(ValueError):
    """Raised before a bounded asynchronous field run can become ambiguous."""


@dataclass(frozen=True, slots=True)
class NeutralAsynchronousFieldRun:
    """Compact result of one complete bounded receptor-to-field run."""

    field: SharedMCMField
    handoff: ReceptorProposalHandoff
    source_support_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise NeutralAsynchronousFieldRuntimeError(
                "run result requires one shared MCM field"
            )
        if not isinstance(self.handoff, ReceptorProposalHandoff):
            raise NeutralAsynchronousFieldRuntimeError(
                "run result requires one receptor handoff"
            )
        if (
            isinstance(self.source_support_count, bool)
            or not isinstance(self.source_support_count, int)
            or self.source_support_count < 1
        ):
            raise NeutralAsynchronousFieldRuntimeError(
                "run result requires a positive source support count"
            )


def _source_support_key(sequence: ReceptorTimeSequence, frame_index: int) -> tuple:
    timed_frame = sequence.frames[frame_index]
    frame = timed_frame.frame
    return (
        frame.modality_id,
        frame.clock_id,
        frame.window_start_tick,
        frame.window_end_tick,
    )


def _validate_unique_source_supports(
    sequences: tuple[ReceptorTimeSequence, ...],
) -> int:
    seen: dict[tuple, tuple[float, ...]] = {}
    for sequence in sequences:
        for frame_index, timed_frame in enumerate(sequence.frames):
            key = _source_support_key(sequence, frame_index)
            previous_values = seen.get(key)
            if previous_values is None:
                seen[key] = timed_frame.frame.values
                continue
            if previous_values != timed_frame.frame.values:
                raise NeutralAsynchronousFieldRuntimeError(
                    "conflicting technical completions share one source support"
                )
            raise NeutralAsynchronousFieldRuntimeError(
                "duplicate technical completion of one source support"
            )
    return len(seen)


def run_neutral_asynchronous_field(
    field: SharedMCMField,
    sequences: Iterable[ReceptorTimeSequence],
    proposal_steps: Iterable[MCMFieldStepTime],
    config: NeutralLocalFieldSubstrateConfig,
) -> NeutralAsynchronousFieldRun:
    """Run one complete bounded source history without counting support twice."""

    if not isinstance(field, SharedMCMField):
        raise NeutralAsynchronousFieldRuntimeError(
            "bounded runtime requires one shared MCM field"
        )
    if not isinstance(config, NeutralLocalFieldSubstrateConfig):
        raise NeutralAsynchronousFieldRuntimeError(
            "bounded runtime requires one explicit field configuration"
        )
    sequences_in = tuple(sequences)
    if not sequences_in or any(
        not isinstance(sequence, ReceptorTimeSequence)
        for sequence in sequences_in
    ):
        raise NeutralAsynchronousFieldRuntimeError(
            "bounded runtime requires receptor time sequences"
        )
    steps_in = tuple(proposal_steps)
    if not steps_in:
        raise NeutralAsynchronousFieldRuntimeError(
            "bounded runtime requires proposal steps"
        )

    source_support_count = _validate_unique_source_supports(sequences_in)
    try:
        handoff = handoff_receptor_completion_groups(sequences_in, steps_in)
    except ValueError as exc:
        raise NeutralAsynchronousFieldRuntimeError(str(exc)) from exc
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
    ):
        raise NeutralAsynchronousFieldRuntimeError(
            "bounded runtime requires every supplied completion inside its horizon"
        )
    if (
        not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != source_support_count
    ):
        raise NeutralAsynchronousFieldRuntimeError(
            "bounded runtime requires every unique source support exactly once"
        )

    current = field
    try:
        for batch in handoff.batches:
            trajectory = map_proposal_batch_to_transient_docks(
                batch,
                current.docks,
            )
            local_inputs = project_transient_docks_to_neuron_inputs(
                trajectory,
                current.docks,
            )
            current = advance_neutral_shared_field_transient(
                current,
                ReceptorDistribution(
                    CommonFieldTime(
                        batch.step_time.clock_id,
                        batch.step_time.start_tick,
                        batch.step_time.end_tick,
                    ),
                    (),
                ),
                local_inputs,
                config,
            )
    except ValueError as exc:
        raise NeutralAsynchronousFieldRuntimeError(str(exc)) from exc

    return NeutralAsynchronousFieldRun(
        field=current,
        handoff=handoff,
        source_support_count=source_support_count,
    )


def neutral_asynchronous_field_runtime_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(NeutralAsynchronousFieldRun))
