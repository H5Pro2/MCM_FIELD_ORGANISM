"""Pure S1-PJ binding-offer to retention-event adapter."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
from typing import Any, Mapping

from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


NOT_COMPUTABLE = "not_computable"
FAILURE_CODES = (
    "PL_ADAPTER_CONTRACT_INVALID", "PL_ADAPTER_SOURCE_INVALID",
    "PL_ADAPTER_FORBIDDEN_INPUT", "PL_ADAPTER_OUTPUT_MISMATCH",
)
_PAYLOAD_DIGEST = "04135ee988060079554b117adf87099d3eeab6d9643ef3b415c05de86a9349da"
_ADAPTER_DIGEST = "7a42352262636bf6dc851095814a1bc6be35c692eb21300e72a13678f4ae3c75"
_RETENTION_EVENT_RAW = (
    b'{"event_class_id":"G2_D3_FRESH_CONTINUATION",'
    b'"event_schema_id":"g2_d3_model_neutral_continuation_event",'
    b'"event_schema_version":"s1oy.v1"}'
)
_OUTPUT_DIGEST = "dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f"
_FORBIDDEN = frozenset({"arm_id", "free_available_arm_id", "blocked_held_arm_id", "candidate_state"})
_PHASES = ("api_intake", "source_validation", "contract_validation", "projection", "output_validation", "receipt")
_CONTRACT_DIGEST = sha256_hex(b"g2.d3.binding_offer_baseline_adapter.s1pl.v1")


@dataclass(frozen=True)
class G2D3BindingOfferBaselineAdapterRegistry:
    source_payload_digest: str
    adapter_digest: str
    output_digest: str
    contract_digest: str
    phases: tuple[str, ...]
    failure_codes: tuple[str, ...]


@dataclass(frozen=True)
class G2D3BindingOfferBaselineAdapterReceipt:
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    source_input_digest: str
    source_payload_digest: str
    adapter_contract_input_digest: str
    adapter_digest: str
    output_input_digest: str
    contract_digest: str
    receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        value = {item.name: getattr(self, item.name) for item in fields(self)}
        value["completed_checks"] = list(self.completed_checks)
        value["failure_reasons"] = list(self.failure_reasons)
        return value


@dataclass(frozen=True)
class G2D3BindingOfferBaselineAdapterResult:
    retention_event_raw_bytes: bytes | str
    receipt: G2D3BindingOfferBaselineAdapterReceipt


def build_g2_d3_binding_offer_baseline_adapter_registry() -> G2D3BindingOfferBaselineAdapterRegistry:
    return G2D3BindingOfferBaselineAdapterRegistry(
        _PAYLOAD_DIGEST, _ADAPTER_DIGEST, _OUTPUT_DIGEST, _CONTRACT_DIGEST, _PHASES, FAILURE_CODES
    )


def _parse(raw: bytes, key: str) -> Mapping[str, Any] | None:
    try:
        value = json.loads(raw)
        if not isinstance(value, dict) or canonical_json_bytes(value) != raw:
            return None
        declared = value.get(key)
        if declared != sha256_hex(canonical_json_bytes({k: v for k, v in value.items() if k != key})):
            return None
        return value
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        return None


def adapt_g2_d3_binding_offer_to_retention_event(
    event_payload_raw_bytes: bytes,
    adapter_contract_raw_bytes: bytes,
    adapter_registry: G2D3BindingOfferBaselineAdapterRegistry,
) -> G2D3BindingOfferBaselineAdapterResult:
    if type(event_payload_raw_bytes) is not bytes or type(adapter_contract_raw_bytes) is not bytes:
        raise TypeError("adapter inputs must be bytes")
    if type(adapter_registry) is not G2D3BindingOfferBaselineAdapterRegistry:
        raise TypeError("adapter_registry type mismatch")
    if adapter_registry != build_g2_d3_binding_offer_baseline_adapter_registry():
        raise ValueError("adapter_registry content mismatch")
    failures: set[str] = set()
    try:
        source_unchecked = json.loads(event_payload_raw_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError):
        source_unchecked = None
    if isinstance(source_unchecked, dict) and _FORBIDDEN & source_unchecked.keys():
        failures.add("PL_ADAPTER_FORBIDDEN_INPUT")
    source = _parse(event_payload_raw_bytes, "payload_digest")
    source_digest = source.get("payload_digest", NOT_COMPUTABLE) if source else NOT_COMPUTABLE
    if not failures and (source is None or source_digest != _PAYLOAD_DIGEST):
        failures.add("PL_ADAPTER_SOURCE_INVALID")
    contract = _parse(adapter_contract_raw_bytes, "adapter_digest")
    adapter_digest = contract.get("adapter_digest", NOT_COMPUTABLE) if contract else NOT_COMPUTABLE
    if not failures and contract is None:
        failures.add("PL_ADAPTER_CONTRACT_INVALID")
    if not failures and contract is not None and contract.get("source_event_payload_digest") != source_digest:
        failures.add("PL_ADAPTER_SOURCE_INVALID")
    if not failures and adapter_digest != _ADAPTER_DIGEST:
        failures.add("PL_ADAPTER_CONTRACT_INVALID")
    output = _RETENTION_EVENT_RAW if not failures else None
    output_digest = sha256_hex(output) if output is not None else NOT_COMPUTABLE
    if not failures and output_digest != _OUTPUT_DIGEST:
        failures.add("PL_ADAPTER_OUTPUT_MISMATCH")
        output = None
        output_digest = NOT_COMPUTABLE
    payload = {
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": list(_PHASES), "failure_reasons": sorted(failures),
        "source_input_digest": sha256_hex(event_payload_raw_bytes),
        "source_payload_digest": source_digest,
        "adapter_contract_input_digest": sha256_hex(adapter_contract_raw_bytes),
        "adapter_digest": adapter_digest, "output_input_digest": output_digest,
        "contract_digest": _CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    receipt = G2D3BindingOfferBaselineAdapterReceipt(**{
        **payload, "completed_checks": _PHASES, "failure_reasons": tuple(sorted(failures)),
        "receipt_digest": receipt_digest,
    })
    return G2D3BindingOfferBaselineAdapterResult(output if output is not None else NOT_COMPUTABLE, receipt)


__all__ = (
    "NOT_COMPUTABLE", "FAILURE_CODES", "G2D3BindingOfferBaselineAdapterRegistry",
    "G2D3BindingOfferBaselineAdapterReceipt", "G2D3BindingOfferBaselineAdapterResult",
    "build_g2_d3_binding_offer_baseline_adapter_registry",
    "adapt_g2_d3_binding_offer_to_retention_event",
)
