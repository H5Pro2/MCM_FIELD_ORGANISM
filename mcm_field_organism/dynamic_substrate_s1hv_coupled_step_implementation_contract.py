"""S1-HV static contract for one private atomic DTS-1/S/H step."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1HVCoupledStepImplementationContractError(ValueError):
    """Raised when the S1-HV coupled-step boundary is weakened."""


S1_HV_CONTRACT_ID = "dynamic-substrate.coupled-step-implementation.s1hv.v1"
S1_HV_SOURCE_S1HU_AUDIT_DIGEST = (
    "c14660c1ac34fed779f772c44d92c074ca765d25ae43d5a520cd8dd52e7437aa"
)
S1_HV_CANDIDATE_ID = "DTS1_LOCAL_THREE_STATE_EDGE_RESOURCE_TURNOVER"
S1_HV_ORDER_ID = "CLOSED_PRESTATE_PARALLEL_READ_ATOMIC_COMMIT"
S1_HV_TARGET_MODULE = "mcm_field_organism.dynamic_substrate_dts1_coupled_step"
S1_HV_ERROR_TYPE = "DTS1CoupledStepError(ValueError)"
S1_HV_ENTRY_POINT = (
    "advance_dts1_coupled_fast_shared_field(field,anatomy,distribution,step_time,"
    "substrate_config,afterimage_config,dts1_rates,dissipation_config=None,*,"
    "backreaction_enabled=bool)->DTS1CoupledFastFieldStepResult"
)
S1_HV_INPUTS = (
    ("field", "one immutable closed SharedMCMField containing S_n and H_n"),
    ("anatomy", "one immutable valid DTS1ResourceAnatomy A_n"),
    ("distribution", "one complete ReceptorDistribution for the same interval"),
    ("step_time", "one explicit MCMFieldStepTime for the closed interval"),
    ("substrate_config", "existing NeutralLocalFieldSubstrateConfig supplying r_0"),
    ("afterimage_config", "the existing NeutralFastAfterimageConfig"),
    ("dts1_rates", "one explicit DTS1StepRates value without selected numbers"),
    ("dissipation_config", "existing optional field dissipation config unchanged"),
    ("backreaction_enabled", "one required strict boolean A0/A1 control"),
)
S1_HV_RESULT_FIELDS = (
    ("field", "one complete validated L_next proposal"),
    ("anatomy", "one complete validated A_next proposal"),
    ("elapsed_time", "the validated explicit interval duration"),
    ("participations", "the complete canonical p_n ledger"),
    ("resource_transfers", "the complete passive S1-HP transfer ledger"),
    ("applied_adapter", "the complete S1-HT A_n adapter"),
)
S1_HV_PHASES = (
    "validate-all-types-geometry-time-configs-and-strict-control-before-proposals",
    "require-one-existing-positive-step-time-matching-the-distribution",
    "derive-one-positive-elapsed-interval-with-the-existing-neutral-time-helper",
    "derive-complete-canonical-p_n-from-S_n-only-with-the-s1hk-observable",
    "derive-active-or-ablated-adapter-and-G_n-from-A_n-only-with-s1ht",
    "compute-complete-A_next-from-A_n-p_n-elapsed-and-rates-with-s1hp",
    "delegate-A0-field-and-active-zero-binding-field-directly-to-neutral-fast-step",
    "otherwise-compute-L_next-with-G_n-and-the-unchanged-neutral-boundary-integrator",
    "validate-both-proposals-and-passive-ledgers-without-mutating-inputs",
    "construct-one-new-result-as-the-only-atomic-pair-commit",
)
S1_HV_NEUTRAL_IDENTITIES = (
    "P0-remains-the-existing-neutral-fast-field-function-outside-this-module",
    "P0-does-not-construct-participation-adapter-generator-or-resource-proposal",
    "A0-computes-A_next-but-calls-the-existing-neutral-fast-field-function-once",
    "A0-field-output-is-value-and-bit-identical-to-P0-for-identical-field-inputs",
    "A1-with-zero-prestate-binding-uses-the-same-direct-neutral-field-call-as-A0",
    "A0-and-A1-from-one-prestate-produce-identical-A_next-and-transfer-ledgers",
    "no-new-field-integrator-boundary-afterimage-leak-or-clipping-rule-is-added",
)
S1_HV_ATOMICITY_RULES = (
    "field-anatomy-and-all-config-inputs-remain-immutable",
    "resource-and-field-proposals-read-one-shared-closed-prestate-only",
    "neither-proposal-may-read-or-mutate-the-other-proposal",
    "any-error-before-result-construction-yields-no-pair-output",
    "no-callback-observer-snapshot-restore-or-partial-result-surface",
    "complete-passive-ledgers-and-elapsed-time-never-drive-later-computation",
)
S1_HV_FORBIDDEN_SURFACES = (
    "poststate-reader-resource-first-field-first-or-midpoint-coupling",
    "implicit-iteration-solver-tolerance-or-adaptive-substep-selection",
    "new-field-integrator-or-duplicated-neutral-A0-numerics",
    "hidden-time-rate-gain-threshold-randomness-or-environment-input",
    "mutation-partial-commit-clipping-normalization-or-state-repair",
    "runtime-runner-probe-snapshot-restore-browser-audio-video-or-file-io",
    "package-level-current-api-or-public-manifest-export",
    "parameter-fitting-functional-measurement-or-research-execution",
)
S1_HV_TEST_MATRIX = (
    ("T01", "positive-step-time-is-required-and-zero-duration-is-unrepresentable"),
    ("T02", "complete-shared-layer-anatomy-edge-geometry-and-digest-required"),
    ("T03", "p_n-ledger-is-complete-canonical-and-reads-only-S_n"),
    ("T04", "A_next-matches-direct-s1hp-call-from-A_n-p_n-and-elapsed"),
    ("T05", "applied-adapter-matches-direct-s1ht-reader-from-A_n"),
    ("T06", "A0-field-is-bit-exact-direct-neutral-fast-step-output"),
    ("T07", "A0-and-A1-produce-identical-same-substep-resource-result"),
    ("T08", "A1-zero-prestate-binding-field-is-bit-exact-A0-and-P0"),
    ("T09", "new-binding-cannot-affect-the-current-field-proposal"),
    ("T10", "new-field-values-cannot-affect-the-current-resource-proposal"),
    ("T11", "active-nonzero-binding-uses-s1ht-generator-with-neutral-boundary"),
    ("T12", "afterimage-dissipation-domain-and-step-time-semantics-are-unchanged"),
    ("T13", "all-inputs-remain-unchanged-and-repeat-is-deterministic"),
    ("T14", "resource-failure-yields-no-field-or-pair-output"),
    ("T15", "field-failure-yields-no-anatomy-or-pair-output"),
    ("T16", "invalid-types-controls-time-configs-and-geometry-fail-closed"),
    ("T17", "edge-and-node-declaration-order-does-not-change-value-output"),
    ("T18", "complete-pair-n-2n-4n-residual-and-reader-latency-are-measurable"),
    ("T19", "no-midpoint-implicit-adaptive-or-partial-commit-path-exists"),
    ("T20", "no-runtime-io-snapshot-public-api-values-or-field-run-is-added"),
)
S1_HV_SUCCESS_BOUNDARY = (
    "private-atomic-first-order-coupled-step-contract-only",
    "existing-neutral-field-integrator-is-reused-not-reselected",
    "exact-P0-A0-and-first-zero-binding-A1-identities-remain-mandatory",
    "implementation-success-would-not-establish-stability-or-function",
    "refinement-and-baseline-separation-remain-future-gates",
)
S1_HV_DECISION = "DTS1_PRIVATE_COUPLED_STEP_CONTRACT_AND_TEST_MATRIX_BOUND"


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1HVCoupledStepImplementationContract:
    contract_id: str
    source_s1hu_audit_digest: str
    candidate_id: str
    order_id: str
    target_module: str
    error_type: str
    entry_point: str
    inputs: tuple[tuple[str, str], ...]
    result_fields: tuple[tuple[str, str], ...]
    phases: tuple[str, ...]
    neutral_identities: tuple[str, ...]
    atomicity_rules: tuple[str, ...]
    forbidden_surfaces: tuple[str, ...]
    test_matrix: tuple[tuple[str, str], ...]
    success_boundary: tuple[str, ...]
    exact_p0_a0_field_identity_required: bool
    active_zero_binding_neutral_delegation_required: bool
    one_closed_prestate_required: bool
    atomic_pair_commit_required: bool
    existing_neutral_integrator_reuse_required: bool
    implementation_authorized_next_stage: bool
    coupled_step_implementation_present: bool
    new_field_integrator_selected: bool
    material_rate_values_selected: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    field_steps_executed: int
    functional_effect_proven: bool
    claims_permitted: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        test_ids = tuple(test_id for test_id, _ in self.test_matrix)
        if (
            self.contract_id != S1_HV_CONTRACT_ID
            or self.source_s1hu_audit_digest != S1_HV_SOURCE_S1HU_AUDIT_DIGEST
            or self.candidate_id != S1_HV_CANDIDATE_ID
            or self.order_id != S1_HV_ORDER_ID
            or self.target_module != S1_HV_TARGET_MODULE
            or self.error_type != S1_HV_ERROR_TYPE
            or self.entry_point != S1_HV_ENTRY_POINT
            or self.inputs != S1_HV_INPUTS
            or self.result_fields != S1_HV_RESULT_FIELDS
            or self.phases != S1_HV_PHASES
            or self.neutral_identities != S1_HV_NEUTRAL_IDENTITIES
            or self.atomicity_rules != S1_HV_ATOMICITY_RULES
            or self.forbidden_surfaces != S1_HV_FORBIDDEN_SURFACES
            or self.test_matrix != S1_HV_TEST_MATRIX
            or test_ids != tuple(f"T{index:02d}" for index in range(1, 21))
            or self.success_boundary != S1_HV_SUCCESS_BOUNDARY
            or any(
                value is not True
                for value in (
                    self.exact_p0_a0_field_identity_required,
                    self.active_zero_binding_neutral_delegation_required,
                    self.one_closed_prestate_required,
                    self.atomic_pair_commit_required,
                    self.existing_neutral_integrator_reuse_required,
                    self.implementation_authorized_next_stage,
                )
            )
            or any(
                value is not False
                for value in (
                    self.coupled_step_implementation_present,
                    self.new_field_integrator_selected,
                    self.material_rate_values_selected,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.functional_effect_proven,
                    self.claims_permitted,
                )
            )
            or self.field_steps_executed != 0
            or self.decision != S1_HV_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1HVCoupledStepImplementationContractError(
                "S1-HV weakened the private atomic coupled-step boundary"
            )


def build_dts1_s1hv_coupled_step_implementation_contract(
) -> DTS1S1HVCoupledStepImplementationContract:
    """Bind one future private coupled step without implementing or running it."""

    values = {
        "contract_id": S1_HV_CONTRACT_ID,
        "source_s1hu_audit_digest": S1_HV_SOURCE_S1HU_AUDIT_DIGEST,
        "candidate_id": S1_HV_CANDIDATE_ID,
        "order_id": S1_HV_ORDER_ID,
        "target_module": S1_HV_TARGET_MODULE,
        "error_type": S1_HV_ERROR_TYPE,
        "entry_point": S1_HV_ENTRY_POINT,
        "inputs": S1_HV_INPUTS,
        "result_fields": S1_HV_RESULT_FIELDS,
        "phases": S1_HV_PHASES,
        "neutral_identities": S1_HV_NEUTRAL_IDENTITIES,
        "atomicity_rules": S1_HV_ATOMICITY_RULES,
        "forbidden_surfaces": S1_HV_FORBIDDEN_SURFACES,
        "test_matrix": S1_HV_TEST_MATRIX,
        "success_boundary": S1_HV_SUCCESS_BOUNDARY,
        "exact_p0_a0_field_identity_required": True,
        "active_zero_binding_neutral_delegation_required": True,
        "one_closed_prestate_required": True,
        "atomic_pair_commit_required": True,
        "existing_neutral_integrator_reuse_required": True,
        "implementation_authorized_next_stage": True,
        "coupled_step_implementation_present": False,
        "new_field_integrator_selected": False,
        "material_rate_values_selected": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "field_steps_executed": 0,
        "functional_effect_proven": False,
        "claims_permitted": False,
        "decision": S1_HV_DECISION,
    }
    return DTS1S1HVCoupledStepImplementationContract(
        **values,
        contract_digest=_digest(values),
    )
