"""Byte-bound S1-OM fixtures for pure G2/D3 target projection."""

from __future__ import annotations

import json
from typing import Any

from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex
from tests.g2_d3_s1nr_fixtures import D3_V_MIXED
from tests.g2_d3_s1oc_fixtures import OA_V_XX
from tests.g2_d3_s1oi_fixtures import (
    NEGATIVE_FIXTURES as OI_NEGATIVE_FIXTURES,
    NEGATIVE_INPUT_DIGESTS as OI_NEGATIVE_INPUT_DIGESTS,
    POSITIVE_FIXTURES as OI_POSITIVE_FIXTURES,
    POSITIVE_INPUT_DIGESTS as OI_POSITIVE_INPUT_DIGESTS,
)


def _bind_boundary(boundary_raw: bytes, d3_raw: bytes) -> bytes:
    boundary = json.loads(boundary_raw)
    source = json.loads(d3_raw)
    boundary["source_d3_anatomy_record_digest"] = source["anatomy_record_digest"]
    boundary["boundary_record_digest"] = sha256_hex(
        canonical_json_bytes(
            {key: value for key, value in boundary.items() if key != "boundary_record_digest"}
        )
    )
    return canonical_json_bytes(boundary)


def _build_second_target() -> bytes:
    target = json.loads(D3_V_MIXED)
    target["bound_unconfigured"] = 0.125
    target["bound_configured"] = 0.375
    target["resource_account_digest"] = sha256_hex(
        canonical_json_bytes(
            {
                key: target[key]
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
    target["aggregate_projection_digest"] = sha256_hex(
        canonical_json_bytes(
            {
                "edge_id": target["edge_id"],
                "capacity": target["capacity"],
                "free": target["free"],
                "bound": target["bound_unconfigured"] + target["bound_configured"],
                "blocked": target["blocked"],
            }
        )
    )
    target["anatomy_record_digest"] = sha256_hex(
        canonical_json_bytes(
            {key: value for key, value in target.items() if key != "anatomy_record_digest"}
        )
    )
    return canonical_json_bytes(target)


OL_V_MIXED_XX_BOUNDARY = _bind_boundary(OA_V_XX, D3_V_MIXED)
D3_OL_SECOND_TARGET = _build_second_target()

_NAME_MAP = {
    "OG_V_FIRST_X_ON": "OL_V_FIRST_X_ON",
    "OG_V_FIRST_Y_ON": "OL_V_FIRST_Y_ON",
    "OG_V_XX_ON": "OL_V_XX_ON",
    "OG_V_YY_ON": "OL_V_YY_ON",
    "OG_V_XY_ON": "OL_V_XY_ON",
    "OG_V_YX_ON": "OL_V_YX_ON",
    "OG_V_XX_OFF": "OL_V_XX_OFF",
    "OG_V_C1_XX_ON": "OL_V_C1_XX_ON",
    "OG_V_INTEGER_XY_ON": "OL_V_INTEGER_XY_ON",
}
POSITIVE_FIXTURES = {
    target_name: OI_POSITIVE_FIXTURES[source_name]
    for source_name, target_name in _NAME_MAP.items()
}
POSITIVE_FIXTURES["OL_V_MIXED_XX_ON"] = (OL_V_MIXED_XX_BOUNDARY, D3_V_MIXED, True)

POSITIVE_INPUT_DIGESTS = {
    target_name: OI_POSITIVE_INPUT_DIGESTS[source_name]
    for source_name, target_name in _NAME_MAP.items()
}
POSITIVE_INPUT_DIGESTS["OL_V_MIXED_XX_ON"] = (
    "5b1413f8041cb6d7c9552860affa75f2e74958b30b5bb00a6dfc2cc674f83087",
    "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
)

NEGATIVE_FIXTURES = dict(OI_NEGATIVE_FIXTURES)
NEGATIVE_INPUT_DIGESTS = dict(OI_NEGATIVE_INPUT_DIGESTS)

EXPECTED_TARGETS = {
    "OL_V_FIRST_X_ON": POSITIVE_FIXTURES["OL_V_FIRST_X_ON"][1],
    "OL_V_FIRST_Y_ON": POSITIVE_FIXTURES["OL_V_FIRST_Y_ON"][1],
    "OL_V_XX_ON": D3_V_MIXED,
    "OL_V_YY_ON": D3_V_MIXED,
    "OL_V_XY_ON": POSITIVE_FIXTURES["OL_V_XY_ON"][1],
    "OL_V_YX_ON": POSITIVE_FIXTURES["OL_V_YX_ON"][1],
    "OL_V_XX_OFF": POSITIVE_FIXTURES["OL_V_XX_OFF"][1],
    "OL_V_C1_XX_ON": POSITIVE_FIXTURES["OL_V_C1_XX_ON"][1],
    "OL_V_INTEGER_XY_ON": POSITIVE_FIXTURES["OL_V_INTEGER_XY_ON"][1],
    "OL_V_MIXED_XX_ON": D3_OL_SECOND_TARGET,
}

NULL_FIXTURE_NAMES = (
    "OL_V_FIRST_X_ON",
    "OL_V_FIRST_Y_ON",
    "OL_V_XY_ON",
    "OL_V_YX_ON",
    "OL_V_XX_OFF",
    "OL_V_C1_XX_ON",
    "OL_V_INTEGER_XY_ON",
)

BOUND_DIGESTS = {
    "mixed_boundary_record": "62003cc5144577d7c793051c01534348bc8be20e756bc1ab14d50199e17da79b",
    "first_target_resource": "75bee4f5732ed8c57c942c0e495b910c54097ef72ed1fb457740a4dd7045cd1c",
    "first_target_projection": "bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e",
    "first_target_record": "d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c",
    "first_target_input": "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
    "second_target_resource": "95568070519f29b65e34a4c06d681f150e81776b2bae4dfac60b132276df1f52",
    "second_target_projection": "bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e",
    "second_target_record": "efba6284b3e56cfe2041465eb8acc76b00de34ee8303f6a2caa20b2a3fc66681",
    "second_target_input": "a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab",
}


def fixture_input_digests(fixture: tuple[bytes, bytes, bool]) -> tuple[str, str]:
    boundary_raw, d3_raw, _ = fixture
    return sha256_hex(boundary_raw), sha256_hex(d3_raw)


def record(raw: bytes) -> dict[str, Any]:
    return json.loads(raw)
