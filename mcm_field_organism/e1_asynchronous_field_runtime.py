"""Private bounded asynchronous AV composition for transient E1/S/H."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    validate_e1_state_for_layer,
)
from .e1_transient_coupled_field import (
    E1TransientCoupledFieldError,
    E1TransientCoupledFieldStepResult,
    advance_e1_coupled_fast_shared_field_transient,
)
from .field_step_time import MCMFieldStepTime
from .neutral_asynchronous_field_runtime import _validate_unique_source_supports
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
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1AsynchronousFieldRuntimeError(ValueError):
    """Raised when a bounded transient E1 run is incomplete or ambiguous."""


@dataclass(frozen=True, slots=True)
class E1AsynchronousFieldRun:
    """Complete private run with E1 kept outside the neutral field snapshot."""

    field: SharedMCMField
    e1_state: E1LocalEdgePlasticityState
    handoff: ReceptorProposalHandoff
    source_support_count: int
    steps: tuple[E1TransientCoupledFieldStepResult, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.field, SharedMCMField):
            raise E1AsynchronousFieldRuntimeError("run requires one shared field")
        if not isinstance(self.e1_state, E1LocalEdgePlasticityState):
            raise E1AsynchronousFieldRuntimeError("run requires one E1 state")
        if not isinstance(self.handoff, ReceptorProposalHandoff):
            raise E1AsynchronousFieldRuntimeError("run requires one handoff")
        if (
            isinstance(self.source_support_count, bool)
            or not isinstance(self.source_support_count, int)
            or self.source_support_count < 1
        ):
            raise E1AsynchronousFieldRuntimeError(
                "run requires a positive source support count"
            )
        steps = tuple(self.steps)
        if (
            not steps
            or any(not isinstance(item, E1TransientCoupledFieldStepResult) for item in steps)
            or steps[-1].field != self.field
            or steps[-1].e1_state != self.e1_state
        ):
            raise E1AsynchronousFieldRuntimeError(
                "run requires one ordered sequence of completed E1 steps"
            )
        try:
            validate_e1_state_for_layer(self.field.layer, self.e1_state)
        except E1LocalEdgePlasticityError as exc:
            raise E1AsynchronousFieldRuntimeError(str(exc)) from exc
        object.__setattr__(self, "steps", steps)


def run_e1_asynchronous_field(
    field: SharedMCMField,
    e1_state: E1LocalEdgePlasticityState,
    sequences: Iterable[ReceptorTimeSequence],
    proposal_steps: Iterable[MCMFieldStepTime],
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
    *,
    backreaction_enabled: bool,
) -> E1AsynchronousFieldRun:
    """Run one complete source history without changing the public AV path."""

    if not isinstance(field, SharedMCMField):
        raise E1AsynchronousFieldRuntimeError("bounded E1 runtime requires one field")
    if not isinstance(substrate_config, NeutralLocalFieldSubstrateConfig):
        raise E1AsynchronousFieldRuntimeError(
            "bounded E1 runtime requires one substrate configuration"
        )
    if not isinstance(afterimage_config, NeutralFastAfterimageConfig):
        raise E1AsynchronousFieldRuntimeError(
            "bounded E1 runtime requires one afterimage configuration"
        )
    if dissipation_config is not None and not isinstance(
        dissipation_config, NeutralFieldDissipationConfig
    ):
        raise E1AsynchronousFieldRuntimeError(
            "bounded E1 runtime dissipation configuration is invalid"
        )
    if not isinstance(backreaction_enabled, bool):
        raise E1AsynchronousFieldRuntimeError(
            "backreaction_enabled must be boolean"
        )
    try:
        validate_e1_state_for_layer(field.layer, e1_state)
    except E1LocalEdgePlasticityError as exc:
        raise E1AsynchronousFieldRuntimeError(str(exc)) from exc
    sequences_in = tuple(sequences)
    steps_in = tuple(proposal_steps)
    if not sequences_in or any(
        not isinstance(item, ReceptorTimeSequence) for item in sequences_in
    ):
        raise E1AsynchronousFieldRuntimeError(
            "bounded E1 runtime requires receptor time sequences"
        )
    if not steps_in:
        raise E1AsynchronousFieldRuntimeError(
            "bounded E1 runtime requires proposal steps"
        )
    try:
        source_support_count = _validate_unique_source_supports(sequences_in)
        handoff = handoff_receptor_completion_groups(sequences_in, steps_in)
    except ValueError as exc:
        raise E1AsynchronousFieldRuntimeError(str(exc)) from exc
    if (
        handoff.completed_before_or_at_start_snapshot_ids
        or handoff.completed_after_horizon_snapshot_ids
        or not handoff.every_in_horizon_event_assigned_once
        or handoff.assigned_event_count != source_support_count
    ):
        raise E1AsynchronousFieldRuntimeError(
            "bounded E1 runtime requires every unique source support exactly once"
        )

    current_field = field
    current_state = e1_state
    results = []
    try:
        for batch in handoff.batches:
            trajectory = map_proposal_batch_to_transient_docks(
                batch, current_field.docks
            )
            local_inputs = project_transient_docks_to_neuron_inputs(
                trajectory, current_field.docks
            )
            result = advance_e1_coupled_fast_shared_field_transient(
                current_field,
                current_state,
                ReceptorDistribution(
                    CommonFieldTime(
                        batch.step_time.clock_id,
                        batch.step_time.start_tick,
                        batch.step_time.end_tick,
                    ),
                    (),
                ),
                local_inputs,
                substrate_config,
                afterimage_config,
                dissipation_config,
                backreaction_enabled=backreaction_enabled,
            )
            results.append(result)
            current_field = result.field
            current_state = result.e1_state
    except (ValueError, E1TransientCoupledFieldError) as exc:
        raise E1AsynchronousFieldRuntimeError(str(exc)) from exc
    return E1AsynchronousFieldRun(
        current_field,
        current_state,
        handoff,
        source_support_count,
        tuple(results),
    )
