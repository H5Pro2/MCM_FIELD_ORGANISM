"""Static S1-LT complete B3/P_IK C11 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_LS_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
    S1_LS_CHECKPOINT_FIELD_DIGESTS,
    S1_LS_CHECKPOINT_PRIVATE_STATE_DIGESTS,
    S1_LS_DECISION,
    S1_LS_TARGET_COMPARISON_DIGESTS,
    S1_LS_TARGET_COMPONENTS_BY_REFINEMENT,
    S1_LS_TARGET_OUTPUT_DIGESTS,
    S1_LS_TARGET_REPLICA_IDS,
    build_dts1_s1ls_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1lr_b3_pik_case_selection_contract import (
    S1_LR_CASE_ID,
    build_dts1_s1lr_b3_pik_case_selection_contract,
)


class DTS1S1LTB3PIKCaseOutputContractError(ValueError):
    """Raised when the static S1-LT C11 case output is weakened."""


S1_LT_CONTRACT_ID = "dynamic-substrate.b3-pik-case-output.s1lt.v1"
S1_LT_SOURCE_S1LR_DIGEST = (
    "17fe3103426ab340f1c7cceb8ad9d8a03a4fe8e98645ace99688df61b6ceeebc"
)
S1_LT_SOURCE_S1LS_DIGEST = (
    "9793383c0ef474336f4b9ce79e2513fea1d32c1a89260de018a3b29240e0ebcb"
)
S1_LT_CASE_ID = S1_LR_CASE_ID


def _subtract(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, ...]:
    if len(left) != 6 or len(right) != 6:
        raise DTS1S1LTB3PIKCaseOutputContractError(
            "C11 residual inputs must each contain six components"
        )
    return tuple(
        0.0 if left_value == right_value else left_value - right_value
        for left_value, right_value in zip(left, right, strict=True)
    )


_COMPONENTS = dict(S1_LS_TARGET_COMPONENTS_BY_REFINEMENT)
S1_LT_REFINEMENT_RESIDUALS = (
    ("r2_minus_r4", _subtract(_COMPONENTS[2], _COMPONENTS[4])),
    ("r4_minus_r8", _subtract(_COMPONENTS[4], _COMPONENTS[8])),
)
S1_LT_CASE_SCHEMA = (
    ("schema_id", "mcm.s1lt.complete-three-refinement-case.v1"),
    (
        "fields",
        (
            "schema_id",
            "case_id",
            "model_role",
            "long_model_role",
            "profile_block",
            "node_count",
            "component_count",
            "replica_ids",
            "replica_output_digests",
            "refinement_comparison_digests",
            "components_by_refinement",
            "primary_refinement",
            "primary_components",
            "refinement_residuals",
            "checkpoint_field_digests",
            "checkpoint_private_state_digests",
            "checkpoint_adapter_output_digests",
            "checkpoint_parent_identity_valid",
            "refinement_outputs_distinct",
            "status",
            "case_output_digest",
        ),
    ),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_LT_STATUS = "TECHNICALLY_COMPLETE_NO_PIK_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_LT_DECISION = (
    "C11_B3_PIK_THREE_REFINEMENT_CASE_OUTPUT_AND_RESIDUALS_BOUND_FROM_S1LS_RECEIPT_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1lt.complete-three-refinement-case.v1",
        "case_id": S1_LT_CASE_ID,
        "model_role": "B3",
        "long_model_role": "B3_F3_LOCAL_LEAKY",
        "profile_block": "P_IK_INTERFERENCE",
        "node_count": 3,
        "component_count": 6,
        "replica_ids": S1_LS_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_LS_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digests": S1_LS_TARGET_COMPARISON_DIGESTS,
        "components_by_refinement": S1_LS_TARGET_COMPONENTS_BY_REFINEMENT,
        "primary_refinement": 4,
        "primary_components": _COMPONENTS[4],
        "refinement_residuals": S1_LT_REFINEMENT_RESIDUALS,
        "checkpoint_field_digests": S1_LS_CHECKPOINT_FIELD_DIGESTS,
        "checkpoint_private_state_digests": S1_LS_CHECKPOINT_PRIVATE_STATE_DIGESTS,
        "checkpoint_adapter_output_digests": S1_LS_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
        "checkpoint_parent_identity_valid": True,
        "refinement_outputs_distinct": True,
        "status": S1_LT_STATUS,
    }


S1_LT_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1LTB3PIKCaseOutputContract:
    contract_id: str
    source_s1lr_digest: str
    source_s1ls_digest: str
    source_s1jx_case_record: tuple[object, ...]
    source_s1ls_decision: str
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
    residual_block_count: int
    residual_component_count: int
    checkpoint_parent_identity_valid: bool
    refinement_outputs_distinct: bool
    all_primary_components_zero: bool
    primary_components_nonzero: bool
    all_refinement_residuals_zero: bool
    residuals_shrink_r4_to_r8: bool
    case_record_composed: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    runtime_integration_present: bool
    c12_selection_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected_case = next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_LT_CASE_ID
        )
        residual_values = tuple(
            value for _, values in S1_LT_REFINEMENT_RESIDUALS for value in values
        )
        r2_r4_norm = sum(abs(value) for value in dict(S1_LT_REFINEMENT_RESIDUALS)["r2_minus_r4"])
        r4_r8_norm = sum(abs(value) for value in dict(S1_LT_REFINEMENT_RESIDUALS)["r4_minus_r8"])
        if (
            self.contract_id != S1_LT_CONTRACT_ID
            or self.source_s1lr_digest != S1_LT_SOURCE_S1LR_DIGEST
            or self.source_s1ls_digest != S1_LT_SOURCE_S1LS_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.source_s1ls_decision != S1_LS_DECISION
            or self.case_schema != S1_LT_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_LT_CASE_OUTPUT_DIGEST
            or (self.replica_count, self.sequence_count_per_refinement) != (3, 2)
            or (self.checkpoint_count_per_refinement, self.component_count_per_refinement) != (2, 6)
            or (self.primary_refinement, self.comparison_digest_count) != (4, 3)
            or self.distinct_provenance_digest_count != 3
            or (self.residual_block_count, self.residual_component_count) != (2, 12)
            or self.checkpoint_parent_identity_valid is not True
            or self.refinement_outputs_distinct is not True
            or self.all_primary_components_zero is not False
            or self.primary_components_nonzero is not True
            or self.all_refinement_residuals_zero is not False
            or self.residuals_shrink_r4_to_r8 is not (r4_r8_norm < r2_r4_norm)
            or self.case_record_composed is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.c12_selection_authorized_next_stage is not True
            or self.decision != S1_LT_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LTB3PIKCaseOutputContractError(
                "S1-LT weakened the complete C11 case output"
            )


def build_dts1_s1lt_b3_pik_case_output_contract(
) -> DTS1S1LTB3PIKCaseOutputContract:
    """Compose C11 and its residuals without executing a replica."""

    source_lr = build_dts1_s1lr_b3_pik_case_selection_contract()
    source_ls = build_dts1_s1ls_implementation_receipt()
    if (
        source_lr.contract_digest != S1_LT_SOURCE_S1LR_DIGEST
        or source_ls.receipt_digest != S1_LT_SOURCE_S1LS_DIGEST
        or source_ls.decision != S1_LS_DECISION
        or source_lr.target_case_record[0] != S1_LT_CASE_ID
        or source_lr.target_case_record[1] != "B3"
        or source_lr.target_case_record[2] != "B3_F3_LOCAL_LEAKY"
        or source_lr.target_case_record[3] != "P_IK_INTERFERENCE"
        or not source_lr.case_selected
        or source_lr.runner_extension_implemented is not False
        or source_lr.exact_implementation_execution_authorized_next_stage is not True
        or source_ls.case_output_composed is not False
        or source_ls.matrix_case_output_published is not False
        or source_ls.interference_or_baseline_judgment_present is not False
    ):
        raise DTS1S1LTB3PIKCaseOutputContractError(
            "S1-LT source contracts are not the expected static boundary"
        )
    residual_values = tuple(
        value for _, values in S1_LT_REFINEMENT_RESIDUALS for value in values
    )
    residuals = dict(S1_LT_REFINEMENT_RESIDUALS)
    values = {
        "contract_id": S1_LT_CONTRACT_ID,
        "source_s1lr_digest": source_lr.contract_digest,
        "source_s1ls_digest": source_ls.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_LT_CASE_ID
        ),
        "source_s1ls_decision": source_ls.decision,
        "case_schema": S1_LT_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_LT_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "sequence_count_per_refinement": 2,
        "checkpoint_count_per_refinement": 2,
        "component_count_per_refinement": 6,
        "primary_refinement": 4,
        "comparison_digest_count": len(set(S1_LS_TARGET_COMPARISON_DIGESTS)),
        "distinct_provenance_digest_count": len(set(S1_LS_TARGET_OUTPUT_DIGESTS)),
        "residual_block_count": 2,
        "residual_component_count": len(residual_values),
        "checkpoint_parent_identity_valid": True,
        "refinement_outputs_distinct": True,
        "all_primary_components_zero": all(value == 0.0 for value in _COMPONENTS[4]),
        "primary_components_nonzero": all(value != 0.0 for value in _COMPONENTS[4]),
        "all_refinement_residuals_zero": all(value == 0.0 for value in residual_values),
        "residuals_shrink_r4_to_r8": (
            sum(abs(value) for value in residuals["r4_minus_r8"])
            < sum(abs(value) for value in residuals["r2_minus_r4"])
        ),
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "c12_selection_authorized_next_stage": True,
        "decision": S1_LT_DECISION,
    }
    return DTS1S1LTB3PIKCaseOutputContract(
        **values, contract_digest=_digest(values)
    )
