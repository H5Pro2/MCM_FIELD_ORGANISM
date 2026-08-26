"""Byte-bound S1-NR fixtures and their single controlled mutations."""

from __future__ import annotations

import json

from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes


def _record(
    *,
    edge_id: str,
    carrier_a_id: str,
    carrier_b_id: str,
    geometry_digest: str,
    free: float,
    bound_unconfigured: float,
    bound_configured: float,
    blocked: float,
    resource_digest: str,
    projection_digest: str,
    record_digest: str,
) -> bytes:
    return canonical_json_bytes(
        {
            "aggregate_projection_digest": projection_digest,
            "anatomy_record_digest": record_digest,
            "blocked": blocked,
            "bound_configured": bound_configured,
            "bound_unconfigured": bound_unconfigured,
            "candidate_class_id": "G2_CONSERVATIVE_BOUND_SUBPARTITION",
            "capacity": 1.0,
            "carrier_a_id": carrier_a_id,
            "carrier_b_id": carrier_b_id,
            "edge_id": edge_id,
            "field_reference_digest": "8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835",
            "free": free,
            "geometry_digest": geometry_digest,
            "resource_account_digest": resource_digest,
            "schema_id": "g2_d3_anatomy_record",
            "schema_version": "s1np.v1",
        }
    )


_PRIMARY_GEOMETRY = "26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651"
_PROJECTION = "bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e"

D3_V_C0 = _record(
    edge_id="edge:carrier-a:carrier-b", carrier_a_id="carrier-a", carrier_b_id="carrier-b",
    geometry_digest=_PRIMARY_GEOMETRY, free=0.5, bound_unconfigured=0.5,
    bound_configured=0.0, blocked=0.0,
    resource_digest="3421bacb4167e15f864c53b5fa9e2c15969a485906ebc5e1a47f24d3fd93994c",
    projection_digest=_PROJECTION,
    record_digest="1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f",
)
D3_V_C1 = _record(
    edge_id="edge:carrier-a:carrier-b", carrier_a_id="carrier-a", carrier_b_id="carrier-b",
    geometry_digest=_PRIMARY_GEOMETRY, free=0.5, bound_unconfigured=0.0,
    bound_configured=0.5, blocked=0.0,
    resource_digest="4abb521d1b2e0dbf93938493033e75f3c0da73643ec90bf3808f28d0241b017b",
    projection_digest=_PROJECTION,
    record_digest="3cf515292d1a8591ce1fdecf6f510dfc79cdf72d0fa64dcd965dca41859c3e8c",
)
D3_V_MIXED = _record(
    edge_id="edge:carrier-a:carrier-b", carrier_a_id="carrier-a", carrier_b_id="carrier-b",
    geometry_digest=_PRIMARY_GEOMETRY, free=0.5, bound_unconfigured=0.25,
    bound_configured=0.25, blocked=0.0,
    resource_digest="75bee4f5732ed8c57c942c0e495b910c54097ef72ed1fb457740a4dd7045cd1c",
    projection_digest=_PROJECTION,
    record_digest="d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c",
)
D3_V_C1_IDENTITY_CONTROL = _record(
    edge_id="edge:carrier-c:carrier-d", carrier_a_id="carrier-c", carrier_b_id="carrier-d",
    geometry_digest="75e06f6602eeb02fe90bd5aa72b1c67103a6bc4f0c7b2136611f4ef4945fa2f1",
    free=0.5, bound_unconfigured=0.0, bound_configured=0.5, blocked=0.0,
    resource_digest="441d304e5c5f166b9abe036be04e4e82c2a95f8d0d504a1807cd00dedbdbaa08",
    projection_digest="9ae4547347667b0a8b8ae97708778d4211dd6548b1c58074aab8070c835cdcab",
    record_digest="1df1ef9eb25362084aa13e1d5f65a5270e6ea8d72175feea64b9d9b7ec0dccdb",
)
D3_V_C1_AGGREGATE_CONTROL = _record(
    edge_id="edge:carrier-a:carrier-b", carrier_a_id="carrier-a", carrier_b_id="carrier-b",
    geometry_digest=_PRIMARY_GEOMETRY, free=0.25, bound_unconfigured=0.0,
    bound_configured=0.75, blocked=0.0,
    resource_digest="ff7c51e0909ac99d88940246117b10b87df0a097bba27dd326b1b41d3aa2dcb4",
    projection_digest="82b2360b2b19e75263df1d796fbc65df5fd705b55eb7963615911aa3f5071016",
    record_digest="1e0eda146f07f281bccf408f73f1d6b7cbef52d7f2779700025591c6c73597c7",
)


def _mutate(**changes: object) -> bytes:
    value = json.loads(D3_V_C0)
    value.update(changes)
    return canonical_json_bytes(value)


def _remove(key: str) -> bytes:
    value = json.loads(D3_V_C0)
    del value[key]
    return canonical_json_bytes(value)


ZERO_DIGEST = "0" * 64
SINGLE_MUTATIONS = {
    "D3_I_VERSION": _mutate(schema_version="s1np.v2"),
    "D3_I_MISSING": _remove("candidate_class_id"),
    "D3_I_EXTRA": _mutate(unknown_field=True),
    "D3_I_FORBIDDEN": _mutate(raw_data=[]),
    "D3_I_SERIALIZATION": json.dumps(json.loads(D3_V_C0), indent=2, sort_keys=True).encode("utf-8"),
    "D3_I_CLASS": _mutate(candidate_class_id="OTHER"),
    "D3_I_GEOMETRY": _mutate(geometry_digest="f1849e3b0c746c23998141d5809140119a78b3029b0e824b44030246398151da"),
    "D3_I_EDGE": _mutate(edge_id="edge:wrong"),
    "D3_I_FIELD": _mutate(field_reference_digest="82e9aade46d17f704bd5dc649fecb94af195b903d31ce42dd52e3990b3e2e5f7"),
    "D3_I_NEGATIVE": _mutate(free=-0.5),
    "D3_I_NONFINITE": D3_V_C0.replace(b'"free":0.5', b'"free":1e999', 1),
    "D3_I_BOOLEAN": _mutate(free=True),
    "D3_I_NEGATIVE_ZERO": D3_V_C0.replace(b'"blocked":0.0', b'"blocked":-0.0', 1),
    "D3_I_CAPACITY": _mutate(capacity=2.0),
    "D3_I_RESOURCE_DIGEST": _mutate(resource_account_digest=ZERO_DIGEST),
    "D3_I_PROJECTION_DIGEST": _mutate(aggregate_projection_digest=ZERO_DIGEST),
    "D3_I_RECORD_DIGEST": _mutate(anatomy_record_digest=ZERO_DIGEST),
    "D3_I_STORED_BOUND": _mutate(bound=0.5),
}

SINGLE_EXPECTED = {
    "D3_I_VERSION": ("D3_UNKNOWN_SCHEMA_OR_VERSION",),
    "D3_I_MISSING": ("D3_MISSING_OR_UNKNOWN_FIELD",),
    "D3_I_EXTRA": ("D3_MISSING_OR_UNKNOWN_FIELD",),
    "D3_I_FORBIDDEN": ("D3_FORBIDDEN_PAYLOAD_PRESENT",),
    "D3_I_SERIALIZATION": ("D3_NONCANONICAL_SERIALIZATION",),
    "D3_I_CLASS": ("D3_CLASS_ID_MISMATCH",),
    "D3_I_GEOMETRY": ("D3_EDGE_ID_GEOMETRY_MISMATCH",),
    "D3_I_EDGE": ("D3_EDGE_ID_GEOMETRY_MISMATCH",),
    "D3_I_FIELD": ("D3_FIELD_REFERENCE_MISMATCH",),
    "D3_I_NEGATIVE": ("D3_NEGATIVE_OR_NONFINITE_RESOURCE_ROLE",),
    "D3_I_NONFINITE": ("D3_NEGATIVE_OR_NONFINITE_RESOURCE_ROLE",),
    "D3_I_BOOLEAN": ("D3_NEGATIVE_OR_NONFINITE_RESOURCE_ROLE",),
    "D3_I_NEGATIVE_ZERO": ("D3_NONCANONICAL_SERIALIZATION",),
    "D3_I_CAPACITY": ("D3_CAPACITY_MISMATCH",),
    "D3_I_RESOURCE_DIGEST": ("D3_RESOURCE_ACCOUNT_DIGEST_MISMATCH",),
    "D3_I_PROJECTION_DIGEST": ("D3_AGGREGATE_PROJECTION_DIGEST_MISMATCH",),
    "D3_I_RECORD_DIGEST": ("D3_ANATOMY_RECORD_DIGEST_MISMATCH",),
    "D3_I_STORED_BOUND": ("D3_MISSING_OR_UNKNOWN_FIELD",),
}

PAIR_MUTATIONS = {
    "D3_P_ARM_INVALID": (D3_V_C0, SINGLE_MUTATIONS["D3_I_RECORD_DIGEST"]),
    "D3_P_IDENTITY": (D3_V_C0, D3_V_C1_IDENTITY_CONTROL),
    "D3_P_C0_ROLE": (D3_V_MIXED, D3_V_C1),
    "D3_P_C1_ROLE": (D3_V_C0, D3_V_MIXED),
    "D3_P_AGGREGATE": (D3_V_C0, D3_V_C1_AGGREGATE_CONTROL),
    "D3_P_ABLATION": (D3_V_MIXED, D3_V_C1),
}
PAIR_EXPECTED = {
    "D3_P_ARM_INVALID": ("D3_PAIR_RECORD_INVALID",),
    "D3_P_IDENTITY": ("D3_PAIR_AGGREGATE_MISMATCH", "D3_PAIR_IDENTITY_MISMATCH"),
    "D3_P_C0_ROLE": ("D3_ABLATION_MISMATCH", "D3_C0_FIXTURE_MISMATCH"),
    "D3_P_C1_ROLE": ("D3_C1_FIXTURE_MISMATCH",),
    "D3_P_AGGREGATE": ("D3_ABLATION_MISMATCH", "D3_C1_FIXTURE_MISMATCH", "D3_PAIR_AGGREGATE_MISMATCH"),
    "D3_P_ABLATION": ("D3_ABLATION_MISMATCH", "D3_C0_FIXTURE_MISMATCH"),
}

POSITIVE_INPUT_DIGESTS = {
    "D3_V_C0": "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
    "D3_V_C1": "058ae964682a9750a316d1db1b2e155714c18bc5adab9eb71fbc6e85e3be54b5",
    "D3_V_MIXED": "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
    "D3_V_C1_IDENTITY_CONTROL": "d1ed106bb1224919e6a106f73bab80e2ead22e02d648d928bbc66ffe635a55b6",
    "D3_V_C1_AGGREGATE_CONTROL": "fb0267ce2697ee8e1c5dae3dff6b43c35817966e401f5edefb6935c7df8578f7",
}
