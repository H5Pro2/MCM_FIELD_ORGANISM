"""Static S1-IX corrected event-boundary contract for fair exposure."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1iw_exposure_ordering_precheck import (
    build_dts1_s1iw_exposure_ordering_precheck,
)


class DTS1S1IXCorrectedEventBoundaryContractError(ValueError):
    """Raised when the corrected S1-IX boundary semantics are weakened."""


S1_IX_CONTRACT_ID = "dynamic-substrate.corrected-common-event-boundaries.s1ix.v1"
S1_IX_SOURCE_S1IW_DIGEST = (
    "c3cb4826421b34129af5b3d412be853f23a67bac7dd2e3a88ae434f1c8a88c89"
)
S1_IX_BOUNDARY_ROLES = (
    ("A_BOUNDARY", "positive-S1-HK-participation-on-A-and-exact-zero-on-B"),
    ("B_BOUNDARY", "exact-zero-S1-HK-participation-on-A-and-positive-on-B"),
    ("GAP_BOUNDARY", "exact-zero-S1-HK-participation-on-A-and-B"),
    ("PROBE_BOUNDARY", "one-arm-identical-complete-S-H-readout-prestate"),
)
S1_IX_BOUNDARY_OPERATOR_RULES = (
    "accept-one-complete-valid-model-state-and-one-preregistered-boundary-role",
    "replace-only-the-exposed-three-node-S-H-vectors-with-the-role-bound-canonical-vectors",
    "apply-the-bit-identical-S-H-vectors-to-DTS1-B1-B2-B3-B4-B5-and-B6-for-the-same-role-and-arm",
    "preserve-DTS1-anatomy-B1-fixed-adapter-B2-L-and-B3-through-B6-M-bit-for-bit",
    "consume-zero-time-call-no-model-equation-and-create-no-resource-transfer-field-step-or-checkpoint",
    "reject-any-arm-case-model-result-future-state-or-hidden-coordinate-dependent-boundary-vector",
)
S1_IX_ACTIVE_INTERVAL_RULES = (
    "derive-DTS1-S1-HK-participation-from-the-clamped-S-prestate-before-each-resource-active-interval",
    "start-every-model-from-the-corresponding-clamped-S-H-prestate-and-its-own-preserved-hidden-state",
    "use-one-model-neutral-all-node-zero-receptor-contact-throughout-each-positive-active-interval",
    "carry-only-model-owned-hidden-state-across-the-next-boundary-while-the-next-boundary-replaces-S-H",
    "record-complete-preboundary-postboundary-postinterval-S-H-and-hidden-state-digests",
)
S1_IX_P_IK_SCHEDULE = (
    ("ABA", 1, "A_BOUNDARY", "A_ACTIVE"),
    ("ABA", 2, "B_BOUNDARY", "B_ACTIVE"),
    ("ABA", 3, "A_BOUNDARY", "A_ACTIVE"),
    ("A_GAP_A", 1, "A_BOUNDARY", "A_ACTIVE"),
    ("A_GAP_A", 2, "GAP_BOUNDARY", "GAP_ACTIVE"),
    ("A_GAP_A", 3, "A_BOUNDARY", "A_ACTIVE"),
    ("BOTH", 4, "PROBE_BOUNDARY", "COMMON_ZERO_CONTACT_READOUT"),
)
S1_IX_P_IN_SCHEDULE = (
    ("RECOVERY_ON", 1, "A_BOUNDARY", "A_ACTIVE"),
    ("RECOVERY_OFF", 1, "A_BOUNDARY", "A_ACTIVE"),
    ("RECOVERY_ON", 2, "GAP_BOUNDARY", "GAP_ACTIVE_RECOVERY_ON"),
    ("RECOVERY_OFF", 2, "GAP_BOUNDARY", "GAP_ACTIVE_RECOVERY_OFF"),
    ("RECOVERY_ON", 3, "B_BOUNDARY", "B_ACTIVE"),
    ("RECOVERY_OFF", 3, "B_BOUNDARY", "B_ACTIVE"),
    ("BOTH", 4, "PROBE_BOUNDARY", "COMMON_ZERO_CONTACT_READOUT"),
)
S1_IX_INTERVENTION_RULES = (
    "P_IK-only-the-middle-B-versus-gap-boundary-role-differs-between-arms",
    "P_IN-all-boundary-roles-and-zero-contacts-are-arm-identical",
    "P_IN-only-the-internal-DTS1-recovery-channel-differs-during-the-gap-active-interval",
    "B1-through-B6-remain-parameter-and-configuration-identical-between-P_IN-arms",
    "no-baseline-receives-the-DTS1-recovery-switch-participation-or-resource-state",
)
S1_IX_PRESERVED_S1IV_RULES = (
    "model-neutral-delivery-to-DTS1-and-all-six-baselines",
    "separate-common-probe-boundary-and-zero-contact-readout",
    "P_IE-and-P_IH-existing-profile-retention",
    "old-P_IK-and-P_IN-field-vector-quarantine-with-direct-ledger-retention",
    "controlled-P_IK-and-P_IN-profile-reregistration-without-old-numeric-reuse",
)
S1_IX_FORBIDDEN_INTERPRETATIONS = (
    "selected-boundary-values-durations-parameters-or-numerical-admissibility",
    "implemented-runtime-ready-or-executed-boundary-operator",
    "baseline-fit-baseline-rejection-baseline-closure-candidate-superiority-memory-learning-or-artificial-intelligence",
)
S1_IX_DECISION = "CORRECTED_COMMON_SH_BOUNDARY_EXPOSURE_CONTRACT_BOUND_NO_VALUES_OR_EXECUTION"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IXCorrectedEventBoundaryContract:
    contract_id: str
    source_s1iw_digest: str
    boundary_roles: tuple[tuple[str, str], ...]
    boundary_operator_rules: tuple[str, ...]
    active_interval_rules: tuple[str, ...]
    p_ik_schedule: tuple[tuple[str, int, str, str], ...]
    p_in_schedule: tuple[tuple[str, int, str, str], ...]
    intervention_rules: tuple[str, ...]
    preserved_s1iv_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    boundary_role_count: int
    old_within_history_sh_carry_rule_superseded: bool
    temporal_alignment_contract_valid: bool
    boundary_values_selected: bool
    durations_selected: bool
    configuration_values_selected: bool
    configuration_digests_bound: bool
    boundary_operator_implemented: bool
    fixtures_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    finite_boundary_fixture_contract_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_IX_CONTRACT_ID
            or self.source_s1iw_digest != S1_IX_SOURCE_S1IW_DIGEST
            or self.boundary_roles != S1_IX_BOUNDARY_ROLES
            or self.boundary_operator_rules != S1_IX_BOUNDARY_OPERATOR_RULES
            or self.active_interval_rules != S1_IX_ACTIVE_INTERVAL_RULES
            or self.p_ik_schedule != S1_IX_P_IK_SCHEDULE
            or self.p_in_schedule != S1_IX_P_IN_SCHEDULE
            or self.intervention_rules != S1_IX_INTERVENTION_RULES
            or self.preserved_s1iv_rules != S1_IX_PRESERVED_S1IV_RULES
            or self.forbidden_interpretations != S1_IX_FORBIDDEN_INTERPRETATIONS
            or self.boundary_role_count != 4
            or self.old_within_history_sh_carry_rule_superseded is not True
            or self.temporal_alignment_contract_valid is not True
            or any(
                value is not False
                for value in (
                    self.boundary_values_selected,
                    self.durations_selected,
                    self.configuration_values_selected,
                    self.configuration_digests_bound,
                    self.boundary_operator_implemented,
                    self.fixtures_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.finite_boundary_fixture_contract_authorized_next_stage is not True
            or self.decision != S1_IX_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IXCorrectedEventBoundaryContractError(
                "S1-IX weakened the corrected event-boundary contract"
            )


def build_dts1_s1ix_corrected_event_boundary_contract() -> DTS1S1IXCorrectedEventBoundaryContract:
    """Bind aligned boundary roles without selecting vectors or executing models."""

    source = build_dts1_s1iw_exposure_ordering_precheck()
    values = {
        "contract_id": S1_IX_CONTRACT_ID,
        "source_s1iw_digest": source.audit_digest,
        "boundary_roles": S1_IX_BOUNDARY_ROLES,
        "boundary_operator_rules": S1_IX_BOUNDARY_OPERATOR_RULES,
        "active_interval_rules": S1_IX_ACTIVE_INTERVAL_RULES,
        "p_ik_schedule": S1_IX_P_IK_SCHEDULE,
        "p_in_schedule": S1_IX_P_IN_SCHEDULE,
        "intervention_rules": S1_IX_INTERVENTION_RULES,
        "preserved_s1iv_rules": S1_IX_PRESERVED_S1IV_RULES,
        "forbidden_interpretations": S1_IX_FORBIDDEN_INTERPRETATIONS,
        "boundary_role_count": len(S1_IX_BOUNDARY_ROLES),
        "old_within_history_sh_carry_rule_superseded": True,
        "temporal_alignment_contract_valid": True,
        "boundary_values_selected": False,
        "durations_selected": False,
        "configuration_values_selected": False,
        "configuration_digests_bound": False,
        "boundary_operator_implemented": False,
        "fixtures_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "finite_boundary_fixture_contract_authorized_next_stage": True,
        "decision": S1_IX_DECISION,
    }
    return DTS1S1IXCorrectedEventBoundaryContract(
        **values, contract_digest=_digest(values)
    )
