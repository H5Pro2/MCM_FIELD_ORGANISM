"""Static S1-KM correction contract for B1 checkpoint replica identity."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    S1_KF_EXEMPLAR_COMPARISON_DIGEST,
    S1_KH_TARGET_OUTPUT_DIGESTS,
    S1_KH_TARGET_REPLICA_IDS,
)
from .dynamic_substrate_s1ke_dual_refinement_digest_contract import (
    S1_KE_CHECKPOINT_EXCLUSIONS,
    S1_KE_CORRECTED_OUTPUT_SCHEMA,
)
from .dynamic_substrate_s1kl_checkpoint_identity_audit import (
    build_dts1_s1kl_checkpoint_identity_audit,
)


class DTS1S1KMCheckpointIdentityCorrectionContractError(ValueError):
    """Raised when the finite S1-KM correction contract is weakened."""


S1_KM_CONTRACT_ID = (
    "dynamic-substrate.checkpoint-replica-identity-correction-overlay.s1km.v1"
)
S1_KM_SOURCE_S1KL_DIGEST = (
    "5f19cfa319ee82838ec5a6af12d92d7e945591bdc5ba3f11ce4d499d4b86ebff"
)
S1_KM_TARGET_REPLICA_IDS = S1_KH_TARGET_REPLICA_IDS
S1_KM_HISTORICAL_OUTPUT_DIGESTS = S1_KH_TARGET_OUTPUT_DIGESTS
S1_KM_BOUND_COMPARISON_DIGEST = S1_KF_EXEMPLAR_COMPARISON_DIGEST
S1_KM_IDENTITY_RULES = (
    "every-checkpoint-replica_id-must-bit-equal-its-parent-output-replica_id",
    "complete-output-validation-must-fail-closed-on-any-checkpoint-parent-identity-mismatch",
    "runner-must-pass-the-requested-registered-replica_id-to-every-checkpoint",
)
S1_KM_VERSIONING_RULES = (
    "S1-KM-v1-is-a-versioned-semantic-overlay-on-mcm.s1jz.complete-replica-output.v2",
    "v2-field-order-and-dual-digest-algorithms-remain-unchanged",
    "historical-B1-r4-r8-v2-outputs-and-digests-remain-immutable-invalid-provenance-records",
    "corrected-B1-r4-r8-v2-outputs-must-have-new-complete-provenance-digests",
    "comparison-digest-must-remain-bit-identical-because-checkpoint-replica_id-is-an-S1-KE-exclusion",
)
S1_KM_RERUN_PLAN = (
    ("target_replica_count", 2),
    ("interval_calls_per_target", 4),
    ("maximum_new_interval_calls", 8),
    ("retry_or_repeat_calls", 0),
)
S1_KM_ACCEPTANCE_RULES = (
    "publish-only-one-atomic-corrected-B1-r4-r8-pair-or-one-error",
    "all-four-checkpoint-replica-ids-in-each-output-equal-that-parent-output-id",
    "all-numeric-checkpoints-components-and-adapter-diagnostics-bit-equal-historical-content",
    "both-comparison-digests-bit-equal-the-bound-B1-r2-comparison-digest",
    "both-corrected-provenance-digests-differ-from-each-other-and-from-both-historical-digests",
)
S1_KM_UNAFFECTED_SCOPE = (
    "B1-r2-remains-the-accepted-unchanged-control-and-is-not-rerun",
    "all-B2-P_IE-outputs-remain-accepted-and-are-not-rerun",
    "no-other-role-profile-or-refinement-is-registered-by-this-overlay",
)
S1_KM_FORBIDDEN_SCOPE = (
    "no-runner-checkpoint-validator-or-output-implementation",
    "no-replica-interval-retry-or-repeat-execution",
    "no-historical-output-or-digest-rewrite",
    "no-C01-C05-or-24-case-matrix-publication",
    "no-baseline-candidate-runtime-or-research-judgment",
)
S1_KM_DECISION = (
    "VERSIONED_B1_R4_R8_CHECKPOINT_IDENTITY_CORRECTION_BOUND_EIGHT_CALL_BUDGET_NO_EXECUTION"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1KMCheckpointIdentityCorrectionContract:
    contract_id: str
    source_s1kl_digest: str
    corrected_output_schema: tuple[tuple[str, object], ...]
    checkpoint_comparison_exclusions: tuple[tuple[str, str], ...]
    target_replica_ids: tuple[str, str]
    historical_output_digests: tuple[str, str]
    bound_comparison_digest: str
    identity_rules: tuple[str, ...]
    versioning_rules: tuple[str, ...]
    rerun_plan: tuple[tuple[str, int], ...]
    acceptance_rules: tuple[str, ...]
    unaffected_scope: tuple[str, ...]
    forbidden_scope: tuple[str, ...]
    target_replica_count: int
    intervals_per_target: int
    maximum_new_interval_calls: int
    semantic_overlay_bound: bool
    output_schema_version_changed: bool
    runner_correction_implemented: bool
    replicas_executed: int
    interval_calls_executed: int
    historical_records_rewritten: bool
    case_composition_blocked: bool
    exact_correction_and_rerun_authorized_next_stage: bool
    decision: str
    contract_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "contract_digest"
        }
        if (
            self.contract_id != S1_KM_CONTRACT_ID
            or self.source_s1kl_digest != S1_KM_SOURCE_S1KL_DIGEST
            or self.corrected_output_schema != S1_KE_CORRECTED_OUTPUT_SCHEMA
            or self.checkpoint_comparison_exclusions != S1_KE_CHECKPOINT_EXCLUSIONS
            or self.target_replica_ids != S1_KM_TARGET_REPLICA_IDS
            or self.historical_output_digests != S1_KM_HISTORICAL_OUTPUT_DIGESTS
            or self.bound_comparison_digest != S1_KM_BOUND_COMPARISON_DIGEST
            or self.identity_rules != S1_KM_IDENTITY_RULES
            or self.versioning_rules != S1_KM_VERSIONING_RULES
            or self.rerun_plan != S1_KM_RERUN_PLAN
            or self.acceptance_rules != S1_KM_ACCEPTANCE_RULES
            or self.unaffected_scope != S1_KM_UNAFFECTED_SCOPE
            or self.forbidden_scope != S1_KM_FORBIDDEN_SCOPE
            or self.target_replica_count != 2
            or self.intervals_per_target != 4
            or self.maximum_new_interval_calls != 8
            or self.semantic_overlay_bound is not True
            or self.output_schema_version_changed is not False
            or self.runner_correction_implemented is not False
            or self.replicas_executed != 0
            or self.interval_calls_executed != 0
            or self.historical_records_rewritten is not False
            or self.case_composition_blocked is not True
            or self.exact_correction_and_rerun_authorized_next_stage is not True
            or self.decision != S1_KM_DECISION
            or self.contract_digest != _digest(payload)
        ):
            raise DTS1S1KMCheckpointIdentityCorrectionContractError(
                "S1-KM weakened the checkpoint identity correction contract"
            )


def build_dts1_s1km_checkpoint_identity_correction_contract(
) -> DTS1S1KMCheckpointIdentityCorrectionContract:
    """Bind the correction overlay without changing or invoking the runner."""

    source = build_dts1_s1kl_checkpoint_identity_audit()
    if (
        source.audit_digest != S1_KM_SOURCE_S1KL_DIGEST
        or source.mismatched_checkpoint_count != 8
        or source.affected_output_digests != S1_KM_HISTORICAL_OUTPUT_DIGESTS
        or dict(S1_KE_CHECKPOINT_EXCLUSIONS).get("replica_id")
        != "refinement-specific-control-identity"
    ):
        raise DTS1S1KMCheckpointIdentityCorrectionContractError(
            "S1-KL evidence or S1-KE comparison exclusion differs"
        )
    values = {
        "contract_id": S1_KM_CONTRACT_ID,
        "source_s1kl_digest": source.audit_digest,
        "corrected_output_schema": S1_KE_CORRECTED_OUTPUT_SCHEMA,
        "checkpoint_comparison_exclusions": S1_KE_CHECKPOINT_EXCLUSIONS,
        "target_replica_ids": S1_KM_TARGET_REPLICA_IDS,
        "historical_output_digests": S1_KM_HISTORICAL_OUTPUT_DIGESTS,
        "bound_comparison_digest": S1_KM_BOUND_COMPARISON_DIGEST,
        "identity_rules": S1_KM_IDENTITY_RULES,
        "versioning_rules": S1_KM_VERSIONING_RULES,
        "rerun_plan": S1_KM_RERUN_PLAN,
        "acceptance_rules": S1_KM_ACCEPTANCE_RULES,
        "unaffected_scope": S1_KM_UNAFFECTED_SCOPE,
        "forbidden_scope": S1_KM_FORBIDDEN_SCOPE,
        "target_replica_count": 2,
        "intervals_per_target": 4,
        "maximum_new_interval_calls": 8,
        "semantic_overlay_bound": True,
        "output_schema_version_changed": False,
        "runner_correction_implemented": False,
        "replicas_executed": 0,
        "interval_calls_executed": 0,
        "historical_records_rewritten": False,
        "case_composition_blocked": True,
        "exact_correction_and_rerun_authorized_next_stage": True,
        "decision": S1_KM_DECISION,
    }
    return DTS1S1KMCheckpointIdentityCorrectionContract(
        **values, contract_digest=_digest(values)
    )
