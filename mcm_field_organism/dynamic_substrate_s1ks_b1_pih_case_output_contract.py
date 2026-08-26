"""Static S1-KS complete B1/P_IH C02 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_KR_TARGET_COMPARISON_DIGEST,
    S1_KR_TARGET_OUTPUT_DIGESTS,
    S1_KR_TARGET_REPLICA_IDS,
    build_dts1_s1kr_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1kp_b2_pie_case_output_contract import (
    build_dts1_s1kp_b2_pie_case_output_contract,
)


class DTS1S1KSB1PIHCaseOutputContractError(ValueError):
    """Raised when the finite S1-KS C02 case output is weakened."""


S1_KS_CONTRACT_ID = "dynamic-substrate.b1-pih-case-output.s1ks.v1"
S1_KS_SOURCE_S1KP_DIGEST = (
    "133680fef4e057f5500d4836ee6f47814d37d9133df78fd250bf48df0f84a473"
)
S1_KS_SOURCE_S1KR_DIGEST = (
    "692d1c959bdc119cceafd9430f86c5727cdbb580a8569a2c5c70765ad1f6782c"
)
S1_KS_CASE_ID = "C02"
S1_KS_COMPONENTS_BY_REFINEMENT = (
    (2, (0.0,) * 8),
    (4, (0.0,) * 8),
    (8, (0.0,) * 8),
)
S1_KS_CASE_SCHEMA = (
    ("schema_id", "mcm.s1ks.complete-three-refinement-case.v1"),
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
        "checkpoint_parent_identity_valid",
        "control_bit_identity",
        "status",
        "case_output_digest",
    )),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_KS_STATUS = "TECHNICALLY_COMPLETE_NO_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_KS_DECISION = (
    "C02_B1_PIH_THREE_REFINEMENT_CASE_OUTPUT_BOUND_FROM_S1KR_RECEIPT_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1ks.complete-three-refinement-case.v1",
        "case_id": S1_KS_CASE_ID,
        "model_role": "B1",
        "long_model_role": "B1_FIXED_PRERELEASE_ADAPTER",
        "profile_block": "P_IH_ATTENUATION",
        "node_count": 2,
        "component_count": 8,
        "replica_ids": S1_KR_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_KR_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digest": S1_KR_TARGET_COMPARISON_DIGEST,
        "components_by_refinement": S1_KS_COMPONENTS_BY_REFINEMENT,
        "primary_refinement": 4,
        "primary_components": (0.0,) * 8,
        "checkpoint_parent_identity_valid": True,
        "control_bit_identity": True,
        "status": S1_KS_STATUS,
    }


S1_KS_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1KSB1PIHCaseOutputContract:
    contract_id: str
    source_s1kp_digest: str
    source_s1kr_digest: str
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
    checkpoint_parent_identity_valid: bool
    all_components_bit_identical: bool
    case_record_composed: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    runtime_integration_present: bool
    b2_pih_case_selection_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected_case = next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_KS_CASE_ID)
        if (
            self.contract_id != S1_KS_CONTRACT_ID
            or self.source_s1kp_digest != S1_KS_SOURCE_S1KP_DIGEST
            or self.source_s1kr_digest != S1_KS_SOURCE_S1KR_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.case_schema != S1_KS_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_KS_CASE_OUTPUT_DIGEST
            or self.replica_count != 3
            or self.checkpoint_count_per_refinement != 3
            or self.component_count_per_refinement != 8
            or self.primary_refinement != 4
            or self.comparison_digest_count != 1
            or self.distinct_provenance_digest_count != 3
            or self.checkpoint_parent_identity_valid is not True
            or self.all_components_bit_identical is not True
            or self.case_record_composed is not True
            or self.new_replicas_executed != 0
            or self.new_interval_calls_executed != 0
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.b2_pih_case_selection_authorized_next_stage is not True
            or self.decision != S1_KS_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KSB1PIHCaseOutputContractError(
                "S1-KS weakened the complete C02 case output"
            )


def build_dts1_s1ks_b1_pih_case_output_contract(
) -> DTS1S1KSB1PIHCaseOutputContract:
    """Compose C02 from bound receipts without executing a replica."""

    prior = build_dts1_s1kp_b2_pie_case_output_contract()
    source = build_dts1_s1kr_implementation_receipt()
    if (
        prior.contract_digest != S1_KS_SOURCE_S1KP_DIGEST
        or source.receipt_digest != S1_KS_SOURCE_S1KR_DIGEST
        or source.target_output_digests != S1_KR_TARGET_OUTPUT_DIGESTS
        or source.target_comparison_digests
        != (S1_KR_TARGET_COMPARISON_DIGEST,) * 3
    ):
        raise DTS1S1KSB1PIHCaseOutputContractError(
            "S1-KP sequence source or S1-KR output source differs"
        )
    components = tuple(row[1] for row in S1_KS_COMPONENTS_BY_REFINEMENT)
    values = {
        "contract_id": S1_KS_CONTRACT_ID,
        "source_s1kp_digest": prior.contract_digest,
        "source_s1kr_digest": source.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_KS_CASE_ID
        ),
        "case_schema": S1_KS_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_KS_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "checkpoint_count_per_refinement": 3,
        "component_count_per_refinement": 8,
        "primary_refinement": 4,
        "comparison_digest_count": 1,
        "distinct_provenance_digest_count": len(set(S1_KR_TARGET_OUTPUT_DIGESTS)),
        "checkpoint_parent_identity_valid": True,
        "all_components_bit_identical": len(set(components)) == 1,
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "b2_pih_case_selection_authorized_next_stage": True,
        "decision": S1_KS_DECISION,
    }
    return DTS1S1KSB1PIHCaseOutputContract(
        **values, contract_digest=_digest(values)
    )
