"""Private S1-EA1 canonical refined E1 formation adapter; not released."""

from __future__ import annotations

import copy
from dataclasses import dataclass

from .e1_av_history_permutation import build_e1_av_history_permutation
from .e1_completion_aligned_refinement import (
    build_e1_completion_aligned_refinement_plans,
)
from .e1_local_edge_plasticity import (
    E1_CONTRACT_ID,
    E1LocalEdgePlasticityContract,
    build_neutral_e1_state,
)
from .e1_refined_chain_canonical_producer import (
    E1RefinedChainCanonicalProducerBinding,
    _fresh_canonical_field,
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import (
    E1RefinedFormationResult,
    _digest,
    _run_ablated_arm,
    _run_active_arm,
    _state_payload,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)


class E1CanonicalRefinedFormationAdapterError(ValueError):
    """Raised when S1-EA1 canonical formation bindings changed."""


@dataclass(frozen=True, slots=True)
class E1CanonicalRefinedFormationProduction:
    source_provenance: str
    binding_digest: str
    ab_plan_digest: str
    ba_plan_digest: str
    initial_field_digest: str
    initial_state_digest: str
    refinements: tuple[E1RefinedFormationResult, ...]
    production_digest: str

    def __post_init__(self) -> None:
        if self.source_provenance != "canonical-s1du":
            raise E1CanonicalRefinedFormationAdapterError(
                "S1-EA1 source provenance changed"
            )
        for role in (
            "binding_digest",
            "ab_plan_digest",
            "ba_plan_digest",
            "initial_field_digest",
            "initial_state_digest",
            "production_digest",
        ):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1CanonicalRefinedFormationAdapterError(
                    f"{role} is not SHA-256"
                )
        refinements = tuple(self.refinements)
        if tuple(
            (item.refinement_id, item.factor) for item in refinements
        ) != (("r1", 1), ("r2", 2), ("r4", 4)):
            raise E1CanonicalRefinedFormationAdapterError(
                "S1-EA1 requires ordered r1, r2, and r4 results"
            )
        object.__setattr__(self, "refinements", refinements)


def _canonical_inputs(binding: E1RefinedChainCanonicalProducerBinding):
    source = build_e1_av_history_permutation()
    ab = build_e1_completion_aligned_refinement_plans(
        source.history_ab,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    ba = build_e1_completion_aligned_refinement_plans(
        source.history_ba,
        horizon_start_tick=0,
        horizon_end_tick=2_000_000,
        ticks_per_second=1_000_000.0,
    )
    field = _fresh_canonical_field(source)
    state = build_neutral_e1_state(
        field.layer,
        E1LocalEdgePlasticityContract(E1_CONTRACT_ID, 1.0, 1.5, 0.25, 0.5),
    )
    observed = (
        source.history_ab_digest,
        source.history_ba_digest,
        source.permutation_digest,
        ab.digest(),
        ba.digest(),
        _initial_field_digest(field),
        _initial_state_digest(state),
    )
    expected = (
        binding.history_ab_digest,
        binding.history_ba_digest,
        binding.permutation_digest,
        binding.ab_plan_digest,
        binding.ba_plan_digest,
        binding.initial_field_digest,
        binding.initial_state_digest,
    )
    if observed != expected:
        raise E1CanonicalRefinedFormationAdapterError(
            "S1-EA1 canonical source, plan, field, or state binding changed"
        )
    return source, ab, ba, field, state


def produce_e1_canonical_refined_formation(
    binding: E1RefinedChainCanonicalProducerBinding,
) -> E1CanonicalRefinedFormationProduction:
    """Run canonical formation only after a later release gate permits it."""

    if not isinstance(binding, E1RefinedChainCanonicalProducerBinding):
        raise E1CanonicalRefinedFormationAdapterError(
            "S1-EA1 requires the S1-DY canonical binding"
        )
    source, ab_plans, ba_plans, initial_field, initial_state = _canonical_inputs(
        binding
    )
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    results = []
    for ab_plan, ba_plan in zip(ab_plans.plans, ba_plans.plans, strict=True):
        fields = tuple(copy.deepcopy(initial_field) for _ in range(5))
        states = tuple(copy.deepcopy(initial_state) for _ in range(5))
        if len({id(item) for item in fields}) != 5 or len(
            {id(item) for item in states}
        ) != 5:
            raise E1CanonicalRefinedFormationAdapterError(
                "S1-EA1 arm inputs are not object-separated"
            )
        ab_state, ab_audit = _run_active_arm(
            "ab", ab_plan.refinement_id, fields[0], states[0],
            source.history_ab, ab_plan.proposal_steps, substrate, afterimage,
        )
        ba_state, ba_audit = _run_active_arm(
            "ba", ba_plan.refinement_id, fields[1], states[1],
            source.history_ba, ba_plan.proposal_steps, substrate, afterimage,
        )
        identity_state, identity_audit = _run_active_arm(
            "ab_identity", ab_plan.refinement_id, fields[2], states[2],
            source.history_ab, ab_plan.proposal_steps, substrate, afterimage,
        )
        ab_ablated, ab_ablated_audit = _run_ablated_arm(
            "ab_formation_ablated", ab_plan.refinement_id, fields[3], states[3],
            source.history_ab, ab_plan.proposal_steps, substrate, afterimage,
        )
        ba_ablated, ba_ablated_audit = _run_ablated_arm(
            "ba_formation_ablated", ba_plan.refinement_id, fields[4], states[4],
            source.history_ba, ba_plan.proposal_steps, substrate, afterimage,
        )
        audits = (
            ab_audit,
            ba_audit,
            identity_audit,
            ab_ablated_audit,
            ba_ablated_audit,
        )
        if (
            ab_audit.field_digest != ab_ablated_audit.field_digest
            or ba_audit.field_digest != ba_ablated_audit.field_digest
            or ab_audit.field_digest != identity_audit.field_digest
        ):
            raise E1CanonicalRefinedFormationAdapterError(
                "S1-EA1 history backreaction ablation failed"
            )
        payload = {
            "refinement": (ab_plan.refinement_id, ab_plan.factor),
            "states": tuple(
                _state_payload(item)
                for item in (
                    ab_state,
                    ba_state,
                    identity_state,
                    ab_ablated,
                    ba_ablated,
                )
            ),
            "audits": tuple(
                (
                    item.arm_id,
                    item.handoff_digest,
                    item.field_digest,
                    item.source_support_count,
                    item.resource_budget_error,
                )
                for item in audits
            ),
        }
        results.append(
            E1RefinedFormationResult(
                refinement_id=ab_plan.refinement_id,
                factor=ab_plan.factor,
                b_ab=ab_state,
                b_ba=ba_state,
                b_ab_identity=identity_state,
                b_ab_formation_ablated=ab_ablated,
                b_ba_formation_ablated=ba_ablated,
                arm_audits=audits,
                result_digest=_digest(payload),
            )
        )
    production_payload = {
        "source_provenance": "canonical-s1du",
        "binding_digest": binding.digest(),
        "ab_plan_digest": ab_plans.digest(),
        "ba_plan_digest": ba_plans.digest(),
        "initial_field_digest": _initial_field_digest(initial_field),
        "initial_state_digest": _initial_state_digest(initial_state),
        "result_digests": tuple(item.result_digest for item in results),
    }
    return E1CanonicalRefinedFormationProduction(
        source_provenance="canonical-s1du",
        binding_digest=binding.digest(),
        ab_plan_digest=ab_plans.digest(),
        ba_plan_digest=ba_plans.digest(),
        initial_field_digest=_initial_field_digest(initial_field),
        initial_state_digest=_initial_state_digest(initial_state),
        refinements=tuple(results),
        production_digest=_digest(production_payload),
    )
