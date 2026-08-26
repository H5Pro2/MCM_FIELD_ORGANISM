"""Static S1-IU precheck for finite DTS-1 baseline adapter binding."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1it_private_adapter_contract import (
    build_dts1_s1it_private_adapter_contract,
)


class DTS1S1IUFiniteBindingPrecheckError(ValueError):
    """Raised when the fail-closed S1-IU exposure check is weakened."""


S1_IU_AUDIT_ID = "dynamic-substrate.finite-adapter-binding-precheck.s1iu.v1"
S1_IU_SOURCE_S1IT_DIGEST = (
    "942373dd7605c8b8054c1b188d99fce47145d7894e7521bad81c2b9065facac4"
)
S1_IU_EXPOSURE_RECORDS = (
    (
        "P_IE_CAUSAL_TWO_SUBSTEP",
        "two-coupled-S-H-field-intervals-with-explicit-zero-receptor-contact-and-carried-field-state",
        "COMMON_CAUSAL_FIELD_SCHEDULE_BOUND",
    ),
    (
        "P_IH_ATTENUATION",
        "three-coupled-S-H-field-intervals-with-explicit-zero-receptor-contact-and-carried-field-state",
        "COMMON_CAUSAL_FIELD_SCHEDULE_BOUND",
    ),
    (
        "P_IK_INTERFERENCE",
        "three-resource-only-A-B-or-gap-A-participation-intervals-then-one-fresh-S-H-zero-contact-readout",
        "BLOCKED_COMMON_BASELINE_CAUSAL_EXPOSURE_UNBOUND",
    ),
    (
        "P_IN_RELEASE_REUSE",
        "three-resource-only-A-load-zero-window-B-probe-intervals-then-one-fresh-S-H-zero-contact-readout",
        "BLOCKED_COMMON_BASELINE_CAUSAL_EXPOSURE_UNBOUND",
    ),
)
S1_IU_BLOCKING_FACTS = (
    "P_IK-A-B-gap-and-final-A-history-is-supplied-as-DTS1-edge-participation-not-as-a-common-field-or-receptor-schedule",
    "P_IN-A-load-gap-and-B-probe-history-is-supplied-as-DTS1-edge-participation-not-as-a-common-field-or-receptor-schedule",
    "P_IK-and-P_IN-field-readouts-create-fresh-common-S-H-prestates-and-expose-only-one-final-zero-contact-interval",
    "DTS1-edge-participation-and-resource-history-are-forbidden-baseline-inputs-under-S1-IR-and-S1-IT",
    "a-final-fresh-zero-contact-probe-alone-is-not-the-complete-causal-exposure-for-stateful-B2-through-B6",
)
S1_IU_STOPP_RULES = (
    "do-not-invent-map-or-fit-receptor-histories-from-DTS1-participation-after-observing-the-recorded-results",
    "do-not-pass-DTS1-participation-resource-state-arm-label-or-result-data-to-any-baseline",
    "do-not-count-identical-final-probe-only-outputs-as-a-joint-dynamic-baseline-comparison",
    "do-not-bind-configuration-values-digests-refinement-or-a-24-case-matrix-before-all-four-common-exposures-are-valid",
    "one-block-without-common-causal-exposure-invalidates-the-complete-finite-binding-stage",
)
S1_IU_FORBIDDEN_INTERPRETATIONS = (
    "kernel-incompatibility-baseline-rejection-baseline-closure-or-candidate-superiority",
    "invalidity-of-the-existing-direct-interference-release-or-reuse-ledgers",
    "memory-learning-semantics-inner-context-organization-self-regulation-organism-or-artificial-intelligence",
)
S1_IU_DECISION = "STOPP_P_IK_P_IN_COMMON_CAUSAL_BASELINE_EXPOSURE_UNBOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IUFiniteBindingPrecheck:
    audit_id: str
    source_s1it_digest: str
    exposure_records: tuple[tuple[str, str, str], ...]
    blocking_facts: tuple[str, ...]
    stopp_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    planned_adapter_case_count: int
    ready_adapter_case_count: int
    blocked_adapter_case_count: int
    common_exposure_contract_valid: bool
    parameter_values_selected: bool
    configuration_digests_bound: bool
    refinements_selected: bool
    finite_case_matrix_bound: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    common_exposure_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_IU_AUDIT_ID
            or self.source_s1it_digest != S1_IU_SOURCE_S1IT_DIGEST
            or self.exposure_records != S1_IU_EXPOSURE_RECORDS
            or self.blocking_facts != S1_IU_BLOCKING_FACTS
            or self.stopp_rules != S1_IU_STOPP_RULES
            or self.forbidden_interpretations != S1_IU_FORBIDDEN_INTERPRETATIONS
            or self.planned_adapter_case_count != 24
            or self.ready_adapter_case_count != 12
            or self.blocked_adapter_case_count != 12
            or any(
                value is not False
                for value in (
                    self.common_exposure_contract_valid,
                    self.parameter_values_selected,
                    self.configuration_digests_bound,
                    self.refinements_selected,
                    self.finite_case_matrix_bound,
                    self.adapters_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.common_exposure_contract_authorized_next_stage is not True
            or self.decision != S1_IU_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1IUFiniteBindingPrecheckError(
                "S1-IU weakened the common-exposure STOPP"
            )


def build_dts1_s1iu_finite_binding_precheck() -> DTS1S1IUFiniteBindingPrecheck:
    """Stop finite binding before values when common causal exposure is absent."""

    source = build_dts1_s1it_private_adapter_contract()
    ready_blocks = sum(row[2] == "COMMON_CAUSAL_FIELD_SCHEDULE_BOUND" for row in S1_IU_EXPOSURE_RECORDS)
    values = {
        "audit_id": S1_IU_AUDIT_ID,
        "source_s1it_digest": source.contract_digest,
        "exposure_records": S1_IU_EXPOSURE_RECORDS,
        "blocking_facts": S1_IU_BLOCKING_FACTS,
        "stopp_rules": S1_IU_STOPP_RULES,
        "forbidden_interpretations": S1_IU_FORBIDDEN_INTERPRETATIONS,
        "planned_adapter_case_count": source.adapter_role_count * len(S1_IU_EXPOSURE_RECORDS),
        "ready_adapter_case_count": source.adapter_role_count * ready_blocks,
        "blocked_adapter_case_count": source.adapter_role_count * (len(S1_IU_EXPOSURE_RECORDS) - ready_blocks),
        "common_exposure_contract_valid": False,
        "parameter_values_selected": False,
        "configuration_digests_bound": False,
        "refinements_selected": False,
        "finite_case_matrix_bound": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "common_exposure_contract_authorized_next_stage": True,
        "decision": S1_IU_DECISION,
    }
    return DTS1S1IUFiniteBindingPrecheck(**values, audit_digest=_digest(values))
