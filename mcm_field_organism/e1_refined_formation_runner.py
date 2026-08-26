"""Private S1-DV synthetic-only runner for refined E1 state formation."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import json
import math

from .e1_asynchronous_field_runtime import (
    E1AsynchronousFieldRuntimeError,
    run_e1_asynchronous_field,
)
from .e1_av_history_permutation import E1AVHistoryPermutation
from .e1_completion_aligned_refinement import (
    E1CompletionAlignedRefinementPlanSet,
    build_e1_completion_aligned_refinement_plans,
)
from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityError,
    E1LocalEdgePlasticityState,
    e1_free_node_resources,
    validate_e1_state_for_layer,
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


class E1RefinedFormationRunnerError(ValueError):
    """Raised when synthetic refined formation loses an isolation control."""


def _digest(value: object) -> str:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _state_payload(state: E1LocalEdgePlasticityState) -> dict[str, object]:
    return {
        "contract": (
            state.contract.contract_id,
            state.contract.node_capacity,
            state.contract.binding_rate_per_second,
            state.contract.release_rate_per_second,
            state.contract.backreaction_gain,
        ),
        "edge_inventory_digest": state.edge_inventory_digest,
        "edge_bindings": tuple(
            (item.first_neuron_id, item.second_neuron_id, item.binding)
            for item in state.edge_bindings
        ),
    }


def _resource_budget_error(
    field: SharedMCMField,
    state: E1LocalEdgePlasticityState,
) -> float:
    free = e1_free_node_resources(field.layer, state)
    expected = len(field.layer.neurons) * state.contract.node_capacity
    observed = math.fsum(value for _, value in free) + math.fsum(
        item.binding for item in state.edge_bindings
    )
    return abs(expected - observed)


@dataclass(frozen=True, slots=True)
class E1RefinedFormationArmAudit:
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
        if self.refinement_id not in {"r1", "r2", "r4"}:
            raise E1RefinedFormationRunnerError(
                "S1-DV refinement audit identity changed"
            )
        if self.arm_id not in {
            "ab",
            "ba",
            "ab_identity",
            "ab_formation_ablated",
            "ba_formation_ablated",
        }:
            raise E1RefinedFormationRunnerError(
                "S1-DV formation arm identity changed"
            )
        for role in ("handoff_digest", "field_digest"):
            value = getattr(self, role)
            if len(value) != 64 or any(
                char not in "0123456789abcdef" for char in value
            ):
                raise E1RefinedFormationRunnerError(f"{role} is not SHA-256")
        if (
            self.source_support_count < 1
            or self.assigned_event_count != self.source_support_count
            or not math.isfinite(self.resource_budget_error)
            or self.resource_budget_error > 1e-12
            or self.history_backreaction_enabled is not False
        ):
            raise E1RefinedFormationRunnerError(
                "S1-DV arm failed support, resource, or backreaction control"
            )
        expected_enabled = not self.arm_id.endswith("formation_ablated")
        if self.formation_enabled is not expected_enabled:
            raise E1RefinedFormationRunnerError(
                "S1-DV formation-mode audit changed"
            )
        if (
            not expected_enabled and self.state_remained_neutral is not True
        ):
            raise E1RefinedFormationRunnerError(
                "S1-DV formation ablation changed E1"
            )


@dataclass(frozen=True, slots=True)
class E1RefinedFormationResult:
    refinement_id: str
    factor: int
    b_ab: E1LocalEdgePlasticityState
    b_ba: E1LocalEdgePlasticityState
    b_ab_identity: E1LocalEdgePlasticityState
    b_ab_formation_ablated: E1LocalEdgePlasticityState
    b_ba_formation_ablated: E1LocalEdgePlasticityState
    arm_audits: tuple[E1RefinedFormationArmAudit, ...]
    result_digest: str

    def __post_init__(self) -> None:
        if (self.refinement_id, self.factor) not in {
            ("r1", 1),
            ("r2", 2),
            ("r4", 4),
        }:
            raise E1RefinedFormationRunnerError(
                "S1-DV result refinement changed"
            )
        states = (
            self.b_ab,
            self.b_ba,
            self.b_ab_identity,
            self.b_ab_formation_ablated,
            self.b_ba_formation_ablated,
        )
        if any(not isinstance(item, E1LocalEdgePlasticityState) for item in states):
            raise E1RefinedFormationRunnerError(
                "S1-DV result requires five E1 states"
            )
        if len({id(item) for item in states}) != len(states):
            raise E1RefinedFormationRunnerError(
                "S1-DV result states must remain object-separated"
            )
        if self.b_ab != self.b_ab_identity:
            raise E1RefinedFormationRunnerError(
                "S1-DV AB identity repetition changed"
            )
        for state in (
            self.b_ab_formation_ablated,
            self.b_ba_formation_ablated,
        ):
            if any(item.binding != 0.0 for item in state.edge_bindings):
                raise E1RefinedFormationRunnerError(
                    "S1-DV formation ablation is not neutral"
                )
        audits = tuple(self.arm_audits)
        expected_arms = (
            "ab",
            "ba",
            "ab_identity",
            "ab_formation_ablated",
            "ba_formation_ablated",
        )
        if tuple(item.arm_id for item in audits) != expected_arms or any(
            item.refinement_id != self.refinement_id for item in audits
        ):
            raise E1RefinedFormationRunnerError(
                "S1-DV result audit inventory changed"
            )
        if len(self.result_digest) != 64:
            raise E1RefinedFormationRunnerError(
                "S1-DV result digest is invalid"
            )
        object.__setattr__(self, "arm_audits", audits)


@dataclass(frozen=True, slots=True)
class E1RefinedFormationProduction:
    source_provenance: str
    ab_plan_digest: str
    ba_plan_digest: str
    initial_field_digest: str
    initial_state_digest: str
    refinements: tuple[E1RefinedFormationResult, ...]
    production_digest: str

    def __post_init__(self) -> None:
        if self.source_provenance != "synthetic":
            raise E1RefinedFormationRunnerError(
                "S1-DV accepts synthetic provenance only"
            )
        for role in (
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
                raise E1RefinedFormationRunnerError(f"{role} is not SHA-256")
        refinements = tuple(self.refinements)
        if tuple(
            (item.refinement_id, item.factor) for item in refinements
        ) != (("r1", 1), ("r2", 2), ("r4", 4)):
            raise E1RefinedFormationRunnerError(
                "S1-DV production requires ordered r1, r2, and r4 results"
            )
        object.__setattr__(self, "refinements", refinements)


def _handoff_digest(handoff) -> str:
    return _digest(
        [
            (
                group.completion_tick,
                tuple(
                    (item.frame.modality_id, item.frame.snapshot_id)
                    for item in group.timed_frames
                ),
            )
            for batch in handoff.batches
            for group in batch.completion_groups
        ]
    )


def _field_digest(field: SharedMCMField) -> str:
    return field.snapshot().digest()


def _run_active_arm(
    arm_id: str,
    refinement_id: str,
    field: SharedMCMField,
    state: E1LocalEdgePlasticityState,
    sequences,
    proposal_steps,
    substrate_config,
    afterimage_config,
):
    run = run_e1_asynchronous_field(
        field,
        state,
        sequences,
        proposal_steps,
        substrate_config,
        afterimage_config,
        backreaction_enabled=False,
    )
    audit = E1RefinedFormationArmAudit(
        refinement_id=refinement_id,
        arm_id=arm_id,
        handoff_digest=_handoff_digest(run.handoff),
        field_digest=_field_digest(run.field),
        source_support_count=run.source_support_count,
        assigned_event_count=run.handoff.assigned_event_count,
        resource_budget_error=_resource_budget_error(run.field, run.e1_state),
        formation_enabled=True,
        history_backreaction_enabled=False,
        state_remained_neutral=all(
            item.binding == 0.0 for item in run.e1_state.edge_bindings
        ),
    )
    return run.e1_state, audit


def _run_ablated_arm(
    arm_id: str,
    refinement_id: str,
    field: SharedMCMField,
    state: E1LocalEdgePlasticityState,
    sequences,
    proposal_steps,
    substrate_config,
    afterimage_config,
):
    run = run_neutral_asynchronous_field(
        field,
        sequences,
        proposal_steps,
        substrate_config,
        afterimage_config=afterimage_config,
    )
    audit = E1RefinedFormationArmAudit(
        refinement_id=refinement_id,
        arm_id=arm_id,
        handoff_digest=_handoff_digest(run.handoff),
        field_digest=_field_digest(run.field),
        source_support_count=run.source_support_count,
        assigned_event_count=run.handoff.assigned_event_count,
        resource_budget_error=_resource_budget_error(run.field, state),
        formation_enabled=False,
        history_backreaction_enabled=False,
        state_remained_neutral=all(
            item.binding == 0.0 for item in state.edge_bindings
        ),
    )
    return state, audit


def run_synthetic_e1_refined_formation(
    source: E1AVHistoryPermutation,
    ab_plans: E1CompletionAlignedRefinementPlanSet,
    ba_plans: E1CompletionAlignedRefinementPlanSet,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1RefinedFormationProduction:
    """Run only noncanonical synthetic formation arms; never run a probe."""

    if not isinstance(source, E1AVHistoryPermutation):
        raise E1RefinedFormationRunnerError(
            "S1-DV requires one synthetic AB/BA source"
        )
    if (
        source.history_ab_digest == S1_DS_HISTORY_AB_DIGEST
        or source.history_ba_digest == S1_DS_HISTORY_BA_DIGEST
    ):
        raise E1RefinedFormationRunnerError(
            "S1-DV rejects canonical AB/BA sources"
        )
    if not isinstance(ab_plans, E1CompletionAlignedRefinementPlanSet) or not isinstance(
        ba_plans, E1CompletionAlignedRefinementPlanSet
    ):
        raise E1RefinedFormationRunnerError(
            "S1-DV requires two complete refinement plan sets"
        )
    if not isinstance(initial_field, SharedMCMField):
        raise E1RefinedFormationRunnerError("S1-DV requires one initial field")
    if (
        initial_field.layer.tick != 0
        or initial_field.last_distribution is not None
        or initial_field.substrate is not None
    ):
        raise E1RefinedFormationRunnerError(
            "S1-DV requires one fresh initial field"
        )
    try:
        validate_e1_state_for_layer(initial_field.layer, initial_state)
    except E1LocalEdgePlasticityError as exc:
        raise E1RefinedFormationRunnerError(str(exc)) from exc
    if any(item.binding != 0.0 for item in initial_state.edge_bindings):
        raise E1RefinedFormationRunnerError(
            "S1-DV requires one neutral initial E1 state"
        )
    if substrate_config != NeutralLocalFieldSubstrateConfig(1.0) or (
        afterimage_config != NeutralFastAfterimageConfig(0.5)
    ):
        raise E1RefinedFormationRunnerError(
            "S1-DV field configuration changed"
        )
    first = ab_plans.plans[0]
    expected_ab = build_e1_completion_aligned_refinement_plans(
        source.history_ab,
        horizon_start_tick=first.horizon_start_tick,
        horizon_end_tick=first.horizon_end_tick,
        ticks_per_second=first.proposal_steps[0].ticks_per_second,
    )
    expected_ba = build_e1_completion_aligned_refinement_plans(
        source.history_ba,
        horizon_start_tick=first.horizon_start_tick,
        horizon_end_tick=first.horizon_end_tick,
        ticks_per_second=first.proposal_steps[0].ticks_per_second,
    )
    if expected_ab.digest() != ab_plans.digest() or expected_ba.digest() != ba_plans.digest():
        raise E1RefinedFormationRunnerError(
            "S1-DV plans do not match their synthetic sources"
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
        for ab_plan, ba_plan in zip(
            ab_plans.plans,
            ba_plans.plans,
            strict=True,
        ):
            fields = tuple(copy.deepcopy(initial_field) for _ in range(5))
            states = tuple(copy.deepcopy(initial_state) for _ in range(5))
            if len({id(item) for item in fields}) != 5 or len(
                {id(item) for item in states}
            ) != 5:
                raise E1RefinedFormationRunnerError(
                    "S1-DV arm inputs are not object-separated"
                )
            ab_state, ab_audit = _run_active_arm(
                "ab",
                ab_plan.refinement_id,
                fields[0],
                states[0],
                source.history_ab,
                ab_plan.proposal_steps,
                substrate_config,
                afterimage_config,
            )
            ba_state, ba_audit = _run_active_arm(
                "ba",
                ab_plan.refinement_id,
                fields[1],
                states[1],
                source.history_ba,
                ba_plan.proposal_steps,
                substrate_config,
                afterimage_config,
            )
            identity_state, identity_audit = _run_active_arm(
                "ab_identity",
                ab_plan.refinement_id,
                fields[2],
                states[2],
                source.history_ab,
                ab_plan.proposal_steps,
                substrate_config,
                afterimage_config,
            )
            ab_ablated, ab_ablated_audit = _run_ablated_arm(
                "ab_formation_ablated",
                ab_plan.refinement_id,
                fields[3],
                states[3],
                source.history_ab,
                ab_plan.proposal_steps,
                substrate_config,
                afterimage_config,
            )
            ba_ablated, ba_ablated_audit = _run_ablated_arm(
                "ba_formation_ablated",
                ab_plan.refinement_id,
                fields[4],
                states[4],
                source.history_ba,
                ba_plan.proposal_steps,
                substrate_config,
                afterimage_config,
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
                raise E1RefinedFormationRunnerError(
                    "S1-DV history backreaction ablation failed"
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
    except (
        E1RefinedFormationRunnerError,
        E1AsynchronousFieldRuntimeError,
        NeutralAsynchronousFieldRuntimeError,
        ValueError,
    ) as exc:
        if isinstance(exc, E1RefinedFormationRunnerError):
            raise
        raise E1RefinedFormationRunnerError(str(exc)) from exc
    if (
        initial_field.layer.tick != 0
        or initial_field.last_distribution is not None
        or _digest(_state_payload(initial_state)) != initial_state_digest
    ):
        raise E1RefinedFormationRunnerError(
            "S1-DV changed an initial input"
        )
    production_payload = {
        "source_provenance": "synthetic",
        "ab_plan_digest": ab_plans.digest(),
        "ba_plan_digest": ba_plans.digest(),
        "initial_field_digest": initial_field_digest,
        "initial_state_digest": initial_state_digest,
        "result_digests": tuple(item.result_digest for item in results),
    }
    return E1RefinedFormationProduction(
        source_provenance="synthetic",
        ab_plan_digest=ab_plans.digest(),
        ba_plan_digest=ba_plans.digest(),
        initial_field_digest=initial_field_digest,
        initial_state_digest=initial_state_digest,
        refinements=tuple(results),
        production_digest=_digest(production_payload),
    )
