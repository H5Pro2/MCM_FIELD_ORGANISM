"""Strict consumer for the versioned S1-SC fresh-matrix registration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from types import MappingProxyType

from .four_node_fresh_manifest import (
    FourNodeFreshManifest,
    FourNodeFreshManifestError,
    parse_four_node_fresh_manifest,
)


class FourNodeFreshMatrixRegistrationError(ValueError):
    """Raised when the S1-SC matrix registration is not exact."""


_SCHEMA_ID = "mcm.s1sc.four-node-fresh-matrix-registration.v1"
_SOURCE_CONTRACT_ID = "S1-SC"
_CANONICALIZATION_ID = "S1-JN/S1-JT-compact-json-sha256-v1"
_REGISTRATION_DIGEST = "edd3414b3dcc082c0ab7bec66f8dd278cedecd76d11e649ca7aff46a9317a4ba"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

_ROOT_KEYS = {
    "base_fresh_manifest",
    "canonicalization_id",
    "exposure_replica_axis",
    "matrix_cardinality",
    "public_fresh_projection_binding",
    "registration_digest",
    "schema_id",
    "source_contract_id",
}
_BASE_KEYS = {
    "edge_inventory_digest",
    "manifest_digest",
    "model_role_count",
    "outer_exposure_role_mapping_digest",
    "physical_geometry_digest",
    "public_fresh_projection_digest",
    "schema_id",
    "stateful_private_role_count",
    "stateless_marker_count",
}
_BASE_IDENTITY = {
    "edge_inventory_digest": "9961eddd8c8a7ad845c9ab43af23f8ae5380c72ffae06c2e0af202cda49c3529",
    "manifest_digest": "ae7a7356a3e06776a000b6e9fafef75b717944f1d75da62d4418be98cc439c68",
    "model_role_count": 14,
    "outer_exposure_role_mapping_digest": "16ffec39daf424b73b94ed03b0ee4552e29372ba557b37f194c0d9499c49c1dd",
    "physical_geometry_digest": "e0c416cc4aa97a66960640a2ff8fbe5d75edcc1f7a603c66b1efbf09ea820884",
    "public_fresh_projection_digest": "ce6912af2bc94458c2ba4243fa6df7b8b05494d956ef96730f4faf7ec5a8a879",
    "schema_id": "mcm.s1rk.four-node-fresh-manifest.v1",
    "stateful_private_role_count": 12,
    "stateless_marker_count": 2,
}
_REPLICA_ROLES = (
    "F_A",
    "F_C",
    "F_G",
    "T_EARLY",
    "T_LATER",
    "I_LOCAL",
    "I_REMOTE",
    "I_GAP",
    "C_LOCAL",
    "C_REMOTE",
    "C_GAP",
    "R_EARLY",
    "R_LATE",
    "U_RELEASED",
    "U_EARLY",
    "U_FRESH_B_EARLY",
    "U_FRESH_B_LATE",
)
_CARDINALITY = {
    "c_family_checkpoint_count_per_model": 6,
    "checkpoint_count_per_model": 40,
    "exposure_replica_count": 17,
    "matrix_cell_count": 238,
    "model_role_count": 14,
    "total_checkpoint_count": 560,
    "universal_checkpoint_count_per_model": 34,
}
_PUBLIC_BINDING = {
    "fresh_object_graph_per_cell": True,
    "public_fresh_projection_digest": _BASE_IDENTITY["public_fresh_projection_digest"],
    "shared_by_all_matrix_cells": True,
    "shared_matrix_cell_count": 238,
}


class _DuplicateKeyError(ValueError):
    pass


def _fail(code: str, detail: str) -> None:
    raise FourNodeFreshMatrixRegistrationError(f"{code}: {detail}")


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
        _fail("FRESH_MATRIX_REGISTRATION_SHAPE_INVALID", f"{role} keys differ")
    return value


def _freeze(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _validate_base(value: object) -> dict[str, object]:
    base = _mapping(value, "base fresh manifest", _BASE_KEYS)
    if base != _BASE_IDENTITY:
        _fail("FRESH_MATRIX_REGISTRATION_BASE_IDENTITY_INVALID", "base identity differs")
    return base


def _validate_axis(value: object) -> tuple[tuple[int, str], ...]:
    if not isinstance(value, list) or len(value) != len(_REPLICA_ROLES):
        _fail("FRESH_MATRIX_REGISTRATION_REPLICA_AXIS_INVALID", "axis length differs")
    actual: list[tuple[int, str]] = []
    for index, item in enumerate(value, start=1):
        row = _mapping(item, f"replica axis row {index}", {"position", "replica_role"})
        position = row["position"]
        role = row["replica_role"]
        if type(position) is not int or type(role) is not str:
            _fail("FRESH_MATRIX_REGISTRATION_REPLICA_AXIS_INVALID", f"axis row {index} type differs")
        actual.append((position, role))
    expected = tuple(enumerate(_REPLICA_ROLES, start=1))
    if tuple(actual) != expected:
        _fail("FRESH_MATRIX_REGISTRATION_REPLICA_AXIS_INVALID", "axis order differs")
    return tuple(actual)


def _validate_cardinality(value: object) -> dict[str, object]:
    cardinality = _mapping(value, "matrix cardinality", set(_CARDINALITY))
    if any(type(item) is not int for item in cardinality.values()):
        _fail("FRESH_MATRIX_REGISTRATION_CARDINALITY_INVALID", "cardinality type differs")
    if cardinality != _CARDINALITY:
        _fail("FRESH_MATRIX_REGISTRATION_CARDINALITY_INVALID", "cardinality differs")
    if (
        cardinality["model_role_count"] * cardinality["exposure_replica_count"]
        != cardinality["matrix_cell_count"]
        or cardinality["universal_checkpoint_count_per_model"]
        + cardinality["c_family_checkpoint_count_per_model"]
        != cardinality["checkpoint_count_per_model"]
        or cardinality["model_role_count"] * cardinality["checkpoint_count_per_model"]
        != cardinality["total_checkpoint_count"]
    ):
        _fail("FRESH_MATRIX_REGISTRATION_CARDINALITY_INVALID", "cardinality derivation differs")
    return cardinality


def _validate_public_binding(value: object) -> dict[str, object]:
    binding = _mapping(value, "public fresh projection binding", set(_PUBLIC_BINDING))
    if (
        type(binding["fresh_object_graph_per_cell"]) is not bool
        or type(binding["shared_by_all_matrix_cells"]) is not bool
        or type(binding["shared_matrix_cell_count"]) is not int
        or type(binding["public_fresh_projection_digest"]) is not str
        or binding != _PUBLIC_BINDING
    ):
        _fail("FRESH_MATRIX_REGISTRATION_CARDINALITY_INVALID", "public binding differs")
    return binding


@dataclass(frozen=True, slots=True)
class FourNodeFreshMatrixRegistration:
    """Recursively immutable, validated matrix registration."""

    root: Mapping[str, object]

    @property
    def registration_digest(self) -> str:
        return self.root["registration_digest"]  # type: ignore[return-value]

    @property
    def replica_roles(self) -> tuple[str, ...]:
        rows = self.root["exposure_replica_axis"]
        return tuple(row["replica_role"] for row in rows)  # type: ignore[index,union-attr]


def parse_four_node_fresh_matrix_registration(
    raw_bytes: bytes,
) -> FourNodeFreshMatrixRegistration:
    """Validate the complete S1-SC registration without repair or defaults."""

    if not isinstance(raw_bytes, bytes):
        _fail("FRESH_MATRIX_REGISTRATION_BYTES_INVALID", "registration input must be bytes")
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
        _fail("FRESH_MATRIX_REGISTRATION_SHAPE_INVALID", str(exc))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        _fail("FRESH_MATRIX_REGISTRATION_BYTES_INVALID", str(exc))

    root = _mapping(root, "matrix registration root", _ROOT_KEYS)
    if (
        root["schema_id"] != _SCHEMA_ID
        or root["source_contract_id"] != _SOURCE_CONTRACT_ID
        or root["canonicalization_id"] != _CANONICALIZATION_ID
    ):
        _fail("FRESH_MATRIX_REGISTRATION_SCHEMA_INVALID", "registration identity differs")

    _validate_base(root["base_fresh_manifest"])
    _validate_axis(root["exposure_replica_axis"])
    _validate_cardinality(root["matrix_cardinality"])
    _validate_public_binding(root["public_fresh_projection_binding"])

    registration_digest = root["registration_digest"]
    if not isinstance(registration_digest, str) or not _SHA256.fullmatch(registration_digest):
        _fail("FRESH_MATRIX_REGISTRATION_DIGEST_INVALID", "registration digest is malformed")
    digest_payload = dict(root)
    digest_payload.pop("registration_digest")
    if registration_digest != _REGISTRATION_DIGEST or _digest(digest_payload) != registration_digest:
        _fail("FRESH_MATRIX_REGISTRATION_DIGEST_INVALID", "registration digest differs")

    frozen = _freeze(root)
    if not isinstance(frozen, Mapping):
        _fail("FRESH_MATRIX_REGISTRATION_SHAPE_INVALID", "immutable root is invalid")
    return FourNodeFreshMatrixRegistration(frozen)


def load_four_node_fresh_matrix_registration(
    path: Path,
) -> FourNodeFreshMatrixRegistration:
    """Read one explicit registration path and validate its bytes."""

    if not isinstance(path, Path):
        _fail("FRESH_MATRIX_REGISTRATION_BYTES_INVALID", "registration path must be pathlib.Path")
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        _fail("FRESH_MATRIX_REGISTRATION_BYTES_INVALID", str(exc))
    return parse_four_node_fresh_matrix_registration(raw_bytes)


def validate_four_node_fresh_matrix_registration_against_manifest(
    registration: FourNodeFreshMatrixRegistration,
    manifest: FourNodeFreshManifest,
) -> None:
    """Require a strictly valid registration and its exact valid v1 base."""

    if not isinstance(registration, FourNodeFreshMatrixRegistration):
        _fail("FRESH_MATRIX_REGISTRATION_MANIFEST_MISMATCH", "registration type differs")
    if not isinstance(manifest, FourNodeFreshManifest):
        _fail("FRESH_MATRIX_REGISTRATION_MANIFEST_MISMATCH", "manifest type differs")
    try:
        manifest_bytes = json.dumps(
            _thaw(manifest.root),
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        validated = parse_four_node_fresh_manifest(manifest_bytes)
    except (FourNodeFreshManifestError, TypeError, ValueError) as exc:
        _fail("FRESH_MATRIX_REGISTRATION_MANIFEST_MISMATCH", str(exc))

    base = registration.root["base_fresh_manifest"]
    expected = {
        "edge_inventory_digest": validated.root["edge_inventory"]["digest"],  # type: ignore[index]
        "manifest_digest": validated.manifest_digest,
        "model_role_count": validated.root["cross_identity_audit"]["model_role_count"],  # type: ignore[index]
        "outer_exposure_role_mapping_digest": validated.root["outer_exposure_role_mapping"]["digest"],  # type: ignore[index]
        "physical_geometry_digest": validated.root["physical_geometry"]["digest"],  # type: ignore[index]
        "public_fresh_projection_digest": validated.root["public_fresh_projection"]["digest"],  # type: ignore[index]
        "schema_id": validated.root["schema_id"],
        "stateful_private_role_count": validated.root["cross_identity_audit"]["stateful_private_digest_count"],  # type: ignore[index]
        "stateless_marker_count": validated.root["cross_identity_audit"]["stateless_marker_count"],  # type: ignore[index]
    }
    if dict(base) != expected:  # type: ignore[arg-type]
        _fail("FRESH_MATRIX_REGISTRATION_MANIFEST_MISMATCH", "validated base manifest differs")
