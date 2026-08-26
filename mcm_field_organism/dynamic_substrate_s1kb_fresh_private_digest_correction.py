"""Static S1-KB correction audit for all fresh private-state digests."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json

from .dynamic_substrate_dts1_common_interval_materializer import (
    DTS1CommonIntervalPrivateState,
)
from .dynamic_substrate_s1jz_finite_orchestrator_api_contract import (
    build_dts1_s1jz_finite_orchestrator_api_contract,
)


class DTS1S1KBFreshPrivateDigestCorrectionError(ValueError):
    """Raised when the finite S1-KB correction is weakened."""


S1_KB_CORRECTION_ID = "dynamic-substrate.fresh-private-digest-correction.s1kb.v1"
S1_KB_SOURCE_S1KA_DIGEST = (
    "8e7a7ed21b6d5528ca152257e8ee550fdf8af12d42fd542893859a7735134a09"
)
S1_KB_CORRECTED_S1JZ_DIGEST = (
    "83a5c6248d0dca0e0ba2461bbc6c0f76470a5af1b21ac89049238f1256380079"
)
S1_KB_CORRECTED_PRIVATE_DIGESTS = (
    (
        "B1",
        "TWO_NODE_OPEN_LINE",
        "7edb70af4e533062167bf314106cbb930c5bd15fc6883468937744145ba1084e",
        "871b0308bfebdcc03a27ff0447f46e054aedc253f1a0975bd77bfbb69b3668d9",
    ),
    (
        "B1",
        "THREE_NODE_OPEN_LINE",
        "979bbb78c7ae85ea37a37a23e80c5db34b1d989a091e94fb1334ecd90ad51bf5",
        "7f9afbe3dccf65514ba8dd5b61d6c24b5113c068655a05861fe1415ade374ee1",
    ),
    (
        "B2",
        "TWO_NODE_OPEN_LINE",
        "f194b32ba7c7de778f1dae7e69d0290db728152bb58db9c86a1a5b1552ddf8bb",
        "06f8e90d235e9676cbdca36863d63c4b1b8f4bda1f508c4110c0bcd5916d3b9d",
    ),
    (
        "B2",
        "THREE_NODE_OPEN_LINE",
        "87aaa945c26569e3bebdaf46cbcfc3818a01ba00dbaf0c100cc53787a9a6649f",
        "c835a011e26d20129f6a44f31f8147dd09f96686cd3427bbf89020ce23c59827",
    ),
)
S1_KB_PRESERVED_PRIVATE_DIGESTS = (
    ("B3", "TWO_NODE_OPEN_LINE", "18e61bccd53473161d8dfc22878234d3ad0b64bb39340a2c909609542a555ab5"),
    ("B3", "THREE_NODE_OPEN_LINE", "811bed92599dea6277bb629442efa8ea9967ba5187ed284f57acc77abd69d4b0"),
    ("B4", "TWO_NODE_OPEN_LINE", "3919b9274f067ae67b1db96be68b075be21f7e799e2d714eea0f83c50df82466"),
    ("B4", "THREE_NODE_OPEN_LINE", "6b83e11901795f68307888acc95c85b6160bd88726824edcbe79a2314ad795c3"),
    ("B5", "TWO_NODE_OPEN_LINE", "3472149b107835b6e692e7dfbd1a687017066c4d9ddb8aaa62968807f533cfda"),
    ("B5", "THREE_NODE_OPEN_LINE", "900f9bf90895292a2ded9846ab5724173011458c2fbeda6c779a5c971418f12c"),
    ("B6", "TWO_NODE_OPEN_LINE", "3df7f15511a1fa87c1333b3c1dd9e0c8b0b4973b609270845f7a77805266166b"),
    ("B6", "THREE_NODE_OPEN_LINE", "7aeaa6bf958f6cdead18020f87d1539a88d4f697021df56587f14566f7965ac4"),
)
S1_KB_EXPECTED_PRIVATE_DIGESTS = tuple(
    (role, geometry, new_digest)
    for role, geometry, _old_digest, new_digest in S1_KB_CORRECTED_PRIVATE_DIGESTS
) + S1_KB_PRESERVED_PRIVATE_DIGESTS
S1_KB_DECISION = (
    "B1_B2_CANONICAL_PRIVATE_PAYLOADS_AND_FOUR_DIGESTS_CORRECTED_ALL_TWELVE_ROUNDTRIPS_PASS"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class DTS1S1KBFreshPrivateDigestCorrection:
    correction_id: str
    source_s1ka_digest: str
    corrected_s1jz_digest: str
    corrected_private_digests: tuple[tuple[str, str, str, str], ...]
    preserved_private_digests: tuple[tuple[str, str, str], ...]
    roundtrip_records: tuple[tuple[str, str, str, str, bool], ...]
    roundtrip_count: int
    passing_roundtrip_count: int
    failing_roundtrip_count: int
    corrected_record_count: int
    preserved_record_count: int
    initializer_implemented: bool
    orchestrator_implemented: bool
    materializer_calls_executed: int
    adapter_calls_executed: int
    interval_calls_executed: int
    profile_cases_executed: int
    same_exemplar_authorized_next_stage: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name != "audit_digest"
        }
        stored_roundtrips = tuple(
            (role, geometry, stored_digest)
            for role, geometry, stored_digest, _runtime_digest, _passes in self.roundtrip_records
        )
        runtime_roundtrips = tuple(
            (role, geometry, runtime_digest)
            for role, geometry, _stored_digest, runtime_digest, _passes in self.roundtrip_records
        )
        if (
            self.correction_id != S1_KB_CORRECTION_ID
            or self.source_s1ka_digest != S1_KB_SOURCE_S1KA_DIGEST
            or self.corrected_s1jz_digest != S1_KB_CORRECTED_S1JZ_DIGEST
            or self.corrected_private_digests != S1_KB_CORRECTED_PRIVATE_DIGESTS
            or self.preserved_private_digests != S1_KB_PRESERVED_PRIVATE_DIGESTS
            or stored_roundtrips != S1_KB_EXPECTED_PRIVATE_DIGESTS
            or runtime_roundtrips != S1_KB_EXPECTED_PRIVATE_DIGESTS
            or not all(row[4] is True for row in self.roundtrip_records)
            or self.roundtrip_count != 12
            or self.passing_roundtrip_count != 12
            or self.failing_roundtrip_count != 0
            or self.corrected_record_count != 4
            or self.preserved_record_count != 8
            or self.initializer_implemented is not False
            or self.orchestrator_implemented is not False
            or self.materializer_calls_executed != 0
            or self.adapter_calls_executed != 0
            or self.interval_calls_executed != 0
            or self.profile_cases_executed != 0
            or self.same_exemplar_authorized_next_stage is not True
            or self.decision != S1_KB_DECISION
            or self.audit_digest != _digest(payload)
        ):
            raise DTS1S1KBFreshPrivateDigestCorrectionError(
                "S1-KB weakened the finite digest correction"
            )


def build_dts1_s1kb_fresh_private_digest_correction(
) -> DTS1S1KBFreshPrivateDigestCorrection:
    """Verify twelve private-state roundtrips without field execution."""

    contract = build_dts1_s1jz_finite_orchestrator_api_contract()
    if contract.contract_digest != S1_KB_CORRECTED_S1JZ_DIGEST:
        raise DTS1S1KBFreshPrivateDigestCorrectionError(
            "corrected S1-JZ digest differs"
        )
    roundtrips = []
    for row in contract.fresh_state_records:
        state = DTS1CommonIntervalPrivateState(row[0], row[7])
        runtime_digest = _digest(state.canonical_payload())
        roundtrips.append((row[0], row[1], row[8], runtime_digest, row[8] == runtime_digest))
    roundtrip_records = tuple(roundtrips)
    values = {
        "correction_id": S1_KB_CORRECTION_ID,
        "source_s1ka_digest": S1_KB_SOURCE_S1KA_DIGEST,
        "corrected_s1jz_digest": contract.contract_digest,
        "corrected_private_digests": S1_KB_CORRECTED_PRIVATE_DIGESTS,
        "preserved_private_digests": S1_KB_PRESERVED_PRIVATE_DIGESTS,
        "roundtrip_records": roundtrip_records,
        "roundtrip_count": len(roundtrip_records),
        "passing_roundtrip_count": sum(row[4] for row in roundtrip_records),
        "failing_roundtrip_count": sum(not row[4] for row in roundtrip_records),
        "corrected_record_count": len(S1_KB_CORRECTED_PRIVATE_DIGESTS),
        "preserved_record_count": len(S1_KB_PRESERVED_PRIVATE_DIGESTS),
        "initializer_implemented": False,
        "orchestrator_implemented": False,
        "materializer_calls_executed": 0,
        "adapter_calls_executed": 0,
        "interval_calls_executed": 0,
        "profile_cases_executed": 0,
        "same_exemplar_authorized_next_stage": True,
        "decision": S1_KB_DECISION,
    }
    return DTS1S1KBFreshPrivateDigestCorrection(
        **values, audit_digest=_digest(values)
    )
