"""Pure validated evaluation of the static G2/D3 O3 admissibility bound."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
from typing import Any

from .g2_d3_schema_validator import (
    G2D3ValidationRegistry,
    validate_g2_d3_anatomy_record,
)
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


RECEIPT_SCHEMA_ID = "g2_d3_admissibility_receipt"
RECEIPT_SCHEMA_VERSION = "s1nv.v1"
FAILURE_CODES = ("D3_ADMISSIBILITY_SOURCE_RECORD_INVALID",)
OPERATOR_CONTRACT_DIGEST = (
    "6f63fcf075a95b6e22ff9cbad9d1326d99478900f6ae613e4cd95da7eacbc756"
)
_NOT_COMPUTABLE = "not_computable"


@dataclass(frozen=True)
class G2D3AdmissibilityReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    input_bytes_digest: str
    source_validation_receipt_digest: str
    source_anatomy_record_digest: str
    free: float | str
    bound_configured: float | str
    local_admissible_engagement: float | str
    evaluation_status: str
    failure_reasons: tuple[str, ...]
    operator_contract_digest: str
    admissibility_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


def _build_receipt(
    *,
    input_bytes_digest: str,
    source_validation_receipt_digest: str,
    source_anatomy_record_digest: str,
    free: float | str,
    bound_configured: float | str,
    local_admissible_engagement: float | str,
    failures: tuple[str, ...],
) -> G2D3AdmissibilityReceipt:
    payload = {
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "input_bytes_digest": input_bytes_digest,
        "source_validation_receipt_digest": source_validation_receipt_digest,
        "source_anatomy_record_digest": source_anatomy_record_digest,
        "free": free,
        "bound_configured": bound_configured,
        "local_admissible_engagement": local_admissible_engagement,
        "evaluation_status": "invalid" if failures else "valid",
        "failure_reasons": list(failures),
        "operator_contract_digest": OPERATOR_CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3AdmissibilityReceipt(
        **{
            **payload,
            "failure_reasons": failures,
            "admissibility_receipt_digest": receipt_digest,
        }
    )


def _local_admissible_engagement(free: float, bound_configured: float) -> float:
    return max(0.0, free - bound_configured)


def evaluate_g2_d3_local_admissible_engagement(
    raw_bytes: bytes,
    registry: G2D3ValidationRegistry,
) -> G2D3AdmissibilityReceipt:
    """Evaluate O3 only after the accepted D3 validator admits the record."""

    source_receipt = validate_g2_d3_anatomy_record(raw_bytes, registry)
    if source_receipt.validation_status != "valid":
        return _build_receipt(
            input_bytes_digest=source_receipt.input_bytes_digest,
            source_validation_receipt_digest=source_receipt.validation_receipt_digest,
            source_anatomy_record_digest=_NOT_COMPUTABLE,
            free=_NOT_COMPUTABLE,
            bound_configured=_NOT_COMPUTABLE,
            local_admissible_engagement=_NOT_COMPUTABLE,
            failures=FAILURE_CODES,
        )

    record = json.loads(raw_bytes.decode("utf-8"))
    free = record["free"]
    bound_configured = record["bound_configured"]
    value = _local_admissible_engagement(free, bound_configured)
    return _build_receipt(
        input_bytes_digest=source_receipt.input_bytes_digest,
        source_validation_receipt_digest=source_receipt.validation_receipt_digest,
        source_anatomy_record_digest=source_receipt.computed_anatomy_record_digest,
        free=free,
        bound_configured=bound_configured,
        local_admissible_engagement=value,
        failures=(),
    )


__all__ = (
    "RECEIPT_SCHEMA_ID",
    "RECEIPT_SCHEMA_VERSION",
    "FAILURE_CODES",
    "OPERATOR_CONTRACT_DIGEST",
    "G2D3AdmissibilityReceipt",
    "evaluate_g2_d3_local_admissible_engagement",
)
