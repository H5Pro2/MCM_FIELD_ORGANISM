"""Static S1-JR corrected role-specific baseline refinement contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1ja_finite_configuration_matrix_contract import (
    build_dts1_s1ja_finite_configuration_matrix_contract,
)
from .dynamic_substrate_s1jk_corrected_monotonic_interval_contract import (
    build_dts1_s1jk_corrected_monotonic_interval_contract,
)
from .dynamic_substrate_s1jq_adapter_refinement_readiness_precheck import (
    build_dts1_s1jq_adapter_refinement_readiness_precheck,
)


class DTS1S1JRCorrectedRoleRefinementContractError(ValueError):
    """Raised when the corrected S1-JR refinement boundary is weakened."""


S1_JR_CONTRACT_ID = "dynamic-substrate.corrected-role-refinement.s1jr.v1"
S1_JR_SOURCE_S1JQ_DIGEST = (
    "9111d1f5814f96f72d995df1eccc7e5163629f515c9c18566e9dceaf904735f5"
)
S1_JR_SOURCE_S1JA_DIGEST = (
    "331168f2a6f937b454742d2be57de3f022f75ca5ca521fbff31f101bd4ea1fbc"
)
S1_JR_SOURCE_S1JK_DIGEST = (
    "64ca5b895146fef453eb27945a1074f5d2b8e4c8834a94cc6f9b0a855a61824f"
)
S1_JR_CONTROL_LABELS = (2, 4, 8)
S1_JR_PRIMARY_LABEL = 4
S1_JR_ROLE_REFINEMENT_RECORDS = (
    (
        "B1",
        "EXACT_FULL_INTERVAL_BIT_IDENTITY_CONTROL",
        "dynamic_substrate_dts1_coupled_step._advance_active_field",
        False,
        "one-closed-spectral-S-H-evaluation-over-the-complete-S1-JO-window",
        "r2-r4-r8-repeat-the-same-immutable-input-and-require-bit-identical-complete-output",
    ),
    (
        "B2",
        "EXACT_FULL_INTERVAL_BIT_IDENTITY_CONTROL",
        "s2_reference_baselines.advance_s2_reference_model:model-b2",
        False,
        "one-scaling-and-squaring-Pade-matrix-exponential-over-the-complete-S1-JO-window",
        "r2-r4-r8-repeat-the-same-immutable-input-and-require-bit-identical-complete-output",
    ),
    (
        "B3",
        "NATIVE_INTERNAL_REFINEMENT",
        "mcm_f3_runtime.advance_mcm_f3_shared_field:local-leaky",
        True,
        "pass-the-exact-control-label-two-four-or-eight-as-the-existing-runtime-refinement",
        "report-complete-signed-r2-r4-and-r4-r8-residuals",
    ),
    (
        "B4",
        "NATIVE_INTERNAL_REFINEMENT",
        "mcm_f3_runtime.advance_mcm_f3_shared_field:linear-coupled",
        True,
        "pass-the-exact-control-label-two-four-or-eight-as-the-existing-runtime-refinement",
        "report-complete-signed-r2-r4-and-r4-r8-residuals",
    ),
    (
        "B5",
        "NATIVE_INTERNAL_REFINEMENT",
        "mcm_f3_runtime.advance_mcm_f3_shared_field:full-F3",
        True,
        "pass-the-exact-control-label-two-four-or-eight-as-the-existing-runtime-refinement",
        "report-complete-signed-r2-r4-and-r4-r8-residuals",
    ),
    (
        "B6",
        "NATIVE_INTERNAL_REFINEMENT",
        "mcm_f3_runtime.advance_mcm_f3_shared_field:const-v",
        True,
        "pass-the-exact-control-label-two-four-or-eight-as-the-existing-runtime-refinement",
        "report-complete-signed-r2-r4-and-r4-r8-residuals",
    ),
)
S1_JR_EXACT_CONTROL_RULES = (
    "B1-and-B2-control-labels-are-repeat-identities-not-kernel-refinement-arguments-or-substep-counts",
    "each-label-starts-independently-from-the-same-complete-materialized-field-and-private-context",
    "each-label-calls-the-bound-exact-kernel-once-over-the-same-complete-S1-JO-duration-contact-and-boundary",
    "no-output-field-or-private-state-is-carried-from-one-control-label-into-another",
    "the-control-label-does-not-enter-the-kernel-input-output-digest-or-model-owned-diagnostics",
    "complete-output-field-next-private-state-diagnostics-and-output-digest-must-be-bit-identical-across-r2-r4-r8",
    "any-nonidentity-is-a-determinism-or-adapter-failure-and-invalidates-the-complete-case-without-tolerance-fit-or-retry",
)
S1_JR_NATIVE_REFINEMENT_RULES = (
    "B3-through-B6-pass-two-four-eight-only-to-the-existing-F3-runtime-refinement-argument",
    "each-level-starts-independently-from-the-same-complete-materialized-field-and-private-context",
    "the-F3-runtime-performs-private-numerical-stages-without-intermediate-SharedMCMField-time-commits",
    "the-common-S-H-boundary-and-receptor-distribution-are-applied-once-for-the-complete-physical-window",
    "each-level-publishes-one-complete-final-field-at-the-exact-original-S1-JO-end-tick",
    "signed-r2-r4-and-r4-r8-output-residuals-remain-required-without-threshold-fit-or-level-omission",
)
S1_JR_COMMON_TIME_RULES = (
    "all-six-roles-use-the-bit-identical-S1-JO-clock-start-end-rate-distribution-and-materialized-S-H-input",
    "no-role-creates-fractional-ticks-a-private-clock-rate-or-visible-intermediate-field-time",
    "one-control-evaluation-consumes-exactly-one-complete-physical-interval-and-produces-one-complete-field-time",
    "control-evaluations-are-alternative-repeats-from-one-prestate-not-three-sequential-physical-intervals",
    "the-primary-profile-remains-label-four-and-labels-two-eight-remain-mandatory-controls",
)
S1_JR_SUPERSESSION = (
    "replace-S1-JP-universal-equal-contiguous-subwindow-partition-for-B1-and-B2-only",
    "specialize-S1-JK-private-refinement-substep-language-so-it-applies-only-where-the-existing-kernel-has-native-internal-refinement",
    "preserve-S1-JA-labels-two-four-eight-primary-four-identical-inputs-and-residual-reporting",
    "preserve-all-S1-JP-information-private-state-output-neutral-and-fail-closed-rules",
    "preserve-all-S1-JK-envelope-times-sequence-digests-interval-digests-and-carry-provenance-bit-for-bit",
)
S1_JR_FAIL_CLOSED_RULES = (
    "reject-any-role-mode-kernel-identity-control-label-or-primary-label-drift-before-adapter-entry",
    "reject-any-cross-label-input-field-private-context-common-exposure-or-duration-difference",
    "reject-any-B1-B2-label-forwarding-subdivision-state-carry-or-non-bit-identical-output",
    "reject-any-B3-through-B6-missing-wrong-or-result-dependent-native-refinement",
    "reject-any-clock-contact-boundary-final-time-output-schema-or-atomicity-drift",
    "one-failed-control-blocks-the-complete-role-block-case-and-therefore-the-later-atomic-comparison",
)
S1_JR_TECHNICAL_TEST_MATRIX = (
    ("T01", "exact-S1-JQ-S1-JA-S1-JK-source-binding"),
    ("T02", "six-role-classification-two-exact-four-native"),
    ("T03", "fixed-control-labels-two-four-eight-and-primary-four"),
    ("T04", "B1-full-window-single-call-and-bit-identity-control"),
    ("T05", "B2-full-window-single-call-and-bit-identity-control"),
    ("T06", "B3-through-B6-native-refinement-forwarding"),
    ("T07", "independent-identical-prestate-per-control-label"),
    ("T08", "no-cross-label-state-carry-or-label-kernel-input"),
    ("T09", "common-one-tick-time-contact-and-boundary-preservation"),
    ("T10", "exact-role-zero-residual-and-native-role-signed-residual-rules"),
    ("T11", "narrow-supersession-and-prior-digest-preservation"),
    ("T12", "fail-closed-no-fit-retry-omission-or-partial-output"),
    ("T13", "deterministic-tamper-evident-and-no-kernel-call"),
    ("T14", "no-adapter-runtime-profile-or-research-execution"),
)
S1_JR_FORBIDDEN_INTERPRETATIONS = (
    "implemented-or-executed-adapter-baseline-or-control-evaluation",
    "numerical-admissibility-baseline-fit-closure-rejection-or-candidate-superiority",
    "physical-material-timescale-runtime-readiness-or-completed-twenty-four-case-matrix",
    "memory-learning-semantics-consciousness-experience-understanding-organic-property-or-artificial-intelligence",
)
S1_JR_DECISION = (
    "ROLE_SPECIFIC_EXACT_AND_NATIVE_REFINEMENT_CONTRACT_BOUND_NO_IMPLEMENTATION_OR_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JRCorrectedRoleRefinementContract:
    contract_id: str
    source_s1jq_digest: str
    source_s1ja_digest: str
    source_s1jk_digest: str
    control_labels: tuple[int, ...]
    primary_label: int
    role_refinement_records: tuple[tuple[str, str, str, bool, str, str], ...]
    exact_control_rules: tuple[str, ...]
    native_refinement_rules: tuple[str, ...]
    common_time_rules: tuple[str, ...]
    supersession: tuple[str, ...]
    fail_closed_rules: tuple[str, ...]
    technical_test_matrix: tuple[tuple[str, str], ...]
    forbidden_interpretations: tuple[str, ...]
    exact_control_role_count: int
    native_refinement_role_count: int
    baseline_role_count: int
    technical_test_count: int
    corrected_role_refinement_contract_bound: bool
    adapter_implementation_ready: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    private_adapter_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_JR_CONTRACT_ID
            or self.source_s1jq_digest != S1_JR_SOURCE_S1JQ_DIGEST
            or self.source_s1ja_digest != S1_JR_SOURCE_S1JA_DIGEST
            or self.source_s1jk_digest != S1_JR_SOURCE_S1JK_DIGEST
            or self.control_labels != S1_JR_CONTROL_LABELS
            or self.primary_label != S1_JR_PRIMARY_LABEL
            or self.role_refinement_records != S1_JR_ROLE_REFINEMENT_RECORDS
            or self.exact_control_rules != S1_JR_EXACT_CONTROL_RULES
            or self.native_refinement_rules != S1_JR_NATIVE_REFINEMENT_RULES
            or self.common_time_rules != S1_JR_COMMON_TIME_RULES
            or self.supersession != S1_JR_SUPERSESSION
            or self.fail_closed_rules != S1_JR_FAIL_CLOSED_RULES
            or self.technical_test_matrix != S1_JR_TECHNICAL_TEST_MATRIX
            or self.forbidden_interpretations != S1_JR_FORBIDDEN_INTERPRETATIONS
            or self.exact_control_role_count != 2
            or self.native_refinement_role_count != 4
            or self.baseline_role_count != 6
            or self.technical_test_count != 14
            or self.corrected_role_refinement_contract_bound is not True
            or self.adapter_implementation_ready is not True
            or self.adapters_implemented is not False
            or self.baseline_models_executed is not False
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.private_adapter_implementation_authorized_next_stage is not True
            or self.decision != S1_JR_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1JRCorrectedRoleRefinementContractError(
                "S1-JR weakened the corrected role refinement contract"
            )


def build_dts1_s1jr_corrected_role_refinement_contract(
) -> DTS1S1JRCorrectedRoleRefinementContract:
    """Bind role-specific refinement semantics without executing a kernel."""

    source = build_dts1_s1jq_adapter_refinement_readiness_precheck()
    matrix_source = build_dts1_s1ja_finite_configuration_matrix_contract()
    time_source = build_dts1_s1jk_corrected_monotonic_interval_contract()
    values = {
        "contract_id": S1_JR_CONTRACT_ID,
        "source_s1jq_digest": source.audit_digest,
        "source_s1ja_digest": matrix_source.contract_digest,
        "source_s1jk_digest": time_source.contract_digest,
        "control_labels": S1_JR_CONTROL_LABELS,
        "primary_label": S1_JR_PRIMARY_LABEL,
        "role_refinement_records": S1_JR_ROLE_REFINEMENT_RECORDS,
        "exact_control_rules": S1_JR_EXACT_CONTROL_RULES,
        "native_refinement_rules": S1_JR_NATIVE_REFINEMENT_RULES,
        "common_time_rules": S1_JR_COMMON_TIME_RULES,
        "supersession": S1_JR_SUPERSESSION,
        "fail_closed_rules": S1_JR_FAIL_CLOSED_RULES,
        "technical_test_matrix": S1_JR_TECHNICAL_TEST_MATRIX,
        "forbidden_interpretations": S1_JR_FORBIDDEN_INTERPRETATIONS,
        "exact_control_role_count": sum(
            not row[3] for row in S1_JR_ROLE_REFINEMENT_RECORDS
        ),
        "native_refinement_role_count": sum(
            row[3] for row in S1_JR_ROLE_REFINEMENT_RECORDS
        ),
        "baseline_role_count": len(S1_JR_ROLE_REFINEMENT_RECORDS),
        "technical_test_count": len(S1_JR_TECHNICAL_TEST_MATRIX),
        "corrected_role_refinement_contract_bound": True,
        "adapter_implementation_ready": True,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "private_adapter_implementation_authorized_next_stage": True,
        "decision": S1_JR_DECISION,
    }
    return DTS1S1JRCorrectedRoleRefinementContract(
        **values, contract_digest=_digest(values)
    )
