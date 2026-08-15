"""Static S1-JY readiness precheck for one-replica orchestration."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    build_dts1_s1jx_sequence_carry_orchestration_contract,
)


class DTS1S1JYOrchestratorAPIReadinessPrecheckError(ValueError):
    """Raised when the S1-JY implementation stop is weakened."""


S1_JY_AUDIT_ID = "dynamic-substrate.orchestrator-api-readiness.s1jy.v1"
S1_JY_SOURCE_S1JX_DIGEST = (
    "4bbf3bfb4997fe7e5ad3364276f127d6a8eb53c6b2452c0b4cac387e097cb5a8"
)
S1_JY_CONFIRMED_READY_BINDINGS = (
    "six-short-and-long-baseline-role-identities",
    "four-profile-blocks-seven-sequences-and-twenty-three-corrected-envelopes",
    "three-independent-refinement-levels-and-seventy-two-replica-identities",
    "field-private-state-envelope-digest-and-output-digest-forward-carry-rules",
    "eleven-checkpoint-ordinals-per-role-refinement",
    "eight-eight-six-six-corrected-component-cardinalities",
    "replica-case-and-matrix-atomicity-and-all-cross-replica-carry-exclusions",
    "six-technically-accepted-private-S1-JW-adapter-bridges",
)
S1_JY_BLOCKING_GAPS = (
    (
        "orchestrator_input_api",
        "no-versioned-function-or-immutable-input-record-binds-replica-identity-and-allowed-arguments",
    ),
    (
        "fresh_sequence_state_payloads",
        "no-canonical-complete-field-and-private-state-payload-or-digest-is-bound-for-each-role-and-geometry",
    ),
    (
        "initializer_validation",
        "no-exact-rule-binds-B1-profile-fixed-payload-B2-zero-L-and-B3-through-B6-uniform-M-to-one-fresh-sequence-record",
    ),
    (
        "checkpoint_record_schema",
        "no-versioned-key-order-binds-sequence-ordinal-complete-S-H-private-state-and-integrity-digests",
    ),
    (
        "signed_component_index",
        "component-count-and-sign-descriptions-do-not-bind-one-exact-sequence-checkpoint-channel-node-index-order",
    ),
    (
        "replica_output_schema",
        "no-versioned-atomic-output-binds-checkpoints-components-diagnostics-and-canonical-output-digest",
    ),
    (
        "error_boundary",
        "no-single-public-error-family-wrapped-exception-set-and-no-partial-output-rule-is-bound-at-the-runner-API",
    ),
    (
        "technical_exemplar",
        "no-one-exact-replica-id-test-budget-and-allowed-kernel-call-count-is-selected-for-S1-JY-acceptance",
    ),
)
S1_JY_IMPLEMENTATION_RISKS = (
    "choosing-S-versus-H-node-and-checkpoint-order-in-code-would-change-the-later-signed-profile-vector",
    "constructing-fresh-fields-or-private-state-ad-hoc-could-introduce-role-or-profile-dependent-hidden-inputs",
    "accepting-caller-owned-initializers-without-a-finite-schema-could-break-sequence-and-refinement-independence",
    "publishing-an-unbound-checkpoint-or-output-shape-could-make-partial-results-look-like-valid-cases",
    "testing-an-unselected-replica-set-could-cross-the-authorized-one-replica-technical-scope",
)
S1_JY_PRESERVED_BINDINGS = (
    "all-S1-JX-sequence-replica-case-carry-checkpoint-cardinality-and-atomicity-records",
    "all-S1-JW-adapter-context-output-digest-and-fail-closed-behavior",
    "all-S1-JO-materializer-identities-provenance-and-information-barriers",
    "all-S1-JR-exact-versus-native-refinement-rules",
    "all-S1-IR-corrected-profile-signs-and-eight-eight-six-six-cardinalities",
)
S1_JY_REQUIRED_CORRECTION = (
    "bind-one-versioned-one-replica-runner-input-schema-with-no-profile-result-or-candidate-data",
    "bind-finite-fresh-field-and-private-state-payloads-and-digests-for-six-roles-and-two-geometries",
    "bind-one-versioned-checkpoint-record-and-one-versioned-complete-replica-output",
    "bind-all-component-indices-as-sequence-key-checkpoint-ordinal-channel-node-id-and-sign-tuples",
    "bind-canonical-digest-rules-and-one-atomic-runner-error-boundary",
    "select-exactly-one-technical-exemplar-replica-and-a-finite-call-budget",
)
S1_JY_DECISION = (
    "STOPP_ONE_REPLICA_ORCHESTRATOR_FINITE_API_INITIALIZERS_AND_OUTPUT_SCHEMAS_MISSING"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JYOrchestratorAPIReadinessPrecheck:
    audit_id: str
    source_s1jx_digest: str
    confirmed_ready_bindings: tuple[str, ...]
    blocking_gaps: tuple[tuple[str, str], ...]
    implementation_risks: tuple[str, ...]
    preserved_bindings: tuple[str, ...]
    required_correction: tuple[str, ...]
    blocking_gap_count: int
    sequence_carry_contract_valid: bool
    finite_runner_api_ready: bool
    orchestrator_implemented: bool
    technical_replicas_executed: int
    profile_cases_executed: int
    baseline_interval_calls_executed: int
    runtime_integration_present: bool
    research_execution_permitted: bool
    research_field_steps_executed: int
    finite_orchestrator_api_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_JY_AUDIT_ID
            or self.source_s1jx_digest != S1_JY_SOURCE_S1JX_DIGEST
            or self.confirmed_ready_bindings != S1_JY_CONFIRMED_READY_BINDINGS
            or self.blocking_gaps != S1_JY_BLOCKING_GAPS
            or self.implementation_risks != S1_JY_IMPLEMENTATION_RISKS
            or self.preserved_bindings != S1_JY_PRESERVED_BINDINGS
            or self.required_correction != S1_JY_REQUIRED_CORRECTION
            or self.blocking_gap_count != 8
            or self.sequence_carry_contract_valid is not True
            or self.finite_runner_api_ready is not False
            or self.orchestrator_implemented is not False
            or self.technical_replicas_executed != 0
            or self.profile_cases_executed != 0
            or self.baseline_interval_calls_executed != 0
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.research_field_steps_executed != 0
            or self.finite_orchestrator_api_contract_authorized_next_stage is not True
            or self.decision != S1_JY_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1JYOrchestratorAPIReadinessPrecheckError(
                "S1-JY weakened the orchestrator API readiness stop"
            )


def build_dts1_s1jy_orchestrator_api_readiness_precheck(
) -> DTS1S1JYOrchestratorAPIReadinessPrecheck:
    """Audit API readiness without materializing or executing a replica."""

    source = build_dts1_s1jx_sequence_carry_orchestration_contract()
    values = {
        "audit_id": S1_JY_AUDIT_ID,
        "source_s1jx_digest": source.contract_digest,
        "confirmed_ready_bindings": S1_JY_CONFIRMED_READY_BINDINGS,
        "blocking_gaps": S1_JY_BLOCKING_GAPS,
        "implementation_risks": S1_JY_IMPLEMENTATION_RISKS,
        "preserved_bindings": S1_JY_PRESERVED_BINDINGS,
        "required_correction": S1_JY_REQUIRED_CORRECTION,
        "blocking_gap_count": len(S1_JY_BLOCKING_GAPS),
        "sequence_carry_contract_valid": True,
        "finite_runner_api_ready": False,
        "orchestrator_implemented": False,
        "technical_replicas_executed": 0,
        "profile_cases_executed": 0,
        "baseline_interval_calls_executed": 0,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "research_field_steps_executed": 0,
        "finite_orchestrator_api_contract_authorized_next_stage": True,
        "decision": S1_JY_DECISION,
    }
    return DTS1S1JYOrchestratorAPIReadinessPrecheck(
        **values, audit_digest=_digest(values)
    )
