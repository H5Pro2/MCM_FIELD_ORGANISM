"""S1-GC typed probe-context bridge for the six fixed-adapter slots."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_completion_aligned_refinement import _source_contact_evidence
from .e1_confirmation_refinement_planner import (
    E1ConfirmationRefinementPlan,
    E1ConfirmationRefinementPlanSet,
)
from .e1_formation_s1fp_common_probe_contract import (
    E1FormationS1FPCommonProbeContract,
)
from .e1_formation_s1fv_live_state_ten_role_contract import (
    E1FormationS1FVLiveStateTenRoleContract,
    E1FormationS1FVProbeSlotBinding,
)
from .e1_formation_s1gb_fixed_adapter_wrapper_contract import (
    E1FormationS1GBFixedAdapterWrapperContract,
)
from .e1_frozen_state_transfer_contract import _probe_digest
from .e1_refined_formation_runner import _digest
from .receptor_time_model import ReceptorTimeSequence


class E1FormationS1GCTenRoleProbeContextBridgeError(ValueError):
    """Raised when the new ten-role context loses exact source objects."""


S1_GC_BRIDGE_ID = "e1.ten-role-probe-context-bridge.s1gc.v1"


@dataclass(frozen=True, slots=True)
class E1FormationS1GCFixedAdapterProbeContext:
    binding: E1FormationS1FVProbeSlotBinding
    probe_sequences: tuple[ReceptorTimeSequence, ...] = field(
        repr=False,
        compare=False,
    )
    probe_plan: E1ConfirmationRefinementPlan = field(repr=False, compare=False)
    probe_source_digest: str
    context_digest: str

    def __post_init__(self) -> None:
        sequences = tuple(self.probe_sequences)
        payload = {
            "binding_digest": self.binding.binding_digest,
            "probe_source_digest": self.probe_source_digest,
            "probe_plan_digest": self.probe_plan.digest(),
        }
        if (
            not isinstance(self.binding, E1FormationS1FVProbeSlotBinding)
            or self.binding.fixed_adapter_derivation_required is not True
            or not self.binding.role_id.startswith("fixed-adapter-")
            or not sequences
            or any(not isinstance(item, ReceptorTimeSequence) for item in sequences)
            or not isinstance(self.probe_plan, E1ConfirmationRefinementPlan)
            or self.probe_plan.refinement_id != self.binding.refinement_id
            or self.probe_source_digest != _probe_digest(sequences)
            or self.probe_plan.handoff.source_event_count < 1
            or self.context_digest != _digest(payload)
        ):
            raise E1FormationS1GCTenRoleProbeContextBridgeError(
                "S1-GC fixed-adapter probe context changed"
            )
        object.__setattr__(self, "probe_sequences", sequences)


@dataclass(frozen=True, slots=True)
class E1FormationS1GCTenRoleProbeContextBridgeResult:
    bridge_id: str
    source_s1gb_contract_digest: str
    source_s1fp_contract_digest: str
    source_s1fv_contract_digest: str
    source_probe_plan_set_digest: str
    probe_source_digest: str
    contexts: tuple[E1FormationS1GCFixedAdapterProbeContext, ...] = field(
        repr=False
    )
    context_digests: tuple[str, ...]
    context_count: int
    refinement_context_counts: tuple[tuple[str, int], ...]
    exact_sequence_tuple_identity_preserved: bool
    exact_sequence_item_identity_preserved: bool
    exact_plan_object_identity_preserved: bool
    all_fixed_slots_bound_once: bool
    old_eight_role_resolved_slot_used: bool
    field_steps_executed: int
    fixed_adapter_wrapper_called: bool
    persistence_performed: bool
    execution_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    result_digest: str

    def __post_init__(self) -> None:
        contexts = tuple(self.contexts)
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"contexts", "result_digest"}
        }
        if (
            self.bridge_id != S1_GC_BRIDGE_ID
            or any(
                len(value) != 64
                for value in (
                    self.source_s1gb_contract_digest,
                    self.source_s1fp_contract_digest,
                    self.source_s1fv_contract_digest,
                    self.source_probe_plan_set_digest,
                    self.probe_source_digest,
                )
            )
            or len(contexts) != 6
            or self.context_digests != tuple(item.context_digest for item in contexts)
            or self.context_count != 6
            or self.refinement_context_counts != (("r2", 2), ("r4", 2), ("r8", 2))
            or any(
                value is not True
                for value in (
                    self.exact_sequence_tuple_identity_preserved,
                    self.exact_sequence_item_identity_preserved,
                    self.exact_plan_object_identity_preserved,
                    self.all_fixed_slots_bound_once,
                )
            )
            or any(
                value is not False
                for value in (
                    self.old_eight_role_resolved_slot_used,
                    self.fixed_adapter_wrapper_called,
                    self.persistence_performed,
                    self.execution_permitted,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision
            != "TEN_ROLE_PROBE_CONTEXT_OBJECT_BRIDGE_COMPLETE_WRAPPER_CLOSED"
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1GCTenRoleProbeContextBridgeError(
                "S1-GC bridge changed or opened wrapper execution"
            )
        object.__setattr__(self, "contexts", contexts)


def bridge_e1_formation_s1gc_ten_role_probe_contexts(
    wrapper_contract: E1FormationS1GBFixedAdapterWrapperContract,
    probe_contract: E1FormationS1FPCommonProbeContract,
    live_contract: E1FormationS1FVLiveStateTenRoleContract,
    probe_sequences: tuple[ReceptorTimeSequence, ...],
    probe_plans: E1ConfirmationRefinementPlanSet,
) -> E1FormationS1GCTenRoleProbeContextBridgeResult:
    """Bind exact probe objects to fixed slots without invoking a wrapper."""

    if not isinstance(wrapper_contract, E1FormationS1GBFixedAdapterWrapperContract):
        raise E1FormationS1GCTenRoleProbeContextBridgeError(
            "S1-GC requires the typed S1-GB contract"
        )
    if not isinstance(probe_contract, E1FormationS1FPCommonProbeContract):
        raise E1FormationS1GCTenRoleProbeContextBridgeError(
            "S1-GC requires the typed S1-FP contract"
        )
    if not isinstance(live_contract, E1FormationS1FVLiveStateTenRoleContract):
        raise E1FormationS1GCTenRoleProbeContextBridgeError(
            "S1-GC requires the typed S1-FV contract"
        )
    if not isinstance(probe_plans, E1ConfirmationRefinementPlanSet):
        raise E1FormationS1GCTenRoleProbeContextBridgeError(
            "S1-GC requires one typed probe plan set"
        )
    wrapper_contract.__post_init__()
    probe_contract.__post_init__()
    live_contract.__post_init__()
    probe_plans.__post_init__()
    sequences = tuple(probe_sequences)
    source_digest = _probe_digest(sequences)
    ticks_per_second = probe_plans.plans[0].proposal_steps[0].ticks_per_second
    source_contact_digest, signed, absolute, quadratic = _source_contact_evidence(
        sequences,
        ticks_per_second,
    )
    if (
        not sequences
        or any(not isinstance(item, ReceptorTimeSequence) for item in sequences)
        or source_digest != probe_contract.probe_source_digest
        or wrapper_contract.probe_context_bridge_implementation_permitted is not True
        or wrapper_contract.fixed_adapter_wrapper_implementation_permitted is not False
        or live_contract.execution_permitted is not False
        or tuple(item.refinement_id for item in probe_plans.plans)
        != live_contract.refinements
        or probe_plans.source_contact_digest != source_contact_digest
        or any(
            item.source_contact_digest != probe_plans.source_contact_digest
            or item.handoff.source_event_count != probe_plans.source_event_count
            or item.source_signed_integral != signed
            or item.source_absolute_integral != absolute
            or item.source_quadratic_integral != quadratic
            for item in probe_plans.plans
        )
    ):
        raise E1FormationS1GCTenRoleProbeContextBridgeError(
            "S1-GC probe source, plans, or closed contracts changed"
        )
    plan_by_refinement = {
        item.refinement_id: item for item in probe_plans.plans
    }
    fixed_bindings = tuple(
        item
        for item in live_contract.slot_bindings
        if item.fixed_adapter_derivation_required
    )
    contexts = []
    for binding in fixed_bindings:
        plan = plan_by_refinement[binding.refinement_id]
        payload = {
            "binding_digest": binding.binding_digest,
            "probe_source_digest": source_digest,
            "probe_plan_digest": plan.digest(),
        }
        contexts.append(
            E1FormationS1GCFixedAdapterProbeContext(
                binding=binding,
                probe_sequences=sequences,
                probe_plan=plan,
                probe_source_digest=source_digest,
                context_digest=_digest(payload),
            )
        )
    context_tuple = tuple(contexts)
    counts = tuple(
        (
            refinement,
            sum(item.binding.refinement_id == refinement for item in context_tuple),
        )
        for refinement in live_contract.refinements
    )
    values = {
        "bridge_id": S1_GC_BRIDGE_ID,
        "source_s1gb_contract_digest": wrapper_contract.contract_digest,
        "source_s1fp_contract_digest": probe_contract.contract_digest,
        "source_s1fv_contract_digest": live_contract.contract_digest,
        "source_probe_plan_set_digest": probe_plans.digest(),
        "probe_source_digest": source_digest,
        "contexts": context_tuple,
        "context_digests": tuple(item.context_digest for item in context_tuple),
        "context_count": len(context_tuple),
        "refinement_context_counts": counts,
        "exact_sequence_tuple_identity_preserved": all(
            item.probe_sequences is sequences for item in context_tuple
        ),
        "exact_sequence_item_identity_preserved": all(
            all(left is right for left, right in zip(item.probe_sequences, sequences, strict=True))
            for item in context_tuple
        ),
        "exact_plan_object_identity_preserved": all(
            item.probe_plan is plan_by_refinement[item.binding.refinement_id]
            for item in context_tuple
        ),
        "all_fixed_slots_bound_once": tuple(item.binding for item in context_tuple)
        == fixed_bindings,
        "old_eight_role_resolved_slot_used": False,
        "field_steps_executed": 0,
        "fixed_adapter_wrapper_called": False,
        "persistence_performed": False,
        "execution_permitted": False,
        "claims_permitted": False,
        "decision": "TEN_ROLE_PROBE_CONTEXT_OBJECT_BRIDGE_COMPLETE_WRAPPER_CLOSED",
        "reason": (
            "six-fixed-slots-bound-to-exact-probe-sequence-and-refinement-plan-"
            "objects;old-eight-role-context-not-used;wrapper-remains-closed"
        ),
    }
    payload = {name: value for name, value in values.items() if name != "contexts"}
    return E1FormationS1GCTenRoleProbeContextBridgeResult(
        **values,
        result_digest=_digest(payload),
    )
