"""Static S1-MF complete B4/P_IH C14 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_ME_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
    S1_ME_CHECKPOINT_FIELD_DIGESTS,
    S1_ME_CHECKPOINT_PRIVATE_STATE_DIGESTS,
    S1_ME_DECISION,
    S1_ME_TARGET_COMPARISON_DIGESTS,
    S1_ME_TARGET_COMPONENTS_BY_REFINEMENT,
    S1_ME_TARGET_OUTPUT_DIGESTS,
    S1_ME_TARGET_REPLICA_IDS,
    build_dts1_s1me_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1md_b4_pih_case_selection_contract import (
    S1_MD_CASE_ID,
    build_dts1_s1md_b4_pih_case_selection_contract,
)


class DTS1S1MFB4PIHCaseOutputContractError(ValueError):
    """Raised when the static S1-MF C14 case output is weakened."""


S1_MF_CONTRACT_ID = "dynamic-substrate.b4-pih-case-output.s1mf.v1"
S1_MF_SOURCE_S1MD_DIGEST = (
    "026e7ac0e7de28345531585a85ba2062691c649b964baa854504283c2a6b818b"
)
S1_MF_SOURCE_S1ME_DIGEST = (
    "87f27b62d3cd75f98a7fb9b01f23dd9cd8a30c0c9fa09dee105f2099466b29cd"
)
S1_MF_CASE_ID = S1_MD_CASE_ID


def _subtract(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, ...]:
    if len(left) != 8 or len(right) != 8:
        raise DTS1S1MFB4PIHCaseOutputContractError(
            "C14 residual inputs must each contain eight components"
        )
    return tuple(left_value - right_value for left_value, right_value in zip(left, right, strict=True))


_COMPONENTS = dict(S1_ME_TARGET_COMPONENTS_BY_REFINEMENT)
S1_MF_REFINEMENT_RESIDUALS = (
    ("r2_minus_r4", _subtract(_COMPONENTS[2], _COMPONENTS[4])),
    ("r4_minus_r8", _subtract(_COMPONENTS[4], _COMPONENTS[8])),
)
S1_MF_CASE_SCHEMA = (
    ("schema_id", "mcm.s1mf.complete-three-refinement-case.v1"),
    ("fields", (
        "schema_id", "case_id", "model_role", "long_model_role",
        "profile_block", "node_count", "component_count", "replica_ids",
        "replica_output_digests", "refinement_comparison_digests",
        "components_by_refinement", "primary_refinement", "primary_components",
        "refinement_residuals", "checkpoint_field_digests",
        "checkpoint_private_state_digests", "checkpoint_adapter_output_digests",
        "checkpoint_parent_identity_valid", "refinement_outputs_distinct",
        "status", "case_output_digest",
    )),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_MF_STATUS = "TECHNICALLY_COMPLETE_NO_PIH_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_MF_DECISION = (
    "C14_B4_PIH_THREE_REFINEMENT_CASE_OUTPUT_AND_RESIDUALS_BOUND_FROM_S1ME_RECEIPT_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1mf.complete-three-refinement-case.v1",
        "case_id": S1_MF_CASE_ID,
        "model_role": "B4",
        "long_model_role": "B4_F3_LINEAR_COUPLED",
        "profile_block": "P_IH_ATTENUATION",
        "node_count": 2,
        "component_count": 8,
        "replica_ids": S1_ME_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_ME_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digests": S1_ME_TARGET_COMPARISON_DIGESTS,
        "components_by_refinement": S1_ME_TARGET_COMPONENTS_BY_REFINEMENT,
        "primary_refinement": 4,
        "primary_components": _COMPONENTS[4],
        "refinement_residuals": S1_MF_REFINEMENT_RESIDUALS,
        "checkpoint_field_digests": S1_ME_CHECKPOINT_FIELD_DIGESTS,
        "checkpoint_private_state_digests": S1_ME_CHECKPOINT_PRIVATE_STATE_DIGESTS,
        "checkpoint_adapter_output_digests": S1_ME_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS,
        "checkpoint_parent_identity_valid": True,
        "refinement_outputs_distinct": True,
        "status": S1_MF_STATUS,
    }


S1_MF_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1MFB4PIHCaseOutputContract:
    contract_id: str
    source_s1md_digest: str
    source_s1me_receipt_digest: str
    source_s1jx_case_record: tuple[object, ...]
    source_s1me_decision: str
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
    refinement_residuals_nonzero_present: bool
    case_record_composed: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    memory_capability_claim_present: bool
    ai_system_claim_present: bool
    runtime_integration_present: bool
    matrix_gate_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected_case = next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_MF_CASE_ID
        )
        residual_values = tuple(
            value for _, values in S1_MF_REFINEMENT_RESIDUALS for value in values
        )
        if (
            self.contract_id != S1_MF_CONTRACT_ID
            or self.source_s1md_digest != S1_MF_SOURCE_S1MD_DIGEST
            or self.source_s1me_receipt_digest != S1_MF_SOURCE_S1ME_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.source_s1me_decision != S1_ME_DECISION
            or self.case_schema != S1_MF_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_MF_CASE_OUTPUT_DIGEST
            or (self.replica_count, self.sequence_count_per_refinement, self.checkpoint_count_per_refinement, self.component_count_per_refinement) != (3, 1, 3, 8)
            or (self.primary_refinement, self.comparison_digest_count, self.distinct_provenance_digest_count) != (4, 3, 3)
            or (self.residual_block_count, self.residual_component_count) != (2, 16)
            or self.checkpoint_parent_identity_valid is not True
            or self.refinement_outputs_distinct is not True
            or self.all_primary_components_zero is not False
            or self.primary_components_nonzero is not True
            or self.all_refinement_residuals_zero is not False
            or self.refinement_residuals_nonzero_present is not (any(value != 0.0 for value in residual_values))
            or self.case_record_composed is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.memory_capability_claim_present is not False
            or self.ai_system_claim_present is not False
            or self.runtime_integration_present is not False
            or self.matrix_gate_authorized_next_stage is not True
            or self.decision != S1_MF_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1MFB4PIHCaseOutputContractError(
                "S1-MF weakened the complete C14 case output"
            )


def build_dts1_s1mf_b4_pih_case_output_contract(
) -> DTS1S1MFB4PIHCaseOutputContract:
    """Compose C14 and its residuals without executing a replica."""

    source_md = build_dts1_s1md_b4_pih_case_selection_contract()
    source_me = build_dts1_s1me_implementation_receipt()
    if (
        source_md.contract_digest != S1_MF_SOURCE_S1MD_DIGEST
        or source_me.receipt_digest != S1_MF_SOURCE_S1ME_DIGEST
        or source_me.decision != S1_ME_DECISION
        or source_md.target_case_record[0] != S1_MF_CASE_ID
        or source_md.case_selected is not True
        or source_md.runner_extension_implemented is not False
        or source_md.exact_implementation_execution_authorized_next_stage is not True
        or source_me.target_output_digests != S1_ME_TARGET_OUTPUT_DIGESTS
        or source_me.target_comparison_digests != S1_ME_TARGET_COMPARISON_DIGESTS
        or source_me.target_components_by_refinement
        != S1_ME_TARGET_COMPONENTS_BY_REFINEMENT
        or source_me.checkpoint_field_digests != S1_ME_CHECKPOINT_FIELD_DIGESTS
        or source_me.checkpoint_private_state_digests
        != S1_ME_CHECKPOINT_PRIVATE_STATE_DIGESTS
        or source_me.checkpoint_adapter_output_digests
        != S1_ME_CHECKPOINT_ADAPTER_OUTPUT_DIGESTS
        or source_me.case_output_composed is not False
        or source_me.matrix_case_output_published is not False
        or source_me.baseline_or_candidate_judgment_present is not False
        or source_me.memory_capability_claim_present is not False
        or source_me.ai_system_claim_present is not False
    ):
        raise DTS1S1MFB4PIHCaseOutputContractError(
            "S1-MD selection or S1-ME output source differs"
        )
    residual_values = tuple(
        value for _, values in S1_MF_REFINEMENT_RESIDUALS for value in values
    )
    values = {
        "contract_id": S1_MF_CONTRACT_ID,
        "source_s1md_digest": source_md.contract_digest,
        "source_s1me_receipt_digest": source_me.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_MF_CASE_ID
        ),
        "source_s1me_decision": source_me.decision,
        "case_schema": S1_MF_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_MF_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "sequence_count_per_refinement": 1,
        "checkpoint_count_per_refinement": 3,
        "component_count_per_refinement": 8,
        "primary_refinement": 4,
        "comparison_digest_count": len(set(S1_ME_TARGET_COMPARISON_DIGESTS)),
        "distinct_provenance_digest_count": len(set(S1_ME_TARGET_OUTPUT_DIGESTS)),
        "residual_block_count": 2,
        "residual_component_count": len(residual_values),
        "checkpoint_parent_identity_valid": True,
        "refinement_outputs_distinct": True,
        "all_primary_components_zero": all(value == 0.0 for value in _COMPONENTS[4]),
        "primary_components_nonzero": all(value != 0.0 for value in _COMPONENTS[4]),
        "all_refinement_residuals_zero": all(value == 0.0 for value in residual_values),
        "refinement_residuals_nonzero_present": any(value != 0.0 for value in residual_values),
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "memory_capability_claim_present": False,
        "ai_system_claim_present": False,
        "runtime_integration_present": False,
        "matrix_gate_authorized_next_stage": True,
        "decision": S1_MF_DECISION,
    }
    return DTS1S1MFB4PIHCaseOutputContract(
        **values, contract_digest=_digest(values)
    )
