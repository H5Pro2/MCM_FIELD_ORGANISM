"""S1-GV static binding contract for S1-GU real-mode injection."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_REFINEMENT_BATCH_COUNTS,
    S1_GF_ROLE_ORDER,
    S1_GF_TOTAL_BATCH_COUNT,
)
from .e1_formation_s1gs_real_single_batch_transition import (
    advance_e1_formation_s1gs_real_single_batch_transition,
)
from .e1_formation_s1gt_six_arm_release_scope_contract import (
    E1FormationS1GTSixArmReleaseScopeContract,
)
from .e1_formation_s1gu_six_arm_counting_adapter import (
    run_e1_formation_s1gu_six_arm_counting_adapter,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GVRealModeBindingContractError(ValueError):
    """Raised when S1-GV opens execution or widens the real-mode boundary."""


S1_GV_CONTRACT_ID = "e1.fixed-adapter-real-mode-binding.s1gv.v1"
S1_GV_REAL_MODE_BINDINGS = (
    "s1gu-carrier-transition-injection-point",
    "s1gs-real-single-batch-transition-function",
    "s1gq-real-field-advance-envelope",
    "six-arm-r2-r4-r8-ab-ba-role-order",
    "exact-2800-real-transition-budget",
    "exact-660-source-support-budget",
)
S1_GV_REMAINING_CLOSED = (
    "no-real-mode-run",
    "no-owner-authorization",
    "no-formation-run",
    "no-p0-probe",
    "no-frozen-e1-active-probe",
    "no-probe-backreaction-ablation",
    "no-formation-ablation",
    "no-45-call-chain",
    "no-ec46-evaluation",
    "no-fixed-adapter-final-explanation",
    "no-persistence-or-writer",
    "no-retry",
    "no-memory-claim",
)
S1_GV_CHECK_NAMES = (
    "s1gt-scope-is-execution-closed",
    "s1gu-exposes-callable-transition-injection",
    "s1gs-real-transition-is-callable",
    "real-mode-budget-matches-six-arm-scope",
    "closed-boundaries-exclude-full-chain-and-claims",
    "contract-calls-no-adapter-runner-kernel-or-writer",
)
S1_GV_DECISION = (
    "S1GU_REAL_MODE_INJECTION_BOUND_STATIC_EXECUTION_AND_CLAIMS_CLOSED"
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
class E1FormationS1GVRealModeBindingContract:
    contract_id: str
    source_s1gt_contract_digest: str
    real_mode_bindings: tuple[str, ...]
    remaining_closed: tuple[str, ...]
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    planned_real_transition_count: int
    planned_field_step_count: int
    planned_source_support_count: int
    checks: tuple[tuple[str, bool], ...]
    s1gu_transition_injection_present: bool
    s1gs_real_transition_bound: bool
    real_mode_implementation_permitted_next: bool
    real_mode_execution_permitted: bool
    owner_authorization_present: bool
    field_execution_performed: bool
    full_chain_opened: bool
    persistence_performed: bool
    retry_permitted: bool
    claims_permitted: bool
    memory_decision_permitted: bool
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
            self.contract_id != S1_GV_CONTRACT_ID
            or len(self.source_s1gt_contract_digest) != 64
            or self.real_mode_bindings != S1_GV_REAL_MODE_BINDINGS
            or self.remaining_closed != S1_GV_REMAINING_CLOSED
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or self.planned_real_transition_count != S1_GF_TOTAL_BATCH_COUNT
            or self.planned_field_step_count != S1_GF_TOTAL_BATCH_COUNT
            or self.planned_source_support_count != 660
            or tuple(name for name, _ in self.checks) != S1_GV_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.s1gu_transition_injection_present,
                    self.s1gs_real_transition_bound,
                    self.real_mode_implementation_permitted_next,
                )
            )
            or any(
                value is not False
                for value in (
                    self.real_mode_execution_permitted,
                    self.owner_authorization_present,
                    self.field_execution_performed,
                    self.full_chain_opened,
                    self.persistence_performed,
                    self.retry_permitted,
                    self.claims_permitted,
                    self.memory_decision_permitted,
                )
            )
            or self.decision != S1_GV_DECISION
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1GVRealModeBindingContractError(
                "S1-GV changed real-mode binding, opened execution, or permitted claims"
            )


def bind_e1_formation_s1gv_real_mode_binding_contract(
    scope: E1FormationS1GTSixArmReleaseScopeContract,
) -> E1FormationS1GVRealModeBindingContract:
    """Bind S1-GS as S1-GU real-mode injection without running it."""

    if not isinstance(scope, E1FormationS1GTSixArmReleaseScopeContract):
        raise E1FormationS1GVRealModeBindingContractError(
            "S1-GV requires the typed S1-GT scope"
        )
    scope.__post_init__()
    binder_source = inspect.getsource(bind_e1_formation_s1gv_real_mode_binding_contract)
    s1gu_signature = inspect.signature(run_e1_formation_s1gu_six_arm_counting_adapter)
    s1gs_signature = inspect.signature(
        advance_e1_formation_s1gs_real_single_batch_transition
    )
    forbidden_calls = {
        "run_e1_formation_s1gu_six_arm_counting_adapter",
        "advance_e1_formation_s1gs_real_single_batch_transition",
        "map_proposal_batch_to_transient_docks",
        "project_transient_docks_to_neuron_inputs",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "open",
        "write_text",
        "write_bytes",
    }
    checks = (
        (
            S1_GV_CHECK_NAMES[0],
            scope.execution_permitted is False
            and scope.field_execution_performed is False
            and scope.planned_real_transition_count == S1_GF_TOTAL_BATCH_COUNT,
        ),
        (
            S1_GV_CHECK_NAMES[1],
            "carrier_transition" in s1gu_signature.parameters,
        ),
        (
            S1_GV_CHECK_NAMES[2],
            callable(advance_e1_formation_s1gs_real_single_batch_transition)
            and tuple(s1gs_signature.parameters) == ("fresh", "batch", "carrier"),
        ),
        (
            S1_GV_CHECK_NAMES[3],
            scope.role_order == S1_GF_ROLE_ORDER
            and scope.refinement_step_counts == S1_GF_REFINEMENT_BATCH_COUNTS
            and scope.planned_field_step_count == S1_GF_TOTAL_BATCH_COUNT
            and scope.planned_source_support_count == 660,
        ),
        (
            S1_GV_CHECK_NAMES[4],
            all(
                item in S1_GV_REMAINING_CLOSED
                for item in (
                    "no-real-mode-run",
                    "no-45-call-chain",
                    "no-memory-claim",
                    "no-persistence-or-writer",
                )
            ),
        ),
        (
            S1_GV_CHECK_NAMES[5],
            _called_names(binder_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "contract_id": S1_GV_CONTRACT_ID,
        "source_s1gt_contract_digest": scope.contract_digest,
        "real_mode_bindings": S1_GV_REAL_MODE_BINDINGS,
        "remaining_closed": S1_GV_REMAINING_CLOSED,
        "role_order": S1_GF_ROLE_ORDER,
        "refinement_step_counts": S1_GF_REFINEMENT_BATCH_COUNTS,
        "planned_real_transition_count": S1_GF_TOTAL_BATCH_COUNT,
        "planned_field_step_count": S1_GF_TOTAL_BATCH_COUNT,
        "planned_source_support_count": 660,
        "checks": checks,
        "s1gu_transition_injection_present": True,
        "s1gs_real_transition_bound": True,
        "real_mode_implementation_permitted_next": True,
        "real_mode_execution_permitted": False,
        "owner_authorization_present": False,
        "field_execution_performed": False,
        "full_chain_opened": False,
        "persistence_performed": False,
        "retry_permitted": False,
        "claims_permitted": False,
        "memory_decision_permitted": False,
        "decision": S1_GV_DECISION,
        "reason": (
            "s1gs-is-bound-as-the-only-s1gu-real-mode-transition-injection-for-"
            "a-later-six-arm-adapter;2800-real-steps-and-660-supports-remain-"
            "budgeted-but-no-real-mode-run-owner-authorization-full-chain-"
            "persistence-retry-claim-or-memory-decision-is-opened"
        ),
    }
    return E1FormationS1GVRealModeBindingContract(
        **values,
        contract_digest=_digest(values),
    )
