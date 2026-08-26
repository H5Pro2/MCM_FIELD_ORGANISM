"""S1-HA final static preflight for the bound S1-GZ real-mode call site."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1gf_fixed_adapter_positive_wrapper_fixture import (
    S1_GF_REFINEMENT_BATCH_COUNTS,
    S1_GF_ROLE_ORDER,
    S1_GF_TOTAL_BATCH_COUNT,
)
from .e1_formation_s1gy_atomic_real_mode_execution_contract import (
    E1FormationS1GYAtomicRealModeExecutionContract,
)
from .e1_formation_s1gz_dry_run_real_mode_runner import (
    E1FormationS1GZDryRunRealModeCallSite,
    S1_GZ_RUNNER_NAME,
    S1_GZ_SELECTED_TRANSITION_NAME,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1HAFinalRealModePreflightError(ValueError):
    """Raised when S1-HA detects an opened or altered execution boundary."""


S1_HA_PREFLIGHT_ID = "e1.s1gu-final-real-mode-preflight.s1ha.v1"
S1_HA_CHECK_NAMES = (
    "s1gy-contract-and-s1gz-call-site-digests-match",
    "dry-run-blocker-still-prevents-runner-and-callable",
    "six-arm-budget-and-atomic-result-unchanged",
    "owner-authorization-still-absent",
    "preflight-calls-no-runner-transition-kernel-or-writer",
)
S1_HA_DECISION = (
    "FINAL_REAL_MODE_PREFLIGHT_BOUND_OWNER_AUTHORIZATION_STILL_REQUIRED"
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
class E1FormationS1HAFinalRealModePreflight:
    preflight_id: str
    source_s1gy_contract_digest: str
    source_s1gz_call_site_digest: str
    selected_transition_name: str
    runner_name: str
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    expected_arm_count: int
    expected_transition_count: int
    expected_field_step_count: int
    expected_source_support_count: int
    expected_output_count: int
    expected_receipt_count: int
    checks: tuple[tuple[str, bool], ...]
    source_chain_bound: bool
    call_site_bound: bool
    dry_run_blocker_verified: bool
    atomic_contract_verified: bool
    owner_authorization_required_next: bool
    execution_permitted: bool
    owner_authorization_present: bool
    s1gu_runner_called: bool
    s1gs_callable_called: bool
    real_kernel_called: bool
    field_execution_performed: bool
    persistence_performed: bool
    retry_permitted: bool
    claims_permitted: bool
    memory_decision_permitted: bool
    partial_return_permitted: bool
    decision: str
    reason: str
    preflight_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "preflight_digest"
        }
        if (
            self.preflight_id != S1_HA_PREFLIGHT_ID
            or len(self.source_s1gy_contract_digest) != 64
            or len(self.source_s1gz_call_site_digest) != 64
            or self.selected_transition_name != S1_GZ_SELECTED_TRANSITION_NAME
            or self.runner_name != S1_GZ_RUNNER_NAME
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or self.expected_arm_count != 6
            or self.expected_transition_count != S1_GF_TOTAL_BATCH_COUNT
            or self.expected_field_step_count != S1_GF_TOTAL_BATCH_COUNT
            or self.expected_source_support_count != 660
            or self.expected_output_count != 6
            or self.expected_receipt_count != 6
            or tuple(name for name, _ in self.checks) != S1_HA_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or any(
                value is not True
                for value in (
                    self.source_chain_bound,
                    self.call_site_bound,
                    self.dry_run_blocker_verified,
                    self.atomic_contract_verified,
                    self.owner_authorization_required_next,
                )
            )
            or any(
                value is not False
                for value in (
                    self.execution_permitted,
                    self.owner_authorization_present,
                    self.s1gu_runner_called,
                    self.s1gs_callable_called,
                    self.real_kernel_called,
                    self.field_execution_performed,
                    self.persistence_performed,
                    self.retry_permitted,
                    self.claims_permitted,
                    self.memory_decision_permitted,
                    self.partial_return_permitted,
                )
            )
            or self.decision != S1_HA_DECISION
            or not self.reason
            or self.preflight_digest != _digest(payload)
        ):
            raise E1FormationS1HAFinalRealModePreflightError(
                "S1-HA opened execution or changed the final static preflight"
            )


def preflight_e1_formation_s1ha_final_real_mode_without_authorization(
    contract: E1FormationS1GYAtomicRealModeExecutionContract,
    call_site: E1FormationS1GZDryRunRealModeCallSite,
) -> E1FormationS1HAFinalRealModePreflight:
    """Verify the complete bound call path while owner authorization is absent."""

    if not isinstance(contract, E1FormationS1GYAtomicRealModeExecutionContract):
        raise E1FormationS1HAFinalRealModePreflightError(
            "S1-HA requires the typed S1-GY execution contract"
        )
    if not isinstance(call_site, E1FormationS1GZDryRunRealModeCallSite):
        raise E1FormationS1HAFinalRealModePreflightError(
            "S1-HA requires the typed S1-GZ dry-run call site"
        )
    contract.__post_init__()
    call_site.__post_init__()
    preflight_source = inspect.getsource(
        preflight_e1_formation_s1ha_final_real_mode_without_authorization
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
    exact_counts = (
        contract.expected_arm_count,
        contract.expected_transition_count,
        contract.expected_field_step_count,
        contract.expected_source_support_count,
        contract.expected_output_count,
        contract.expected_receipt_count,
    ) == (
        call_site.expected_arm_count,
        call_site.expected_transition_count,
        call_site.expected_field_step_count,
        call_site.expected_source_support_count,
        call_site.expected_output_count,
        call_site.expected_receipt_count,
    )
    checks = (
        (
            S1_HA_CHECK_NAMES[0],
            call_site.source_s1gy_contract_digest == contract.contract_digest,
        ),
        (
            S1_HA_CHECK_NAMES[1],
            call_site.dry_run_gate_present is True
            and call_site.blocked_before_callable_invocation is True
            and call_site.s1gu_runner_called is False
            and call_site.s1gs_callable_called is False,
        ),
        (
            S1_HA_CHECK_NAMES[2],
            exact_counts
            and contract.implementation_permitted_next is True
            and contract.execution_permitted is False,
        ),
        (
            S1_HA_CHECK_NAMES[3],
            contract.owner_authorization_present is False
            and call_site.owner_authorization_present is False
            and call_site.execution_permitted is False,
        ),
        (
            S1_HA_CHECK_NAMES[4],
            _called_names(preflight_source).isdisjoint(forbidden_calls),
        ),
    )
    if any(value is not True for _, value in checks):
        raise E1FormationS1HAFinalRealModePreflightError(
            "S1-HA source chain, call site, budget, or closed boundary mismatched"
        )
    values = {
        "preflight_id": S1_HA_PREFLIGHT_ID,
        "source_s1gy_contract_digest": contract.contract_digest,
        "source_s1gz_call_site_digest": call_site.call_site_digest,
        "selected_transition_name": call_site.selected_transition_name,
        "runner_name": call_site.runner_name,
        "role_order": call_site.role_order,
        "refinement_step_counts": call_site.refinement_step_counts,
        "expected_arm_count": call_site.expected_arm_count,
        "expected_transition_count": call_site.expected_transition_count,
        "expected_field_step_count": call_site.expected_field_step_count,
        "expected_source_support_count": call_site.expected_source_support_count,
        "expected_output_count": call_site.expected_output_count,
        "expected_receipt_count": call_site.expected_receipt_count,
        "checks": checks,
        "source_chain_bound": True,
        "call_site_bound": True,
        "dry_run_blocker_verified": True,
        "atomic_contract_verified": True,
        "owner_authorization_required_next": True,
        "execution_permitted": False,
        "owner_authorization_present": False,
        "s1gu_runner_called": False,
        "s1gs_callable_called": False,
        "real_kernel_called": False,
        "field_execution_performed": False,
        "persistence_performed": False,
        "retry_permitted": False,
        "claims_permitted": False,
        "memory_decision_permitted": False,
        "partial_return_permitted": False,
        "decision": S1_HA_DECISION,
        "reason": (
            "s1gy-and-s1gz-are-digest-bound-with-six-arms-2800-transitions-"
            "660-supports-and-atomic-six-output-six-receipt-result;the-dry-run-"
            "blocker-remains-active-and-owner-authorization-is-still-required-"
            "before-any-runner-call-callable-invocation-or-field-execution"
        ),
    }
    return E1FormationS1HAFinalRealModePreflight(
        **values,
        preflight_digest=_digest(values),
    )
