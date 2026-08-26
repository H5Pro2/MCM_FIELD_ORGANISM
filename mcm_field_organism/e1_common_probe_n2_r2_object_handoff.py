"""S1-EC59 object-carrying handoff for the bounded n2/r2 probe matrix."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_real_binding_contract import (
    E1CommonProbeRealBindingContract,
    S1_EC52_FORMATION_STATE_ROLES,
)
from .e1_common_probe_real_wrappers import (
    E1CommonProbeResolvedSlot,
    resolve_e1_common_probe_real_slot,
)
from .e1_confirmation_refinement_planner import E1ConfirmationRefinementPlanSet
from .e1_frozen_state_transfer_contract import _probe_digest
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_refined_chain_canonical_producer import _initial_field_digest
from .e1_refined_formation_runner import _digest, _state_payload
from .e1_repetition_formation_planner import E1RepetitionFormationPlanSet
from .receptor_time_model import ReceptorTimeSequence
from .shared_mcm_field import SharedMCMField


class E1CommonProbeN2R2ObjectHandoffError(ValueError):
    """Raised when EC59 loses an object route or crosses execution scope."""


S1_EC59_HANDOFF_ID = "e1.common-probe-n2-r2-object-handoff.s1ec59.v1"
S1_EC59_EC52_CONTRACT_DIGEST = (
    "291ea70c96ad26b3f6e696588ebd55d3e6f7163967b45de9a689bd731cb7bf7b"
)


SlotResolver = Callable[
    [
        E1CommonProbeRealBindingContract,
        object,
        E1RepetitionFormationPlanSet,
        tuple[ReceptorTimeSequence, ...],
        E1ConfirmationRefinementPlanSet,
    ],
    E1CommonProbeResolvedSlot,
]


@dataclass(frozen=True, slots=True)
class E1CommonProbeN2R2ObjectHandoff:
    handoff_id: str
    source_contract_digest: str
    contact_count: int
    refinement_id: str
    roles: tuple[str, ...]
    formation_state_roles: tuple[str, ...]
    resolved_context_digests: tuple[str, ...]
    formation_context_digests: tuple[str, ...]
    probe_source_digest: str
    initial_field_digest: str
    initial_state_digest: str
    all_slot_objects_resolved: bool
    all_formation_routes_unique: bool
    initial_objects_carried_by_identity: bool
    field_steps_executed: int
    execution_permitted: bool
    persistence_performed: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    handoff_digest: str
    contract: E1CommonProbeRealBindingContract = field(repr=False, compare=False)
    formation_plans: E1RepetitionFormationPlanSet = field(repr=False, compare=False)
    probe_sequences: tuple[ReceptorTimeSequence, ...] = field(repr=False, compare=False)
    probe_plans: E1ConfirmationRefinementPlanSet = field(repr=False, compare=False)
    initial_field: SharedMCMField = field(repr=False, compare=False)
    initial_state: E1LocalEdgePlasticityState = field(repr=False, compare=False)
    resolved_slots: tuple[E1CommonProbeResolvedSlot, ...] = field(repr=False, compare=False)
    formation_slots: tuple[E1CommonProbeResolvedSlot, ...] = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        slot_bindings = tuple(item.binding for item in self.resolved_slots)
        formation_roles = tuple(item.binding.state_role for item in self.formation_slots)
        metadata = _metadata(self)
        if (
            self.handoff_id != S1_EC59_HANDOFF_ID
            or self.source_contract_digest != S1_EC59_EC52_CONTRACT_DIGEST
            or (self.contact_count, self.refinement_id) != (2, "r2")
            or self.roles != S1_EC45_PROBE_ROLES
            or self.formation_state_roles != S1_EC52_FORMATION_STATE_ROLES
            or tuple(item.role_id for item in slot_bindings) != self.roles
            or any((item.contact_count, item.refinement_id) != (2, "r2") for item in slot_bindings)
            or formation_roles != self.formation_state_roles
            or len({item.binding.state_role for item in self.formation_slots}) != 4
            or self.resolved_context_digests != tuple(item.context_digest for item in self.resolved_slots)
            or self.formation_context_digests != tuple(item.context_digest for item in self.formation_slots)
            or self.probe_source_digest != _probe_digest(self.probe_sequences)
            or self.initial_field_digest != _initial_field_digest(self.initial_field)
            or self.initial_state_digest != _digest(_state_payload(self.initial_state))
            or any(value is not True for value in (
                self.all_slot_objects_resolved,
                self.all_formation_routes_unique,
                self.initial_objects_carried_by_identity,
            ))
            or self.field_steps_executed != 0
            or any(value is not False for value in (
                self.execution_permitted,
                self.persistence_performed,
                self.research_decision_permitted,
                self.memory_claim_permitted,
            ))
            or self.handoff_digest != _digest(metadata)
        ):
            raise E1CommonProbeN2R2ObjectHandoffError(
                "S1-EC59 changed an object route or crossed zero-step scope"
            )


def _metadata(handoff: E1CommonProbeN2R2ObjectHandoff) -> dict[str, object]:
    return {
        name: getattr(handoff, name)
        for name in (
            "handoff_id",
            "source_contract_digest",
            "contact_count",
            "refinement_id",
            "roles",
            "formation_state_roles",
            "resolved_context_digests",
            "formation_context_digests",
            "probe_source_digest",
            "initial_field_digest",
            "initial_state_digest",
            "all_slot_objects_resolved",
            "all_formation_routes_unique",
            "initial_objects_carried_by_identity",
            "field_steps_executed",
            "execution_permitted",
            "persistence_performed",
            "research_decision_permitted",
            "memory_claim_permitted",
        )
    }


def prepare_e1_common_probe_n2_r2_object_handoff(
    contract: E1CommonProbeRealBindingContract,
    formation_plans: E1RepetitionFormationPlanSet,
    probe_sequences: tuple[ReceptorTimeSequence, ...],
    probe_plans: E1ConfirmationRefinementPlanSet,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    *,
    resolver: SlotResolver = resolve_e1_common_probe_real_slot,
) -> E1CommonProbeN2R2ObjectHandoff:
    """Resolve and retain the real objects without invoking a field kernel."""

    if (
        not isinstance(contract, E1CommonProbeRealBindingContract)
        or contract.contract_digest != S1_EC59_EC52_CONTRACT_DIGEST
        or not isinstance(formation_plans, E1RepetitionFormationPlanSet)
        or not isinstance(probe_plans, E1ConfirmationRefinementPlanSet)
        or not isinstance(initial_field, SharedMCMField)
        or not isinstance(initial_state, E1LocalEdgePlasticityState)
        or not callable(resolver)
    ):
        raise E1CommonProbeN2R2ObjectHandoffError(
            "S1-EC59 requires the bound real input objects"
        )
    sequences = tuple(probe_sequences)
    if _probe_digest(sequences) != contract.probe_source_digest:
        raise E1CommonProbeN2R2ObjectHandoffError(
            "S1-EC59 common probe source changed"
        )
    bindings = tuple(
        item
        for item in contract.slot_bindings
        if (item.contact_count, item.refinement_id) == (2, "r2")
    )
    if tuple(item.role_id for item in bindings) != S1_EC45_PROBE_ROLES:
        raise E1CommonProbeN2R2ObjectHandoffError(
            "S1-EC59 bounded slot order changed"
        )
    resolved = tuple(
        resolver(contract, item, formation_plans, sequences, probe_plans)
        for item in bindings
    )
    if any(
        not isinstance(item, E1CommonProbeResolvedSlot)
        or item.binding is not binding
        for item, binding in zip(resolved, bindings, strict=True)
    ):
        raise E1CommonProbeN2R2ObjectHandoffError(
            "S1-EC59 resolver lost a concrete slot object"
        )
    formation_slots = tuple(
        next(item for item in resolved if item.binding.state_role == role)
        for role in S1_EC52_FORMATION_STATE_ROLES
    )
    values = {
        "handoff_id": S1_EC59_HANDOFF_ID,
        "source_contract_digest": contract.contract_digest,
        "contact_count": 2,
        "refinement_id": "r2",
        "roles": S1_EC45_PROBE_ROLES,
        "formation_state_roles": S1_EC52_FORMATION_STATE_ROLES,
        "resolved_context_digests": tuple(item.context_digest for item in resolved),
        "formation_context_digests": tuple(item.context_digest for item in formation_slots),
        "probe_source_digest": _probe_digest(sequences),
        "initial_field_digest": _initial_field_digest(initial_field),
        "initial_state_digest": _digest(_state_payload(initial_state)),
        "all_slot_objects_resolved": True,
        "all_formation_routes_unique": len({item.binding.state_role for item in formation_slots}) == 4,
        "initial_objects_carried_by_identity": True,
        "field_steps_executed": 0,
        "execution_permitted": False,
        "persistence_performed": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
    }
    return E1CommonProbeN2R2ObjectHandoff(
        **values,
        handoff_digest=_digest(values),
        contract=contract,
        formation_plans=formation_plans,
        probe_sequences=sequences,
        probe_plans=probe_plans,
        initial_field=initial_field,
        initial_state=initial_state,
        resolved_slots=resolved,
        formation_slots=formation_slots,
    )
