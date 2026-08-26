"""Atomic local binding-offer operator for the bounded S1-PJ fixture."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
import math
from typing import Any, Mapping

from .g2_d3_schema_validator import G2D3ValidationRegistry, validate_g2_d3_anatomy_record
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


NOT_COMPUTABLE = "not_computable"
FAILURE_CODES = (
    "PL_PRESTATE_INVALID", "PL_EVENT_PAYLOAD_INVALID", "PL_EQUATION_CONTRACT_INVALID",
    "PL_EVENT_STATE_IDENTITY_MISMATCH", "PL_NONFINITE_OR_NEGATIVE_AMOUNT",
    "PL_POSTSTATE_INVALID", "PL_ATOMIC_COMMIT_FAILED",
)
_PAYLOAD_SCHEMA = "g2_d3_fresh_binding_event_payload"
_PAYLOAD_VERSION = "s1pi.v1"
_EQUATION_SCHEMA = "g2_d3_local_binding_equation_contract"
_EQUATION_VERSION = "s1pj.v1"
_PAYLOAD_DIGEST = "04135ee988060079554b117adf87099d3eeab6d9643ef3b415c05de86a9349da"
_EQUATION_DIGEST = "ae19f42cf9b35e4bfc3429976388c75d01b2128b91b686875edfbd76e46f5ecb"
_FIELD = "8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835"
_EDGE = "edge:carrier-a:carrier-b"
_ALLOWED_PRE_RECORDS = frozenset({
    "d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c",
    "4bd692e489c6c9a217e5790abb0970d279fa367c7024b2119db6342e3f5d66e9",
})
_PHASES = (
    "api_intake", "prestate_validation", "event_validation", "equation_validation",
    "amount_evaluation", "poststate_construction", "poststate_validation",
    "atomic_publication", "receipt",
)
_CONTRACT_DIGEST = sha256_hex(b"g2.d3.local_binding_offer.s1pl.v1")


@dataclass(frozen=True)
class G2D3LocalBindingOfferRegistry:
    payload_digest: str
    equation_contract_digest: str
    allowed_pre_record_digests: tuple[str, ...]
    operator_contract_digest: str
    phases: tuple[str, ...]
    failure_codes: tuple[str, ...]


@dataclass(frozen=True)
class G2D3LocalBindingOfferReceipt:
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    prestate_input_digest: str
    prestate_record_digest: str
    event_payload_input_digest: str
    event_payload_digest: str
    equation_contract_input_digest: str
    equation_contract_digest: str
    poststate_input_digest: str
    poststate_record_digest: str
    commit_amount: float | str
    operator_contract_digest: str
    receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        value = {item.name: getattr(self, item.name) for item in fields(self)}
        value["completed_checks"] = list(self.completed_checks)
        value["failure_reasons"] = list(self.failure_reasons)
        return value


@dataclass(frozen=True)
class G2D3LocalBindingOfferResult:
    poststate_raw_bytes: bytes | str
    commit_amount: float | str
    receipt: G2D3LocalBindingOfferReceipt


def build_g2_d3_local_binding_offer_registry() -> G2D3LocalBindingOfferRegistry:
    return G2D3LocalBindingOfferRegistry(
        payload_digest=_PAYLOAD_DIGEST,
        equation_contract_digest=_EQUATION_DIGEST,
        allowed_pre_record_digests=tuple(sorted(_ALLOWED_PRE_RECORDS)),
        operator_contract_digest=_CONTRACT_DIGEST,
        phases=_PHASES,
        failure_codes=FAILURE_CODES,
    )


def _parse_bound(raw: bytes, own_key: str) -> Mapping[str, Any] | None:
    try:
        value = json.loads(raw)
        if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
            return None
        declared = value.get(own_key)
        payload = {key: item for key, item in value.items() if key != own_key}
        if declared != sha256_hex(canonical_json_bytes(payload)):
            return None
        return value
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        return None


def _anatomy_bytes(pre: Mapping[str, Any], commit: float) -> bytes:
    value = dict(pre)
    value["free"] = pre["free"] - commit
    value["bound_unconfigured"] = pre["bound_unconfigured"] + commit
    value["resource_account_digest"] = sha256_hex(canonical_json_bytes({
        key: value[key] for key in (
            "edge_id", "capacity", "free", "bound_unconfigured", "bound_configured", "blocked"
        )
    }))
    value["aggregate_projection_digest"] = sha256_hex(canonical_json_bytes({
        "edge_id": value["edge_id"], "capacity": value["capacity"], "free": value["free"],
        "bound": value["bound_unconfigured"] + value["bound_configured"], "blocked": value["blocked"],
    }))
    value.pop("anatomy_record_digest", None)
    value["anatomy_record_digest"] = sha256_hex(canonical_json_bytes(value))
    return canonical_json_bytes(value)


def _result(
    failures: set[str], pre_input: str, pre_record: str, event_input: str,
    event_digest: str, equation_input: str, equation_digest: str,
    post_raw: bytes | None, post_record: str, commit: float | None,
) -> G2D3LocalBindingOfferResult:
    payload = {
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": list(_PHASES),
        "failure_reasons": sorted(failures),
        "prestate_input_digest": pre_input,
        "prestate_record_digest": pre_record,
        "event_payload_input_digest": event_input,
        "event_payload_digest": event_digest,
        "equation_contract_input_digest": equation_input,
        "equation_contract_digest": equation_digest,
        "poststate_input_digest": sha256_hex(post_raw) if post_raw is not None else NOT_COMPUTABLE,
        "poststate_record_digest": post_record,
        "commit_amount": commit if commit is not None else NOT_COMPUTABLE,
        "operator_contract_digest": _CONTRACT_DIGEST,
    }
    digest = sha256_hex(canonical_json_bytes(payload))
    receipt = G2D3LocalBindingOfferReceipt(**{
        **payload, "completed_checks": _PHASES, "failure_reasons": tuple(sorted(failures)),
        "receipt_digest": digest,
    })
    return G2D3LocalBindingOfferResult(
        post_raw if not failures and post_raw is not None else NOT_COMPUTABLE,
        commit if not failures and commit is not None else NOT_COMPUTABLE,
        receipt,
    )


def apply_g2_d3_local_binding_offer(
    prestate_raw_bytes: bytes,
    event_payload_raw_bytes: bytes,
    equation_contract_raw_bytes: bytes,
    binding_registry: G2D3LocalBindingOfferRegistry,
    anatomy_registry: G2D3ValidationRegistry,
) -> G2D3LocalBindingOfferResult:
    if any(type(item) is not bytes for item in (
        prestate_raw_bytes, event_payload_raw_bytes, equation_contract_raw_bytes
    )):
        raise TypeError("binding inputs must be bytes")
    if type(binding_registry) is not G2D3LocalBindingOfferRegistry:
        raise TypeError("binding_registry type mismatch")
    if binding_registry != build_g2_d3_local_binding_offer_registry():
        raise ValueError("binding_registry content mismatch")
    if type(anatomy_registry) is not G2D3ValidationRegistry:
        raise TypeError("anatomy_registry type mismatch")

    failures: set[str] = set()
    pre_input = sha256_hex(prestate_raw_bytes)
    event_input = sha256_hex(event_payload_raw_bytes)
    equation_input = sha256_hex(equation_contract_raw_bytes)
    pre_receipt = validate_g2_d3_anatomy_record(prestate_raw_bytes, anatomy_registry)
    pre_record = pre_receipt.computed_anatomy_record_digest
    try:
        pre = json.loads(prestate_raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError):
        pre = None
    if pre_receipt.validation_status != "valid" or pre_record not in _ALLOWED_PRE_RECORDS:
        failures.add("PL_PRESTATE_INVALID")

    event = _parse_bound(event_payload_raw_bytes, "payload_digest")
    event_digest = event.get("payload_digest", NOT_COMPUTABLE) if event else NOT_COMPUTABLE
    if event is None or (event.get("schema_id"), event.get("schema_version")) != (
        _PAYLOAD_SCHEMA, _PAYLOAD_VERSION
    ):
        failures.add("PL_EVENT_PAYLOAD_INVALID")

    equation = _parse_bound(equation_contract_raw_bytes, "equation_contract_digest")
    equation_digest = equation.get("equation_contract_digest", NOT_COMPUTABLE) if equation else NOT_COMPUTABLE
    if equation is None or (equation.get("schema_id"), equation.get("schema_version")) != (
        _EQUATION_SCHEMA, _EQUATION_VERSION
    ) or equation_digest != _EQUATION_DIGEST:
        failures.add("PL_EQUATION_CONTRACT_INVALID")

    if not failures and event is not None and pre is not None:
        if event_digest != _PAYLOAD_DIGEST or event.get("edge_id") != pre.get("edge_id") or event.get(
            "field_reference_digest"
        ) != pre.get("field_reference_digest"):
            failures.add("PL_EVENT_STATE_IDENTITY_MISMATCH")
    if not failures and equation is not None and event is not None:
        if equation.get("event_payload_digest") != event_digest or equation.get("offer_amount") != event.get(
            "offer_amount"
        ):
            failures.add("PL_EQUATION_CONTRACT_INVALID")

    commit: float | None = None
    post_raw: bytes | None = None
    post_record = NOT_COMPUTABLE
    if not failures and pre is not None and event is not None:
        offer = event.get("offer_amount")
        free = pre.get("free")
        if any(
            not isinstance(value, (int, float)) or isinstance(value, bool)
            or not math.isfinite(value) or value < 0.0
            for value in (offer, free)
        ):
            failures.add("PL_NONFINITE_OR_NEGATIVE_AMOUNT")
        else:
            commit = min(float(offer), float(free))
            post_raw = _anatomy_bytes(pre, commit)
            post_receipt = validate_g2_d3_anatomy_record(post_raw, anatomy_registry)
            post_record = post_receipt.computed_anatomy_record_digest
            if post_receipt.validation_status != "valid":
                failures.add("PL_POSTSTATE_INVALID")

    return _result(
        failures, pre_input, pre_record, event_input, event_digest, equation_input,
        equation_digest, post_raw, post_record, commit,
    )


__all__ = (
    "NOT_COMPUTABLE", "FAILURE_CODES", "G2D3LocalBindingOfferRegistry",
    "G2D3LocalBindingOfferReceipt", "G2D3LocalBindingOfferResult",
    "build_g2_d3_local_binding_offer_registry", "apply_g2_d3_local_binding_offer",
)
