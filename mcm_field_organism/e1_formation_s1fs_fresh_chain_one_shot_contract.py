"""S1-FS closed one-shot contract for one fresh formation-probe chain."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_formation_s1fr_static_resource_matrix_audit import (
    E1FormationS1FRStaticResourceMatrixAudit,
    S1_FR_EXPECTED_BUDGETS,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FSFreshChainOneShotContractError(ValueError):
    """Raised when S1-FS changes scope or opens the real chain."""


S1_FS_CONTRACT_ID = "e1.fresh-formation-common-probe-one-shot.s1fs.v1"
S1_FS_EXECUTION_SEQUENCE = (
    "verify-new-run-identity-and-fresh-process",
    "verify-typed-input-and-plan-digests",
    "refresh-resource-preflight-before-attempt",
    "verify-new-exact-owner-authorization",
    "refresh-resource-preflight-immediately-before-first-formation-arm",
    "execute-fifteen-r2-r4-r8-formation-arms-once",
    "capture-and-validate-all-fifteen-live-formation-states",
    "abort-before-probe-unless-formation-controls-pass",
    "create-thirty-value-identical-object-separated-fresh-probe-fields",
    "execute-thirty-frozen-state-common-probe-arms-once",
    "return-one-atomic-in-memory-formation-and-probe-result",
    "evaluate-ec46-and-fixed-adapter-explanation-after-return-only",
)
S1_FS_ABORT_CONDITIONS = (
    "new-run-identity-missing-or-reused",
    "typed-input-plan-or-source-digest-change",
    "owner-authorization-missing-consumed-or-mismatched",
    "resource-preflight-failed-or-changed",
    "runtime-or-field-step-cap-reached",
    "formation-call-inventory-or-control-failed",
    "formation-state-capture-or-digest-failed",
    "probe-field-not-fresh-equal-or-object-separated",
    "formed-state-changed-during-probe",
    "probe-call-inventory-or-control-failed",
    "partial-or-nonatomic-result",
    "persistence-retry-or-posthoc-change-requested",
)
S1_FS_RETURN_COMPONENTS = (
    "fifteen-formation-result-receipts-and-state-digests",
    "thirty-probe-result-receipts-and-field-digests",
    "r2-r4-r8-active-order-activation-vectors",
    "r2-r4-r8-active-order-afterimage-vectors",
    "p0-feedback-and-formation-ablation-control-vectors",
    "active-versus-fixed-adapter-vectors-for-ab-and-ba",
    "exact-per-arm-and-total-field-step-accounting",
    "pre-and-post-input-state-and-plan-digests",
)
S1_FS_REPORT_SECTIONS = (
    "measurement",
    "technical-interpretation",
    "non-evidence",
    "open-assumptions",
)


@dataclass(frozen=True, slots=True)
class E1FormationS1FSFreshChainOneShotContract:
    contract_id: str
    source_s1fr_audit_digest: str
    run_kind: str
    world_scope: str
    budgets: tuple[tuple[str, int, int, int, int, int, int, int, int], ...]
    planned_execution_count: int
    authorized_execution_count: int
    formation_call_count: int
    probe_call_count: int
    total_field_call_count: int
    maximum_formation_field_steps: int
    maximum_probe_field_steps: int
    maximum_total_field_steps: int
    retained_formation_state_count: int
    retained_binding_count_upper_bound: int
    field_node_count: int
    state_edge_count: int
    minimum_free_memory_bytes: int
    maximum_runtime_seconds: float
    execution_sequence: tuple[str, ...]
    abort_conditions: tuple[str, ...]
    atomic_return_components: tuple[str, ...]
    report_sections: tuple[str, ...]
    same_session_fresh_formation_and_probe_required: bool
    immediate_pre_execution_resource_preflight_required: bool
    formation_acceptance_required_before_probe: bool
    fresh_object_separated_field_per_probe_required: bool
    formed_state_frozen_during_probe_required: bool
    atomic_result_required: bool
    evaluation_after_atomic_return_only: bool
    fixed_adapter_evaluation_separate_required: bool
    explicit_new_owner_authorization_required: bool
    preflight_implementation_permitted: bool
    owner_authorization_present: bool
    execution_permitted: bool
    real_runner_implementation_permitted: bool
    partial_result_decision_permitted: bool
    automatic_retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    persistence_permitted: bool
    historical_state_reuse_permitted: bool
    historical_authorization_reuse_permitted: bool
    research_decision_during_run_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if (
            self.contract_id != S1_FS_CONTRACT_ID
            or len(self.source_s1fr_audit_digest) != 64
            or self.run_kind != "fresh-nonpersistent-formation-common-probe-once"
            or self.world_scope != "controlled-audiovisual-test-world-only"
            or self.budgets != S1_FR_EXPECTED_BUDGETS
            or (self.planned_execution_count, self.authorized_execution_count)
            != (1, 0)
            or (
                self.formation_call_count,
                self.probe_call_count,
                self.total_field_call_count,
            )
            != (15, 30, 45)
            or (
                self.maximum_formation_field_steps,
                self.maximum_probe_field_steps,
                self.maximum_total_field_steps,
            )
            != (14_000, 14_000, 28_000)
            or self.retained_formation_state_count != 15
            or self.retained_binding_count_upper_bound != 2_175
            or (self.field_node_count, self.state_edge_count) != (84, 145)
            or self.minimum_free_memory_bytes != 4 * 1024**3
            or self.maximum_runtime_seconds != 1_800.0
            or self.execution_sequence != S1_FS_EXECUTION_SEQUENCE
            or self.abort_conditions != S1_FS_ABORT_CONDITIONS
            or self.atomic_return_components != S1_FS_RETURN_COMPONENTS
            or self.report_sections != S1_FS_REPORT_SECTIONS
            or any(
                value is not True
                for value in (
                    self.same_session_fresh_formation_and_probe_required,
                    self.immediate_pre_execution_resource_preflight_required,
                    self.formation_acceptance_required_before_probe,
                    self.fresh_object_separated_field_per_probe_required,
                    self.formed_state_frozen_during_probe_required,
                    self.atomic_result_required,
                    self.evaluation_after_atomic_return_only,
                    self.fixed_adapter_evaluation_separate_required,
                    self.explicit_new_owner_authorization_required,
                    self.preflight_implementation_permitted,
                )
            )
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.real_runner_implementation_permitted,
                    self.partial_result_decision_permitted,
                    self.automatic_retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.persistence_permitted,
                    self.historical_state_reuse_permitted,
                    self.historical_authorization_reuse_permitted,
                    self.research_decision_during_run_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "FRESH_CHAIN_ONE_SHOT_BOUND_AWAITING_PREFLIGHT_AND_EXPLICIT_OWNER_AUTHORIZATION"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1FSFreshChainOneShotContractError(
                "S1-FS one-shot contract changed or opened execution"
            )


def prepare_e1_formation_s1fs_fresh_chain_one_shot_contract(
    audit: E1FormationS1FRStaticResourceMatrixAudit,
) -> E1FormationS1FSFreshChainOneShotContract:
    """Bind one closed fresh chain without accepting authorization."""

    if not isinstance(audit, E1FormationS1FRStaticResourceMatrixAudit):
        raise E1FormationS1FSFreshChainOneShotContractError(
            "S1-FS requires the typed S1-FR audit"
        )
    audit.__post_init__()
    if (
        audit.decision != "FULL_45_ARM_MATRIX_REQUIRED_STATIC_BUDGET_BOUND"
        or audit.total_field_steps != 28_000
        or audit.causally_equivalent_matrix_reduction_available is not False
        or audit.owner_authorization_present is not False
        or audit.execution_permitted is not False
    ):
        raise E1FormationS1FSFreshChainOneShotContractError(
            "S1-FS requires the complete closed S1-FR matrix"
        )
    values = {
        "contract_id": S1_FS_CONTRACT_ID,
        "source_s1fr_audit_digest": audit.audit_digest,
        "run_kind": "fresh-nonpersistent-formation-common-probe-once",
        "world_scope": "controlled-audiovisual-test-world-only",
        "budgets": audit.budgets,
        "planned_execution_count": 1,
        "authorized_execution_count": 0,
        "formation_call_count": audit.formation_call_count,
        "probe_call_count": audit.probe_call_count,
        "total_field_call_count": audit.total_field_call_count,
        "maximum_formation_field_steps": audit.formation_field_steps,
        "maximum_probe_field_steps": audit.probe_field_steps,
        "maximum_total_field_steps": audit.total_field_steps,
        "retained_formation_state_count": audit.retained_formation_state_count,
        "retained_binding_count_upper_bound": audit.retained_binding_count,
        "field_node_count": audit.field_node_count,
        "state_edge_count": audit.state_edge_count,
        "minimum_free_memory_bytes": audit.minimum_free_memory_bytes,
        "maximum_runtime_seconds": 1_800.0,
        "execution_sequence": S1_FS_EXECUTION_SEQUENCE,
        "abort_conditions": S1_FS_ABORT_CONDITIONS,
        "atomic_return_components": S1_FS_RETURN_COMPONENTS,
        "report_sections": S1_FS_REPORT_SECTIONS,
        "same_session_fresh_formation_and_probe_required": True,
        "immediate_pre_execution_resource_preflight_required": True,
        "formation_acceptance_required_before_probe": True,
        "fresh_object_separated_field_per_probe_required": True,
        "formed_state_frozen_during_probe_required": True,
        "atomic_result_required": True,
        "evaluation_after_atomic_return_only": True,
        "fixed_adapter_evaluation_separate_required": True,
        "explicit_new_owner_authorization_required": True,
        "preflight_implementation_permitted": True,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "real_runner_implementation_permitted": False,
        "partial_result_decision_permitted": False,
        "automatic_retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "persistence_permitted": False,
        "historical_state_reuse_permitted": False,
        "historical_authorization_reuse_permitted": False,
        "research_decision_during_run_permitted": False,
        "claims_permitted": False,
        "decision": (
            "FRESH_CHAIN_ONE_SHOT_BOUND_AWAITING_PREFLIGHT_AND_"
            "EXPLICIT_OWNER_AUTHORIZATION"
        ),
        "reason": (
            "one-fresh-45-call-28000-step-chain-bound;formation-must-pass-"
            "before-probe;atomic-return-and-post-return-evaluation-required;"
            "preflight-and-explicit-owner-authorization-absent"
        ),
    }
    return E1FormationS1FSFreshChainOneShotContract(
        **values,
        contract_digest=_digest(values),
    )
