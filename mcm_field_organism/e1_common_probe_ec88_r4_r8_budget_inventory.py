"""S1-EC88 static n2/r4-r8 object and step-budget inventory."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_common_probe_ec87_r2_ec46_complement_contract import (
    E1CommonProbeEC87R2EC46ComplementContract,
)
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_real_binding_contract import (
    E1CommonProbeRealBindingContract,
    S1_EC52_FORMATION_STATE_ROLES,
)
from .e1_confirmation_refinement_planner import E1ConfirmationRefinementPlanSet
from .e1_refined_formation_runner import _digest
from .e1_repetition_formation_planner import E1RepetitionFormationPlanSet
from .e1_repetition_pilot_release_contract import (
    S1_EC29_MIN_FREE_DISK_BYTES,
    S1_EC29_MIN_FREE_MEMORY_BYTES,
)


class E1CommonProbeEC88R4R8BudgetInventoryError(ValueError):
    """Raised when EC88 cannot derive the exact closed refinement inventory."""


S1_EC88_INVENTORY_ID = "e1.common-probe-r4-r8-budget-inventory.s1ec88.v1"
S1_EC88_EC87_CONTRACT_DIGEST = (
    "5d65823a811b70b106927a5b8e93350e954f3d58058f2ab4ec6e9b9980c14942"
)
S1_EC88_EXPECTED_BUDGETS = (
    ("r4", 804, 400, 4, 8, 3216, 3200, 6416),
    ("r8", 1608, 800, 4, 8, 6432, 6400, 12832),
)


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC88R4R8BudgetInventory:
    inventory_id: str
    source_ec87_contract_digest: str
    source_binding_contract_digest: str
    source_formation_plan_set_digest: str
    source_probe_plan_set_digest: str
    contact_count: int
    refinement_levels: tuple[str, ...]
    role_ids: tuple[str, ...]
    formation_state_roles: tuple[str, ...]
    budgets: tuple[tuple[str, int, int, int, int, int, int, int], ...]
    combined_formation_steps: int
    combined_probe_steps: int
    combined_total_steps: int
    formation_source_support_count: int
    probe_source_support_count: int
    all_supports_assigned_once: bool
    minimum_free_memory_bytes: int
    minimum_free_disk_bytes: int
    concrete_object_handoffs_ready: bool
    runtime_caps_bound: bool
    field_execution_permitted: bool
    owner_authorization_present: bool
    persistence_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    inventory_digest: str

    def __post_init__(self) -> None:
        if (
            self.inventory_id != S1_EC88_INVENTORY_ID
            or self.source_ec87_contract_digest != S1_EC88_EC87_CONTRACT_DIGEST
            or any(
                len(value) != 64
                for value in (
                    self.source_binding_contract_digest,
                    self.source_formation_plan_set_digest,
                    self.source_probe_plan_set_digest,
                )
            )
            or self.contact_count != 2
            or self.refinement_levels != ("r4", "r8")
            or self.role_ids != S1_EC45_PROBE_ROLES
            or self.formation_state_roles != S1_EC52_FORMATION_STATE_ROLES
            or self.budgets != S1_EC88_EXPECTED_BUDGETS
            or (
                self.combined_formation_steps,
                self.combined_probe_steps,
                self.combined_total_steps,
            )
            != (9648, 9600, 19248)
            or (self.formation_source_support_count, self.probe_source_support_count)
            != (220, 110)
            or self.all_supports_assigned_once is not True
            or self.minimum_free_memory_bytes != S1_EC29_MIN_FREE_MEMORY_BYTES
            or self.minimum_free_disk_bytes != S1_EC29_MIN_FREE_DISK_BYTES
            or any(
                value is not False
                for value in (
                    self.concrete_object_handoffs_ready,
                    self.runtime_caps_bound,
                    self.field_execution_permitted,
                    self.owner_authorization_present,
                    self.persistence_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "R4_R8_BUDGETS_BOUND_HANDOFFS_AND_RUNTIME_CAPS_MISSING"
            or not self.reason
        ):
            raise E1CommonProbeEC88R4R8BudgetInventoryError(
                "S1-EC88 inventory changed or crossed static scope"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "inventory_digest"
        }
        if self.inventory_digest != _digest(payload):
            raise E1CommonProbeEC88R4R8BudgetInventoryError(
                "S1-EC88 inventory digest changed"
            )


def build_e1_common_probe_ec88_r4_r8_budget_inventory(
    complement: E1CommonProbeEC87R2EC46ComplementContract,
    binding: E1CommonProbeRealBindingContract,
    formation_plans: E1RepetitionFormationPlanSet,
    probe_plans: E1ConfirmationRefinementPlanSet,
) -> E1CommonProbeEC88R4R8BudgetInventory:
    """Derive exact n2/r4-r8 plan counts without resolving or running fields."""

    for value, expected_type, role in (
        (complement, E1CommonProbeEC87R2EC46ComplementContract, "EC87"),
        (binding, E1CommonProbeRealBindingContract, "EC52"),
        (formation_plans, E1RepetitionFormationPlanSet, "EC27"),
        (probe_plans, E1ConfirmationRefinementPlanSet, "EB1"),
    ):
        if not isinstance(value, expected_type):
            raise E1CommonProbeEC88R4R8BudgetInventoryError(
                f"S1-EC88 requires typed {role} input"
            )
        value.__post_init__()
    if complement.contract_digest != S1_EC88_EC87_CONTRACT_DIGEST:
        raise E1CommonProbeEC88R4R8BudgetInventoryError(
            "S1-EC88 EC87 binding changed"
        )

    pair = next(item for item in formation_plans.pairs if item.contact_count == 2)
    formation_by_refinement = {
        plan.refinement_id: plan
        for plan in pair.repeated_plans.plans
    }
    continuous_by_refinement = {
        plan.refinement_id: plan
        for plan in pair.continuous_plans.plans
    }
    probe_by_refinement = {plan.refinement_id: plan for plan in probe_plans.plans}
    budgets = []
    supports_assigned_once = True
    for refinement in complement.missing_refinement_levels:
        slots = tuple(
            item
            for item in binding.slot_bindings
            if item.contact_count == 2 and item.refinement_id == refinement
        )
        repeated = formation_by_refinement[refinement]
        continuous = continuous_by_refinement[refinement]
        probe = probe_by_refinement[refinement]
        if (
            tuple(item.role_id for item in slots) != S1_EC45_PROBE_ROLES
            or len({item.state_role for item in slots if item.state_role is not None}) != 4
            or len(repeated.proposal_steps) != len(continuous.proposal_steps)
        ):
            raise E1CommonProbeEC88R4R8BudgetInventoryError(
                "S1-EC88 refinement role or plan geometry changed"
            )
        formation_steps_each = len(repeated.proposal_steps)
        probe_steps_each = len(probe.proposal_steps)
        formation_count = 4
        probe_count = 8
        formation_total = formation_count * formation_steps_each
        probe_total = probe_count * probe_steps_each
        budgets.append(
            (
                refinement,
                formation_steps_each,
                probe_steps_each,
                formation_count,
                probe_count,
                formation_total,
                probe_total,
                formation_total + probe_total,
            )
        )
        supports_assigned_once = supports_assigned_once and all(
            plan.handoff.every_in_horizon_event_assigned_once
            and plan.handoff.assigned_event_count == plan.handoff.source_event_count
            for plan in (repeated, continuous, probe)
        )
    budget_tuple = tuple(budgets)
    values = {
        "inventory_id": S1_EC88_INVENTORY_ID,
        "source_ec87_contract_digest": complement.contract_digest,
        "source_binding_contract_digest": binding.contract_digest,
        "source_formation_plan_set_digest": formation_plans.plan_set_digest,
        "source_probe_plan_set_digest": probe_plans.digest(),
        "contact_count": 2,
        "refinement_levels": complement.missing_refinement_levels,
        "role_ids": S1_EC45_PROBE_ROLES,
        "formation_state_roles": S1_EC52_FORMATION_STATE_ROLES,
        "budgets": budget_tuple,
        "combined_formation_steps": sum(item[5] for item in budget_tuple),
        "combined_probe_steps": sum(item[6] for item in budget_tuple),
        "combined_total_steps": sum(item[7] for item in budget_tuple),
        "formation_source_support_count": pair.repeated_plans.source_event_count,
        "probe_source_support_count": probe_plans.source_event_count,
        "all_supports_assigned_once": supports_assigned_once,
        "minimum_free_memory_bytes": S1_EC29_MIN_FREE_MEMORY_BYTES,
        "minimum_free_disk_bytes": S1_EC29_MIN_FREE_DISK_BYTES,
        "concrete_object_handoffs_ready": False,
        "runtime_caps_bound": False,
        "field_execution_permitted": False,
        "owner_authorization_present": False,
        "persistence_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "decision": "R4_R8_BUDGETS_BOUND_HANDOFFS_AND_RUNTIME_CAPS_MISSING",
        "reason": (
            "ec52-slots-and-ec27-eb1-plans-cover-r4-r8;"
            "concrete-object-handoffs-and-runtime-caps-not-yet-bound"
        ),
    }
    return E1CommonProbeEC88R4R8BudgetInventory(
        **values, inventory_digest=_digest(values)
    )
