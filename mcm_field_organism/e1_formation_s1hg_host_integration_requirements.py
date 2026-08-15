"""S1-HG closed requirements for an external trusted host integration."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import inspect

from .e1_formation_s1hb_external_owner_origin_bridge import (
    E1FormationS1HBExternalOwnerOriginEvent,
)
from .e1_formation_s1hf_five_component_total_preflight import (
    E1FormationS1HFFiveComponentTotalPreflight,
    S1_HF_PRODUCTION_BLOCKERS,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1HGHostIntegrationRequirementsError(ValueError):
    """Raised when requirements infer trust or open the production path."""


S1_HG_CONTRACT_ID = "e1.host-integration-requirements.s1hg.v1"
S1_HG_REQUIRED_EXTERNAL_EVENT_FIELDS = (
    "host_provider_id",
    "authenticated_owner_principal_digest",
    "task_or_session_binding_digest",
    "fresh_single_use_nonce_digest",
    "host_attestation_digest",
    "owner_message_digest",
    "project_id",
    "run_id",
    "gate_digest",
    "binding_digest",
    "batch_index",
    "carrier_digest",
    "maximum_adapter_calls",
    "maximum_field_steps",
    "host_sequence",
    "event_digest",
)
S1_HG_REQUIRED_HOST_CAPABILITY_FIELDS = (
    "capability_id",
    "host_provider_id",
    "source_external_event_digest",
    "authorization_digest",
    "task_or_session_binding_digest",
    "fresh_single_use_nonce_digest",
    "run_id",
    "gate_digest",
    "binding_digest",
    "batch_index",
    "carrier_digest",
    "kernel_entrypoint_id",
    "maximum_adapter_calls",
    "maximum_field_steps",
    "single_use",
    "non_exportable",
    "expires_after_success_or_failure",
    "capability_attestation_digest",
)
S1_HG_REQUIRED_HOST_OPERATIONS = (
    "authenticate-owner-event-and-verify-message-session-order-and-nonce",
    "issue-nonexportable-capability-bound-to-exact-authorization-and-target",
    "consume-capability-inside-host-owned-kernel-boundary",
    "perform-exactly-one-production-kernel-call-and-one-field-step",
    "return-attested-complete-result-or-no-result-and-expire-capability",
)
S1_HG_REJECTION_RULES = (
    "local-callable-cannot-substitute-host-origin-verifier",
    "assistant-or-research-module-text-cannot-attest-owner-origin",
    "plain-python-object-cannot-prove-host-capability-ownership",
    "missing-mismatched-or-replayed-host-event-fails-closed",
    "capability-without-exact-event-and-authorization-binding-fails-closed",
    "exportable-copyable-or-reusable-capability-fails-closed",
    "production-kernel-outside-host-owned-capability-boundary-fails-closed",
    "partial-result-retry-reparametrization-persistence-and-claims-forbidden",
)
S1_HG_CHECK_NAMES = (
    "source-preflight-has-exactly-two-production-blockers",
    "host-event-schema-covers-existing-s1hb-event-fields",
    "capability-binds-event-authorization-session-target-and-kernel",
    "event-authentication-precedes-capability-issuance",
    "capability-consumption-immediately-precedes-production-kernel-call",
    "complete-attested-return-follows-the-single-kernel-call",
    "single-call-single-step-and-expiration-are-required",
    "local-verifier-and-local-capability-fallbacks-are-rejected",
    "external-provider-and-production-path-are-currently-absent",
    "requirements-audit-calls-no-bridge-token-adapter-kernel-or-writer",
)


def _called_names(subject: object) -> frozenset[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(inspect.getsource(subject))):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return frozenset(names)


@dataclass(frozen=True, slots=True)
class E1FormationS1HGHostIntegrationRequirements:
    contract_id: str
    source_s1hf_preflight_digest: str
    target_digest: str
    required_external_event_fields: tuple[str, ...]
    required_host_capability_fields: tuple[str, ...]
    required_host_operations: tuple[str, ...]
    rejection_rules: tuple[str, ...]
    checks: tuple[tuple[str, bool], ...]
    maximum_adapter_calls: int
    maximum_field_steps: int
    external_host_provider_present: bool
    authenticated_origin_verifier_connected: bool
    host_capability_factory_connected: bool
    production_kernel_boundary_connected: bool
    host_capability_issued: bool
    authorization_request_ready: bool
    execution_permitted: bool
    adapter_calls: int
    field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
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
            self.contract_id != S1_HG_CONTRACT_ID
            or len(self.source_s1hf_preflight_digest) != 64
            or len(self.target_digest) != 64
            or self.required_external_event_fields
            != S1_HG_REQUIRED_EXTERNAL_EVENT_FIELDS
            or self.required_host_capability_fields
            != S1_HG_REQUIRED_HOST_CAPABILITY_FIELDS
            or self.required_host_operations != S1_HG_REQUIRED_HOST_OPERATIONS
            or self.rejection_rules != S1_HG_REJECTION_RULES
            or tuple(name for name, _ in self.checks) != S1_HG_CHECK_NAMES
            or any(value is not True for _, value in self.checks)
            or self.maximum_adapter_calls != 1
            or self.maximum_field_steps != 1
            or any(
                value is not False
                for value in (
                    self.external_host_provider_present,
                    self.authenticated_origin_verifier_connected,
                    self.host_capability_factory_connected,
                    self.production_kernel_boundary_connected,
                    self.host_capability_issued,
                    self.authorization_request_ready,
                    self.execution_permitted,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.adapter_calls != 0
            or self.field_steps_executed != 0
            or self.decision
            != "HOST_INTEGRATION_REQUIREMENTS_BOUND_EXTERNAL_PROVIDER_ABSENT"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1HGHostIntegrationRequirementsError(
                "S1-HG inferred host trust or opened production execution"
            )


def audit_e1_formation_s1hg_host_integration_requirements(
    preflight: E1FormationS1HFFiveComponentTotalPreflight,
) -> E1FormationS1HGHostIntegrationRequirements:
    """Bind the external handoff requirements without implementing the host."""

    if not isinstance(preflight, E1FormationS1HFFiveComponentTotalPreflight):
        raise E1FormationS1HGHostIntegrationRequirementsError(
            "S1-HG requires the exact S1-HF total preflight"
        )
    preflight.__post_init__()
    event_fields = E1FormationS1HBExternalOwnerOriginEvent.__dataclass_fields__
    operations = S1_HG_REQUIRED_HOST_OPERATIONS
    capability_fields = set(S1_HG_REQUIRED_HOST_CAPABILITY_FIELDS)
    called = _called_names(
        audit_e1_formation_s1hg_host_integration_requirements
    )
    forbidden_calls = {
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
            S1_HG_CHECK_NAMES[0],
            preflight.production_blockers == S1_HF_PRODUCTION_BLOCKERS
            and len(preflight.production_blockers) == 2
            and preflight.production_implementation_complete is False,
        ),
        (
            S1_HG_CHECK_NAMES[1],
            set(S1_HG_REQUIRED_EXTERNAL_EVENT_FIELDS).issubset(event_fields),
        ),
        (
            S1_HG_CHECK_NAMES[2],
            {
                "source_external_event_digest",
                "authorization_digest",
                "task_or_session_binding_digest",
                "run_id",
                "gate_digest",
                "binding_digest",
                "batch_index",
                "carrier_digest",
                "kernel_entrypoint_id",
            }.issubset(capability_fields),
        ),
        (
            S1_HG_CHECK_NAMES[3],
            operations.index(
                "authenticate-owner-event-and-verify-message-session-order-and-nonce"
            )
            < operations.index(
                "issue-nonexportable-capability-bound-to-exact-authorization-and-target"
            ),
        ),
        (
            S1_HG_CHECK_NAMES[4],
            operations.index(
                "consume-capability-inside-host-owned-kernel-boundary"
            )
            + 1
            == operations.index(
                "perform-exactly-one-production-kernel-call-and-one-field-step"
            ),
        ),
        (
            S1_HG_CHECK_NAMES[5],
            operations.index(
                "perform-exactly-one-production-kernel-call-and-one-field-step"
            )
            < operations.index(
                "return-attested-complete-result-or-no-result-and-expire-capability"
            ),
        ),
        (
            S1_HG_CHECK_NAMES[6],
            {
                "maximum_adapter_calls",
                "maximum_field_steps",
                "single_use",
                "expires_after_success_or_failure",
            }.issubset(capability_fields),
        ),
        (
            S1_HG_CHECK_NAMES[7],
            {
                "local-callable-cannot-substitute-host-origin-verifier",
                "plain-python-object-cannot-prove-host-capability-ownership",
            }.issubset(S1_HG_REJECTION_RULES),
        ),
        (
            S1_HG_CHECK_NAMES[8],
            preflight.productive_host_verifier_connected is False
            and preflight.productive_kernel_adapter_connected is False
            and preflight.execution_permitted is False,
        ),
        (S1_HG_CHECK_NAMES[9], called.isdisjoint(forbidden_calls)),
    )
    values = {
        "contract_id": S1_HG_CONTRACT_ID,
        "source_s1hf_preflight_digest": preflight.preflight_digest,
        "target_digest": preflight.target_digest,
        "required_external_event_fields": S1_HG_REQUIRED_EXTERNAL_EVENT_FIELDS,
        "required_host_capability_fields": (
            S1_HG_REQUIRED_HOST_CAPABILITY_FIELDS
        ),
        "required_host_operations": S1_HG_REQUIRED_HOST_OPERATIONS,
        "rejection_rules": S1_HG_REJECTION_RULES,
        "checks": checks,
        "maximum_adapter_calls": 1,
        "maximum_field_steps": 1,
        "external_host_provider_present": False,
        "authenticated_origin_verifier_connected": False,
        "host_capability_factory_connected": False,
        "production_kernel_boundary_connected": False,
        "host_capability_issued": False,
        "authorization_request_ready": False,
        "execution_permitted": False,
        "adapter_calls": 0,
        "field_steps_executed": 0,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "HOST_INTEGRATION_REQUIREMENTS_BOUND_EXTERNAL_PROVIDER_ABSENT"
        ),
        "reason": (
            "the-research-repository-now-defines-the-exact-host-event-and-"
            "nonexportable-capability-handoff-but-cannot-create-or-attest-"
            "either;an-external-orchestrator-host-provider-is-required-before-"
            "any-production-authorization-or-kernel-call"
        ),
    }
    return E1FormationS1HGHostIntegrationRequirements(
        **values,
        contract_digest=_digest(values),
    )
