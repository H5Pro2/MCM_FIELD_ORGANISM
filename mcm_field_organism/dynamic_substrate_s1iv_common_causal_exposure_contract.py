"""Static S1-IV common causal exposure contract for P_IK and P_IN."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1iu_finite_binding_precheck import (
    build_dts1_s1iu_finite_binding_precheck,
)


class DTS1S1IVCommonCausalExposureContractError(ValueError):
    """Raised when the fair S1-IV exposure boundary is weakened."""


S1_IV_CONTRACT_ID = "dynamic-substrate.common-causal-exposure.s1iv.v1"
S1_IV_SOURCE_S1IU_DIGEST = (
    "e9323eab702148e4fc82262e2974e73696206c8614c7b80216d44f9b56901e65"
)
S1_IV_COMMON_EVENT_SCHEMA = (
    "one-model-neutral-exogenous-receptor-frame-with-canonical-node-order-and-no-model-state-coordinate",
    "one-positive-duration-with-explicit-start-end-and-common-checkpoint-boundaries",
    "one-role-from-A-exposure-B-exposure-gap-exposure-or-common-zero-contact-readout",
    "the-identical-event-payload-is-delivered-to-DTS1-B1-B2-B3-B4-B5-and-B6-for-the-same-arm",
    "each-model-derives-its-own-internal-response-only-from-the-event-and-its-carried-prestate",
)
S1_IV_P_IK_SCHEDULE = (
    ("ABA", 1, "A_EXPOSURE", "CARRY_COMPLETE_MODEL_STATE"),
    ("ABA", 2, "B_EXPOSURE", "CARRY_COMPLETE_MODEL_STATE"),
    ("ABA", 3, "A_EXPOSURE", "CARRY_COMPLETE_MODEL_STATE"),
    ("A_GAP_A", 1, "A_EXPOSURE", "CARRY_COMPLETE_MODEL_STATE"),
    ("A_GAP_A", 2, "GAP_EXPOSURE", "CARRY_COMPLETE_MODEL_STATE"),
    ("A_GAP_A", 3, "A_EXPOSURE", "CARRY_COMPLETE_MODEL_STATE"),
    ("BOTH", 4, "COMMON_SH_RESET", "PRESERVE_MODEL_OWNED_HIDDEN_STATE"),
    ("BOTH", 5, "COMMON_ZERO_CONTACT_READOUT", "CARRY_COMPLETE_MODEL_STATE"),
)
S1_IV_P_IN_SCHEDULE = (
    ("RECOVERY_ON", 1, "A_EXPOSURE", "CARRY_COMPLETE_MODEL_STATE"),
    ("RECOVERY_OFF", 1, "A_EXPOSURE", "CARRY_COMPLETE_MODEL_STATE"),
    ("RECOVERY_ON", 2, "GAP_EXPOSURE", "DTS1_RECOVERY_CHANNEL_ON_ONLY"),
    ("RECOVERY_OFF", 2, "GAP_EXPOSURE", "DTS1_RECOVERY_CHANNEL_OFF_ONLY"),
    ("BOTH", 3, "B_EXPOSURE", "CARRY_COMPLETE_MODEL_STATE"),
    ("BOTH", 4, "COMMON_SH_RESET", "PRESERVE_MODEL_OWNED_HIDDEN_STATE"),
    ("BOTH", 5, "COMMON_ZERO_CONTACT_READOUT", "CARRY_COMPLETE_MODEL_STATE"),
)
S1_IV_STATE_RULES = (
    "all-models-start-each-arm-from-one-bit-exact-common-S-H-prestate-and-their-preregistered-neutral-owned-state",
    "DTS1-carries-free-conductive-refractory-B1-carries-one-fixed-adapter-B2-carries-L-and-B3-through-B6-carry-M",
    "no-model-state-is-reset-merged-copied-between-models-or-reconstructed-from-another-model-during-exposure",
    "the-common-pre-readout-reset-overwrites-only-exposed-S-H-with-one-arm-identical-preregistered-probe-prestate",
    "the-common-reset-preserves-DTS1-anatomy-B1-fixed-adapter-B2-L-and-B3-through-B6-M-bit-for-bit",
    "the-final-zero-contact-readout-starts-only-after-the-common-reset-and-uses-one-identical-positive-duration",
)
S1_IV_INTERVENTION_RULES = (
    "P_IK-arm-difference-is-only-the-model-neutral-middle-B-versus-gap-exogenous-event",
    "P_IN-exogenous-A-gap-B-events-are-arm-identical-and-only-the-DTS1-recovery-channel-is-on-versus-off",
    "B1-through-B6-receive-no-analogue-of-the-DTS1-specific-recovery-switch-and-remain-configuration-identical-between-P_IN-arms",
    "DTS1-edge-participation-is-derived-only-inside-DTS1-from-its-own-current-field-via-the-bound-S1-HK-observable",
    "no-baseline-receives-DTS1-participation-resource-ledgers-recovery-state-or-intervention-label",
)
S1_IV_PROFILE_DISPOSITION = (
    ("P_IE_CAUSAL_TWO_SUBSTEP", "RETAIN_EXISTING_PROFILE_AND_RECEIPT"),
    ("P_IH_ATTENUATION", "RETAIN_EXISTING_PROFILE_AND_RECEIPT"),
    ("P_IK_INTERFERENCE", "QUARANTINE_OLD_FIELD_VECTOR_RETAIN_DIRECT_LEDGERS_REREGISTER_PROFILE"),
    ("P_IN_RELEASE_REUSE", "QUARANTINE_OLD_FIELD_VECTOR_RETAIN_DIRECT_LEDGERS_REREGISTER_PROFILE"),
)
S1_IV_REREGISTRATION_RULES = (
    "new-P_IK-and-P_IN-field-profiles-must-use-the-common-event-schema-and-bound-schedules-without-reusing-old-numeric-vectors",
    "old-P_IK-and-P_IN-direct-resource-ledgers-receipts-and-functional-directions-remain-evidence-but-not-new-profile-values",
    "the-future-joint-profile-keeps-8-8-6-6-structure-but-the-final-two-six-component-blocks-require-new-receipts",
    "new-event-values-durations-reset-prestate-tolerances-and-call-budgets-must-be-preregistered-before-implementation",
    "failure-to-realize-one-common-event-for-every-model-is-STOPP-not-a-license-to-drop-or-repair-a-baseline",
)
S1_IV_FORBIDDEN_INTERPRETATIONS = (
    "reuse-equivalence-or-validity-of-the-old-P_IK-or-P_IN-field-vectors-for-joint-baseline-comparison",
    "baseline-fit-baseline-rejection-baseline-closure-candidate-superiority-or-functional-confirmation",
    "memory-learning-semantics-inner-context-organization-self-regulation-organism-or-artificial-intelligence",
)
S1_IV_DECISION = "COMMON_CAUSAL_EXPOSURE_BOUND_P_IK_P_IN_CONTROLLED_REREGISTRATION_REQUIRED"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IVCommonCausalExposureContract:
    contract_id: str
    source_s1iu_digest: str
    common_event_schema: tuple[str, ...]
    p_ik_schedule: tuple[tuple[str, int, str, str], ...]
    p_in_schedule: tuple[tuple[str, int, str, str], ...]
    state_rules: tuple[str, ...]
    intervention_rules: tuple[str, ...]
    profile_disposition: tuple[tuple[str, str], ...]
    reregistration_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    old_profile_blocks_retained: int
    old_field_blocks_quarantined: int
    direct_ledger_blocks_retained: int
    future_profile_component_count: int
    exposure_values_selected: bool
    durations_selected: bool
    reset_prestate_selected: bool
    configuration_values_selected: bool
    configuration_digests_bound: bool
    fixture_implemented: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    finite_exposure_fixture_contract_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_IV_CONTRACT_ID
            or self.source_s1iu_digest != S1_IV_SOURCE_S1IU_DIGEST
            or self.common_event_schema != S1_IV_COMMON_EVENT_SCHEMA
            or self.p_ik_schedule != S1_IV_P_IK_SCHEDULE
            or self.p_in_schedule != S1_IV_P_IN_SCHEDULE
            or self.state_rules != S1_IV_STATE_RULES
            or self.intervention_rules != S1_IV_INTERVENTION_RULES
            or self.profile_disposition != S1_IV_PROFILE_DISPOSITION
            or self.reregistration_rules != S1_IV_REREGISTRATION_RULES
            or self.forbidden_interpretations != S1_IV_FORBIDDEN_INTERPRETATIONS
            or self.old_profile_blocks_retained != 2
            or self.old_field_blocks_quarantined != 2
            or self.direct_ledger_blocks_retained != 2
            or self.future_profile_component_count != 28
            or any(
                value is not False
                for value in (
                    self.exposure_values_selected,
                    self.durations_selected,
                    self.reset_prestate_selected,
                    self.configuration_values_selected,
                    self.configuration_digests_bound,
                    self.fixture_implemented,
                    self.adapters_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.finite_exposure_fixture_contract_authorized_next_stage is not True
            or self.decision != S1_IV_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IVCommonCausalExposureContractError(
                "S1-IV weakened the fair causal exposure boundary"
            )


def build_dts1_s1iv_common_causal_exposure_contract() -> DTS1S1IVCommonCausalExposureContract:
    """Bind fair histories and quarantine non-equivalent old field profiles."""

    source = build_dts1_s1iu_finite_binding_precheck()
    values = {
        "contract_id": S1_IV_CONTRACT_ID,
        "source_s1iu_digest": source.audit_digest,
        "common_event_schema": S1_IV_COMMON_EVENT_SCHEMA,
        "p_ik_schedule": S1_IV_P_IK_SCHEDULE,
        "p_in_schedule": S1_IV_P_IN_SCHEDULE,
        "state_rules": S1_IV_STATE_RULES,
        "intervention_rules": S1_IV_INTERVENTION_RULES,
        "profile_disposition": S1_IV_PROFILE_DISPOSITION,
        "reregistration_rules": S1_IV_REREGISTRATION_RULES,
        "forbidden_interpretations": S1_IV_FORBIDDEN_INTERPRETATIONS,
        "old_profile_blocks_retained": 2,
        "old_field_blocks_quarantined": 2,
        "direct_ledger_blocks_retained": 2,
        "future_profile_component_count": 28,
        "exposure_values_selected": False,
        "durations_selected": False,
        "reset_prestate_selected": False,
        "configuration_values_selected": False,
        "configuration_digests_bound": False,
        "fixture_implemented": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "finite_exposure_fixture_contract_authorized_next_stage": True,
        "decision": S1_IV_DECISION,
    }
    return DTS1S1IVCommonCausalExposureContract(
        **values, contract_digest=_digest(values)
    )
