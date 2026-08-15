"""Static S1-JL precheck of complete model-view value identity."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)


class DTS1S1JLModelViewEquivalencePrecheckError(ValueError):
    """Raised when the fail-closed S1-JL finding is weakened."""


S1_JL_AUDIT_ID = "dynamic-substrate.model-view-equivalence-precheck.s1jl.v1"
S1_JL_SOURCE_S1JK_DIGEST = (
    "64ca5b895146fef453eb27945a1074f5d2b8e4c8834a94cc6f9b0a855a61824f"
)
S1_JL_CONFLICTING_REQUIREMENTS = (
    (
        "S1_JG_COMPLETE_VIEW_IDENTITY",
        "deliver-value-identical-model-facing-views-to-DTS1-and-B1-through-B6-for-the-same-envelope",
    ),
    (
        "S1_JG_MODEL_STATE_CARRY",
        "each-model-owned-hidden-state-is-carried-between-envelopes-and-never-stored-in-the-common-envelope",
    ),
    (
        "S1_JG_P_IE_COMPLETE_SH_CARRY",
        "P_IE-carries-complete-S-H-after-interval-one",
    ),
)
S1_JL_MODEL_OWNED_STATE_ROLES = (
    ("DTS1", "private-resource-anatomy-and-current-coupled-field-output"),
    ("B1", "one-fixed-prerelease-adapter-and-current-field-output"),
    ("B2", "private-L-state-and-current-field-output"),
    ("B3", "private-M-state-and-current-field-output"),
    ("B4", "private-M-state-and-current-field-output"),
    ("B5", "private-M-state-and-current-field-output"),
    ("B6", "private-M-state-frozen-spec-and-current-field-output"),
)
S1_JL_PROFILE_IMPACT = (
    (
        "P_IE_CAUSAL_TWO_SUBSTEP",
        "interval-two-must-carry-each-models-own-complete-postinterval-one-S-H",
        "complete-field-value-identity-is-not-permitted-after-divergence",
    ),
    (
        "P_IH_ATTENUATION",
        "each-A-boundary-equalizes-only-S-H-while-private-state-carries",
        "complete-model-prestate-value-identity-is-not-permitted",
    ),
    (
        "P_IK_INTERFERENCE",
        "each-boundary-equalizes-only-S-H-while-private-history-carries",
        "complete-model-prestate-value-identity-is-not-permitted",
    ),
    (
        "P_IN_RELEASE_REUSE",
        "each-boundary-equalizes-only-S-H-while-private-history-and-DTS1-recovery-intervention-carry",
        "complete-model-prestate-value-identity-is-not-permitted",
    ),
)
S1_JL_VALID_COMMON_EXPOSURE_EQUIVALENCE = (
    "same-canonical-geometry-and-node-order-for-the-same-envelope",
    "same-registered-S-H-source-values-when-a-boundary-or-initial-directive-applies",
    "same-receptor-contact-distribution-values-identities-and-common-step-time",
    "same-envelope-order-checkpoint-location-and-physical-refinement-horizon",
    "no-profile-arm-case-target-result-or-candidate-sidecar-visible-to-B1-through-B6",
)
S1_JL_REQUIRED_PRIVATE_PRESTATE_SEPARATION = (
    "complete-carried-field-and-model-owned-state-are-validated-per-model-not-equalized-across-models",
    "P_IE-complete-S-H-carry-remains-model-specific-after-the-first-interval",
    "boundary-profiles-replace-only-S-H-and-preserve-each-models-own-hidden-state",
    "candidate-sidecars-remain-DTS1-only-and-baseline-state-never-enters-another-model",
    "private-prestate-provenance-may-not-control-the-common-envelope-or-any-other-model",
)
S1_JL_DIGEST_CORRECTION_REQUIREMENTS = (
    (
        "COMMON_EXPOSURE_DIGEST",
        "cross-model-identical-value-only-digest-of-geometry-registered-prestate-directive-contact-time-and-checkpoint-without-labels-or-model-state",
    ),
    (
        "PRIVATE_PRESTATE_DIGEST",
        "orchestrator-only-per-model-value-digest-of-complete-carried-field-and-model-owned-state-for-provenance-not-cross-model-equality",
    ),
    (
        "MODEL_INPUT_DIGEST",
        "must-not-collapse-common-exposure-and-private-prestate-into-a-false-cross-model-identity-claim",
    ),
)
S1_JL_PRESERVED_BINDINGS = (
    "all-S1-JK-monotonic-times-sequence-digests-interval-digests-and-carry-links",
    "all-S1-JH-geometries-S-H-values-contacts-sidecars-refinements-budgets-and-quarantine-rules",
    "all-S1-JI-missing-materialization-identity-API-payload-and-atomicity-requirements",
    "all-twenty-four-baseline-role-block-case-identities-remain-blocked",
)
S1_JL_SUPERSEDED_BINDING = (
    "only-the-S1-JG-requirement-that-the-complete-model-facing-view-be-value-identical-across-models"
)
S1_JL_FORBIDDEN_SHORTCUTS = (
    "do-not-reset-copy-or-project-away-private-L-M-adapter-anatomy-or-carried-S-H-to-force-equality",
    "do-not-pass-one-models-private-prestate-or-digest-to-another-model",
    "do-not-use-private-prestate-digests-as-fit-keys-branch-selectors-or-common-exposure-values",
    "do-not-weaken-cross-model-equality-of-the-actual-external-exposure",
)
S1_JL_FORBIDDEN_INTERPRETATIONS = (
    "fair-comparison-no-longer-requires-identical-external-causal-history",
    "S1-JK-or-preserved-S1-JH-values-digests-sidecars-or-budgets-are-invalid",
    "materializer-adapter-model-or-baseline-implemented-or-executed",
    "baseline-closure-candidate-superiority-memory-learning-or-artificial-intelligence",
)
S1_JL_DECISION = (
    "STOPP_COMPLETE_MODEL_VIEW_VALUE_IDENTITY_CONFLICTS_WITH_REQUIRED_MODEL_STATE_CARRY"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JLModelViewEquivalencePrecheck:
    audit_id: str
    source_s1jk_digest: str
    conflicting_requirements: tuple[tuple[str, str], ...]
    model_owned_state_roles: tuple[tuple[str, str], ...]
    profile_impact: tuple[tuple[str, str, str], ...]
    valid_common_exposure_equivalence: tuple[str, ...]
    required_private_prestate_separation: tuple[str, ...]
    digest_correction_requirements: tuple[tuple[str, str], ...]
    preserved_bindings: tuple[str, ...]
    superseded_binding: str
    forbidden_shortcuts: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    affected_profile_count: int
    model_role_count: int
    baseline_case_count_still_blocked: int
    complete_model_view_value_identity_valid: bool
    common_exposure_equivalence_remains_required: bool
    private_model_state_carry_remains_required: bool
    materialization_schema_bound: bool
    common_interval_fixture_implemented: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    corrected_exposure_prestate_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_JL_AUDIT_ID
            or self.source_s1jk_digest != S1_JL_SOURCE_S1JK_DIGEST
            or self.conflicting_requirements != S1_JL_CONFLICTING_REQUIREMENTS
            or self.model_owned_state_roles != S1_JL_MODEL_OWNED_STATE_ROLES
            or self.profile_impact != S1_JL_PROFILE_IMPACT
            or self.valid_common_exposure_equivalence
            != S1_JL_VALID_COMMON_EXPOSURE_EQUIVALENCE
            or self.required_private_prestate_separation
            != S1_JL_REQUIRED_PRIVATE_PRESTATE_SEPARATION
            or self.digest_correction_requirements
            != S1_JL_DIGEST_CORRECTION_REQUIREMENTS
            or self.preserved_bindings != S1_JL_PRESERVED_BINDINGS
            or self.superseded_binding != S1_JL_SUPERSEDED_BINDING
            or self.forbidden_shortcuts != S1_JL_FORBIDDEN_SHORTCUTS
            or self.forbidden_interpretations != S1_JL_FORBIDDEN_INTERPRETATIONS
            or self.affected_profile_count != 4
            or self.model_role_count != 7
            or self.baseline_case_count_still_blocked != 24
            or self.complete_model_view_value_identity_valid is not False
            or self.common_exposure_equivalence_remains_required is not True
            or self.private_model_state_carry_remains_required is not True
            or self.materialization_schema_bound is not False
            or self.common_interval_fixture_implemented is not False
            or self.adapters_implemented is not False
            or self.baseline_models_executed is not False
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.corrected_exposure_prestate_contract_authorized_next_stage
            is not True
            or self.decision != S1_JL_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1JLModelViewEquivalencePrecheckError(
                "S1-JL weakened the model-view equivalence STOPP"
            )


def build_dts1_s1jl_model_view_equivalence_precheck(
) -> DTS1S1JLModelViewEquivalencePrecheck:
    """Stop schema binding when complete model-view identity is contradictory."""

    source = build_dts1_s1jk_corrected_monotonic_interval_contract()
    values = {
        "audit_id": S1_JL_AUDIT_ID,
        "source_s1jk_digest": source.contract_digest,
        "conflicting_requirements": S1_JL_CONFLICTING_REQUIREMENTS,
        "model_owned_state_roles": S1_JL_MODEL_OWNED_STATE_ROLES,
        "profile_impact": S1_JL_PROFILE_IMPACT,
        "valid_common_exposure_equivalence": S1_JL_VALID_COMMON_EXPOSURE_EQUIVALENCE,
        "required_private_prestate_separation": S1_JL_REQUIRED_PRIVATE_PRESTATE_SEPARATION,
        "digest_correction_requirements": S1_JL_DIGEST_CORRECTION_REQUIREMENTS,
        "preserved_bindings": S1_JL_PRESERVED_BINDINGS,
        "superseded_binding": S1_JL_SUPERSEDED_BINDING,
        "forbidden_shortcuts": S1_JL_FORBIDDEN_SHORTCUTS,
        "forbidden_interpretations": S1_JL_FORBIDDEN_INTERPRETATIONS,
        "affected_profile_count": len(S1_JL_PROFILE_IMPACT),
        "model_role_count": len(S1_JL_MODEL_OWNED_STATE_ROLES),
        "baseline_case_count_still_blocked": 24,
        "complete_model_view_value_identity_valid": False,
        "common_exposure_equivalence_remains_required": True,
        "private_model_state_carry_remains_required": True,
        "materialization_schema_bound": False,
        "common_interval_fixture_implemented": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "corrected_exposure_prestate_contract_authorized_next_stage": True,
        "decision": S1_JL_DECISION,
    }
    return DTS1S1JLModelViewEquivalencePrecheck(
        **values, audit_digest=_digest(values)
    )
