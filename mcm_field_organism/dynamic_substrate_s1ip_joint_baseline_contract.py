"""Static S1-IP contract for joint DTS-1 baseline closure."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json


class DTS1S1IPJointBaselineContractError(ValueError):
    """Raised when the closed S1-IP baseline comparison is weakened."""


S1_IP_CONTRACT_ID = "dynamic-substrate.joint-baseline-closure.s1ip.v1"
S1_IP_SOURCE_S1IO_AUDIT_DIGEST = (
    "8d588be0e2dd00394f28579dec81a7e494c0c2ed112a202db6c95153e1d4eddd"
)
S1_IP_REFERENCE_RECEIPTS = (
    ("S1-IB", "55159311a95b555900632014d68b3534aeb958787e0e6bcfba4d3e32dfedb217"),
    ("S1-IE", "dbaa141450f1a00defb71824feb4e61bbef727c0023ea1d1e19cc979581ebcea"),
    ("S1-IH", "2fd24fd7ccdee690ea5610440e2d76f85e6a5ca0b8bc4b9045ff7c12a34d0c36"),
    ("S1-IK", "7d0a5bffd19cc7f212392b1d4a9c4d8ea8c79ffb1414d6a9fbc9a936ff9dedfe"),
    ("S1-IN", "521dcb2750b87315550552979c4d1fe4ab7cd045fef4f3218265c3a32959a245"),
)
S1_IP_EXECUTABLE_BASELINE_ROLES = (
    ("B1_FIXED_PRERELEASE_ADAPTER", "dynamic_substrate_dts1_backreaction.compute_dts1_edge_rates+dynamic_substrate_dts1_coupled_step._advance_active_field"),
    ("B2_S2_LINEAR_INTEGRATOR", "s2_reference_baselines.advance_s2_reference_model:model-b2"),
    ("B3_F3_LOCAL_LEAKY", "mcm_f3_baseline_coupling.compute_mcm_f3_local_leaky_baseline"),
    ("B4_F3_LINEAR_COUPLED", "mcm_f3_baseline_coupling.compute_mcm_f3_linear_coupled_baseline"),
    ("B5_F3_FULL", "mcm_f3_coupling.compute_mcm_f3_coupling"),
    ("B6_CONST_V", "w7n_capacity_function_baselines.compute_w7n_coupling_baseline:model-const-v"),
)
S1_IP_STRUCTURAL_BASELINE_ROLES = (
    ("DYNAMIC_TWO_STATE_E1", "state-space-gate-from-S1-IB-and-S1-IE-no-execution"),
    ("FAST_AFTERIMAGE_H", "zero-H-control-gate-from-S1-IE-IH-IK-IN-no-fit"),
)
S1_IP_PROFILE_BLOCKS = (
    ("P_IE_CAUSAL_TWO_SUBSTEP", "signed-F_HIGH-minus-R_HIGH-complete-SH-at-substeps-1-and-2", 12),
    ("P_IH_ATTENUATION", "signed-checkpoint-2-minus-1-and-checkpoint-3-minus-1-complete-SH", 12),
    ("P_IK_INTERFERENCE", "signed-ABA-minus-A-gap-A-postsequence-complete-SH", 6),
    ("P_IN_RELEASE_REUSE", "signed-recovery-on-minus-recovery-off-postprobe-complete-SH", 6),
)
S1_IP_PROFILE_RULES = (
    "canonical-profile-order-is-P_IE-then-P_IH-then-P_IK-then-P_IN",
    "within-each-checkpoint-order-is-all-S-nodes-then-all-H-nodes-in-canonical-node-order",
    "all-components-remain-signed-and-no-absolute-value-endpoint-only-or-armwise-rescaling-is-permitted",
    "the-reference-profile-is-reconstructed-only-from-preregistered-fixtures-and-bound-receipts",
    "each-baseline-receives-the-same-contact-order-duration-boundaries-S-H-starts-and-geometry-for-each-block",
    "baseline-internal-states-are-compared-only-through-the-common-observable-field-profile",
    "two-node-and-three-node-blocks-remain-separate-until-canonical-concatenation",
)
S1_IP_STRUCTURAL_GATES = (
    "S1-IB-direct-free-refractory-engagement-direction-and-local-global-ledgers-must-remain-valid",
    "S1-IE-first-substep-field-identity-and-second-substep-causal-direction-must-remain-valid",
    "S1-IH-direct-engagement-attenuation-must-remain-valid-beside-the-field-profile",
    "S1-IK-middle-B-shared-free-and-final-A-engagement-directions-must-remain-valid",
    "S1-IN-direct-recovery-shared-free-and-additional-B-engagement-directions-must-remain-valid",
    "all-A0-value-identical-zero-participation-fixed-adapter-and-zero-H-controls-remain-hard-gates",
    "no-observable-profile-fit-may-substitute-for-one-failed-direct-resource-or-control-gate",
)
S1_IP_ALLOWED_BASELINE_INPUTS = (
    "canonical-field-geometry-and-node-order",
    "registered-S-H-field-prestates-contact-sequences-times-and-event-boundaries",
    "one-baseline-owned-initial-state-created-without-reading-DTS1-arm-identity-or-postdivergence-anatomy",
    "for-B1-only-one-common-predivergence-conductive-state-may-derive-one-fixed-adapter-per-fixture",
    "each-baseline-may-read-only-coordinates-defined-by-its-existing-published-state-contract",
)
S1_IP_FORBIDDEN_BASELINE_INPUTS = (
    "DTS1-free-refractory-or-transfer-ledger-as-a-baseline-state-coordinate",
    "arm-id-case-id-checkpoint-id-target-direction-reference-output-or-future-state",
    "per-arm-per-checkpoint-per-profile-block-or-result-dependent-parameter-values",
    "candidate-derived-fixed-adapter-from-any-postdivergence-state",
    "hidden-reset-phase-detector-label-reward-target-topology-or-resource-transport",
)
S1_IP_PARAMETER_RULES = (
    "B1-uses-one-predivergence-fixed-adapter-per-source-fixture-and-never-refits-after-arm-divergence",
    "B2-through-B6-each-use-one-immutable-configuration-source-and-one-configuration-digest-across-all-compatible-profile-blocks",
    "existing-kernel-equations-and-existing-published-default-parameter-sources-remain-unchanged",
    "geometry-or-data-shape-adapters-may-translate-identities-order-and-shapes-but-not-equations-parameters-or-state-dimension",
    "technical-incompatibility-is-a-recorded-result-and-may-not-be-repaired-after-seeing-profile-values",
    "no-oracle-gain-per-checkpoint-or-candidate-state-reader-is-an-explanatory-baseline",
)
S1_IP_COMPARISON_METRICS = (
    "profile_linf_residual-over-all-36-signed-components",
    "profile_l1_residual-over-all-36-signed-components",
    "relative_profile_linf_residual-against-one-preregistered-reference-scale",
    "per-block-linf-residual-for-P_IE-P_IH-P_IK-and-P_IN",
    "baseline-refinement-residual-where-the-existing-kernel-has-a-refinement-control",
    "maximum-own-invariant-residual-and-minimum-own-valid-resource-where-defined",
    "schedule-geometry-ablation-fixed-reader-zero-H-and-deterministic-repeat-booleans",
)
S1_IP_DECISION_ORDER = (
    "INVALID_JOINT_BASELINE_AUDIT",
    "TECHNICALLY_INCOMPATIBLE_BASELINE_INVENTORY",
    "DTS1_PROFILE_EXPLAINED_BY_REGISTERED_BASELINE",
    "DTS1_RESIDUAL_AFTER_REGISTERED_BASELINES",
)
S1_IP_STOPP_CONDITIONS = (
    "reference-receipt-profile-block-component-order-sign-or-structural-gate-drift",
    "any-baseline-receives-one-forbidden-input-or-an-unregistered-state-coordinate",
    "any-baseline-equation-state-dimension-parameter-source-or-configuration-digest-changes-after-binding",
    "any-armwise-checkpointwise-result-dependent-fit-rescale-threshold-retry-or-partial-output",
    "any-geometry-schedule-boundary-A0-fixed-reader-zero-H-invariant-or-repeat-control-fails",
    "an-incompatible-baseline-is-silently-omitted-replaced-or-counted-as-a-residual",
    "a-profile-fit-is-used-to-overrule-a-failed-direct-resource-or-causal-gate",
    "runtime-coupling-research-field-use-or-claim-expansion",
)
S1_IP_FORBIDDEN_INTERPRETATIONS = (
    "baseline-closure-baseline-rejection-or-candidate-superiority-before-execution",
    "universal-model-nonreducibility-material-validity-or-runtime-readiness",
    "memory-learning-semantics-inner-context-organization-self-regulation-organism-or-artificial-intelligence",
    "new-natural-law-or-general-capability",
)
S1_IP_DECISION = "DTS1_JOINT_BASELINE_CLOSURE_CONTRACT_BOUND_NO_PARAMETERS_OR_EXECUTION"


def _digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1IPJointBaselineContract:
    contract_id: str
    source_s1io_audit_digest: str
    reference_receipts: tuple[tuple[str, str], ...]
    executable_baseline_roles: tuple[tuple[str, str], ...]
    structural_baseline_roles: tuple[tuple[str, str], ...]
    profile_blocks: tuple[tuple[str, str, int], ...]
    profile_rules: tuple[str, ...]
    structural_gates: tuple[str, ...]
    allowed_baseline_inputs: tuple[str, ...]
    forbidden_baseline_inputs: tuple[str, ...]
    parameter_rules: tuple[str, ...]
    comparison_metrics: tuple[str, ...]
    decision_order: tuple[str, ...]
    stopp_conditions: tuple[str, ...]
    forbidden_interpretations: tuple[str, ...]
    profile_component_count: int
    parameter_values_selected: bool
    comparison_threshold_selected: bool
    geometry_adapters_implemented: bool
    profile_container_implemented: bool
    baseline_models_executed: bool
    joint_comparison_executed: bool
    runtime_integration_present: bool
    research_execution_permitted: bool
    technical_field_steps_executed: int
    research_field_steps_executed: int
    baseline_closure_proven: bool
    claims_permitted: bool
    compatibility_audit_authorized_next_stage: bool
    atomic_decision_required: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {field.name: getattr(self, field.name) for field in fields(self) if field.name != "contract_digest"}
        if (
            self.contract_id != S1_IP_CONTRACT_ID
            or self.source_s1io_audit_digest != S1_IP_SOURCE_S1IO_AUDIT_DIGEST
            or self.reference_receipts != S1_IP_REFERENCE_RECEIPTS
            or self.executable_baseline_roles != S1_IP_EXECUTABLE_BASELINE_ROLES
            or self.structural_baseline_roles != S1_IP_STRUCTURAL_BASELINE_ROLES
            or self.profile_blocks != S1_IP_PROFILE_BLOCKS
            or self.profile_rules != S1_IP_PROFILE_RULES
            or self.structural_gates != S1_IP_STRUCTURAL_GATES
            or self.allowed_baseline_inputs != S1_IP_ALLOWED_BASELINE_INPUTS
            or self.forbidden_baseline_inputs != S1_IP_FORBIDDEN_BASELINE_INPUTS
            or self.parameter_rules != S1_IP_PARAMETER_RULES
            or self.comparison_metrics != S1_IP_COMPARISON_METRICS
            or self.decision_order != S1_IP_DECISION_ORDER
            or self.stopp_conditions != S1_IP_STOPP_CONDITIONS
            or self.forbidden_interpretations != S1_IP_FORBIDDEN_INTERPRETATIONS
            or self.profile_component_count != 36
            or any(
                value is not False
                for value in (
                    self.parameter_values_selected,
                    self.comparison_threshold_selected,
                    self.geometry_adapters_implemented,
                    self.profile_container_implemented,
                    self.baseline_models_executed,
                    self.joint_comparison_executed,
                    self.runtime_integration_present,
                    self.research_execution_permitted,
                    self.baseline_closure_proven,
                    self.claims_permitted,
                )
            )
            or self.technical_field_steps_executed != 0
            or self.research_field_steps_executed != 0
            or self.compatibility_audit_authorized_next_stage is not True
            or self.atomic_decision_required is not True
            or self.decision != S1_IP_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1IPJointBaselineContractError("S1-IP weakened the joint baseline boundary")


def build_dts1_s1ip_joint_baseline_contract() -> DTS1S1IPJointBaselineContract:
    """Bind one joint baseline comparison without values or execution."""

    values = {
        "contract_id": S1_IP_CONTRACT_ID,
        "source_s1io_audit_digest": S1_IP_SOURCE_S1IO_AUDIT_DIGEST,
        "reference_receipts": S1_IP_REFERENCE_RECEIPTS,
        "executable_baseline_roles": S1_IP_EXECUTABLE_BASELINE_ROLES,
        "structural_baseline_roles": S1_IP_STRUCTURAL_BASELINE_ROLES,
        "profile_blocks": S1_IP_PROFILE_BLOCKS,
        "profile_rules": S1_IP_PROFILE_RULES,
        "structural_gates": S1_IP_STRUCTURAL_GATES,
        "allowed_baseline_inputs": S1_IP_ALLOWED_BASELINE_INPUTS,
        "forbidden_baseline_inputs": S1_IP_FORBIDDEN_BASELINE_INPUTS,
        "parameter_rules": S1_IP_PARAMETER_RULES,
        "comparison_metrics": S1_IP_COMPARISON_METRICS,
        "decision_order": S1_IP_DECISION_ORDER,
        "stopp_conditions": S1_IP_STOPP_CONDITIONS,
        "forbidden_interpretations": S1_IP_FORBIDDEN_INTERPRETATIONS,
        "profile_component_count": 36,
        "parameter_values_selected": False,
        "comparison_threshold_selected": False,
        "geometry_adapters_implemented": False,
        "profile_container_implemented": False,
        "baseline_models_executed": False,
        "joint_comparison_executed": False,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "technical_field_steps_executed": 0,
        "research_field_steps_executed": 0,
        "baseline_closure_proven": False,
        "claims_permitted": False,
        "compatibility_audit_authorized_next_stage": True,
        "atomic_decision_required": True,
        "decision": S1_IP_DECISION,
    }
    return DTS1S1IPJointBaselineContract(**values, contract_digest=_digest(values))
