"""S1-EC89 nonexecuting n2/r4 and n2/r8 object handoffs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .e1_common_probe_ec88_r4_r8_budget_inventory import (
    E1CommonProbeEC88R4R8BudgetInventory,
)
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


class E1CommonProbeEC89R4R8ObjectHandoffsError(ValueError):
    """Raised when EC89 cannot bind the exact zero-step refinement objects."""


S1_EC89_HANDOFF_SET_ID = "e1.common-probe-r4-r8-object-handoffs.s1ec89.v1"
S1_EC89_EC88_INVENTORY_DIGEST = (
    "7fff1cd657283401ffcc01d97e16e2785f4b18e80070120cd028a7e560c5e8da"
)


Resolver = Callable[
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
class E1CommonProbeEC89RefinementObjectHandoff:
    contact_count: int
    refinement_id: str
    role_ids: tuple[str, ...]
    formation_state_roles: tuple[str, ...]
    resolved_context_digests: tuple[str, ...]
    formation_context_digests: tuple[str, ...]
    formation_steps_each: int
    probe_steps_each: int
    maximum_total_steps: int
    probe_source_digest: str
    initial_field_digest: str
    initial_state_digest: str
    all_slot_objects_resolved: bool
    all_formation_routes_unique: bool
    initial_objects_carried_by_identity: bool
    field_steps_executed: int
    execution_permitted: bool
    persistence_performed: bool
    ec46_decision_permitted: bool
    claims_permitted: bool
    handoff_digest: str
    resolved_slots: tuple[E1CommonProbeResolvedSlot, ...] = field(
        repr=False, compare=False
    )
    formation_slots: tuple[E1CommonProbeResolvedSlot, ...] = field(
        repr=False, compare=False
    )
    initial_field: SharedMCMField = field(repr=False, compare=False)
    initial_state: E1LocalEdgePlasticityState = field(repr=False, compare=False)

    def __post_init__(self) -> None:
        expected_budget = {
            "r4": (804, 400, 6416),
            "r8": (1608, 800, 12832),
        }.get(self.refinement_id)
        if (
            self.contact_count != 2
            or expected_budget is None
            or self.role_ids != S1_EC45_PROBE_ROLES
            or self.formation_state_roles != S1_EC52_FORMATION_STATE_ROLES
            or tuple(item.binding.role_id for item in self.resolved_slots)
            != self.role_ids
            or tuple(item.binding.state_role for item in self.formation_slots)
            != self.formation_state_roles
            or self.resolved_context_digests
            != tuple(item.context_digest for item in self.resolved_slots)
            or self.formation_context_digests
            != tuple(item.context_digest for item in self.formation_slots)
            or (
                self.formation_steps_each,
                self.probe_steps_each,
                self.maximum_total_steps,
            )
            != expected_budget
            or self.initial_field_digest != _initial_field_digest(self.initial_field)
            or self.initial_state_digest != _digest(_state_payload(self.initial_state))
            or any(
                value is not True
                for value in (
                    self.all_slot_objects_resolved,
                    self.all_formation_routes_unique,
                    self.initial_objects_carried_by_identity,
                )
            )
            or self.field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.execution_permitted,
                    self.persistence_performed,
                    self.ec46_decision_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1CommonProbeEC89R4R8ObjectHandoffsError(
                "S1-EC89 refinement handoff changed or crossed zero-step scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name
            not in {
                "handoff_digest",
                "resolved_slots",
                "formation_slots",
                "initial_field",
                "initial_state",
            }
        }
        if self.handoff_digest != _digest(payload):
            raise E1CommonProbeEC89R4R8ObjectHandoffsError(
                "S1-EC89 refinement handoff digest changed"
            )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC89R4R8ObjectHandoffSet:
    handoff_set_id: str
    source_ec88_inventory_digest: str
    refinement_ids: tuple[str, ...]
    handoff_digests: tuple[str, ...]
    combined_maximum_total_steps: int
    all_objects_resolved: bool
    all_handoffs_object_separate: bool
    field_steps_executed: int
    execution_permitted: bool
    persistence_performed: bool
    ec46_decision_permitted: bool
    claims_permitted: bool
    result_digest: str
    handoffs: tuple[E1CommonProbeEC89RefinementObjectHandoff, ...] = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        if (
            self.handoff_set_id != S1_EC89_HANDOFF_SET_ID
            or self.source_ec88_inventory_digest != S1_EC89_EC88_INVENTORY_DIGEST
            or self.refinement_ids != ("r4", "r8")
            or self.handoff_digests
            != tuple(item.handoff_digest for item in self.handoffs)
            or self.combined_maximum_total_steps != 19248
            or self.all_objects_resolved is not True
            or self.all_handoffs_object_separate is not True
            or self.field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.execution_permitted,
                    self.persistence_performed,
                    self.ec46_decision_permitted,
                    self.claims_permitted,
                )
            )
        ):
            raise E1CommonProbeEC89R4R8ObjectHandoffsError(
                "S1-EC89 handoff set changed or crossed zero-step scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"result_digest", "handoffs"}
        }
        if self.result_digest != _digest(payload):
            raise E1CommonProbeEC89R4R8ObjectHandoffsError(
                "S1-EC89 handoff set digest changed"
            )


def prepare_e1_common_probe_ec89_r4_r8_object_handoffs(
    inventory: E1CommonProbeEC88R4R8BudgetInventory,
    contract: E1CommonProbeRealBindingContract,
    formation_plans: E1RepetitionFormationPlanSet,
    probe_sequences: tuple[ReceptorTimeSequence, ...],
    probe_plans: E1ConfirmationRefinementPlanSet,
    initial_field: SharedMCMField,
    initial_state: E1LocalEdgePlasticityState,
    *,
    resolver: Resolver = resolve_e1_common_probe_real_slot,
) -> E1CommonProbeEC89R4R8ObjectHandoffSet:
    """Resolve r4/r8 objects while keeping every field and state untouched."""

    for value, expected, role in (
        (inventory, E1CommonProbeEC88R4R8BudgetInventory, "EC88"),
        (contract, E1CommonProbeRealBindingContract, "EC52"),
        (formation_plans, E1RepetitionFormationPlanSet, "EC27"),
        (probe_plans, E1ConfirmationRefinementPlanSet, "EB1"),
        (initial_field, SharedMCMField, "field"),
        (initial_state, E1LocalEdgePlasticityState, "state"),
    ):
        if not isinstance(value, expected):
            raise E1CommonProbeEC89R4R8ObjectHandoffsError(
                f"S1-EC89 requires typed {role} input"
            )
        value.__post_init__()
    if (
        inventory.inventory_digest != S1_EC89_EC88_INVENTORY_DIGEST
        or contract.contract_digest != inventory.source_binding_contract_digest
        or formation_plans.plan_set_digest
        != inventory.source_formation_plan_set_digest
        or probe_plans.digest() != inventory.source_probe_plan_set_digest
        or not callable(resolver)
    ):
        raise E1CommonProbeEC89R4R8ObjectHandoffsError(
            "S1-EC89 source bindings changed"
        )
    sequences = tuple(probe_sequences)
    if not sequences:
        raise E1CommonProbeEC89R4R8ObjectHandoffsError(
            "S1-EC89 requires the common probe source"
        )
    budget_by_refinement = {item[0]: item for item in inventory.budgets}
    handoffs = []
    for refinement in inventory.refinement_levels:
        bindings = tuple(
            item
            for item in contract.slot_bindings
            if item.contact_count == 2 and item.refinement_id == refinement
        )
        resolved = tuple(
            resolver(contract, binding, formation_plans, sequences, probe_plans)
            for binding in bindings
        )
        if any(
            not isinstance(item, E1CommonProbeResolvedSlot)
            or item.binding is not binding
            for item, binding in zip(resolved, bindings, strict=True)
        ):
            raise E1CommonProbeEC89R4R8ObjectHandoffsError(
                "S1-EC89 resolver lost a concrete slot object"
            )
        formation_slots = tuple(
            next(item for item in resolved if item.binding.state_role == role)
            for role in S1_EC52_FORMATION_STATE_ROLES
        )
        budget = budget_by_refinement[refinement]
        values = {
            "contact_count": 2,
            "refinement_id": refinement,
            "role_ids": tuple(item.binding.role_id for item in resolved),
            "formation_state_roles": tuple(
                item.binding.state_role for item in formation_slots
            ),
            "resolved_context_digests": tuple(item.context_digest for item in resolved),
            "formation_context_digests": tuple(
                item.context_digest for item in formation_slots
            ),
            "formation_steps_each": budget[1],
            "probe_steps_each": budget[2],
            "maximum_total_steps": budget[7],
            "probe_source_digest": _probe_digest(sequences),
            "initial_field_digest": _initial_field_digest(initial_field),
            "initial_state_digest": _digest(_state_payload(initial_state)),
            "all_slot_objects_resolved": True,
            "all_formation_routes_unique": len(
                {item.binding.state_role for item in formation_slots}
            )
            == 4,
            "initial_objects_carried_by_identity": True,
            "field_steps_executed": 0,
            "execution_permitted": False,
            "persistence_performed": False,
            "ec46_decision_permitted": False,
            "claims_permitted": False,
        }
        handoffs.append(
            E1CommonProbeEC89RefinementObjectHandoff(
                **values,
                handoff_digest=_digest(values),
                resolved_slots=resolved,
                formation_slots=formation_slots,
                initial_field=initial_field,
                initial_state=initial_state,
            )
        )
    handoff_tuple = tuple(handoffs)
    values = {
        "handoff_set_id": S1_EC89_HANDOFF_SET_ID,
        "source_ec88_inventory_digest": inventory.inventory_digest,
        "refinement_ids": tuple(item.refinement_id for item in handoff_tuple),
        "handoff_digests": tuple(item.handoff_digest for item in handoff_tuple),
        "combined_maximum_total_steps": sum(
            item.maximum_total_steps for item in handoff_tuple
        ),
        "all_objects_resolved": all(
            item.all_slot_objects_resolved for item in handoff_tuple
        ),
        "all_handoffs_object_separate": len({id(item) for item in handoff_tuple}) == 2,
        "field_steps_executed": 0,
        "execution_permitted": False,
        "persistence_performed": False,
        "ec46_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1CommonProbeEC89R4R8ObjectHandoffSet(
        **values,
        result_digest=_digest(values),
        handoffs=handoff_tuple,
    )
