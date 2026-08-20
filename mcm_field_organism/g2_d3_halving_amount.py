"""Pure fail-closed evaluation of the G2/D3 continuation halving amount."""

from __future__ import annotations

from dataclasses import dataclass, fields
from fractions import Fraction
import json
import math
from typing import Any

from .g2_d3_schema_validator import G2D3ValidationRegistry
from .g2_d3_transient_boundary_validator import (
    G2D3TransientBoundaryRegistry,
    validate_g2_d3_transient_boundary,
)
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


RECEIPT_SCHEMA_ID = "g2_d3_halving_amount_evaluation_receipt"
RECEIPT_SCHEMA_VERSION = "s1og.v1"
OPERATOR_CLASS_ID = "G2_D3_CONTINUATION_RESIDUAL_HALVING_AMOUNT"
EVENT_ROLES = ("NO_PREDECESSOR", "LOCAL_CONTINUATION", "LOCAL_SWITCH")
HALVING_NUMERATOR = 1
HALVING_DENOMINATOR = 2
EVALUATION_PHASES = (
    "api_intake",
    "source_boundary_validation",
    "source_d3_projection",
    "null_gate",
    "numeric_domain_validation",
    "halving_evaluation",
    "exact_ledger_preview",
    "persistence_guard",
    "evaluation_receipt",
)
FAILURE_CODES = (
    "OG_EXACT_LEDGER_IDENTITY_MISMATCH",
    "OG_HALVING_INVARIANT_MISMATCH",
    "OG_NUMERIC_DOMAIN_MISMATCH",
    "OG_SOURCE_BOUNDARY_VALIDATION_FAILED",
    "OG_TARGET_REPRESENTATION_MISMATCH",
)
BOUNDARY_VALIDATOR_CONTRACT_DIGEST = (
    "7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0"
)
D3_VALIDATOR_CONTRACT_DIGEST = (
    "b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c"
)
OPERATOR_CONTRACT_DIGEST = (
    "396bd7b9fde4b7ee3b268e1d53245fd2a950cf4d8d9464f084d9b498c17de83b"
)
_NOT_COMPUTABLE = "not_computable"
_RESOURCE_KEYS = (
    "capacity",
    "free",
    "bound_unconfigured",
    "bound_configured",
    "blocked",
)


@dataclass(frozen=True)
class G2D3HalvingAmountRegistry:
    receipt_schema_id: str
    receipt_schema_version: str
    operator_class_id: str
    event_roles: tuple[str, ...]
    halving_numerator: int
    halving_denominator: int
    evaluation_phases: tuple[str, ...]
    failure_codes: tuple[str, ...]
    accepted_boundary_validator_contract_digest: str
    accepted_d3_validator_contract_digest: str
    operator_contract_digest: str


@dataclass(frozen=True)
class G2D3HalvingAmountEvaluationReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    operator_class_id: str
    boundary_input_bytes_digest: str
    d3_input_bytes_digest: str
    formation_enabled: bool
    source_boundary_validation_receipt_digest: str
    source_d3_validation_receipt_digest: str
    source_d3_anatomy_record_digest: str
    source_boundary_record_digest: str
    event_role: str
    source_bound_unconfigured: Any
    source_bound_configured: Any
    halving_numerator: int
    halving_denominator: int
    computed_repartition_amount: Any
    evaluation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    accepted_boundary_validator_contract_digest: str
    accepted_d3_validator_contract_digest: str
    operator_contract_digest: str
    amount_evaluation_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        payload["completed_checks"] = list(self.completed_checks)
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


def build_g2_d3_halving_amount_registry() -> G2D3HalvingAmountRegistry:
    return G2D3HalvingAmountRegistry(
        receipt_schema_id=RECEIPT_SCHEMA_ID,
        receipt_schema_version=RECEIPT_SCHEMA_VERSION,
        operator_class_id=OPERATOR_CLASS_ID,
        event_roles=EVENT_ROLES,
        halving_numerator=HALVING_NUMERATOR,
        halving_denominator=HALVING_DENOMINATOR,
        evaluation_phases=EVALUATION_PHASES,
        failure_codes=FAILURE_CODES,
        accepted_boundary_validator_contract_digest=BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
        accepted_d3_validator_contract_digest=D3_VALIDATOR_CONTRACT_DIGEST,
        operator_contract_digest=OPERATOR_CONTRACT_DIGEST,
    )


def _validate_api(
    boundary_raw_bytes: bytes,
    d3_raw_bytes: bytes,
    formation_enabled: bool,
    amount_registry: G2D3HalvingAmountRegistry,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> None:
    if type(boundary_raw_bytes) is not bytes:
        raise TypeError("boundary_raw_bytes must be bytes")
    if type(d3_raw_bytes) is not bytes:
        raise TypeError("d3_raw_bytes must be bytes")
    if type(formation_enabled) is not bool:
        raise TypeError("formation_enabled must be bool")
    if type(amount_registry) is not G2D3HalvingAmountRegistry:
        raise TypeError("amount_registry must be G2D3HalvingAmountRegistry")
    if amount_registry != build_g2_d3_halving_amount_registry():
        raise ValueError("amount_registry does not match the bound S1-OH registry")
    if type(boundary_registry) is not G2D3TransientBoundaryRegistry:
        raise TypeError("boundary_registry must be G2D3TransientBoundaryRegistry")
    if type(d3_registry) is not G2D3ValidationRegistry:
        raise TypeError("d3_registry must be G2D3ValidationRegistry")


def _build_receipt(
    *,
    boundary_input_digest: str,
    d3_input_digest: str,
    formation_enabled: bool,
    boundary_receipt_digest: str,
    d3_receipt_digest: str,
    d3_record_digest: str,
    boundary_record_digest: str,
    event_role: str,
    source_u: Any,
    source_c: Any,
    amount: Any,
    completed: list[str],
    failures: set[str],
) -> G2D3HalvingAmountEvaluationReceipt:
    payload = {
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "operator_class_id": OPERATOR_CLASS_ID,
        "boundary_input_bytes_digest": boundary_input_digest,
        "d3_input_bytes_digest": d3_input_digest,
        "formation_enabled": formation_enabled,
        "source_boundary_validation_receipt_digest": boundary_receipt_digest,
        "source_d3_validation_receipt_digest": d3_receipt_digest,
        "source_d3_anatomy_record_digest": d3_record_digest,
        "source_boundary_record_digest": boundary_record_digest,
        "event_role": event_role,
        "source_bound_unconfigured": source_u,
        "source_bound_configured": source_c,
        "halving_numerator": HALVING_NUMERATOR,
        "halving_denominator": HALVING_DENOMINATOR,
        "computed_repartition_amount": amount,
        "evaluation_status": "invalid" if failures else "valid",
        "completed_checks": completed,
        "failure_reasons": sorted(failures),
        "accepted_boundary_validator_contract_digest": BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
        "accepted_d3_validator_contract_digest": D3_VALIDATOR_CONTRACT_DIGEST,
        "operator_contract_digest": OPERATOR_CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3HalvingAmountEvaluationReceipt(
        **{
            **payload,
            "completed_checks": tuple(completed),
            "failure_reasons": tuple(sorted(failures)),
            "amount_evaluation_receipt_digest": receipt_digest,
        }
    )


def _exact(value: float) -> Fraction:
    return Fraction.from_float(value)


def evaluate_g2_d3_continuation_halving_amount(
    boundary_raw_bytes: bytes,
    d3_raw_bytes: bytes,
    formation_enabled: bool,
    amount_registry: G2D3HalvingAmountRegistry,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> G2D3HalvingAmountEvaluationReceipt:
    """Evaluate one passive amount without producing a target D3 state."""

    _validate_api(
        boundary_raw_bytes,
        d3_raw_bytes,
        formation_enabled,
        amount_registry,
        boundary_registry,
        d3_registry,
    )
    boundary_input_digest = sha256_hex(boundary_raw_bytes)
    d3_input_digest = sha256_hex(d3_raw_bytes)
    completed = ["api_intake"]
    failures: set[str] = set()
    d3_record_digest = _NOT_COMPUTABLE
    boundary_record_digest = _NOT_COMPUTABLE
    event_role = _NOT_COMPUTABLE
    source_u: Any = _NOT_COMPUTABLE
    source_c: Any = _NOT_COMPUTABLE
    amount: Any = _NOT_COMPUTABLE

    boundary_receipt = validate_g2_d3_transient_boundary(
        boundary_raw_bytes,
        d3_raw_bytes,
        boundary_registry,
        d3_registry,
    )
    boundary_receipt_digest = boundary_receipt.boundary_validation_receipt_digest
    d3_receipt_digest = boundary_receipt.source_d3_validation_receipt_digest
    completed.append("source_boundary_validation")
    if boundary_receipt.validation_status != "valid":
        failures.add("OG_SOURCE_BOUNDARY_VALIDATION_FAILED")
        completed.extend(("persistence_guard", "evaluation_receipt"))
        return _build_receipt(
            boundary_input_digest=boundary_input_digest,
            d3_input_digest=d3_input_digest,
            formation_enabled=formation_enabled,
            boundary_receipt_digest=boundary_receipt_digest,
            d3_receipt_digest=d3_receipt_digest,
            d3_record_digest=d3_record_digest,
            boundary_record_digest=boundary_record_digest,
            event_role=event_role,
            source_u=source_u,
            source_c=source_c,
            amount=amount,
            completed=completed,
            failures=failures,
        )

    d3_record = json.loads(d3_raw_bytes.decode("utf-8"))
    d3_record_digest = boundary_receipt.source_d3_anatomy_record_digest
    boundary_record_digest = boundary_receipt.computed_boundary_record_digest
    event_role = boundary_receipt.event_role
    if event_role not in amount_registry.event_roles:
        raise RuntimeError("valid boundary receipt returned an unbound event role")
    source_u = d3_record["bound_unconfigured"]
    source_c = d3_record["bound_configured"]
    completed.append("source_d3_projection")

    is_null = (
        not formation_enabled
        or event_role in ("NO_PREDECESSOR", "LOCAL_SWITCH")
        or source_u == 0
    )
    completed.append("null_gate")
    if is_null:
        amount = 0.0
        completed.extend(("persistence_guard", "evaluation_receipt"))
        return _build_receipt(
            boundary_input_digest=boundary_input_digest,
            d3_input_digest=d3_input_digest,
            formation_enabled=formation_enabled,
            boundary_receipt_digest=boundary_receipt_digest,
            d3_receipt_digest=d3_receipt_digest,
            d3_record_digest=d3_record_digest,
            boundary_record_digest=boundary_record_digest,
            event_role=event_role,
            source_u=source_u,
            source_c=source_c,
            amount=amount,
            completed=completed,
            failures=failures,
        )

    numeric_domain_ok = all(
        type(d3_record[key]) is float and math.isfinite(d3_record[key])
        for key in _RESOURCE_KEYS
    )
    completed.append("numeric_domain_validation")
    if not numeric_domain_ok:
        failures.add("OG_NUMERIC_DOMAIN_MISMATCH")
    else:
        candidate_amount = source_u * 0.5
        completed.append("halving_evaluation")
        halving_ok = (
            math.isfinite(candidate_amount)
            and 0.0 < candidate_amount < source_u
            and candidate_amount + candidate_amount == source_u
        )
        if not halving_ok:
            failures.add("OG_HALVING_INVARIANT_MISMATCH")
        else:
            preview_u = source_u - candidate_amount
            preview_c = source_c + candidate_amount
            expected_u = _exact(source_u) - _exact(candidate_amount)
            expected_c = _exact(source_c) + _exact(candidate_amount)
            target_representation_ok = (
                math.isfinite(preview_u)
                and math.isfinite(preview_c)
                and preview_u >= 0.0
                and preview_c >= 0.0
                and _exact(preview_u) == expected_u
                and _exact(preview_c) == expected_c
            )
            if not target_representation_ok:
                failures.add("OG_TARGET_REPRESENTATION_MISMATCH")
            else:
                pre_total = sum((_exact(d3_record[key]) for key in _RESOURCE_KEYS[1:]), Fraction())
                post_total = sum(
                    (
                        _exact(d3_record["free"]),
                        _exact(preview_u),
                        _exact(preview_c),
                        _exact(d3_record["blocked"]),
                    ),
                    Fraction(),
                )
                capacity = _exact(d3_record["capacity"])
                if pre_total != capacity or post_total != capacity or pre_total != post_total:
                    failures.add("OG_EXACT_LEDGER_IDENTITY_MISMATCH")
                else:
                    amount = candidate_amount
            completed.append("exact_ledger_preview")

    completed.extend(("persistence_guard", "evaluation_receipt"))
    return _build_receipt(
        boundary_input_digest=boundary_input_digest,
        d3_input_digest=d3_input_digest,
        formation_enabled=formation_enabled,
        boundary_receipt_digest=boundary_receipt_digest,
        d3_receipt_digest=d3_receipt_digest,
        d3_record_digest=d3_record_digest,
        boundary_record_digest=boundary_record_digest,
        event_role=event_role,
        source_u=source_u,
        source_c=source_c,
        amount=amount,
        completed=completed,
        failures=failures,
    )


__all__ = (
    "RECEIPT_SCHEMA_ID",
    "RECEIPT_SCHEMA_VERSION",
    "OPERATOR_CLASS_ID",
    "EVENT_ROLES",
    "HALVING_NUMERATOR",
    "HALVING_DENOMINATOR",
    "EVALUATION_PHASES",
    "FAILURE_CODES",
    "BOUNDARY_VALIDATOR_CONTRACT_DIGEST",
    "D3_VALIDATOR_CONTRACT_DIGEST",
    "OPERATOR_CONTRACT_DIGEST",
    "G2D3HalvingAmountRegistry",
    "G2D3HalvingAmountEvaluationReceipt",
    "build_g2_d3_halving_amount_registry",
    "evaluate_g2_d3_continuation_halving_amount",
)
