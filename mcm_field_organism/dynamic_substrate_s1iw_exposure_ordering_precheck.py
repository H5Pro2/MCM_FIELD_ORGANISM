"""Static S1-IW ordering precheck before finite causal exposure binding."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1iv_common_causal_exposure_contract import (
    build_dts1_s1iv_common_causal_exposure_contract,
)


class DTS1S1IWExposureOrderingPrecheckError(ValueError):
    """Raised when the fail-closed S1-IW ordering result is weakened."""


S1_IW_AUDIT_ID = "dynamic-substrate.exposure-ordering-precheck.s1iw.v1"
S1_IW_SOURCE_S1IV_DIGEST = (
    "9242aa71d086b7c0cde86aa1327e502b65700383d886eb7d93812a58478ec92c"
)
S1_IW_COUPLED_STEP_ORDER = (
    "validate-complete-closed-field-anatomy-distribution-time-and-config-inputs",
    "derive-one-fixed-or-dynamic-edge-rate-adapter-from-the-closed-anatomy-prestate",
    "derive-S1-HK-edge-participation-from-the-closed-S-field-prestate",
    "commit-the-DTS1-resource-step-for-the-full-interval-from-that-prestate-participation",
    "only-after-resource-commit-advance-S-H-through-the-current-receptor-distribution",
)
S1_IW_MISALIGNMENT_RECORDS = (
    (
        "P_IK_INTERFERENCE",
        "middle-B-or-gap-receptor-payload-cannot-affect-DTS1-participation-until-the-following-A-labelled-interval",
    ),
    (
        "P_IN_RELEASE_REUSE",
        "final-B-receptor-payload-cannot-affect-DTS1-resource-state-before-the-immediate-common-SH-reset-and-readout",
    ),
)
S1_IW_BLOCKING_RULES = (
    "an-exposure-role-may-not-be-defined-by-a-receptor-payload-that-the-DTS1-resource-update-has-not-yet-seen",
    "changing-contact-amplitude-duration-or-tolerance-cannot-reverse-the-bound-prestate-before-payload-order",
    "a-one-interval-label-shift-is-not-a-shape-adapter-and-may-not-be-applied-silently",
    "baseline-continuous-state-updates-and-DTS1-closed-prestate-resource-updates-must-share-an-explicit-event-boundary-semantics",
    "no-finite-fixture-value-configuration-digest-or-call-matrix-may-be-bound-until-the-event-boundary-is-corrected",
)
S1_IW_CORRECTION_REQUIREMENTS = (
    "bind-one-model-neutral-common-S-H-boundary-clamp-before-each-A-B-or-gap-resource-active-interval",
    "apply-the-same-clamped-S-H-boundary-to-DTS1-and-B1-through-B6-while-preserving-each-model-owned-hidden-state",
    "derive-DTS1-participation-only-after-the-common-clamp-and-before-the-resource-active-interval",
    "keep-the-separate-common-pre-readout-S-H-reset-and-zero-contact-readout-from-S1-IV",
    "supersede-only-the-S1-IV-within-history-S-H-carry-rule-not-its-model-neutrality-intervention-or-profile-quarantine-rules",
)
S1_IW_FORBIDDEN_INTERPRETATIONS = (
    "kernel-incompatibility-baseline-rejection-baseline-closure-or-candidate-superiority",
    "invalidity-of-existing-direct-ledgers-or-the-S1-HK-participation-observable",
    "memory-learning-semantics-inner-context-organization-self-regulation-organism-or-artificial-intelligence",
)
S1_IW_DECISION = "STOPP_S1IV_EVENT_LABEL_DTS1_PARTICIPATION_TEMPORAL_MISALIGNMENT"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IWExposureOrderingPrecheck:
    audit_id: str
    source_s1iv_digest: str
    coupled_step_order: tuple[str, ...]
    misalignment_records: tuple[tuple[str, str], ...]
    blocking_rules: tuple[str, ...]
    correction_requirements: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    affected_profile_block_count: int
    event_boundary_contract_valid: bool
    exposure_values_selected: bool
    durations_selected: bool
    reset_prestates_selected: bool
    configuration_values_selected: bool
    configuration_digests_bound: bool
    finite_case_matrix_bound: bool
    fixture_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    corrected_event_boundary_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_IW_AUDIT_ID
            or self.source_s1iv_digest != S1_IW_SOURCE_S1IV_DIGEST
            or self.coupled_step_order != S1_IW_COUPLED_STEP_ORDER
            or self.misalignment_records != S1_IW_MISALIGNMENT_RECORDS
            or self.blocking_rules != S1_IW_BLOCKING_RULES
            or self.correction_requirements != S1_IW_CORRECTION_REQUIREMENTS
            or self.forbidden_interpretations != S1_IW_FORBIDDEN_INTERPRETATIONS
            or self.affected_profile_block_count != 2
            or any(
                value is not False
                for value in (
                    self.event_boundary_contract_valid,
                    self.exposure_values_selected,
                    self.durations_selected,
                    self.reset_prestates_selected,
                    self.configuration_values_selected,
                    self.configuration_digests_bound,
                    self.finite_case_matrix_bound,
                    self.fixture_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.corrected_event_boundary_contract_authorized_next_stage is not True
            or self.decision != S1_IW_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1IWExposureOrderingPrecheckError(
                "S1-IW weakened the temporal-alignment STOPP"
            )


def build_dts1_s1iw_exposure_ordering_precheck() -> DTS1S1IWExposureOrderingPrecheck:
    """Stop finite value binding when event labels lag DTS-1 participation."""

    source = build_dts1_s1iv_common_causal_exposure_contract()
    values = {
        "audit_id": S1_IW_AUDIT_ID,
        "source_s1iv_digest": source.contract_digest,
        "coupled_step_order": S1_IW_COUPLED_STEP_ORDER,
        "misalignment_records": S1_IW_MISALIGNMENT_RECORDS,
        "blocking_rules": S1_IW_BLOCKING_RULES,
        "correction_requirements": S1_IW_CORRECTION_REQUIREMENTS,
        "forbidden_interpretations": S1_IW_FORBIDDEN_INTERPRETATIONS,
        "affected_profile_block_count": len(S1_IW_MISALIGNMENT_RECORDS),
        "event_boundary_contract_valid": False,
        "exposure_values_selected": False,
        "durations_selected": False,
        "reset_prestates_selected": False,
        "configuration_values_selected": False,
        "configuration_digests_bound": False,
        "finite_case_matrix_bound": False,
        "fixture_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "corrected_event_boundary_contract_authorized_next_stage": True,
        "decision": S1_IW_DECISION,
    }
    return DTS1S1IWExposureOrderingPrecheck(**values, audit_digest=_digest(values))
