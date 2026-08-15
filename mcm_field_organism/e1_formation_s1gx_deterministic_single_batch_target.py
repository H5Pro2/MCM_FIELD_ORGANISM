"""S1-GX deterministic selection of one smallest future real pilot target."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_ROLE_ORDER,
)
from .e1_formation_s1gh_fresh_field_bridge import (
    E1FormationS1GHFreshFieldBinding,
    E1FormationS1GHFreshFieldBridgeResult,
)
from .e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
    build_e1_formation_s1gn_initial_live_field_carrier,
)
from .e1_formation_s1gs_real_single_batch_gate_contract import (
    E1FormationS1GSRealSingleBatchGateContract,
)
from .e1_refined_formation_runner import _digest
from .receptor_proposal_handoff import ReceptorProposalBatch


class E1FormationS1GXDeterministicSingleBatchTargetError(ValueError):
    """Raised when pilot selection is widened, reordered, or executed."""


S1_GX_TARGET_ID = "e1.deterministic-single-carrier-batch-target.s1gx.v1"
S1_GX_RUN_ID = "S1-GY-REAL-SINGLE-CARRIER-BATCH-PILOT"
S1_GX_SELECTION_POLICY = (
    "minimum-probe-batch-count",
    "then-canonical-s1gf-role-order",
    "then-exact-first-batch-index-zero",
)


@dataclass(frozen=True, slots=True)
class E1FormationS1GXDeterministicSingleBatchTarget:
    target_id: str
    run_id: str
    source_s1gh_result_digest: str
    source_s1gs_gate_digest: str
    selection_policy: tuple[str, ...]
    candidate_role_order: tuple[tuple[str, str], ...]
    candidate_batch_counts: tuple[tuple[str, str, int], ...]
    selected_refinement_id: str
    selected_role_id: str
    selected_binding_digest: str
    selected_initial_field_digest: str
    selected_carrier_digest: str
    selected_batch_index: int
    selected_batch_start_tick: int
    selected_batch_end_tick: int
    selected_batch_support_count: int
    maximum_adapter_calls: int
    maximum_field_steps: int
    smallest_refinement_selected: bool
    canonical_first_role_selected: bool
    exact_first_batch_selected: bool
    fresh_field_object_carried_explicitly: bool
    source_field_unchanged: bool
    authorization_required: bool
    authorization_present: bool
    authorization_requested: bool
    token_created: bool
    transition_created: bool
    adapter_calls: int
    field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    reason: str
    target_digest: str
    selected_fresh_binding: E1FormationS1GHFreshFieldBinding = field(
        repr=False,
        compare=False,
    )
    selected_initial_carrier: E1FormationS1GNLiveFieldCarrier = field(
        repr=False,
        compare=False,
    )
    selected_batch: ReceptorProposalBatch = field(
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name
            not in {
                "target_digest",
                "selected_fresh_binding",
                "selected_initial_carrier",
                "selected_batch",
            }
        }
        fresh = self.selected_fresh_binding
        carrier = self.selected_initial_carrier
        batch = self.selected_batch
        if (
            self.target_id != S1_GX_TARGET_ID
            or self.run_id != S1_GX_RUN_ID
            or len(self.source_s1gh_result_digest) != 64
            or len(self.source_s1gs_gate_digest) != 64
            or self.selection_policy != S1_GX_SELECTION_POLICY
            or self.candidate_role_order != S1_GF_ROLE_ORDER
            or len(self.candidate_batch_counts) != 6
            or not isinstance(fresh, E1FormationS1GHFreshFieldBinding)
            or not isinstance(carrier, E1FormationS1GNLiveFieldCarrier)
            or not isinstance(batch, ReceptorProposalBatch)
            or (self.selected_refinement_id, self.selected_role_id)
            != ("r2", "fixed-adapter-ab")
            or self.selected_refinement_id != fresh.refinement_id
            or self.selected_role_id != fresh.role_id
            or self.selected_binding_digest != fresh.binding_digest
            or self.selected_binding_digest != carrier.binding_digest
            or self.selected_initial_field_digest != fresh.initial_field_digest
            or self.selected_initial_field_digest != carrier.initial_field_digest
            or self.selected_carrier_digest != carrier.carrier_digest
            or self.selected_batch_index != 0
            or self.selected_batch_index != batch.batch_index
            or self.selected_batch_start_tick != batch.step_time.start_tick
            or self.selected_batch_end_tick != batch.step_time.end_tick
            or self.selected_batch_support_count != batch.event_count
            or self.maximum_adapter_calls != 1
            or self.maximum_field_steps != 1
            or carrier.fresh_binding is not fresh
            or carrier.current_field is not fresh.fresh_field
            or carrier.completed_batch_count != 0
            or carrier.accounted_source_support_count != 0
            or carrier.actual_field_steps_executed != 0
            or fresh.invocation.context.probe_plan.handoff.batches[0] is not batch
            or any(
                value is not True
                for value in (
                    self.smallest_refinement_selected,
                    self.canonical_first_role_selected,
                    self.exact_first_batch_selected,
                    self.fresh_field_object_carried_explicitly,
                    self.source_field_unchanged,
                    self.authorization_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.authorization_present,
                    self.authorization_requested,
                    self.token_created,
                    self.transition_created,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.adapter_calls != 0
            or self.field_steps_executed != 0
            or self.decision
            != "R2_AB_FIRST_BATCH_DETERMINISTICALLY_BOUND_NO_AUTHORIZATION_REQUESTED"
            or not self.reason
            or self.target_digest != _digest(payload)
        ):
            raise E1FormationS1GXDeterministicSingleBatchTargetError(
                "S1-GX target changed, widened, or crossed execution scope"
            )


def select_e1_formation_s1gx_deterministic_single_batch_target(
    bridge: E1FormationS1GHFreshFieldBridgeResult,
    gate: E1FormationS1GSRealSingleBatchGateContract,
) -> E1FormationS1GXDeterministicSingleBatchTarget:
    """Select the canonical smallest first batch without advancing its field."""

    if not isinstance(bridge, E1FormationS1GHFreshFieldBridgeResult) or not isinstance(
        gate, E1FormationS1GSRealSingleBatchGateContract
    ):
        raise E1FormationS1GXDeterministicSingleBatchTargetError(
            "S1-GX requires the exact fresh bridge and closed gate"
        )
    bridge.__post_init__()
    gate.__post_init__()
    fresh_bindings = tuple(bridge.fresh_bindings)
    role_order = tuple(
        (fresh.refinement_id, fresh.role_id) for fresh in fresh_bindings
    )
    if (
        role_order != S1_GF_ROLE_ORDER
        or gate.maximum_adapter_calls != 1
        or gate.maximum_field_steps != 1
        or gate.execution_permitted is not False
        or gate.authorization_present is not False
    ):
        raise E1FormationS1GXDeterministicSingleBatchTargetError(
            "S1-GX sources changed order or opened the real gate"
        )
    candidates = tuple(
        (
            len(fresh.invocation.context.probe_plan.handoff.batches),
            S1_GF_ROLE_ORDER.index((fresh.refinement_id, fresh.role_id)),
            fresh,
        )
        for fresh in fresh_bindings
    )
    _, _, selected = min(candidates, key=lambda item: (item[0], item[1]))
    selected_batches = selected.invocation.context.probe_plan.handoff.batches
    batch = selected_batches[0]
    carrier = build_e1_formation_s1gn_initial_live_field_carrier(selected)
    candidate_batch_counts = tuple(
        (fresh.refinement_id, fresh.role_id, count)
        for count, _, fresh in candidates
    )
    values = {
        "target_id": S1_GX_TARGET_ID,
        "run_id": S1_GX_RUN_ID,
        "source_s1gh_result_digest": bridge.result_digest,
        "source_s1gs_gate_digest": gate.gate_digest,
        "selection_policy": S1_GX_SELECTION_POLICY,
        "candidate_role_order": role_order,
        "candidate_batch_counts": candidate_batch_counts,
        "selected_refinement_id": selected.refinement_id,
        "selected_role_id": selected.role_id,
        "selected_binding_digest": selected.binding_digest,
        "selected_initial_field_digest": selected.initial_field_digest,
        "selected_carrier_digest": carrier.carrier_digest,
        "selected_batch_index": batch.batch_index,
        "selected_batch_start_tick": batch.step_time.start_tick,
        "selected_batch_end_tick": batch.step_time.end_tick,
        "selected_batch_support_count": batch.event_count,
        "maximum_adapter_calls": 1,
        "maximum_field_steps": 1,
        "smallest_refinement_selected": len(selected_batches)
        == min(item[0] for item in candidates),
        "canonical_first_role_selected": (
            selected.refinement_id,
            selected.role_id,
        )
        == S1_GF_ROLE_ORDER[0],
        "exact_first_batch_selected": batch.batch_index == 0,
        "fresh_field_object_carried_explicitly": carrier.current_field
        is selected.fresh_field,
        "source_field_unchanged": carrier.current_field_digest
        == selected.initial_field_digest,
        "authorization_required": True,
        "authorization_present": False,
        "authorization_requested": False,
        "token_created": False,
        "transition_created": False,
        "adapter_calls": 0,
        "field_steps_executed": 0,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "R2_AB_FIRST_BATCH_DETERMINISTICALLY_BOUND_"
            "NO_AUTHORIZATION_REQUESTED"
        ),
        "reason": (
            "r2-has-the-smallest-200-batch-plan;fixed-adapter-ab-is-first-in-"
            "canonical-role-order;batch-zero-and-its-exact-fresh-carrier-are-"
            "bound-without-transition-token-authorization-request-or-field-step"
        ),
    }
    payload = dict(values)
    return E1FormationS1GXDeterministicSingleBatchTarget(
        **values,
        target_digest=_digest(payload),
        selected_fresh_binding=selected,
        selected_initial_carrier=carrier,
        selected_batch=batch,
    )
