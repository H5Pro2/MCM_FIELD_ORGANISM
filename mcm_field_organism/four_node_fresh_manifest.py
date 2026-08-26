"""Strict immutable consumer for the registered S1-RK four-node manifest."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from types import MappingProxyType
from typing import Mapping


class FourNodeFreshManifestError(ValueError):
    """Raised when the S1-RK manifest cannot be accepted exactly."""


_SCHEMA_ID = "mcm.s1rk.four-node-fresh-manifest.v1"
_SOURCE_CONTRACT_ID = "S1-RJ"
_CANONICALIZATION_ID = "S1-JN/S1-JT-compact-json-sha256-v1"
_MANIFEST_DIGEST = "ae7a7356a3e06776a000b6e9fafef75b717944f1d75da62d4418be98cc439c68"
_EDGE_DIGEST = "9961eddd8c8a7ad845c9ab43af23f8ae5380c72ffae06c2e0af202cda49c3529"
_GEOMETRY_DIGEST = "e0c416cc4aa97a66960640a2ff8fbe5d75edcc1f7a603c66b1efbf09ea820884"
_ROLE_MAPPING_DIGEST = "16ffec39daf424b73b94ed03b0ee4552e29372ba557b37f194c0d9499c49c1dd"
_PUBLIC_FRESH_DIGEST = "ce6912af2bc94458c2ba4243fa6df7b8b05494d956ef96730f4faf7ec5a8a879"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

_ROOT_KEYS = {
    "canonicalization_id",
    "cross_identity_audit",
    "edge_inventory",
    "manifest_digest",
    "outer_exposure_role_mapping",
    "physical_geometry",
    "private_fresh_states",
    "public_fresh_projection",
    "schema_id",
    "source_contract_id",
    "stateless_markers",
}
_CROSS_IDENTITY_AUDIT = {
    "configuration_bindings_resolved": True,
    "dependency_graph_acyclic": True,
    "edge_inventory_shared_by_roles": [
        "A2_B1_FIXED_ADAPTER",
        "A2_B3_LOCAL_LEAKY",
        "A2_B4_LINEAR_COUPLED",
        "A2_B5_F3_FULL",
        "A2_B6_CONST_V",
        "M4_DTS1_T1",
    ],
    "model_role_count": 14,
    "physical_geometry_shared_by_all_roles": True,
    "public_fresh_digest_count": 1,
    "public_fresh_shared_by_all_224_cells": True,
    "stateful_private_digest_count": 12,
    "stateless_marker_count": 2,
}
_STATELESS_MARKERS = (
    (1, "A0_CURRENT_CONTACT", "STATELESS_MARKER:A0_CURRENT_CONTACT:S1RJ"),
    (2, "A1_FAST_SH", "FIELD_ONLY:A1_FAST_SH:S1RJ"),
)
_PRIVATE_ROLES = (
    (3, "A2_B1_FIXED_ADAPTER", "8a55ecf2cac9e4d3268eeb125cb7a6bcd2a4e79e005fbf79a381569fe30911ce"),
    (4, "A2_B2_INTEGRATOR", "cf1f3b36b7e47645df478c0e6099db79d199df95ef9cb0fa9f0288904928be05"),
    (5, "A2_B3_LOCAL_LEAKY", "89924659b50b545c17bd1734a4440764db29063f8d328719f5863d6ed230e12b"),
    (6, "A2_B4_LINEAR_COUPLED", "8d2a656d81d72e430d9c66611b92efc371866b65aefd530c079c67ffaa01b52e"),
    (7, "A2_B5_F3_FULL", "bd23b8ea5811d21c9a3abddf8622183d54b9cfb5a2aa3f0ebec8a2d5c92b3d89"),
    (8, "A2_B6_CONST_V", "2c7899a846853d1683aa2a0421ffda2f7cbd8951399c008a20932c0ca67edfc0"),
    (9, "A3_NORM", "f52e3304538891ed7f9b9eb7ca8d3bbfc79bbf8284ac506f6496ad7052ab2ab4"),
    (10, "M1_PARALLEL_LEAK", "c84829037970255ca0e16417cae9001938a5a50843cc416325c0a9f44963afc5"),
    (11, "M2_DELAY", "97ff90b67e001ba3346173f8a1df7620a5b2895022df14947f34142595f03ea0"),
    (12, "M2_REPLAY", "5fc1d98b534e5a6fbe13afe6913e86011ceed7b2b1f94be7c9abb375aaa08be7"),
    (13, "M4_DTS1_T1", "c673984c64f88074d276f4430e92a4b9242f1118d47eaa85d4a776f405169b2f"),
    (14, "M5_DIRECT", "7eed04ea4fbc72d8c7370ee96ee2a509b9384bc9ec19be54cc533b8f89434edc"),
)
_EDGE_BOUND_ROLES = frozenset(_CROSS_IDENTITY_AUDIT["edge_inventory_shared_by_roles"])


class _DuplicateKeyError(ValueError):
    pass


def _fail(code: str, detail: str) -> None:
    raise FourNodeFreshManifestError(f"{code}: {detail}")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(f"duplicate JSON key {key}")
        result[key] = value
    return result


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mapping(value: object, role: str, keys: set[str]) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        _fail("FRESH_MANIFEST_SHAPE_INVALID", f"{role} keys differ")
    return value


def _array(value: object, role: str) -> list[object]:
    if not isinstance(value, list):
        _fail("FRESH_MANIFEST_SHAPE_INVALID", f"{role} must be an array")
    return value


def _digest_record(
    value: object,
    role: str,
    expected_digest: str,
) -> dict[str, object]:
    record = _mapping(value, role, {"digest", "payload"})
    digest = record["digest"]
    if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
        _fail("FRESH_MANIFEST_DIGEST_INVALID", f"{role} digest is malformed")
    if digest != expected_digest or _digest(record["payload"]) != digest:
        _fail("FRESH_MANIFEST_DIGEST_INVALID", f"{role} digest differs")
    return record


def _validate_common_records(root: dict[str, object]) -> tuple[dict[str, object], ...]:
    edge = _digest_record(root["edge_inventory"], "edge inventory", _EDGE_DIGEST)
    geometry = _digest_record(root["physical_geometry"], "physical geometry", _GEOMETRY_DIGEST)
    role_mapping = _digest_record(
        root["outer_exposure_role_mapping"],
        "outer exposure role mapping",
        _ROLE_MAPPING_DIGEST,
    )
    public = _digest_record(
        root["public_fresh_projection"],
        "public fresh projection",
        _PUBLIC_FRESH_DIGEST,
    )

    edge_payload = _mapping(
        edge["payload"],
        "edge inventory payload",
        {"edges", "geometry_class", "node_order", "schema_id"},
    )
    edges = _array(edge_payload["edges"], "edge inventory edges")
    if len(edges) != 3:
        _fail("FRESH_MANIFEST_SHAPE_INVALID", "edge inventory must contain three edges")
    for index, row in enumerate(edges):
        _mapping(row, f"edge inventory row {index}", {"first_node_id", "second_node_id"})

    geometry_payload = _mapping(
        geometry["payload"],
        "physical geometry payload",
        {
            "dock",
            "edge_inventory_digest",
            "field_id",
            "geometry_class",
            "geometry_id",
            "layer_id",
            "modality_id",
            "nodes",
            "periodic_axes",
            "sample_offsets",
            "schema_id",
        },
    )
    _mapping(
        geometry_payload["dock"],
        "physical geometry dock",
        {"carrier_pairs", "dock_id", "receptor_geometry_id"},
    )
    nodes = _array(geometry_payload["nodes"], "physical geometry nodes")
    if len(nodes) != 4:
        _fail("FRESH_MANIFEST_SHAPE_INVALID", "physical geometry must contain four nodes")
    for index, row in enumerate(nodes):
        _mapping(row, f"physical geometry node {index}", {"node_id", "position"})

    mapping_payload = _mapping(
        role_mapping["payload"],
        "outer exposure role mapping payload",
        {
            "edge_reflection_orbits",
            "node_reflection_orbits",
            "physical_geometry_digest",
            "role_to_node",
            "schema_id",
        },
    )
    public_payload = _mapping(
        public["payload"],
        "public fresh projection payload",
        {
            "initial_field_tick",
            "last_distribution",
            "nodes",
            "physical_geometry_digest",
            "schema_id",
        },
    )
    public_nodes = _array(public_payload["nodes"], "public fresh projection nodes")
    if len(public_nodes) != 4:
        _fail("FRESH_MANIFEST_SHAPE_INVALID", "public projection must contain four nodes")
    for index, row in enumerate(public_nodes):
        _mapping(
            row,
            f"public fresh node {index}",
            {"H", "S", "local_samples", "node_id", "perception_tick", "receptor_contact"},
        )
    return edge_payload, geometry_payload, mapping_payload, public_payload


def _validate_role_axis(root: dict[str, object]) -> tuple[dict[str, object], ...]:
    stateless = _array(root["stateless_markers"], "stateless markers")
    actual_markers = []
    for index, value in enumerate(stateless):
        row = _mapping(
            value,
            f"stateless marker {index}",
            {"model_role", "position", "state_marker"},
        )
        actual_markers.append((row["position"], row["model_role"], row["state_marker"]))
    if tuple(actual_markers) != _STATELESS_MARKERS:
        _fail("FRESH_MANIFEST_ROLE_AXIS_INVALID", "stateless role axis differs")

    private = _array(root["private_fresh_states"], "private fresh states")
    if len(private) != len(_PRIVATE_ROLES):
        _fail("FRESH_MANIFEST_ROLE_AXIS_INVALID", "private role count differs")
    payloads = []
    for value, expected in zip(private, _PRIVATE_ROLES, strict=True):
        position, role, expected_digest = expected
        row = _mapping(
            value,
            f"private role {role}",
            {"digest", "model_role", "payload", "position"},
        )
        if row["position"] != position or row["model_role"] != role:
            _fail("FRESH_MANIFEST_ROLE_AXIS_INVALID", f"private role {role} differs")
        payload = _mapping(
            row["payload"],
            f"private role payload {role}",
            {
                "carry_class",
                "configuration_binding",
                "model_role",
                "native_state_schema_id",
                "schema_id",
                "state_payload",
            },
        )
        if payload["model_role"] != role or not isinstance(payload["state_payload"], dict):
            _fail("FRESH_MANIFEST_ROLE_AXIS_INVALID", f"private payload role {role} differs")
        digest = row["digest"]
        if digest != expected_digest or _digest(payload) != digest:
            _fail("FRESH_MANIFEST_DIGEST_INVALID", f"private role {role} digest differs")
        payloads.append(payload)
    return tuple(payloads)


def _validate_dependencies(
    root: dict[str, object],
    common: tuple[dict[str, object], ...],
    private_payloads: tuple[dict[str, object], ...],
) -> None:
    _, geometry, role_mapping, public = common
    if (
        geometry["edge_inventory_digest"] != _EDGE_DIGEST
        or role_mapping["physical_geometry_digest"] != _GEOMETRY_DIGEST
        or public["physical_geometry_digest"] != _GEOMETRY_DIGEST
        or root["cross_identity_audit"] != _CROSS_IDENTITY_AUDIT
    ):
        _fail("FRESH_MANIFEST_DEPENDENCY_INVALID", "common identity dependency differs")

    by_role = {
        role: payload["state_payload"]
        for (_, role, _), payload in zip(_PRIVATE_ROLES, private_payloads, strict=True)
    }
    for role in _EDGE_BOUND_ROLES:
        state = by_role[role]
        if not isinstance(state, dict) or state.get("edge_inventory_digest") != _EDGE_DIGEST:
            _fail("FRESH_MANIFEST_DEPENDENCY_INVALID", f"edge dependency differs for {role}")
    for role in ("M2_DELAY", "M2_REPLAY"):
        state = by_role[role]
        if not isinstance(state, dict) or state.get("geometry_digest") != _GEOMETRY_DIGEST:
            _fail("FRESH_MANIFEST_DEPENDENCY_INVALID", f"geometry dependency differs for {role}")


def _freeze(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class FourNodeFreshManifest:
    """Recursively immutable, fully validated view of the S1-RK manifest."""

    root: Mapping[str, object]

    @property
    def manifest_digest(self) -> str:
        return self.root["manifest_digest"]  # type: ignore[return-value]

    @property
    def physical_geometry(self) -> Mapping[str, object]:
        return self.root["physical_geometry"]  # type: ignore[return-value]

    @property
    def public_fresh_projection(self) -> Mapping[str, object]:
        return self.root["public_fresh_projection"]  # type: ignore[return-value]


def parse_four_node_fresh_manifest(raw_bytes: bytes) -> FourNodeFreshManifest:
    """Validate every registered S1-RK identity without repair or defaults."""

    if not isinstance(raw_bytes, bytes):
        _fail("FRESH_MANIFEST_BYTES_INVALID", "manifest input must be bytes")
    try:
        decoded = raw_bytes.decode("utf-8")
        root = json.loads(
            decoded,
            object_pairs_hook=_unique_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON constant {value}")
            ),
        )
    except _DuplicateKeyError as exc:
        _fail("FRESH_MANIFEST_SHAPE_INVALID", str(exc))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _fail("FRESH_MANIFEST_BYTES_INVALID", str(exc))

    root = _mapping(root, "manifest root", _ROOT_KEYS)
    if (
        root["schema_id"] != _SCHEMA_ID
        or root["source_contract_id"] != _SOURCE_CONTRACT_ID
        or root["canonicalization_id"] != _CANONICALIZATION_ID
    ):
        _fail("FRESH_MANIFEST_SCHEMA_INVALID", "manifest identity differs")

    common = _validate_common_records(root)
    private_payloads = _validate_role_axis(root)
    _validate_dependencies(root, common, private_payloads)

    manifest_digest = root["manifest_digest"]
    if not isinstance(manifest_digest, str) or not _SHA256.fullmatch(manifest_digest):
        _fail("FRESH_MANIFEST_DIGEST_INVALID", "manifest digest is malformed")
    digest_payload = dict(root)
    digest_payload.pop("manifest_digest")
    if manifest_digest != _MANIFEST_DIGEST or _digest(digest_payload) != manifest_digest:
        _fail("FRESH_MANIFEST_DIGEST_INVALID", "manifest digest differs")

    frozen = _freeze(root)
    if not isinstance(frozen, Mapping):
        _fail("FRESH_MANIFEST_SHAPE_INVALID", "immutable manifest root is invalid")
    return FourNodeFreshManifest(frozen)


def load_four_node_fresh_manifest(path: Path) -> FourNodeFreshManifest:
    """Read one explicit path once and pass its bytes to the strict parser."""

    if not isinstance(path, Path):
        _fail("FRESH_MANIFEST_BYTES_INVALID", "manifest path must be pathlib.Path")
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        _fail("FRESH_MANIFEST_BYTES_INVALID", str(exc))
    return parse_four_node_fresh_manifest(raw_bytes)
