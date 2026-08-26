"""Static S1-JJ compatibility precheck of the S1-JH interval clock."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1ji_materialization_readiness_precheck import (
    build_dts1_s1ji_materialization_readiness_precheck,
)


class DTS1S1JJIntervalClockCompatibilityPrecheckError(ValueError):
    """Raised when the fail-closed S1-JJ clock finding is weakened."""


S1_JJ_AUDIT_ID = "dynamic-substrate.interval-clock-compatibility.s1jj.v1"
S1_JJ_SOURCE_S1JI_DIGEST = (
    "652fea995a72b1dd8b7ed0ae4845a43dfd36327402206c25516db5d787c60b30"
)
S1_JJ_S1JH_CLOCK_FACTS = (
    ("clock_id", "mcm.s1jh.common.interval"),
    ("start_tick", 0),
    ("end_tick", 1),
    ("ticks_per_second", 2.0),
    ("elapsed_synthetic_time", 0.5),
    ("same_complete_step_time_repeated_in_all_twenty_three_envelopes", True),
)
S1_JJ_RUNTIME_INVARIANTS = (
    "a-carried-SharedMCMField-retains-the-last-completed-ReceptorDistribution",
    "the-S1-IZ-and-S1-JF-boundary-operators-preserve-last_distribution-by-identity",
    "the-next-distribution-must-use-the-same-common-field-clock-as-the-carried-field",
    "the-next-window_end_tick-must-be-strictly-greater-than-the-carried-window_end_tick",
    "MCMFieldStepTime-must-equal-the-current-ReceptorDistribution-field-window",
)
S1_JJ_SEQUENCE_IMPACT = (
    ("P_IE_F_HIGH", 2, 1),
    ("P_IE_R_HIGH", 2, 1),
    ("P_IH_A_A_A", 3, 2),
    ("P_IK_A_B_A", 4, 3),
    ("P_IK_A_GAP_A", 4, 3),
    ("P_IN_RECOVERY_ON", 4, 3),
    ("P_IN_RECOVERY_OFF", 4, 3),
)
S1_JJ_FAILURE_CHAIN = (
    "the-first-interval-may-complete-with-last-window-end-tick-one",
    "the-second-envelope-again-presents-window-zero-through-one",
    "its-window-end-tick-one-is-not-greater-than-the-carried-end-tick-one",
    "SharedMCMField-therefore-rejects-before-any-valid-second-transition",
    "boundary-reset-of-only-S-H-cannot-remove-or-rewrite-this-time-history",
)
S1_JJ_PRESERVED_BINDINGS = (
    "all-two-and-three-node-geometries-and-canonical-node-orders",
    "all-P_IE-initial-P_IH-two-node-and-P_IK-P_IN-three-node-S-H-values",
    "all-width-specific-zero-contact-values-and-source-contact-identities",
    "all-candidate-sidecars-refinement-levels-call-budgets-and-quarantine-rules",
    "the-S1-JG-information-barrier-and-value-identical-cross-model-delivery",
)
S1_JJ_SUPERSEDED_BINDINGS = (
    "the-single-repeated-zero-to-one-common-step-time-for-every-envelope",
    "all-S1-JH-sequence-digests-that-commit-to-that-repeated-step-time",
    "all-S1-JH-interval-digests-that-commit-to-that-repeated-step-time",
    "the-S1-JH-claim-that-time-values-are-ready-for-materialization",
)
S1_JJ_CORRECTION_REQUIREMENTS = (
    "bind-one-contiguous-sequence-relative-half-unit-window-per-ordinal",
    "use-zero-to-one-one-to-two-and-so-on-at-two-ticks-per-synthetic-time-unit",
    "restart-only-when-a-new-independent-sequence-and-model-state-begins",
    "deliver-the-same-ordinal-window-to-DTS1-and-B1-through-B6-without-an-explicit-ordinal-label",
    "recompute-all-time-dependent-sequence-and-interval-digests-before-materialization-schema-binding",
)
S1_JJ_FORBIDDEN_SHORTCUTS = (
    "do-not-clear-last_distribution-between-carried-intervals",
    "do-not-change-the-clock-id-or-rewind-ticks-inside-one-sequence",
    "do-not-hide-causal-time-from-a-model-that-requires-it-for-the-common-transition",
    "do-not-special-case-DTS1-or-any-baseline-with-a-private-time-schedule",
    "do-not-reuse-the-invalid-S1-JH-time-dependent-digests",
)
S1_JJ_FORBIDDEN_INTERPRETATIONS = (
    "the-preserved-S1-JH-geometries-S-H-values-contacts-sidecars-or-budgets-are-rejected",
    "a-model-adapter-baseline-or-common-envelope-was-implemented-or-executed",
    "baseline-closure-candidate-superiority-memory-learning-or-artificial-intelligence",
)
S1_JJ_DECISION = (
    "STOPP_S1JH_REPEATED_INTERVAL_CLOCK_INCOMPATIBLE_WITH_CARRIED_FIELD_TIME"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JJIntervalClockCompatibilityPrecheck:
    audit_id: str
    source_s1ji_digest: str
    s1jh_clock_facts: tuple[tuple[str, object], ...]
    runtime_invariants: tuple[str, ...]
    sequence_impact: tuple[tuple[str, int, int], ...]
    failure_chain: tuple[str, ...]
    preserved_bindings: tuple[str, ...]
    superseded_bindings: tuple[str, ...]
    correction_requirements: tuple[str, ...]
    forbidden_shortcuts: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    affected_sequence_count: int
    incompatible_continuation_envelopes_per_model_per_refinement: int
    baseline_case_count_still_blocked: int
    s1jh_time_schedule_materializable: bool
    non_time_s1jh_bindings_preserved: bool
    materialization_schema_bound: bool
    common_interval_fixture_implemented: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    corrected_monotonic_clock_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_JJ_AUDIT_ID
            or self.source_s1ji_digest != S1_JJ_SOURCE_S1JI_DIGEST
            or self.s1jh_clock_facts != S1_JJ_S1JH_CLOCK_FACTS
            or self.runtime_invariants != S1_JJ_RUNTIME_INVARIANTS
            or self.sequence_impact != S1_JJ_SEQUENCE_IMPACT
            or self.failure_chain != S1_JJ_FAILURE_CHAIN
            or self.preserved_bindings != S1_JJ_PRESERVED_BINDINGS
            or self.superseded_bindings != S1_JJ_SUPERSEDED_BINDINGS
            or self.correction_requirements != S1_JJ_CORRECTION_REQUIREMENTS
            or self.forbidden_shortcuts != S1_JJ_FORBIDDEN_SHORTCUTS
            or self.forbidden_interpretations != S1_JJ_FORBIDDEN_INTERPRETATIONS
            or self.affected_sequence_count != 7
            or self.incompatible_continuation_envelopes_per_model_per_refinement
            != 16
            or self.baseline_case_count_still_blocked != 24
            or self.s1jh_time_schedule_materializable is not False
            or self.non_time_s1jh_bindings_preserved is not True
            or self.materialization_schema_bound is not False
            or self.common_interval_fixture_implemented is not False
            or self.adapters_implemented is not False
            or self.baseline_models_executed is not False
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.corrected_monotonic_clock_contract_authorized_next_stage
            is not True
            or self.decision != S1_JJ_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1JJIntervalClockCompatibilityPrecheckError(
                "S1-JJ weakened the repeated-clock compatibility STOPP"
            )


def build_dts1_s1jj_interval_clock_compatibility_precheck(
) -> DTS1S1JJIntervalClockCompatibilityPrecheck:
    """Stop schema binding when carried field time cannot advance."""

    source = build_dts1_s1ji_materialization_readiness_precheck()
    values = {
        "audit_id": S1_JJ_AUDIT_ID,
        "source_s1ji_digest": source.audit_digest,
        "s1jh_clock_facts": S1_JJ_S1JH_CLOCK_FACTS,
        "runtime_invariants": S1_JJ_RUNTIME_INVARIANTS,
        "sequence_impact": S1_JJ_SEQUENCE_IMPACT,
        "failure_chain": S1_JJ_FAILURE_CHAIN,
        "preserved_bindings": S1_JJ_PRESERVED_BINDINGS,
        "superseded_bindings": S1_JJ_SUPERSEDED_BINDINGS,
        "correction_requirements": S1_JJ_CORRECTION_REQUIREMENTS,
        "forbidden_shortcuts": S1_JJ_FORBIDDEN_SHORTCUTS,
        "forbidden_interpretations": S1_JJ_FORBIDDEN_INTERPRETATIONS,
        "affected_sequence_count": len(S1_JJ_SEQUENCE_IMPACT),
        "incompatible_continuation_envelopes_per_model_per_refinement": sum(
            row[2] for row in S1_JJ_SEQUENCE_IMPACT
        ),
        "baseline_case_count_still_blocked": 24,
        "s1jh_time_schedule_materializable": False,
        "non_time_s1jh_bindings_preserved": True,
        "materialization_schema_bound": False,
        "common_interval_fixture_implemented": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "corrected_monotonic_clock_contract_authorized_next_stage": True,
        "decision": S1_JJ_DECISION,
    }
    return DTS1S1JJIntervalClockCompatibilityPrecheck(
        **values, audit_digest=_digest(values)
    )
