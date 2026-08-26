"""Independent static S1-NB input bytes and expected validator outcomes."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from typing import Any


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _identity(label: str) -> str:
    return _sha(label.encode("ascii"))


def _record_digest(record: dict[str, Any], digest_field: str) -> str:
    return _sha(_canonical({key: value for key, value in record.items() if key != digest_field}))


GEOMETRY_DIGEST = _identity("kfs1.geometry.min.01")
FIELD_REFERENCE_DIGEST = _identity("kfs1.field-reference.min.01")
EXPOSURE_HISTORY_DIGEST = _identity("kfs1.exposure-history.min.01")
EDGE_ID = "edge:carrier-a:carrier-b"


def _positive_anatomy() -> dict[str, Any]:
    ledger = {"edge_id": EDGE_ID, "capacity": 1, "free": 1, "bound": 0, "blocked": 0}
    record: dict[str, Any] = {
        "schema_id": "kfs1_anatomy_record",
        "schema_version": "s1my.v1",
        "candidate_id": "KFS-1",
        "geometry_digest": GEOMETRY_DIGEST,
        "carrier_ids": ["carrier-a", "carrier-b"],
        "edge_records": [
            {
                "edge_id": EDGE_ID,
                "carrier_a_id": "carrier-a",
                "carrier_b_id": "carrier-b",
                "capacity": 1,
                "free": 1,
                "bound": 0,
                "blocked": 0,
                "field_reference_digest": FIELD_REFERENCE_DIGEST,
                "resource_account_digest": _sha(_canonical(ledger)),
            }
        ],
    }
    record["anatomy_digest"] = _record_digest(record, "anatomy_digest")
    return record


POSITIVE_ANATOMY = _positive_anatomy()
ANATOMY_DIGEST = POSITIVE_ANATOMY["anatomy_digest"]


def _positive_measurement() -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_id": "kfs1_measurement_record",
        "schema_version": "s1my.v1",
        "measurement_slot_id": "slot:disturbance:01",
        "measurement_role": "disturbance_read",
        "candidate_or_baseline_id": "KFS-1",
        "anatomy_digest": ANATOMY_DIGEST,
        "field_reference_digest": FIELD_REFERENCE_DIGEST,
        "exposure_history_digest": EXPOSURE_HISTORY_DIGEST,
        "read_scope": "read_only",
        "validation_status": "valid",
        "failure_reasons": [],
    }
    record["measurement_record_digest"] = _record_digest(record, "measurement_record_digest")
    return record


POSITIVE_MEASUREMENT = _positive_measurement()


@dataclass(frozen=True)
class FixtureExpectation:
    fixture_id: str
    raw_bytes: bytes
    input_bytes_digest: str
    status: str
    failure_reasons: tuple[str, ...]
    computed_record_digest: str


def _fixture(
    fixture_id: str,
    record: dict[str, Any],
    failure_reasons: tuple[str, ...] = (),
    *,
    raw_bytes: bytes | None = None,
    computable: bool = True,
) -> FixtureExpectation:
    raw = _canonical(record) if raw_bytes is None else raw_bytes
    digest_field = (
        "anatomy_digest"
        if record.get("schema_id") == "kfs1_anatomy_record"
        else "measurement_record_digest"
    )
    computed = _record_digest(record, digest_field) if computable else "not_computable"
    return FixtureExpectation(
        fixture_id=fixture_id,
        raw_bytes=raw,
        input_bytes_digest=_sha(raw),
        status="invalid" if failure_reasons else "valid",
        failure_reasons=tuple(sorted(failure_reasons)),
        computed_record_digest=computed,
    )


def _mutate(base: dict[str, Any], path: tuple[Any, ...], value: Any) -> dict[str, Any]:
    record = deepcopy(base)
    target: Any = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    return record


def _without(base: dict[str, Any], key: str) -> dict[str, Any]:
    record = deepcopy(base)
    del record[key]
    return record


_schema_version = _mutate(POSITIVE_ANATOMY, ("schema_version",), "s1my.v2")
_field_missing = _without(POSITIVE_ANATOMY, "candidate_id")
_field_extra = _mutate(POSITIVE_ANATOMY, ("unknown_field",), "forbidden-by-schema")
_serial_raw = json.dumps(POSITIVE_ANATOMY, ensure_ascii=False, indent=2).encode("utf-8")
_carrier_duplicate = _mutate(POSITIVE_ANATOMY, ("carrier_ids",), ["carrier-a", "carrier-a"])
_edge_geometry = _mutate(POSITIVE_ANATOMY, ("edge_records", 0, "edge_id"), "edge:wrong")
_resource_negative = _mutate(POSITIVE_ANATOMY, ("edge_records", 0, "free"), -1)
_resource_nonfinite = _mutate(POSITIVE_ANATOMY, ("edge_records", 0, "free"), float("inf"))
_resource_nonfinite_raw = _canonical(POSITIVE_ANATOMY).replace(b'"free":1', b'"free":1e999', 1)
_capacity_sum = _mutate(POSITIVE_ANATOMY, ("edge_records", 0, "capacity"), 2)
_resource_duplicate = deepcopy(POSITIVE_ANATOMY)
_resource_duplicate["edge_records"].append(deepcopy(_resource_duplicate["edge_records"][0]))
_resource_duplicate["edge_records"][1]["edge_id"] = "edge:duplicate-resource"
_field_reference = _mutate(POSITIVE_MEASUREMENT, ("field_reference_digest",), _identity("wrong-field"))
_anatomy_reference = _mutate(POSITIVE_MEASUREMENT, ("anatomy_digest",), _identity("wrong-anatomy"))
_exposure_missing = _without(POSITIVE_MEASUREMENT, "exposure_history_digest")
_exposure_mismatch = _mutate(POSITIVE_MEASUREMENT, ("exposure_history_digest",), _identity("wrong-exposure"))
_measurement_role = _mutate(POSITIVE_MEASUREMENT, ("measurement_role",), "active_writer")
_read_scope = _mutate(POSITIVE_MEASUREMENT, ("read_scope",), "read_write")
_forbidden_payload = _mutate(POSITIVE_ANATOMY, ("raw_data",), [1, 2, 3])
_digest = _mutate(POSITIVE_ANATOMY, ("anatomy_digest",), "0" * 64)
_multi_schema_ledger = _mutate(POSITIVE_ANATOMY, ("unknown_field",), "x")
_multi_schema_ledger["edge_records"][0]["capacity"] = 2
_multi_causal_read = _mutate(POSITIVE_MEASUREMENT, ("read_scope",), "read_write")
_multi_causal_read["exposure_history_digest"] = _identity("wrong-exposure")
_unreadable_raw = b'{"schema_id":"kfs1_anatomy_record",'


FIXTURES = (
    _fixture("V_ANATOMY_MIN_01", POSITIVE_ANATOMY),
    _fixture("V_MEASUREMENT_MIN_01", POSITIVE_MEASUREMENT),
    _fixture("I_SCHEMA_VERSION_01", _schema_version, ("UNKNOWN_SCHEMA_OR_VERSION",)),
    _fixture("I_FIELD_MISSING_01", _field_missing, ("MISSING_OR_UNKNOWN_FIELD",), computable=False),
    _fixture("I_FIELD_EXTRA_01", _field_extra, ("MISSING_OR_UNKNOWN_FIELD",), computable=False),
    _fixture("I_SERIALIZATION_01", POSITIVE_ANATOMY, ("NONCANONICAL_SERIALIZATION",), raw_bytes=_serial_raw),
    _fixture("I_CARRIER_DUPLICATE_01", _carrier_duplicate, ("DUPLICATE_CARRIER_OR_EDGE_ID",)),
    _fixture("I_EDGE_GEOMETRY_01", _edge_geometry, ("EDGE_ID_GEOMETRY_MISMATCH",)),
    _fixture("I_RESOURCE_NEGATIVE_01", _resource_negative, ("NEGATIVE_OR_NONFINITE_RESOURCE_ROLE",)),
    _fixture("I_RESOURCE_NONFINITE_01", _resource_nonfinite, ("NEGATIVE_OR_NONFINITE_RESOURCE_ROLE",), raw_bytes=_resource_nonfinite_raw, computable=False),
    _fixture("I_CAPACITY_SUM_01", _capacity_sum, ("RESOURCE_CAPACITY_MISMATCH",)),
    _fixture("I_RESOURCE_DUPLICATE_01", _resource_duplicate, ("RESOURCE_DOUBLE_COUNTING",)),
    _fixture("I_FIELD_REFERENCE_01", _field_reference, ("FIELD_REFERENCE_MISMATCH",)),
    _fixture("I_ANATOMY_DIGEST_01", _anatomy_reference, ("ANATOMY_DIGEST_MISMATCH",)),
    _fixture("I_EXPOSURE_MISSING_01", _exposure_missing, ("EXPOSURE_HISTORY_MISSING_OR_MISMATCHED",), computable=False),
    _fixture("I_EXPOSURE_MISMATCH_01", _exposure_mismatch, ("EXPOSURE_HISTORY_MISSING_OR_MISMATCHED",)),
    _fixture("I_MEASUREMENT_ROLE_01", _measurement_role, ("UNREGISTERED_MEASUREMENT_ROLE",)),
    _fixture("I_READ_SCOPE_01", _read_scope, ("READ_SCOPE_NOT_PASSIVE",)),
    _fixture("I_FORBIDDEN_PAYLOAD_01", _forbidden_payload, ("RAW_DATA_LABEL_TARGET_OR_SEQUENCE_BUFFER_PRESENT",), computable=False),
    _fixture("I_DIGEST_01", _digest, ("DIGEST_MISMATCH",)),
    _fixture("I_MULTI_SCHEMA_LEDGER_01", _multi_schema_ledger, ("MISSING_OR_UNKNOWN_FIELD", "RESOURCE_CAPACITY_MISMATCH"), computable=False),
    _fixture("I_MULTI_CAUSAL_READ_01", _multi_causal_read, ("EXPOSURE_HISTORY_MISSING_OR_MISMATCHED", "READ_SCOPE_NOT_PASSIVE")),
    _fixture("I_MULTI_UNREADABLE_01", {}, ("NONCANONICAL_SERIALIZATION",), raw_bytes=_unreadable_raw, computable=False),
)

FIXTURE_EXPECTATIONS = {fixture.fixture_id: fixture for fixture in FIXTURES}

assert len(FIXTURES) == 23
assert len(FIXTURE_EXPECTATIONS) == 23
