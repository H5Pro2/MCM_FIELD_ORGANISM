"""Static S1-LB complete B2/P_IK C07 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_LA_TARGET_COMPARISON_DIGEST,
    S1_LA_TARGET_COMPONENTS,
    S1_LA_TARGET_OUTPUT_DIGESTS,
    S1_LA_TARGET_REPLICA_IDS,
    S1_LA_TERMINAL_ADAPTER_OUTPUT_DIGESTS,
    S1_LA_TERMINAL_FIELD_DIGESTS,
    S1_LA_TERMINAL_PRIVATE_STATE_DIGESTS,
    build_dts1_s1la_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import S1_JX_CASE_RECORDS
from .dynamic_substrate_s1ky_b1_pik_case_output_contract import build_dts1_s1ky_b1_pik_case_output_contract


class DTS1S1LBB2PIKCaseOutputContractError(ValueError):
    """Raised when the finite S1-LB C07 case output is weakened."""


S1_LB_CONTRACT_ID = "dynamic-substrate.b2-pik-case-output.s1lb.v1"
S1_LB_SOURCE_S1KY_DIGEST = "0877c42df920ef9302cf46fc5c4247638b456cf3961d640e9b3752629e5f96f9"
S1_LB_SOURCE_S1LA_DIGEST = "40d7e333af46e9bcdfb476648d62dd589428cc4fae07ee233d55017de5d19d25"
S1_LB_CASE_ID = "C07"
S1_LB_COMPONENTS_BY_REFINEMENT = tuple((refinement, S1_LA_TARGET_COMPONENTS) for refinement in (2, 4, 8))
S1_LB_CASE_SCHEMA = (
    ("schema_id", "mcm.s1lb.complete-three-refinement-case.v1"),
    ("fields", (
        "schema_id", "case_id", "model_role", "long_model_role", "profile_block",
        "node_count", "component_count", "replica_ids", "replica_output_digests",
        "refinement_comparison_digest", "components_by_refinement",
        "terminal_field_digests", "terminal_private_state_digests",
        "terminal_adapter_output_digests", "primary_refinement", "primary_components",
        "checkpoint_parent_identity_valid", "sequence_terminals_distinct",
        "refinement_bit_identity", "status", "case_output_digest",
    )),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_LB_STATUS = "TECHNICALLY_COMPLETE_NO_INTERFERENCE_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_LB_DECISION = "C07_B2_PIK_THREE_REFINEMENT_CASE_OUTPUT_BOUND_FROM_S1LA_RECEIPT_NO_NEW_EXECUTION"


def _digest(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1lb.complete-three-refinement-case.v1",
        "case_id": S1_LB_CASE_ID,
        "model_role": "B2",
        "long_model_role": "B2_S2_LINEAR_INTEGRATOR",
        "profile_block": "P_IK_INTERFERENCE",
        "node_count": 3,
        "component_count": 6,
        "replica_ids": S1_LA_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_LA_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digest": S1_LA_TARGET_COMPARISON_DIGEST,
        "components_by_refinement": S1_LB_COMPONENTS_BY_REFINEMENT,
        "terminal_field_digests": S1_LA_TERMINAL_FIELD_DIGESTS,
        "terminal_private_state_digests": S1_LA_TERMINAL_PRIVATE_STATE_DIGESTS,
        "terminal_adapter_output_digests": S1_LA_TERMINAL_ADAPTER_OUTPUT_DIGESTS,
        "primary_refinement": 4,
        "primary_components": S1_LA_TARGET_COMPONENTS,
        "checkpoint_parent_identity_valid": True,
        "sequence_terminals_distinct": True,
        "refinement_bit_identity": True,
        "status": S1_LB_STATUS,
    }


S1_LB_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1LBB2PIKCaseOutputContract:
    contract_id: str
    source_s1ky_digest: str
    source_s1la_digest: str
    source_s1jx_case_record: tuple[object, ...]
    case_schema: tuple[tuple[str, object], ...]
    case_payload: tuple[tuple[str, object], ...]
    case_output_digest: str
    replica_count: int
    sequence_count_per_refinement: int
    checkpoint_count_per_refinement: int
    component_count_per_refinement: int
    primary_refinement: int
    comparison_digest_count: int
    distinct_provenance_digest_count: int
    checkpoint_parent_identity_valid: bool
    sequence_terminals_distinct: bool
    terminal_digest_pairs_bit_identical_across_refinements: bool
    all_components_bit_identical: bool
    nonzero_component_count: int
    case_record_composed: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    matrix_24_case_output_published: bool
    interference_judgment_present: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    runtime_integration_present: bool
    b1_pin_case_selection_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {field.name: getattr(self, field.name) for field in fields(self) if field.name != "contract_digest"}
        expected_case = next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_LB_CASE_ID)
        if (
            self.contract_id != S1_LB_CONTRACT_ID
            or self.source_s1ky_digest != S1_LB_SOURCE_S1KY_DIGEST
            or self.source_s1la_digest != S1_LB_SOURCE_S1LA_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.case_schema != S1_LB_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_LB_CASE_OUTPUT_DIGEST
            or (self.replica_count, self.sequence_count_per_refinement, self.checkpoint_count_per_refinement, self.component_count_per_refinement) != (3, 2, 2, 6)
            or (self.primary_refinement, self.comparison_digest_count, self.distinct_provenance_digest_count) != (4, 1, 3)
            or self.checkpoint_parent_identity_valid is not True
            or self.sequence_terminals_distinct is not True
            or self.terminal_digest_pairs_bit_identical_across_refinements is not True
            or self.all_components_bit_identical is not True
            or self.nonzero_component_count != 6
            or self.case_record_composed is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.matrix_24_case_output_published is not False
            or self.interference_judgment_present is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.b1_pin_case_selection_authorized_next_stage is not True
            or self.decision != S1_LB_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LBB2PIKCaseOutputContractError("S1-LB weakened the complete C07 case output")


def build_dts1_s1lb_b2_pik_case_output_contract() -> DTS1S1LBB2PIKCaseOutputContract:
    """Compose C07 from bound receipts without executing a replica."""

    prior = build_dts1_s1ky_b1_pik_case_output_contract()
    source = build_dts1_s1la_implementation_receipt()
    if (
        prior.contract_digest != S1_LB_SOURCE_S1KY_DIGEST
        or source.receipt_digest != S1_LB_SOURCE_S1LA_DIGEST
        or source.target_output_digests != S1_LA_TARGET_OUTPUT_DIGESTS
        or source.target_components != S1_LA_TARGET_COMPONENTS
        or source.terminal_field_digests != S1_LA_TERMINAL_FIELD_DIGESTS
        or source.terminal_private_state_digests != S1_LA_TERMINAL_PRIVATE_STATE_DIGESTS
        or source.terminal_adapter_output_digests != S1_LA_TERMINAL_ADAPTER_OUTPUT_DIGESTS
    ):
        raise DTS1S1LBB2PIKCaseOutputContractError("S1-KY sequence source or S1-LA output source differs")
    components = tuple(row[1] for row in S1_LB_COMPONENTS_BY_REFINEMENT)
    values = {
        "contract_id": S1_LB_CONTRACT_ID,
        "source_s1ky_digest": prior.contract_digest,
        "source_s1la_digest": source.receipt_digest,
        "source_s1jx_case_record": next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_LB_CASE_ID),
        "case_schema": S1_LB_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_LB_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "sequence_count_per_refinement": 2,
        "checkpoint_count_per_refinement": 2,
        "component_count_per_refinement": 6,
        "primary_refinement": 4,
        "comparison_digest_count": 1,
        "distinct_provenance_digest_count": len(set(S1_LA_TARGET_OUTPUT_DIGESTS)),
        "checkpoint_parent_identity_valid": True,
        "sequence_terminals_distinct": all(len(set(values)) == 2 for values in (S1_LA_TERMINAL_FIELD_DIGESTS, S1_LA_TERMINAL_PRIVATE_STATE_DIGESTS, S1_LA_TERMINAL_ADAPTER_OUTPUT_DIGESTS)),
        "terminal_digest_pairs_bit_identical_across_refinements": True,
        "all_components_bit_identical": len(set(components)) == 1,
        "nonzero_component_count": sum(value != 0.0 for value in S1_LA_TARGET_COMPONENTS),
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "interference_judgment_present": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "b1_pin_case_selection_authorized_next_stage": True,
        "decision": S1_LB_DECISION,
    }
    return DTS1S1LBB2PIKCaseOutputContract(**values, contract_digest=_digest(values))
