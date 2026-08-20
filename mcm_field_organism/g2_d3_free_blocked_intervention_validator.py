"""Passive fail-closed validator for the S1-PE free/blocked fixture."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
import math
from typing import Any, Mapping

from .g2_d3_schema_validator import (
    G2D3ValidationRegistry,
    validate_g2_d3_anatomy_record,
)
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


FIXTURE_SCHEMA_ID = "g2_d3_free_blocked_intervention_fixture"
EVENT_SCHEMA_ID = "g2_d3_fresh_binding_event_identity"
SCHEMA_VERSION = "s1pe.v1"
RECEIPT_SCHEMA_ID = "g2_d3_free_blocked_intervention_validation_receipt"
RECEIPT_SCHEMA_VERSION = "s1pg.v1"
FIXTURE_ID = "S1_PE_G2_D3_FREE_BLOCKED_PAIR_V1"
CAUSAL_SOURCE_ID = "REGISTERED_EXTERNAL_TEST_INTERVENTION"
FREE_AVAILABLE_ARM_ID = "FREE_AVAILABLE"
BLOCKED_HELD_ARM_ID = "BLOCKED_HELD"
FRESH_EVENT_ID = "S1_PE_IDENTICAL_FRESH_BINDING_EVENT_V1"
TRANSFER_AMOUNT = 0.125
VALIDATION_PHASES = (
    "byte_intake",
    "schema_validation",
    "digest_validation",
    "causal_source_validation",
    "anatomy_record_validation",
    "transfer_validation",
    "pair_control_validation",
    "event_identity_validation",
    "metadata_exposure_validation",
    "validation_receipt",
)
FAILURE_CODES = (
    "PE_UNKNOWN_SCHEMA_OR_VERSION",
    "PE_MISSING_OR_UNKNOWN_FIELD",
    "PE_NONCANONICAL_SERIALIZATION",
    "PE_EVENT_IDENTITY_DIGEST_MISMATCH",
    "PE_FIXTURE_DIGEST_MISMATCH",
    "PE_ANATOMY_RECORD_INVALID",
    "PE_EVENT_PAYLOAD_BOUND",
    "PD_INVALID_CAUSAL_SOURCE",
    "PD_INVALID_COMMON_PRESTATE",
    "PD_INVALID_ARM_SET",
    "PD_INVALID_TRANSFER_AMOUNT",
    "PD_INSUFFICIENT_SOURCE_RESOURCE",
    "PD_NON_TARGET_ROLE_CHANGED",
    "PD_PAIR_CONTROL_MISMATCH",
    "PD_LOCAL_CONSERVATION_FAILED",
    "PD_NONFINITE_OR_NEGATIVE_RESOURCE",
    "PD_PARTIAL_COMMIT_ATTEMPT",
    "PD_FORBIDDEN_METADATA_PERSISTENCE",
)

_CONTRACT_DIGEST = "5d91f9c6c5d07cf098bfc9bb9e10131025d2e177795b6ab583b595ad75a244c1"
_NOT_COMPUTABLE = "not_computable"
_ANATOMY_RESOURCE_KEYS = (
    "capacity",
    "free",
    "bound_unconfigured",
    "bound_configured",
    "blocked",
)
_ANATOMY_IDENTITY_KEYS = (
    "schema_id",
    "schema_version",
    "candidate_class_id",
    "geometry_digest",
    "field_reference_digest",
    "edge_id",
    "carrier_a_id",
    "carrier_b_id",
    "capacity",
)
_FORBIDDEN_CANDIDATE_METADATA = frozenset(
    {
        "arm_id",
        "blocked_held_arm_id",
        "causal_source_id",
        "fixture_id",
        "free_available_arm_id",
        "intervention_role",
        "transfer_amount",
    }
)
_EVENT_FIELDS = frozenset(
    {
        "schema_id",
        "schema_version",
        "event_id",
        "event_role",
        "exposure_scope",
        "event_payload_status",
        "event_identity_digest",
    }
)
_FIXTURE_FIELDS = frozenset(
    {
        "schema_id",
        "schema_version",
        "fixture_id",
        "causal_source_id",
        "common_prestate_record_digest",
        "transfer_amount",
        "free_available_arm_id",
        "free_available_post_record_digest",
        "blocked_held_arm_id",
        "blocked_held_post_record_digest",
        "fresh_event_identity_digest",
        "candidate_metadata_exposure",
        "fixture_digest",
    }
)


@dataclass(frozen=True)
class G2D3FreeBlockedInterventionRegistry:
    fixture_schema_id: str
    event_schema_id: str
    schema_version: str
    fixture_id: str
    causal_source_id: str
    free_available_arm_id: str
    blocked_held_arm_id: str
    fresh_event_id: str
    transfer_amount: float
    prestate_input_bytes_digest: str
    free_available_input_bytes_digest: str
    blocked_held_input_bytes_digest: str
    event_identity_input_bytes_digest: str
    fixture_manifest_input_bytes_digest: str
    validator_contract_digest: str
    validation_phases: tuple[str, ...]
    failure_codes: tuple[str, ...]


@dataclass(frozen=True)
class G2D3FreeBlockedInterventionReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    prestate_input_bytes_digest: str
    free_available_input_bytes_digest: str
    blocked_held_input_bytes_digest: str
    event_identity_input_bytes_digest: str
    fixture_manifest_input_bytes_digest: str
    prestate_record_digest: str
    free_available_record_digest: str
    blocked_held_record_digest: str
    event_identity_digest: str
    fixture_digest: str
    validator_contract_digest: str
    validation_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        payload["completed_checks"] = list(self.completed_checks)
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


def build_g2_d3_free_blocked_intervention_registry() -> G2D3FreeBlockedInterventionRegistry:
    return G2D3FreeBlockedInterventionRegistry(
        fixture_schema_id=FIXTURE_SCHEMA_ID,
        event_schema_id=EVENT_SCHEMA_ID,
        schema_version=SCHEMA_VERSION,
        fixture_id=FIXTURE_ID,
        causal_source_id=CAUSAL_SOURCE_ID,
        free_available_arm_id=FREE_AVAILABLE_ARM_ID,
        blocked_held_arm_id=BLOCKED_HELD_ARM_ID,
        fresh_event_id=FRESH_EVENT_ID,
        transfer_amount=TRANSFER_AMOUNT,
        prestate_input_bytes_digest="47e65ce1b4f0a7a42dce13222cfb6e29a91b226c8b9ed479ccd3d9eb3539eff6",
        free_available_input_bytes_digest="2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
        blocked_held_input_bytes_digest="f9a43177383df5f900faf9020f6aa76e10b0898cdf527d21d1f0e2a93bbd4025",
        event_identity_input_bytes_digest="82996574d1de2b09953188332b6a81a6ea549a7406e3a39c0ba31c164b49acf7",
        fixture_manifest_input_bytes_digest="a1af0a6336cd3911f4b3e2cae03e8af0de1a0a3d4cd3a8967dbb9fe33d1650c6",
        validator_contract_digest=_CONTRACT_DIGEST,
        validation_phases=VALIDATION_PHASES,
        failure_codes=FAILURE_CODES,
    )


def _validate_registry(registry: G2D3FreeBlockedInterventionRegistry) -> None:
    if type(registry) is not G2D3FreeBlockedInterventionRegistry:
        raise TypeError("intervention_registry must be G2D3FreeBlockedInterventionRegistry")
    if registry != build_g2_d3_free_blocked_intervention_registry():
        raise ValueError("intervention_registry does not match the bound S1-PF registry")


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


def _parse_external(
    raw_bytes: bytes,
    expected_fields: frozenset[str],
    expected_schema_id: str,
    own_digest_key: str,
    digest_failure: str,
    failures: set[str],
) -> tuple[Mapping[str, Any] | None, str]:
    try:
        value, duplicate = _parse(raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        failures.add("PE_NONCANONICAL_SERIALIZATION")
        return None, _NOT_COMPUTABLE
    if not isinstance(value, dict):
        failures.add("PE_MISSING_OR_UNKNOWN_FIELD")
        return None, _NOT_COMPUTABLE
    try:
        canonical = not duplicate and canonical_json_bytes(value) == raw_bytes
    except (TypeError, ValueError):
        canonical = False
    if not canonical:
        failures.add("PE_NONCANONICAL_SERIALIZATION")
    if frozenset(value) != expected_fields:
        failures.add("PE_MISSING_OR_UNKNOWN_FIELD")
    if (value.get("schema_id"), value.get("schema_version")) != (
        expected_schema_id,
        SCHEMA_VERSION,
    ):
        failures.add("PE_UNKNOWN_SCHEMA_OR_VERSION")
    computed = _NOT_COMPUTABLE
    if frozenset(value) == expected_fields and canonical:
        payload = {key: item for key, item in value.items() if key != own_digest_key}
        try:
            computed = sha256_hex(canonical_json_bytes(payload))
        except (TypeError, ValueError):
            computed = _NOT_COMPUTABLE
        if value.get(own_digest_key) != computed:
            failures.add(digest_failure)
    return value, computed


def _read_anatomy(raw_bytes: bytes) -> Mapping[str, Any] | None:
    try:
        value, duplicate = _parse(raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return None
    return value if isinstance(value, dict) and not duplicate else None


def _is_finite_resource(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0.0
    )


def _build_receipt(
    failures: set[str],
    input_digests: tuple[str, str, str, str, str],
    record_digests: tuple[str, str, str],
    event_digest: str,
    fixture_digest: str,
) -> G2D3FreeBlockedInterventionReceipt:
    payload = {
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": list(VALIDATION_PHASES),
        "failure_reasons": sorted(failures),
        "prestate_input_bytes_digest": input_digests[0],
        "free_available_input_bytes_digest": input_digests[1],
        "blocked_held_input_bytes_digest": input_digests[2],
        "event_identity_input_bytes_digest": input_digests[3],
        "fixture_manifest_input_bytes_digest": input_digests[4],
        "prestate_record_digest": record_digests[0],
        "free_available_record_digest": record_digests[1],
        "blocked_held_record_digest": record_digests[2],
        "event_identity_digest": event_digest,
        "fixture_digest": fixture_digest,
        "validator_contract_digest": _CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3FreeBlockedInterventionReceipt(
        **{
            **payload,
            "completed_checks": VALIDATION_PHASES,
            "failure_reasons": tuple(sorted(failures)),
            "validation_receipt_digest": receipt_digest,
        }
    )


def validate_g2_d3_free_blocked_intervention(
    prestate_raw_bytes: bytes,
    free_available_post_raw_bytes: bytes,
    blocked_held_post_raw_bytes: bytes,
    event_identity_raw_bytes: bytes,
    fixture_manifest_raw_bytes: bytes,
    intervention_registry: G2D3FreeBlockedInterventionRegistry,
    anatomy_registry: G2D3ValidationRegistry,
) -> G2D3FreeBlockedInterventionReceipt:
    raw_inputs = (
        prestate_raw_bytes,
        free_available_post_raw_bytes,
        blocked_held_post_raw_bytes,
        event_identity_raw_bytes,
        fixture_manifest_raw_bytes,
    )
    if any(type(item) is not bytes for item in raw_inputs):
        raise TypeError("all intervention inputs must be bytes")
    _validate_registry(intervention_registry)
    if type(anatomy_registry) is not G2D3ValidationRegistry:
        raise TypeError("anatomy_registry must be G2D3ValidationRegistry")

    failures: set[str] = set()
    input_digests = tuple(sha256_hex(item) for item in raw_inputs)
    event, event_digest = _parse_external(
        event_identity_raw_bytes,
        _EVENT_FIELDS,
        EVENT_SCHEMA_ID,
        "event_identity_digest",
        "PE_EVENT_IDENTITY_DIGEST_MISMATCH",
        failures,
    )
    fixture, fixture_digest = _parse_external(
        fixture_manifest_raw_bytes,
        _FIXTURE_FIELDS,
        FIXTURE_SCHEMA_ID,
        "fixture_digest",
        "PE_FIXTURE_DIGEST_MISMATCH",
        failures,
    )

    anatomy_values = tuple(_read_anatomy(item) for item in raw_inputs[:3])
    semantic_anatomy_failures: set[str] = set()
    for value in anatomy_values:
        if value is None:
            continue
        if _FORBIDDEN_CANDIDATE_METADATA & value.keys():
            semantic_anatomy_failures.add("PD_FORBIDDEN_METADATA_PERSISTENCE")
        if any(not _is_finite_resource(value.get(key)) for key in _ANATOMY_RESOURCE_KEYS):
            semantic_anatomy_failures.add("PD_NONFINITE_OR_NEGATIVE_RESOURCE")
    failures.update(semantic_anatomy_failures)

    anatomy_receipts = tuple(
        validate_g2_d3_anatomy_record(item, anatomy_registry) for item in raw_inputs[:3]
    )
    if any(receipt.validation_status != "valid" for receipt in anatomy_receipts):
        if not semantic_anatomy_failures:
            failures.add("PE_ANATOMY_RECORD_INVALID")
    record_digests = tuple(receipt.computed_anatomy_record_digest for receipt in anatomy_receipts)

    external_gate_clear = not failures and event is not None and fixture is not None
    if external_gate_clear:
        if event.get("event_payload_status") != "UNBOUND":
            failures.add("PE_EVENT_PAYLOAD_BOUND")
        if (
            event.get("event_id") != intervention_registry.fresh_event_id
            or event.get("event_role") != "IDENTICAL_FRESH_LOCAL_BINDING"
            or event.get("exposure_scope") != "CANDIDATE_ARMS_AND_REGISTERED_BASELINES"
            or fixture.get("causal_source_id") != intervention_registry.causal_source_id
        ):
            failures.add("PD_INVALID_CAUSAL_SOURCE")
        if fixture.get("fixture_id") != intervention_registry.fixture_id:
            failures.add("PD_INVALID_CAUSAL_SOURCE")
        if fixture.get("candidate_metadata_exposure") is not False:
            failures.add("PD_FORBIDDEN_METADATA_PERSISTENCE")

    if not failures and fixture is not None and event is not None:
        if fixture.get("common_prestate_record_digest") != record_digests[0]:
            failures.add("PD_INVALID_COMMON_PRESTATE")
        arm_ids = (fixture.get("free_available_arm_id"), fixture.get("blocked_held_arm_id"))
        if arm_ids != (
            intervention_registry.free_available_arm_id,
            intervention_registry.blocked_held_arm_id,
        ) or arm_ids[0] == arm_ids[1]:
            failures.add("PD_INVALID_ARM_SET")
        if (
            fixture.get("free_available_post_record_digest") != record_digests[1]
            or fixture.get("blocked_held_post_record_digest") != record_digests[2]
        ):
            failures.add("PD_INVALID_ARM_SET")
        if fixture.get("fresh_event_identity_digest") != event_digest:
            failures.add("PD_INVALID_CAUSAL_SOURCE")

    amount: float | None = None
    if not failures and fixture is not None:
        raw_amount = fixture.get("transfer_amount")
        if (
            not isinstance(raw_amount, (int, float))
            or isinstance(raw_amount, bool)
            or not math.isfinite(raw_amount)
            or raw_amount <= 0.0
        ):
            failures.add("PD_INVALID_TRANSFER_AMOUNT")
        else:
            amount = float(raw_amount)

    if not failures and amount is not None:
        pre = anatomy_values[0]
        if pre is None or amount > pre["free"] or amount > pre["blocked"]:
            failures.add("PD_INSUFFICIENT_SOURCE_RESOURCE")

    if not failures:
        pre, free_post, blocked_post = anatomy_values
        assert pre is not None and free_post is not None and blocked_post is not None
        non_target_keys = ("capacity", "bound_unconfigured", "bound_configured")
        if any(
            post[key] != pre[key]
            for post in (free_post, blocked_post)
            for key in non_target_keys
        ):
            failures.add("PD_NON_TARGET_ROLE_CHANGED")

    if not failures:
        pre, free_post, blocked_post = anatomy_values
        assert pre is not None and free_post is not None and blocked_post is not None
        if any(
            post[key] != pre[key]
            for post in (free_post, blocked_post)
            for key in _ANATOMY_IDENTITY_KEYS
            if key not in {"capacity"}
        ):
            failures.add("PD_PAIR_CONTROL_MISMATCH")

    if not failures:
        pre, free_post, blocked_post = anatomy_values
        assert pre is not None and free_post is not None and blocked_post is not None
        assert amount is not None
        expected_free = (pre["free"] + amount, pre["blocked"] - amount)
        expected_blocked = (pre["free"] - amount, pre["blocked"] + amount)
        if (free_post["free"], free_post["blocked"]) != expected_free or (
            blocked_post["free"],
            blocked_post["blocked"],
        ) != expected_blocked:
            failures.add("PD_LOCAL_CONSERVATION_FAILED")

    return _build_receipt(
        failures,
        input_digests,
        record_digests,
        event_digest,
        fixture_digest,
    )


__all__ = (
    "FIXTURE_SCHEMA_ID",
    "EVENT_SCHEMA_ID",
    "SCHEMA_VERSION",
    "RECEIPT_SCHEMA_ID",
    "RECEIPT_SCHEMA_VERSION",
    "VALIDATION_PHASES",
    "FAILURE_CODES",
    "G2D3FreeBlockedInterventionRegistry",
    "G2D3FreeBlockedInterventionReceipt",
    "build_g2_d3_free_blocked_intervention_registry",
    "validate_g2_d3_free_blocked_intervention",
)
