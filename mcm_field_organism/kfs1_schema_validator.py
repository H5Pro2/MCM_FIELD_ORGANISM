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
    "TRANSITION_SCHEMA_ID",
    "TRANSITION_SCHEMA_VERSION",
    "MEASUREMENT_ROLES",
    "PASSIVE_READ_SCOPES",
    "VALIDATION_PHASES",
    "FAILURE_CODES",
    "TRANSITION_FAILURE_CODES",
    "TRANSITION_ALPHABET",
    "KFS1ValidationRegistry",
    "KFS1ValidationReceipt",
    "canonical_json_bytes",
    "sha256_hex",
    "validate_kfs1_record",
    "validate_kfs1_transition_record",
    "build_kfs1_validation_registry",
)


ANATOMY_SCHEMA_ID = "kfs1_anatomy_record"
MEASUREMENT_SCHEMA_ID = "kfs1_measurement_record"
RECORD_SCHEMA_VERSION = "s1my.v1"
RECEIPT_SCHEMA_ID = "kfs1_validation_receipt"
RECEIPT_SCHEMA_VERSION = "s1mz.v1"
TRANSITION_SCHEMA_ID = "kfs1_transition_record"
TRANSITION_SCHEMA_VERSION = "s1nd.v1"

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
TRANSITION_FAILURE_CODES = (
    "ANATOMY_DIGEST_MISMATCH",
    "CAPACITY_CHANGED",
    "EDGE_ID_MISMATCH",
    "EVENT_DIGEST_MISMATCH",
    "EVENT_ORDER_OR_PREDECESSOR_MISMATCH",
    "EXPOSURE_HISTORY_MISSING_OR_MISMATCHED",
    "FIELD_REFERENCE_MISMATCH",
    "FORBIDDEN_TRANSITION_PAYLOAD_PRESENT",
    "INVALID_TRANSFER_AMOUNT",
    "LOCAL_CONSERVATION_MISMATCH",
    "MISSING_OR_UNKNOWN_TRANSITION_FIELD",
    "NONCANONICAL_TRANSITION_SERIALIZATION",
    "POST_LEDGER_INVALID",
    "PRE_LEDGER_INVALID",
    "TRANSITION_ROLE_PAIR_MISMATCH",
    "TRIGGER_BINDING_MISMATCH",
    "UNKNOWN_TRANSITION_ID",
    "UNKNOWN_TRANSITION_SCHEMA_OR_VERSION",
)
TRANSITION_ALPHABET = (
    ("LOCAL_CONTACT_BIND", "free", "bound", "LOCAL_CONTACT_OBSERVATION"),
    ("LOCAL_BOUND_RELEASE", "bound", "free", "LOCAL_BOUND_RELEASE_OBSERVATION"),
    ("LOCAL_REFRACTORY_ENTRY", "bound", "blocked", "LOCAL_BOUND_COMPLETION_OBSERVATION"),
    ("LOCAL_REFRACTORY_RELEASE", "blocked", "free", "LOCAL_BLOCKED_RELEASE_OBSERVATION"),
    ("HOLD_FREE", "free", "free", "NO_TRIGGER"),
    ("HOLD_BOUND", "bound", "bound", "NO_TRIGGER"),
    ("HOLD_BLOCKED", "blocked", "blocked", "NO_TRIGGER"),
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
_TRANSITION_FIELDS = frozenset(
    {
        "schema_id",
        "schema_version",
        "candidate_id",
        "event_id",
        "transition_id",
        "edge_id",
        "field_interval_id",
        "event_ordinal",
        "source_role",
        "target_role",
        "transfer_amount",
        "pre_ledger",
        "post_ledger",
        "anatomy_digest",
        "field_reference_digest",
        "exposure_history_digest",
        "trigger_class",
        "trigger_observation_digest",
        "prior_event_digest",
        "event_digest",
    }
)
_TRANSITION_LEDGER_FIELDS = frozenset(
    {"edge_id", "capacity", "free", "bound", "blocked", "resource_account_digest"}
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
    transition_schema_version: str
    transition_alphabet: tuple[tuple[str, str, str, str], ...]
    transition_trigger_observations: tuple[tuple[str, str, str, str, int, str], ...]
    transition_start_ledger_digests: tuple[str, ...]
    transition_failure_codes: tuple[str, ...]


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
    "kfs1.validator.contract.s1ne.v1"
)


def _static_ledger_digest(free: int, bound: int, blocked: int) -> str:
    return sha256_hex(
        canonical_json_bytes(
            {
                "edge_id": "edge:carrier-a:carrier-b",
                "capacity": 1,
                "free": free,
                "bound": bound,
                "blocked": blocked,
            }
        )
    )


_TRANSITION_TRIGGER_OBSERVATIONS = (
    (
        _fixture_identity("kfs1.trigger.contact.01"),
        "LOCAL_CONTACT_OBSERVATION",
        "edge:carrier-a:carrier-b",
        "interval:contact:01",
        0,
        _FIELD_REFERENCE_DIGEST,
    ),
    (
        _fixture_identity("kfs1.trigger.bound-release.01"),
        "LOCAL_BOUND_RELEASE_OBSERVATION",
        "edge:carrier-a:carrier-b",
        "interval:bound-release:01",
        0,
        _FIELD_REFERENCE_DIGEST,
    ),
    (
        _fixture_identity("kfs1.trigger.bound-completion.01"),
        "LOCAL_BOUND_COMPLETION_OBSERVATION",
        "edge:carrier-a:carrier-b",
        "interval:refractory-entry:01",
        0,
        _FIELD_REFERENCE_DIGEST,
    ),
    (
        _fixture_identity("kfs1.trigger.blocked-release.01"),
        "LOCAL_BLOCKED_RELEASE_OBSERVATION",
        "edge:carrier-a:carrier-b",
        "interval:blocked-release:01",
        0,
        _FIELD_REFERENCE_DIGEST,
    ),
)
_TRANSITION_START_LEDGER_DIGESTS = (
    _static_ledger_digest(1, 0, 0),
    _static_ledger_digest(0, 1, 0),
    _static_ledger_digest(0, 0, 1),
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
        transition_schema_version=TRANSITION_SCHEMA_VERSION,
        transition_alphabet=TRANSITION_ALPHABET,
        transition_trigger_observations=_TRANSITION_TRIGGER_OBSERVATIONS,
        transition_start_ledger_digests=_TRANSITION_START_LEDGER_DIGESTS,
        transition_failure_codes=TRANSITION_FAILURE_CODES,
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


def _transition_fields_complete(
    record: dict[str, Any], failures: set[str]
) -> bool:
    actual = frozenset(record)
    missing = _TRANSITION_FIELDS - actual
    extra = actual - _TRANSITION_FIELDS
    forbidden_extra = extra & _FORBIDDEN_KEYS
    if "exposure_history_digest" in missing:
        failures.add("EXPOSURE_HISTORY_MISSING_OR_MISMATCHED")
        missing = missing - {"exposure_history_digest"}
    if forbidden_extra:
        failures.add("FORBIDDEN_TRANSITION_PAYLOAD_PRESENT")
        extra = extra - forbidden_extra
    if missing or extra:
        failures.add("MISSING_OR_UNKNOWN_TRANSITION_FIELD")
    return actual == _TRANSITION_FIELDS


def _transition_ledger_valid(ledger: Any) -> bool:
    if not isinstance(ledger, dict) or frozenset(ledger) != _TRANSITION_LEDGER_FIELDS:
        return False
    values = tuple(ledger.get(key) for key in ("capacity", "free", "bound", "blocked"))
    if not all(_is_finite_nonnegative(value) for value in values):
        return False
    if values[0] != values[1] + values[2] + values[3]:
        return False
    try:
        expected = _digest_payload(ledger, "resource_account_digest")
    except (TypeError, ValueError):
        return False
    return ledger.get("resource_account_digest") == expected


def _transition_amount_valid(value: Any, hold: bool) -> bool:
    if not _is_finite_nonnegative(value):
        return False
    return value == 0 if hold else value > 0


def _transition_conserved(
    pre: dict[str, Any],
    post: dict[str, Any],
    source_role: str,
    target_role: str,
    amount: int | float,
    hold: bool,
) -> bool:
    if hold:
        return pre == post
    for role in ("free", "bound", "blocked"):
        expected = pre[role]
        if role == source_role:
            expected -= amount
        if role == target_role:
            expected += amount
        if post[role] != expected:
            return False
    return True


def _parse_prior_transition(raw_bytes: bytes) -> dict[str, Any] | None:
    try:
        record, duplicate_key = _parse_record(raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return None
    if duplicate_key or not isinstance(record, dict):
        return None
    try:
        if canonical_json_bytes(record) != raw_bytes:
            return None
    except (TypeError, ValueError):
        return None
    if frozenset(record) != _TRANSITION_FIELDS:
        return None
    try:
        if record.get("event_digest") != _digest_payload(record, "event_digest"):
            return None
    except (TypeError, ValueError):
        return None
    return record


def validate_kfs1_transition_record(
    raw_bytes: bytes,
    registry: KFS1ValidationRegistry,
    prior_raw_bytes: bytes | None = None,
) -> KFS1ValidationReceipt:
    """Validate one static transition record and its optional direct predecessor."""

    if type(raw_bytes) is not bytes:
        raise TypeError("raw_bytes must be bytes")
    if prior_raw_bytes is not None and type(prior_raw_bytes) is not bytes:
        raise TypeError("prior_raw_bytes must be bytes or None")
    _validate_registry(registry)

    input_digest = sha256_hex(raw_bytes)
    failures: set[str] = set()
    completed = ["byte_intake"]
    declared_schema = "unreadable"
    computed_record_digest = "not_computable"

    try:
        record, duplicate_key = _parse_record(raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        failures.add("NONCANONICAL_TRANSITION_SERIALIZATION")
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
        failures.add("NONCANONICAL_TRANSITION_SERIALIZATION")
    try:
        if canonical_json_bytes(record) != raw_bytes:
            failures.add("NONCANONICAL_TRANSITION_SERIALIZATION")
    except (TypeError, ValueError):
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
        failures.add("FORBIDDEN_TRANSITION_PAYLOAD_PRESENT")
    fields_complete = _transition_fields_complete(record, failures)
    if not fields_complete:
        completed.append("validation_receipt")
        return _receipt(
            input_digest=input_digest,
            declared_schema=declared_schema,
            failures=failures,
            completed=completed,
            computed_record_digest=computed_record_digest,
        )

    if (
        declared_schema != TRANSITION_SCHEMA_ID
        or record.get("schema_version") != registry.transition_schema_version
    ):
        failures.add("UNKNOWN_TRANSITION_SCHEMA_OR_VERSION")
    if record.get("candidate_id") != "KFS-1" or not isinstance(record.get("event_id"), str):
        failures.add("MISSING_OR_UNKNOWN_TRANSITION_FIELD")
    if not isinstance(record.get("field_interval_id"), str):
        failures.add("MISSING_OR_UNKNOWN_TRANSITION_FIELD")

    alphabet = {
        transition_id: (source, target, trigger)
        for transition_id, source, target, trigger in registry.transition_alphabet
    }
    transition_id = record.get("transition_id")
    expected = alphabet.get(transition_id)
    if expected is None:
        failures.add("UNKNOWN_TRANSITION_ID")
        completed.extend(("ledger_validation", "causal_validation", "digest_validation", "validation_receipt"))
        return _receipt(
            input_digest=input_digest,
            declared_schema=declared_schema,
            failures=failures,
            completed=completed,
            computed_record_digest=_digest_payload(record, "event_digest"),
        )

    expected_source, expected_target, expected_trigger = expected
    if (record.get("source_role"), record.get("target_role")) != (
        expected_source,
        expected_target,
    ):
        failures.add("TRANSITION_ROLE_PAIR_MISMATCH")
    hold = transition_id.startswith("HOLD_")
    amount = record.get("transfer_amount")
    amount_valid = _transition_amount_valid(amount, hold)
    if not amount_valid:
        failures.add("INVALID_TRANSFER_AMOUNT")

    pre = record.get("pre_ledger")
    post = record.get("post_ledger")
    pre_valid = _transition_ledger_valid(pre)
    post_valid = _transition_ledger_valid(post)
    if not pre_valid:
        failures.add("PRE_LEDGER_INVALID")
    if not post_valid:
        failures.add("POST_LEDGER_INVALID")
    completed.append("ledger_validation")

    edge_matches = pre_valid and post_valid and (
        pre.get("edge_id") == record.get("edge_id") == post.get("edge_id")
    )
    if pre_valid and post_valid and not edge_matches:
        failures.add("EDGE_ID_MISMATCH")
    capacity_matches = pre_valid and post_valid and pre.get("capacity") == post.get("capacity")
    if pre_valid and post_valid and not capacity_matches:
        failures.add("CAPACITY_CHANGED")
    if (
        pre_valid
        and post_valid
        and edge_matches
        and capacity_matches
        and amount_valid
        and "TRANSITION_ROLE_PAIR_MISMATCH" not in failures
        and not _transition_conserved(
            pre, post, expected_source, expected_target, amount, hold
        )
    ):
        failures.add("LOCAL_CONSERVATION_MISMATCH")

    if record.get("field_reference_digest") not in registry.field_reference_digests:
        failures.add("FIELD_REFERENCE_MISMATCH")
    if record.get("anatomy_digest") not in registry.anatomy_digests:
        failures.add("ANATOMY_DIGEST_MISMATCH")
    if record.get("exposure_history_digest") not in registry.exposure_history_digests:
        failures.add("EXPOSURE_HISTORY_MISSING_OR_MISMATCHED")

    trigger_ok = False
    trigger_checkable = hold or (
        "FIELD_REFERENCE_MISMATCH" not in failures and edge_matches
    )
    if hold:
        trigger_ok = (
            record.get("trigger_class") == "NO_TRIGGER"
            and record.get("trigger_observation_digest") is None
        )
    elif trigger_checkable:
        trigger_map = {
            digest: (trigger_class, edge_id, interval_id, ordinal, field_digest)
            for digest, trigger_class, edge_id, interval_id, ordinal, field_digest
            in registry.transition_trigger_observations
        }
        trigger = trigger_map.get(record.get("trigger_observation_digest"))
        event_ordinal = record.get("event_ordinal")
        if trigger is not None:
            trigger_class, trigger_edge, trigger_interval, trigger_ordinal, trigger_field = trigger
            trigger_ok = (
                trigger_class == expected_trigger
                and trigger_edge == record.get("edge_id")
                and trigger_interval == record.get("field_interval_id")
                and trigger_field == record.get("field_reference_digest")
                and isinstance(event_ordinal, int)
                and not isinstance(event_ordinal, bool)
                and trigger_ordinal < event_ordinal
            )
    if trigger_checkable and not trigger_ok:
        failures.add("TRIGGER_BINDING_MISMATCH")
    completed.append("causal_validation")

    event_ordinal = record.get("event_ordinal")
    order_ok = isinstance(event_ordinal, int) and not isinstance(event_ordinal, bool) and event_ordinal > 0
    if prior_raw_bytes is None:
        order_ok = order_ok and event_ordinal == 1 and record.get("prior_event_digest") is None
        if pre_valid:
            order_ok = order_ok and pre.get("resource_account_digest") in registry.transition_start_ledger_digests
    else:
        prior = _parse_prior_transition(prior_raw_bytes)
        order_ok = order_ok and prior is not None
        if prior is not None:
            order_ok = order_ok and event_ordinal == prior.get("event_ordinal") + 1
            order_ok = order_ok and record.get("prior_event_digest") == prior.get("event_digest")
            order_ok = order_ok and pre == prior.get("post_ledger")
            order_ok = order_ok and record.get("event_id") != prior.get("event_id")
            for key in ("edge_id", "anatomy_digest", "field_reference_digest"):
                order_ok = order_ok and record.get(key) == prior.get(key)
    if not order_ok:
        failures.add("EVENT_ORDER_OR_PREDECESSOR_MISMATCH")

    try:
        computed_record_digest = _digest_payload(record, "event_digest")
    except (TypeError, ValueError):
        computed_record_digest = "not_computable"
    if not failures and record.get("event_digest") != computed_record_digest:
        failures.add("EVENT_DIGEST_MISMATCH")
    completed.extend(("digest_validation", "validation_receipt"))
    return _receipt(
        input_digest=input_digest,
        declared_schema=declared_schema,
        failures=failures,
        completed=completed,
        computed_record_digest=computed_record_digest,
    )


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
