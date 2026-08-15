"""Static S1-JS readiness precheck for private adapter payload schemas."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from .dynamic_substrate_s1jn_finite_materialization_schema_contract import (
    build_dts1_s1jn_finite_materialization_schema_contract,
)
from .dynamic_substrate_s1jp_baseline_adapter_bridge_contract import (
    build_dts1_s1jp_baseline_adapter_bridge_contract,
)
from .dynamic_substrate_s1jr_corrected_role_refinement_contract import (
    build_dts1_s1jr_corrected_role_refinement_contract,
)


class DTS1S1JSAdapterPayloadReadinessPrecheckError(ValueError):
    """Raised when the S1-JS payload readiness stop is weakened."""


S1_JS_AUDIT_ID = "dynamic-substrate.adapter-payload-readiness.s1js.v1"
S1_JS_SOURCE_S1JR_DIGEST = (
    "1314e59ef30722c04cf992a88a25c94dd8aedb930dba6c94c20c1fca71f6c2b8"
)
S1_JS_SOURCE_S1JP_DIGEST = (
    "2852c8215dc9cc6e20d7de5865e50f9d6badc65ed7df99e37779e281960faa7b"
)
S1_JS_SOURCE_S1JN_DIGEST = (
    "b0edec20c6d27d98ba8a523c3034d8890b01cfe514eede1d72d05c2e548dd281"
)
S1_JS_SOURCE_S1JA_DIGEST = (
    "331168f2a6f937b454742d2be57de3f022f75ca5ca521fbff31f101bd4ea1fbc"
)
S1_JS_BOUND_BUT_INSUFFICIENT = (
    "S1-JN-binds-private-state-key-names-but-allows-generic-canonical-values-without-role-payload-shapes",
    "S1-JA-binds-numeric-configuration-records-and-digests-but-not-all-runtime-object-construction-identities",
    "S1-JP-binds-behavioral-bridges-state-return-and-one-generic-diagnostic-output-role",
    "S1-JR-binds-exact-versus-native-control-semantics-without-adding-private-payload-shapes",
)
S1_JS_ROLE_GAP_RECORDS = (
    (
        "B1",
        "fixed_adapter_payload",
        "DTS1BackreactionResult",
        (
            "exact-payload-keys-and-schema-id",
            "canonical-edge-endpoint-and-rate-record-shape",
            "base-rate-backreaction-flag-and-edge-inventory-digest-binding",
            "payload-to-typed-result-reconstruction-and-roundtrip-identity",
        ),
        "BLOCKED_PRIVATE_FIXED_ADAPTER_PAYLOAD_UNBOUND",
    ),
    (
        "B2",
        "complete_L_state_payload",
        "S2ReferenceState.development",
        (
            "exact-payload-keys-and-schema-id",
            "node-id-to-L-value-association-and-canonical-order",
            "finite-domain-shape-and-geometry-validation",
            "S2-output-to-SharedMCMField-tick-perception-time-and-private-L-commit-protocol",
        ),
        "BLOCKED_PRIVATE_L_AND_FIELD_COMMIT_SCHEMA_UNBOUND",
    ),
    (
        "B3",
        "embedded_M_state_digest-plus-B3_configuration_digest",
        "MCMF3-runtime-local-leaky-context",
        (
            "exact-runtime-config-object-construction-record",
            "embedded-arm-identity-to-S1-JA-configuration-roundtrip",
        ),
        "BLOCKED_RUNTIME_CONTEXT_RECORD_UNBOUND",
    ),
    (
        "B4",
        "embedded_M_state_digest-plus-B4_configuration_digest",
        "MCMF3-runtime-linear-coupled-context",
        (
            "exact-runtime-config-object-construction-record",
            "embedded-arm-identity-to-S1-JA-configuration-roundtrip",
        ),
        "BLOCKED_RUNTIME_CONTEXT_RECORD_UNBOUND",
    ),
    (
        "B5",
        "embedded_M_state_digest-plus-B5_configuration_digest",
        "MCMF3-runtime-default-context",
        (
            "exact-runtime-config-object-construction-record",
            "embedded-arm-identity-to-S1-JA-configuration-roundtrip",
        ),
        "BLOCKED_RUNTIME_CONTEXT_RECORD_UNBOUND",
    ),
    (
        "B6",
        "embedded_M_state_digest-plus-frozen_CONST_V_spec_digest-plus-B6_configuration_digest",
        "W7MBaselineSpec-plus-MCMF3-runtime-context",
        (
            "exact-frozen-spec-payload-and-schema-id",
            "spec-digest-algorithm-and-payload-roundtrip",
            "exact-runtime-config-object-construction-record",
            "embedded-arm-and-frozen-spec-to-S1-JA-configuration-roundtrip",
        ),
        "BLOCKED_CONST_V_SPEC_AND_RUNTIME_CONTEXT_UNBOUND",
    ),
)
S1_JS_COMMON_OUTPUT_GAPS = (
    "no-finite-role-specific-diagnostic-record-schema-is-bound-for-B1-B2-or-the-F3-runtime-result",
    "no-canonical-payload-schema-is-bound-for-the-complete-adapter-output-field-private-state-and-diagnostics",
    "no-output-digest-schema-id-number-canonicalization-or-roundtrip-validator-is-bound",
    "no-single-publication-error-type-and-wrapped-kernel-error-inventory-is-bound",
    "no-exact-private-context-and-output-record-dataclass-field-order-is-bound",
)
S1_JS_FORBIDDEN_IMPLEMENTATION_CHOICES = (
    "invent-payload-keys-schema-identities-node-order-or-default-values-in-adapter-code",
    "accept-arbitrary-mappings-and-infer-a-typed-object-from-present-keys",
    "serialize-dataclass-repr-pickle-object-identity-or-platform-dependent-numpy-bytes",
    "drop-B2-L-reconstruct-it-from-S-H-or-hide-it-in-a-closure-cache-or-global",
    "rebuild-B6-spec-from-an-unbound-source-or-accept-digest-only-without-payload-validation",
    "publish-field-state-diagnostics-or-digest-before-every-output-component-validates",
)
S1_JS_REQUIRED_BINDING = (
    "bind-one-versioned-finite-private-payload-schema-for-each-of-B1-through-B6",
    "bind-exact-value-to-runtime-object-and-runtime-object-to-value-roundtrips",
    "bind-B2-full-field-commit-and-private-L-return-without-new-dynamics",
    "bind-one-finite-role-specific-diagnostic-union-and-canonical-output-payload",
    "bind-one-output-digest-algorithm-validation-order-error-boundary-and-technical-test-matrix",
    "retain-S1-JP-information-barriers-S1-JR-control-semantics-and-zero-model-execution",
)
S1_JS_PRESERVED_BINDINGS = (
    "all-S1-JO-materializer-fixtures-identities-and-four-integrity-roles",
    "all-S1-JA-configuration-values-digests-refinement-labels-and-twenty-four-case-identities",
    "all-S1-JP-role-kernel-information-state-return-neutral-and-atomicity-rules",
    "all-S1-JR-exact-and-native-control-semantics",
    "all-existing-baseline-kernels-equations-and-runtime-objects-remain-unchanged",
)
S1_JS_DECISION = (
    "STOPP_PRIVATE_BASELINE_ADAPTER_IMPLEMENTATION_FINITE_PAYLOAD_AND_OUTPUT_SCHEMAS_MISSING"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JSAdapterPayloadReadinessPrecheck:
    audit_id: str
    source_s1jr_digest: str
    source_s1jp_digest: str
    source_s1jn_digest: str
    source_s1ja_digest: str
    bound_but_insufficient: tuple[str, ...]
    role_gap_records: tuple[tuple[str, str, str, tuple[str, ...], str], ...]
    common_output_gaps: tuple[str, ...]
    forbidden_implementation_choices: tuple[str, ...]
    required_binding: tuple[str, ...]
    preserved_bindings: tuple[str, ...]
    baseline_role_count: int
    role_payload_schema_count: int
    roles_blocked_count: int
    all_twenty_four_cases_blocked_atomically: bool
    adapter_implementation_ready: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    finite_payload_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_JS_AUDIT_ID
            or self.source_s1jr_digest != S1_JS_SOURCE_S1JR_DIGEST
            or self.source_s1jp_digest != S1_JS_SOURCE_S1JP_DIGEST
            or self.source_s1jn_digest != S1_JS_SOURCE_S1JN_DIGEST
            or self.source_s1ja_digest != S1_JS_SOURCE_S1JA_DIGEST
            or self.bound_but_insufficient != S1_JS_BOUND_BUT_INSUFFICIENT
            or self.role_gap_records != S1_JS_ROLE_GAP_RECORDS
            or self.common_output_gaps != S1_JS_COMMON_OUTPUT_GAPS
            or self.forbidden_implementation_choices
            != S1_JS_FORBIDDEN_IMPLEMENTATION_CHOICES
            or self.required_binding != S1_JS_REQUIRED_BINDING
            or self.preserved_bindings != S1_JS_PRESERVED_BINDINGS
            or self.baseline_role_count != 6
            or self.role_payload_schema_count != 0
            or self.roles_blocked_count != 6
            or self.all_twenty_four_cases_blocked_atomically is not True
            or self.adapter_implementation_ready is not False
            or self.adapters_implemented is not False
            or self.baseline_models_executed is not False
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.finite_payload_contract_authorized_next_stage is not True
            or self.decision != S1_JS_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1JSAdapterPayloadReadinessPrecheckError(
                "S1-JS weakened the adapter payload readiness stop"
            )


def build_dts1_s1js_adapter_payload_readiness_precheck(
) -> DTS1S1JSAdapterPayloadReadinessPrecheck:
    """Audit finite adapter schemas without constructing or running adapters."""

    refinement_source = build_dts1_s1jr_corrected_role_refinement_contract()
    bridge_source = build_dts1_s1jp_baseline_adapter_bridge_contract()
    materialization_source = build_dts1_s1jn_finite_materialization_schema_contract()
    configuration_source = build_dts1_s1ja_finite_configuration_matrix_contract()
    values = {
        "audit_id": S1_JS_AUDIT_ID,
        "source_s1jr_digest": refinement_source.contract_digest,
        "source_s1jp_digest": bridge_source.contract_digest,
        "source_s1jn_digest": materialization_source.contract_digest,
        "source_s1ja_digest": configuration_source.contract_digest,
        "bound_but_insufficient": S1_JS_BOUND_BUT_INSUFFICIENT,
        "role_gap_records": S1_JS_ROLE_GAP_RECORDS,
        "common_output_gaps": S1_JS_COMMON_OUTPUT_GAPS,
        "forbidden_implementation_choices": S1_JS_FORBIDDEN_IMPLEMENTATION_CHOICES,
        "required_binding": S1_JS_REQUIRED_BINDING,
        "preserved_bindings": S1_JS_PRESERVED_BINDINGS,
        "baseline_role_count": len(S1_JS_ROLE_GAP_RECORDS),
        "role_payload_schema_count": 0,
        "roles_blocked_count": len(S1_JS_ROLE_GAP_RECORDS),
        "all_twenty_four_cases_blocked_atomically": True,
        "adapter_implementation_ready": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "finite_payload_contract_authorized_next_stage": True,
        "decision": S1_JS_DECISION,
    }
    return DTS1S1JSAdapterPayloadReadinessPrecheck(
        **values, audit_digest=_digest(values)
    )
