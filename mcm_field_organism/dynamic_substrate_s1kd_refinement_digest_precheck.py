"""Static S1-KD precheck for refinement comparison digest semantics."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_one_replica_orchestrator import (
    build_dts1_s1kc_implementation_receipt,
)
from .dynamic_substrate_s1jx_sequence_carry_orchestration_contract import (
    build_dts1_s1jx_sequence_carry_orchestration_contract,
)
from .dynamic_substrate_s1jz_finite_orchestrator_api_contract import (
    build_dts1_s1jz_finite_orchestrator_api_contract,
)


class DTS1S1KDRefinementDigestPrecheckError(ValueError):
    """Raised when the S1-KD refinement-digest stop is weakened."""


S1_KD_AUDIT_ID = "dynamic-substrate.refinement-digest-precheck.s1kd.v1"
S1_KD_SOURCE_S1KC_DIGEST = (
    "59b721a33fddf278c2cc858db40aafdca270e33006ec0cc0cbca82cbfedf177c"
)
S1_KD_SOURCE_S1JX_DIGEST = (
    "4bbf3bfb4997fe7e5ad3364276f127d6a8eb53c6b2452c0b4cac387e097cb5a8"
)
S1_KD_SOURCE_S1JZ_DIGEST = (
    "83a5c6248d0dca0e0ba2461bbc6c0f76470a5af1b21ac89049238f1256380079"
)
S1_KD_TARGET_REPLICAS = (
    ("B1:P_IE_CAUSAL_TWO_SUBSTEP:r2", 2),
    ("B1:P_IE_CAUSAL_TWO_SUBSTEP:r4", 4),
    ("B1:P_IE_CAUSAL_TWO_SUBSTEP:r8", 8),
)
S1_KD_CONFLICT_RECORDS = (
    (
        "S1-JX",
        "B1-and-B2-require-bit-identical-complete-replica-output-digests-across-r2-r4-r8",
    ),
    ("S1-JZ-output", "complete-output-includes-replica_id-and-refinement"),
    ("S1-JZ-checkpoint", "each-complete-checkpoint-includes-replica_id"),
    ("S1-KC-digest", "output-digest-covers-the-complete-identity-bearing-output-payload"),
)
S1_KD_REQUIRED_CORRECTION = (
    "retain-one-identity-bearing-complete-output-digest-for-provenance-and-tamper-evidence",
    "bind-one-separate-identity-neutral-refinement-comparison-payload-and-digest",
    "enumerate-exactly-which-replica-and-refinement-identity-fields-are-excluded-only-from-comparison",
    "revise-the-S1-JX-B1-B2-bit-identity-rule-and-S1-JZ-output-schema-before-r4-r8-implementation",
    "require-bit-identity-of-the-bound-comparison-content-without-equating-complete-provenance-digests",
)
S1_KD_DECISION = (
    "STOPP_B1_REFINEMENT_BIT_IDENTITY_CONFLICTS_WITH_IDENTITY_BEARING_COMPLETE_OUTPUT_DIGEST"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1KDRefinementDigestPrecheck:
    audit_id: str
    source_s1kc_digest: str
    source_s1jx_digest: str
    source_s1jz_digest: str
    target_replicas: tuple[tuple[str, int], ...]
    conflict_records: tuple[tuple[str, str], ...]
    complete_output_identity_fields: tuple[str, ...]
    checkpoint_identity_fields: tuple[str, ...]
    hypothetical_identity_digests: tuple[str, ...]
    distinct_hypothetical_digest_count: int
    required_correction: tuple[str, ...]
    r4_r8_runner_extension_authorized: bool
    r4_r8_replicas_executed: int
    interval_calls_executed: int
    complete_matrix_cases_executed: int
    runtime_integration_present: bool
    research_execution_permitted: bool
    correction_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_KD_AUDIT_ID
            or self.source_s1kc_digest != S1_KD_SOURCE_S1KC_DIGEST
            or self.source_s1jx_digest != S1_KD_SOURCE_S1JX_DIGEST
            or self.source_s1jz_digest != S1_KD_SOURCE_S1JZ_DIGEST
            or self.target_replicas != S1_KD_TARGET_REPLICAS
            or self.conflict_records != S1_KD_CONFLICT_RECORDS
            or self.complete_output_identity_fields != ("replica_id", "refinement")
            or self.checkpoint_identity_fields != ("replica_id",)
            or len(self.hypothetical_identity_digests) != 3
            or self.distinct_hypothetical_digest_count != 3
            or len(set(self.hypothetical_identity_digests)) != 3
            or self.required_correction != S1_KD_REQUIRED_CORRECTION
            or self.r4_r8_runner_extension_authorized is not False
            or self.r4_r8_replicas_executed != 0
            or self.interval_calls_executed != 0
            or self.complete_matrix_cases_executed != 0
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.correction_contract_authorized_next_stage is not True
            or self.decision != S1_KD_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1KDRefinementDigestPrecheckError(
                "S1-KD weakened the refinement digest stop"
            )


def build_dts1_s1kd_refinement_digest_precheck(
) -> DTS1S1KDRefinementDigestPrecheck:
    """Audit identity-bearing digest semantics without running a replica."""

    kc = build_dts1_s1kc_implementation_receipt()
    jx = build_dts1_s1jx_sequence_carry_orchestration_contract()
    jz = build_dts1_s1jz_finite_orchestrator_api_contract()
    output_fields = tuple(dict(jz.replica_output_schema)["fields"])
    checkpoint_fields = tuple(dict(jz.checkpoint_schema)["fields"])
    required_rule = S1_KD_CONFLICT_RECORDS[0][1]
    if (
        kc.receipt_digest != S1_KD_SOURCE_S1KC_DIGEST
        or jx.contract_digest != S1_KD_SOURCE_S1JX_DIGEST
        or jz.contract_digest != S1_KD_SOURCE_S1JZ_DIGEST
        or required_rule not in jx.refinement_output_rules
        or "replica_id" not in output_fields
        or "refinement" not in output_fields
        or "replica_id" not in checkpoint_fields
    ):
        raise DTS1S1KDRefinementDigestPrecheckError(
            "source contracts no longer expose the audited conflict"
        )
    hypothetical_digests = tuple(
        _digest({"replica_id": replica_id, "refinement": refinement})
        for replica_id, refinement in S1_KD_TARGET_REPLICAS
    )
    values = {
        "audit_id": S1_KD_AUDIT_ID,
        "source_s1kc_digest": kc.receipt_digest,
        "source_s1jx_digest": jx.contract_digest,
        "source_s1jz_digest": jz.contract_digest,
        "target_replicas": S1_KD_TARGET_REPLICAS,
        "conflict_records": S1_KD_CONFLICT_RECORDS,
        "complete_output_identity_fields": ("replica_id", "refinement"),
        "checkpoint_identity_fields": ("replica_id",),
        "hypothetical_identity_digests": hypothetical_digests,
        "distinct_hypothetical_digest_count": len(set(hypothetical_digests)),
        "required_correction": S1_KD_REQUIRED_CORRECTION,
        "r4_r8_runner_extension_authorized": False,
        "r4_r8_replicas_executed": 0,
        "interval_calls_executed": 0,
        "complete_matrix_cases_executed": 0,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "correction_contract_authorized_next_stage": True,
        "decision": S1_KD_DECISION,
    }
    return DTS1S1KDRefinementDigestPrecheck(
        **values, audit_digest=_digest(values)
    )
