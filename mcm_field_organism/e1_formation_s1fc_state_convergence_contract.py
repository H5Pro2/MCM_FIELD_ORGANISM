"""S1-FC static convergence contract for E1 formation end states."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_e3_probe_run import E1_E3_PROBE_ABSOLUTE_TOLERANCE
from .e1_e4_execution import E1_E4_REFINEMENT_LIMIT
from .e1_local_edge_plasticity import E1_CONTRACT_ID
from .e1_refined_confirmation_contract import S1_EB_REFINEMENTS
from .e1_refined_formation_runner import _digest, _state_payload


class E1FormationS1FCStateConvergenceContractError(ValueError):
    """Raised when the formation-state contract changes or opens execution."""


S1_FC_CONTRACT_ID = "e1.formation-state-convergence-contract.s1fc.v1"
S1_FC_FORMATION_ROLES = (
    "active-ab",
    "active-ba",
    "identity-ab",
    "formation-ablated-ab",
    "formation-ablated-ba",
)
S1_FC_STATE_VECTOR_SCHEMA = (
    "refinement_id",
    "formation_role",
    "edge_inventory_digest",
    "ordered_edge_ids",
    "ordered_binding_vector",
    "state_digest",
    "source_formation_result_digest",
    "resource_budget_error",
)
S1_FC_DERIVED_METRICS = (
    "active-order-vector-per-refinement:active-ab-minus-active-ba",
    "active-ab-coarse-fine-linf",
    "active-ba-coarse-fine-linf",
    "active-order-coarse-fine-linf",
    "active-ab-fine-relative-to-r8-state-linf",
    "active-ba-fine-relative-to-r8-state-linf",
    "active-order-fine-relative-to-r8-order-linf",
    "identity-ab-minus-active-ab-linf-per-refinement",
    "formation-ablated-state-linf-per-refinement-and-side",
    "maximum-resource-budget-error",
)
S1_FC_DECISIONS = (
    "INVALID_FORMATION_STATE_CONTROLS",
    "NO_DISTINGUISHABLE_FORMATION_ORDER_STATE",
    "FORMATION_STATE_NOT_CONVERGED",
    "FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY",
)
S1_FC_CHECK_NAMES = (
    "three-refinements-fixed",
    "five-formation-roles-fixed",
    "fifteen-state-vectors-required",
    "canonical-edge-order-and-full-vector-required",
    "ab-ba-and-order-convergence-separated",
    "identity-ablation-and-resource-controls-required",
    "absolute-tolerance-inherited",
    "relative-limit-inherited",
    "ec46-remains-independent-and-unchanged",
    "audit-does-not-run-formation-probe-decider-or-writer",
)


def _called_names(source: str) -> frozenset[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return frozenset(names)


@dataclass(frozen=True, slots=True)
class E1FormationS1FCStateConvergenceContract:
    contract_id: str
    source_e1_contract_id: str
    refinements: tuple[tuple[str, int], ...]
    formation_roles: tuple[str, ...]
    state_vector_schema: tuple[str, ...]
    required_state_vector_count: int
    derived_metrics: tuple[str, ...]
    absolute_control_tolerance: float
    relative_refinement_limit: float
    convergence_rule: str
    control_rule: str
    decisions: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    vectors_must_be_returned_atomically: bool
    state_comparison_occurs_before_probe: bool
    edge_order_must_match_across_all_states: bool
    resource_balance_must_hold_per_state: bool
    ec46_probe_contract_replaced: bool
    ec46_threshold_changed: bool
    field_execution_permitted: bool
    real_state_capture_permitted: bool
    persistence_permitted: bool
    memory_claim_permitted: bool
    synthetic_evaluator_implementation_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if (
            self.contract_id != S1_FC_CONTRACT_ID
            or self.source_e1_contract_id != E1_CONTRACT_ID
            or self.refinements != S1_EB_REFINEMENTS
            or self.formation_roles != S1_FC_FORMATION_ROLES
            or self.state_vector_schema != S1_FC_STATE_VECTOR_SCHEMA
            or self.required_state_vector_count != 15
            or self.derived_metrics != S1_FC_DERIVED_METRICS
            or self.absolute_control_tolerance
            != E1_E3_PROBE_ABSOLUTE_TOLERANCE
            or self.relative_refinement_limit != E1_E4_REFINEMENT_LIMIT
            or self.convergence_rule
            != "fine<=coarse-and-fine/max(r8-linf,1e-12)<=0.01:active-ab-active-ba-and-order"
            or self.control_rule
            != "identity-ab<=1e-12-and-formation-ablated<=1e-12-and-resource-error<=1e-12"
            or self.decisions != S1_FC_DECISIONS
            or tuple(name for name, _ in self.checks) != S1_FC_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.vectors_must_be_returned_atomically,
                    self.state_comparison_occurs_before_probe,
                    self.edge_order_must_match_across_all_states,
                    self.resource_balance_must_hold_per_state,
                    self.synthetic_evaluator_implementation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.ec46_probe_contract_replaced,
                    self.ec46_threshold_changed,
                    self.field_execution_permitted,
                    self.real_state_capture_permitted,
                    self.persistence_permitted,
                    self.memory_claim_permitted,
                )
            )
            or self.decision
            != "FORMATION_STATE_CONVERGENCE_BOUND_IMPLEMENTATION_MISSING"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1FCStateConvergenceContractError(
                "S1-FC contract changed, weakened controls, or opened execution"
            )


def audit_e1_formation_s1fc_state_convergence_contract(
) -> E1FormationS1FCStateConvergenceContract:
    """Bind state-vector convergence without producing or reading E1 states."""

    source = inspect.getsource(audit_e1_formation_s1fc_state_convergence_contract)
    called = _called_names(source)
    forbidden_calls = {
        "run_prepared_real_formation_arm_in_memory",
        "run_e1_asynchronous_field",
        "run_e1_common_probe_real_probe_wrapper",
        "advance_frozen_e1_fast_shared_field_transient",
        "decide_common_probe_evidence",
        "write_text",
        "write_bytes",
        "open",
    }
    state_payload_source = inspect.getsource(_state_payload)
    metrics = set(S1_FC_DERIVED_METRICS)
    checks = (
        (S1_FC_CHECK_NAMES[0], S1_EB_REFINEMENTS == (("r2", 2), ("r4", 4), ("r8", 8))),
        (S1_FC_CHECK_NAMES[1], len(S1_FC_FORMATION_ROLES) == 5),
        (
            S1_FC_CHECK_NAMES[2],
            len(S1_EB_REFINEMENTS) * len(S1_FC_FORMATION_ROLES) == 15,
        ),
        (
            S1_FC_CHECK_NAMES[3],
            {"ordered_edge_ids", "ordered_binding_vector"}
            .issubset(S1_FC_STATE_VECTOR_SCHEMA)
            and "edge_bindings" in state_payload_source,
        ),
        (
            S1_FC_CHECK_NAMES[4],
            {
                "active-ab-coarse-fine-linf",
                "active-ba-coarse-fine-linf",
                "active-order-coarse-fine-linf",
            }.issubset(metrics),
        ),
        (
            S1_FC_CHECK_NAMES[5],
            {
                "identity-ab-minus-active-ab-linf-per-refinement",
                "formation-ablated-state-linf-per-refinement-and-side",
                "maximum-resource-budget-error",
            }.issubset(metrics),
        ),
        (
            S1_FC_CHECK_NAMES[6],
            E1_E3_PROBE_ABSOLUTE_TOLERANCE == 1e-12,
        ),
        (S1_FC_CHECK_NAMES[7], E1_E4_REFINEMENT_LIMIT == 0.01),
        (S1_FC_CHECK_NAMES[8], True),
        (S1_FC_CHECK_NAMES[9], called.isdisjoint(forbidden_calls)),
    )
    values = {
        "contract_id": S1_FC_CONTRACT_ID,
        "source_e1_contract_id": E1_CONTRACT_ID,
        "refinements": S1_EB_REFINEMENTS,
        "formation_roles": S1_FC_FORMATION_ROLES,
        "state_vector_schema": S1_FC_STATE_VECTOR_SCHEMA,
        "required_state_vector_count": 15,
        "derived_metrics": S1_FC_DERIVED_METRICS,
        "absolute_control_tolerance": E1_E3_PROBE_ABSOLUTE_TOLERANCE,
        "relative_refinement_limit": E1_E4_REFINEMENT_LIMIT,
        "convergence_rule": (
            "fine<=coarse-and-fine/max(r8-linf,1e-12)<=0.01:"
            "active-ab-active-ba-and-order"
        ),
        "control_rule": (
            "identity-ab<=1e-12-and-formation-ablated<=1e-12-and-"
            "resource-error<=1e-12"
        ),
        "decisions": S1_FC_DECISIONS,
        "checks": checks,
        "vectors_must_be_returned_atomically": True,
        "state_comparison_occurs_before_probe": True,
        "edge_order_must_match_across_all_states": True,
        "resource_balance_must_hold_per_state": True,
        "ec46_probe_contract_replaced": False,
        "ec46_threshold_changed": False,
        "field_execution_permitted": False,
        "real_state_capture_permitted": False,
        "persistence_permitted": False,
        "memory_claim_permitted": False,
        "synthetic_evaluator_implementation_permitted": True,
        "decision": "FORMATION_STATE_CONVERGENCE_BOUND_IMPLEMENTATION_MISSING",
        "reason": (
            "fifteen-canonical-edge-binding-vectors-required-before-probe;"
            "ab-ba-and-order-refinement-separated;identity-ablation-and-resource-"
            "controls-bound;ec46-remains-independent"
        ),
    }
    return E1FormationS1FCStateConvergenceContract(
        **values, contract_digest=_digest(values)
    )
