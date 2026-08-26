"""S1-GY atomic execution contract for a later S1-GU real-mode run."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_REFINEMENT_BATCH_COUNTS,
    S1_GF_ROLE_ORDER,
    S1_GF_TOTAL_BATCH_COUNT,
)
from .e1_formation_s1gu_six_arm_counting_adapter import (
    run_e1_formation_s1gu_six_arm_counting_adapter,
)
from .e1_formation_s1gx_real_mode_preflight import (
    E1FormationS1GXRealModePreflight,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GYAtomicRealModeExecutionContractError(ValueError):
    """Raised when S1-GY opens execution or weakens atomic result boundaries."""


S1_GY_CONTRACT_ID = "e1.s1gu-atomic-real-mode-execution-contract.s1gy.v1"
S1_GY_PRECONDITIONS = (
    "s1gx-preflight-digest-bound",
    "s1gw-gate-selects-s1gs-callable",
    "s1gu-source-scope-and-bridge-digests-bound",
    "six-arm-role-order-bound",
    "exact-2800-transition-budget-bound",
    "exact-660-support-budget-bound",
    "owner-authorization-remains-absent",
)
S1_GY_SINGLE_CALL = (
    "one-later-s1gu-call-only",
    "carrier-transition-from-s1gw-gate-only",
    "same-s1gt-s1gk-s1gh-source-chain-only",
    "no-retry",
    "no-parameter-change-after-start",
    "no-partial-return",
)
S1_GY_ATOMIC_RESULT = (
    "six-terminal-carriers",
    "six-s1gi-outputs",
    "six-common-probe-receipts",
    "2800-transition-digests",
    "2800-envelope-digests",
    "source-state-digests-before-after",
    "fixed-adapter-digests-before-after",
    "no-ec46-evaluation",
    "no-memory-decision",
)
S1_GY_ABORT_CONDITIONS = (
    "any-source-digest-mismatch",
    "callable-name-mismatch",
    "role-order-or-batch-order-mismatch",
    "transition-count-not-2800",
    "support-count-not-660",
    "any-source-state-or-fixed-adapter-mutation",
    "any-output-or-receipt-missing",
    "writer-persistence-retry-or-claim-attempt",
)
S1_GY_CHECK_NAMES = (
    "s1gx-preflight-is-closed-and-not-executed",
    "s1gu-runner-is-callable-but-not-called",
    "single-call-and-atomic-result-boundaries-present",
    "full-chain-ec46-memory-and-persistence-excluded",
    "contract-calls-no-runner-transition-kernel-or-writer",
)
S1_GY_DECISION = "ATOMIC_REAL_MODE_EXECUTION_CONTRACT_BOUND_NO_EXECUTION"


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
class E1FormationS1GYAtomicRealModeExecutionContract:
    contract_id: str
    source_s1gx_preflight_digest: str
    preconditions: tuple[str, ...]
    single_call_contract: tuple[str, ...]
    atomic_result_contract: tuple[str, ...]
    abort_conditions: tuple[str, ...]
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    expected_arm_count: int
    expected_transition_count: int
    expected_field_step_count: int
    expected_source_support_count: int
    expected_output_count: int
    expected_receipt_count: int
    checks: tuple[tuple[str, bool], ...]
    implementation_permitted_next: bool
    execution_permitted: bool
    owner_authorization_present: bool
    field_execution_performed: bool
    retry_permitted: bool
    persistence_performed: bool
    ec46_evaluation_permitted: bool
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
            self.contract_id != S1_GY_CONTRACT_ID
            or len(self.source_s1gx_preflight_digest) != 64
            or self.preconditions != S1_GY_PRECONDITIONS
            or self.single_call_contract != S1_GY_SINGLE_CALL
            or self.atomic_result_contract != S1_GY_ATOMIC_RESULT
            or self.abort_conditions != S1_GY_ABORT_CONDITIONS
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or self.expected_arm_count != 6
            or self.expected_transition_count != S1_GF_TOTAL_BATCH_COUNT
            or self.expected_field_step_count != S1_GF_TOTAL_BATCH_COUNT
            or self.expected_source_support_count != 660
            or self.expected_output_count != 6
            or self.expected_receipt_count != 6
            or tuple(name for name, _ in self.checks) != S1_GY_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.implementation_permitted_next is not True
            or any(
                value is not False
                for value in (
                    self.execution_permitted,
                    self.owner_authorization_present,
                    self.field_execution_performed,
                    self.retry_permitted,
                    self.persistence_performed,
                    self.ec46_evaluation_permitted,
                    self.claims_permitted,
                    self.memory_decision_permitted,
                )
            )
            or self.decision != S1_GY_DECISION
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1GYAtomicRealModeExecutionContractError(
                "S1-GY opened execution, weakened atomicity, or permitted claims"
            )


def bind_e1_formation_s1gy_atomic_real_mode_execution_contract(
    preflight: E1FormationS1GXRealModePreflight,
) -> E1FormationS1GYAtomicRealModeExecutionContract:
    """Bind a later single S1-GU real-mode call without executing it."""

    if not isinstance(preflight, E1FormationS1GXRealModePreflight):
        raise E1FormationS1GYAtomicRealModeExecutionContractError(
            "S1-GY requires the typed S1-GX preflight"
        )
    preflight.__post_init__()
    binder_source = inspect.getsource(
        bind_e1_formation_s1gy_atomic_real_mode_execution_contract
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
            S1_GY_CHECK_NAMES[0],
            preflight.callable_selected is True
            and preflight.callable_executed is False
            and preflight.s1gu_runner_executed is False
            and preflight.real_mode_execution_permitted is False,
        ),
        (
            S1_GY_CHECK_NAMES[1],
            callable(run_e1_formation_s1gu_six_arm_counting_adapter),
        ),
        (
            S1_GY_CHECK_NAMES[2],
            all(
                item in S1_GY_SINGLE_CALL
                for item in ("one-later-s1gu-call-only", "no-retry", "no-partial-return")
            )
            and all(
                item in S1_GY_ATOMIC_RESULT
                for item in ("six-s1gi-outputs", "six-common-probe-receipts")
            ),
        ),
        (
            S1_GY_CHECK_NAMES[3],
            all(
                item in S1_GY_ATOMIC_RESULT
                for item in ("no-ec46-evaluation", "no-memory-decision")
            )
            and "writer-persistence-retry-or-claim-attempt" in S1_GY_ABORT_CONDITIONS,
        ),
        (
            S1_GY_CHECK_NAMES[4],
            _called_names(binder_source).isdisjoint(forbidden_calls),
        ),
    )
    values = {
        "contract_id": S1_GY_CONTRACT_ID,
        "source_s1gx_preflight_digest": preflight.preflight_digest,
        "preconditions": S1_GY_PRECONDITIONS,
        "single_call_contract": S1_GY_SINGLE_CALL,
        "atomic_result_contract": S1_GY_ATOMIC_RESULT,
        "abort_conditions": S1_GY_ABORT_CONDITIONS,
        "role_order": S1_GF_ROLE_ORDER,
        "refinement_step_counts": S1_GF_REFINEMENT_BATCH_COUNTS,
        "expected_arm_count": preflight.expected_arm_count,
        "expected_transition_count": preflight.expected_transition_count,
        "expected_field_step_count": preflight.expected_field_step_count,
        "expected_source_support_count": preflight.expected_source_support_count,
        "expected_output_count": preflight.expected_output_count,
        "expected_receipt_count": preflight.expected_receipt_count,
        "checks": checks,
        "implementation_permitted_next": True,
        "execution_permitted": False,
        "owner_authorization_present": False,
        "field_execution_performed": False,
        "retry_permitted": False,
        "persistence_performed": False,
        "ec46_evaluation_permitted": False,
        "claims_permitted": False,
        "memory_decision_permitted": False,
        "decision": S1_GY_DECISION,
        "reason": (
            "single-later-s1gu-real-mode-call-is-specified-behind-s1gx-"
            "preflight-with-2800-transitions-660-supports-six-outputs-and-six-"
            "receipts;execution-owner-authorization-retry-persistence-ec46-"
            "claims-and-memory-decision-remain-closed"
        ),
    }
    return E1FormationS1GYAtomicRealModeExecutionContract(
        **values,
        contract_digest=_digest(values),
    )
