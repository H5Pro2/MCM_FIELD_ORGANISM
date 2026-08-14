"""Private S1-EA0 seven-arm frozen probe runner for synthetic E1 states."""

from __future__ import annotations

from collections.abc import Callable
import math

from .e1_frozen_state_transfer import _distance, _field_vector, _fresh_field_digest
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
    advance_frozen_e1_fast_shared_field_transient,
)
from .e1_refined_chain_producer_composition import (
    E1RefinedProbeCompositionResult,
    S1_DZ_PROBE_FIELD_ROLES,
    _state_digest,
)
from .e1_refined_formation_runner import E1RefinedFormationResult
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
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1RefinedSevenArmProbeRunnerError(ValueError):
    """Raised when an S1-EA0 synthetic frozen probe loses an invariant."""


def _max_distance(
    reference: SharedMCMField,
    candidates: tuple[SharedMCMField, ...],
) -> float:
    return max(
        _distance(reference, candidate, role)
        for candidate in candidates
        for role in ("s", "h")
    )


def _vector(field: SharedMCMField, role: str) -> tuple[float, ...]:
    values = tuple(float(value) for value in _field_vector(field, role))
    if not values or any(not math.isfinite(value) for value in values):
        raise E1RefinedSevenArmProbeRunnerError(
            "S1-EA0 probe field vector is invalid"
        )
    return values


def run_private_e1_refined_seven_arm_probe(
    formed: E1RefinedFormationResult,
    field_factory: Callable[[], SharedMCMField],
    probe_sequences: tuple[ReceptorTimeSequence, ...],
    proposal_steps: tuple[MCMFieldStepTime, ...],
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1RefinedProbeCompositionResult:
    """Run one private frozen probe without persistence or claim roles."""

    if not isinstance(formed, E1RefinedFormationResult):
        raise E1RefinedSevenArmProbeRunnerError(
            "S1-EA0 requires one synthetic refined formation result"
        )
    if not callable(field_factory):
        raise E1RefinedSevenArmProbeRunnerError(
            "S1-EA0 requires one fresh field factory"
        )
    sequences = tuple(probe_sequences)
    steps = tuple(proposal_steps)
    if (
        tuple(item.modality_id for item in sequences) != ("auditory", "visual")
        or not steps
        or substrate_config != NeutralLocalFieldSubstrateConfig(1.0)
        or afterimage_config != NeutralFastAfterimageConfig(0.5)
    ):
        raise E1RefinedSevenArmProbeRunnerError(
            "S1-EA0 probe source, steps, or field configuration changed"
        )
    fields = tuple(field_factory() for _ in S1_DZ_PROBE_FIELD_ROLES)
    if any(not isinstance(item, SharedMCMField) for item in fields) or len(
        {id(item) for item in fields}
    ) != len(fields):
        raise E1RefinedSevenArmProbeRunnerError(
            "S1-EA0 requires seven object-separated fields"
        )
    initial_digests = tuple(_fresh_field_digest(item) for item in fields)
    if len(set(initial_digests)) != 1:
        raise E1RefinedSevenArmProbeRunnerError(
            "S1-EA0 probe fields are not initially identical"
        )
    handoff = handoff_receptor_completion_groups(sequences, steps)
    expected_supports = sum(len(item.frames) for item in sequences)
    supports_once = (
        handoff.assigned_event_count == expected_supports
        and handoff.every_in_horizon_event_assigned_once
        and not handoff.completed_before_or_at_start_snapshot_ids
        and not handoff.completed_after_horizon_snapshot_ids
    )
    if not supports_once:
        raise E1RefinedSevenArmProbeRunnerError(
            "S1-EA0 probe supports are not assigned exactly once"
        )

    current = list(fields)
    ab_state = formed.b_ab
    ba_state = formed.b_ba
    ab_digest = _state_digest(ab_state)
    ba_digest = _state_digest(ba_state)
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(batch, current[0].docks)
        inputs = project_transient_docks_to_neuron_inputs(trajectory, current[0].docks)
        distribution = ReceptorDistribution(
            CommonFieldTime(
                batch.step_time.clock_id,
                batch.step_time.start_tick,
                batch.step_time.end_tick,
            ),
            (),
        )
        current[0] = advance_neutral_fast_shared_field_transient(
            current[0], distribution, inputs, substrate_config, afterimage_config
        )
        ab_active = advance_frozen_e1_fast_shared_field_transient(
            current[1], ab_state, distribution, inputs, substrate_config,
            afterimage_config, backreaction_enabled=True,
        )
        ba_active = advance_frozen_e1_fast_shared_field_transient(
            current[2], ba_state, distribution, inputs, substrate_config,
            afterimage_config, backreaction_enabled=True,
        )
        ab_ablated = advance_frozen_e1_fast_shared_field_transient(
            current[3], ab_state, distribution, inputs, substrate_config,
            afterimage_config, backreaction_enabled=False,
        )
        ba_ablated = advance_frozen_e1_fast_shared_field_transient(
            current[4], ba_state, distribution, inputs, substrate_config,
            afterimage_config, backreaction_enabled=False,
        )
        current[1], current[2], current[3], current[4] = (
            ab_active.field,
            ba_active.field,
            ab_ablated.field,
            ba_ablated.field,
        )
        current[5] = advance_fixed_e1_adapter_fast_shared_field_transient(
            current[5], ab_active.applied_adapter, distribution, inputs,
            substrate_config, afterimage_config,
        )
        current[6] = advance_fixed_e1_adapter_fast_shared_field_transient(
            current[6], ba_active.applied_adapter, distribution, inputs,
            substrate_config, afterimage_config,
        )
        if (
            ab_active.e1_state is not ab_state
            or ab_ablated.e1_state is not ab_state
            or ba_active.e1_state is not ba_state
            or ba_ablated.e1_state is not ba_state
        ):
            raise E1RefinedSevenArmProbeRunnerError(
                "S1-EA0 changed a frozen E1 state object"
            )

    final = tuple(current)
    return E1RefinedProbeCompositionResult(
        refinement_id=formed.refinement_id,
        factor=formed.factor,
        field_digests=tuple(
            (role, field.snapshot().digest())
            for role, field in zip(S1_DZ_PROBE_FIELD_ROLES, final, strict=True)
        ),
        ab_active_s=_vector(final[1], "s"),
        ba_active_s=_vector(final[2], "s"),
        ab_active_h=_vector(final[1], "h"),
        ba_active_h=_vector(final[2], "h"),
        post_probe_ab_state_digest=_state_digest(ab_state),
        post_probe_ba_state_digest=_state_digest(ba_state),
        probe_ablation_residual=_max_distance(final[0], (final[3], final[4])),
        fixed_adapter_residual=max(
            _max_distance(final[1], (final[5],)),
            _max_distance(final[2], (final[6],)),
        ),
        initial_fields_identical_and_separate=True,
        supports_assigned_once=supports_once,
    )


def run_synthetic_e1_refined_seven_arm_probe(
    formed: E1RefinedFormationResult,
    field_factory: Callable[[], SharedMCMField],
    probe_sequences: tuple[ReceptorTimeSequence, ...],
    proposal_steps: tuple[MCMFieldStepTime, ...],
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1RefinedProbeCompositionResult:
    """Keep the explicit synthetic S1-EA0 entry separate from canonical wiring."""

    return run_private_e1_refined_seven_arm_probe(
        formed,
        field_factory,
        probe_sequences,
        proposal_steps,
        substrate_config,
        afterimage_config,
    )
