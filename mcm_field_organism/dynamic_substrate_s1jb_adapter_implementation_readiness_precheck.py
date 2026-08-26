"""Static S1-JB precheck before private baseline adapter implementation."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)


class DTS1S1JBAdapterImplementationReadinessPrecheckError(ValueError):
    """Raised when the fail-closed S1-JB precheck is weakened."""


S1_JB_AUDIT_ID = "dynamic-substrate.adapter-implementation-readiness.s1jb.v1"
S1_JB_SOURCE_S1JA_DIGEST = (
    "331168f2a6f937b454742d2be57de3f022f75ca5ca521fbff31f101bd4ea1fbc"
)
S1_JB_SURFACE_RECORDS = (
    (
        "COMMON_INTERVAL_ENVELOPE",
        "MCMFieldStepTime-ReceptorDistribution-SH-boundary-and-checkpoint-semantics-exist-only-as-separate-surfaces",
        "BLOCKED_NO_SINGLE_AUTHORITATIVE_MODEL_NEUTRAL_VALUE_OBJECT",
    ),
    (
        "P_IE_CAUSAL_TWO_SUBSTEP",
        "existing-audit-private-builders-create-time-distribution-and-checkpoints-inside-the-candidate-harness",
        "BLOCKED_CONTROLLED_COMMON_ENVELOPE_NOT_REGISTERED",
    ),
    (
        "P_IH_ATTENUATION",
        "existing-audit-private-builders-create-time-distribution-and-checkpoints-inside-the-candidate-harness",
        "BLOCKED_CONTROLLED_COMMON_ENVELOPE_NOT_REGISTERED",
    ),
    (
        "P_IK_INTERFERENCE",
        "S1-IX-schedule-and-S1-IZ-boundary-operator-lack-one-bound-distribution-time-and-checkpoint-envelope",
        "BLOCKED_EXECUTABLE_COMMON_ENVELOPE_NOT_REGISTERED",
    ),
    (
        "P_IN_RELEASE_REUSE",
        "S1-IX-schedule-and-S1-IZ-boundary-operator-lack-one-bound-distribution-time-and-checkpoint-envelope",
        "BLOCKED_EXECUTABLE_COMMON_ENVELOPE_NOT_REGISTERED",
    ),
)
S1_JB_BLOCKING_FACTS = (
    "S1-IT-defines-the-common-adapter-input-schema-in-prose-but-no-concrete-immutable-Python-value-type",
    "S1-IZ-applies-one-S-H-boundary-but-does-not-bind-one-interval-time-distribution-order-or-checkpoint",
    "S1-JA-binds-configuration-and-case-identities-but-not-the-complete-per-event-adapter-input-values",
    "existing-P_IE-and-P_IH-builders-are-private-to-candidate-audits-and-not-a-common-adapter-input-source",
    "old-P_IK-and-P_IN-audit-builders-encode-the-quarantined-resource-first-history-and-cannot-be-reused",
    "six-independent-adapter-schedule-builders-could-merge-split-delay-repeat-or-relabel-the-common-exposure",
)
S1_JB_REQUIRED_NEXT_CONTRACT = (
    "one-private-immutable-model-neutral-interval-envelope-type",
    "canonical-geometry-and-complete-S-H-prestate-or-explicit-S1-IZ-boundary-role",
    "one-complete-receptor-contact-vector-and-one-positive-MCMFieldStepTime",
    "ordered-interval-position-and-output-checkpoint-boolean-without-arm-case-target-or-result-data",
    "one-canonical-envelope-digest-and-sequence-digest-created-before-any-baseline-role-is-selected",
    "P_IE-P_IH-P_IK-P_IN-sequences-built-once-then-delivered-value-identically-to-DTS1-and-B1-through-B6",
    "fail-closed-rejection-of-merge-split-delay-replay-lookahead-or-profile-dependent-reconstruction",
)
S1_JB_PRESERVED_BINDINGS = (
    "all-seven-S1-JA-configuration-values-and-digests-remain-bound",
    "all-seven-common-refinement-records-remain-bound",
    "all-twenty-four-case-identities-remain-bound-but-blocked",
    "S1-IX-S1-IY-S1-IZ-boundary-semantics-values-and-operator-remain-valid",
    "old-P_IK-P_IN-field-vector-quarantine-and-direct-ledger-retention-remain-valid",
)
S1_JB_FORBIDDEN_INTERPRETATIONS = (
    "kernel-incompatibility-invalid-configuration-baseline-rejection-or-candidate-superiority",
    "permission-to-reuse-audit-private-or-quarantined-schedules-as-common-input",
    "memory-learning-or-artificial-intelligence",
)
S1_JB_DECISION = "STOPP_PRIVATE_BASELINE_ADAPTER_IMPLEMENTATION_COMMON_INTERVAL_ENVELOPE_UNBOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JBAdapterImplementationReadinessPrecheck:
    audit_id: str
    source_s1ja_digest: str
    surface_records: tuple[tuple[str, str, str], ...]
    blocking_facts: tuple[str, ...]
    required_next_contract: tuple[str, ...]
    preserved_bindings: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    planned_adapter_case_count: int
    ready_adapter_case_count: int
    blocked_adapter_case_count: int
    common_interval_envelope_bound: bool
    configuration_binding_preserved: bool
    case_matrix_binding_preserved: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    common_interval_envelope_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_JB_AUDIT_ID
            or self.source_s1ja_digest != S1_JB_SOURCE_S1JA_DIGEST
            or self.surface_records != S1_JB_SURFACE_RECORDS
            or self.blocking_facts != S1_JB_BLOCKING_FACTS
            or self.required_next_contract != S1_JB_REQUIRED_NEXT_CONTRACT
            or self.preserved_bindings != S1_JB_PRESERVED_BINDINGS
            or self.forbidden_interpretations != S1_JB_FORBIDDEN_INTERPRETATIONS
            or self.planned_adapter_case_count != 24
            or self.ready_adapter_case_count != 0
            or self.blocked_adapter_case_count != 24
            or self.common_interval_envelope_bound is not False
            or self.configuration_binding_preserved is not True
            or self.case_matrix_binding_preserved is not True
            or any(
                value is not False
                for value in (
                    self.adapters_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.common_interval_envelope_contract_authorized_next_stage is not True
            or self.decision != S1_JB_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1JBAdapterImplementationReadinessPrecheckError(
                "S1-JB weakened the common interval envelope STOPP"
            )


def build_dts1_s1jb_adapter_implementation_readiness_precheck() -> DTS1S1JBAdapterImplementationReadinessPrecheck:
    """Stop adapter implementation before six schedule reconstructions diverge."""

    source = build_dts1_s1ja_finite_configuration_matrix_contract()
    values = {
        "audit_id": S1_JB_AUDIT_ID,
        "source_s1ja_digest": source.contract_digest,
        "surface_records": S1_JB_SURFACE_RECORDS,
        "blocking_facts": S1_JB_BLOCKING_FACTS,
        "required_next_contract": S1_JB_REQUIRED_NEXT_CONTRACT,
        "preserved_bindings": S1_JB_PRESERVED_BINDINGS,
        "forbidden_interpretations": S1_JB_FORBIDDEN_INTERPRETATIONS,
        "planned_adapter_case_count": source.baseline_case_count,
        "ready_adapter_case_count": 0,
        "blocked_adapter_case_count": source.baseline_case_count,
        "common_interval_envelope_bound": False,
        "configuration_binding_preserved": True,
        "case_matrix_binding_preserved": True,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "common_interval_envelope_contract_authorized_next_stage": True,
        "decision": S1_JB_DECISION,
    }
    return DTS1S1JBAdapterImplementationReadinessPrecheck(
        **values, audit_digest=_digest(values)
    )
