"""Static S1-KO corrected-provenance C01 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_KF_EXEMPLAR_COMPARISON_DIGEST,
    S1_KF_EXEMPLAR_OUTPUT_DIGEST,
    S1_KH_TARGET_OUTPUT_DIGESTS,
    S1_KN_CORRECTED_OUTPUT_DIGESTS,
    build_dts1_s1kn_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1ki_b1_pie_case_output_contract import (
    S1_KI_CASE_OUTPUT_DIGEST,
)


class DTS1S1KOCorrectedB1PIECaseOutputContractError(ValueError):
    """Raised when the corrected finite C01 case output is weakened."""


S1_KO_CONTRACT_ID = "dynamic-substrate.corrected-b1-pie-case-output.s1ko.v1"
S1_KO_SOURCE_S1KN_DIGEST = (
    "d751b4d059cd17200d884e69ff2a4c7d261127c12962b03e33b960ae7d75c939"
)
S1_KO_CASE_ID = "C01"
S1_KO_HISTORICAL_CASE_OUTPUT_DIGEST = S1_KI_CASE_OUTPUT_DIGEST
S1_KO_HISTORICAL_AFFECTED_OUTPUT_DIGESTS = S1_KH_TARGET_OUTPUT_DIGESTS
S1_KO_REPLICA_IDS = (
    "B1:P_IE_CAUSAL_TWO_SUBSTEP:r2",
    "B1:P_IE_CAUSAL_TWO_SUBSTEP:r4",
    "B1:P_IE_CAUSAL_TWO_SUBSTEP:r8",
)
S1_KO_CORRECTED_REPLICA_OUTPUT_DIGESTS = (
    S1_KF_EXEMPLAR_OUTPUT_DIGEST,
    *S1_KN_CORRECTED_OUTPUT_DIGESTS,
)
S1_KO_COMPONENTS_BY_REFINEMENT = (
    (2, (0.0,) * 8),
    (4, (0.0,) * 8),
    (8, (0.0,) * 8),
)
S1_KO_CASE_SCHEMA = (
    ("schema_id", "mcm.s1ko.corrected-provenance-three-refinement-case.v1"),
    ("fields", (
        "schema_id",
        "case_id",
        "model_role",
        "long_model_role",
        "profile_block",
        "node_count",
        "component_count",
        "replica_ids",
        "corrected_replica_output_digests",
        "refinement_comparison_digest",
        "components_by_refinement",
        "primary_refinement",
        "primary_components",
        "checkpoint_parent_identity_valid",
        "historical_case_output_digest",
        "status",
        "case_output_digest",
    )),
    ("publication", "one-complete-corrected-case-record-or-one-error-with-no-partial-value"),
)
S1_KO_STATUS = "TECHNICALLY_COMPLETE_CORRECTED_PROVENANCE_NO_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_KO_DECISION = (
    "C01_CORRECTED_PROVENANCE_CASE_OUTPUT_BOUND_FROM_R2_AND_S1KN_RECEIPT_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1ko.corrected-provenance-three-refinement-case.v1",
        "case_id": S1_KO_CASE_ID,
        "model_role": "B1",
        "long_model_role": "B1_FIXED_PRERELEASE_ADAPTER",
        "profile_block": "P_IE_CAUSAL_TWO_SUBSTEP",
        "node_count": 2,
        "component_count": 8,
        "replica_ids": S1_KO_REPLICA_IDS,
        "corrected_replica_output_digests": S1_KO_CORRECTED_REPLICA_OUTPUT_DIGESTS,
        "refinement_comparison_digest": S1_KF_EXEMPLAR_COMPARISON_DIGEST,
        "components_by_refinement": S1_KO_COMPONENTS_BY_REFINEMENT,
        "primary_refinement": 4,
        "primary_components": (0.0,) * 8,
        "checkpoint_parent_identity_valid": True,
        "historical_case_output_digest": S1_KO_HISTORICAL_CASE_OUTPUT_DIGEST,
        "status": S1_KO_STATUS,
    }


S1_KO_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1KOCorrectedB1PIECaseOutputContract:
    contract_id: str
    source_s1kn_digest: str
    source_s1jx_case_record: tuple[object, ...]
    case_schema: tuple[tuple[str, object], ...]
    case_payload: tuple[tuple[str, object], ...]
    case_output_digest: str
    historical_case_output_digest: str
    historical_affected_output_digests: tuple[str, str]
    corrected_replica_output_digests: tuple[str, str, str]
    replica_count: int
    component_count_per_refinement: int
    primary_refinement: int
    comparison_digest_count: int
    distinct_corrected_provenance_digest_count: int
    checkpoint_parent_identity_valid: bool
    all_components_bit_identical: bool
    corrected_case_record_composed: bool
    historical_case_record_rewritten: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    runtime_integration_present: bool
    c05_case_composition_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected_case = next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_KO_CASE_ID)
        if (
            self.contract_id != S1_KO_CONTRACT_ID
            or self.source_s1kn_digest != S1_KO_SOURCE_S1KN_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.case_schema != S1_KO_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_KO_CASE_OUTPUT_DIGEST
            or self.historical_case_output_digest != S1_KO_HISTORICAL_CASE_OUTPUT_DIGEST
            or self.historical_affected_output_digests != S1_KO_HISTORICAL_AFFECTED_OUTPUT_DIGESTS
            or self.corrected_replica_output_digests != S1_KO_CORRECTED_REPLICA_OUTPUT_DIGESTS
            or self.replica_count != 3
            or self.component_count_per_refinement != 8
            or self.primary_refinement != 4
            or self.comparison_digest_count != 1
            or self.distinct_corrected_provenance_digest_count != 3
            or self.checkpoint_parent_identity_valid is not True
            or self.all_components_bit_identical is not True
            or self.corrected_case_record_composed is not True
            or self.historical_case_record_rewritten is not False
            or self.new_replicas_executed != 0
            or self.new_interval_calls_executed != 0
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.c05_case_composition_authorized_next_stage is not True
            or self.decision != S1_KO_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KOCorrectedB1PIECaseOutputContractError(
                "S1-KO weakened the corrected C01 case output"
            )


def build_dts1_s1ko_corrected_b1_pie_case_output_contract(
) -> DTS1S1KOCorrectedB1PIECaseOutputContract:
    """Compose corrected C01 from bound receipts without running a replica."""

    source = build_dts1_s1kn_implementation_receipt()
    if (
        source.receipt_digest != S1_KO_SOURCE_S1KN_DIGEST
        or source.corrected_output_digests != S1_KN_CORRECTED_OUTPUT_DIGESTS
        or source.historical_records_rewritten is not False
    ):
        raise DTS1S1KOCorrectedB1PIECaseOutputContractError(
            "S1-KN correction source differs"
        )
    components = tuple(row[1] for row in S1_KO_COMPONENTS_BY_REFINEMENT)
    values = {
        "contract_id": S1_KO_CONTRACT_ID,
        "source_s1kn_digest": source.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_KO_CASE_ID
        ),
        "case_schema": S1_KO_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_KO_CASE_OUTPUT_DIGEST,
        "historical_case_output_digest": S1_KO_HISTORICAL_CASE_OUTPUT_DIGEST,
        "historical_affected_output_digests": S1_KO_HISTORICAL_AFFECTED_OUTPUT_DIGESTS,
        "corrected_replica_output_digests": S1_KO_CORRECTED_REPLICA_OUTPUT_DIGESTS,
        "replica_count": 3,
        "component_count_per_refinement": 8,
        "primary_refinement": 4,
        "comparison_digest_count": 1,
        "distinct_corrected_provenance_digest_count": len(
            set(S1_KO_CORRECTED_REPLICA_OUTPUT_DIGESTS)
        ),
        "checkpoint_parent_identity_valid": True,
        "all_components_bit_identical": len(set(components)) == 1,
        "corrected_case_record_composed": True,
        "historical_case_record_rewritten": False,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "c05_case_composition_authorized_next_stage": True,
        "decision": S1_KO_DECISION,
    }
    return DTS1S1KOCorrectedB1PIECaseOutputContract(
        **values, contract_digest=_digest(values)
    )
