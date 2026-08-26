"""Opt-in asynchronous receptor execution through the S1-B reference path."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Callable, Iterable

from .field_step_time import MCMFieldStepTime
from .mcm_local_development_state import MCMLocalDevelopmentContract
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_proposal_handoff import (
    ReceptorProposalHandoff,
    handoff_receptor_completion_groups,
)
from .receptor_time_model import ReceptorTimeSequence
from .s1b_reciprocal_accommodation import (
    advance_s1b_reciprocal_shared_field_transient,
)
from .shared_mcm_field import (
    SharedMCMField,
    attach_zero_mcm_local_development,
)
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class S1BAsynchronousFieldRuntimeError(ValueError):
    """Raised before an opt-in S1-B receptor history can become ambiguous."""


@dataclass(frozen=True, slots=True)
class S1BAsynchronousFieldRun:
    """Result of one bounded asynchronous S1-B reference execution."""

    field: SharedMCMField
    handoff: ReceptorProposalHandoff
    source_support_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise S1BAsynchronousFieldRuntimeError(
                "S1-B run result requires one shared MCM field"
            )
        if self.field.substrate is not None or self.field.development is None:
            raise S1BAsynchronousFieldRuntimeError(
                "S1-B run result requires exactly one attached L state"
            )
        if not isinstance(self.handoff, ReceptorProposalHandoff):
            raise S1BAsynchronousFieldRuntimeError(
                "S1-B run result requires one receptor handoff"
            )
        if (
            isinstance(self.source_support_count, bool)
            or not isinstance(self.source_support_count, int)
            or self.source_support_count < 1
        ):
            raise S1BAsynchronousFieldRuntimeError(
                "S1-B run result requires a positive source support count"
            )


def _source_support_key(
    sequence: ReceptorTimeSequence,
    frame_index: int,
) -> tuple[object, ...]:
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
    seen: dict[tuple[object, ...], tuple[float, ...]] = {}
    for sequence in sequences:
        for frame_index, timed_frame in enumerate(sequence.frames):
            key = _source_support_key(sequence, frame_index)
            previous_values = seen.get(key)
            if previous_values is None:
                seen[key] = timed_frame.frame.values
                continue
            if previous_values != timed_frame.frame.values:
                raise S1BAsynchronousFieldRuntimeError(
                    "conflicting technical completions share one source support"
                )
            raise S1BAsynchronousFieldRuntimeError(
                "duplicate technical completion of one source support"
            )
    return len(seen)


def _attach_or_validate_development(
    field: SharedMCMField,
    contract: MCMLocalDevelopmentContract,
) -> SharedMCMField:
    if field.substrate is not None:
        raise S1BAsynchronousFieldRuntimeError(
            "the opt-in S1-B adapter cannot combine M and L states"
        )
    if field.development is None:
        return attach_zero_mcm_local_development(field, contract)
    if field.development.contract != contract:
        raise S1BAsynchronousFieldRuntimeError(
            "continued S1-B execution cannot change the L nature contract"
        )
    return field


def run_s1b_asynchronous_field(
    field: SharedMCMField,
    sequences: Iterable[ReceptorTimeSequence],
    proposal_steps: Iterable[MCMFieldStepTime],
    field_config: NeutralLocalFieldSubstrateConfig,
    development_contract: MCMLocalDevelopmentContract,
    *,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    observer: Callable[[int, object, object, object], None] | None = None,
) -> S1BAsynchronousFieldRun:
    """Advance reduced receptor histories through the explicit S1-B arm."""

    if not isinstance(field, SharedMCMField):
        raise S1BAsynchronousFieldRuntimeError(
            "S1-B runtime requires one shared MCM field"
        )
    if not isinstance(field_config, NeutralLocalFieldSubstrateConfig):
        raise S1BAsynchronousFieldRuntimeError(
            "S1-B runtime requires one explicit fast field configuration"
        )
    if not isinstance(development_contract, MCMLocalDevelopmentContract):
        raise S1BAsynchronousFieldRuntimeError(
            "S1-B runtime requires one fixed L nature contract"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise S1BAsynchronousFieldRuntimeError(
            "S1-B runtime requires one explicit afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config,
        NeutralFieldDissipationConfig,
    ):
        raise S1BAsynchronousFieldRuntimeError(
            "S1-B runtime dissipation configuration is invalid"
        )
    if observer is not None and not callable(observer):
        raise S1BAsynchronousFieldRuntimeError(
            "S1-B runtime observer must be callable"
        )

    sequences_in = tuple(sequences)
    if not sequences_in or any(
        not isinstance(sequence, ReceptorTimeSequence)
        for sequence in sequences_in
    ):
        raise S1BAsynchronousFieldRuntimeError(
            "S1-B runtime requires receptor time sequences"
        )
    steps_in = tuple(proposal_steps)
    if not steps_in or any(
        not isinstance(step, MCMFieldStepTime) for step in steps_in
    ):
        raise S1BAsynchronousFieldRuntimeError(
            "S1-B runtime requires field proposal steps"
        )

    source_support_count = _validate_unique_source_supports(sequences_in)
    try:
        handoff = handoff_receptor_completion_groups(sequences_in, steps_in)
    except ValueError as exc:
        raise S1BAsynchronousFieldRuntimeError(str(exc)) from exc
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
    ):
        raise S1BAsynchronousFieldRuntimeError(
            "S1-B runtime requires every supplied completion inside its horizon"
        )
    if (
        not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != source_support_count
    ):
        raise S1BAsynchronousFieldRuntimeError(
            "S1-B runtime requires every unique source support exactly once"
        )

    try:
        current = _attach_or_validate_development(field, development_contract)
        for batch in handoff.batches:
            trajectory = map_proposal_batch_to_transient_docks(
                batch,
                current.docks,
            )
            local_inputs = project_transient_docks_to_neuron_inputs(
                trajectory,
                current.docks,
            )
            distribution = ReceptorDistribution(
                CommonFieldTime(
                    batch.step_time.clock_id,
                    batch.step_time.start_tick,
                    batch.step_time.end_tick,
                ),
                (),
            )
            current = advance_s1b_reciprocal_shared_field_transient(
                current,
                distribution,
                local_inputs,
                field_config,
                afterimage_config,
                dissipation_config,
                observer=observer,
            )
    except S1BAsynchronousFieldRuntimeError:
        raise
    except ValueError as exc:
        raise S1BAsynchronousFieldRuntimeError(str(exc)) from exc

    return S1BAsynchronousFieldRun(
        field=current,
        handoff=handoff,
        source_support_count=source_support_count,
    )


def s1b_asynchronous_field_runtime_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(S1BAsynchronousFieldRun))
