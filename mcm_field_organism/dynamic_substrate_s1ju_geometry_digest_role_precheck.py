"""Static S1-JU precheck for outer and internal geometry digest roles."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jt_finite_adapter_payload_contract import (
    build_dts1_s1jt_finite_adapter_payload_contract,
)


class DTS1S1JUGeometryDigestRolePrecheckError(ValueError):
    """Raised when the S1-JU geometry digest stop is weakened."""


S1_JU_AUDIT_ID = "dynamic-substrate.geometry-digest-role-precheck.s1ju.v1"
S1_JU_SOURCE_S1JT_DIGEST = (
    "10a01aa9275a3bb571f3d5113126e90a0183d862c42cf1a9f8a2b58da1285d40"
)
S1_JU_GEOMETRY_DIGEST_RECORDS = (
    (
        "TWO_NODE_OPEN_LINE",
        ("node-a", "node-b"),
        "5f7bdc4e0e657a613262c237fbd3bdd5a8bff0073be0aa5890ce6b4f58ae810d",
        "77595b855f2d1ed9b208508fea1225364162ad5b8156c9532bbff52fc9ee6b72",
        False,
    ),
    (
        "THREE_NODE_OPEN_LINE",
        ("node-a", "node-b", "node-c"),
        "2efcf504573780a314947cb0fba3c64e152ff5f776666af7d4283b75b564aa49",
        "2536e5e2bc075c703ef9d707132b97ce626857ab7f7fe70d0080d7b7de84273a",
        False,
    ),
)
S1_JU_DIGEST_ROLE_DEFINITIONS = (
    (
        "outer_common_geometry_digest",
        "S1-JG-S1-JK-envelope-and-S1-JO-model-invocation",
        "commits-to-the-registered-complete-open-line-exposure-geometry-identity",
        "must-remain-model-facing-and-cross-model-identical-for-one-geometry",
    ),
    (
        "internal_edge_inventory_digest",
        "mcm_substrate_edge_inventory_digest-of-the-complete-MCMNeuronLayer",
        "commits-to-canonical-node-identities-positions-sampling-offsets-and-derived-undirected-edges",
        "required-by-DTS1BackreactionResult-MCMSubstrateState-and-F3-kernel-validation",
    ),
)
S1_JU_CONFLICT_FINDINGS = (
    "S1-JT-B1-binds-one-edge-inventory-digest-field-without-explicitly-selecting-the-internal-digest-role",
    "the-S1-JO-model-invocation-exposes-only-the-outer-common-geometry-digest",
    "DTS1BackreactionResult-rejects-the-outer-digest-because-it-requires-the-internal-layer-edge-inventory-digest",
    "both-registered-geometries-have-distinct-outer-and-internal-digest-values",
    "a-generic-adapter-check-that-equates-both-digests-rejects-every-valid-B1-through-B6-invocation-before-kernel-entry",
    "B3-through-B6-already-carry-the-correct-internal-digest-inside-MCMSubstrateState-but-still-require-an-explicit-outer-to-internal-geometry-pair-check",
    "B2-needs-the-same-pair-check-for-geometry-integrity-even-though-S2ReferenceState-has-no-edge-digest-field",
)
S1_JU_PRESERVED_BINDINGS = (
    "all-S1-JK-outer-geometry-sequence-interval-time-and-carry-digests",
    "the-four-value-S1-JO-model-invocation-and-four-separated-integrity-digests",
    "all-S1-JT-values-private-payload-shapes-runtime-records-diagnostics-output-and-error-rules-not-dependent-on-digest-role",
    "the-B1-two-node-rate-1.2-and-three-node-rates-1.1-remain-bound",
    "all-existing-baseline-kernels-and-internal-edge-digest-validation-remain-unchanged",
)
S1_JU_FORBIDDEN_REPAIRS = (
    "replace-recompute-or-relabel-any-existing-S1-JK-or-S1-JO-outer-digest",
    "pass-the-outer-digest-into-DTS1BackreactionResult-or-MCMSubstrateState",
    "drop-the-outer-digest-or-skip-cross-checking-it-against-the-registered-geometry-pair",
    "change-the-internal-edge-inventory-digest-algorithm-or-kernel-validation",
    "choose-a-digest-by-role-profile-control-label-or-observed-output",
    "continue-partial-adapter-implementation-or-kernel-testing-before-correction",
)
S1_JU_REQUIRED_CORRECTION = (
    "bind-one-finite-outer-to-internal-digest-pair-for-each-of-the-two-registered-geometries",
    "bind-node-inventory-and-field-identity-as-the-non-ambiguous-pair-selection-key",
    "bind-B1-fixed-adapter-payload-edge_inventory_digest-exclusively-to-the-internal-role",
    "bind-B2-and-B3-through-B6-prekernel-validation-to-both-the-outer-and-internal-role-without-equating-them",
    "replace-only-S1-JT-wording-and-dependent-digests-that-left-the-B1-digest-role-ambiguous",
)
S1_JU_DECISION = (
    "STOPP_OUTER_COMMON_GEOMETRY_AND_INTERNAL_EDGE_INVENTORY_DIGEST_ROLES_NOT_SEPARATED"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1JUGeometryDigestRolePrecheck:
    audit_id: str
    source_s1jt_digest: str
    geometry_digest_records: tuple[tuple[str, tuple[str, ...], str, str, bool], ...]
    digest_role_definitions: tuple[tuple[str, str, str, str], ...]
    conflict_findings: tuple[str, ...]
    preserved_bindings: tuple[str, ...]
    forbidden_repairs: tuple[str, ...]
    required_correction: tuple[str, ...]
    geometry_count: int
    unequal_digest_pair_count: int
    adapter_implementation_ready: bool
    adapters_implemented: bool
    baseline_kernels_called: bool
    profile_cases_executed: int
    runtime_integration_present: bool
    research_execution_permitted: bool
    research_field_steps_executed: int
    corrected_digest_role_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        if (
            self.audit_id != S1_JU_AUDIT_ID
            or self.source_s1jt_digest != S1_JU_SOURCE_S1JT_DIGEST
            or self.geometry_digest_records != S1_JU_GEOMETRY_DIGEST_RECORDS
            or self.digest_role_definitions != S1_JU_DIGEST_ROLE_DEFINITIONS
            or self.conflict_findings != S1_JU_CONFLICT_FINDINGS
            or self.preserved_bindings != S1_JU_PRESERVED_BINDINGS
            or self.forbidden_repairs != S1_JU_FORBIDDEN_REPAIRS
            or self.required_correction != S1_JU_REQUIRED_CORRECTION
            or self.geometry_count != 2
            or self.unequal_digest_pair_count != 2
            or self.adapter_implementation_ready is not False
            or self.adapters_implemented is not False
            or self.baseline_kernels_called is not False
            or self.profile_cases_executed != 0
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.research_field_steps_executed != 0
            or self.corrected_digest_role_contract_authorized_next_stage is not True
            or self.decision != S1_JU_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1JUGeometryDigestRolePrecheckError(
                "S1-JU weakened the geometry digest role stop"
            )


def build_dts1_s1ju_geometry_digest_role_precheck(
) -> DTS1S1JUGeometryDigestRolePrecheck:
    """Audit two digest roles without constructing or running an adapter."""

    source = build_dts1_s1jt_finite_adapter_payload_contract()
    values = {
        "audit_id": S1_JU_AUDIT_ID,
        "source_s1jt_digest": source.contract_digest,
        "geometry_digest_records": S1_JU_GEOMETRY_DIGEST_RECORDS,
        "digest_role_definitions": S1_JU_DIGEST_ROLE_DEFINITIONS,
        "conflict_findings": S1_JU_CONFLICT_FINDINGS,
        "preserved_bindings": S1_JU_PRESERVED_BINDINGS,
        "forbidden_repairs": S1_JU_FORBIDDEN_REPAIRS,
        "required_correction": S1_JU_REQUIRED_CORRECTION,
        "geometry_count": len(S1_JU_GEOMETRY_DIGEST_RECORDS),
        "unequal_digest_pair_count": sum(
            not row[4] for row in S1_JU_GEOMETRY_DIGEST_RECORDS
        ),
        "adapter_implementation_ready": False,
        "adapters_implemented": False,
        "baseline_kernels_called": False,
        "profile_cases_executed": 0,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "research_field_steps_executed": 0,
        "corrected_digest_role_contract_authorized_next_stage": True,
        "decision": S1_JU_DECISION,
    }
    return DTS1S1JUGeometryDigestRolePrecheck(
        **values, audit_digest=_digest(values)
    )
