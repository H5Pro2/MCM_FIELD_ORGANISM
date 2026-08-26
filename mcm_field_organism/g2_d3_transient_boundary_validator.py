"""Pure validator for transient G2/D3 two-interval boundary records."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
from typing import Any, Mapping

from .g2_d3_schema_validator import (
    G2D3ValidationRegistry,
    validate_g2_d3_anatomy_record,
)
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


SCHEMA_ID = "g2_d3_transient_boundary_record"
SCHEMA_VERSION = "s1oa.v1"
RECEIPT_SCHEMA_ID = "g2_d3_transient_boundary_validation_receipt"
RECEIPT_SCHEMA_VERSION = "s1oa.v1"
CANDIDATE_CLASS_ID = "G2_D3_TRANSIENT_LOCAL_CONTINUATION_GATED_REPARTITION"
ORIENTATIONS = ("X", "Y")
EVENT_ROLES = ("NO_PREDECESSOR", "LOCAL_CONTINUATION", "LOCAL_SWITCH")
VALIDATION_PHASES = (
    "byte_intake",
    "schema_validation",
    "contact_digest_validation",
    "d3_source_validation",
    "adjacency_validation",
    "event_classification",
    "persistence_guard",
    "validation_receipt",
)
FAILURE_CODES = (
    "OA_BOUNDARY_RECORD_DIGEST_MISMATCH",
    "OA_CLASS_ID_MISMATCH",
    "OA_CURRENT_CONTACT_DIGEST_MISMATCH",
    "OA_D3_SOURCE_DIGEST_MISMATCH",
    "OA_D3_SOURCE_RECORD_INVALID",
    "OA_EDGE_OR_FIELD_REFERENCE_MISMATCH",
    "OA_FORBIDDEN_PAYLOAD_PRESENT",
    "OA_INTERVAL_NOT_CLOSED",
    "OA_INVALID_INTERVAL_ORDINAL",
    "OA_MISSING_OR_UNKNOWN_FIELD",
    "OA_NONCANONICAL_SERIALIZATION",
    "OA_PRIOR_CONTACT_DIGEST_MISMATCH",
    "OA_PRIOR_NULLABILITY_MISMATCH",
    "OA_TRANSIENT_PERSISTENCE_FIELD_PRESENT",
    "OA_UNKNOWN_ORIENTATION",
    "OA_UNKNOWN_SCHEMA_OR_VERSION",
)
VALIDATOR_CONTRACT_DIGEST = (
    "7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0"
)
D3_VALIDATOR_CONTRACT_DIGEST = (
    "b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c"
)
_NOT_COMPUTABLE = "not_computable"
_NOT_APPLICABLE = "not_applicable"

_FIELDS = frozenset(
    {
        "schema_id",
        "schema_version",
        "candidate_class_id",
        "current_edge_id",
        "current_field_reference_digest",
        "current_interval_ordinal",
        "current_orientation",
        "current_interval_closed",
        "current_contact_digest",
        "prior_edge_id",
        "prior_field_reference_digest",
        "prior_interval_ordinal",
        "prior_orientation",
        "prior_interval_closed",
        "prior_contact_digest",
        "source_d3_anatomy_record_digest",
        "boundary_record_digest",
    }
)
_PRIOR_FIELDS = (
    "prior_edge_id",
    "prior_field_reference_digest",
    "prior_interval_ordinal",
    "prior_orientation",
    "prior_interval_closed",
    "prior_contact_digest",
)
_PERSISTENCE_KEYS = frozenset(
    {
        "event_role",
        "event_history",
        "history_id",
        "arm_id",
        "sequence",
        "sequence_buffer",
        "continuation_count",
        "switch_count",
        "formation_amount",
        "transfer_amount",
        "post_d3_state",
    }
)
_FORBIDDEN_KEYS = frozenset(
    {"raw_data", "raw_audio", "raw_video", "label", "target", "reward", "readout"}
)


@dataclass(frozen=True)
class G2D3TransientBoundaryRegistry:
    schema_id: str
    schema_version: str
    candidate_class_id: str
    orientations: tuple[str, ...]
    event_roles: tuple[str, ...]
    validation_phases: tuple[str, ...]
    failure_codes: tuple[str, ...]
    d3_validator_contract_digest: str
    validator_contract_digest: str


@dataclass(frozen=True)
class G2D3TransientBoundaryValidationReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    boundary_input_bytes_digest: str
    d3_input_bytes_digest: str
    declared_boundary_schema_id: str
    source_d3_validation_receipt_digest: str
    source_d3_anatomy_record_digest: str
    computed_current_contact_digest: str
    computed_prior_contact_digest: str
    computed_boundary_record_digest: str
    event_role: str
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    validator_contract_digest: str
    boundary_validation_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        payload["completed_checks"] = list(self.completed_checks)
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


def build_g2_d3_transient_boundary_registry() -> G2D3TransientBoundaryRegistry:
    return G2D3TransientBoundaryRegistry(
        schema_id=SCHEMA_ID,
        schema_version=SCHEMA_VERSION,
        candidate_class_id=CANDIDATE_CLASS_ID,
        orientations=ORIENTATIONS,
        event_roles=EVENT_ROLES,
        validation_phases=VALIDATION_PHASES,
        failure_codes=FAILURE_CODES,
        d3_validator_contract_digest=D3_VALIDATOR_CONTRACT_DIGEST,
        validator_contract_digest=VALIDATOR_CONTRACT_DIGEST,
    )


def _validate_registries(
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> None:
    if type(boundary_registry) is not G2D3TransientBoundaryRegistry:
        raise TypeError("boundary_registry must be G2D3TransientBoundaryRegistry")
    if boundary_registry != build_g2_d3_transient_boundary_registry():
        raise ValueError("boundary_registry does not match the bound S1-OB registry")
    if type(d3_registry) is not G2D3ValidationRegistry:
        raise TypeError("d3_registry must be G2D3ValidationRegistry")
    if d3_registry.validator_contract_digest != D3_VALIDATOR_CONTRACT_DIGEST:
        raise ValueError("d3_registry contract digest is not accepted")


def _parse(raw_bytes: bytes) -> tuple[Any, bool]:
    duplicate = False

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        nonlocal duplicate
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                duplicate = True
            result[key] = value
        return result

    return json.loads(raw_bytes.decode("utf-8"), object_pairs_hook=pairs_hook), duplicate


def _contains_key(value: Any, keys: frozenset[str]) -> bool:
    if isinstance(value, dict):
        return bool(keys & value.keys()) or any(_contains_key(item, keys) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, keys) for item in value)
    return False


def _is_ordinal(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _contact_payload(record: Mapping[str, Any], prefix: str) -> dict[str, Any]:
    return {
        "edge_id": record[f"{prefix}_edge_id"],
        "field_reference_digest": record[f"{prefix}_field_reference_digest"],
        "interval_closed": record[f"{prefix}_interval_closed"],
        "interval_ordinal": record[f"{prefix}_interval_ordinal"],
        "orientation": record[f"{prefix}_orientation"],
    }


def _digest_without(record: Mapping[str, Any], excluded_key: str) -> str:
    return sha256_hex(
        canonical_json_bytes({key: value for key, value in record.items() if key != excluded_key})
    )


def _build_receipt(
    *,
    boundary_input_digest: str,
    d3_input_digest: str,
    declared_schema: str,
    d3_receipt_digest: str,
    d3_record_digest: str,
    current_digest: str,
    prior_digest: str,
    boundary_digest: str,
    event_role: str,
    completed: list[str],
    failures: set[str],
) -> G2D3TransientBoundaryValidationReceipt:
    payload = {
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "boundary_input_bytes_digest": boundary_input_digest,
        "d3_input_bytes_digest": d3_input_digest,
        "declared_boundary_schema_id": declared_schema,
        "source_d3_validation_receipt_digest": d3_receipt_digest,
        "source_d3_anatomy_record_digest": d3_record_digest,
        "computed_current_contact_digest": current_digest,
        "computed_prior_contact_digest": prior_digest,
        "computed_boundary_record_digest": boundary_digest,
        "event_role": event_role,
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": completed,
        "failure_reasons": sorted(failures),
        "validator_contract_digest": VALIDATOR_CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3TransientBoundaryValidationReceipt(
        **{
            **payload,
            "completed_checks": tuple(completed),
            "failure_reasons": tuple(sorted(failures)),
            "boundary_validation_receipt_digest": receipt_digest,
        }
    )


def validate_g2_d3_transient_boundary(
    boundary_raw_bytes: bytes,
    d3_raw_bytes: bytes,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> G2D3TransientBoundaryValidationReceipt:
    """Validate and classify one boundary without retaining or mutating it."""

    if type(boundary_raw_bytes) is not bytes:
        raise TypeError("boundary_raw_bytes must be bytes")
    if type(d3_raw_bytes) is not bytes:
        raise TypeError("d3_raw_bytes must be bytes")
    _validate_registries(boundary_registry, d3_registry)

    boundary_input_digest = sha256_hex(boundary_raw_bytes)
    d3_input_digest = sha256_hex(d3_raw_bytes)
    failures: set[str] = set()
    completed = ["byte_intake"]
    declared_schema = "unreadable"
    current_digest = _NOT_COMPUTABLE
    prior_digest = _NOT_COMPUTABLE
    boundary_digest = _NOT_COMPUTABLE
    d3_receipt_digest = _NOT_COMPUTABLE
    d3_record_digest = _NOT_COMPUTABLE
    event_role = _NOT_COMPUTABLE

    try:
        record, duplicate = _parse(boundary_raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        failures.add("OA_NONCANONICAL_SERIALIZATION")
        completed.extend(("schema_validation", "validation_receipt"))
        return _build_receipt(
            boundary_input_digest=boundary_input_digest,
            d3_input_digest=d3_input_digest,
            declared_schema=declared_schema,
            d3_receipt_digest=d3_receipt_digest,
            d3_record_digest=d3_record_digest,
            current_digest=current_digest,
            prior_digest=prior_digest,
            boundary_digest=boundary_digest,
            event_role=event_role,
            completed=completed,
            failures=failures,
        )

    if isinstance(record, dict) and isinstance(record.get("schema_id"), str):
        declared_schema = record["schema_id"]
    canonical = not duplicate and isinstance(record, dict)
    try:
        canonical = canonical and canonical_json_bytes(record) == boundary_raw_bytes
    except (TypeError, ValueError):
        canonical = False
    if not canonical:
        failures.add("OA_NONCANONICAL_SERIALIZATION")
    completed.append("schema_validation")
    if not isinstance(record, dict):
        completed.append("validation_receipt")
        return _build_receipt(
            boundary_input_digest=boundary_input_digest,
            d3_input_digest=d3_input_digest,
            declared_schema=declared_schema,
            d3_receipt_digest=d3_receipt_digest,
            d3_record_digest=d3_record_digest,
            current_digest=current_digest,
            prior_digest=prior_digest,
            boundary_digest=boundary_digest,
            event_role=event_role,
            completed=completed,
            failures=failures,
        )

    persistence_present = _contains_key(record, _PERSISTENCE_KEYS)
    forbidden_present = _contains_key(record, _FORBIDDEN_KEYS)
    if persistence_present:
        failures.add("OA_TRANSIENT_PERSISTENCE_FIELD_PRESENT")
    if forbidden_present:
        failures.add("OA_FORBIDDEN_PAYLOAD_PRESENT")
    actual = frozenset(record)
    exempt_extra = _PERSISTENCE_KEYS | _FORBIDDEN_KEYS
    missing = _FIELDS - actual
    unknown = actual - _FIELDS - exempt_extra
    structure_ok = not missing and not unknown and not persistence_present and not forbidden_present
    if missing or unknown:
        failures.add("OA_MISSING_OR_UNKNOWN_FIELD")
    if (record.get("schema_id"), record.get("schema_version")) != (
        boundary_registry.schema_id,
        boundary_registry.schema_version,
    ):
        failures.add("OA_UNKNOWN_SCHEMA_OR_VERSION")
    if "candidate_class_id" in record and record.get("candidate_class_id") != boundary_registry.candidate_class_id:
        failures.add("OA_CLASS_ID_MISMATCH")

    current_fields_present = all(
        key in record
        for key in (
            "current_edge_id",
            "current_field_reference_digest",
            "current_interval_ordinal",
            "current_orientation",
            "current_interval_closed",
            "current_contact_digest",
        )
    )
    current_digest_computable = current_fields_present
    if current_digest_computable:
        try:
            current_digest = sha256_hex(canonical_json_bytes(_contact_payload(record, "current")))
        except (TypeError, ValueError):
            current_digest = _NOT_COMPUTABLE
    if current_digest != _NOT_COMPUTABLE and record.get("current_contact_digest") != current_digest:
        failures.add("OA_CURRENT_CONTACT_DIGEST_MISMATCH")

    prior_values = [record.get(key, _NOT_COMPUTABLE) for key in _PRIOR_FIELDS]
    all_prior_null = all(value is None for value in prior_values)
    all_prior_present = all(value is not None and value != _NOT_COMPUTABLE for value in prior_values)
    prior_shape_ok = all_prior_null or all_prior_present
    if structure_ok and not prior_shape_ok:
        failures.add("OA_PRIOR_NULLABILITY_MISMATCH")
    if all_prior_null:
        prior_digest = _NOT_APPLICABLE
    elif all_prior_present:
        try:
            prior_digest = sha256_hex(canonical_json_bytes(_contact_payload(record, "prior")))
        except (TypeError, ValueError):
            prior_digest = _NOT_COMPUTABLE
        if prior_digest != _NOT_COMPUTABLE and record.get("prior_contact_digest") != prior_digest:
            failures.add("OA_PRIOR_CONTACT_DIGEST_MISMATCH")
    completed.append("contact_digest_validation")

    current_ordinal = record.get("current_interval_ordinal")
    prior_ordinal = record.get("prior_interval_ordinal")
    ordinal_ok = _is_ordinal(current_ordinal)
    if all_prior_null:
        ordinal_ok = ordinal_ok and current_ordinal == 0
    elif all_prior_present:
        ordinal_ok = ordinal_ok and _is_ordinal(prior_ordinal) and current_ordinal == prior_ordinal + 1
    else:
        ordinal_ok = False
    if structure_ok and prior_shape_ok and not ordinal_ok:
        failures.add("OA_INVALID_INTERVAL_ORDINAL")

    intervals_closed = record.get("current_interval_closed") is True
    if all_prior_present:
        intervals_closed = intervals_closed and record.get("prior_interval_closed") is True
    if structure_ok and prior_shape_ok and not intervals_closed:
        failures.add("OA_INTERVAL_NOT_CLOSED")

    orientations_ok = record.get("current_orientation") in boundary_registry.orientations
    if all_prior_present:
        orientations_ok = orientations_ok and record.get("prior_orientation") in boundary_registry.orientations
    if structure_ok and prior_shape_ok and not orientations_ok:
        failures.add("OA_UNKNOWN_ORIENTATION")

    d3_receipt = validate_g2_d3_anatomy_record(d3_raw_bytes, d3_registry)
    d3_receipt_digest = d3_receipt.validation_receipt_digest
    if d3_receipt.validation_status != "valid":
        failures.add("OA_D3_SOURCE_RECORD_INVALID")
        d3_record = None
    else:
        d3_record_digest = d3_receipt.computed_anatomy_record_digest
        d3_record = json.loads(d3_raw_bytes.decode("utf-8"))
        if record.get("source_d3_anatomy_record_digest") != d3_record_digest:
            failures.add("OA_D3_SOURCE_DIGEST_MISMATCH")
    completed.append("d3_source_validation")

    identity_ok = d3_record is not None and (
        record.get("current_edge_id") == d3_record.get("edge_id")
        and record.get("current_field_reference_digest") == d3_record.get("field_reference_digest")
    )
    if identity_ok and all_prior_present:
        identity_ok = (
            record.get("prior_edge_id") == record.get("current_edge_id")
            and record.get("prior_field_reference_digest") == record.get("current_field_reference_digest")
        )
    if d3_record is not None and structure_ok and prior_shape_ok and not identity_ok:
        failures.add("OA_EDGE_OR_FIELD_REFERENCE_MISMATCH")
    completed.append("adjacency_validation")

    if structure_ok and canonical:
        try:
            boundary_digest = _digest_without(record, "boundary_record_digest")
        except (TypeError, ValueError):
            boundary_digest = _NOT_COMPUTABLE
        if boundary_digest != _NOT_COMPUTABLE and record.get("boundary_record_digest") != boundary_digest:
            failures.add("OA_BOUNDARY_RECORD_DIGEST_MISMATCH")

    if not failures:
        if all_prior_null:
            event_role = "NO_PREDECESSOR"
        elif record["prior_orientation"] == record["current_orientation"]:
            event_role = "LOCAL_CONTINUATION"
        else:
            event_role = "LOCAL_SWITCH"
    completed.extend(("event_classification", "persistence_guard", "validation_receipt"))
    return _build_receipt(
        boundary_input_digest=boundary_input_digest,
        d3_input_digest=d3_input_digest,
        declared_schema=declared_schema,
        d3_receipt_digest=d3_receipt_digest,
        d3_record_digest=d3_record_digest,
        current_digest=current_digest,
        prior_digest=prior_digest,
        boundary_digest=boundary_digest,
        event_role=event_role,
        completed=completed,
        failures=failures,
    )


__all__ = (
    "SCHEMA_ID",
    "SCHEMA_VERSION",
    "RECEIPT_SCHEMA_ID",
    "RECEIPT_SCHEMA_VERSION",
    "CANDIDATE_CLASS_ID",
    "ORIENTATIONS",
    "EVENT_ROLES",
    "VALIDATION_PHASES",
    "FAILURE_CODES",
    "VALIDATOR_CONTRACT_DIGEST",
    "D3_VALIDATOR_CONTRACT_DIGEST",
    "G2D3TransientBoundaryRegistry",
    "G2D3TransientBoundaryValidationReceipt",
    "build_g2_d3_transient_boundary_registry",
    "validate_g2_d3_transient_boundary",
)
