"""Byte-bound S1-OI fixtures for the passive halving amount evaluator."""

from __future__ import annotations

import json
from typing import Any

from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1nr_fixtures import D3_V_C0, D3_V_C1
from tests.g2_d3_s1oc_fixtures import (
    NEGATIVE_FIXTURES as OA_NEGATIVE_FIXTURES,
    OA_V_FIRST_X,
    OA_V_FIRST_Y,
    OA_V_XX,
    OA_V_XY,
    OA_V_YX,
    OA_V_YY,
)


def _build_d3(
    capacity: int | float,
    free: int | float,
    bound_unconfigured: int | float,
    bound_configured: int | float,
    blocked: int | float,
) -> bytes:
    record = json.loads(D3_V_C0)
    record.update(
        capacity=capacity,
        free=free,
        bound_unconfigured=bound_unconfigured,
        bound_configured=bound_configured,
        blocked=blocked,
    )
    record["resource_account_digest"] = sha256_hex(
        canonical_json_bytes(
            {
                key: record[key]
                for key in (
                    "edge_id",
                    "capacity",
                    "free",
                    "bound_unconfigured",
                    "bound_configured",
                    "blocked",
                )
            }
        )
    )
    record["aggregate_projection_digest"] = sha256_hex(
        canonical_json_bytes(
            {
                "edge_id": record["edge_id"],
                "capacity": capacity,
                "free": free,
                "bound": bound_unconfigured + bound_configured,
                "blocked": blocked,
            }
        )
    )
    record["anatomy_record_digest"] = sha256_hex(
        canonical_json_bytes(
            {key: value for key, value in record.items() if key != "anatomy_record_digest"}
        )
    )
    return canonical_json_bytes(record)


def _bind_boundary(boundary_raw: bytes, d3_raw: bytes) -> bytes:
    boundary = json.loads(boundary_raw)
    d3_record = json.loads(d3_raw)
    boundary["source_d3_anatomy_record_digest"] = d3_record["anatomy_record_digest"]
    boundary["boundary_record_digest"] = sha256_hex(
        canonical_json_bytes(
            {key: value for key, value in boundary.items() if key != "boundary_record_digest"}
        )
    )
    return canonical_json_bytes(boundary)


D3_OG_INTEGER = _build_d3(2, 1, 1, 0, 0)
D3_OG_MIN_SUBNORMAL = _build_d3(1.0, 1.0, 5e-324, 0.0, 0.0)
D3_OG_TARGET_ROUND = _build_d3(1.0, 0.5, 2.0**-54, 0.5, 0.0)
D3_OG_LEDGER_RATIONAL = _build_d3(1.0, 1.0, 2.0**-53, 0.0, 0.0)

OG_V_C1_XX_BOUNDARY = _bind_boundary(OA_V_XX, D3_V_C1)
OG_V_INTEGER_XY_BOUNDARY = _bind_boundary(OA_V_XY, D3_OG_INTEGER)

POSITIVE_FIXTURES = {
    "OG_V_FIRST_X_ON": (OA_V_FIRST_X, D3_V_C0, True),
    "OG_V_FIRST_Y_ON": (OA_V_FIRST_Y, D3_V_C0, True),
    "OG_V_XX_ON": (OA_V_XX, D3_V_C0, True),
    "OG_V_YY_ON": (OA_V_YY, D3_V_C0, True),
    "OG_V_XY_ON": (OA_V_XY, D3_V_C0, True),
    "OG_V_YX_ON": (OA_V_YX, D3_V_C0, True),
    "OG_V_XX_OFF": (OA_V_XX, D3_V_C0, False),
    "OG_V_C1_XX_ON": (OG_V_C1_XX_BOUNDARY, D3_V_C1, True),
    "OG_V_INTEGER_XY_ON": (OG_V_INTEGER_XY_BOUNDARY, D3_OG_INTEGER, True),
}
POSITIVE_EXPECTED = {
    "OG_V_FIRST_X_ON": ("NO_PREDECESSOR", 0.0),
    "OG_V_FIRST_Y_ON": ("NO_PREDECESSOR", 0.0),
    "OG_V_XX_ON": ("LOCAL_CONTINUATION", 0.25),
    "OG_V_YY_ON": ("LOCAL_CONTINUATION", 0.25),
    "OG_V_XY_ON": ("LOCAL_SWITCH", 0.0),
    "OG_V_YX_ON": ("LOCAL_SWITCH", 0.0),
    "OG_V_XX_OFF": ("LOCAL_CONTINUATION", 0.0),
    "OG_V_C1_XX_ON": ("LOCAL_CONTINUATION", 0.0),
    "OG_V_INTEGER_XY_ON": ("LOCAL_SWITCH", 0.0),
}

POSITIVE_INPUT_DIGESTS = {
    "OG_V_FIRST_X_ON": ("bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228", "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7"),
    "OG_V_FIRST_Y_ON": ("3da5f86db0772fb339b25c6e916bf0a13dfde6f5e144a8e48cb7eea62cc43769", "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7"),
    "OG_V_XX_ON": ("c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c", "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7"),
    "OG_V_YY_ON": ("2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b", "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7"),
    "OG_V_XY_ON": ("d9db45ac53bcbddda68555ff398e7ea0f8f45f33979e84a7208d07fca965d1d0", "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7"),
    "OG_V_YX_ON": ("68a94dc17f18afb4418e0d79f54f9a148d2c4eb8d9ced0f7607f372d9c2ff63e", "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7"),
    "OG_V_XX_OFF": ("c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c", "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7"),
    "OG_V_C1_XX_ON": ("a462d90c805e87d1f64d423260864f476640df12f5ff922c6350653967c61962", "058ae964682a9750a316d1db1b2e155714c18bc5adab9eb71fbc6e85e3be54b5"),
    "OG_V_INTEGER_XY_ON": ("1a2ec59aa7d2b0f50eb1d3727219f37c4c785246cdfe841a43649a1c4d209de7", "9749ac0c341b85fbe318e6f084261d96da68cf13475cbc6dda51fb0b22e5518e"),
}

NEGATIVE_FIXTURES = {
    "OG_I_SOURCE": (*OA_NEGATIVE_FIXTURES["OA_I_VERSION"], True),
    "OG_I_NUMERIC_DOMAIN": (_bind_boundary(OA_V_XX, D3_OG_INTEGER), D3_OG_INTEGER, True),
    "OG_I_HALVING_INVARIANT": (_bind_boundary(OA_V_XX, D3_OG_MIN_SUBNORMAL), D3_OG_MIN_SUBNORMAL, True),
    "OG_I_TARGET_REPRESENTATION": (_bind_boundary(OA_V_XX, D3_OG_TARGET_ROUND), D3_OG_TARGET_ROUND, True),
    "OG_I_EXACT_LEDGER": (_bind_boundary(OA_V_XX, D3_OG_LEDGER_RATIONAL), D3_OG_LEDGER_RATIONAL, True),
}
NEGATIVE_EXPECTED = {
    "OG_I_SOURCE": ("OG_SOURCE_BOUNDARY_VALIDATION_FAILED",),
    "OG_I_NUMERIC_DOMAIN": ("OG_NUMERIC_DOMAIN_MISMATCH",),
    "OG_I_HALVING_INVARIANT": ("OG_HALVING_INVARIANT_MISMATCH",),
    "OG_I_TARGET_REPRESENTATION": ("OG_TARGET_REPRESENTATION_MISMATCH",),
    "OG_I_EXACT_LEDGER": ("OG_EXACT_LEDGER_IDENTITY_MISMATCH",),
}
NEGATIVE_INPUT_DIGESTS = {
    "OG_I_SOURCE": ("2ef258e62980c27b31f36d271615d2e8c8323aa12e5f4e0d5f0c7254b7d99493", "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7"),
    "OG_I_NUMERIC_DOMAIN": ("ce44be3f2eb046307a0012fb4a6a296af177ea93f1362ee314d5d409d667aa6e", "9749ac0c341b85fbe318e6f084261d96da68cf13475cbc6dda51fb0b22e5518e"),
    "OG_I_HALVING_INVARIANT": ("0eb3b2814108033dfbd5e409ce98866fca36f7cea68696bec41101e92c65e680", "3dbd6182676d5c65b6e375cab90728a1860daadc318a358d5e1dd45ab023f558"),
    "OG_I_TARGET_REPRESENTATION": ("81039d1ddc544751bd014d89c2541e826ac7c17909283ebec3f0f0cdfc846700", "d73b67ce9d9d77b7a3bdce43a4852c892212e048c976b5f1b8b606b08d887d68"),
    "OG_I_EXACT_LEDGER": ("59fba0f0361e248b1af1699eaed8a6fedc8c7fdb257f89fac343d5f05306f552", "2d29818b7dac97a7a20d45ef39134f23170911ea1e3caf3b859d2626c71bd5ab"),
}


def fixture_input_digests(fixture: tuple[bytes, bytes, bool]) -> tuple[str, str]:
    boundary_raw, d3_raw, _ = fixture
    return sha256_hex(boundary_raw), sha256_hex(d3_raw)


def record_digest(raw: bytes, key: str) -> str:
    value: dict[str, Any] = json.loads(raw)
    return value[key]
