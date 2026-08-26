"""S1-FH closed contract for one fresh nonpersistent formation capture."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_confirmation_full_formation_resource_preflight import (
    S1_EC12_EXPECTED_REFINEMENTS,
    S1_EC12_LIMITS,
)
from .e1_confirmation_full_published_release_audit import (
    S1_EC18_MAX_RUNTIME_SECONDS,
    S1_EC18_MIN_FREE_MEMORY_BYTES,
)
from .e1_confirmation_prepared_formation_consumer import S1_EC7_FORMATION_ARMS
from .e1_formation_s1fg_fresh_run_insertion_contract import (
    E1FormationS1FGFreshRunInsertionContract,
    audit_e1_formation_s1fg_fresh_run_insertion_contract,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FHFreshCaptureOneShotContractError(ValueError):
    """Raised when the S1-FH one-shot boundary changes or opens execution."""


S1_FH_CONTRACT_ID = "e1.formation-capture-fresh-one-shot.s1fh.v1"
S1_FH_EXECUTION_SEQUENCE = (
    "verify-new-run-identity",
    "verify-prepared-input-digests",
    "refresh-resource-preflight-before-attempt",
    "verify-new-explicit-owner-authorization",
    "refresh-resource-preflight-immediately-before-first-formation-arm",
    "execute-r2-r4-r8-five-arm-formation-once",
    "capture-fifteen-live-results-with-s1ff",
    "evaluate-fifteen-vectors-with-s1fd",
    "return-atomic-in-memory-diagnostic-only",
)
S1_FH_ABORT_CONDITIONS = (
    "new-run-identity-missing-or-reused",
    "prepared-input-digest-change",
    "owner-authorization-missing-or-mismatched",
    "resource-preflight-failed-or-changed",
    "runtime-cap-reached",
    "formation-inventory-or-step-count-changed",
    "formation-control-failed",
    "capture-inventory-or-digest-failed",
    "probe-requested",
    "persistence-requested",
    "retry-requested",
)
S1_FH_REPORT_SECTIONS = (
    "measurement",
    "technical-interpretation",
    "non-evidence",
    "open-assumptions",
)


@dataclass(frozen=True, slots=True)
class E1FormationS1FHFreshCaptureOneShotContract:
    contract_id: str
    source_s1fg_contract_digest: str
    run_kind: str
    world_scope: str
    refinements: tuple[tuple[str, int, int, int], ...]
    formation_arm_ids: tuple[str, ...]
    planned_execution_count: int
    authorized_execution_count: int
    formation_arm_count: int
    maximum_formation_field_steps: int
    capture_count: int
    evaluation_count: int
    retained_state_count: int
    retained_binding_count_upper_bound: int
    field_node_count: int
    state_edge_count: int
    minimum_free_memory_bytes: int
    maximum_runtime_seconds: float
    execution_sequence: tuple[str, ...]
    abort_conditions: tuple[str, ...]
    report_sections: tuple[str, ...]
    resource_limits: tuple[tuple[str, int], ...]
    fresh_preflight_required: bool
    immediate_pre_execution_preflight_required: bool
    explicit_new_owner_authorization_required: bool
    owner_authorization_present: bool
    execution_permitted: bool
    automatic_retry_permitted: bool
    posthoc_parameter_change_permitted: bool
    probe_execution_permitted: bool
    persistence_permitted: bool
    historical_artifact_reuse_permitted: bool
    historical_authorization_reuse_permitted: bool
    research_decision_permitted: bool
    memory_claim_permitted: bool
    field_time_claim_permitted: bool
    organization_claim_permitted: bool
    semantic_claim_permitted: bool
    self_regulation_claim_permitted: bool
    ai_claim_permitted: bool
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
            self.contract_id != S1_FH_CONTRACT_ID
            or len(self.source_s1fg_contract_digest) != 64
            or self.run_kind != "fresh-nonpersistent-formation-capture-once"
            or self.world_scope != "controlled-audiovisual-test-world-only"
            or self.refinements != S1_EC12_EXPECTED_REFINEMENTS
            or self.formation_arm_ids != S1_EC7_FORMATION_ARMS
            or (self.planned_execution_count, self.authorized_execution_count)
            != (1, 0)
            or self.formation_arm_count != 15
            or self.maximum_formation_field_steps != 14_000
            or (self.capture_count, self.evaluation_count) != (1, 1)
            or self.retained_state_count != 15
            or self.retained_binding_count_upper_bound != 2_175
            or (self.field_node_count, self.state_edge_count) != (84, 145)
            or self.minimum_free_memory_bytes != 4 * 1024**3
            or self.minimum_free_memory_bytes != S1_EC18_MIN_FREE_MEMORY_BYTES
            or self.maximum_runtime_seconds != 900.0
            or self.maximum_runtime_seconds != S1_EC18_MAX_RUNTIME_SECONDS
            or self.execution_sequence != S1_FH_EXECUTION_SEQUENCE
            or self.abort_conditions != S1_FH_ABORT_CONDITIONS
            or self.report_sections != S1_FH_REPORT_SECTIONS
            or self.resource_limits != S1_EC12_LIMITS
            or any(
                value is not True
                for value in (
                    self.fresh_preflight_required,
                    self.immediate_pre_execution_preflight_required,
                    self.explicit_new_owner_authorization_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.owner_authorization_present,
                    self.execution_permitted,
                    self.automatic_retry_permitted,
                    self.posthoc_parameter_change_permitted,
                    self.probe_execution_permitted,
                    self.persistence_permitted,
                    self.historical_artifact_reuse_permitted,
                    self.historical_authorization_reuse_permitted,
                    self.research_decision_permitted,
                    self.memory_claim_permitted,
                    self.field_time_claim_permitted,
                    self.organization_claim_permitted,
                    self.semantic_claim_permitted,
                    self.self_regulation_claim_permitted,
                    self.ai_claim_permitted,
                )
            )
            or self.decision
            != "FRESH_FORMATION_CAPTURE_ONE_SHOT_BOUND_AWAITING_PREFLIGHT_AND_OWNER_AUTHORIZATION"
            or not self.reason
            or self.contract_digest != _digest(payload)
        ):
            raise E1FormationS1FHFreshCaptureOneShotContractError(
                "S1-FH one-shot contract changed or opened execution"
            )


def prepare_e1_formation_s1fh_fresh_capture_one_shot_contract(
    insertion: E1FormationS1FGFreshRunInsertionContract | None = None,
) -> E1FormationS1FHFreshCaptureOneShotContract:
    """Bind one closed fresh attempt without accepting authorization."""

    source = insertion or audit_e1_formation_s1fg_fresh_run_insertion_contract()
    if not isinstance(source, E1FormationS1FGFreshRunInsertionContract):
        raise E1FormationS1FHFreshCaptureOneShotContractError(
            "S1-FH requires the typed S1-FG insertion contract"
        )
    source.__post_init__()
    if (
        source.fresh_run_contract_required is not True
        or source.new_owner_authorization_required is not True
        or source.formation_execution_permitted is not False
        or source.capture_execution_permitted is not False
        or source.probe_execution_permitted is not False
        or source.persistence_permitted is not False
    ):
        raise E1FormationS1FHFreshCaptureOneShotContractError(
            "S1-FH requires the closed S1-FG insertion boundary"
        )
    values = {
        "contract_id": S1_FH_CONTRACT_ID,
        "source_s1fg_contract_digest": source.contract_digest,
        "run_kind": "fresh-nonpersistent-formation-capture-once",
        "world_scope": "controlled-audiovisual-test-world-only",
        "refinements": S1_EC12_EXPECTED_REFINEMENTS,
        "formation_arm_ids": S1_EC7_FORMATION_ARMS,
        "planned_execution_count": 1,
        "authorized_execution_count": 0,
        "formation_arm_count": 15,
        "maximum_formation_field_steps": 14_000,
        "capture_count": 1,
        "evaluation_count": 1,
        "retained_state_count": 15,
        "retained_binding_count_upper_bound": 2_175,
        "field_node_count": 84,
        "state_edge_count": 145,
        "minimum_free_memory_bytes": S1_EC18_MIN_FREE_MEMORY_BYTES,
        "maximum_runtime_seconds": S1_EC18_MAX_RUNTIME_SECONDS,
        "execution_sequence": S1_FH_EXECUTION_SEQUENCE,
        "abort_conditions": S1_FH_ABORT_CONDITIONS,
        "report_sections": S1_FH_REPORT_SECTIONS,
        "resource_limits": S1_EC12_LIMITS,
        "fresh_preflight_required": True,
        "immediate_pre_execution_preflight_required": True,
        "explicit_new_owner_authorization_required": True,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "automatic_retry_permitted": False,
        "posthoc_parameter_change_permitted": False,
        "probe_execution_permitted": False,
        "persistence_permitted": False,
        "historical_artifact_reuse_permitted": False,
        "historical_authorization_reuse_permitted": False,
        "research_decision_permitted": False,
        "memory_claim_permitted": False,
        "field_time_claim_permitted": False,
        "organization_claim_permitted": False,
        "semantic_claim_permitted": False,
        "self_regulation_claim_permitted": False,
        "ai_claim_permitted": False,
        "decision": (
            "FRESH_FORMATION_CAPTURE_ONE_SHOT_BOUND_AWAITING_"
            "PREFLIGHT_AND_OWNER_AUTHORIZATION"
        ),
        "reason": (
            "one-fresh-fourteen-thousand-step-formation-capture-attempt-bound;"
            "new-preflight-and-explicit-owner-authorization-absent"
        ),
    }
    return E1FormationS1FHFreshCaptureOneShotContract(
        **values,
        contract_digest=_digest(values),
    )
