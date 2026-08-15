"""Static S1-KA precheck for fresh private-state digest roundtrips."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_s1jz_finite_orchestrator_api_contract import (
    build_dts1_s1jz_finite_orchestrator_api_contract,
)


class DTS1S1KAFreshPrivateDigestPrecheckError(ValueError):
    """Raised when the S1-KA fresh-state stop is weakened."""


S1_KA_AUDIT_ID = "dynamic-substrate.fresh-private-digest-precheck.s1ka.v1"
S1_KA_SOURCE_S1JZ_DIGEST = (
    "afc1c2d752aca9e5dd62a5f8ceb08859669e105108c6b23138d67d19aa3d508d"
)
S1_KA_DIGEST_ROUNDTRIP_RECORDS = (
    ("B1", "TWO_NODE_OPEN_LINE", "7edb70af4e533062167bf314106cbb930c5bd15fc6883468937744145ba1084e", "871b0308bfebdcc03a27ff0447f46e054aedc253f1a0975bd77bfbb69b3668d9", False),
    ("B1", "THREE_NODE_OPEN_LINE", "979bbb78c7ae85ea37a37a23e80c5db34b1d989a091e94fb1334ecd90ad51bf5", "7f9afbe3dccf65514ba8dd5b61d6c24b5113c068655a05861fe1415ade374ee1", False),
    ("B2", "TWO_NODE_OPEN_LINE", "f194b32ba7c7de778f1dae7e69d0290db728152bb58db9c86a1a5b1552ddf8bb", "06f8e90d235e9676cbdca36863d63c4b1b8f4bda1f508c4110c0bcd5916d3b9d", False),
    ("B2", "THREE_NODE_OPEN_LINE", "87aaa945c26569e3bebdaf46cbcfc3818a01ba00dbaf0c100cc53787a9a6649f", "c835a011e26d20129f6a44f31f8147dd09f96686cd3427bbf89020ce23c59827", False),
    ("B3", "TWO_NODE_OPEN_LINE", "18e61bccd53473161d8dfc22878234d3ad0b64bb39340a2c909609542a555ab5", "18e61bccd53473161d8dfc22878234d3ad0b64bb39340a2c909609542a555ab5", True),
    ("B3", "THREE_NODE_OPEN_LINE", "811bed92599dea6277bb629442efa8ea9967ba5187ed284f57acc77abd69d4b0", "811bed92599dea6277bb629442efa8ea9967ba5187ed284f57acc77abd69d4b0", True),
    ("B4", "TWO_NODE_OPEN_LINE", "3919b9274f067ae67b1db96be68b075be21f7e799e2d714eea0f83c50df82466", "3919b9274f067ae67b1db96be68b075be21f7e799e2d714eea0f83c50df82466", True),
    ("B4", "THREE_NODE_OPEN_LINE", "6b83e11901795f68307888acc95c85b6160bd88726824edcbe79a2314ad795c3", "6b83e11901795f68307888acc95c85b6160bd88726824edcbe79a2314ad795c3", True),
    ("B5", "TWO_NODE_OPEN_LINE", "3472149b107835b6e692e7dfbd1a687017066c4d9ddb8aaa62968807f533cfda", "3472149b107835b6e692e7dfbd1a687017066c4d9ddb8aaa62968807f533cfda", True),
    ("B5", "THREE_NODE_OPEN_LINE", "900f9bf90895292a2ded9846ab5724173011458c2fbeda6c779a5c971418f12c", "900f9bf90895292a2ded9846ab5724173011458c2fbeda6c779a5c971418f12c", True),
    ("B6", "TWO_NODE_OPEN_LINE", "3df7f15511a1fa87c1333b3c1dd9e0c8b0b4973b609270845f7a77805266166b", "3df7f15511a1fa87c1333b3c1dd9e0c8b0b4973b609270845f7a77805266166b", True),
    ("B6", "THREE_NODE_OPEN_LINE", "7aeaa6bf958f6cdead18020f87d1539a88d4f697021df56587f14566f7965ac4", "7aeaa6bf958f6cdead18020f87d1539a88d4f697021df56587f14566f7965ac4", True),
)
S1_KA_FINDINGS = (
    "S1-JZ-digested-nested-B1-fixed-adapter-tuples-as-arrays-instead-of-the-runtime-canonical-mapping",
    "S1-JZ-digested-nested-B2-L-entry-tuples-without-the-runtime-node_id-and-value-object-shape",
    "both-B1-and-both-B2-geometry-records-fail-the-private-state-roundtrip-before-materialization",
    "all-eight-B3-through-B6-scalar-private-state-records-roundtrip-bit-identically",
    "the-bound-S1-KA-B1-two-node-exemplar-is-among-the-four-failing-records",
)
S1_KA_PRESERVED_BINDINGS = (
    "all-S1-JZ-runner-input-checkpoint-component-index-output-error-and-exemplar-records",
    "all-twelve-fresh-field-payloads-and-field-digests",
    "all-B1-rates-B2-zero-L-values-B3-through-B6-M-values-and-configuration-digests",
    "all-S1-JX-sequence-carry-replica-case-checkpoint-and-atomicity-rules",
    "all-S1-JW-adapter-implementation-and-geometry-digest-role-validation",
)
S1_KA_REQUIRED_CORRECTION = (
    "replace-only-the-nested-B1-fixed-adapter-and-B2-L-payload-representations-with-runtime-canonical-object-shapes",
    "recompute-only-the-four-dependent-private-state-digests-and-the-S1-JZ-contract-digest",
    "retain-the-eight-bit-identical-B3-through-B6-private-state-records",
    "rerun-all-twelve-static-roundtrips-before-authorizing-the-same-S1-KA-exemplar-again",
)
S1_KA_DECISION = (
    "STOPP_S1JZ_B1_B2_FRESH_PRIVATE_STATE_DIGESTS_DO_NOT_ROUNDTRIP"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1KAFreshPrivateDigestPrecheck:
    audit_id: str
    source_s1jz_digest: str
    digest_roundtrip_records: tuple[tuple[str, str, str, str, bool], ...]
    findings: tuple[str, ...]
    preserved_bindings: tuple[str, ...]
    required_correction: tuple[str, ...]
    record_count: int
    failing_record_count: int
    passing_record_count: int
    exemplar_record_passes: bool
    initializer_implemented: bool
    orchestrator_implemented: bool
    technical_replicas_executed: int
    baseline_interval_calls_executed: int
    profile_cases_executed: int
    runtime_integration_present: bool
    research_execution_permitted: bool
    corrected_fresh_state_contract_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {f.name: getattr(self, f.name) for f in fields(self) if f.name != "audit_digest"}
        if (
            self.audit_id != S1_KA_AUDIT_ID
            or self.source_s1jz_digest != S1_KA_SOURCE_S1JZ_DIGEST
            or self.digest_roundtrip_records != S1_KA_DIGEST_ROUNDTRIP_RECORDS
            or self.findings != S1_KA_FINDINGS
            or self.preserved_bindings != S1_KA_PRESERVED_BINDINGS
            or self.required_correction != S1_KA_REQUIRED_CORRECTION
            or self.record_count != 12
            or self.failing_record_count != 4
            or self.passing_record_count != 8
            or self.exemplar_record_passes is not False
            or self.initializer_implemented is not False
            or self.orchestrator_implemented is not False
            or self.technical_replicas_executed != 0
            or self.baseline_interval_calls_executed != 0
            or self.profile_cases_executed != 0
            or self.runtime_integration_present is not False
            or self.research_execution_permitted is not False
            or self.corrected_fresh_state_contract_authorized_next_stage is not True
            or self.decision != S1_KA_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1KAFreshPrivateDigestPrecheckError(
                "S1-KA weakened the fresh private-state digest stop"
            )


def build_dts1_s1ka_fresh_private_digest_precheck(
) -> DTS1S1KAFreshPrivateDigestPrecheck:
    """Audit twelve private digests without constructing or running a runner."""

    source = build_dts1_s1jz_finite_orchestrator_api_contract()
    values = {
        "audit_id": S1_KA_AUDIT_ID,
        "source_s1jz_digest": source.contract_digest,
        "digest_roundtrip_records": S1_KA_DIGEST_ROUNDTRIP_RECORDS,
        "findings": S1_KA_FINDINGS,
        "preserved_bindings": S1_KA_PRESERVED_BINDINGS,
        "required_correction": S1_KA_REQUIRED_CORRECTION,
        "record_count": len(S1_KA_DIGEST_ROUNDTRIP_RECORDS),
        "failing_record_count": sum(not row[4] for row in S1_KA_DIGEST_ROUNDTRIP_RECORDS),
        "passing_record_count": sum(row[4] for row in S1_KA_DIGEST_ROUNDTRIP_RECORDS),
        "exemplar_record_passes": False,
        "initializer_implemented": False,
        "orchestrator_implemented": False,
        "technical_replicas_executed": 0,
        "baseline_interval_calls_executed": 0,
        "profile_cases_executed": 0,
        "runtime_integration_present": False,
        "research_execution_permitted": False,
        "corrected_fresh_state_contract_authorized_next_stage": True,
        "decision": S1_KA_DECISION,
    }
    return DTS1S1KAFreshPrivateDigestPrecheck(
        **values, audit_digest=_digest(values)
    )
