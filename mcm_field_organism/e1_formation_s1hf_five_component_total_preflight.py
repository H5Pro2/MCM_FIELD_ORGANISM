"""S1-HF static total preflight for the five local real-path components."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1ha_pure_real_transition_builder import (
    build_e1_formation_s1ha_pure_real_transition,
)
from .e1_formation_s1hb_external_owner_origin_bridge import (
    S1_HB_ORIGIN_KIND,
    bind_e1_formation_s1hb_external_owner_authorization,
)
from .e1_formation_s1hc_real_single_use_token import (
    E1FormationS1HCRealSingleUseToken,
    issue_e1_formation_s1hc_real_single_use_token,
)
from .e1_formation_s1hd_private_atomic_receipt_factory import (
    _seal_e1_formation_s1hd_real_adapter_call_receipt,
)
from .e1_formation_s1he_synthetic_gated_single_batch_adapter import (
    build_e1_formation_s1he_synthetic_adapter_gate,
    run_e1_formation_s1he_gated_single_batch_adapter_synthetically,
)
from .e1_formation_s1gz_real_path_implementation_plan import (
    E1FormationS1GZRealPathImplementationPlan,
    S1_GZ_IMPLEMENTATION_SEQUENCE,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1HFFiveComponentTotalPreflightError(ValueError):
    """Raised when the static audit hides a production boundary."""


S1_HF_PREFLIGHT_ID = "e1.five-component-total-preflight.s1hf.v1"
S1_HF_COMPONENT_STATUS = (
    ("pure-real-transition-builder", "implemented-synthetically-validated"),
    (
        "external-owner-authorization-origin-bridge",
        "local-ingress-implemented-productive-host-verifier-missing",
    ),
    ("real-single-use-token-factory", "implemented-synthetically-validated"),
    (
        "atomic-real-adapter-call-receipt-factory",
        "private-sealer-implemented-synthetically-validated",
    ),
    (
        "gated-real-single-batch-adapter",
        "atomic-flow-synthetic-only-production-kernel-closed",
    ),
)
S1_HF_PRODUCTION_BLOCKERS = (
    "authenticated-host-origin-verifier-not-connected",
    "production-kernel-not-bound-behind-authenticated-host-boundary",
)
S1_HF_CHECK_NAMES = (
    "source-plan-is-valid-and-execution-closed",
    "five-local-component-symbols-are-present",
    "component-statuses-follow-s1gz-order",
    "transition-builder-has-no-authorization-token-or-kernel-call",
    "origin-bridge-requires-an-injected-external-verifier",
    "token-factory-exposes-process-local-consume-and-retire-state",
    "receipt-sealer-is-private-and-calls-no-adapter-kernel",
    "integrated-adapter-is-explicitly-synthetic-only",
    "integrated-adapter-orders-token-callback-receipt-transition-envelope",
    "two-production-trust-boundaries-remain-explicit",
    "production-readiness-and-authorization-request-remain-closed",
    "preflight-calls-no-component-adapter-kernel-token-or-writer",
)


def _called_names(subject: object) -> tuple[str, ...]:
    names: list[str] = []
    for node in ast.walk(ast.parse(inspect.getsource(subject))):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.append(node.func.attr)
    return tuple(names)


def _call_order(subject: object, names: tuple[str, ...]) -> bool:
    called = _called_names(subject)
    positions = []
    for name in names:
        try:
            positions.append(called.index(name))
        except ValueError:
            return False
    return positions == sorted(positions) and len(set(positions)) == len(positions)


@dataclass(frozen=True, slots=True)
class E1FormationS1HFFiveComponentTotalPreflight:
    preflight_id: str
    source_s1gz_plan_digest: str
    target_digest: str
    component_status: tuple[tuple[str, str], ...]
    production_blockers: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    maximum_adapter_calls: int
    maximum_field_steps: int
    all_five_local_components_present: bool
    local_contracts_complete: bool
    synthetic_integration_complete: bool
    productive_host_verifier_connected: bool
    productive_kernel_adapter_connected: bool
    production_implementation_complete: bool
    authorization_request_ready: bool
    execution_permitted: bool
    authorization_present: bool
    token_created: bool
    receipt_created: bool
    transition_created: bool
    adapter_calls: int
    field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
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
            self.preflight_id != S1_HF_PREFLIGHT_ID
            or len(self.source_s1gz_plan_digest) != 64
            or len(self.target_digest) != 64
            or self.component_status != S1_HF_COMPONENT_STATUS
            or self.production_blockers != S1_HF_PRODUCTION_BLOCKERS
            or tuple(name for name, _ in self.checks) != S1_HF_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.maximum_adapter_calls != 1
            or self.maximum_field_steps != 1
            or self.all_five_local_components_present is not True
            or self.local_contracts_complete is not True
            or self.synthetic_integration_complete is not True
            or any(
                value is not False
                for value in (
                    self.productive_host_verifier_connected,
                    self.productive_kernel_adapter_connected,
                    self.production_implementation_complete,
                    self.authorization_request_ready,
                    self.execution_permitted,
                    self.authorization_present,
                    self.token_created,
                    self.receipt_created,
                    self.transition_created,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.adapter_calls != 0
            or self.field_steps_executed != 0
            or self.decision
            != "FIVE_LOCAL_COMPONENTS_COMPLETE_PRODUCTION_TRUST_BOUNDARIES_MISSING"
            or not self.reason
            or self.preflight_digest != _digest(payload)
        ):
            raise E1FormationS1HFFiveComponentTotalPreflightError(
                "S1-HF hid a production boundary or opened execution"
            )


def audit_e1_formation_s1hf_five_component_total_preflight(
    plan: E1FormationS1GZRealPathImplementationPlan,
) -> E1FormationS1HFFiveComponentTotalPreflight:
    """Audit local implementation completeness without creating run objects."""

    if not isinstance(plan, E1FormationS1GZRealPathImplementationPlan):
        raise E1FormationS1HFFiveComponentTotalPreflightError(
            "S1-HF requires the exact S1-GZ implementation plan"
        )
    plan.__post_init__()

    builder_calls = set(_called_names(build_e1_formation_s1ha_pure_real_transition))
    bridge_signature = inspect.signature(
        bind_e1_formation_s1hb_external_owner_authorization
    )
    token_methods = {
        name for name in ("consume", "retire")
        if callable(getattr(E1FormationS1HCRealSingleUseToken, name, None))
    }
    receipt_calls = set(
        _called_names(_seal_e1_formation_s1hd_real_adapter_call_receipt)
    )
    synthetic_gate = build_e1_formation_s1he_synthetic_adapter_gate()
    preflight_calls = set(
        _called_names(audit_e1_formation_s1hf_five_component_total_preflight)
    )

    component_symbols = (
        build_e1_formation_s1ha_pure_real_transition,
        bind_e1_formation_s1hb_external_owner_authorization,
        issue_e1_formation_s1hc_real_single_use_token,
        _seal_e1_formation_s1hd_real_adapter_call_receipt,
        run_e1_formation_s1he_gated_single_batch_adapter_synthetically,
    )
    forbidden_preflight_calls = {
        "build_e1_formation_s1ha_pure_real_transition",
        "bind_e1_formation_s1hb_external_owner_authorization",
        "issue_e1_formation_s1hc_real_single_use_token",
        "_seal_e1_formation_s1hd_real_adapter_call_receipt",
        "run_e1_formation_s1he_gated_single_batch_adapter_synthetically",
        "advance_fixed_e1_adapter_fast_shared_field_transient",
        "consume",
        "retire",
        "open",
        "write_text",
        "write_bytes",
    }
    checks = (
        (
            S1_HF_CHECK_NAMES[0],
            plan.implementation_ready is False
            and plan.authorization_request_ready is False
            and plan.adapter_calls == 0
            and plan.field_steps_executed == 0,
        ),
        (S1_HF_CHECK_NAMES[1], all(callable(item) for item in component_symbols)),
        (
            S1_HF_CHECK_NAMES[2],
            tuple(name for name, _ in S1_HF_COMPONENT_STATUS)
            == S1_GZ_IMPLEMENTATION_SEQUENCE,
        ),
        (
            S1_HF_CHECK_NAMES[3],
            builder_calls.isdisjoint(
                {
                    "bind_e1_formation_s1hb_external_owner_authorization",
                    "issue_e1_formation_s1hc_real_single_use_token",
                    "advance_fixed_e1_adapter_fast_shared_field_transient",
                }
            ),
        ),
        (
            S1_HF_CHECK_NAMES[4],
            "origin_verifier" in bridge_signature.parameters
            and bridge_signature.parameters["origin_verifier"].kind
            is inspect.Parameter.KEYWORD_ONLY
            and S1_HB_ORIGIN_KIND == "external-host-owner-message",
        ),
        (S1_HF_CHECK_NAMES[5], token_methods == {"consume", "retire"}),
        (
            S1_HF_CHECK_NAMES[6],
            _seal_e1_formation_s1hd_real_adapter_call_receipt.__name__.startswith("_")
            and "advance_fixed_e1_adapter_fast_shared_field_transient"
            not in receipt_calls,
        ),
        (
            S1_HF_CHECK_NAMES[7],
            synthetic_gate.synthetic_only is True
            and synthetic_gate.production_kernel_permitted is False,
        ),
        (
            S1_HF_CHECK_NAMES[8],
            _call_order(
                run_e1_formation_s1he_gated_single_batch_adapter_synthetically,
                (
                    "consume",
                    "synthetic_kernel",
                    "_seal_e1_formation_s1hd_real_adapter_call_receipt",
                    "build_e1_formation_s1ha_pure_real_transition",
                    "bind_e1_formation_s1gq_carrier_transition_envelope",
                    "retire",
                ),
            ),
        ),
        (
            S1_HF_CHECK_NAMES[9],
            S1_HF_PRODUCTION_BLOCKERS
            == (
                "authenticated-host-origin-verifier-not-connected",
                "production-kernel-not-bound-behind-authenticated-host-boundary",
            ),
        ),
        (
            S1_HF_CHECK_NAMES[10],
            plan.authorization_request_ready is False
            and plan.authorization_present is False
            and synthetic_gate.production_kernel_permitted is False,
        ),
        (
            S1_HF_CHECK_NAMES[11],
            preflight_calls.isdisjoint(forbidden_preflight_calls),
        ),
    )
    values = {
        "preflight_id": S1_HF_PREFLIGHT_ID,
        "source_s1gz_plan_digest": plan.plan_digest,
        "target_digest": plan.target_digest,
        "component_status": S1_HF_COMPONENT_STATUS,
        "production_blockers": S1_HF_PRODUCTION_BLOCKERS,
        "checks": checks,
        "maximum_adapter_calls": 1,
        "maximum_field_steps": 1,
        "all_five_local_components_present": all(
            value for _, value in checks[:9]
        ),
        "local_contracts_complete": all(value for _, value in checks),
        "synthetic_integration_complete": True,
        "productive_host_verifier_connected": False,
        "productive_kernel_adapter_connected": False,
        "production_implementation_complete": False,
        "authorization_request_ready": False,
        "execution_permitted": False,
        "authorization_present": False,
        "token_created": False,
        "receipt_created": False,
        "transition_created": False,
        "adapter_calls": 0,
        "field_steps_executed": 0,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "FIVE_LOCAL_COMPONENTS_COMPLETE_"
            "PRODUCTION_TRUST_BOUNDARIES_MISSING"
        ),
        "reason": (
            "all-five-local-components-and-the-synthetic-atomic-flow-are-"
            "present;the-authenticated-host-origin-verifier-and-a-production-"
            "kernel-path-bound-behind-that-host-boundary-are-not-connected;"
            "authorization-request-and-execution-remain-closed"
        ),
    }
    return E1FormationS1HFFiveComponentTotalPreflight(
        **values,
        preflight_digest=_digest(values),
    )
