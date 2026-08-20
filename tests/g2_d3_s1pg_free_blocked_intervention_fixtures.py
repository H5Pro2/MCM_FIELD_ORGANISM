"""Canonical S1-PG intervention fixtures and isolated mutations."""

from __future__ import annotations

import json

from mcm_field_organism.kfs1_schema_validator import canonical_json_bytes, sha256_hex


EDGE = "edge:carrier-a:carrier-b"
GEOMETRY = "26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651"
FIELD = "8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835"


def _rebind_anatomy(record: dict[str, object]) -> bytes:
    value = dict(record)
    value["resource_account_digest"] = sha256_hex(
        canonical_json_bytes(
            {
                key: value[key]
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
    value["aggregate_projection_digest"] = sha256_hex(
        canonical_json_bytes(
            {
                "edge_id": value["edge_id"],
                "capacity": value["capacity"],
                "free": value["free"],
                "bound": value["bound_unconfigured"] + value["bound_configured"],
                "blocked": value["blocked"],
            }
        )
    )
    value.pop("anatomy_record_digest", None)
    value["anatomy_record_digest"] = sha256_hex(canonical_json_bytes(value))
    return canonical_json_bytes(value)


def _anatomy(
    free: float,
    blocked: float,
    *,
    bound_unconfigured: float = 0.25,
    bound_configured: float = 0.25,
    edge_id: str = EDGE,
    carrier_a_id: str = "carrier-a",
    carrier_b_id: str = "carrier-b",
    geometry_digest: str = GEOMETRY,
) -> bytes:
    return _rebind_anatomy(
        {
            "schema_id": "g2_d3_anatomy_record",
            "schema_version": "s1np.v1",
            "candidate_class_id": "G2_CONSERVATIVE_BOUND_SUBPARTITION",
            "geometry_digest": geometry_digest,
            "field_reference_digest": FIELD,
            "edge_id": edge_id,
            "carrier_a_id": carrier_a_id,
            "carrier_b_id": carrier_b_id,
            "capacity": 1.0,
            "free": free,
            "bound_unconfigured": bound_unconfigured,
            "bound_configured": bound_configured,
            "blocked": blocked,
        }
    )


def _event(**changes: object) -> bytes:
    value = {
        "schema_id": "g2_d3_fresh_binding_event_identity",
        "schema_version": "s1pe.v1",
        "event_id": "S1_PE_IDENTICAL_FRESH_BINDING_EVENT_V1",
        "event_role": "IDENTICAL_FRESH_LOCAL_BINDING",
        "exposure_scope": "CANDIDATE_ARMS_AND_REGISTERED_BASELINES",
        "event_payload_status": "UNBOUND",
    }
    value.update(changes)
    value.pop("event_identity_digest", None)
    value["event_identity_digest"] = sha256_hex(canonical_json_bytes(value))
    return canonical_json_bytes(value)


def _fixture(
    prestate: bytes,
    free_post: bytes,
    blocked_post: bytes,
    event: bytes,
    **changes: object,
) -> bytes:
    pre = json.loads(prestate)
    free_value = json.loads(free_post)
    blocked_value = json.loads(blocked_post)
    event_value = json.loads(event)
    value = {
        "schema_id": "g2_d3_free_blocked_intervention_fixture",
        "schema_version": "s1pe.v1",
        "fixture_id": "S1_PE_G2_D3_FREE_BLOCKED_PAIR_V1",
        "causal_source_id": "REGISTERED_EXTERNAL_TEST_INTERVENTION",
        "common_prestate_record_digest": pre["anatomy_record_digest"],
        "transfer_amount": 0.125,
        "free_available_arm_id": "FREE_AVAILABLE",
        "free_available_post_record_digest": free_value["anatomy_record_digest"],
        "blocked_held_arm_id": "BLOCKED_HELD",
        "blocked_held_post_record_digest": blocked_value["anatomy_record_digest"],
        "fresh_event_identity_digest": event_value["event_identity_digest"],
        "candidate_metadata_exposure": False,
    }
    value.update(changes)
    value.pop("fixture_digest", None)
    value["fixture_digest"] = sha256_hex(canonical_json_bytes(value))
    return canonical_json_bytes(value)


PRESTATE = _anatomy(0.375, 0.125)
FREE_AVAILABLE_POST = _anatomy(0.5, 0.0)
BLOCKED_HELD_POST = _anatomy(0.25, 0.25)
EVENT_IDENTITY = _event()
FIXTURE_MANIFEST = _fixture(PRESTATE, FREE_AVAILABLE_POST, BLOCKED_HELD_POST, EVENT_IDENTITY)
POSITIVE_INPUTS = (
    PRESTATE,
    FREE_AVAILABLE_POST,
    BLOCKED_HELD_POST,
    EVENT_IDENTITY,
    FIXTURE_MANIFEST,
)
POSITIVE_INPUT_DIGESTS = (
    "47e65ce1b4f0a7a42dce13222cfb6e29a91b226c8b9ed479ccd3d9eb3539eff6",
    "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
    "f9a43177383df5f900faf9020f6aa76e10b0898cdf527d21d1f0e2a93bbd4025",
    "82996574d1de2b09953188332b6a81a6ea549a7406e3a39c0ba31c164b49acf7",
    "a1af0a6336cd3911f4b3e2cae03e8af0de1a0a3d4cd3a8967dbb9fe33d1650c6",
)


def _replace_fixture(**changes: object) -> tuple[bytes, bytes, bytes, bytes, bytes]:
    return (
        PRESTATE,
        FREE_AVAILABLE_POST,
        BLOCKED_HELD_POST,
        EVENT_IDENTITY,
        _fixture(PRESTATE, FREE_AVAILABLE_POST, BLOCKED_HELD_POST, EVENT_IDENTITY, **changes),
    )


version_mutation = _replace_fixture(schema_version="s1pe.v2")
missing_value = json.loads(FIXTURE_MANIFEST)
del missing_value["causal_source_id"]
missing_value.pop("fixture_digest")
missing_value["fixture_digest"] = sha256_hex(canonical_json_bytes(missing_value))
missing_mutation = (*POSITIVE_INPUTS[:4], canonical_json_bytes(missing_value))

extra_event = _event(unknown_field=True)
extra_event_mutation = (
    PRESTATE,
    FREE_AVAILABLE_POST,
    BLOCKED_HELD_POST,
    extra_event,
    _fixture(PRESTATE, FREE_AVAILABLE_POST, BLOCKED_HELD_POST, extra_event),
)
pretty_fixture = json.dumps(json.loads(FIXTURE_MANIFEST), indent=2, sort_keys=True).encode("utf-8")
serialization_mutation = (*POSITIVE_INPUTS[:4], pretty_fixture)

bad_event_digest_value = json.loads(EVENT_IDENTITY)
bad_event_digest_value["event_identity_digest"] = "0" * 64
event_digest_mutation = (*POSITIVE_INPUTS[:3], canonical_json_bytes(bad_event_digest_value), FIXTURE_MANIFEST)
bad_fixture_digest_value = json.loads(FIXTURE_MANIFEST)
bad_fixture_digest_value["fixture_digest"] = "0" * 64
fixture_digest_mutation = (*POSITIVE_INPUTS[:4], canonical_json_bytes(bad_fixture_digest_value))

causal_mutation = _replace_fixture(causal_source_id="OTHER_SOURCE")
pre_reference_mutation = _replace_fixture(common_prestate_record_digest="0" * 64)
arm_set_mutation = _replace_fixture(blocked_held_arm_id="FREE_AVAILABLE")
zero_transfer_mutation = _replace_fixture(transfer_amount=0.0)
insufficient_transfer_mutation = _replace_fixture(transfer_amount=0.5)

non_target_post = _anatomy(0.625, 0.0, bound_unconfigured=0.125)
non_target_mutation = (
    PRESTATE,
    non_target_post,
    BLOCKED_HELD_POST,
    EVENT_IDENTITY,
    _fixture(PRESTATE, non_target_post, BLOCKED_HELD_POST, EVENT_IDENTITY),
)

other_edge_post = _anatomy(
    0.5,
    0.0,
    edge_id="edge:carrier-c:carrier-d",
    carrier_a_id="carrier-c",
    carrier_b_id="carrier-d",
    geometry_digest="75e06f6602eeb02fe90bd5aa72b1c67103a6bc4f0c7b2136611f4ef4945fa2f1",
)
pair_control_mutation = (
    PRESTATE,
    other_edge_post,
    BLOCKED_HELD_POST,
    EVENT_IDENTITY,
    _fixture(PRESTATE, other_edge_post, BLOCKED_HELD_POST, EVENT_IDENTITY),
)

wrong_transfer_post = _anatomy(0.4375, 0.0625)
local_conservation_mutation = (
    PRESTATE,
    wrong_transfer_post,
    BLOCKED_HELD_POST,
    EVENT_IDENTITY,
    _fixture(PRESTATE, wrong_transfer_post, BLOCKED_HELD_POST, EVENT_IDENTITY),
)

negative_value = json.loads(FREE_AVAILABLE_POST)
negative_value.update(free=-0.125, blocked=0.625)
negative_post = _rebind_anatomy(negative_value)
negative_mutation = (
    PRESTATE,
    negative_post,
    BLOCKED_HELD_POST,
    EVENT_IDENTITY,
    _fixture(PRESTATE, negative_post, BLOCKED_HELD_POST, EVENT_IDENTITY),
)

metadata_value = json.loads(FREE_AVAILABLE_POST)
metadata_value["arm_id"] = "FREE_AVAILABLE"
metadata_post = _rebind_anatomy(metadata_value)
metadata_mutation = (
    PRESTATE,
    metadata_post,
    BLOCKED_HELD_POST,
    EVENT_IDENTITY,
    _fixture(PRESTATE, metadata_post, BLOCKED_HELD_POST, EVENT_IDENTITY),
)

bound_event = _event(event_payload_status="BOUND")
bound_event_mutation = (
    PRESTATE,
    FREE_AVAILABLE_POST,
    BLOCKED_HELD_POST,
    bound_event,
    _fixture(PRESTATE, FREE_AVAILABLE_POST, BLOCKED_HELD_POST, bound_event),
)

SEMANTIC_MUTATIONS = {
    "version": version_mutation,
    "missing": missing_mutation,
    "event_extra": extra_event_mutation,
    "serialization": serialization_mutation,
    "event_digest": event_digest_mutation,
    "fixture_digest": fixture_digest_mutation,
    "causal_source": causal_mutation,
    "pre_reference": pre_reference_mutation,
    "arm_set": arm_set_mutation,
    "zero_transfer": zero_transfer_mutation,
    "insufficient_transfer": insufficient_transfer_mutation,
    "non_target": non_target_mutation,
    "pair_control": pair_control_mutation,
    "local_conservation": local_conservation_mutation,
    "negative": negative_mutation,
    "metadata": metadata_mutation,
    "event_payload": bound_event_mutation,
}
SEMANTIC_EXPECTED = {
    "version": ("PE_UNKNOWN_SCHEMA_OR_VERSION",),
    "missing": ("PE_MISSING_OR_UNKNOWN_FIELD",),
    "event_extra": ("PE_MISSING_OR_UNKNOWN_FIELD",),
    "serialization": ("PE_NONCANONICAL_SERIALIZATION",),
    "event_digest": ("PE_EVENT_IDENTITY_DIGEST_MISMATCH",),
    "fixture_digest": ("PE_FIXTURE_DIGEST_MISMATCH",),
    "causal_source": ("PD_INVALID_CAUSAL_SOURCE",),
    "pre_reference": ("PD_INVALID_COMMON_PRESTATE",),
    "arm_set": ("PD_INVALID_ARM_SET",),
    "zero_transfer": ("PD_INVALID_TRANSFER_AMOUNT",),
    "insufficient_transfer": ("PD_INSUFFICIENT_SOURCE_RESOURCE",),
    "non_target": ("PD_NON_TARGET_ROLE_CHANGED",),
    "pair_control": ("PD_PAIR_CONTROL_MISMATCH",),
    "local_conservation": ("PD_LOCAL_CONSERVATION_FAILED",),
    "negative": ("PD_NONFINITE_OR_NEGATIVE_RESOURCE",),
    "metadata": ("PD_FORBIDDEN_METADATA_PERSISTENCE",),
    "event_payload": ("PE_EVENT_PAYLOAD_BOUND",),
}

invalid_anatomy_value = json.loads(FREE_AVAILABLE_POST)
invalid_anatomy_value["anatomy_record_digest"] = "0" * 64
INVALID_ANATOMY_INPUTS = (
    PRESTATE,
    canonical_json_bytes(invalid_anatomy_value),
    BLOCKED_HELD_POST,
    EVENT_IDENTITY,
    FIXTURE_MANIFEST,
)


__all__ = (
    "PRESTATE",
    "FREE_AVAILABLE_POST",
    "BLOCKED_HELD_POST",
    "EVENT_IDENTITY",
    "FIXTURE_MANIFEST",
    "POSITIVE_INPUTS",
    "POSITIVE_INPUT_DIGESTS",
    "SEMANTIC_MUTATIONS",
    "SEMANTIC_EXPECTED",
    "INVALID_ANATOMY_INPUTS",
)
