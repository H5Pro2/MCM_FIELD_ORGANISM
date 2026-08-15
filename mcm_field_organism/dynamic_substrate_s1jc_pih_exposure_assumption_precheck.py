"""Static S1-JC precheck of the retained P_IH exposure assumption."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jb_adapter_implementation_readiness_precheck import (
    build_dts1_s1jb_adapter_implementation_readiness_precheck,
)


class DTS1S1JCPIHExposureAssumptionPrecheckError(ValueError):
    """Raised when the fail-closed S1-JC P_IH finding is weakened."""


S1_JC_AUDIT_ID = "dynamic-substrate.pih-common-exposure-assumption.s1jc.v1"
S1_JC_SOURCE_S1JB_DIGEST = (
    "0b07da931c60b298e398d75449eb4bc41e528f3a16baad392a25d95cf033d93b"
)
S1_JC_PROFILE_RECORDS = (
    (
        "P_IE_CAUSAL_TWO_SUBSTEP",
        "both-arms-carry-one-complete-S-H-field-and-model-state-through-two-coupled-intervals",
        "COMMON_CAUSAL_EXPOSURE_CONFIRMED",
    ),
    (
        "P_IH_ATTENUATION",
        "three-resource-only-DTS1-steps-carry-anatomy-while-each-field-checkpoint-starts-from-one-fresh-common-S-H-field",
        "INVALID_RETAINED_COMMON_EXPOSURE_ASSUMPTION",
    ),
    (
        "P_IK_INTERFERENCE",
        "corrected-S1-IX-S1-IY-event-boundaries-bound-common-envelope-still-missing",
        "CORRECTED_EXPOSURE_CONTRACT_VALID_ENVELOPE_BLOCKED",
    ),
    (
        "P_IN_RELEASE_REUSE",
        "corrected-S1-IX-S1-IY-event-boundaries-bound-common-envelope-still-missing",
        "CORRECTED_EXPOSURE_CONTRACT_VALID_ENVELOPE_BLOCKED",
    ),
)
S1_JC_P_IH_SOURCE_FACTS = (
    "active-P_IH-loop-calls-compute_dts1_closed_prestate_step-for-the-carried-resource-history",
    "each-P_IH-field-call-constructs-a-new-initial-field-from-the-same-S-and-H-values",
    "each-P_IH-field-call-reads-the-current-precontact-anatomy-but-its-returned-anatomy-is-discarded",
    "P_IH-field-checkpoint-outputs-therefore-see-DTS1-anatomy-history-not-one-common-stateful-baseline-history",
    "DTS1-participation-anatomy-and-resource-transfers-are-forbidden-inputs-for-B1-through-B6",
    "fresh-field-checkpoints-alone-cannot-supply-equivalent-prior-A-exposure-to-stateful-B2-through-B6",
)
S1_JC_REQUIRED_CORRECTION = (
    "bind-one-model-neutral-two-node-A-boundary-with-positive-S1-HK-participation-before-values",
    "deliver-three-identical-positive-A-active-intervals-to-DTS1-and-B1-through-B6",
    "replace-only-S-H-at-each-A-boundary-while-each-model-owned-hidden-state-carries",
    "use-one-identical-all-node-zero-contact-duration-and-checkpoint-after-each-active-interval",
    "derive-DTS1-participation-only-after-each-common-two-node-S-H-boundary",
    "quarantine-old-P_IH-field-vectors-for-joint-comparison-and-reregister-without-old-numeric-reuse",
    "retain-P_IH-direct-engagement-attenuation-ledgers-receipts-and-functional-direction",
)
S1_JC_PRESERVED_BINDINGS = (
    "P_IE-existing-common-exposure-and-profile-remain-valid",
    "P_IK-and-P_IN-corrected-boundary-contracts-remain-valid",
    "all-seven-S1-JA-configurations-digests-and-refinements-remain-bound",
    "all-twenty-four-case-identities-remain-bound-and-blocked",
    "S1-JB-common-interval-envelope-requirement-remains-valid-after-P_IH-correction",
)
S1_JC_FORBIDDEN_INTERPRETATIONS = (
    "invalidity-of-direct-P_IH-attenuation-ledgers-kernel-incompatibility-or-configuration-failure",
    "baseline-rejection-baseline-closure-candidate-superiority-memory-learning-or-artificial-intelligence",
)
S1_JC_DECISION = "STOPP_P_IH_RETAINED_COMMON_CAUSAL_EXPOSURE_ASSUMPTION_INVALID"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JCPIHExposureAssumptionPrecheck:
    audit_id: str
    source_s1jb_digest: str
    profile_records: tuple[tuple[str, str, str], ...]
    p_ih_source_facts: tuple[str, ...]
    required_correction: tuple[str, ...]
    preserved_bindings: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    retained_profile_block_count: int
    invalid_retained_profile_block_count: int
    planned_adapter_case_count: int
    blocked_adapter_case_count: int
    p_ih_common_exposure_valid: bool
    old_p_ih_field_vectors_quarantined: bool
    p_ih_direct_ledgers_retained: bool
    common_interval_envelope_bound: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    corrected_p_ih_exposure_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_JC_AUDIT_ID
            or self.source_s1jb_digest != S1_JC_SOURCE_S1JB_DIGEST
            or self.profile_records != S1_JC_PROFILE_RECORDS
            or self.p_ih_source_facts != S1_JC_P_IH_SOURCE_FACTS
            or self.required_correction != S1_JC_REQUIRED_CORRECTION
            or self.preserved_bindings != S1_JC_PRESERVED_BINDINGS
            or self.forbidden_interpretations != S1_JC_FORBIDDEN_INTERPRETATIONS
            or self.retained_profile_block_count != 2
            or self.invalid_retained_profile_block_count != 1
            or self.planned_adapter_case_count != 24
            or self.blocked_adapter_case_count != 24
            or self.p_ih_common_exposure_valid is not False
            or self.old_p_ih_field_vectors_quarantined is not True
            or self.p_ih_direct_ledgers_retained is not True
            or self.common_interval_envelope_bound is not False
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
            or self.corrected_p_ih_exposure_contract_authorized_next_stage is not True
            or self.decision != S1_JC_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1JCPIHExposureAssumptionPrecheckError(
                "S1-JC weakened the P_IH common-exposure STOPP"
            )


def build_dts1_s1jc_pih_exposure_assumption_precheck() -> DTS1S1JCPIHExposureAssumptionPrecheck:
    """Stop envelope binding when retained P_IH history is not common."""

    source = build_dts1_s1jb_adapter_implementation_readiness_precheck()
    values = {
        "audit_id": S1_JC_AUDIT_ID,
        "source_s1jb_digest": source.audit_digest,
        "profile_records": S1_JC_PROFILE_RECORDS,
        "p_ih_source_facts": S1_JC_P_IH_SOURCE_FACTS,
        "required_correction": S1_JC_REQUIRED_CORRECTION,
        "preserved_bindings": S1_JC_PRESERVED_BINDINGS,
        "forbidden_interpretations": S1_JC_FORBIDDEN_INTERPRETATIONS,
        "retained_profile_block_count": 2,
        "invalid_retained_profile_block_count": 1,
        "planned_adapter_case_count": source.planned_adapter_case_count,
        "blocked_adapter_case_count": source.blocked_adapter_case_count,
        "p_ih_common_exposure_valid": False,
        "old_p_ih_field_vectors_quarantined": True,
        "p_ih_direct_ledgers_retained": True,
        "common_interval_envelope_bound": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "corrected_p_ih_exposure_contract_authorized_next_stage": True,
        "decision": S1_JC_DECISION,
    }
    return DTS1S1JCPIHExposureAssumptionPrecheck(
        **values, audit_digest=_digest(values)
    )
