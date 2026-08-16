"""Static S1-KP complete B2/P_IE C05 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_KK_TARGET_COMPARISON_DIGEST,
    S1_KK_TARGET_OUTPUT_DIGESTS,
    S1_KK_TARGET_REPLICA_IDS,
    build_dts1_s1kk_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1ko_corrected_b1_pie_case_output_contract import (
    build_dts1_s1ko_corrected_b1_pie_case_output_contract,
)


class DTS1S1KPB2PIECaseOutputContractError(ValueError):
    """Raised when the finite S1-KP C05 case output is weakened."""


S1_KP_CONTRACT_ID = "dynamic-substrate.b2-pie-case-output.s1kp.v1"
S1_KP_SOURCE_S1KO_DIGEST = (
    "f97b306256c42ab9872f7db71ad5605f18a97a274052ba96430c7b0e2244cfa0"
)
S1_KP_SOURCE_S1KK_DIGEST = (
    "503a13050c22e4e33e553a4661411868e29b8b2c3e987eee2c3d962daf977e61"
)
S1_KP_CASE_ID = "C05"
S1_KP_COMPONENTS_BY_REFINEMENT = (
    (2, (0.0,) * 8),
    (4, (0.0,) * 8),
    (8, (0.0,) * 8),
)
S1_KP_CASE_SCHEMA = (
    ("schema_id", "mcm.s1kp.complete-three-refinement-case.v1"),
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
S1_KP_STATUS = "TECHNICALLY_COMPLETE_NO_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_KP_DECISION = (
    "C05_B2_PIE_THREE_REFINEMENT_CASE_OUTPUT_BOUND_FROM_S1KK_RECEIPT_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1kp.complete-three-refinement-case.v1",
        "case_id": S1_KP_CASE_ID,
        "model_role": "B2",
        "long_model_role": "B2_S2_LINEAR_INTEGRATOR",
        "profile_block": "P_IE_CAUSAL_TWO_SUBSTEP",
        "node_count": 2,
        "component_count": 8,
        "replica_ids": S1_KK_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_KK_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digest": S1_KK_TARGET_COMPARISON_DIGEST,
        "components_by_refinement": S1_KP_COMPONENTS_BY_REFINEMENT,
        "primary_refinement": 4,
        "primary_components": (0.0,) * 8,
        "checkpoint_parent_identity_valid": True,
        "control_bit_identity": True,
        "status": S1_KP_STATUS,
    }


S1_KP_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1KPB2PIECaseOutputContract:
    contract_id: str
    source_s1ko_digest: str
    source_s1kk_digest: str
    source_s1jx_case_record: tuple[object, ...]
    case_schema: tuple[tuple[str, object], ...]
    case_payload: tuple[tuple[str, object], ...]
    case_output_digest: str
    replica_count: int
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
    next_case_selection_contract_authorized: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected_case = next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_KP_CASE_ID)
        if (
            self.contract_id != S1_KP_CONTRACT_ID
            or self.source_s1ko_digest != S1_KP_SOURCE_S1KO_DIGEST
            or self.source_s1kk_digest != S1_KP_SOURCE_S1KK_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.case_schema != S1_KP_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_KP_CASE_OUTPUT_DIGEST
            or self.replica_count != 3
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
            or self.next_case_selection_contract_authorized is not True
            or self.decision != S1_KP_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KPB2PIECaseOutputContractError(
                "S1-KP weakened the complete C05 case output"
            )


def build_dts1_s1kp_b2_pie_case_output_contract(
) -> DTS1S1KPB2PIECaseOutputContract:
    """Compose C05 from bound receipts without executing a replica."""

    prior = build_dts1_s1ko_corrected_b1_pie_case_output_contract()
    source = build_dts1_s1kk_implementation_receipt()
    if (
        prior.contract_digest != S1_KP_SOURCE_S1KO_DIGEST
        or source.receipt_digest != S1_KP_SOURCE_S1KK_DIGEST
        or source.target_output_digests != S1_KK_TARGET_OUTPUT_DIGESTS
        or source.target_comparison_digests
        != (S1_KK_TARGET_COMPARISON_DIGEST,) * 3
    ):
        raise DTS1S1KPB2PIECaseOutputContractError(
            "S1-KO sequence source or S1-KK output source differs"
        )
    components = tuple(row[1] for row in S1_KP_COMPONENTS_BY_REFINEMENT)
    values = {
        "contract_id": S1_KP_CONTRACT_ID,
        "source_s1ko_digest": prior.contract_digest,
        "source_s1kk_digest": source.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_KP_CASE_ID
        ),
        "case_schema": S1_KP_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_KP_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "component_count_per_refinement": 8,
        "primary_refinement": 4,
        "comparison_digest_count": 1,
        "distinct_provenance_digest_count": len(set(S1_KK_TARGET_OUTPUT_DIGESTS)),
        "checkpoint_parent_identity_valid": True,
        "all_components_bit_identical": len(set(components)) == 1,
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "next_case_selection_contract_authorized": True,
        "decision": S1_KP_DECISION,
    }
    return DTS1S1KPB2PIECaseOutputContract(
        **values, contract_digest=_digest(values)
    )
