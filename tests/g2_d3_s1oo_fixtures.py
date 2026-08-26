"""Byte-bound S1-OO fixtures for pure atomic G2/D3 commit selection."""

from __future__ import annotations

from mcm_field_organism.kfs1_schema_validator import sha256_hex
from tests.g2_d3_s1nr_fixtures import D3_V_C1, SINGLE_MUTATIONS
from tests.g2_d3_s1om_fixtures import (
    EXPECTED_TARGETS,
    NEGATIVE_FIXTURES as PROJECTION_NEGATIVE_FIXTURES,
    POSITIVE_FIXTURES as PROJECTION_POSITIVE_FIXTURES,
)


def _copy(raw: bytes) -> bytes:
    return bytes(bytearray(raw))


def _commit_fixture(projection_name: str) -> tuple[bytes, bytes, bytes, bytes, bool]:
    boundary, source, enabled = PROJECTION_POSITIVE_FIXTURES[projection_name]
    return boundary, source, _copy(source), _copy(EXPECTED_TARGETS[projection_name]), enabled


VALID_FIXTURES = {
    "ON_V_NO_CHANGE_FIRST_X": _commit_fixture("OL_V_FIRST_X_ON"),
    "ON_V_NO_CHANGE_XY": _commit_fixture("OL_V_XY_ON"),
    "ON_V_PROJECTED_XX": _commit_fixture("OL_V_XX_ON"),
    "ON_V_PROJECTED_YY": _commit_fixture("OL_V_YY_ON"),
    "ON_V_PROJECTED_SECOND": _commit_fixture("OL_V_MIXED_XX_ON"),
}

_RECOMPUTE_NAME_MAP = {
    "OG_I_SOURCE": "ON_I_RECOMPUTE_SOURCE",
    "OG_I_NUMERIC_DOMAIN": "ON_I_RECOMPUTE_NUMERIC_DOMAIN",
    "OG_I_HALVING_INVARIANT": "ON_I_RECOMPUTE_HALVING_INVARIANT",
    "OG_I_TARGET_REPRESENTATION": "ON_I_RECOMPUTE_TARGET_REPRESENTATION",
    "OG_I_EXACT_LEDGER": "ON_I_RECOMPUTE_EXACT_LEDGER",
}
RECOMPUTE_FAILURE_FIXTURES = {}
for source_name, target_name in _RECOMPUTE_NAME_MAP.items():
    boundary, source, enabled = PROJECTION_NEGATIVE_FIXTURES[source_name]
    RECOMPUTE_FAILURE_FIXTURES[target_name] = (
        boundary,
        source,
        _copy(source),
        _copy(source),
        enabled,
    )

_xx_boundary, _c0_source, _enabled = PROJECTION_POSITIVE_FIXTURES["OL_V_XX_ON"]
_mixed_target = EXPECTED_TARGETS["OL_V_XX_ON"]
_invalid_record = SINGLE_MUTATIONS["D3_I_RECORD_DIGEST"]

COMMIT_FAILURE_FIXTURES = {
    "ON_I_PROPOSED_INVALID": (
        _xx_boundary, _c0_source, _copy(_c0_source), _copy(_invalid_record), _enabled
    ),
    "ON_I_PROPOSED_MISMATCH": (
        _xx_boundary, _c0_source, _copy(_c0_source), _copy(D3_V_C1), _enabled
    ),
    "ON_I_CURRENT_INVALID": (
        _xx_boundary, _c0_source, _copy(_invalid_record), _copy(_mixed_target), _enabled
    ),
    "ON_I_STALE_SOURCE": (
        _xx_boundary, _c0_source, _copy(_mixed_target), _copy(_mixed_target), _enabled
    ),
}

ALL_FIXTURES = {
    **VALID_FIXTURES,
    **RECOMPUTE_FAILURE_FIXTURES,
    **COMMIT_FAILURE_FIXTURES,
}

INPUT_DIGESTS = {
    "ON_V_NO_CHANGE_FIRST_X": (
        "bc6ce8c49458bc27da0a7872680c7f8e78890acd316831d921cc82e3a1f6b228",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
    "ON_V_NO_CHANGE_XY": (
        "d9db45ac53bcbddda68555ff398e7ea0f8f45f33979e84a7208d07fca965d1d0",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
    "ON_V_PROJECTED_XX": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
    ),
    "ON_V_PROJECTED_YY": (
        "2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
    ),
    "ON_V_PROJECTED_SECOND": (
        "5b1413f8041cb6d7c9552860affa75f2e74958b30b5bb00a6dfc2cc674f83087",
        "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
        "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
        "a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab",
    ),
    "ON_I_RECOMPUTE_SOURCE": (
        "2ef258e62980c27b31f36d271615d2e8c8323aa12e5f4e0d5f0c7254b7d99493",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    ),
    "ON_I_RECOMPUTE_NUMERIC_DOMAIN": (
        "ce44be3f2eb046307a0012fb4a6a296af177ea93f1362ee314d5d409d667aa6e",
        "9749ac0c341b85fbe318e6f084261d96da68cf13475cbc6dda51fb0b22e5518e",
        "9749ac0c341b85fbe318e6f084261d96da68cf13475cbc6dda51fb0b22e5518e",
        "9749ac0c341b85fbe318e6f084261d96da68cf13475cbc6dda51fb0b22e5518e",
    ),
    "ON_I_RECOMPUTE_HALVING_INVARIANT": (
        "0eb3b2814108033dfbd5e409ce98866fca36f7cea68696bec41101e92c65e680",
        "3dbd6182676d5c65b6e375cab90728a1860daadc318a358d5e1dd45ab023f558",
        "3dbd6182676d5c65b6e375cab90728a1860daadc318a358d5e1dd45ab023f558",
        "3dbd6182676d5c65b6e375cab90728a1860daadc318a358d5e1dd45ab023f558",
    ),
    "ON_I_RECOMPUTE_TARGET_REPRESENTATION": (
        "81039d1ddc544751bd014d89c2541e826ac7c17909283ebec3f0f0cdfc846700",
        "d73b67ce9d9d77b7a3bdce43a4852c892212e048c976b5f1b8b606b08d887d68",
        "d73b67ce9d9d77b7a3bdce43a4852c892212e048c976b5f1b8b606b08d887d68",
        "d73b67ce9d9d77b7a3bdce43a4852c892212e048c976b5f1b8b606b08d887d68",
    ),
    "ON_I_RECOMPUTE_EXACT_LEDGER": (
        "59fba0f0361e248b1af1699eaed8a6fedc8c7fdb257f89fac343d5f05306f552",
        "2d29818b7dac97a7a20d45ef39134f23170911ea1e3caf3b859d2626c71bd5ab",
        "2d29818b7dac97a7a20d45ef39134f23170911ea1e3caf3b859d2626c71bd5ab",
        "2d29818b7dac97a7a20d45ef39134f23170911ea1e3caf3b859d2626c71bd5ab",
    ),
    "ON_I_PROPOSED_INVALID": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "1e101961c98475ef1015c85f5eb68de4ef101b977b5db435294a6e822c931a9f",
    ),
    "ON_I_PROPOSED_MISMATCH": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "058ae964682a9750a316d1db1b2e155714c18bc5adab9eb71fbc6e85e3be54b5",
    ),
    "ON_I_CURRENT_INVALID": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "1e101961c98475ef1015c85f5eb68de4ef101b977b5db435294a6e822c931a9f",
        "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
    ),
    "ON_I_STALE_SOURCE": (
        "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
        "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
        "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
    ),
}


def fixture_input_digests(
    fixture: tuple[bytes, bytes, bytes, bytes, bool],
) -> tuple[str, str, str, str]:
    boundary, source, current, proposed, _ = fixture
    return tuple(sha256_hex(raw) for raw in (boundary, source, current, proposed))
