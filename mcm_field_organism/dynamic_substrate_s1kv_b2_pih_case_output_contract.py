"""Static S1-KV complete B2/P_IH C06 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_KU_CHECKPOINT_PRIVATE_STATE_DIGESTS,
    S1_KU_TARGET_COMPARISON_DIGEST,
    S1_KU_TARGET_COMPONENTS,
    S1_KU_TARGET_OUTPUT_DIGESTS,
    S1_KU_TARGET_REPLICA_IDS,
    build_dts1_s1ku_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import S1_JX_CASE_RECORDS
from .dynamic_substrate_s1ks_b1_pih_case_output_contract import build_dts1_s1ks_b1_pih_case_output_contract


class DTS1S1KVB2PIHCaseOutputContractError(ValueError):
    """Raised when the finite S1-KV C06 case output is weakened."""


S1_KV_CONTRACT_ID = "dynamic-substrate.b2-pih-case-output.s1kv.v1"
S1_KV_SOURCE_S1KS_DIGEST = "d2ed48ba9be2fcbac31d069ad9fc741cd517f521b5d8037441ead40fd19e53aa"
S1_KV_SOURCE_S1KU_DIGEST = "c8568cdad103f2fa86295119e24578e32f9169e354b1e0e981d73aadeb36a9f7"
S1_KV_CASE_ID = "C06"
S1_KV_COMPONENTS_BY_REFINEMENT = tuple((refinement, S1_KU_TARGET_COMPONENTS) for refinement in (2, 4, 8))
S1_KV_CASE_SCHEMA = (
    ("schema_id", "mcm.s1kv.complete-three-refinement-case.v1"),
    ("fields", (
        "schema_id", "case_id", "model_role", "long_model_role", "profile_block",
        "node_count", "component_count", "replica_ids", "replica_output_digests",
        "refinement_comparison_digest", "components_by_refinement",
        "checkpoint_private_state_digests", "primary_refinement", "primary_components",
        "checkpoint_parent_identity_valid", "refinement_bit_identity", "status",
        "case_output_digest",
    )),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_KV_STATUS = "TECHNICALLY_COMPLETE_NO_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_KV_DECISION = "C06_B2_PIH_THREE_REFINEMENT_CASE_OUTPUT_BOUND_FROM_S1KU_RECEIPT_NO_NEW_EXECUTION"


def _digest(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1kv.complete-three-refinement-case.v1",
        "case_id": S1_KV_CASE_ID,
        "model_role": "B2",
        "long_model_role": "B2_S2_LINEAR_INTEGRATOR",
        "profile_block": "P_IH_ATTENUATION",
        "node_count": 2,
        "component_count": 8,
        "replica_ids": S1_KU_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_KU_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digest": S1_KU_TARGET_COMPARISON_DIGEST,
        "components_by_refinement": S1_KV_COMPONENTS_BY_REFINEMENT,
        "checkpoint_private_state_digests": S1_KU_CHECKPOINT_PRIVATE_STATE_DIGESTS,
        "primary_refinement": 4,
        "primary_components": S1_KU_TARGET_COMPONENTS,
        "checkpoint_parent_identity_valid": True,
        "refinement_bit_identity": True,
        "status": S1_KV_STATUS,
    }


S1_KV_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1KVB2PIHCaseOutputContract:
    contract_id: str
    source_s1ks_digest: str
    source_s1ku_digest: str
    source_s1jx_case_record: tuple[object, ...]
    case_schema: tuple[tuple[str, object], ...]
    case_payload: tuple[tuple[str, object], ...]
    case_output_digest: str
    replica_count: int
    checkpoint_count_per_refinement: int
    component_count_per_refinement: int
    primary_refinement: int
    comparison_digest_count: int
    distinct_provenance_digest_count: int
    distinct_private_state_digest_count: int
    checkpoint_parent_identity_valid: bool
    all_components_bit_identical: bool
    nonzero_component_count: int
    private_state_progression_bit_identical: bool
    case_record_composed: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    runtime_integration_present: bool
    next_case_selection_contract_authorized: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {field.name: getattr(self, field.name) for field in fields(self) if field.name != "contract_digest"}
        expected_case = next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_KV_CASE_ID)
        if (
            self.contract_id != S1_KV_CONTRACT_ID
            or self.source_s1ks_digest != S1_KV_SOURCE_S1KS_DIGEST
            or self.source_s1ku_digest != S1_KV_SOURCE_S1KU_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.case_schema != S1_KV_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_KV_CASE_OUTPUT_DIGEST
            or (self.replica_count, self.checkpoint_count_per_refinement, self.component_count_per_refinement) != (3, 3, 8)
            or (self.primary_refinement, self.comparison_digest_count, self.distinct_provenance_digest_count) != (4, 1, 3)
            or self.distinct_private_state_digest_count != 3
            or self.checkpoint_parent_identity_valid is not True
            or self.all_components_bit_identical is not True
            or self.nonzero_component_count != 8
            or self.private_state_progression_bit_identical is not True
            or self.case_record_composed is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.next_case_selection_contract_authorized is not True
            or self.decision != S1_KV_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KVB2PIHCaseOutputContractError("S1-KV weakened the complete C06 case output")


def build_dts1_s1kv_b2_pih_case_output_contract() -> DTS1S1KVB2PIHCaseOutputContract:
    """Compose C06 from bound receipts without executing a replica."""

    prior = build_dts1_s1ks_b1_pih_case_output_contract()
    source = build_dts1_s1ku_implementation_receipt()
    if (
        prior.contract_digest != S1_KV_SOURCE_S1KS_DIGEST
        or source.receipt_digest != S1_KV_SOURCE_S1KU_DIGEST
        or source.target_output_digests != S1_KU_TARGET_OUTPUT_DIGESTS
        or source.target_components != S1_KU_TARGET_COMPONENTS
        or source.checkpoint_private_state_digests != S1_KU_CHECKPOINT_PRIVATE_STATE_DIGESTS
    ):
        raise DTS1S1KVB2PIHCaseOutputContractError("S1-KS sequence source or S1-KU output source differs")
    components = tuple(row[1] for row in S1_KV_COMPONENTS_BY_REFINEMENT)
    values = {
        "contract_id": S1_KV_CONTRACT_ID,
        "source_s1ks_digest": prior.contract_digest,
        "source_s1ku_digest": source.receipt_digest,
        "source_s1jx_case_record": next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_KV_CASE_ID),
        "case_schema": S1_KV_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_KV_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "checkpoint_count_per_refinement": 3,
        "component_count_per_refinement": 8,
        "primary_refinement": 4,
        "comparison_digest_count": 1,
        "distinct_provenance_digest_count": len(set(S1_KU_TARGET_OUTPUT_DIGESTS)),
        "distinct_private_state_digest_count": len(set(S1_KU_CHECKPOINT_PRIVATE_STATE_DIGESTS)),
        "checkpoint_parent_identity_valid": True,
        "all_components_bit_identical": len(set(components)) == 1,
        "nonzero_component_count": sum(value != 0.0 for value in S1_KU_TARGET_COMPONENTS),
        "private_state_progression_bit_identical": True,
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "next_case_selection_contract_authorized": True,
        "decision": S1_KV_DECISION,
    }
    return DTS1S1KVB2PIHCaseOutputContract(**values, contract_digest=_digest(values))
