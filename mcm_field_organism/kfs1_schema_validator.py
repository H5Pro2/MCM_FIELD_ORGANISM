"""Isolated static validator for the KFS-1 S1-MY record schemas."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from typing import Any, Mapping


__all__ = (
    "ANATOMY_SCHEMA_ID",
    "MEASUREMENT_SCHEMA_ID",
    "RECORD_SCHEMA_VERSION",
    "RECEIPT_SCHEMA_ID",
    "RECEIPT_SCHEMA_VERSION",
    "MEASUREMENT_ROLES",
    "PASSIVE_READ_SCOPES",
    "VALIDATION_PHASES",
    "FAILURE_CODES",
    "KFS1ValidationRegistry",
    "KFS1ValidationReceipt",
    "canonical_json_bytes",
    "sha256_hex",
    "validate_kfs1_record",
    "build_kfs1_validation_registry",
)


ANATOMY_SCHEMA_ID = "kfs1_anatomy_record"
MEASUREMENT_SCHEMA_ID = "kfs1_measurement_record"
RECORD_SCHEMA_VERSION = "s1my.v1"
RECEIPT_SCHEMA_ID = "kfs1_validation_receipt"
RECEIPT_SCHEMA_VERSION = "s1mz.v1"

MEASUREMENT_ROLES = (
    "attenuation_observer",
    "disturbance_read",
    "interference_observer",
    "late_reception_read",
    "rebinding_observer",
    "release_observer",
)
PASSIVE_READ_SCOPES = ("read_only",)
VALIDATION_PHASES = (
    "byte_intake",
    "schema_validation",
    "anatomy_validation",
    "ledger_validation",
    "causal_validation",
    "digest_validation",
    "validation_receipt",
)
FAILURE_CODES = (
    "ANATOMY_DIGEST_MISMATCH",
    "DIGEST_MISMATCH",
    "DUPLICATE_CARRIER_OR_EDGE_ID",
    "EDGE_ID_GEOMETRY_MISMATCH",
    "EXPOSURE_HISTORY_MISSING_OR_MISMATCHED",
    "FIELD_REFERENCE_MISMATCH",
    "MISSING_OR_UNKNOWN_FIELD",
    "NEGATIVE_OR_NONFINITE_RESOURCE_ROLE",
    "NONCANONICAL_SERIALIZATION",
    "RAW_DATA_LABEL_TARGET_OR_SEQUENCE_BUFFER_PRESENT",
    "READ_SCOPE_NOT_PASSIVE",
    "RESOURCE_CAPACITY_MISMATCH",
    "RESOURCE_DOUBLE_COUNTING",
    "UNKNOWN_SCHEMA_OR_VERSION",
    "UNREGISTERED_MEASUREMENT_ROLE",
)

_ANATOMY_FIELDS = frozenset(
    {
        "schema_id",
        "schema_version",
        "candidate_id",
        "geometry_digest",
        "carrier_ids",
        "edge_records",
        "anatomy_digest",
    }
)
_EDGE_FIELDS = frozenset(
    {
        "edge_id",
        "carrier_a_id",
        "carrier_b_id",
        "capacity",
        "free",
        "bound",
        "blocked",
        "field_reference_digest",
        "resource_account_digest",
    }
)
_MEASUREMENT_FIELDS = frozenset(
    {
        "schema_id",
        "schema_version",
        "measurement_slot_id",
        "measurement_role",
        "candidate_or_baseline_id",
        "anatomy_digest",
        "field_reference_digest",
        "exposure_history_digest",
        "read_scope",
        "validation_status",
        "failure_reasons",
        "measurement_record_digest",
    }
)
_FORBIDDEN_KEYS = frozenset(
    {
        "raw_data",
        "raw_audio",
        "raw_video",
        "label",
        "labels",
        "target",
        "targets",
        "sequence_buffer",
        "reward",
    }
)


@dataclass(frozen=True)
class KFS1ValidationRegistry:
    schema_versions: tuple[tuple[str, str], ...]
    measurement_roles: tuple[str, ...]
    passive_read_scopes: tuple[str, ...]
    geometry_edges: tuple[tuple[str, tuple[tuple[str, str, str], ...]], ...]
    field_reference_digests: tuple[str, ...]
    anatomy_digests: tuple[str, ...]
    exposure_history_digests: tuple[str, ...]
    failure_codes: tuple[str, ...]
    validation_phases: tuple[str, ...]


@dataclass(frozen=True)
class KFS1ValidationReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    input_bytes_digest: str
    declared_record_schema_id: str
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    computed_record_digest: str
    validator_contract_digest: str
    validation_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {field.name: getattr(self, field.name) for field in fields(self)}
        payload["completed_checks"] = list(self.completed_checks)
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


def _fixture_identity(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


_GEOMETRY_DIGEST = _fixture_identity("kfs1.geometry.min.01")
_FIELD_REFERENCE_DIGEST = _fixture_identity("kfs1.field-reference.min.01")
_EXPOSURE_HISTORY_DIGEST = _fixture_identity("kfs1.exposure-history.min.01")


def _assert_canonical_value(value: Any) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value) or (value == 0.0 and math.copysign(1.0, value) < 0):
            raise ValueError("nonfinite and negative-zero numbers are not canonical")
        return
    if isinstance(value, list):
        for item in value:
            _assert_canonical_value(item)
        return
    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise TypeError("canonical mappings require string keys")
        for item in value.values():
            _assert_canonical_value(item)
        return
    raise TypeError("unsupported canonical JSON value")


def canonical_json_bytes(value: Any) -> bytes:
    """Return the bound compact canonical JSON bytes without mutating value."""

    _assert_canonical_value(value)
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_hex(raw_bytes: bytes) -> str:
    if type(raw_bytes) is not bytes:
        raise TypeError("raw_bytes must be bytes")
    return hashlib.sha256(raw_bytes).hexdigest()


def _digest_payload(payload: Mapping[str, Any], excluded_key: str) -> str:
    return sha256_hex(
        canonical_json_bytes(
            {key: value for key, value in payload.items() if key != excluded_key}
        )
    )


def _positive_anatomy_digest() -> str:
    edge_id = "edge:carrier-a:carrier-b"
    resource_payload = {
        "edge_id": edge_id,
        "capacity": 1,
        "free": 1,
        "bound": 0,
        "blocked": 0,
    }
    anatomy = {
        "schema_id": ANATOMY_SCHEMA_ID,
        "schema_version": RECORD_SCHEMA_VERSION,
        "candidate_id": "KFS-1",
        "geometry_digest": _GEOMETRY_DIGEST,
        "carrier_ids": ["carrier-a", "carrier-b"],
        "edge_records": [
            {
                "edge_id": edge_id,
                "carrier_a_id": "carrier-a",
                "carrier_b_id": "carrier-b",
                "capacity": 1,
                "free": 1,
                "bound": 0,
                "blocked": 0,
                "field_reference_digest": _FIELD_REFERENCE_DIGEST,
                "resource_account_digest": sha256_hex(
                    canonical_json_bytes(resource_payload)
                ),
            }
        ],
    }
    return sha256_hex(canonical_json_bytes(anatomy))


_ANATOMY_DIGEST = _positive_anatomy_digest()
_VALIDATOR_CONTRACT_DIGEST = _fixture_identity(
    "kfs1.validator.contract.s1na.v1"
)


def build_kfs1_validation_registry() -> KFS1ValidationRegistry:
    return KFS1ValidationRegistry(
        schema_versions=(
            (ANATOMY_SCHEMA_ID, RECORD_SCHEMA_VERSION),
            (MEASUREMENT_SCHEMA_ID, RECORD_SCHEMA_VERSION),
        ),
        measurement_roles=MEASUREMENT_ROLES,
        passive_read_scopes=PASSIVE_READ_SCOPES,
        geometry_edges=(
            (
                _GEOMETRY_DIGEST,
                (("edge:carrier-a:carrier-b", "carrier-a", "carrier-b"),),
            ),
        ),
        field_reference_digests=(_FIELD_REFERENCE_DIGEST,),
        anatomy_digests=(_ANATOMY_DIGEST,),
        exposure_history_digests=(_EXPOSURE_HISTORY_DIGEST,),
        failure_codes=FAILURE_CODES,
        validation_phases=VALIDATION_PHASES,
    )


def _validate_registry(registry: KFS1ValidationRegistry) -> None:
    if type(registry) is not KFS1ValidationRegistry:
        raise TypeError("registry must be KFS1ValidationRegistry")
    if registry != build_kfs1_validation_registry():
        raise ValueError("registry does not match the bound S1-NA registry")


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        if any(key in _FORBIDDEN_KEYS for key in value):
            return True
        return any(_contains_forbidden_key(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_finite_nonnegative(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return value >= 0
    return isinstance(value, float) and math.isfinite(value) and value >= 0


def _parse_record(raw_bytes: bytes) -> tuple[Any, bool]:
    duplicate_key = False

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        nonlocal duplicate_key
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                duplicate_key = True
            result[key] = value
        return result

    parsed = json.loads(
        raw_bytes.decode("utf-8"),
        object_pairs_hook=pairs_hook,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"invalid JSON constant {value}")
        ),
    )
    return parsed, duplicate_key


def _receipt(
    *,
    input_digest: str,
    declared_schema: str,
    failures: set[str],
    completed: list[str],
    computed_record_digest: str,
) -> KFS1ValidationReceipt:
    ordered_failures = tuple(sorted(failures))
    payload = {
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "input_bytes_digest": input_digest,
        "declared_record_schema_id": declared_schema,
        "validation_status": "invalid" if ordered_failures else "valid",
        "completed_checks": list(completed),
        "failure_reasons": list(ordered_failures),
        "computed_record_digest": computed_record_digest,
        "validator_contract_digest": _VALIDATOR_CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    return KFS1ValidationReceipt(
        receipt_schema_id=RECEIPT_SCHEMA_ID,
        receipt_schema_version=RECEIPT_SCHEMA_VERSION,
        input_bytes_digest=input_digest,
        declared_record_schema_id=declared_schema,
        validation_status="invalid" if ordered_failures else "valid",
        completed_checks=tuple(completed),
        failure_reasons=ordered_failures,
        computed_record_digest=computed_record_digest,
        validator_contract_digest=_VALIDATOR_CONTRACT_DIGEST,
        validation_receipt_digest=receipt_digest,
    )


def _check_exact_fields(
    record: dict[str, Any], expected: frozenset[str], failures: set[str]
) -> bool:
    actual = frozenset(record)
    missing = expected - actual
    extra = actual - expected
    specific_missing = {"exposure_history_digest"}
    specific_extra = extra & _FORBIDDEN_KEYS
    if (missing - specific_missing) or (extra - specific_extra):
        failures.add("MISSING_OR_UNKNOWN_FIELD")
    if "exposure_history_digest" in missing:
        failures.add("EXPOSURE_HISTORY_MISSING_OR_MISMATCHED")
    if specific_extra:
        failures.add("RAW_DATA_LABEL_TARGET_OR_SEQUENCE_BUFFER_PRESENT")
    return not missing and not extra


def _validate_anatomy(
    record: dict[str, Any], registry: KFS1ValidationRegistry, failures: set[str]
) -> str:
    fields_complete = _check_exact_fields(record, _ANATOMY_FIELDS, failures)
    if record.get("candidate_id") != "KFS-1":
        failures.add("MISSING_OR_UNKNOWN_FIELD")

    carrier_ids = record.get("carrier_ids")
    edges = record.get("edge_records")
    if not isinstance(carrier_ids, list) or not all(
        isinstance(item, str) for item in carrier_ids
    ):
        failures.add("MISSING_OR_UNKNOWN_FIELD")
        carrier_ids = []
    if len(carrier_ids) != len(set(carrier_ids)):
        failures.add("DUPLICATE_CARRIER_OR_EDGE_ID")
    if not isinstance(edges, list) or not all(isinstance(item, dict) for item in edges):
        failures.add("MISSING_OR_UNKNOWN_FIELD")
        edges = []

    geometry_digest = record.get("geometry_digest")
    geometry_map = dict(registry.geometry_edges)
    allowed_edges = {
        edge_id: (carrier_a, carrier_b)
        for edge_id, carrier_a, carrier_b in geometry_map.get(geometry_digest, ())
    }
    edge_ids = [edge.get("edge_id") for edge in edges]
    if len(edge_ids) != len(set(edge_ids)):
        failures.add("DUPLICATE_CARRIER_OR_EDGE_ID")

    resource_digests: list[str] = []
    for edge in edges:
        edge_complete = _check_exact_fields(edge, _EDGE_FIELDS, failures)
        edge_id = edge.get("edge_id")
        pair = (edge.get("carrier_a_id"), edge.get("carrier_b_id"))
        if edge_id not in allowed_edges or allowed_edges.get(edge_id) != pair:
            failures.add("EDGE_ID_GEOMETRY_MISMATCH")

        values = tuple(edge.get(key) for key in ("capacity", "free", "bound", "blocked"))
        if not all(_is_finite_nonnegative(value) for value in values):
            failures.add("NEGATIVE_OR_NONFINITE_RESOURCE_ROLE")
        elif values[0] != values[1] + values[2] + values[3]:
            failures.add("RESOURCE_CAPACITY_MISMATCH")

        resource_digest = edge.get("resource_account_digest")
        if isinstance(resource_digest, str):
            resource_digests.append(resource_digest)
        if edge.get("field_reference_digest") not in registry.field_reference_digests:
            failures.add("FIELD_REFERENCE_MISMATCH")

        if edge_complete and all(_is_finite_nonnegative(value) for value in values):
            resource_payload = {
                "edge_id": edge_id,
                "capacity": values[0],
                "free": values[1],
                "bound": values[2],
                "blocked": values[3],
            }
            if not failures and resource_digest != sha256_hex(canonical_json_bytes(resource_payload)):
                failures.add("DIGEST_MISMATCH")

    if len(resource_digests) != len(set(resource_digests)):
        failures.discard("DUPLICATE_CARRIER_OR_EDGE_ID")
        failures.discard("EDGE_ID_GEOMETRY_MISMATCH")
        failures.discard("DIGEST_MISMATCH")
        failures.add("RESOURCE_DOUBLE_COUNTING")

    computed = "not_computable"
    if fields_complete:
        try:
            computed = _digest_payload(record, "anatomy_digest")
        except (TypeError, ValueError):
            pass
    declared = record.get("anatomy_digest")
    if not failures and computed != "not_computable" and declared != computed:
        failures.add("DIGEST_MISMATCH")
    return computed


def _validate_measurement(
    record: dict[str, Any], registry: KFS1ValidationRegistry, failures: set[str]
) -> str:
    fields_complete = _check_exact_fields(record, _MEASUREMENT_FIELDS, failures)
    role = record.get("measurement_role")
    if role not in registry.measurement_roles:
        failures.add("UNREGISTERED_MEASUREMENT_ROLE")
    if record.get("read_scope") not in registry.passive_read_scopes:
        failures.add("READ_SCOPE_NOT_PASSIVE")
    if record.get("field_reference_digest") not in registry.field_reference_digests:
        failures.add("FIELD_REFERENCE_MISMATCH")
    if record.get("anatomy_digest") not in registry.anatomy_digests:
        failures.add("ANATOMY_DIGEST_MISMATCH")
    if record.get("exposure_history_digest") not in registry.exposure_history_digests:
        failures.add("EXPOSURE_HISTORY_MISSING_OR_MISMATCHED")
    if record.get("validation_status") not in ("valid", "invalid") or not isinstance(
        record.get("failure_reasons"), list
    ):
        failures.add("MISSING_OR_UNKNOWN_FIELD")

    computed = "not_computable"
    if fields_complete:
        try:
            computed = _digest_payload(record, "measurement_record_digest")
        except (TypeError, ValueError):
            pass
    declared = record.get("measurement_record_digest")
    if not failures and computed != "not_computable" and declared != computed:
        failures.add("DIGEST_MISMATCH")
    return computed


def validate_kfs1_record(
    raw_bytes: bytes, registry: KFS1ValidationRegistry
) -> KFS1ValidationReceipt:
    """Validate raw record bytes without repair, runtime access, or field writes."""

    if type(raw_bytes) is not bytes:
        raise TypeError("raw_bytes must be bytes")
    _validate_registry(registry)

    input_digest = sha256_hex(raw_bytes)
    failures: set[str] = set()
    completed = ["byte_intake"]
    declared_schema = "unreadable"
    computed_record_digest = "not_computable"

    try:
        record, duplicate_key = _parse_record(raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        failures.add("NONCANONICAL_SERIALIZATION")
        completed.extend(("schema_validation", "validation_receipt"))
        return _receipt(
            input_digest=input_digest,
            declared_schema=declared_schema,
            failures=failures,
            completed=completed,
            computed_record_digest=computed_record_digest,
        )

    if isinstance(record, dict) and isinstance(record.get("schema_id"), str):
        declared_schema = record["schema_id"]
    if duplicate_key or not isinstance(record, dict):
        failures.add("NONCANONICAL_SERIALIZATION")
    try:
        if canonical_json_bytes(record) != raw_bytes:
            failures.add("NONCANONICAL_SERIALIZATION")
    except (TypeError, ValueError):
        # Domain checks below emit the more specific nonfinite-resource code.
        pass
    completed.append("schema_validation")

    if not isinstance(record, dict):
        completed.append("validation_receipt")
        return _receipt(
            input_digest=input_digest,
            declared_schema=declared_schema,
            failures=failures,
            completed=completed,
            computed_record_digest=computed_record_digest,
        )

    if _contains_forbidden_key(record):
        failures.add("RAW_DATA_LABEL_TARGET_OR_SEQUENCE_BUFFER_PRESENT")

    schema_version = record.get("schema_version")
    if (declared_schema, schema_version) not in registry.schema_versions:
        failures.add("UNKNOWN_SCHEMA_OR_VERSION")

    if declared_schema == ANATOMY_SCHEMA_ID:
        completed.extend(("anatomy_validation", "ledger_validation"))
        computed_record_digest = _validate_anatomy(record, registry, failures)
        completed.append("causal_validation")
    elif declared_schema == MEASUREMENT_SCHEMA_ID:
        completed.extend(("anatomy_validation", "ledger_validation", "causal_validation"))
        computed_record_digest = _validate_measurement(record, registry, failures)
    elif "UNKNOWN_SCHEMA_OR_VERSION" not in failures:
        failures.add("UNKNOWN_SCHEMA_OR_VERSION")

    completed.extend(("digest_validation", "validation_receipt"))
    return _receipt(
        input_digest=input_digest,
        declared_schema=declared_schema,
        failures=failures,
        completed=completed,
        computed_record_digest=computed_record_digest,
    )
