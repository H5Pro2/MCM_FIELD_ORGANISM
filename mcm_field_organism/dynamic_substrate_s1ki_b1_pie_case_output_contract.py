"""Static S1-KI case output contract for the accepted B1/P_IE controls."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_KF_EXEMPLAR_COMPARISON_DIGEST,
    S1_KF_EXEMPLAR_OUTPUT_DIGEST,
    S1_KH_TARGET_OUTPUT_DIGESTS,
    build_dts1_s1kh_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)


class DTS1S1KIB1PIECaseOutputContractError(ValueError):
    """Raised when the finite S1-KI case output contract is weakened."""


S1_KI_CONTRACT_ID = "dynamic-substrate.b1-pie-case-output.s1ki.v1"
S1_KI_SOURCE_S1KH_DIGEST = (
    "d9a1216ad04463a633c6d773c37a368eebab0945165fdf3a4dfb438dd8f9d604"
)
S1_KI_CASE_ID = "C01"
S1_KI_CASE_SCHEMA = (
    ("schema_id", "mcm.s1ki.complete-three-refinement-case.v1"),
    ("fields", (
        "schema_id",
        "case_id",
        "model_role",
        "long_model_role",
        "profile_block",
        "node_count",
        "component_count",
        "replica_ids",
        "replica_output_digests",
        "refinement_comparison_digest",
        "components_by_refinement",
        "primary_refinement",
        "primary_components",
        "control_bit_identity",
        "status",
        "case_output_digest",
    )),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_KI_REPLICA_IDS = (
    "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2",
    "B1:P_IE_CAUSAL_TWO_SUBSTEP:r4",
    "B1:P_IE_CAUSAL_TWO_SUBSTEP:r8",
)
S1_KI_REPLICA_OUTPUT_DIGESTS = (
    S1_KF_EXEMPLAR_OUTPUT_DIGEST,
    *S1_KH_TARGET_OUTPUT_DIGESTS,
)
S1_KI_COMPONENTS_BY_REFINEMENT = (
    (2, (0.0,) * 8),
    (4, (0.0,) * 8),
    (8, (0.0,) * 8),
)
S1_KI_STATUS = "TECHNICALLY_COMPLETE_NO_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_KI_DECISION = (
    "B1_P_IE_THREE_REFINEMENT_CASE_OUTPUT_BOUND_FROM_EXISTING_RECEIPTS_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1ki.complete-three-refinement-case.v1",
        "case_id": S1_KI_CASE_ID,
        "model_role": "B1",
        "long_model_role": "B1_FIXED_PRERELEASE_ADAPTER",
        "profile_block": "P_IE_CAUSAL_TWO_SUBSTEP",
        "node_count": 2,
        "component_count": 8,
        "replica_ids": S1_KI_REPLICA_IDS,
        "replica_output_digests": S1_KI_REPLICA_OUTPUT_DIGESTS,
        "refinement_comparison_digest": S1_KF_EXEMPLAR_COMPARISON_DIGEST,
        "components_by_refinement": S1_KI_COMPONENTS_BY_REFINEMENT,
        "primary_refinement": 4,
        "primary_components": (0.0,) * 8,
        "control_bit_identity": True,
        "status": S1_KI_STATUS,
    }


S1_KI_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1KIB1PIECaseOutputContract:
    contract_id: str
    source_s1kh_digest: str
    source_s1jx_case_record: tuple[object, ...]
    case_schema: tuple[tuple[str, object], ...]
    case_payload: tuple[tuple[str, object], ...]
    case_output_digest: str
    replica_count: int
    component_count_per_refinement: int
    primary_refinement: int
    comparison_digest_count: int
    distinct_provenance_digest_count: int
    all_components_bit_identical: bool
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
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_KI_CONTRACT_ID
            or self.source_s1kh_digest != S1_KI_SOURCE_S1KH_DIGEST
            or self.source_s1jx_case_record
            != next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_KI_CASE_ID)
            or self.case_schema != S1_KI_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_KI_CASE_OUTPUT_DIGEST
            or self.replica_count != 3
            or self.component_count_per_refinement != 8
            or self.primary_refinement != 4
            or self.comparison_digest_count != 1
            or self.distinct_provenance_digest_count != 3
            or self.all_components_bit_identical is not True
            or self.case_record_composed is not True
            or self.new_replicas_executed != 0
            or self.new_interval_calls_executed != 0
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.next_case_selection_contract_authorized is not True
            or self.decision != S1_KI_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KIB1PIECaseOutputContractError(
                "S1-KI weakened the complete B1/P_IE case output"
            )


def build_dts1_s1ki_b1_pie_case_output_contract(
) -> DTS1S1KIB1PIECaseOutputContract:
    """Compose C01 only from bound receipts without executing a replica."""

    source = build_dts1_s1kh_implementation_receipt()
    if source.receipt_digest != S1_KI_SOURCE_S1KH_DIGEST:
        raise DTS1S1KIB1PIECaseOutputContractError("S1-KH source differs")
    components = tuple(row[1] for row in S1_KI_COMPONENTS_BY_REFINEMENT)
    values = {
        "contract_id": S1_KI_CONTRACT_ID,
        "source_s1kh_digest": source.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_KI_CASE_ID
        ),
        "case_schema": S1_KI_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_KI_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "component_count_per_refinement": 8,
        "primary_refinement": 4,
        "comparison_digest_count": 1,
        "distinct_provenance_digest_count": len(set(S1_KI_REPLICA_OUTPUT_DIGESTS)),
        "all_components_bit_identical": len(set(components)) == 1,
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "next_case_selection_contract_authorized": True,
        "decision": S1_KI_DECISION,
    }
    return DTS1S1KIB1PIECaseOutputContract(
        **values, contract_digest=_digest(values)
    )
