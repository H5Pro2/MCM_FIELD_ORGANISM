"""Static S1-JD corrected common causal exposure contract for P_IH."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jc_pih_exposure_assumption_precheck import (
    build_dts1_s1jc_pih_exposure_assumption_precheck,
)


class DTS1S1JDCorrectedPIHExposureContractError(ValueError):
    """Raised when the corrected S1-JD P_IH contract is weakened."""


S1_JD_CONTRACT_ID = "dynamic-substrate.corrected-common-pih-exposure.s1jd.v1"
S1_JD_SOURCE_S1JC_DIGEST = (
    "f1bb190007697aa29ff0e35e6532d3855ad67f5ab1cfe45d6e4b6cf14fd0783e"
)
S1_JD_BOUNDARY_ROLE = (
    "A_BOUNDARY_2N",
    "one-complete-two-node-S-H-prestate-with-strictly-positive-S1-HK-participation",
)
S1_JD_SCHEDULE = (
    (1, "A_BOUNDARY_2N", "A_ACTIVE_2N", "EMIT_COMPLETE_SH_CHECKPOINT_1"),
    (2, "A_BOUNDARY_2N", "A_ACTIVE_2N", "EMIT_COMPLETE_SH_CHECKPOINT_2"),
    (3, "A_BOUNDARY_2N", "A_ACTIVE_2N", "EMIT_COMPLETE_SH_CHECKPOINT_3"),
)
S1_JD_BOUNDARY_RULES = (
    "apply-one-bit-identical-two-node-S-H-boundary-to-DTS1-and-B1-through-B6-before-each-active-interval",
    "replace-only-S-H-while-preserving-DTS1-anatomy-B1-fixed-adapter-B2-L-and-B3-through-B6-M",
    "consume-zero-time-and-create-no-model-step-resource-transfer-or-checkpoint",
    "reject-boundary-values-dependent-on-model-checkpoint-result-hidden-state-or-future-state",
)
S1_JD_ACTIVE_INTERVAL_RULES = (
    "derive-DTS1-S1-HK-participation-and-current-adapter-after-the-common-boundary-from-one-closed-prestate",
    "deliver-one-identical-all-node-zero-receptor-contact-and-one-identical-positive-duration-to-all-seven-models",
    "advance-each-model-owned-state-only-through-its-registered-kernel-and-carry-the-complete-poststate",
    "emit-one-complete-S-H-checkpoint-after-each-interval-in-canonical-node-order",
    "apply-no-additional-S-H-boundary-at-private-internal-refinement-substeps",
)
S1_JD_PROFILE_RULES = (
    "P_IH-profile-is-signed-checkpoint-two-minus-one-followed-by-checkpoint-three-minus-one",
    "within-each-difference-order-is-two-S-values-then-two-H-values",
    "complete-P_IH-profile-width-is-eight-signed-components",
    "no-absolute-value-rescaling-checkpoint-fit-or-endpoint-only-substitution",
)
S1_JD_MODEL_RULES = (
    "DTS1-carries-only-its-complete-resource-anatomy-between-common-intervals",
    "B1-reuses-one-fixed-predivergence-adapter-and-has-no-evolving-hidden-state",
    "B2-carries-only-its-baseline-owned-L-state",
    "B3-through-B6-carry-only-their-respective-baseline-owned-M-state",
    "no-model-receives-another-models-hidden-state-participation-transfer-ledger-or-role-label",
)
S1_JD_CONTROL_RULES = (
    "B1-fixed-adapter-counterprediction-is-bit-identical-complete-checkpoints-after-identical-boundaries",
    "value-identical-sequence-repeat-must-be-bit-identical-per-model",
    "zero-DTS1-binding-control-must-remove-DTS1-engagement-without-changing-common-exposure",
    "zero-H-control-may-change-H-levels-but-must-not-create-a-private-history-input",
    "direct-P_IH-engagement-attenuation-ledger-remains-a-separate-hard-gate",
)
S1_JD_SUPERSESSION_RULES = (
    "supersede-only-the-old-P_IH-resource-only-history-plus-fresh-field-checkpoint-path-for-joint-comparison",
    "quarantine-old-P_IH-field-vectors-and-forbid-old-numeric-reuse",
    "retain-old-P_IH-direct-resource-ledgers-receipts-and-attenuation-direction",
    "preserve-P_IE-and-corrected-P_IK-P_IN-exposure-contracts",
)
S1_JD_FORBIDDEN_INTERPRETATIONS = (
    "selected-two-node-boundary-values-duration-tolerance-or-call-budget",
    "implemented-envelope-adapter-model-run-baseline-fit-or-candidate-superiority",
    "memory-learning-or-artificial-intelligence",
)
S1_JD_DECISION = "CORRECTED_COMMON_P_IH_THREE_INTERVAL_EXPOSURE_CONTRACT_BOUND_NO_VALUES_OR_EXECUTION"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JDCorrectedPIHExposureContract:
    contract_id: str
    source_s1jc_digest: str
    boundary_role: tuple[str, str]
    schedule: tuple[tuple[int, str, str, str], ...]
    boundary_rules: tuple[str, ...]
    active_interval_rules: tuple[str, ...]
    profile_rules: tuple[str, ...]
    model_rules: tuple[str, ...]
    control_rules: tuple[str, ...]
    supersession_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    interval_count: int
    checkpoint_count: int
    profile_component_count: int
    corrected_common_exposure_valid: bool
    old_resource_only_field_path_superseded: bool
    old_p_ih_field_vectors_quarantined: bool
    direct_p_ih_ledgers_retained: bool
    boundary_values_selected: bool
    duration_selected: bool
    tolerances_selected: bool
    call_budget_bound: bool
    two_node_boundary_implemented: bool
    common_interval_envelope_bound: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    finite_two_node_boundary_fixture_contract_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_JD_CONTRACT_ID
            or self.source_s1jc_digest != S1_JD_SOURCE_S1JC_DIGEST
            or self.boundary_role != S1_JD_BOUNDARY_ROLE
            or self.schedule != S1_JD_SCHEDULE
            or self.boundary_rules != S1_JD_BOUNDARY_RULES
            or self.active_interval_rules != S1_JD_ACTIVE_INTERVAL_RULES
            or self.profile_rules != S1_JD_PROFILE_RULES
            or self.model_rules != S1_JD_MODEL_RULES
            or self.control_rules != S1_JD_CONTROL_RULES
            or self.supersession_rules != S1_JD_SUPERSESSION_RULES
            or self.forbidden_interpretations != S1_JD_FORBIDDEN_INTERPRETATIONS
            or self.interval_count != 3
            or self.checkpoint_count != 3
            or self.profile_component_count != 8
            or any(
                value is not True
                for value in (
                    self.corrected_common_exposure_valid,
                    self.old_resource_only_field_path_superseded,
                    self.old_p_ih_field_vectors_quarantined,
                    self.direct_p_ih_ledgers_retained,
                    self.finite_two_node_boundary_fixture_contract_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.boundary_values_selected,
                    self.duration_selected,
                    self.tolerances_selected,
                    self.call_budget_bound,
                    self.two_node_boundary_implemented,
                    self.common_interval_envelope_bound,
                    self.adapters_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_JD_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JDCorrectedPIHExposureContractError(
                "S1-JD weakened the corrected common P_IH exposure contract"
            )


def build_dts1_s1jd_corrected_pih_exposure_contract() -> DTS1S1JDCorrectedPIHExposureContract:
    """Bind corrected common P_IH causality without values or execution."""

    source = build_dts1_s1jc_pih_exposure_assumption_precheck()
    values = {
        "contract_id": S1_JD_CONTRACT_ID,
        "source_s1jc_digest": source.audit_digest,
        "boundary_role": S1_JD_BOUNDARY_ROLE,
        "schedule": S1_JD_SCHEDULE,
        "boundary_rules": S1_JD_BOUNDARY_RULES,
        "active_interval_rules": S1_JD_ACTIVE_INTERVAL_RULES,
        "profile_rules": S1_JD_PROFILE_RULES,
        "model_rules": S1_JD_MODEL_RULES,
        "control_rules": S1_JD_CONTROL_RULES,
        "supersession_rules": S1_JD_SUPERSESSION_RULES,
        "forbidden_interpretations": S1_JD_FORBIDDEN_INTERPRETATIONS,
        "interval_count": len(S1_JD_SCHEDULE),
        "checkpoint_count": len(S1_JD_SCHEDULE),
        "profile_component_count": 8,
        "corrected_common_exposure_valid": True,
        "old_resource_only_field_path_superseded": True,
        "old_p_ih_field_vectors_quarantined": True,
        "direct_p_ih_ledgers_retained": True,
        "boundary_values_selected": False,
        "duration_selected": False,
        "tolerances_selected": False,
        "call_budget_bound": False,
        "two_node_boundary_implemented": False,
        "common_interval_envelope_bound": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "finite_two_node_boundary_fixture_contract_authorized_next_stage": True,
        "decision": S1_JD_DECISION,
    }
    return DTS1S1JDCorrectedPIHExposureContract(
        **values, contract_digest=_digest(values)
    )
