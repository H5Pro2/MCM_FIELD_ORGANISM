"""Static S1-JG common model-neutral interval envelope contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_common_boundary_2n import (
    build_dts1_s1jf_implementation_receipt,
)


class DTS1S1JGCommonIntervalEnvelopeContractError(ValueError):
    """Raised when the S1-JG common interval boundary is weakened."""


S1_JG_CONTRACT_ID = "dynamic-substrate.common-interval-envelope.s1jg.v1"
S1_JG_SOURCE_S1JF_DIGEST = (
    "ce0d17c185f08327bf81ea50b936fdc54992968980c56b385fd9629658236277"
)
S1_JG_ORCHESTRATION_ENVELOPE_FIELDS = (
    ("sequence_digest", "one-preregistered-content-digest-with-no-model-result-input"),
    ("ordinal", "one-positive-contiguous-integer-within-the-sequence"),
    ("canonical_node_ids", "complete-two-or-three-node-order"),
    ("edge_inventory_digest", "complete-open-line-geometry-identity"),
    (
        "prestate_directive",
        "INITIAL_REGISTERED_SH-or-CARRY_PRIOR_SH-or-APPLY_BOUNDARY_2N-or-APPLY_BOUNDARY_3N",
    ),
    ("prestate_source_digest", "one-bound-initial-SH-or-boundary-fixture-digest"),
    ("receptor_contact", "one-complete-finite-vector-in-canonical-node-order"),
    ("step_time", "one-positive-MCMFieldStepTime"),
    ("checkpoint_after_interval", "one-strict-boolean-orchestrator-instruction"),
    ("interval_digest", "one-canonical-digest-over-all-prior-envelope-fields"),
)
S1_JG_MATERIALIZATION_PHASES = (
    "validate-complete-sequence-order-geometry-prestate-contact-time-and-digests-before-model-selection",
    "apply-the-registered-initial-S-H-carry-rule-or-pure-two-or-three-node-boundary-exactly-once",
    "construct-one-complete-ReceptorDistribution-matching-the-same-node-order-contact-and-field-time",
    "construct-one-model-facing-view-only-after-the-complete-common-prestate-is-materialized",
    "deliver-value-identical-model-facing-views-to-DTS1-and-B1-through-B6-for-the-same-envelope",
    "capture-the-complete-postinterval-field-only-in-the-orchestrator-when-checkpoint-is-true",
)
S1_JG_MODEL_FACING_FIELDS = (
    ("field", "one-complete-materialized-SharedMCMField-prestate"),
    ("distribution", "one-complete-matching-ReceptorDistribution"),
    ("step_time", "one-complete-matching-MCMFieldStepTime"),
    ("geometry_digest", "one-complete-common-edge-inventory-digest"),
    ("input_digest", "one-canonical-digest-of-the-model-facing-values"),
)
S1_JG_MODEL_FACING_EXCLUSIONS = (
    "profile-block-arm-case-sequence-name-checkpoint-number-or-target-direction",
    "prestate-directive-boundary-role-event-label-or-orchestrator-checkpoint-boolean",
    "candidate-anatomy-participation-transfer-ledger-recovery-switch-or-result",
    "reference-output-future-state-fit-residual-threshold-retry-or-randomness",
)
S1_JG_PROFILE_SEQUENCE_TOPOLOGY = (
    (
        "P_IE_CAUSAL_TWO_SUBSTEP",
        2,
        2,
        2,
        "INITIAL_REGISTERED_SH-then-CARRY_PRIOR_SH",
        "two-value-identical-external-sequences-candidate-anatomy-sidecar-differs",
    ),
    (
        "P_IH_ATTENUATION",
        1,
        3,
        3,
        "APPLY_BOUNDARY_2N-before-every-interval",
        "one-three-interval-sequence-with-hidden-model-state-carry",
    ),
    (
        "P_IK_INTERFERENCE",
        2,
        4,
        1,
        "APPLY_BOUNDARY_3N-before-every-interval",
        "A-B-A-versus-A-GAP-A-then-one-common-probe-readout-per-sequence",
    ),
    (
        "P_IN_RELEASE_REUSE",
        2,
        4,
        1,
        "APPLY_BOUNDARY_3N-before-every-interval",
        "two-value-identical-A-GAP-B-probe-sequences-DTS1-recovery-sidecar-differs",
    ),
)
S1_JG_CANDIDATE_SIDECAR_RULES = (
    "P_IE-only-DTS1-receives-the-preregistered-F_HIGH-versus-R_HIGH-initial-anatomy-sidecar",
    "P_IN-only-DTS1-receives-the-preregistered-recovery-on-versus-off-gap-intervention-sidecar",
    "sidecars-are-not-fields-of-the-common-envelope-or-model-facing-view",
    "B1-through-B6-receive-no-sidecar-analogue-placeholder-label-or-derived-value",
    "sidecars-are-bound-before-execution-and-may-not-read-any-output-or-refinement-residual",
)
S1_JG_SEQUENCE_RULES = (
    "all-sequences-are-built-and-digested-before-any-model-role-is-selected",
    "ordinals-are-contiguous-and-one-envelope-maps-to-exactly-one-positive-physical-interval",
    "no-envelope-may-be-merged-split-delayed-repeated-reordered-or-skipped",
    "common-boundaries-are-not-reapplied-at-private-refinement-substeps",
    "P_IE-carries-complete-S-H-after-interval-one-while-all-other-boundary-directives-replace-only-S-H",
    "each-model-owned-hidden-state-is-carried-between-envelopes-and-never-stored-in-the-common-envelope",
    "checkpoint-capture-does-not-feed-back-into-any-model-or-later-envelope",
)
S1_JG_CARDINALITY = (
    ("P_IE_envelopes_per_model_per_refinement", 4),
    ("P_IH_envelopes_per_model_per_refinement", 3),
    ("P_IK_envelopes_per_model_per_refinement", 8),
    ("P_IN_envelopes_per_model_per_refinement", 8),
    ("all_profiles_envelopes_per_model_per_refinement", 23),
    ("baseline_role_block_cases", 24),
    ("signed_profile_components", 28),
)
S1_JG_FAIL_CLOSED_RULES = (
    "reject-any-missing-extra-mistyped-nonfinite-or-digest-mismatched-envelope-field",
    "reject-any-geometry-node-order-contact-width-time-or-prestate-source-mismatch",
    "reject-any-forbidden-model-facing-field-or-candidate-sidecar-delivery-to-a-baseline",
    "reject-any-sequence-cardinality-order-boundary-carry-or-checkpoint-drift",
    "one-invalid-envelope-blocks-all-twenty-four-later-baseline-cases-without-partial-output",
)
S1_JG_FORBIDDEN_INTERPRETATIONS = (
    "selected-clock-ticks-initial-P_IE-S-H-values-or-concrete-envelope-digests",
    "implemented-materialized-executed-or-numerically-admissible-envelope-or-adapter",
    "baseline-fit-baseline-closure-candidate-superiority-memory-learning-or-artificial-intelligence",
)
S1_JG_DECISION = "COMMON_MODEL_NEUTRAL_INTERVAL_ENVELOPE_CONTRACT_BOUND_NO_VALUES_IMPLEMENTATION_OR_EXECUTION"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JGCommonIntervalEnvelopeContract:
    contract_id: str
    source_s1jf_digest: str
    orchestration_envelope_fields: tuple[tuple[str, str], ...]
    materialization_phases: tuple[str, ...]
    model_facing_fields: tuple[tuple[str, str], ...]
    model_facing_exclusions: tuple[str, ...]
    profile_sequence_topology: tuple[tuple[str, int, int, int, str, str], ...]
    candidate_sidecar_rules: tuple[str, ...]
    sequence_rules: tuple[str, ...]
    cardinality: tuple[tuple[str, int], ...]
    fail_closed_rules: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    profile_block_count: int
    envelopes_per_model_per_refinement: int
    baseline_case_count: int
    profile_component_count: int
    schema_bound: bool
    information_barrier_bound: bool
    all_four_exposure_topologies_bound: bool
    concrete_clock_ticks_selected: bool
    concrete_envelope_digests_bound: bool
    interval_envelope_implemented: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    finite_common_interval_fixture_contract_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_JG_CONTRACT_ID
            or self.source_s1jf_digest != S1_JG_SOURCE_S1JF_DIGEST
            or self.orchestration_envelope_fields != S1_JG_ORCHESTRATION_ENVELOPE_FIELDS
            or self.materialization_phases != S1_JG_MATERIALIZATION_PHASES
            or self.model_facing_fields != S1_JG_MODEL_FACING_FIELDS
            or self.model_facing_exclusions != S1_JG_MODEL_FACING_EXCLUSIONS
            or self.profile_sequence_topology != S1_JG_PROFILE_SEQUENCE_TOPOLOGY
            or self.candidate_sidecar_rules != S1_JG_CANDIDATE_SIDECAR_RULES
            or self.sequence_rules != S1_JG_SEQUENCE_RULES
            or self.cardinality != S1_JG_CARDINALITY
            or self.fail_closed_rules != S1_JG_FAIL_CLOSED_RULES
            or self.forbidden_interpretations != S1_JG_FORBIDDEN_INTERPRETATIONS
            or self.profile_block_count != 4
            or self.envelopes_per_model_per_refinement != 23
            or self.baseline_case_count != 24
            or self.profile_component_count != 28
            or any(
                value is not True
                for value in (
                    self.schema_bound,
                    self.information_barrier_bound,
                    self.all_four_exposure_topologies_bound,
                    self.finite_common_interval_fixture_contract_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.concrete_clock_ticks_selected,
                    self.concrete_envelope_digests_bound,
                    self.interval_envelope_implemented,
                    self.adapters_implemented,
                    self.baseline_models_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.decision != S1_JG_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JGCommonIntervalEnvelopeContractError(
                "S1-JG weakened the common model-neutral interval envelope"
            )


def build_dts1_s1jg_common_interval_envelope_contract() -> DTS1S1JGCommonIntervalEnvelopeContract:
    """Bind the common envelope schema without values or implementation."""

    source = build_dts1_s1jf_implementation_receipt()
    values = {
        "contract_id": S1_JG_CONTRACT_ID,
        "source_s1jf_digest": source.receipt_digest,
        "orchestration_envelope_fields": S1_JG_ORCHESTRATION_ENVELOPE_FIELDS,
        "materialization_phases": S1_JG_MATERIALIZATION_PHASES,
        "model_facing_fields": S1_JG_MODEL_FACING_FIELDS,
        "model_facing_exclusions": S1_JG_MODEL_FACING_EXCLUSIONS,
        "profile_sequence_topology": S1_JG_PROFILE_SEQUENCE_TOPOLOGY,
        "candidate_sidecar_rules": S1_JG_CANDIDATE_SIDECAR_RULES,
        "sequence_rules": S1_JG_SEQUENCE_RULES,
        "cardinality": S1_JG_CARDINALITY,
        "fail_closed_rules": S1_JG_FAIL_CLOSED_RULES,
        "forbidden_interpretations": S1_JG_FORBIDDEN_INTERPRETATIONS,
        "profile_block_count": len(S1_JG_PROFILE_SEQUENCE_TOPOLOGY),
        "envelopes_per_model_per_refinement": sum(
            row[1] * row[2] for row in S1_JG_PROFILE_SEQUENCE_TOPOLOGY
        ),
        "baseline_case_count": 24,
        "profile_component_count": 28,
        "schema_bound": True,
        "information_barrier_bound": True,
        "all_four_exposure_topologies_bound": True,
        "concrete_clock_ticks_selected": False,
        "concrete_envelope_digests_bound": False,
        "interval_envelope_implemented": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "finite_common_interval_fixture_contract_authorized_next_stage": True,
        "decision": S1_JG_DECISION,
    }
    return DTS1S1JGCommonIntervalEnvelopeContract(
        **values, contract_digest=_digest(values)
    )
