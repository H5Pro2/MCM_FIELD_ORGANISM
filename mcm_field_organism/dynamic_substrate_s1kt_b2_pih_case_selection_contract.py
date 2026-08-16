"""Static S1-KT selection contract for the finite B2/P_IH case."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jz_finite_orchestrator_api_contract import S1_JZ_FRESH_STATE_RECORDS
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    S1_JX_CASE_RECORDS,
    S1_JX_REPLICA_RECORDS,
    S1_JX_SEQUENCE_RECORDS,
)
from .dynamic_substrate_s1ke_dual_refinement_digest_contract import (
    S1_KE_COMPARISON_DIGEST_ROLE,
    S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
    S1_KE_CORRECTED_OUTPUT_SCHEMA,
)
from .dynamic_substrate_s1ks_b1_pih_case_output_contract import (
    build_dts1_s1ks_b1_pih_case_output_contract,
)


class DTS1S1KTB2PIHCaseSelectionContractError(ValueError):
    """Raised when the finite S1-KT case selection is weakened."""


S1_KT_CONTRACT_ID = "dynamic-substrate.b2-pih-case-selection.s1kt.v1"
S1_KT_SOURCE_S1KS_DIGEST = (
    "d2ed48ba9be2fcbac31d069ad9fc741cd517f521b5d8037441ead40fd19e53aa"
)
S1_KT_CASE_ID = "C06"
S1_KT_SEQUENCE_KEY = "P_IH_A_A_A"
S1_KT_TARGET_REPLICA_IDS = (
    "B2:P_IH_ATTENUATION:r2",
    "B2:P_IH_ATTENUATION:r4",
    "B2:P_IH_ATTENUATION:r8",
)
S1_KT_TARGET_CASE_RECORD = next(row for row in S1_JX_CASE_RECORDS if row[0] == S1_KT_CASE_ID)
S1_KT_TARGET_REPLICA_RECORDS = tuple(row for row in S1_JX_REPLICA_RECORDS if row[0] in S1_KT_TARGET_REPLICA_IDS)
S1_KT_SEQUENCE_RECORD = next(row for row in S1_JX_SEQUENCE_RECORDS if row[0] == S1_KT_SEQUENCE_KEY)
S1_KT_FRESH_STATE_RECORD = next(
    row for row in S1_JZ_FRESH_STATE_RECORDS
    if row[0] == "B2" and row[1] == "TWO_NODE_OPEN_LINE"
)
S1_KT_FRESH_FIELD_DIGEST = "389f731c42f91164332fcfda65cc5130d5090db7f03e211736ae0bb6c1ca2f61"
S1_KT_FRESH_PRIVATE_STATE_DIGEST = "06f8e90d235e9676cbdca36863d63c4b1b8f4bda1f508c4110c0bcd5916d3b9d"
S1_KT_FRESH_START_AND_CARRY_RULES = (
    "r2-r4-and-r8-each-start-from-an-independent-corrected-B2-fresh-state",
    "P_IH_A_A_A-starts-once-from-that-refinements-own-fresh-state",
    "complete-field-and-complete-L-private-state-carry-across-all-three-ordered-A-intervals",
    "no-field-L-state-output-or-provenance-carries-between-refinements",
)
S1_KT_EXECUTION_BUDGET = (
    ("target_replica_count", 3),
    ("interval_calls_per_replica", 3),
    ("maximum_new_interval_calls", 9),
    ("retry_or_repeat_calls", 0),
)
S1_KT_OUTPUT_ACCEPTANCE_RULES = (
    "each-replica-publishes-one-atomic-mcm.s1jz.complete-replica-output.v2-or-one-error",
    "each-output-has-three-ordered-checkpoints-eight-signed-components-and-three-adapter-diagnostics",
    "every-checkpoint-replica_id-bit-equals-its-parent-output-replica_id",
    "B2-refinement-comparison-digests-must-be-bit-identical-across-r2-r4-r8",
    "complete-output-digests-remain-identity-bearing-and-must-be-distinct",
    "all-three-replicas-must-pass-before-C06-may-be-composed-in-a-later-stage",
)
S1_KT_SELECTION_RATIONALE = (
    "C06-is-the-stateful-B2-counterpart-to-technically-complete-B1-C02",
    "B2-receives-the-same-P_IH-sequence-geometry-and-checkpoint-plan-as-B1",
    "selection-does-not-predict-sign-threshold-baseline-closure-or-candidate-outcome",
)
S1_KT_FORBIDDEN_SCOPE = (
    "no-runner-initializer-adapter-or-output-implementation",
    "no-replica-interval-retry-or-repeat-execution",
    "no-C06-output-or-24-case-matrix-publication",
    "no-other-role-profile-selection",
    "no-baseline-candidate-runtime-or-research-judgment",
)
S1_KT_DECISION = "B2_PIH_C06_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_NINE_CALL_CONTRACT_BOUND_NO_EXECUTION"


def _digest(payload: object) -> str:
    return hashlib.sha256(json.dumps(payload, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1KTB2PIHCaseSelectionContract:
    contract_id: str
    source_s1ks_digest: str
    target_case_record: tuple[object, ...]
    target_replica_ids: tuple[str, ...]
    target_replica_records: tuple[tuple[object, ...], ...]
    sequence_record: tuple[object, ...]
    corrected_fresh_state_record: tuple[object, ...]
    fresh_field_digest: str
    fresh_private_state_digest: str
    complete_provenance_digest_role: tuple[tuple[str, object], ...]
    comparison_digest_role: tuple[tuple[str, object], ...]
    corrected_output_schema: tuple[tuple[str, object], ...]
    fresh_start_and_carry_rules: tuple[str, ...]
    execution_budget: tuple[tuple[str, int], ...]
    output_acceptance_rules: tuple[str, ...]
    selection_rationale: tuple[str, ...]
    forbidden_scope: tuple[str, ...]
    target_replica_count: int
    intervals_per_target_replica: int
    checkpoints_per_target_replica: int
    signed_components_per_target_replica: int
    maximum_new_interval_calls: int
    case_selected: bool
    runner_extension_implemented: bool
    target_replicas_executed: int
    interval_calls_executed: int
    case_output_composed: bool
    matrix_24_case_output_published: bool
    baseline_judgment_present: bool
    runtime_integration_present: bool
    exact_implementation_execution_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {field.name: getattr(self, field.name) for field in fields(self) if field.name != "contract_digest"}
        if (
            self.contract_id != S1_KT_CONTRACT_ID
            or self.source_s1ks_digest != S1_KT_SOURCE_S1KS_DIGEST
            or self.target_case_record != S1_KT_TARGET_CASE_RECORD
            or self.target_replica_ids != S1_KT_TARGET_REPLICA_IDS
            or self.target_replica_records != S1_KT_TARGET_REPLICA_RECORDS
            or self.sequence_record != S1_KT_SEQUENCE_RECORD
            or self.corrected_fresh_state_record != S1_KT_FRESH_STATE_RECORD
            or self.fresh_field_digest != S1_KT_FRESH_FIELD_DIGEST
            or self.fresh_private_state_digest != S1_KT_FRESH_PRIVATE_STATE_DIGEST
            or self.complete_provenance_digest_role != S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE
            or self.comparison_digest_role != S1_KE_COMPARISON_DIGEST_ROLE
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.fresh_start_and_carry_rules != S1_KT_FRESH_START_AND_CARRY_RULES
            or self.execution_budget != S1_KT_EXECUTION_BUDGET
            or self.output_acceptance_rules != S1_KT_OUTPUT_ACCEPTANCE_RULES
            or self.selection_rationale != S1_KT_SELECTION_RATIONALE
            or self.forbidden_scope != S1_KT_FORBIDDEN_SCOPE
            or (self.target_replica_count, self.intervals_per_target_replica, self.checkpoints_per_target_replica, self.signed_components_per_target_replica, self.maximum_new_interval_calls) != (3, 3, 3, 8, 9)
            or self.case_selected is not True
            or self.runner_extension_implemented is not False
            or (self.target_replicas_executed, self.interval_calls_executed) != (0, 0)
            or self.case_output_composed is not False
            or self.matrix_24_case_output_published is not False
            or self.baseline_judgment_present is not False
            or self.runtime_integration_present is not False
            or self.exact_implementation_execution_authorized_next_stage is not True
            or self.decision != S1_KT_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KTB2PIHCaseSelectionContractError("S1-KT weakened the finite B2/P_IH case selection")


def build_dts1_s1kt_b2_pih_case_selection_contract() -> DTS1S1KTB2PIHCaseSelectionContract:
    """Select and bind C06 without implementing or executing its replicas."""

    source = build_dts1_s1ks_b1_pih_case_output_contract()
    if (
        source.contract_digest != S1_KT_SOURCE_S1KS_DIGEST
        or len(S1_KT_TARGET_REPLICA_RECORDS) != 3
        or tuple(row[0] for row in S1_KT_TARGET_REPLICA_RECORDS) != S1_KT_TARGET_REPLICA_IDS
        or S1_KT_SEQUENCE_RECORD[3] != 3
        or S1_KT_FRESH_STATE_RECORD[6] != S1_KT_FRESH_FIELD_DIGEST
        or S1_KT_FRESH_STATE_RECORD[8] != S1_KT_FRESH_PRIVATE_STATE_DIGEST
    ):
        raise DTS1S1KTB2PIHCaseSelectionContractError("registered C06 evidence or corrected B2 fresh state differs")
    values = {
        "contract_id": S1_KT_CONTRACT_ID,
        "source_s1ks_digest": source.contract_digest,
        "target_case_record": S1_KT_TARGET_CASE_RECORD,
        "target_replica_ids": S1_KT_TARGET_REPLICA_IDS,
        "target_replica_records": S1_KT_TARGET_REPLICA_RECORDS,
        "sequence_record": S1_KT_SEQUENCE_RECORD,
        "corrected_fresh_state_record": S1_KT_FRESH_STATE_RECORD,
        "fresh_field_digest": S1_KT_FRESH_FIELD_DIGEST,
        "fresh_private_state_digest": S1_KT_FRESH_PRIVATE_STATE_DIGEST,
        "complete_provenance_digest_role": S1_KE_COMPLETE_PROVENANCE_DIGEST_ROLE,
        "comparison_digest_role": S1_KE_COMPARISON_DIGEST_ROLE,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "fresh_start_and_carry_rules": S1_KT_FRESH_START_AND_CARRY_RULES,
        "execution_budget": S1_KT_EXECUTION_BUDGET,
        "output_acceptance_rules": S1_KT_OUTPUT_ACCEPTANCE_RULES,
        "selection_rationale": S1_KT_SELECTION_RATIONALE,
        "forbidden_scope": S1_KT_FORBIDDEN_SCOPE,
        "target_replica_count": 3,
        "intervals_per_target_replica": 3,
        "checkpoints_per_target_replica": 3,
        "signed_components_per_target_replica": 8,
        "maximum_new_interval_calls": 9,
        "case_selected": True,
        "runner_extension_implemented": False,
        "target_replicas_executed": 0,
        "interval_calls_executed": 0,
        "case_output_composed": False,
        "matrix_24_case_output_published": False,
        "baseline_judgment_present": False,
        "runtime_integration_present": False,
        "exact_implementation_execution_authorized_next_stage": True,
        "decision": S1_KT_DECISION,
    }
    return DTS1S1KTB2PIHCaseSelectionContract(**values, contract_digest=_digest(values))
