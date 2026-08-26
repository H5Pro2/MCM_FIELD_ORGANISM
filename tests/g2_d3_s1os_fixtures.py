"""Byte-bound S1-OS fixtures for pure two-step G2/D3 composition."""

from __future__ import annotations

import json

from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1nr_fixtures import D3_V_C0, D3_V_MIXED
from tests.g2_d3_s1oc_fixtures import OA_V_XX, OA_V_XY, OA_V_YY, build_boundary
from tests.g2_d3_s1om_fixtures import D3_OL_SECOND_TARGET


def _bind_source(boundary_raw: bytes, source_raw: bytes) -> bytes:
    boundary = json.loads(boundary_raw)
    source = json.loads(source_raw)
    boundary["source_d3_anatomy_record_digest"] = source["anatomy_record_digest"]
    boundary["boundary_record_digest"] = sha256_hex(
        canonical_json_bytes(
            {key: value for key, value in boundary.items() if key != "boundary_record_digest"}
        )
    )
    return canonical_json_bytes(boundary)


SECOND_X = _bind_source(build_boundary("X", 2, "X"), D3_V_MIXED)
SECOND_Y = _bind_source(build_boundary("Y", 2, "Y"), D3_V_MIXED)
SECOND_X_SOURCE_C0 = _bind_source(build_boundary("X", 2, "X"), D3_V_C0)
SECOND_X_RESET = _bind_source(build_boundary("X", 1, "X"), D3_V_MIXED)

_invalid = json.loads(SECOND_X)
_invalid["schema_version"] = "s1oa.v2"
SECOND_X_INVALID = canonical_json_bytes(_invalid)

VALID_FIXTURES = {
    "OR_V_XXX": (OA_V_XX, SECOND_X, D3_V_C0, True),
    "OR_V_YYY": (OA_V_YY, SECOND_Y, D3_V_C0, True),
}

INVALID_FIXTURES = {
    "OR_I_UNKNOWN_FIRST": (OA_V_XY, SECOND_X, D3_V_C0, True),
    "OR_I_UNKNOWN_INITIAL": (OA_V_XX, SECOND_X, D3_V_MIXED, True),
    "OR_I_FORMATION_DISABLED": (OA_V_XX, SECOND_X, D3_V_C0, False),
    "OR_I_SECOND_INVALID": (OA_V_XX, SECOND_X_INVALID, D3_V_C0, True),
    "OR_I_SECOND_SOURCE_C0": (OA_V_XX, SECOND_X_SOURCE_C0, D3_V_C0, True),
    "OR_I_SECOND_CONTACT_CROSS": (OA_V_XX, SECOND_Y, D3_V_C0, True),
    "OR_I_SECOND_CONTACT_RESET": (OA_V_XX, SECOND_X_RESET, D3_V_C0, True),
}

EXPECTED_FAILURES = {
    "OR_I_UNKNOWN_FIRST": "OQ_UNKNOWN_CHAIN_BINDING",
    "OR_I_UNKNOWN_INITIAL": "OQ_UNKNOWN_CHAIN_BINDING",
    "OR_I_FORMATION_DISABLED": "OQ_FORMATION_DISABLED",
    "OR_I_SECOND_INVALID": "OQ_SECOND_BOUNDARY_INVALID",
    "OR_I_SECOND_SOURCE_C0": "OQ_SECOND_SOURCE_BINDING_MISMATCH",
    "OR_I_SECOND_CONTACT_CROSS": "OQ_SECOND_CONTACT_LINK_MISMATCH",
    "OR_I_SECOND_CONTACT_RESET": "OQ_SECOND_CONTACT_LINK_MISMATCH",
}

ALL_FIXTURES = {**VALID_FIXTURES, **INVALID_FIXTURES}

INPUT_DIGESTS = {
    "OR_V_XXX": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
    "OR_V_YYY": (
        "2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b",
        "dc772636ed23e9cf9a904fd9943a7a1bcfacafe08aed9e60a65ac93f3d266d32",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
    "OR_I_UNKNOWN_FIRST": (
        "d9db45ac53bcbddda68555ff398e7ea0f8f45f33979e84a7208d07fca965d1d0",
        "6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
    "OR_I_UNKNOWN_INITIAL": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a",
        "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
    ),
    "OR_I_FORMATION_DISABLED": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
    "OR_I_SECOND_INVALID": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "5a4f299e8737d118c747fcd4246a2c94f6a610b7a37aeed600241f90e7496b16",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
    "OR_I_SECOND_SOURCE_C0": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "b2d417714d168a73291be743752be7586e32e2b0c67a9f7b96c6708a3ae7b82c",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
    "OR_I_SECOND_CONTACT_CROSS": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "dc772636ed23e9cf9a904fd9943a7a1bcfacafe08aed9e60a65ac93f3d266d32",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
    "OR_I_SECOND_CONTACT_RESET": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "5b1413f8041cb6d7c9552860affa75f2e74958b30b5bb00a6dfc2cc674f83087",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
}

DEFENSIVE_CODES = (
    "OQ_FIRST_PROJECTION_FAILED",
    "OQ_FIRST_COMMIT_FAILED",
    "OQ_INTERMEDIATE_IDENTITY_MISMATCH",
    "OQ_SECOND_PROJECTION_FAILED",
    "OQ_SECOND_COMMIT_FAILED",
    "OQ_FINAL_IDENTITY_MISMATCH",
)


def fixture_input_digests(
    fixture: tuple[bytes, bytes, bytes, bool],
) -> tuple[str, str, str]:
    first, second, initial, _ = fixture
    return sha256_hex(first), sha256_hex(second), sha256_hex(initial)
