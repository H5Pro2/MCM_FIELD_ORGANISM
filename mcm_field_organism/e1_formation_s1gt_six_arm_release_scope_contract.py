"""S1-GT static release-scope contract for a bounded six-arm fixed-adapter probe."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_REFINEMENT_BATCH_COUNTS,
    S1_GF_ROLE_ORDER,
    S1_GF_TOTAL_BATCH_COUNT,
)
from .e1_formation_s1gk_fixed_adapter_real_wrapper_contract import (
    E1FormationS1GKFixedAdapterRealWrapperContract,
)
from .e1_formation_s1go_private_carrier_wrapper import (
    run_e1_formation_s1go_private_carrier_wrapper,
)
from .e1_formation_s1gs_real_single_batch_transition import (
    advance_e1_formation_s1gs_real_single_batch_transition,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GTSixArmReleaseScopeContractError(ValueError):
    """Raised when S1-GT opens execution or widens the fixed-adapter scope."""


S1_GT_CONTRACT_ID = "e1.fixed-adapter-six-arm-release-scope.s1gt.v1"
S1_GT_RELEASE_SCOPE = (
    "six-fixed-adapter-arms-only",
    "r2-r4-r8-ab-ba-role-order-only",
    "use-existing-s1gh-fresh-fields-and-s1gd-invocations",
    "use-s1gs-real-single-batch-transition-as-only-real-step-adapter",
    "validate-each-transition-through-s1gq-envelope",
    "return-six-s1gi-outputs-and-six-common-receipts-atomically",
)
S1_GT_EXCLUDED_SCOPE = (
    "no-formation-run",
    "no-frozen-e1-active-probe",
    "no-p0-probe",
    "no-formation-ablation-probe",
    "no-probe-backreaction-ablation-probe",
    "no-ec46-or-memory-decision",
    "no-45-call-same-session-chain",
    "no-writer-or-persistence",
    "no-retry-or-posthoc-parameter-change",
)
S1_GT_REQUIRED_GATES = (
    "s1gs-single-batch-real-envelope-validated",
    "s1go-synthetic-only-reference-remains-closed-to-real-envelope",
    "all-six-inputs-validated-before-first-field-step",
    "exact-2800-batch-budget-bound",
    "exact-660-source-support-budget-bound",
    "source-state-and-fixed-adapter-digests-preserved",
    "atomic-six-result-boundary-required",
)
S1_GT_ABORT_CONDITIONS = (
    "any-source-contract-digest-mismatch",
    "role-order-or-batch-order-mismatch",
    "unexpected-transition-kind",
    "field-step-count-differs-from-2800",
    "source-support-count-differs-from-660",
    "source-state-or-fixed-adapter-digest-changes",
    "partial-arm-output",
    "writer-retry-persistence-or-claim-attempt",
)
S1_GT_CHECK_NAMES = (
    "source-s1gk-contract-is-execution-closed",
    "s1gs-real-single-batch-adapter-is-present",
    "s1go-wrapper-remains-synthetic-gated-reference",
    "six-arm-role-and-refinement-budget-bound",
    "scope-excludes-full-common-probe-matrix",
    "contract-calls-no-real-runner-kernel-or-writer",
)
S1_GT_DECISION = (
    "SIX_ARM_FIXED_ADAPTER_RELEASE_SCOPE_BOUND_STATIC_EXECUTION_CLOSED"
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
class E1FormationS1GTSixArmReleaseScopeContract:
    contract_id: str
    source_s1gk_contract_digest: str
    release_scope: tuple[str, ...]
    excluded_scope: tuple[str, ...]
    required_gates: tuple[str, ...]
    abort_conditions: tuple[str, ...]
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    fixed_adapter_arm_count: int
    planned_real_transition_count: int
    planned_field_step_count: int
    planned_source_support_count: int
    full_chain_call_count_permitted: int
    full_chain_field_steps_permitted: int
    checks: tuple[tuple[str, bool], ...]
    s1gs_adapter_imported_for_static_binding: bool
    s1go_wrapper_reference_imported_for_static_gate_check: bool
    six_arm_implementation_permitted_next: bool
    owner_authorization_present: bool
    execution_permitted: bool
    field_execution_performed: bool
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
            self.contract_id != S1_GT_CONTRACT_ID
            or len(self.source_s1gk_contract_digest) != 64
            or self.release_scope != S1_GT_RELEASE_SCOPE
            or self.excluded_scope != S1_GT_EXCLUDED_SCOPE
            or self.required_gates != S1_GT_REQUIRED_GATES
            or self.abort_conditions != S1_GT_ABORT_CONDITIONS
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or self.fixed_adapter_arm_count != 6
            or self.planned_real_transition_count != S1_GF_TOTAL_BATCH_COUNT
            or self.planned_field_step_count != S1_GF_TOTAL_BATCH_COUNT
            or self.planned_source_support_count != 660
            or self.full_chain_call_count_permitted != 0
            or self.full_chain_field_steps_permitted != 0
            or tuple(name for name, _ in self.checks) != S1_GT_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.s1gs_adapter_imported_for_static_binding,
                    self.s1go_wrapper_reference_imported_for_static_gate_check,
                    self.six_arm_implementation_permitted_next,
                )
            )
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.retry_permitted,
                    self.claims_permitted,
                    self.memory_decision_permitted,
                )
            )
            or self.decision != S1_GT_DECISION
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1GTSixArmReleaseScopeContractError(
                "S1-GT contract changed scope, opened execution, or permitted claims"
            )


def bind_e1_formation_s1gt_six_arm_release_scope_contract(
    source_contract: E1FormationS1GKFixedAdapterRealWrapperContract,
) -> E1FormationS1GTSixArmReleaseScopeContract:
    """Bind the next six-arm fixed-adapter scope without running a field."""

    if not isinstance(source_contract, E1FormationS1GKFixedAdapterRealWrapperContract):
        raise E1FormationS1GTSixArmReleaseScopeContractError(
            "S1-GT requires the typed S1-GK source contract"
        )
    source_contract.__post_init__()
    binder_source = inspect.getsource(
        bind_e1_formation_s1gt_six_arm_release_scope_contract
    )
    s1go_source = inspect.getsource(run_e1_formation_s1go_private_carrier_wrapper)
    forbidden_calls = {
        "advance_e1_formation_s1gs_real_single_batch_transition",
        "run_e1_formation_s1go_private_carrier_wrapper",
        "map_proposal_batch_to_transient_docks",
        "project_transient_docks_to_neuron_inputs",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "open",
        "write_text",
        "write_bytes",
    }
    checks = (
        (
            S1_GT_CHECK_NAMES[0],
            source_contract.execution_permitted is False
            and source_contract.field_execution_performed is False
            and source_contract.planned_field_step_count
            == S1_GF_TOTAL_BATCH_COUNT,
        ),
        (
            S1_GT_CHECK_NAMES[1],
            callable(advance_e1_formation_s1gs_real_single_batch_transition),
        ),
        (
            S1_GT_CHECK_NAMES[2],
            "synthetic-no-field-advance" in s1go_source
            and "real-field-advance" not in s1go_source,
        ),
        (
            S1_GT_CHECK_NAMES[3],
            source_contract.role_order == S1_GF_ROLE_ORDER
            and source_contract.refinement_step_counts
            == S1_GF_REFINEMENT_BATCH_COUNTS
            and source_contract.wrapper_arm_count == 6,
        ),
        (
            S1_GT_CHECK_NAMES[4],
            all(item in S1_GT_EXCLUDED_SCOPE for item in (
                "no-45-call-same-session-chain",
                "no-ec46-or-memory-decision",
                "no-formation-run",
            )),
        ),
        (
            S1_GT_CHECK_NAMES[5],
            _called_names(binder_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "contract_id": S1_GT_CONTRACT_ID,
        "source_s1gk_contract_digest": source_contract.contract_digest,
        "release_scope": S1_GT_RELEASE_SCOPE,
        "excluded_scope": S1_GT_EXCLUDED_SCOPE,
        "required_gates": S1_GT_REQUIRED_GATES,
        "abort_conditions": S1_GT_ABORT_CONDITIONS,
        "role_order": S1_GF_ROLE_ORDER,
        "refinement_step_counts": S1_GF_REFINEMENT_BATCH_COUNTS,
        "fixed_adapter_arm_count": 6,
        "planned_real_transition_count": S1_GF_TOTAL_BATCH_COUNT,
        "planned_field_step_count": S1_GF_TOTAL_BATCH_COUNT,
        "planned_source_support_count": 660,
        "full_chain_call_count_permitted": 0,
        "full_chain_field_steps_permitted": 0,
        "checks": checks,
        "s1gs_adapter_imported_for_static_binding": True,
        "s1go_wrapper_reference_imported_for_static_gate_check": True,
        "six_arm_implementation_permitted_next": True,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "retry_permitted": False,
        "claims_permitted": False,
        "memory_decision_permitted": False,
        "decision": S1_GT_DECISION,
        "reason": (
            "after-s1gs-only-a-bounded-six-fixed-adapter-arm-implementation-"
            "is-in-scope;2800-real-transitions-and-660-supports-are-bound-for-"
            "a-later-runner;full-45-call-chain-ec46-memory-decision-writers-"
            "and-retry-remain-excluded"
        ),
    }
    return E1FormationS1GTSixArmReleaseScopeContract(
        **values,
        contract_digest=_digest(values),
    )
