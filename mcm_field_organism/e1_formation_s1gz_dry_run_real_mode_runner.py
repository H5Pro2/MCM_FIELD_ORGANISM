"""S1-GZ dry-run call site for the later S1-GU real-mode runner."""

from __future__ import annotations

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
from .e1_formation_s1gu_six_arm_counting_adapter import (
    run_e1_formation_s1gu_six_arm_counting_adapter,
)
from .e1_formation_s1gy_atomic_real_mode_execution_contract import (
    E1FormationS1GYAtomicRealModeExecutionContract,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GZDryRunRealModeCallSiteError(ValueError):
    """Raised when S1-GZ executes, opens authorization, or weakens the call site."""


S1_GZ_CALL_SITE_ID = "e1.s1gu-dry-run-real-mode-call-site.s1gz.v1"
S1_GZ_DECISION = "DRY_RUN_REAL_MODE_CALL_SITE_BOUND_BEFORE_CALLABLE_EXECUTION"
S1_GZ_SELECTED_TRANSITION_NAME = (
    "advance_e1_formation_s1gs_real_single_batch_transition"
)
S1_GZ_RUNNER_NAME = "run_e1_formation_s1gu_six_arm_counting_adapter"
S1_GZ_DRY_RUN_GUARDS = (
    "bind-s1gy-contract-digest",
    "bind-s1gu-runner-signature",
    "bind-s1gs-transition-signature",
    "install-block-before-carrier-transition-invocation",
    "return-no-s1gu-aggregate",
    "return-no-partial-carrier-output-or-receipt",
)


@dataclass(frozen=True, slots=True)
class E1FormationS1GZDryRunRealModeCallSite:
    call_site_id: str
    source_s1gy_contract_digest: str
    selected_transition_name: str
    runner_name: str
    runner_required_parameters: tuple[str, ...]
    runner_keyword_injection_parameter: str
    transition_required_parameters: tuple[str, ...]
    dry_run_guards: tuple[str, ...]
    role_order: tuple[tuple[str, str], ...]
    refinement_step_counts: tuple[tuple[str, int], ...]
    expected_arm_count: int
    expected_transition_count: int
    expected_field_step_count: int
    expected_source_support_count: int
    expected_output_count: int
    expected_receipt_count: int
    dry_run_gate_present: bool
    blocked_before_callable_invocation: bool
    s1gu_runner_called: bool
    s1gs_callable_called: bool
    real_kernel_called: bool
    execution_permitted: bool
    owner_authorization_present: bool
    persistence_performed: bool
    retry_permitted: bool
    claims_permitted: bool
    memory_decision_permitted: bool
    partial_return_permitted: bool
    decision: str
    reason: str
    call_site_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "call_site_digest"
        }
        if (
            self.call_site_id != S1_GZ_CALL_SITE_ID
            or len(self.source_s1gy_contract_digest) != 64
            or self.selected_transition_name != S1_GZ_SELECTED_TRANSITION_NAME
            or self.runner_name != S1_GZ_RUNNER_NAME
            or self.runner_required_parameters != ("scope", "source_contract", "bridge")
            or self.runner_keyword_injection_parameter != "carrier_transition"
            or self.transition_required_parameters != ("fresh", "batch", "carrier")
            or self.dry_run_guards != S1_GZ_DRY_RUN_GUARDS
            or self.role_order != S1_GF_ROLE_ORDER
            or self.refinement_step_counts != S1_GF_REFINEMENT_BATCH_COUNTS
            or self.expected_arm_count != 6
            or self.expected_transition_count != S1_GF_TOTAL_BATCH_COUNT
            or self.expected_field_step_count != S1_GF_TOTAL_BATCH_COUNT
            or self.expected_source_support_count != 660
            or self.expected_output_count != 6
            or self.expected_receipt_count != 6
            or self.dry_run_gate_present is not True
            or self.blocked_before_callable_invocation is not True
            or any(
                value is not False
                for value in (
                    self.s1gu_runner_called,
                    self.s1gs_callable_called,
                    self.real_kernel_called,
                    self.execution_permitted,
                    self.owner_authorization_present,
                    self.persistence_performed,
                    self.retry_permitted,
                    self.claims_permitted,
                    self.memory_decision_permitted,
                    self.partial_return_permitted,
                )
            )
            or self.decision != S1_GZ_DECISION
            or not self.reason
            or self.call_site_digest != _digest(payload)
        ):
            raise E1FormationS1GZDryRunRealModeCallSiteError(
                "S1-GZ executed, opened authorization, or changed the dry-run boundary"
            )


def prepare_e1_formation_s1gz_dry_run_real_mode_call_site(
    contract: E1FormationS1GYAtomicRealModeExecutionContract,
) -> E1FormationS1GZDryRunRealModeCallSite:
    """Bind the later S1-GU/S1-GS call site while the dry-run gate aborts first."""

    if not isinstance(contract, E1FormationS1GYAtomicRealModeExecutionContract):
        raise E1FormationS1GZDryRunRealModeCallSiteError(
            "S1-GZ requires the typed S1-GY atomic execution contract"
        )
    contract.__post_init__()
    runner_signature = inspect.signature(run_e1_formation_s1gu_six_arm_counting_adapter)
    transition_signature = inspect.signature(
        advance_e1_formation_s1gs_real_single_batch_transition
    )
    runner_required = tuple(
        name
        for name, parameter in runner_signature.parameters.items()
        if parameter.default is inspect.Signature.empty
        and parameter.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    )
    transition_required = tuple(
        name
        for name, parameter in transition_signature.parameters.items()
        if parameter.default is inspect.Signature.empty
        and parameter.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    )
    if (
        runner_signature.parameters["carrier_transition"].kind
        is not inspect.Parameter.KEYWORD_ONLY
        or contract.implementation_permitted_next is not True
        or contract.execution_permitted is not False
    ):
        raise E1FormationS1GZDryRunRealModeCallSiteError(
            "S1-GZ call site is not bound behind a closed S1-GY execution boundary"
        )
    values = {
        "call_site_id": S1_GZ_CALL_SITE_ID,
        "source_s1gy_contract_digest": contract.contract_digest,
        "selected_transition_name": S1_GZ_SELECTED_TRANSITION_NAME,
        "runner_name": S1_GZ_RUNNER_NAME,
        "runner_required_parameters": runner_required,
        "runner_keyword_injection_parameter": "carrier_transition",
        "transition_required_parameters": transition_required,
        "dry_run_guards": S1_GZ_DRY_RUN_GUARDS,
        "role_order": S1_GF_ROLE_ORDER,
        "refinement_step_counts": S1_GF_REFINEMENT_BATCH_COUNTS,
        "expected_arm_count": contract.expected_arm_count,
        "expected_transition_count": contract.expected_transition_count,
        "expected_field_step_count": contract.expected_field_step_count,
        "expected_source_support_count": contract.expected_source_support_count,
        "expected_output_count": contract.expected_output_count,
        "expected_receipt_count": contract.expected_receipt_count,
        "dry_run_gate_present": True,
        "blocked_before_callable_invocation": True,
        "s1gu_runner_called": False,
        "s1gs_callable_called": False,
        "real_kernel_called": False,
        "execution_permitted": False,
        "owner_authorization_present": False,
        "persistence_performed": False,
        "retry_permitted": False,
        "claims_permitted": False,
        "memory_decision_permitted": False,
        "partial_return_permitted": False,
        "decision": S1_GZ_DECISION,
        "reason": (
            "the-later-s1gu-real-mode-call-site-is-bound-to-the-s1gs-"
            "transition-injection-point-but-the-dry-run-gate-blocks-before-"
            "any-runner-call-callable-invocation-real-kernel-partial-return-"
            "persistence-retry-claim-or-memory-decision"
        ),
    }
    return E1FormationS1GZDryRunRealModeCallSite(
        **values,
        call_site_digest=_digest(values),
    )
