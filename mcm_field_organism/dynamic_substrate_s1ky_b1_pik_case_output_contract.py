"""Static S1-KY complete B1/P_IK C03 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_KX_TARGET_COMPARISON_DIGEST,
    S1_KX_TARGET_COMPONENTS,
    S1_KX_TARGET_OUTPUT_DIGESTS,
    S1_KX_TARGET_REPLICA_IDS,
    S1_KX_TERMINAL_ADAPTER_OUTPUT_DIGEST,
    S1_KX_TERMINAL_FIELD_DIGEST,
    S1_KX_TERMINAL_PRIVATE_STATE_DIGEST,
    build_dts1_s1kx_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import S1_JX_CASE_RECORDS
from .dynamic_substrate_s1kv_b2_pih_case_output_contract import build_dts1_s1kv_b2_pih_case_output_contract


class DTS1S1KYB1PIKCaseOutputContractError(ValueError):
    """Raised when the finite S1-KY C03 case output is weakened."""


S1_KY_CONTRACT_ID = "dynamic-substrate.b1-pik-case-output.s1ky.v1"
S1_KY_SOURCE_S1KV_DIGEST = "495139baff29222708e261d0be4c949cf403b6dd6af267670da8774d84cfaf41"
S1_KY_SOURCE_S1KX_DIGEST = "aebf334b2c1113a91e871c6aecb079fa9a8d559d12ee943238a28bee403a38b4"
S1_KY_CASE_ID = "C03"
S1_KY_COMPONENTS_BY_REFINEMENT = tuple((refinement, S1_KX_TARGET_COMPONENTS) for refinement in (2, 4, 8))
S1_KY_TERMINAL_FIELD_DIGESTS = (S1_KX_TERMINAL_FIELD_DIGEST,) * 2
S1_KY_TERMINAL_PRIVATE_STATE_DIGESTS = (S1_KX_TERMINAL_PRIVATE_STATE_DIGEST,) * 2
S1_KY_TERMINAL_ADAPTER_OUTPUT_DIGESTS = (S1_KX_TERMINAL_ADAPTER_OUTPUT_DIGEST,) * 2
S1_KY_CASE_SCHEMA = (
    ("schema_id", "mcm.s1ky.complete-three-refinement-case.v1"),
    ("fields", (
        "schema_id", "case_id", "model_role", "long_model_role", "profile_block",
        "node_count", "component_count", "replica_ids", "replica_output_digests",
        "refinement_comparison_digest", "components_by_refinement",
        "terminal_field_digests", "terminal_private_state_digests",
        "terminal_adapter_output_digests", "primary_refinement", "primary_components",
        "checkpoint_parent_identity_valid", "sequence_terminal_bit_identity",
        "refinement_bit_identity", "status", "case_output_digest",
    )),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_KY_STATUS = "TECHNICALLY_COMPLETE_NO_INTERFERENCE_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_KY_DECISION = "C03_B1_PIK_THREE_REFINEMENT_CASE_OUTPUT_BOUND_FROM_S1KX_RECEIPT_NO_NEW_EXECUTION"


def _digest(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1ky.complete-three-refinement-case.v1",
        "case_id": S1_KY_CASE_ID,
        "model_role": "B1",
        "long_model_role": "B1_FIXED_PRERELEASE_ADAPTER",
        "profile_block": "P_IK_INTERFERENCE",
        "node_count": 3,
        "component_count": 6,
        "replica_ids": S1_KX_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_KX_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digest": S1_KX_TARGET_COMPARISON_DIGEST,
        "components_by_refinement": S1_KY_COMPONENTS_BY_REFINEMENT,
        "terminal_field_digests": S1_KY_TERMINAL_FIELD_DIGESTS,
        "terminal_private_state_digests": S1_KY_TERMINAL_PRIVATE_STATE_DIGESTS,
        "terminal_adapter_output_digests": S1_KY_TERMINAL_ADAPTER_OUTPUT_DIGESTS,
        "primary_refinement": 4,
        "primary_components": S1_KX_TARGET_COMPONENTS,
        "checkpoint_parent_identity_valid": True,
        "sequence_terminal_bit_identity": True,
        "refinement_bit_identity": True,
        "status": S1_KY_STATUS,
    }


S1_KY_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1KYB1PIKCaseOutputContract:
    contract_id: str
    source_s1kv_digest: str
    source_s1kx_digest: str
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
    sequence_terminal_bit_identity: bool
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
    b2_pik_case_selection_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {field.name: getattr(self, field.name) for field in fields(self) if field.name != "contract_digest"}
        expected_case = next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_KY_CASE_ID)
        if (
            self.contract_id != S1_KY_CONTRACT_ID
            or self.source_s1kv_digest != S1_KY_SOURCE_S1KV_DIGEST
            or self.source_s1kx_digest != S1_KY_SOURCE_S1KX_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.case_schema != S1_KY_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_KY_CASE_OUTPUT_DIGEST
            or (self.replica_count, self.sequence_count_per_refinement, self.checkpoint_count_per_refinement, self.component_count_per_refinement) != (3, 2, 2, 6)
            or (self.primary_refinement, self.comparison_digest_count, self.distinct_provenance_digest_count) != (4, 1, 3)
            or self.checkpoint_parent_identity_valid is not True
            or self.sequence_terminal_bit_identity is not True
            or self.all_components_bit_identical is not True
            or self.nonzero_component_count != 0
            or self.case_record_composed is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.matrix_24_case_output_published is not False
            or self.interference_judgment_present is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.b2_pik_case_selection_authorized_next_stage is not True
            or self.decision != S1_KY_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KYB1PIKCaseOutputContractError("S1-KY weakened the complete C03 case output")


def build_dts1_s1ky_b1_pik_case_output_contract() -> DTS1S1KYB1PIKCaseOutputContract:
    """Compose C03 from bound receipts without executing a replica."""

    prior = build_dts1_s1kv_b2_pih_case_output_contract()
    source = build_dts1_s1kx_implementation_receipt()
    if (
        prior.contract_digest != S1_KY_SOURCE_S1KV_DIGEST
        or source.receipt_digest != S1_KY_SOURCE_S1KX_DIGEST
        or source.target_output_digests != S1_KX_TARGET_OUTPUT_DIGESTS
        or source.target_components != S1_KX_TARGET_COMPONENTS
        or source.terminal_field_digests != S1_KY_TERMINAL_FIELD_DIGESTS
        or source.terminal_private_state_digests != S1_KY_TERMINAL_PRIVATE_STATE_DIGESTS
        or source.terminal_adapter_output_digests != S1_KY_TERMINAL_ADAPTER_OUTPUT_DIGESTS
    ):
        raise DTS1S1KYB1PIKCaseOutputContractError("S1-KV sequence source or S1-KX output source differs")
    components = tuple(row[1] for row in S1_KY_COMPONENTS_BY_REFINEMENT)
    values = {
        "contract_id": S1_KY_CONTRACT_ID,
        "source_s1kv_digest": prior.contract_digest,
        "source_s1kx_digest": source.receipt_digest,
        "source_s1jx_case_record": next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_KY_CASE_ID),
        "case_schema": S1_KY_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_KY_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "sequence_count_per_refinement": 2,
        "checkpoint_count_per_refinement": 2,
        "component_count_per_refinement": 6,
        "primary_refinement": 4,
        "comparison_digest_count": 1,
        "distinct_provenance_digest_count": len(set(S1_KX_TARGET_OUTPUT_DIGESTS)),
        "checkpoint_parent_identity_valid": True,
        "sequence_terminal_bit_identity": True,
        "all_components_bit_identical": len(set(components)) == 1,
        "nonzero_component_count": sum(value != 0.0 for value in S1_KX_TARGET_COMPONENTS),
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "interference_judgment_present": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "b2_pik_case_selection_authorized_next_stage": True,
        "decision": S1_KY_DECISION,
    }
    return DTS1S1KYB1PIKCaseOutputContract(**values, contract_digest=_digest(values))
