"""Static S1-LE complete B1/P_IN C04 case output contract."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_LD_TARGET_COMPARISON_DIGEST,
    S1_LD_TARGET_COMPONENTS,
    S1_LD_TARGET_OUTPUT_DIGESTS,
    S1_LD_TARGET_REPLICA_IDS,
    S1_LD_TERMINAL_ADAPTER_OUTPUT_DIGEST,
    S1_LD_TERMINAL_FIELD_DIGEST,
    S1_LD_TERMINAL_PRIVATE_STATE_DIGEST,
    build_dts1_s1ld_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
)
from .dynamic_substrate_s1lb_b2_pik_case_output_contract import (
    build_dts1_s1lb_b2_pik_case_output_contract,
)


class DTS1S1LEB1PINCaseOutputContractError(ValueError):
    """Raised when the finite S1-LE C04 case output is weakened."""


S1_LE_CONTRACT_ID = "dynamic-substrate.b1-pin-case-output.s1le.v1"
S1_LE_SOURCE_S1LB_DIGEST = (
    "d5ebc93d6521d384d0087ea2601df52a5b0ebe2cacea34d3b920966b326c54ed"
)
S1_LE_SOURCE_S1LD_DIGEST = (
    "c4eb4fa0b8c1c79979c6a9bf28fc15c765d9a45d155c48665ae69dd6df513169"
)
S1_LE_CASE_ID = "C04"
S1_LE_COMPONENTS_BY_REFINEMENT = tuple(
    (refinement, S1_LD_TARGET_COMPONENTS) for refinement in (2, 4, 8)
)
S1_LE_TERMINAL_FIELD_DIGESTS = (S1_LD_TERMINAL_FIELD_DIGEST,) * 2
S1_LE_TERMINAL_PRIVATE_STATE_DIGESTS = (
    S1_LD_TERMINAL_PRIVATE_STATE_DIGEST,
) * 2
S1_LE_TERMINAL_ADAPTER_OUTPUT_DIGESTS = (
    S1_LD_TERMINAL_ADAPTER_OUTPUT_DIGEST,
) * 2
S1_LE_CASE_SCHEMA = (
    ("schema_id", "mcm.s1le.complete-three-refinement-case.v1"),
    ("fields", (
        "schema_id", "case_id", "model_role", "long_model_role",
        "profile_block", "node_count", "component_count", "replica_ids",
        "replica_output_digests", "refinement_comparison_digest",
        "components_by_refinement", "terminal_field_digests",
        "terminal_private_state_digests", "terminal_adapter_output_digests",
        "primary_refinement", "primary_components",
        "checkpoint_parent_identity_valid", "sequence_terminals_bit_identical",
        "refinement_bit_identity", "status", "case_output_digest",
    )),
    ("publication", "one-complete-case-record-or-one-error-with-no-partial-value"),
)
S1_LE_STATUS = "TECHNICALLY_COMPLETE_NO_RELEASE_REUSE_BASELINE_OR_CANDIDATE_JUDGMENT"
S1_LE_DECISION = (
    "C04_B1_PIN_THREE_REFINEMENT_CASE_OUTPUT_BOUND_FROM_S1LD_RECEIPT_NO_NEW_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _case_payload() -> dict[str, object]:
    return {
        "schema_id": "mcm.s1le.complete-three-refinement-case.v1",
        "case_id": S1_LE_CASE_ID,
        "model_role": "B1",
        "long_model_role": "B1_FIXED_PRERELEASE_ADAPTER",
        "profile_block": "P_IN_RELEASE_REUSE",
        "node_count": 3,
        "component_count": 6,
        "replica_ids": S1_LD_TARGET_REPLICA_IDS,
        "replica_output_digests": S1_LD_TARGET_OUTPUT_DIGESTS,
        "refinement_comparison_digest": S1_LD_TARGET_COMPARISON_DIGEST,
        "components_by_refinement": S1_LE_COMPONENTS_BY_REFINEMENT,
        "terminal_field_digests": S1_LE_TERMINAL_FIELD_DIGESTS,
        "terminal_private_state_digests": S1_LE_TERMINAL_PRIVATE_STATE_DIGESTS,
        "terminal_adapter_output_digests": S1_LE_TERMINAL_ADAPTER_OUTPUT_DIGESTS,
        "primary_refinement": 4,
        "primary_components": S1_LD_TARGET_COMPONENTS,
        "checkpoint_parent_identity_valid": True,
        "sequence_terminals_bit_identical": True,
        "refinement_bit_identity": True,
        "status": S1_LE_STATUS,
    }


S1_LE_CASE_OUTPUT_DIGEST = _digest(_case_payload())


@dataclass(frozen=True, slots=True)
class DTS1S1LEB1PINCaseOutputContract:
    contract_id: str
    source_s1lb_digest: str
    source_s1ld_digest: str
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
    sequence_terminals_bit_identical: bool
    terminal_digest_pairs_bit_identical_across_refinements: bool
    all_components_bit_identical: bool
    nonzero_component_count: int
    case_record_composed: bool
    new_replicas_executed: int
    new_interval_calls_executed: int
    matrix_24_case_output_published: bool
    release_reuse_judgment_present: bool
    baseline_judgment_present: bool
    candidate_comparison_present: bool
    runtime_integration_present: bool
    b2_pin_case_selection_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        expected_case = next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_LE_CASE_ID
        )
        if (
            self.contract_id != S1_LE_CONTRACT_ID
            or self.source_s1lb_digest != S1_LE_SOURCE_S1LB_DIGEST
            or self.source_s1ld_digest != S1_LE_SOURCE_S1LD_DIGEST
            or self.source_s1jx_case_record != expected_case
            or self.case_schema != S1_LE_CASE_SCHEMA
            or self.case_payload != tuple(_case_payload().items())
            or self.case_output_digest != S1_LE_CASE_OUTPUT_DIGEST
            or (self.replica_count, self.sequence_count_per_refinement, self.checkpoint_count_per_refinement, self.component_count_per_refinement) != (3, 2, 2, 6)
            or (self.primary_refinement, self.comparison_digest_count, self.distinct_provenance_digest_count) != (4, 1, 3)
            or self.checkpoint_parent_identity_valid is not True
            or self.sequence_terminals_bit_identical is not True
            or self.terminal_digest_pairs_bit_identical_across_refinements is not True
            or self.all_components_bit_identical is not True
            or self.nonzero_component_count != 0
            or self.case_record_composed is not True
            or (self.new_replicas_executed, self.new_interval_calls_executed) != (0, 0)
            or self.matrix_24_case_output_published is not False
            or self.release_reuse_judgment_present is not False
            or self.baseline_judgment_present is not False
            or self.candidate_comparison_present is not False
            or self.runtime_integration_present is not False
            or self.b2_pin_case_selection_authorized_next_stage is not True
            or self.decision != S1_LE_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1LEB1PINCaseOutputContractError(
                "S1-LE weakened the complete C04 case output"
            )


def build_dts1_s1le_b1_pin_case_output_contract(
) -> DTS1S1LEB1PINCaseOutputContract:
    """Compose C04 from bound receipts without executing a replica."""

    prior = build_dts1_s1lb_b2_pik_case_output_contract()
    source = build_dts1_s1ld_implementation_receipt()
    if (
        prior.contract_digest != S1_LE_SOURCE_S1LB_DIGEST
        or source.receipt_digest != S1_LE_SOURCE_S1LD_DIGEST
        or source.target_output_digests != S1_LD_TARGET_OUTPUT_DIGESTS
        or source.target_components != S1_LD_TARGET_COMPONENTS
        or source.terminal_field_digests != S1_LE_TERMINAL_FIELD_DIGESTS
        or source.terminal_private_state_digests
        != S1_LE_TERMINAL_PRIVATE_STATE_DIGESTS
        or source.terminal_adapter_output_digests
        != S1_LE_TERMINAL_ADAPTER_OUTPUT_DIGESTS
    ):
        raise DTS1S1LEB1PINCaseOutputContractError(
            "S1-LB case source or S1-LD output source differs"
        )
    components = tuple(row[1] for row in S1_LE_COMPONENTS_BY_REFINEMENT)
    values = {
        "contract_id": S1_LE_CONTRACT_ID,
        "source_s1lb_digest": prior.contract_digest,
        "source_s1ld_digest": source.receipt_digest,
        "source_s1jx_case_record": next(
            row for row in S1_JX_CASE_RECORDS if row[0] == S1_LE_CASE_ID
        ),
        "case_schema": S1_LE_CASE_SCHEMA,
        "case_payload": tuple(_case_payload().items()),
        "case_output_digest": S1_LE_CASE_OUTPUT_DIGEST,
        "replica_count": 3,
        "sequence_count_per_refinement": 2,
        "checkpoint_count_per_refinement": 2,
        "component_count_per_refinement": 6,
        "primary_refinement": 4,
        "comparison_digest_count": 1,
        "distinct_provenance_digest_count": len(set(S1_LD_TARGET_OUTPUT_DIGESTS)),
        "checkpoint_parent_identity_valid": True,
        "sequence_terminals_bit_identical": True,
        "terminal_digest_pairs_bit_identical_across_refinements": True,
        "all_components_bit_identical": len(set(components)) == 1,
        "nonzero_component_count": sum(
            value != 0.0 for value in S1_LD_TARGET_COMPONENTS
        ),
        "case_record_composed": True,
        "new_replicas_executed": 0,
        "new_interval_calls_executed": 0,
        "matrix_24_case_output_published": False,
        "release_reuse_judgment_present": False,
        "baseline_judgment_present": False,
        "candidate_comparison_present": False,
        "runtime_integration_present": False,
        "b2_pin_case_selection_authorized_next_stage": True,
        "decision": S1_LE_DECISION,
    }
    return DTS1S1LEB1PINCaseOutputContract(
        **values, contract_digest=_digest(values)
    )
