"""Static S1-JQ readiness precheck for baseline adapter refinement."""

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
from .dynamic_substrate_s1jp_baseline_adapter_bridge_contract import (
    build_dts1_s1jp_baseline_adapter_bridge_contract,
)


class DTS1S1JQAdapterRefinementReadinessPrecheckError(ValueError):
    """Raised when the S1-JQ stop boundary is weakened."""


S1_JQ_AUDIT_ID = "dynamic-substrate.adapter-refinement-readiness.s1jq.v1"
S1_JQ_SOURCE_S1JP_DIGEST = (
    "2852c8215dc9cc6e20d7de5865e50f9d6badc65ed7df99e37779e281960faa7b"
)
S1_JQ_SOURCE_S1JK_DIGEST = (
    "64ca5b895146fef453eb27945a1074f5d2b8e4c8834a94cc6f9b0a855a61824f"
)
S1_JQ_SOURCE_S1JA_DIGEST = (
    "331168f2a6f937b454742d2be57de3f022f75ca5ca521fbff31f101bd4ea1fbc"
)
S1_JQ_BOUND_TIME_FACTS = (
    "every-S1-JK-physical-interval-has-one-integer-tick-from-ordinal-start-to-start-plus-one",
    "MCMFieldStepTime-requires-integer-start-and-end-ticks-with-end-strictly-greater-than-start",
    "the-S1-JO-distribution-and-step-time-must-remain-exactly-equal-to-the-bound-S1-JK-window",
    "the-carried-field-last-distribution-must-end-exactly-at-the-next-bound-start-tick-on-the-same-clock",
    "S1-JA-and-S1-JP-bind-refinement-levels-two-four-eight-for-every-baseline-role",
)
S1_JQ_KERNEL_CAPABILITY_RECORDS = (
    (
        "B1",
        "dynamic_substrate_dts1_coupled_step._advance_active_field",
        False,
        True,
        "one-exact-spectral-integration-followed-by-one-atomic-field.advance-with-the-complete-step-time",
        "BLOCKED_BY_S1JP_REQUIRED_SUBWINDOW_PARTITION",
    ),
    (
        "B2",
        "s2_reference_baselines.advance_s2_reference_model:model-b2",
        False,
        False,
        "one-analytic-matrix-exponential-over-one-positive-elapsed-duration-with-no-refinement-argument",
        "BLOCKED_BY_S1JP_REQUIRED_SUBWINDOW_PARTITION",
    ),
    (
        "B3",
        "mcm_f3_runtime.advance_mcm_f3_shared_field:local-leaky",
        True,
        True,
        "existing-runtime-accepts-one-positive-integer-native-refinement",
        "KERNEL_SURFACE_SUPPORTS_BOUND_REFINEMENT",
    ),
    (
        "B4",
        "mcm_f3_runtime.advance_mcm_f3_shared_field:linear-coupled",
        True,
        True,
        "existing-runtime-accepts-one-positive-integer-native-refinement",
        "KERNEL_SURFACE_SUPPORTS_BOUND_REFINEMENT",
    ),
    (
        "B5",
        "mcm_f3_runtime.advance_mcm_f3_shared_field:full-F3",
        True,
        True,
        "existing-runtime-accepts-one-positive-integer-native-refinement",
        "KERNEL_SURFACE_SUPPORTS_BOUND_REFINEMENT",
    ),
    (
        "B6",
        "mcm_f3_runtime.advance_mcm_f3_shared_field:const-v",
        True,
        True,
        "existing-runtime-accepts-one-positive-integer-native-refinement",
        "KERNEL_SURFACE_SUPPORTS_BOUND_REFINEMENT",
    ),
)
S1_JQ_CONFLICT_PROOF = (
    "r-positive-contiguous-integer-subwindows-require-at-least-r-ticks",
    "each-bound-S1-JK-window-contains-exactly-one-tick-so-r-two-four-eight-cannot-be-represented",
    "fractional-ticks-are-invalid-for-MCMFieldStepTime",
    "multiplying-clock-rate-or-replacing-ticks-would-change-the-common-exposure-and-corrected-time-contract",
    "repeating-B1-with-the-same-complete-window-would-reuse-nonmonotonic-field-time-and-reapply-the-contact",
    "B2-model-b2-has-no-refinement-parameter-and-S1-JP-does-not-permit-reimplementing-its-equation",
    "silently-ignoring-the-level-would-violate-the-S1-JP-universal-subwindow-rule",
)
S1_JQ_PRESERVED_BINDINGS = (
    "all-twenty-three-S1-JK-envelopes-times-identities-and-digests",
    "the-S1-JO-materializer-and-its-four-separated-integrity-roles",
    "all-seven-S1-JA-configurations-and-twenty-four-case-identities",
    "all-S1-JP-information-output-state-return-neutral-and-fail-closed-rules-not-dependent-on-refinement-partition",
    "the-existing-B1-B2-and-B3-through-B6-kernels-remain-unchanged",
)
S1_JQ_REQUIRED_CORRECTION = (
    "classify-refinement-by-existing-kernel-integration-semantics-before-implementation",
    "bind-B1-and-B2-exact-full-interval-evaluation-and-preregister-bit-identical-r2-r4-r8-control-expectations-or-stop",
    "retain-native-refinement-two-four-eight-for-B3-through-B6",
    "preserve-one-common-physical-window-contact-and-final-field-time-for-all-roles",
    "replace-only-the-conflicting-universal-subwindow-claims-and-dependent-digests",
)
S1_JQ_FORBIDDEN_REPAIRS = (
    "fractional-field-ticks-or-an-unregistered-private-clock",
    "clock-rate-rewrite-final-metadata-rewrite-or-post-hoc-time-repair",
    "B1-or-B2-kernel-reimplementation-equation-change-or-new-integrator",
    "contact-reapplication-hidden-substep-field-commit-or-silent-refinement-ignore",
    "adapter-implementation-partial-baseline-omission-or-case-execution-before-correction",
)
S1_JQ_DECISION = (
    "STOPP_S1JP_UNIVERSAL_REFINEMENT_PARTITION_INCOMPATIBLE_WITH_ONE_TICK_B1_B2_KERNELS"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JQAdapterRefinementReadinessPrecheck:
    audit_id: str
    source_s1jp_digest: str
    source_s1jk_digest: str
    source_s1ja_digest: str
    bound_time_facts: tuple[str, ...]
    kernel_capability_records: tuple[tuple[str, str, bool, bool, str, str], ...]
    conflict_proof: tuple[str, ...]
    preserved_bindings: tuple[str, ...]
    required_correction: tuple[str, ...]
    forbidden_repairs: tuple[str, ...]
    baseline_role_count: int
    native_refinement_role_count: int
    blocked_role_count: int
    blocked_case_count: int
    all_twenty_four_cases_blocked_atomically: bool
    adapter_implementation_ready: bool
    adapters_implemented: bool
    baseline_models_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    corrected_refinement_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_JQ_AUDIT_ID
            or self.source_s1jp_digest != S1_JQ_SOURCE_S1JP_DIGEST
            or self.source_s1jk_digest != S1_JQ_SOURCE_S1JK_DIGEST
            or self.source_s1ja_digest != S1_JQ_SOURCE_S1JA_DIGEST
            or self.bound_time_facts != S1_JQ_BOUND_TIME_FACTS
            or self.kernel_capability_records != S1_JQ_KERNEL_CAPABILITY_RECORDS
            or self.conflict_proof != S1_JQ_CONFLICT_PROOF
            or self.preserved_bindings != S1_JQ_PRESERVED_BINDINGS
            or self.required_correction != S1_JQ_REQUIRED_CORRECTION
            or self.forbidden_repairs != S1_JQ_FORBIDDEN_REPAIRS
            or self.baseline_role_count != 6
            or self.native_refinement_role_count != 4
            or self.blocked_role_count != 2
            or self.blocked_case_count != 8
            or self.all_twenty_four_cases_blocked_atomically is not True
            or self.adapter_implementation_ready is not False
            or self.adapters_implemented is not False
            or self.baseline_models_executed is not False
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.corrected_refinement_contract_authorized_next_stage is not True
            or self.decision != S1_JQ_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1JQAdapterRefinementReadinessPrecheckError(
                "S1-JQ weakened the refinement readiness stop"
            )


def build_dts1_s1jq_adapter_refinement_readiness_precheck(
) -> DTS1S1JQAdapterRefinementReadinessPrecheck:
    """Audit refinement compatibility without constructing an adapter."""

    source = build_dts1_s1jp_baseline_adapter_bridge_contract()
    time_source = build_dts1_s1jk_corrected_monotonic_interval_contract()
    matrix_source = build_dts1_s1ja_finite_configuration_matrix_contract()
    values = {
        "audit_id": S1_JQ_AUDIT_ID,
        "source_s1jp_digest": source.contract_digest,
        "source_s1jk_digest": time_source.contract_digest,
        "source_s1ja_digest": matrix_source.contract_digest,
        "bound_time_facts": S1_JQ_BOUND_TIME_FACTS,
        "kernel_capability_records": S1_JQ_KERNEL_CAPABILITY_RECORDS,
        "conflict_proof": S1_JQ_CONFLICT_PROOF,
        "preserved_bindings": S1_JQ_PRESERVED_BINDINGS,
        "required_correction": S1_JQ_REQUIRED_CORRECTION,
        "forbidden_repairs": S1_JQ_FORBIDDEN_REPAIRS,
        "baseline_role_count": len(S1_JQ_KERNEL_CAPABILITY_RECORDS),
        "native_refinement_role_count": sum(
            row[2] for row in S1_JQ_KERNEL_CAPABILITY_RECORDS
        ),
        "blocked_role_count": sum(
            not row[2] for row in S1_JQ_KERNEL_CAPABILITY_RECORDS
        ),
        "blocked_case_count": 2 * 4,
        "all_twenty_four_cases_blocked_atomically": True,
        "adapter_implementation_ready": False,
        "adapters_implemented": False,
        "baseline_models_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "corrected_refinement_contract_authorized_next_stage": True,
        "decision": S1_JQ_DECISION,
    }
    return DTS1S1JQAdapterRefinementReadinessPrecheck(
        **values, audit_digest=_digest(values)
    )
