"""Private S1-EB12 canonical-bound seven-arm probe adapter; locked."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .e1_av_history_permutation import build_e1_av_history_permutation
from .e1_confirmation_canonical_formation_adapter import (
    E1ConfirmationCanonicalFormationProduction,
)
from .e1_confirmation_canonical_probe_handoff import (
    E1ConfirmationCanonicalProbeHandoff,
)
from .e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBinding,
)
from .e1_confirmation_chain_contract import E1ConfirmationChainContract
from .e1_confirmation_formation_runner import E1ConfirmationFormationResult
from .e1_confirmation_refinement_planner import (
    E1ConfirmationRefinementPlan,
    S1_EB_CONTRACT_DIGEST,
    build_e1_confirmation_refinement_plans,
)
from .e1_confirmation_seven_arm_probe import (
    E1ConfirmationProbeResult,
    S1_EB6_FIELD_ROLES,
    _max_distance,
    _state_digest,
    _vector,
)
from .e1_frozen_state_transfer import _fresh_field_digest
from .e1_frozen_state_transfer_contract import (
    _fixed_probe_sequences,
    _probe_digest,
)
from .e1_frozen_transient_probe import (
    advance_fixed_e1_adapter_fast_shared_field_transient,
    advance_frozen_e1_fast_shared_field_transient,
)
from .e1_refined_chain_canonical_producer import (
    _fresh_canonical_field,
    _initial_field_digest,
)
from .e1_refined_confirmation_contract import (
    E1RefinedConfirmationContract,
    build_e1_refined_confirmation_contract,
)
from .e1_refined_formation_runner import _digest
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField
from .transient_dock_trajectory import map_proposal_batch_to_transient_docks
from .transient_neuron_input import project_transient_docks_to_neuron_inputs


class E1ConfirmationCanonicalProbeAdapterError(ValueError):
    """Raised when an S1-EB12 binding, gate, or probe control changed."""


_BINDING_DIGEST = (
    "aae7f9427200c88f60155f884c3ee6a4279941c4ecf878f8490a69e19f7c2d34"
)


def _canonical_probe_inputs(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
):
    corridor = build_e1_refined_confirmation_contract(
        Path(chain_contract.report_path).parent,
        Path(chain_contract.upstream_report_path),
    )
    probe = _fixed_probe_sequences()
    plans = build_e1_confirmation_refinement_plans(
        corridor,
        probe,
        horizon_start_tick=0,
        horizon_end_tick=1_000_000,
        ticks_per_second=1_000_000.0,
    )
    history_source = build_e1_av_history_permutation()

    def field_factory() -> SharedMCMField:
        return _fresh_canonical_field(history_source)

    fresh = field_factory()
    if (
        corridor.digest() != chain_contract.confirmation_contract_digest
        or _probe_digest(probe) != binding.probe_digest
        or plans.digest() != binding.probe_plan_digest
        or fresh.layer.digest() != binding.geometry_digest
        or _initial_field_digest(fresh) != binding.initial_field_digest
    ):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 canonical probe, plans, geometry, or field changed"
        )
    return corridor, probe, plans, field_factory


def _run_bound_probe_core(
    contract: E1RefinedConfirmationContract,
    formed: E1ConfirmationFormationResult,
    field_factory: Callable[[], SharedMCMField],
    probe_sequences: tuple[ReceptorTimeSequence, ...],
    probe_plan: E1ConfirmationRefinementPlan,
    expected_source_digest: str,
) -> E1ConfirmationProbeResult:
    if not isinstance(contract, E1RefinedConfirmationContract) or (
        contract.digest() != S1_EB_CONTRACT_DIGEST
    ):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 requires the current S1-EB contract"
        )
    if not isinstance(formed, E1ConfirmationFormationResult):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 requires one formation result"
        )
    sequences = tuple(probe_sequences)
    if (
        tuple(item.modality_id for item in sequences) != ("auditory", "visual")
        or not all(isinstance(item, ReceptorTimeSequence) for item in sequences)
    ):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 probe source changed"
        )
    source_digest = _probe_digest(sequences)
    if source_digest != expected_source_digest:
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 probe source does not match its binding"
        )
    if not isinstance(probe_plan, E1ConfirmationRefinementPlan) or (
        (formed.refinement_id, formed.factor)
        != (probe_plan.refinement_id, probe_plan.factor)
    ):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 formation and probe refinement do not match"
        )
    steps = tuple(probe_plan.proposal_steps)
    expected = build_e1_confirmation_refinement_plans(
        contract,
        sequences,
        horizon_start_tick=probe_plan.horizon_start_tick,
        horizon_end_tick=probe_plan.horizon_end_tick,
        ticks_per_second=steps[0].ticks_per_second,
    )
    expected_plan = next(
        item
        for item in expected.plans
        if item.refinement_id == probe_plan.refinement_id
    )
    if expected_plan.digest() != probe_plan.digest():
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 probe plan does not match its source"
        )
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    if not callable(field_factory):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 field factory changed"
        )
    fields = tuple(field_factory() for _ in S1_EB6_FIELD_ROLES)
    if any(not isinstance(item, SharedMCMField) for item in fields) or len(
        {id(item) for item in fields}
    ) != len(fields):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 requires seven object-separated fields"
        )
    if len({_fresh_field_digest(item) for item in fields}) != 1:
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 probe fields are not initially identical"
        )
    handoff = probe_plan.handoff
    supports_once = (
        handoff.assigned_event_count == sum(len(item.frames) for item in sequences)
        and handoff.every_in_horizon_event_assigned_once
        and not handoff.completed_before_or_at_start_snapshot_ids
        and not handoff.completed_after_horizon_snapshot_ids
    )
    if not supports_once:
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 probe supports are not assigned exactly once"
        )

    current = list(fields)
    ab_state = formed.b_ab
    ba_state = formed.b_ba
    pre_ab_digest = _state_digest(ab_state)
    pre_ba_digest = _state_digest(ba_state)
    for batch in handoff.batches:
        trajectory = map_proposal_batch_to_transient_docks(
            batch, current[0].docks
        )
        inputs = project_transient_docks_to_neuron_inputs(
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
            current[0], distribution, inputs, substrate, afterimage
        )
        ab_active = advance_frozen_e1_fast_shared_field_transient(
            current[1],
            ab_state,
            distribution,
            inputs,
            substrate,
            afterimage,
            backreaction_enabled=True,
        )
        ba_active = advance_frozen_e1_fast_shared_field_transient(
            current[2],
            ba_state,
            distribution,
            inputs,
            substrate,
            afterimage,
            backreaction_enabled=True,
        )
        ab_ablated = advance_frozen_e1_fast_shared_field_transient(
            current[3],
            ab_state,
            distribution,
            inputs,
            substrate,
            afterimage,
            backreaction_enabled=False,
        )
        ba_ablated = advance_frozen_e1_fast_shared_field_transient(
            current[4],
            ba_state,
            distribution,
            inputs,
            substrate,
            afterimage,
            backreaction_enabled=False,
        )
        current[1], current[2], current[3], current[4] = (
            ab_active.field,
            ba_active.field,
            ab_ablated.field,
            ba_ablated.field,
        )
        current[5] = advance_fixed_e1_adapter_fast_shared_field_transient(
            current[5],
            ab_active.applied_adapter,
            distribution,
            inputs,
            substrate,
            afterimage,
        )
        current[6] = advance_fixed_e1_adapter_fast_shared_field_transient(
            current[6],
            ba_active.applied_adapter,
            distribution,
            inputs,
            substrate,
            afterimage,
        )
        if (
            ab_active.e1_state is not ab_state
            or ab_ablated.e1_state is not ab_state
            or ba_active.e1_state is not ba_state
            or ba_ablated.e1_state is not ba_state
        ):
            raise E1ConfirmationCanonicalProbeAdapterError(
                "S1-EB12 changed a frozen E1 state object"
            )

    final = tuple(current)
    values = {
        "refinement_id": formed.refinement_id,
        "factor": formed.factor,
        "probe_source_digest": source_digest,
        "probe_plan_digest": probe_plan.digest(),
        "field_digests": tuple(
            (role, item.snapshot().digest())
            for role, item in zip(S1_EB6_FIELD_ROLES, final, strict=True)
        ),
        "ab_active_s": _vector(final[1], "s"),
        "ba_active_s": _vector(final[2], "s"),
        "ab_active_h": _vector(final[1], "h"),
        "ba_active_h": _vector(final[2], "h"),
        "pre_probe_ab_state_digest": pre_ab_digest,
        "pre_probe_ba_state_digest": pre_ba_digest,
        "post_probe_ab_state_digest": _state_digest(ab_state),
        "post_probe_ba_state_digest": _state_digest(ba_state),
        "probe_ablation_residual": _max_distance(final[0], (final[3], final[4])),
        "fixed_adapter_residual": max(
            _max_distance(final[1], (final[5],)),
            _max_distance(final[2], (final[6],)),
        ),
        "initial_fields_identical_and_separate": True,
        "supports_assigned_once": supports_once,
    }
    return E1ConfirmationProbeResult(**values, result_digest=_digest(values))


def run_e1_confirmation_canonical_seven_arm_probe(
    binding: E1ConfirmationCanonicalProducerBinding,
    chain_contract: E1ConfirmationChainContract,
    formation: E1ConfirmationCanonicalFormationProduction,
    handoff: E1ConfirmationCanonicalProbeHandoff,
) -> tuple[E1ConfirmationProbeResult, ...]:
    """Reserve the canonical probe entrypoint while its release is closed."""

    if not isinstance(binding, E1ConfirmationCanonicalProducerBinding) or (
        binding.digest() != _BINDING_DIGEST
    ):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 requires the unchanged S1-EB9 binding"
        )
    if not isinstance(chain_contract, E1ConfirmationChainContract) or (
        chain_contract.digest() != binding.chain_contract_digest
    ):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 requires the bound S1-EB4 chain contract"
        )
    if not isinstance(handoff, E1ConfirmationCanonicalProbeHandoff) or (
        handoff.binding_digest != binding.digest()
        or handoff.chain_contract_digest != chain_contract.digest()
    ):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 requires the bound S1-EB11 handoff"
        )
    if not isinstance(formation, E1ConfirmationCanonicalFormationProduction) or (
        formation.production_digest != handoff.formation_production_digest
    ):
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 formation does not match its probe handoff"
        )
    if handoff.probe_execution_permitted is not True:
        raise E1ConfirmationCanonicalProbeAdapterError(
            "S1-EB12 canonical probe execution remains locked"
        )
    corridor, probe, plans, field_factory = _canonical_probe_inputs(
        binding, chain_contract
    )
    return tuple(
        _run_bound_probe_core(
            corridor,
            formed,
            field_factory,
            probe,
            plan,
            binding.probe_digest,
        )
        for formed, plan in zip(
            formation.refinements, plans.plans, strict=True
        )
    )
