"""Pure fail-closed validator for the static G2/D3 anatomy records."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
import math
from typing import Any, Mapping

from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


SCHEMA_ID = "g2_d3_anatomy_record"
SCHEMA_VERSION = "s1np.v1"
RECEIPT_SCHEMA_ID = "g2_d3_validation_receipt"
PAIR_RECEIPT_SCHEMA_ID = "g2_d3_pair_validation_receipt"
RECEIPT_SCHEMA_VERSION = "s1np.v1"
CANDIDATE_CLASS_ID = "G2_CONSERVATIVE_BOUND_SUBPARTITION"
VALIDATION_PHASES = (
    "byte_intake",
    "schema_validation",
    "identity_validation",
    "ledger_validation",
    "projection_validation",
    "digest_validation",
    "pair_validation",
    "validation_receipt",
)
FAILURE_CODES = (
    "D3_ABLATION_MISMATCH",
    "D3_AGGREGATE_PROJECTION_DIGEST_MISMATCH",
    "D3_ANATOMY_RECORD_DIGEST_MISMATCH",
    "D3_C0_FIXTURE_MISMATCH",
    "D3_C1_FIXTURE_MISMATCH",
    "D3_CAPACITY_MISMATCH",
    "D3_CLASS_ID_MISMATCH",
    "D3_EDGE_ID_GEOMETRY_MISMATCH",
    "D3_FIELD_REFERENCE_MISMATCH",
    "D3_FORBIDDEN_PAYLOAD_PRESENT",
    "D3_MISSING_OR_UNKNOWN_FIELD",
    "D3_NEGATIVE_OR_NONFINITE_RESOURCE_ROLE",
    "D3_NONCANONICAL_SERIALIZATION",
    "D3_PAIR_AGGREGATE_MISMATCH",
    "D3_PAIR_IDENTITY_MISMATCH",
    "D3_PAIR_RECORD_INVALID",
    "D3_RESOURCE_ACCOUNT_DIGEST_MISMATCH",
    "D3_UNKNOWN_SCHEMA_OR_VERSION",
)

_FIELDS = frozenset(
    {
        "schema_id",
        "schema_version",
        "candidate_class_id",
        "geometry_digest",
        "field_reference_digest",
        "edge_id",
        "carrier_a_id",
        "carrier_b_id",
        "capacity",
        "free",
        "bound_unconfigured",
        "bound_configured",
        "blocked",
        "aggregate_projection_digest",
        "resource_account_digest",
        "anatomy_record_digest",
    }
)
_FORBIDDEN_KEYS = frozenset(
    {"raw_data", "raw_audio", "raw_video", "label", "labels", "target", "targets", "reward", "sequence_buffer"}
)
_RESOURCE_KEYS = ("capacity", "free", "bound_unconfigured", "bound_configured", "blocked")
_CONTRACT_DIGEST = sha256_hex(b"g2.d3.validator.contract.s1nq.v1")


@dataclass(frozen=True)
class G2D3ValidationRegistry:
    schema_id: str
    schema_version: str
    candidate_class_id: str
    edge_identities: tuple[tuple[str, str, str, str], ...]
    field_reference_digest: str
    validator_contract_digest: str
    validation_phases: tuple[str, ...]
    failure_codes: tuple[str, ...]


@dataclass(frozen=True)
class G2D3ValidationReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    input_bytes_digest: str
    declared_record_schema_id: str
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    computed_resource_account_digest: str
    computed_aggregate_projection_digest: str
    computed_anatomy_record_digest: str
    validator_contract_digest: str
    validation_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        return _dataclass_payload(self)


@dataclass(frozen=True)
class G2D3PairValidationReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    c0_input_bytes_digest: str
    c1_input_bytes_digest: str
    c0_record_digest: str
    c1_record_digest: str
    aggregate_projection_digest: str
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    validator_contract_digest: str
    pair_validation_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        return _dataclass_payload(self)


def _dataclass_payload(value: Any) -> dict[str, Any]:
    payload = {item.name: getattr(value, item.name) for item in fields(value)}
    for key in ("completed_checks", "failure_reasons"):
        if key in payload:
            payload[key] = list(payload[key])
    return payload


def build_g2_d3_validation_registry() -> G2D3ValidationRegistry:
    return G2D3ValidationRegistry(
        schema_id=SCHEMA_ID,
        schema_version=SCHEMA_VERSION,
        candidate_class_id=CANDIDATE_CLASS_ID,
        edge_identities=(
            (
                "26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651",
                "edge:carrier-a:carrier-b",
                "carrier-a",
                "carrier-b",
            ),
            (
                "75e06f6602eeb02fe90bd5aa72b1c67103a6bc4f0c7b2136611f4ef4945fa2f1",
                "edge:carrier-c:carrier-d",
                "carrier-c",
                "carrier-d",
            ),
        ),
        field_reference_digest="8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835",
        validator_contract_digest=_CONTRACT_DIGEST,
        validation_phases=VALIDATION_PHASES,
        failure_codes=FAILURE_CODES,
    )


def _validate_registry(registry: G2D3ValidationRegistry) -> None:
    if type(registry) is not G2D3ValidationRegistry:
        raise TypeError("registry must be G2D3ValidationRegistry")
    if registry != build_g2_d3_validation_registry():
        raise ValueError("registry does not match the bound S1-NQ registry")


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


def _contains_forbidden(value: Any) -> bool:
    if isinstance(value, dict):
        return bool(_FORBIDDEN_KEYS & value.keys()) or any(_contains_forbidden(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden(item) for item in value)
    return False


def _is_resource(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def _digest_without(record: Mapping[str, Any], excluded_key: str) -> str:
    return sha256_hex(canonical_json_bytes({key: value for key, value in record.items() if key != excluded_key}))


def _resource_digest(record: Mapping[str, Any]) -> str:
    return sha256_hex(canonical_json_bytes({key: record[key] for key in ("edge_id",) + _RESOURCE_KEYS}))


def _projection_digest(record: Mapping[str, Any]) -> str:
    return sha256_hex(
        canonical_json_bytes(
            {
                "edge_id": record["edge_id"],
                "capacity": record["capacity"],
                "free": record["free"],
                "bound": record["bound_unconfigured"] + record["bound_configured"],
                "blocked": record["blocked"],
            }
        )
    )


def _record_receipt(
    input_digest: str,
    declared_schema: str,
    failures: set[str],
    completed: list[str],
    resource_digest: str,
    projection_digest: str,
    record_digest: str,
) -> G2D3ValidationReceipt:
    payload = {
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "input_bytes_digest": input_digest,
        "declared_record_schema_id": declared_schema,
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": completed,
        "failure_reasons": sorted(failures),
        "computed_resource_account_digest": resource_digest,
        "computed_aggregate_projection_digest": projection_digest,
        "computed_anatomy_record_digest": record_digest,
        "validator_contract_digest": _CONTRACT_DIGEST,
    }
    digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3ValidationReceipt(
        **{**payload, "completed_checks": tuple(completed), "failure_reasons": tuple(sorted(failures)), "validation_receipt_digest": digest}
    )


def validate_g2_d3_anatomy_record(
    raw_bytes: bytes, registry: G2D3ValidationRegistry
) -> G2D3ValidationReceipt:
    if type(raw_bytes) is not bytes:
        raise TypeError("raw_bytes must be bytes")
    _validate_registry(registry)
    input_digest = sha256_hex(raw_bytes)
    failures: set[str] = set()
    completed = ["byte_intake"]
    declared = "unreadable"
    not_computable = "not_computable"

    try:
        record, duplicate = _parse(raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        failures.add("D3_NONCANONICAL_SERIALIZATION")
        completed.extend(("schema_validation", "validation_receipt"))
        return _record_receipt(input_digest, declared, failures, completed, not_computable, not_computable, not_computable)

    if isinstance(record, dict) and isinstance(record.get("schema_id"), str):
        declared = record["schema_id"]
    canonical = not duplicate and isinstance(record, dict)
    try:
        canonical = canonical and canonical_json_bytes(record) == raw_bytes
    except (TypeError, ValueError):
        canonical = False
        if not isinstance(record, dict) or not all(_is_resource(record.get(key)) for key in _RESOURCE_KEYS):
            canonical = True
    if not canonical:
        failures.add("D3_NONCANONICAL_SERIALIZATION")
    completed.append("schema_validation")
    if not isinstance(record, dict):
        completed.append("validation_receipt")
        return _record_receipt(input_digest, declared, failures, completed, not_computable, not_computable, not_computable)

    forbidden = _contains_forbidden(record)
    if forbidden:
        failures.add("D3_FORBIDDEN_PAYLOAD_PRESENT")
    actual = frozenset(record)
    extra = actual - _FIELDS - _FORBIDDEN_KEYS
    missing = _FIELDS - actual
    structure_ok = not missing and not extra and not forbidden
    if missing or extra:
        failures.add("D3_MISSING_OR_UNKNOWN_FIELD")
    if (record.get("schema_id"), record.get("schema_version")) != (registry.schema_id, registry.schema_version):
        failures.add("D3_UNKNOWN_SCHEMA_OR_VERSION")

    if "candidate_class_id" in record and record.get("candidate_class_id") != registry.candidate_class_id:
        failures.add("D3_CLASS_ID_MISMATCH")
    identity = (record.get("geometry_digest"), record.get("edge_id"), record.get("carrier_a_id"), record.get("carrier_b_id"))
    if identity not in registry.edge_identities:
        failures.add("D3_EDGE_ID_GEOMETRY_MISMATCH")
    if record.get("field_reference_digest") != registry.field_reference_digest:
        failures.add("D3_FIELD_REFERENCE_MISMATCH")
    completed.append("identity_validation")

    resources_ok = structure_ok and all(_is_resource(record.get(key)) for key in _RESOURCE_KEYS)
    if structure_ok and not resources_ok:
        failures.add("D3_NEGATIVE_OR_NONFINITE_RESOURCE_ROLE")
    ledger_ok = resources_ok and record["capacity"] > 0 and record["capacity"] == sum(record[key] for key in _RESOURCE_KEYS[1:])
    if resources_ok and not ledger_ok:
        failures.add("D3_CAPACITY_MISMATCH")
    completed.append("ledger_validation")

    resource_digest = not_computable
    projection_digest = not_computable
    record_digest = not_computable
    identity_ok = not ({"D3_UNKNOWN_SCHEMA_OR_VERSION", "D3_CLASS_ID_MISMATCH", "D3_EDGE_ID_GEOMETRY_MISMATCH", "D3_FIELD_REFERENCE_MISMATCH"} & failures)
    if ledger_ok and identity_ok and "D3_NONCANONICAL_SERIALIZATION" not in failures:
        resource_digest = _resource_digest(record)
        if record.get("resource_account_digest") != resource_digest:
            failures.add("D3_RESOURCE_ACCOUNT_DIGEST_MISMATCH")
        projection_digest = _projection_digest(record)
        if record.get("aggregate_projection_digest") != projection_digest:
            failures.add("D3_AGGREGATE_PROJECTION_DIGEST_MISMATCH")
    completed.append("projection_validation")
    digest_dependencies_ok = not ({"D3_RESOURCE_ACCOUNT_DIGEST_MISMATCH", "D3_AGGREGATE_PROJECTION_DIGEST_MISMATCH"} & failures)
    if ledger_ok and identity_ok and structure_ok and canonical and digest_dependencies_ok:
        record_digest = _digest_without(record, "anatomy_record_digest")
        if record.get("anatomy_record_digest") != record_digest:
            failures.add("D3_ANATOMY_RECORD_DIGEST_MISMATCH")
    completed.extend(("digest_validation", "validation_receipt"))
    return _record_receipt(input_digest, declared, failures, completed, resource_digest, projection_digest, record_digest)


def _pair_receipt(
    c0: G2D3ValidationReceipt,
    c1: G2D3ValidationReceipt,
    failures: set[str],
    aggregate_digest: str,
) -> G2D3PairValidationReceipt:
    completed = ("byte_intake", "schema_validation", "identity_validation", "ledger_validation", "projection_validation", "digest_validation", "pair_validation", "validation_receipt")
    payload = {
        "receipt_schema_id": PAIR_RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "c0_input_bytes_digest": c0.input_bytes_digest,
        "c1_input_bytes_digest": c1.input_bytes_digest,
        "c0_record_digest": c0.computed_anatomy_record_digest,
        "c1_record_digest": c1.computed_anatomy_record_digest,
        "aggregate_projection_digest": aggregate_digest,
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": list(completed),
        "failure_reasons": sorted(failures),
        "validator_contract_digest": _CONTRACT_DIGEST,
    }
    digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3PairValidationReceipt(
        **{**payload, "completed_checks": completed, "failure_reasons": tuple(sorted(failures)), "pair_validation_receipt_digest": digest}
    )


def validate_g2_d3_f1_pair(
    c0_raw_bytes: bytes, c1_raw_bytes: bytes, registry: G2D3ValidationRegistry
) -> G2D3PairValidationReceipt:
    if type(c0_raw_bytes) is not bytes or type(c1_raw_bytes) is not bytes:
        raise TypeError("pair inputs must be bytes")
    _validate_registry(registry)
    c0_receipt = validate_g2_d3_anatomy_record(c0_raw_bytes, registry)
    c1_receipt = validate_g2_d3_anatomy_record(c1_raw_bytes, registry)
    failures: set[str] = set()
    if c0_receipt.validation_status != "valid" or c1_receipt.validation_status != "valid":
        failures.add("D3_PAIR_RECORD_INVALID")
        return _pair_receipt(c0_receipt, c1_receipt, failures, "not_computable")

    c0, _ = _parse(c0_raw_bytes)
    c1, _ = _parse(c1_raw_bytes)
    identity_keys = ("schema_id", "schema_version", "candidate_class_id", "geometry_digest", "field_reference_digest", "edge_id", "carrier_a_id", "carrier_b_id", "capacity")
    if any(c0[key] != c1[key] for key in identity_keys):
        failures.add("D3_PAIR_IDENTITY_MISMATCH")
    c0_roles = tuple(c0[key] for key in ("free", "bound_unconfigured", "bound_configured", "blocked"))
    c1_roles = tuple(c1[key] for key in ("free", "bound_unconfigured", "bound_configured", "blocked"))
    if c0_roles != (0.5, 0.5, 0.0, 0.0):
        failures.add("D3_C0_FIXTURE_MISMATCH")
    if c1_roles != (0.5, 0.0, 0.5, 0.0):
        failures.add("D3_C1_FIXTURE_MISMATCH")
    aggregate = c0["aggregate_projection_digest"] if c0["aggregate_projection_digest"] == c1["aggregate_projection_digest"] else "not_computable"
    if aggregate == "not_computable":
        failures.add("D3_PAIR_AGGREGATE_MISMATCH")
    ablated_c1 = (c1["free"], c1["bound_unconfigured"] + c1["bound_configured"], 0.0, c1["blocked"])
    if ablated_c1 != c0_roles:
        failures.add("D3_ABLATION_MISMATCH")
    return _pair_receipt(c0_receipt, c1_receipt, failures, aggregate)


__all__ = (
    "SCHEMA_ID", "SCHEMA_VERSION", "RECEIPT_SCHEMA_ID", "PAIR_RECEIPT_SCHEMA_ID",
    "RECEIPT_SCHEMA_VERSION", "CANDIDATE_CLASS_ID", "VALIDATION_PHASES", "FAILURE_CODES",
    "G2D3ValidationRegistry", "G2D3ValidationReceipt", "G2D3PairValidationReceipt",
    "build_g2_d3_validation_registry", "validate_g2_d3_anatomy_record", "validate_g2_d3_f1_pair",
)
