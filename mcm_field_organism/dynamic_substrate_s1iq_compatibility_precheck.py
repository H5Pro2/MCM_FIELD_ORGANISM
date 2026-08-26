"""Static S1-IQ precheck before DTS-1 baseline compatibility auditing."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1ip_joint_baseline_contract import (
    S1_IP_DECISION_ORDER,
    build_dts1_s1ip_joint_baseline_contract,
)


class DTS1S1IQCompatibilityPrecheckError(ValueError):
    """Raised when the fail-closed S1-IQ precheck is weakened."""


S1_IQ_AUDIT_ID = "dynamic-substrate.baseline-compatibility-precheck.s1iq.v1"
S1_IQ_SOURCE_S1IP_DIGEST = (
    "685d4d90c894d441f69d558fa91de110e51124b84442df31949b45e4de8d6625"
)
S1_IQ_PROFILE_CARDINALITIES = (
    ("P_IE_CAUSAL_TWO_SUBSTEP", 2, 2, 4, 8, 12),
    ("P_IH_ATTENUATION", 2, 2, 4, 8, 12),
    ("P_IK_INTERFERENCE", 3, 1, 6, 6, 6),
    ("P_IN_RELEASE_REUSE", 3, 1, 6, 6, 6),
)
S1_IQ_EVIDENCE_RULES = (
    "P_IE-record-schema-binds-two-node-complete-SH-width-four-and-two-signed-substep-differences",
    "P_IH-record-schema-binds-two-node-complete-SH-width-four-and-two-signed-checkpoint-differences",
    "P_IK-record-schema-binds-three-node-complete-SH-width-six-and-one-signed-postsequence-difference",
    "P_IN-record-schema-binds-three-node-complete-SH-width-six-and-one-signed-postprobe-difference",
    "component-count-is-vector-width-times-number-of-bound-signed-differences-without-padding-or-duplication",
)
S1_IQ_BASELINE_STATUSES = (
    ("B1_FIXED_PRERELEASE_ADAPTER", "NOT_REACHED_INVALID_PROFILE_CARDINALITY"),
    ("B2_S2_LINEAR_INTEGRATOR", "NOT_REACHED_INVALID_PROFILE_CARDINALITY"),
    ("B3_F3_LOCAL_LEAKY", "NOT_REACHED_INVALID_PROFILE_CARDINALITY"),
    ("B4_F3_LINEAR_COUPLED", "NOT_REACHED_INVALID_PROFILE_CARDINALITY"),
    ("B5_F3_FULL", "NOT_REACHED_INVALID_PROFILE_CARDINALITY"),
    ("B6_CONST_V", "NOT_REACHED_INVALID_PROFILE_CARDINALITY"),
)
S1_IQ_STOPP_RULES = (
    "S1-IP-decision-order-requires-INVALID_JOINT_BASELINE_AUDIT-before-any-compatibility-classification",
    "registered-profile-cardinality-36-does-not-equal-schema-derived-cardinality-28",
    "no-baseline-may-be-classified-omitted-adapted-parameterized-or-executed-after-this-precheck-failure",
    "S1-IP-must-be-superseded-by-one-static-corrected-profile-contract-before-compatibility-audit-resumes",
)
S1_IQ_FORBIDDEN_INTERPRETATIONS = (
    "baseline-incompatibility-baseline-rejection-baseline-closure-or-candidate-superiority",
    "functional-falsification-or-support-beyond-the-existing-S1-IO-evidence-audit",
    "memory-learning-semantics-inner-context-organization-self-regulation-organism-or-artificial-intelligence",
)
S1_IQ_DECISION = "STOPP_INVALID_S1IP_PROFILE_CARDINALITY_36_NE_28"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IQCompatibilityPrecheck:
    audit_id: str
    source_s1ip_digest: str
    profile_cardinalities: tuple[tuple[str, int, int, int, int, int], ...]
    evidence_rules: tuple[str, ...]
    baseline_statuses: tuple[tuple[str, str], ...]
    stopp_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    expected_profile_component_count: int
    registered_profile_component_count: int
    cardinality_excess: int
    first_atomic_decision: str
    profile_contract_valid: bool
    baseline_signatures_classified: bool
    geometry_adapters_specified: bool
    parameter_values_selected: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    correction_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_IQ_AUDIT_ID
            or self.source_s1ip_digest != S1_IQ_SOURCE_S1IP_DIGEST
            or self.profile_cardinalities != S1_IQ_PROFILE_CARDINALITIES
            or self.evidence_rules != S1_IQ_EVIDENCE_RULES
            or self.baseline_statuses != S1_IQ_BASELINE_STATUSES
            or self.stopp_rules != S1_IQ_STOPP_RULES
            or self.forbidden_interpretations != S1_IQ_FORBIDDEN_INTERPRETATIONS
            or self.expected_profile_component_count != 28
            or self.registered_profile_component_count != 36
            or self.cardinality_excess != 8
            or self.first_atomic_decision != "INVALID_JOINT_BASELINE_AUDIT"
            or any(
                value is not False
                for value in (
                    self.profile_contract_valid,
                    self.baseline_signatures_classified,
                    self.geometry_adapters_specified,
                    self.parameter_values_selected,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.correction_contract_authorized_next_stage is not True
            or self.decision != S1_IQ_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1IQCompatibilityPrecheckError(
                "S1-IQ weakened the cardinality STOPP"
            )


def build_dts1_s1iq_compatibility_precheck() -> DTS1S1IQCompatibilityPrecheck:
    """Bind the schema-derived cardinality failure without model execution."""

    source = build_dts1_s1ip_joint_baseline_contract()
    expected = sum(item[4] for item in S1_IQ_PROFILE_CARDINALITIES)
    values = {
        "audit_id": S1_IQ_AUDIT_ID,
        "source_s1ip_digest": source.contract_digest,
        "profile_cardinalities": S1_IQ_PROFILE_CARDINALITIES,
        "evidence_rules": S1_IQ_EVIDENCE_RULES,
        "baseline_statuses": S1_IQ_BASELINE_STATUSES,
        "stopp_rules": S1_IQ_STOPP_RULES,
        "forbidden_interpretations": S1_IQ_FORBIDDEN_INTERPRETATIONS,
        "expected_profile_component_count": expected,
        "registered_profile_component_count": source.profile_component_count,
        "cardinality_excess": source.profile_component_count - expected,
        "first_atomic_decision": S1_IP_DECISION_ORDER[0],
        "profile_contract_valid": False,
        "baseline_signatures_classified": False,
        "geometry_adapters_specified": False,
        "parameter_values_selected": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "correction_contract_authorized_next_stage": True,
        "decision": S1_IQ_DECISION,
    }
    return DTS1S1IQCompatibilityPrecheck(**values, audit_digest=_digest(values))
