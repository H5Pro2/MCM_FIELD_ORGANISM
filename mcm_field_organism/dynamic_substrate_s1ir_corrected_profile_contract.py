"""Static S1-IR correction of the DTS-1 joint baseline profile contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1ip_joint_baseline_contract import (
    S1_IP_ALLOWED_BASELINE_INPUTS,
    S1_IP_CONTRACT_ID,
    S1_IP_DECISION_ORDER,
    S1_IP_EXECUTABLE_BASELINE_ROLES,
    S1_IP_FORBIDDEN_BASELINE_INPUTS,
    S1_IP_FORBIDDEN_INTERPRETATIONS,
    S1_IP_PARAMETER_RULES,
    S1_IP_PROFILE_RULES,
    S1_IP_REFERENCE_RECEIPTS,
    S1_IP_STOPP_CONDITIONS,
    S1_IP_STRUCTURAL_BASELINE_ROLES,
    S1_IP_STRUCTURAL_GATES,
)
from .dynamic_substrate_s1iq_compatibility_precheck import (
    build_dts1_s1iq_compatibility_precheck,
)


class DTS1S1IRCorrectedProfileContractError(ValueError):
    """Raised when S1-IR changes more than the audited cardinality error."""


S1_IR_CONTRACT_ID = "dynamic-substrate.corrected-joint-baseline-profile.s1ir.v1"
S1_IR_SOURCE_S1IQ_AUDIT_DIGEST = (
    "b766a456ad1e368701a797bec7a85bf9e442be207c945594d6ed1c0a99712b60"
)
S1_IR_SUPERSEDED_S1IP_DIGEST = (
    "685d4d90c894d441f69d558fa91de110e51124b84442df31949b45e4de8d6625"
)
S1_IR_PROFILE_BLOCKS = (
    ("P_IE_CAUSAL_TWO_SUBSTEP", "signed-F_HIGH-minus-R_HIGH-complete-SH-at-substeps-1-and-2", 8),
    ("P_IH_ATTENUATION", "signed-checkpoint-2-minus-1-and-checkpoint-3-minus-1-complete-SH", 8),
    ("P_IK_INTERFERENCE", "signed-ABA-minus-A-gap-A-postsequence-complete-SH", 6),
    ("P_IN_RELEASE_REUSE", "signed-recovery-on-minus-recovery-off-postprobe-complete-SH", 6),
)
S1_IR_COMPARISON_METRICS = (
    "profile_linf_residual-over-all-28-signed-components",
    "profile_l1_residual-over-all-28-signed-components",
    "relative_profile_linf_residual-against-one-preregistered-reference-scale",
    "per-block-linf-residual-for-P_IE-P_IH-P_IK-and-P_IN",
    "baseline-refinement-residual-where-the-existing-kernel-has-a-refinement-control",
    "maximum-own-invariant-residual-and-minimum-own-valid-resource-where-defined",
    "schedule-geometry-ablation-fixed-reader-zero-H-and-deterministic-repeat-booleans",
)
S1_IR_CORRECTION_SCOPE = (
    "P_IE-component-count-corrected-from-12-to-8",
    "P_IH-component-count-corrected-from-12-to-8",
    "joint-profile-component-count-corrected-from-36-to-28",
    "global-linf-and-l1-metric-labels-corrected-from-36-to-28",
    "all-profile-content-order-sign-gates-baseline-roles-input-rules-parameter-rules-decision-order-stopp-rules-and-claim-locks-preserved",
)
S1_IR_DECISION = (
    "DTS1_CORRECTED_28_COMPONENT_JOINT_BASELINE_CONTRACT_BOUND_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IRCorrectedProfileContract:
    contract_id: str
    source_s1iq_audit_digest: str
    superseded_s1ip_contract_id: str
    superseded_s1ip_digest: str
    reference_receipts: tuple[tuple[str, str], ...]
    executable_baseline_roles: tuple[tuple[str, str], ...]
    structural_baseline_roles: tuple[tuple[str, str], ...]
    profile_blocks: tuple[tuple[str, str, int], ...]
    profile_rules: tuple[str, ...]
    structural_gates: tuple[str, ...]
    allowed_baseline_inputs: tuple[str, ...]
    forbidden_baseline_inputs: tuple[str, ...]
    parameter_rules: tuple[str, ...]
    comparison_metrics: tuple[str, ...]
    decision_order: tuple[str, ...]
    stopp_conditions: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    correction_scope: tuple[str, ...]
    profile_component_count: int
    s1ip_valid_for_future_baseline_work: bool
    corrected_profile_contract_valid: bool
    parameter_values_selected: bool
    comparison_threshold_selected: bool
    geometry_adapters_implemented: bool
    profile_container_implemented: bool
    baseline_signatures_classified: bool
    baseline_models_executed: bool
    joint_comparison_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    compatibility_audit_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_IR_CONTRACT_ID
            or self.source_s1iq_audit_digest != S1_IR_SOURCE_S1IQ_AUDIT_DIGEST
            or self.superseded_s1ip_contract_id != S1_IP_CONTRACT_ID
            or self.superseded_s1ip_digest != S1_IR_SUPERSEDED_S1IP_DIGEST
            or self.reference_receipts != S1_IP_REFERENCE_RECEIPTS
            or self.executable_baseline_roles != S1_IP_EXECUTABLE_BASELINE_ROLES
            or self.structural_baseline_roles != S1_IP_STRUCTURAL_BASELINE_ROLES
            or self.profile_blocks != S1_IR_PROFILE_BLOCKS
            or self.profile_rules != S1_IP_PROFILE_RULES
            or self.structural_gates != S1_IP_STRUCTURAL_GATES
            or self.allowed_baseline_inputs != S1_IP_ALLOWED_BASELINE_INPUTS
            or self.forbidden_baseline_inputs != S1_IP_FORBIDDEN_BASELINE_INPUTS
            or self.parameter_rules != S1_IP_PARAMETER_RULES
            or self.comparison_metrics != S1_IR_COMPARISON_METRICS
            or self.decision_order != S1_IP_DECISION_ORDER
            or self.stopp_conditions != S1_IP_STOPP_CONDITIONS
            or self.forbidden_interpretations != S1_IP_FORBIDDEN_INTERPRETATIONS
            or self.correction_scope != S1_IR_CORRECTION_SCOPE
            or self.profile_component_count != 28
            or self.s1ip_valid_for_future_baseline_work is not False
            or self.corrected_profile_contract_valid is not True
            or any(
                value is not False
                for value in (
                    self.parameter_values_selected,
                    self.comparison_threshold_selected,
                    self.geometry_adapters_implemented,
                    self.profile_container_implemented,
                    self.baseline_signatures_classified,
                    self.baseline_models_executed,
                    self.joint_comparison_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.compatibility_audit_authorized_next_stage is not True
            or self.decision != S1_IR_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IRCorrectedProfileContractError(
                "S1-IR changed more than the audited profile cardinality"
            )


def build_dts1_s1ir_corrected_profile_contract() -> DTS1S1IRCorrectedProfileContract:
    """Supersede S1-IP with the corrected 28-component static contract."""

    source = build_dts1_s1iq_compatibility_precheck()
    values = {
        "contract_id": S1_IR_CONTRACT_ID,
        "source_s1iq_audit_digest": source.audit_digest,
        "superseded_s1ip_contract_id": S1_IP_CONTRACT_ID,
        "superseded_s1ip_digest": source.source_s1ip_digest,
        "reference_receipts": S1_IP_REFERENCE_RECEIPTS,
        "executable_baseline_roles": S1_IP_EXECUTABLE_BASELINE_ROLES,
        "structural_baseline_roles": S1_IP_STRUCTURAL_BASELINE_ROLES,
        "profile_blocks": S1_IR_PROFILE_BLOCKS,
        "profile_rules": S1_IP_PROFILE_RULES,
        "structural_gates": S1_IP_STRUCTURAL_GATES,
        "allowed_baseline_inputs": S1_IP_ALLOWED_BASELINE_INPUTS,
        "forbidden_baseline_inputs": S1_IP_FORBIDDEN_BASELINE_INPUTS,
        "parameter_rules": S1_IP_PARAMETER_RULES,
        "comparison_metrics": S1_IR_COMPARISON_METRICS,
        "decision_order": S1_IP_DECISION_ORDER,
        "stopp_conditions": S1_IP_STOPP_CONDITIONS,
        "forbidden_interpretations": S1_IP_FORBIDDEN_INTERPRETATIONS,
        "correction_scope": S1_IR_CORRECTION_SCOPE,
        "profile_component_count": sum(item[2] for item in S1_IR_PROFILE_BLOCKS),
        "s1ip_valid_for_future_baseline_work": False,
        "corrected_profile_contract_valid": True,
        "parameter_values_selected": False,
        "comparison_threshold_selected": False,
        "geometry_adapters_implemented": False,
        "profile_container_implemented": False,
        "baseline_signatures_classified": False,
        "baseline_models_executed": False,
        "joint_comparison_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "compatibility_audit_authorized_next_stage": True,
        "decision": S1_IR_DECISION,
    }
    return DTS1S1IRCorrectedProfileContract(
        **values, contract_digest=_digest(values)
    )
