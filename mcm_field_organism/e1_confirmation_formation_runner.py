"""Private S1-EB3 synthetic-only r2/r4/r8 E1 formation runner."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import math

from .e1_asynchronous_field_runtime import (
    E1AsynchronousFieldRuntimeError,
    run_e1_asynchronous_field,
)
from .e1_av_history_permutation import E1AVHistoryPermutation
from .e1_confirmation_refinement_planner import (
    E1ConfirmationRefinementPlanSet,
    S1_EB_CONTRACT_DIGEST,
    build_e1_confirmation_refinement_plans,
)
from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    validate_e1_state_for_layer,
)
from .e1_refined_confirmation_contract import E1RefinedConfirmationContract
from .e1_refined_formation_runner import (
    _digest,
    _field_digest,
    _handoff_digest,
    _resource_budget_error,
    _state_payload,
)
from .e1_refined_world_formation_contract import (
    S1_DS_HISTORY_AB_DIGEST,
    S1_DS_HISTORY_BA_DIGEST,
)
from .neutral_asynchronous_field_runtime import (
    NeutralAsynchronousFieldRuntimeError,
    run_neutral_asynchronous_field,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .shared_mcm_field import SharedMCMField


class E1ConfirmationFormationRunnerError(ValueError):
    """Raised when the S1-EB3 synthetic formation controls fail."""


_REFINEMENTS = (("r2", 2), ("r4", 4), ("r8", 8))
_ARMS = (
    "ab",
    "ba",
    "ab_identity",
    "ab_formation_ablated",
    "ba_formation_ablated",
)


def _valid_digest(value: str) -> bool:
    return len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1ConfirmationFormationArmAudit:
    refinement_id: str
    arm_id: str
    handoff_digest: str
    field_digest: str
    source_support_count: int
    assigned_event_count: int
    resource_budget_error: float
    formation_enabled: bool
    history_backreaction_enabled: bool
    state_remained_neutral: bool

    def __post_init__(self) -> None:
        if self.refinement_id not in {item[0] for item in _REFINEMENTS}:
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 refinement audit identity changed"
            )
        if self.arm_id not in _ARMS:
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 formation arm identity changed"
            )
        if not _valid_digest(self.handoff_digest) or not _valid_digest(
            self.field_digest
        ):
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 arm digest is not SHA-256"
            )
        if (
            self.source_support_count < 1
            or self.assigned_event_count != self.source_support_count
            or not math.isfinite(self.resource_budget_error)
            or self.resource_budget_error < 0.0
            or self.resource_budget_error > 1e-12
            or self.history_backreaction_enabled is not False
        ):
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 arm failed support, resource, or backreaction control"
            )
        expected_enabled = not self.arm_id.endswith("formation_ablated")
        if self.formation_enabled is not expected_enabled:
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 formation-mode audit changed"
            )
        if not expected_enabled and self.state_remained_neutral is not True:
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 formation ablation changed E1"
            )


@dataclass(frozen=True, slots=True)
class E1ConfirmationFormationResult:
    refinement_id: str
    factor: int
    b_ab: E1LocalEdgePlasticityState
    b_ba: E1LocalEdgePlasticityState
    b_ab_identity: E1LocalEdgePlasticityState
    b_ab_formation_ablated: E1LocalEdgePlasticityState
    b_ba_formation_ablated: E1LocalEdgePlasticityState
    arm_audits: tuple[E1ConfirmationFormationArmAudit, ...]
    result_digest: str

    def __post_init__(self) -> None:
        if (self.refinement_id, self.factor) not in _REFINEMENTS:
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 result refinement changed"
            )
        states = (
            self.b_ab,
            self.b_ba,
            self.b_ab_identity,
            self.b_ab_formation_ablated,
            self.b_ba_formation_ablated,
        )
        if any(not isinstance(item, E1LocalEdgePlasticityState) for item in states):
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 result requires five E1 states"
            )
        if len({id(item) for item in states}) != 5:
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 result states must remain object-separated"
            )
        if self.b_ab != self.b_ab_identity:
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 AB identity repetition changed"
            )
        for state in (
            self.b_ab_formation_ablated,
            self.b_ba_formation_ablated,
        ):
            if any(item.binding != 0.0 for item in state.edge_bindings):
                raise E1ConfirmationFormationRunnerError(
                    "S1-EB3 formation ablation is not neutral"
                )
        audits = tuple(self.arm_audits)
        if tuple(item.arm_id for item in audits) != _ARMS or any(
            item.refinement_id != self.refinement_id for item in audits
        ):
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 result audit inventory changed"
            )
        if not _valid_digest(self.result_digest):
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 result digest is invalid"
            )
        object.__setattr__(self, "arm_audits", audits)


@dataclass(frozen=True, slots=True)
class E1ConfirmationFormationProduction:
    source_provenance: str
    contract_digest: str
    ab_plan_digest: str
    ba_plan_digest: str
    initial_field_digest: str
    initial_state_digest: str
    refinements: tuple[E1ConfirmationFormationResult, ...]
    production_digest: str

    def __post_init__(self) -> None:
        if self.source_provenance != "synthetic-s1eb3":
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 accepts synthetic provenance only"
            )
        for role in (
            "contract_digest",
            "ab_plan_digest",
            "ba_plan_digest",
            "initial_field_digest",
            "initial_state_digest",
            "production_digest",
        ):
            if not _valid_digest(getattr(self, role)):
                raise E1ConfirmationFormationRunnerError(
                    f"{role} is not SHA-256"
                )
        if self.contract_digest != S1_EB_CONTRACT_DIGEST:
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 contract binding changed"
            )
        refinements = tuple(self.refinements)
        if tuple(
            (item.refinement_id, item.factor) for item in refinements
        ) != _REFINEMENTS:
            raise E1ConfirmationFormationRunnerError(
                "S1-EB3 production requires ordered r2, r4, and r8 results"
            )
        object.__setattr__(self, "refinements", refinements)


def _run_arm(
    arm_id,
    refinement_id,
    field,
    state,
    sequences,
    proposal_steps,
    substrate_config,
    afterimage_config,
    *,
    formation_enabled,
):
    if formation_enabled:
        run = run_e1_asynchronous_field(
            field,
            state,
            sequences,
            proposal_steps,
            substrate_config,
            afterimage_config,
            backreaction_enabled=False,
        )
        output_state = run.e1_state
    else:
        run = run_neutral_asynchronous_field(
            field,
            sequences,
            proposal_steps,
            substrate_config,
            afterimage_config=afterimage_config,
        )
        output_state = state
    audit = E1ConfirmationFormationArmAudit(
        refinement_id=refinement_id,
        arm_id=arm_id,
        handoff_digest=_handoff_digest(run.handoff),
        field_digest=_field_digest(run.field),
        source_support_count=run.source_support_count,
        assigned_event_count=run.handoff.assigned_event_count,
        resource_budget_error=_resource_budget_error(run.field, output_state),
        formation_enabled=formation_enabled,
        history_backreaction_enabled=False,
        state_remained_neutral=all(
            item.binding == 0.0 for item in output_state.edge_bindings
        ),
    )
    return output_state, audit


def run_synthetic_e1_confirmation_formation(
    contract: E1RefinedConfirmationContract,
    source: E1AVHistoryPermutation,
    ab_plans: E1ConfirmationRefinementPlanSet,
    ba_plans: E1ConfirmationRefinementPlanSet,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1ConfirmationFormationProduction:
    """Exercise r2/r4/r8 formation with noncanonical synthetic sources only."""

    if not isinstance(contract, E1RefinedConfirmationContract) or (
        contract.digest() != S1_EB_CONTRACT_DIGEST
    ):
        raise E1ConfirmationFormationRunnerError(
            "S1-EB3 requires the current S1-EB contract"
        )
    if not isinstance(source, E1AVHistoryPermutation):
        raise E1ConfirmationFormationRunnerError(
            "S1-EB3 requires one synthetic AB/BA source"
        )
    if (
        source.history_ab_digest == S1_DS_HISTORY_AB_DIGEST
        or source.history_ba_digest == S1_DS_HISTORY_BA_DIGEST
    ):
        raise E1ConfirmationFormationRunnerError(
            "S1-EB3 rejects canonical AB/BA sources"
        )
    if not isinstance(ab_plans, E1ConfirmationRefinementPlanSet) or not isinstance(
        ba_plans, E1ConfirmationRefinementPlanSet
    ):
        raise E1ConfirmationFormationRunnerError(
            "S1-EB3 requires two confirmation plan sets"
        )
    if not isinstance(initial_field, SharedMCMField) or (
        initial_field.layer.tick != 0
        or initial_field.last_distribution is not None
        or initial_field.substrate is not None
    ):
        raise E1ConfirmationFormationRunnerError(
            "S1-EB3 requires one fresh initial field"
        )
    try:
        validate_e1_state_for_layer(initial_field.layer, initial_state)
    except E1LocalEdgePlasticityError as exc:
        raise E1ConfirmationFormationRunnerError(str(exc)) from exc
    if any(item.binding != 0.0 for item in initial_state.edge_bindings):
        raise E1ConfirmationFormationRunnerError(
            "S1-EB3 requires one neutral initial E1 state"
        )
    if substrate_config != NeutralLocalFieldSubstrateConfig(1.0) or (
        afterimage_config != NeutralFastAfterimageConfig(0.5)
    ):
        raise E1ConfirmationFormationRunnerError(
            "S1-EB3 field configuration changed"
        )
    first = ab_plans.plans[0]
    expected_ab = build_e1_confirmation_refinement_plans(
        contract,
        source.history_ab,
        horizon_start_tick=first.horizon_start_tick,
        horizon_end_tick=first.horizon_end_tick,
        ticks_per_second=first.proposal_steps[0].ticks_per_second,
    )
    expected_ba = build_e1_confirmation_refinement_plans(
        contract,
        source.history_ba,
        horizon_start_tick=first.horizon_start_tick,
        horizon_end_tick=first.horizon_end_tick,
        ticks_per_second=first.proposal_steps[0].ticks_per_second,
    )
    if expected_ab.digest() != ab_plans.digest() or expected_ba.digest() != ba_plans.digest():
        raise E1ConfirmationFormationRunnerError(
            "S1-EB3 plans do not match their synthetic sources"
        )
    initial_field_digest = _digest(
        {
            "layer": initial_field.layer.digest(),
            "docks": tuple(
                (dock.dock_id, dock.dock_map.pairs)
                for dock in initial_field.docks
            ),
        }
    )
    initial_state_digest = _digest(_state_payload(initial_state))
    results = []
    try:
        for ab_plan, ba_plan in zip(ab_plans.plans, ba_plans.plans, strict=True):
            fields = tuple(copy.deepcopy(initial_field) for _ in range(5))
            states = tuple(copy.deepcopy(initial_state) for _ in range(5))
            if len({id(item) for item in fields}) != 5 or len(
                {id(item) for item in states}
            ) != 5:
                raise E1ConfirmationFormationRunnerError(
                    "S1-EB3 arm inputs are not object-separated"
                )
            arm_specs = (
                ("ab", source.history_ab, ab_plan.proposal_steps, True),
                ("ba", source.history_ba, ba_plan.proposal_steps, True),
                (
                    "ab_identity",
                    source.history_ab,
                    ab_plan.proposal_steps,
                    True,
                ),
                (
                    "ab_formation_ablated",
                    source.history_ab,
                    ab_plan.proposal_steps,
                    False,
                ),
                (
                    "ba_formation_ablated",
                    source.history_ba,
                    ba_plan.proposal_steps,
                    False,
                ),
            )
            outputs = tuple(
                _run_arm(
                    arm_id,
                    ab_plan.refinement_id,
                    fields[index],
                    states[index],
                    sequences,
                    proposal_steps,
                    substrate_config,
                    afterimage_config,
                    formation_enabled=enabled,
                )
                for index, (
                    arm_id,
                    sequences,
                    proposal_steps,
                    enabled,
                ) in enumerate(arm_specs)
            )
            output_states = tuple(item[0] for item in outputs)
            audits = tuple(item[1] for item in outputs)
            if (
                audits[0].field_digest != audits[2].field_digest
                or audits[0].field_digest != audits[3].field_digest
                or audits[1].field_digest != audits[4].field_digest
            ):
                raise E1ConfirmationFormationRunnerError(
                    "S1-EB3 history backreaction ablation failed"
                )
            payload = {
                "refinement": (ab_plan.refinement_id, ab_plan.factor),
                "states": tuple(_state_payload(item) for item in output_states),
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
                E1ConfirmationFormationResult(
                    refinement_id=ab_plan.refinement_id,
                    factor=ab_plan.factor,
                    b_ab=output_states[0],
                    b_ba=output_states[1],
                    b_ab_identity=output_states[2],
                    b_ab_formation_ablated=output_states[3],
                    b_ba_formation_ablated=output_states[4],
                    arm_audits=audits,
                    result_digest=_digest(payload),
                )
            )
    except (
        E1ConfirmationFormationRunnerError,
        E1AsynchronousFieldRuntimeError,
        NeutralAsynchronousFieldRuntimeError,
        ValueError,
    ) as exc:
        if isinstance(exc, E1ConfirmationFormationRunnerError):
            raise
        raise E1ConfirmationFormationRunnerError(str(exc)) from exc
    if (
        initial_field.layer.tick != 0
        or initial_field.last_distribution is not None
        or _digest(_state_payload(initial_state)) != initial_state_digest
    ):
        raise E1ConfirmationFormationRunnerError(
            "S1-EB3 changed an initial input"
        )
    production_payload = {
        "source_provenance": "synthetic-s1eb3",
        "contract_digest": contract.digest(),
        "ab_plan_digest": ab_plans.digest(),
        "ba_plan_digest": ba_plans.digest(),
        "initial_field_digest": initial_field_digest,
        "initial_state_digest": initial_state_digest,
        "result_digests": tuple(item.result_digest for item in results),
    }
    return E1ConfirmationFormationProduction(
        source_provenance="synthetic-s1eb3",
        contract_digest=contract.digest(),
        ab_plan_digest=ab_plans.digest(),
        ba_plan_digest=ba_plans.digest(),
        initial_field_digest=initial_field_digest,
        initial_state_digest=initial_state_digest,
        refinements=tuple(results),
        production_digest=_digest(production_payload),
    )
