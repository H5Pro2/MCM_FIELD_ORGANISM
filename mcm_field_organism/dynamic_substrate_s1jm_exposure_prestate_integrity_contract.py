"""Static S1-JM separation of exposure and private prestate integrity."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)
from .dynamic_substrate_s1jl_model_view_equivalence_precheck import (
    build_dts1_s1jl_model_view_equivalence_precheck,
)


class DTS1S1JMExposurePrestateIntegrityContractError(ValueError):
    """Raised when the separated S1-JM integrity boundary is weakened."""


S1_JM_CONTRACT_ID = "dynamic-substrate.exposure-prestate-integrity.s1jm.v1"
S1_JM_SOURCE_S1JL_DIGEST = (
    "2c0876d32b87fed1d76c3dace55708708ff4426728d7fc2d9d7a7871a228038c"
)
S1_JM_SOURCE_S1JK_DIGEST = (
    "64ca5b895146fef453eb27945a1074f5d2b8e4c8834a94cc6f9b0a855a61824f"
)
S1_JM_COMMON_EXPOSURE_PAYLOAD_SCHEMA = (
    ("schema_id", "mcm.s1jm.common-exposure.v1"),
    ("geometry_digest", "canonical-common-open-line-geometry-digest"),
    ("prestate_operation", "initial-S-H-values-or-boundary-S-H-values-or-carry-current-S-H-marker"),
    ("receptor_distribution_payload", "complete-value-only-distribution-without-profile-arm-case-or-target-labels"),
    ("step_time_payload", "clock-id-start-tick-end-tick-and-ticks-per-synthetic-time-unit"),
)
S1_JM_PRIVATE_PRESTATE_PAYLOAD_SCHEMA = (
    ("schema_id", "mcm.s1jm.private-prestate.v1"),
    ("model_role", "one-orchestrator-only-DTS1-or-B1-through-B6-role"),
    ("complete_field_payload", "value-only-field-layer-docks-last-distribution-and-optional-L-or-M-state"),
    ("private_state_payload", "role-specific-anatomy-fixed-adapter-L-M-or-frozen-spec-provenance"),
    ("prior_envelope_digest", "null-at-ordinal-one-otherwise-the-exact-prior-corrected-S1-JK-envelope-digest"),
    ("prior_output_digest", "null-at-ordinal-one-otherwise-the-recorded-complete-prior-model-output-digest"),
)
S1_JM_MATERIALIZED_INPUT_PAYLOAD_SCHEMA = (
    ("schema_id", "mcm.s1jm.materialized-model-input.v1"),
    ("materialized_field_payload", "complete-value-only-field-after-the-registered-prestate-operation"),
    ("receptor_distribution_payload", "the-same-complete-distribution-used-in-common-exposure"),
    ("step_time_payload", "the-same-complete-step-time-used-in-common-exposure"),
    ("geometry_digest", "the-same-common-geometry-digest"),
)
S1_JM_ORCHESTRATION_CONTROL_SCHEMA = (
    ("sequence_digest", "exact-corrected-S1-JK-sequence-digest"),
    ("ordinal", "exact-positive-contiguous-sequence-ordinal"),
    ("interval_digest", "exact-corrected-S1-JK-envelope-digest"),
    ("checkpoint_after_interval", "exact-orchestrator-only-boolean"),
    ("candidate_sidecar_digest", "DTS1-only-when-registered-otherwise-null"),
)
S1_JM_DIGEST_ROLES = (
    (
        "common_exposure_digest",
        "SHA-256-of-common-exposure-payload",
        "orchestrator-only-cross-model-equality-gate-before-any-model-call",
    ),
    (
        "private_prestate_digest",
        "SHA-256-of-private-prestate-payload",
        "orchestrator-only-per-model-provenance-never-a-cross-model-equality-gate",
    ),
    (
        "materialized_input_digest",
        "SHA-256-of-materialized-input-payload",
        "wrapper-only-integrity-check-never-a-model-kernel-or-calculator-argument",
    ),
    (
        "orchestration_control_digest",
        "SHA-256-of-orchestration-control-payload",
        "orchestrator-only-order-checkpoint-and-sidecar-control-never-a-model-argument",
    ),
)
S1_JM_MODEL_INVOCATION_FIELDS = (
    "materialized_field",
    "receptor_distribution",
    "step_time",
    "geometry_digest",
)
S1_JM_MODEL_INVOCATION_EXCLUSIONS = (
    "all-four-integrity-digests-and-their-canonical-payloads",
    "sequence-ordinal-profile-arm-case-boundary-checkpoint-target-or-result-labels",
    "another-models-field-private-state-output-or-provenance",
    "candidate-sidecar-for-B1-through-B6-reference-output-future-state-fit-residual-or-threshold",
)
S1_JM_CROSS_MODEL_EQUIVALENCE_MATRIX = (
    ("P_IE_F_HIGH_vs_R_HIGH", (1, 2), "COMMON_EXPOSURE_EQUAL_BY_ORDINAL"),
    ("P_IH_ALL_SEVEN_MODELS", (1, 2, 3), "COMMON_EXPOSURE_EQUAL_BY_ORDINAL"),
    ("P_IK_A_B_A_vs_A_GAP_A", (1, 3, 4), "COMMON_EXPOSURE_EQUAL_BY_ORDINAL"),
    ("P_IK_A_B_A_vs_A_GAP_A", (2,), "COMMON_EXPOSURE_INTENTIONALLY_DIFFERENT_B_VS_GAP"),
    ("P_IN_RECOVERY_ON_vs_OFF", (1, 2, 3, 4), "COMMON_EXPOSURE_EQUAL_BY_ORDINAL"),
)
S1_JM_VALIDATION_ORDER = (
    "validate-one-exact-S1-JK-envelope-and-orchestration-control-before-reading-model-state",
    "canonicalize-and-digest-common-exposure-without-private-state-or-control-labels",
    "require-one-bit-identical-common-exposure-digest-across-all-seven-models-for-the-same-envelope",
    "canonicalize-and-digest-each-complete-private-prestate-without-cross-model-comparison",
    "apply-only-the-registered-initial-boundary-or-carry-operation-in-a-later-pure-materializer",
    "canonicalize-and-digest-the-materialized-input-then-pass-only-the-four-model-invocation-fields",
    "capture-checkpoint-only-after-a-complete-model-return-without-feedback-to-any-digest-or-later-input",
)
S1_JM_PRIVATE_STATE_RULES = (
    "private-prestate-digests-may-be-equal-or-different-by-value-and-neither-outcome-is-an-acceptance-condition",
    "P_IE-carries-each-models-own-complete-S-H-output-after-interval-one",
    "P_IH-P_IK-P_IN-boundaries-replace-only-S-H-and-preserve-each-models-own-private-state",
    "candidate-sidecars-enter-only-DTS1-private-state-and-orchestration-control-never-common-exposure",
    "no-private-digest-may-select-configurations-branches-retries-thresholds-or-another-models-input",
)
S1_JM_CANONICALIZATION_RULES = (
    "all-payloads-use-only-primitives-lists-and-mappings-with-no-object-repr-memory-address-or-process-state",
    "all-numbers-must-be-finite-and-negative-zero-is-canonicalized-to-positive-zero-before-encoding",
    "all-mappings-use-sorted-keys-and-all-registered-sequences-use-canonical-order",
    "encode-as-UTF-8-JSON-with-allow-nan-false-and-compact-comma-colon-separators-then-SHA-256",
    "digest-validation-is-complete-before-output-and-one-mismatch-produces-no-partial-view",
)
S1_JM_SUPERSEDED_S1JG_BINDINGS = (
    "complete-model-facing-view-value-identity-across-DTS1-and-B1-through-B6",
    "model-readable-input-digest-as-a-fifth-model-invocation-field",
)
S1_JM_PRESERVED_BINDINGS = (
    "S1-JG-common-external-exposure-information-barrier-sequence-order-and-checkpoint-nonfeedback",
    "all-S1-JK-times-sequence-digests-interval-digests-and-carry-links",
    "all-S1-JH-nontemporal-fixtures-sidecars-refinements-budgets-and-quarantine-rules",
    "all-S1-JI-materialization-identity-API-payload-atomicity-gaps-remain-to-be-bound",
)
S1_JM_FAIL_CLOSED_RULES = (
    "reject-any-common-exposure-digest-mismatch-among-the-seven-models-before-any-model-call",
    "reject-any-private-state-crossdelivery-missing-provenance-or-prior-output-mismatch",
    "reject-any-integrity-digest-or-control-label-delivery-to-a-model-kernel-or-calculator",
    "reject-any-canonicalization-schema-nonfinite-value-negative-zero-order-or-digest-drift",
    "one-failure-blocks-all-twenty-four-later-baseline-cases-without-partial-output",
)
S1_JM_FORBIDDEN_INTERPRETATIONS = (
    "materialization-identities-or-complete-materializer-API-bound-implemented-or-executed",
    "private-prestate-equality-or-inequality-is-a-functional-result",
    "baseline-fit-baseline-closure-candidate-superiority-memory-learning-or-artificial-intelligence",
)
S1_JM_DECISION = (
    "COMMON_EXPOSURE_PRIVATE_PRESTATE_AND_WRAPPER_INTEGRITY_ROLES_SEPARATED_NO_IMPLEMENTATION_OR_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JMExposurePrestateIntegrityContract:
    contract_id: str
    source_s1jl_digest: str
    source_s1jk_digest: str
    common_exposure_payload_schema: tuple[tuple[str, str], ...]
    private_prestate_payload_schema: tuple[tuple[str, str], ...]
    materialized_input_payload_schema: tuple[tuple[str, str], ...]
    orchestration_control_schema: tuple[tuple[str, str], ...]
    digest_roles: tuple[tuple[str, str, str], ...]
    model_invocation_fields: tuple[str, ...]
    model_invocation_exclusions: tuple[str, ...]
    cross_model_equivalence_matrix: tuple[tuple[str, tuple[int, ...], str], ...]
    validation_order: tuple[str, ...]
    private_state_rules: tuple[str, ...]
    canonicalization_rules: tuple[str, ...]
    superseded_s1jg_bindings: tuple[str, ...]
    preserved_bindings: tuple[str, ...]
    fail_closed_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    digest_role_count: int
    model_invocation_field_count: int
    exposure_prestate_separation_bound: bool
    materialization_identity_schema_bound: bool
    common_interval_fixture_implemented: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    finite_materialization_schema_contract_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_JM_CONTRACT_ID
            or self.source_s1jl_digest != S1_JM_SOURCE_S1JL_DIGEST
            or self.source_s1jk_digest != S1_JM_SOURCE_S1JK_DIGEST
            or self.common_exposure_payload_schema
            != S1_JM_COMMON_EXPOSURE_PAYLOAD_SCHEMA
            or self.private_prestate_payload_schema
            != S1_JM_PRIVATE_PRESTATE_PAYLOAD_SCHEMA
            or self.materialized_input_payload_schema
            != S1_JM_MATERIALIZED_INPUT_PAYLOAD_SCHEMA
            or self.orchestration_control_schema
            != S1_JM_ORCHESTRATION_CONTROL_SCHEMA
            or self.digest_roles != S1_JM_DIGEST_ROLES
            or self.model_invocation_fields != S1_JM_MODEL_INVOCATION_FIELDS
            or self.model_invocation_exclusions != S1_JM_MODEL_INVOCATION_EXCLUSIONS
            or self.cross_model_equivalence_matrix
            != S1_JM_CROSS_MODEL_EQUIVALENCE_MATRIX
            or self.validation_order != S1_JM_VALIDATION_ORDER
            or self.private_state_rules != S1_JM_PRIVATE_STATE_RULES
            or self.canonicalization_rules != S1_JM_CANONICALIZATION_RULES
            or self.superseded_s1jg_bindings != S1_JM_SUPERSEDED_S1JG_BINDINGS
            or self.preserved_bindings != S1_JM_PRESERVED_BINDINGS
            or self.fail_closed_rules != S1_JM_FAIL_CLOSED_RULES
            or self.forbidden_interpretations != S1_JM_FORBIDDEN_INTERPRETATIONS
            or self.digest_role_count != 4
            or self.model_invocation_field_count != 4
            or self.exposure_prestate_separation_bound is not True
            or self.materialization_identity_schema_bound is not False
            or self.common_interval_fixture_implemented is not False
            or self.adapters_implemented is not False
            or self.baseline_models_executed is not False
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.finite_materialization_schema_contract_authorized_next_stage
            is not True
            or self.decision != S1_JM_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JMExposurePrestateIntegrityContractError(
                "S1-JM weakened the exposure and private prestate separation"
            )


def build_dts1_s1jm_exposure_prestate_integrity_contract(
) -> DTS1S1JMExposurePrestateIntegrityContract:
    """Bind separate integrity roles without materializing or running models."""

    source = build_dts1_s1jl_model_view_equivalence_precheck()
    fixture_source = build_dts1_s1jk_corrected_monotonic_interval_contract()
    values = {
        "contract_id": S1_JM_CONTRACT_ID,
        "source_s1jl_digest": source.audit_digest,
        "source_s1jk_digest": fixture_source.contract_digest,
        "common_exposure_payload_schema": S1_JM_COMMON_EXPOSURE_PAYLOAD_SCHEMA,
        "private_prestate_payload_schema": S1_JM_PRIVATE_PRESTATE_PAYLOAD_SCHEMA,
        "materialized_input_payload_schema": S1_JM_MATERIALIZED_INPUT_PAYLOAD_SCHEMA,
        "orchestration_control_schema": S1_JM_ORCHESTRATION_CONTROL_SCHEMA,
        "digest_roles": S1_JM_DIGEST_ROLES,
        "model_invocation_fields": S1_JM_MODEL_INVOCATION_FIELDS,
        "model_invocation_exclusions": S1_JM_MODEL_INVOCATION_EXCLUSIONS,
        "cross_model_equivalence_matrix": S1_JM_CROSS_MODEL_EQUIVALENCE_MATRIX,
        "validation_order": S1_JM_VALIDATION_ORDER,
        "private_state_rules": S1_JM_PRIVATE_STATE_RULES,
        "canonicalization_rules": S1_JM_CANONICALIZATION_RULES,
        "superseded_s1jg_bindings": S1_JM_SUPERSEDED_S1JG_BINDINGS,
        "preserved_bindings": S1_JM_PRESERVED_BINDINGS,
        "fail_closed_rules": S1_JM_FAIL_CLOSED_RULES,
        "forbidden_interpretations": S1_JM_FORBIDDEN_INTERPRETATIONS,
        "digest_role_count": len(S1_JM_DIGEST_ROLES),
        "model_invocation_field_count": len(S1_JM_MODEL_INVOCATION_FIELDS),
        "exposure_prestate_separation_bound": True,
        "materialization_identity_schema_bound": False,
        "common_interval_fixture_implemented": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "finite_materialization_schema_contract_authorized_next_stage": True,
        "decision": S1_JM_DECISION,
    }
    return DTS1S1JMExposurePrestateIntegrityContract(
        **values, contract_digest=_digest(values)
    )
