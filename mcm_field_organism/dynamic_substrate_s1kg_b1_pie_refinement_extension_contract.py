"""Static S1-KG contract for the finite B1/P_IE r4/r8 extension."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_KF_COMPARISON_SCHEMA_ID,
    S1_KF_EXEMPLAR_COMPARISON_DIGEST,
    S1_KF_OUTPUT_SCHEMA_ID,
    build_dts1_s1kf_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_REPLICA_RECORDS,
)


class DTS1S1KGB1PIERefinementExtensionContractError(ValueError):
    """Raised when the finite S1-KG extension contract is weakened."""


S1_KG_CONTRACT_ID = "dynamic-substrate.b1-pie-refinement-extension.s1kg.v1"
S1_KG_SOURCE_S1KF_DIGEST = (
    "ab0d783e83a6d905428da2b87c5be32090e866191abe30c0cee90835ff80e7ff"
)
S1_KG_BOUND_R2_COMPARISON_DIGEST = (
    "276f2891e11e2e5a0b22f8dbf65594dc26e217bec28a526a02632bc20334d589"
)
S1_KG_TARGET_REPLICA_IDS = (
    "B1:P_IE_CAUSAL_TWO_SUBSTEP:r4",
    "B1:P_IE_CAUSAL_TWO_SUBSTEP:r8",
)
S1_KG_TARGET_REPLICA_RECORDS = tuple(
    row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_KG_TARGET_REPLICA_IDS
)
S1_KG_INPUT_REGISTRY_EXTENSION = (
    ("existing_id", "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2"),
    ("new_ids", S1_KG_TARGET_REPLICA_IDS),
    ("caller_fields", ("schema_id", "replica_id")),
    ("caller_supplied_state_or_parameters", False),
)
S1_KG_FRESH_START_RULES = (
    "r4-and-r8-each-start-from-an-independent-S1-KB-corrected-B1-fresh-state",
    "P_IE_F_HIGH-and-P_IE_R_HIGH-each-start-fresh-inside-each-refinement-replica",
    "no-field-private-state-or-provenance-carries-between-r2-r4-or-r8",
    "carry-remains-confined-to-the-two-ordered-intervals-of-one-sequence",
)
S1_KG_EXECUTION_BUDGET = (
    ("r4_replica_count", 1),
    ("r8_replica_count", 1),
    ("interval_calls_per_replica", 4),
    ("maximum_new_interval_calls", 8),
    ("retry_or_repeat_calls", 0),
)
S1_KG_OUTPUT_ACCEPTANCE_RULES = (
    "each-target-publishes-one-atomic-mcm.s1jz.complete-replica-output.v2-or-one-error",
    "each-target-output-contains-one-valid-mcm.s1ke.refinement-comparison-content.v1-digest",
    "r4-and-r8-refinement_comparison_digest-must-bit-equal-the-bound-r2-comparison-digest",
    "r2-r4-r8-complete-output-digests-remain-identity-bearing-and-must-not-be-used-for-equality",
    "both-r4-and-r8-must-pass-or-the-extension-publishes-no-accepted-three-refinement-set",
)
S1_KG_FORBIDDEN_SCOPE = (
    "no-B2-through-B6-or-DTS1-runner-extension",
    "no-threshold-fit-ranking-baseline-closure-or-candidate-comparison",
    "no-complete-24-case-matrix-publication",
    "no-runtime-integration-or-research-execution",
)
S1_KG_DECISION = (
    "FINITE_B1_P_IE_R4_R8_DUAL_DIGEST_EXTENSION_BOUND_EIGHT_CALL_BUDGET_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1KGB1PIERefinementExtensionContract:
    contract_id: str
    source_s1kf_digest: str
    bound_r2_comparison_digest: str
    output_schema_id: str
    comparison_schema_id: str
    target_replica_ids: tuple[str, ...]
    target_replica_records: tuple[tuple[object, ...], ...]
    input_registry_extension: tuple[tuple[str, object], ...]
    fresh_start_rules: tuple[str, ...]
    execution_budget: tuple[tuple[str, int], ...]
    output_acceptance_rules: tuple[str, ...]
    forbidden_scope: tuple[str, ...]
    target_replica_count: int
    intervals_per_target_replica: int
    maximum_new_interval_calls: int
    runner_extension_implemented: bool
    target_replicas_executed: int
    interval_calls_executed: int
    complete_matrix_cases_executed: int
    runtime_integration_present: bool
    exact_extension_implementation_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_KG_CONTRACT_ID
            or self.source_s1kf_digest != S1_KG_SOURCE_S1KF_DIGEST
            or self.bound_r2_comparison_digest != S1_KG_BOUND_R2_COMPARISON_DIGEST
            or self.output_schema_id != S1_KF_OUTPUT_SCHEMA_ID
            or self.comparison_schema_id != S1_KF_COMPARISON_SCHEMA_ID
            or self.target_replica_ids != S1_KG_TARGET_REPLICA_IDS
            or self.target_replica_records != S1_KG_TARGET_REPLICA_RECORDS
            or self.input_registry_extension != S1_KG_INPUT_REGISTRY_EXTENSION
            or self.fresh_start_rules != S1_KG_FRESH_START_RULES
            or self.execution_budget != S1_KG_EXECUTION_BUDGET
            or self.output_acceptance_rules != S1_KG_OUTPUT_ACCEPTANCE_RULES
            or self.forbidden_scope != S1_KG_FORBIDDEN_SCOPE
            or self.target_replica_count != 2
            or self.intervals_per_target_replica != 4
            or self.maximum_new_interval_calls != 8
            or self.runner_extension_implemented is not False
            or self.target_replicas_executed != 0
            or self.interval_calls_executed != 0
            or self.complete_matrix_cases_executed != 0
            or self.runtime_integration_present is not False
            or self.exact_extension_implementation_authorized_next_stage is not True
            or self.decision != S1_KG_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KGB1PIERefinementExtensionContractError(
                "S1-KG weakened the finite B1/P_IE refinement extension"
            )


def build_dts1_s1kg_b1_pie_refinement_extension_contract(
) -> DTS1S1KGB1PIERefinementExtensionContract:
    """Bind exactly r4 and r8 without changing or invoking the runner."""

    source = build_dts1_s1kf_implementation_receipt()
    if (
        source.receipt_digest != S1_KG_SOURCE_S1KF_DIGEST
        or source.repeat_comparison_digests
        != (S1_KF_EXEMPLAR_COMPARISON_DIGEST,) * 2
    ):
        raise DTS1S1KGB1PIERefinementExtensionContractError(
            "S1-KF source differs from the bound r2 comparison"
        )
    values = {
        "contract_id": S1_KG_CONTRACT_ID,
        "source_s1kf_digest": source.receipt_digest,
        "bound_r2_comparison_digest": S1_KG_BOUND_R2_COMPARISON_DIGEST,
        "output_schema_id": S1_KF_OUTPUT_SCHEMA_ID,
        "comparison_schema_id": S1_KF_COMPARISON_SCHEMA_ID,
        "target_replica_ids": S1_KG_TARGET_REPLICA_IDS,
        "target_replica_records": S1_KG_TARGET_REPLICA_RECORDS,
        "input_registry_extension": S1_KG_INPUT_REGISTRY_EXTENSION,
        "fresh_start_rules": S1_KG_FRESH_START_RULES,
        "execution_budget": S1_KG_EXECUTION_BUDGET,
        "output_acceptance_rules": S1_KG_OUTPUT_ACCEPTANCE_RULES,
        "forbidden_scope": S1_KG_FORBIDDEN_SCOPE,
        "target_replica_count": len(S1_KG_TARGET_REPLICA_IDS),
        "intervals_per_target_replica": 4,
        "maximum_new_interval_calls": 8,
        "runner_extension_implemented": False,
        "target_replicas_executed": 0,
        "interval_calls_executed": 0,
        "complete_matrix_cases_executed": 0,
        "runtime_integration_present": False,
        "exact_extension_implementation_authorized_next_stage": True,
        "decision": S1_KG_DECISION,
    }
    return DTS1S1KGB1PIERefinementExtensionContract(
        **values, contract_digest=_digest(values)
    )
