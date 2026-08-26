"""Pure fail-closed projection of conservative G2/D3 target bytes."""

from __future__ import annotations

from dataclasses import dataclass, fields
from fractions import Fraction
import json
from typing import Any

from .g2_d3_halving_amount import (
    G2D3HalvingAmountRegistry,
    OPERATOR_CONTRACT_DIGEST as AMOUNT_OPERATOR_CONTRACT_DIGEST,
    evaluate_g2_d3_continuation_halving_amount,
)
from .g2_d3_schema_validator import (
    G2D3ValidationRegistry,
    validate_g2_d3_anatomy_record,
)
from .g2_d3_transient_boundary_validator import G2D3TransientBoundaryRegistry
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


PROJECTION_RECEIPT_SCHEMA_ID = "g2_d3_target_projection_receipt"
PROJECTION_RECEIPT_SCHEMA_VERSION = "s1ok.v1"
PROJECTION_STATUSES = ("NO_CHANGE", "PROJECTED", "not_computable")
PROJECTION_PHASES = (
    "api_intake",
    "amount_evaluation",
    "source_projection",
    "target_construction",
    "target_digest_binding",
    "target_validation",
    "persistence_guard",
    "projection_receipt",
)
PROJECTION_FAILURE_CODES = ("OK_PROJECTION_AMOUNT_EVALUATION_FAILED",)
COMMIT_RECEIPT_SCHEMA_ID = "g2_d3_atomic_commit_receipt"
COMMIT_RECEIPT_SCHEMA_VERSION = "s1ok.v1"
COMMIT_STATUSES = (
    "NO_CHANGE_COMMITTED",
    "PROJECTED_COMMITTED",
    "STALE_SOURCE",
    "not_computable",
)
COMMIT_PHASES = (
    "api_intake",
    "source_projection_recomputation",
    "proposed_target_validation",
    "proposed_target_comparison",
    "current_source_validation",
    "stale_source_gate",
    "atomic_selection",
    "persistence_guard",
    "commit_receipt",
)
COMMIT_FAILURE_CODES = (
    "OK_COMMIT_PROJECTION_RECOMPUTATION_FAILED",
    "OK_COMMIT_PROPOSED_TARGET_INVALID",
    "OK_COMMIT_PROPOSED_TARGET_MISMATCH",
    "OK_COMMIT_CURRENT_SOURCE_INVALID",
    "OK_COMMIT_STALE_SOURCE",
)
BOUNDARY_VALIDATOR_CONTRACT_DIGEST = (
    "7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0"
)
D3_VALIDATOR_CONTRACT_DIGEST = (
    "b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c"
)
PROJECTOR_CONTRACT_DIGEST = (
    "c761d3f5b2dc486ca6cb9389d305e9b2ec8d847812bac72e40d89995a66f6e2b"
)
COMMIT_CONTRACT_DIGEST = (
    "4cae38e9c7986ff6099cfd8c2c742a2c11465bb61a9885441a403fab9b5859b5"
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
class G2D3TargetCommitRegistry:
    projection_receipt_schema_id: str
    projection_receipt_schema_version: str
    projection_statuses: tuple[str, ...]
    projection_phases: tuple[str, ...]
    projection_failure_codes: tuple[str, ...]
    commit_receipt_schema_id: str
    commit_receipt_schema_version: str
    commit_statuses: tuple[str, ...]
    commit_phases: tuple[str, ...]
    commit_failure_codes: tuple[str, ...]
    accepted_amount_operator_contract_digest: str
    accepted_boundary_validator_contract_digest: str
    accepted_d3_validator_contract_digest: str
    projector_contract_digest: str
    commit_contract_digest: str


@dataclass(frozen=True)
class G2D3TargetProjectionReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    boundary_input_bytes_digest: str
    source_d3_input_bytes_digest: str
    formation_enabled: bool
    amount_evaluation_receipt_digest: str
    source_anatomy_record_digest: str
    computed_repartition_amount: Any
    projection_status: str
    target_d3_input_bytes_digest: str
    target_anatomy_record_digest: str
    target_validation_receipt_digest: str
    aggregate_projection_digest: str
    evaluation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    accepted_amount_operator_contract_digest: str
    accepted_boundary_validator_contract_digest: str
    accepted_d3_validator_contract_digest: str
    projector_contract_digest: str
    projection_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        payload["completed_checks"] = list(self.completed_checks)
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


@dataclass(frozen=True)
class G2D3TargetProjectionResult:
    target_d3_raw_bytes: bytes | str
    receipt: G2D3TargetProjectionReceipt


@dataclass(frozen=True)
class G2D3AtomicCommitReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    boundary_input_bytes_digest: str
    source_d3_input_bytes_digest: str
    current_d3_input_bytes_digest: str
    proposed_target_d3_input_bytes_digest: str
    formation_enabled: bool
    recomputed_projection_receipt_digest: str
    source_anatomy_record_digest: str
    current_anatomy_record_digest: str
    expected_target_d3_input_bytes_digest: str
    proposed_target_anatomy_record_digest: str
    commit_status: str
    committed_d3_input_bytes_digest: str
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    accepted_projector_contract_digest: str
    accepted_amount_operator_contract_digest: str
    accepted_boundary_validator_contract_digest: str
    accepted_d3_validator_contract_digest: str
    commit_contract_digest: str
    commit_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        payload["completed_checks"] = list(self.completed_checks)
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


@dataclass(frozen=True)
class G2D3AtomicCommitResult:
    committed_d3_raw_bytes: bytes | str
    receipt: G2D3AtomicCommitReceipt


def build_g2_d3_target_commit_registry() -> G2D3TargetCommitRegistry:
    return G2D3TargetCommitRegistry(
        projection_receipt_schema_id=PROJECTION_RECEIPT_SCHEMA_ID,
        projection_receipt_schema_version=PROJECTION_RECEIPT_SCHEMA_VERSION,
        projection_statuses=PROJECTION_STATUSES,
        projection_phases=PROJECTION_PHASES,
        projection_failure_codes=PROJECTION_FAILURE_CODES,
        commit_receipt_schema_id=COMMIT_RECEIPT_SCHEMA_ID,
        commit_receipt_schema_version=COMMIT_RECEIPT_SCHEMA_VERSION,
        commit_statuses=COMMIT_STATUSES,
        commit_phases=COMMIT_PHASES,
        commit_failure_codes=COMMIT_FAILURE_CODES,
        accepted_amount_operator_contract_digest=AMOUNT_OPERATOR_CONTRACT_DIGEST,
        accepted_boundary_validator_contract_digest=BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
        accepted_d3_validator_contract_digest=D3_VALIDATOR_CONTRACT_DIGEST,
        projector_contract_digest=PROJECTOR_CONTRACT_DIGEST,
        commit_contract_digest=COMMIT_CONTRACT_DIGEST,
    )


def _validate_api(
    boundary_raw_bytes: bytes,
    source_d3_raw_bytes: bytes,
    formation_enabled: bool,
    target_commit_registry: G2D3TargetCommitRegistry,
    amount_registry: G2D3HalvingAmountRegistry,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> None:
    if type(boundary_raw_bytes) is not bytes:
        raise TypeError("boundary_raw_bytes must be bytes")
    if type(source_d3_raw_bytes) is not bytes:
        raise TypeError("source_d3_raw_bytes must be bytes")
    if type(formation_enabled) is not bool:
        raise TypeError("formation_enabled must be bool")
    if type(target_commit_registry) is not G2D3TargetCommitRegistry:
        raise TypeError("target_commit_registry must be G2D3TargetCommitRegistry")
    if target_commit_registry != build_g2_d3_target_commit_registry():
        raise ValueError("target_commit_registry does not match the bound S1-OL registry")
    if type(amount_registry) is not G2D3HalvingAmountRegistry:
        raise TypeError("amount_registry must be G2D3HalvingAmountRegistry")
    if type(boundary_registry) is not G2D3TransientBoundaryRegistry:
        raise TypeError("boundary_registry must be G2D3TransientBoundaryRegistry")
    if type(d3_registry) is not G2D3ValidationRegistry:
        raise TypeError("d3_registry must be G2D3ValidationRegistry")


def _receipt(
    *,
    boundary_input_digest: str,
    source_input_digest: str,
    formation_enabled: bool,
    amount_receipt_digest: str,
    source_record_digest: str,
    amount: Any,
    projection_status: str,
    target_input_digest: str,
    target_record_digest: str,
    target_validation_receipt_digest: str,
    aggregate_projection_digest: str,
    completed: list[str],
    failures: tuple[str, ...],
) -> G2D3TargetProjectionReceipt:
    payload = {
        "receipt_schema_id": PROJECTION_RECEIPT_SCHEMA_ID,
        "receipt_schema_version": PROJECTION_RECEIPT_SCHEMA_VERSION,
        "boundary_input_bytes_digest": boundary_input_digest,
        "source_d3_input_bytes_digest": source_input_digest,
        "formation_enabled": formation_enabled,
        "amount_evaluation_receipt_digest": amount_receipt_digest,
        "source_anatomy_record_digest": source_record_digest,
        "computed_repartition_amount": amount,
        "projection_status": projection_status,
        "target_d3_input_bytes_digest": target_input_digest,
        "target_anatomy_record_digest": target_record_digest,
        "target_validation_receipt_digest": target_validation_receipt_digest,
        "aggregate_projection_digest": aggregate_projection_digest,
        "evaluation_status": "invalid" if failures else "valid",
        "completed_checks": completed,
        "failure_reasons": list(failures),
        "accepted_amount_operator_contract_digest": AMOUNT_OPERATOR_CONTRACT_DIGEST,
        "accepted_boundary_validator_contract_digest": BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
        "accepted_d3_validator_contract_digest": D3_VALIDATOR_CONTRACT_DIGEST,
        "projector_contract_digest": PROJECTOR_CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3TargetProjectionReceipt(
        **{
            **payload,
            "completed_checks": tuple(completed),
            "failure_reasons": failures,
            "projection_receipt_digest": receipt_digest,
        }
    )


def _exact(value: float) -> Fraction:
    return Fraction.from_float(value)


def _resource_digest(record: dict[str, Any]) -> str:
    return sha256_hex(
        canonical_json_bytes(
            {key: record[key] for key in ("edge_id",) + _RESOURCE_KEYS}
        )
    )


def _projection_digest(record: dict[str, Any]) -> str:
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


def _record_digest(record: dict[str, Any]) -> str:
    return sha256_hex(
        canonical_json_bytes(
            {key: value for key, value in record.items() if key != "anatomy_record_digest"}
        )
    )


def _construct_target(source: dict[str, Any], amount: float) -> bytes:
    source_u = source["bound_unconfigured"]
    source_c = source["bound_configured"]
    target_u = source_u - amount
    target_c = source_c + amount
    if (
        _exact(target_u) != _exact(source_u) - _exact(amount)
        or _exact(target_c) != _exact(source_c) + _exact(amount)
    ):
        raise RuntimeError("target representation violates the bound exact projection")

    target = dict(source)
    target["bound_unconfigured"] = target_u
    target["bound_configured"] = target_c
    target["resource_account_digest"] = _resource_digest(target)
    target["aggregate_projection_digest"] = _projection_digest(target)
    target["anatomy_record_digest"] = _record_digest(target)

    source_total = sum((_exact(source[key]) for key in _RESOURCE_KEYS[1:]), Fraction())
    target_total = sum((_exact(target[key]) for key in _RESOURCE_KEYS[1:]), Fraction())
    if source_total != target_total or target_total != _exact(target["capacity"]):
        raise RuntimeError("target violates the bound exact resource identity")
    if target["aggregate_projection_digest"] != source["aggregate_projection_digest"]:
        raise RuntimeError("target changes the bound aggregate projection")
    if target["resource_account_digest"] == source["resource_account_digest"]:
        raise RuntimeError("positive target did not change the resource account digest")
    if target["anatomy_record_digest"] == source["anatomy_record_digest"]:
        raise RuntimeError("positive target did not change the anatomy record digest")
    return canonical_json_bytes(target)


def project_g2_d3_conservative_target(
    boundary_raw_bytes: bytes,
    source_d3_raw_bytes: bytes,
    formation_enabled: bool,
    target_commit_registry: G2D3TargetCommitRegistry,
    amount_registry: G2D3HalvingAmountRegistry,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> G2D3TargetProjectionResult:
    """Return only validated target bytes and a passive projection receipt."""

    _validate_api(
        boundary_raw_bytes,
        source_d3_raw_bytes,
        formation_enabled,
        target_commit_registry,
        amount_registry,
        boundary_registry,
        d3_registry,
    )
    boundary_input_digest = sha256_hex(boundary_raw_bytes)
    source_input_digest = sha256_hex(source_d3_raw_bytes)
    completed = ["api_intake"]
    amount_receipt = evaluate_g2_d3_continuation_halving_amount(
        boundary_raw_bytes,
        source_d3_raw_bytes,
        formation_enabled,
        amount_registry,
        boundary_registry,
        d3_registry,
    )
    completed.append("amount_evaluation")
    if amount_receipt.evaluation_status != "valid":
        completed.extend(("persistence_guard", "projection_receipt"))
        receipt = _receipt(
            boundary_input_digest=boundary_input_digest,
            source_input_digest=source_input_digest,
            formation_enabled=formation_enabled,
            amount_receipt_digest=amount_receipt.amount_evaluation_receipt_digest,
            source_record_digest=_NOT_COMPUTABLE,
            amount=_NOT_COMPUTABLE,
            projection_status=_NOT_COMPUTABLE,
            target_input_digest=_NOT_COMPUTABLE,
            target_record_digest=_NOT_COMPUTABLE,
            target_validation_receipt_digest=_NOT_COMPUTABLE,
            aggregate_projection_digest=_NOT_COMPUTABLE,
            completed=completed,
            failures=("OK_PROJECTION_AMOUNT_EVALUATION_FAILED",),
        )
        return G2D3TargetProjectionResult(_NOT_COMPUTABLE, receipt)

    source = json.loads(source_d3_raw_bytes.decode("utf-8"))
    source_record_digest = source["anatomy_record_digest"]
    amount = amount_receipt.computed_repartition_amount
    completed.append("source_projection")
    if amount == 0.0:
        completed.extend(("persistence_guard", "projection_receipt"))
        receipt = _receipt(
            boundary_input_digest=boundary_input_digest,
            source_input_digest=source_input_digest,
            formation_enabled=formation_enabled,
            amount_receipt_digest=amount_receipt.amount_evaluation_receipt_digest,
            source_record_digest=source_record_digest,
            amount=amount,
            projection_status="NO_CHANGE",
            target_input_digest=source_input_digest,
            target_record_digest=source_record_digest,
            target_validation_receipt_digest=amount_receipt.source_d3_validation_receipt_digest,
            aggregate_projection_digest=source["aggregate_projection_digest"],
            completed=completed,
            failures=(),
        )
        return G2D3TargetProjectionResult(source_d3_raw_bytes, receipt)

    target_raw_bytes = _construct_target(source, amount)
    completed.extend(("target_construction", "target_digest_binding"))
    target_receipt = validate_g2_d3_anatomy_record(target_raw_bytes, d3_registry)
    completed.append("target_validation")
    if target_receipt.validation_status != "valid":
        raise RuntimeError("internally constructed target failed D3 validation")
    target = json.loads(target_raw_bytes.decode("utf-8"))
    completed.extend(("persistence_guard", "projection_receipt"))
    receipt = _receipt(
        boundary_input_digest=boundary_input_digest,
        source_input_digest=source_input_digest,
        formation_enabled=formation_enabled,
        amount_receipt_digest=amount_receipt.amount_evaluation_receipt_digest,
        source_record_digest=source_record_digest,
        amount=amount,
        projection_status="PROJECTED",
        target_input_digest=sha256_hex(target_raw_bytes),
        target_record_digest=target["anatomy_record_digest"],
        target_validation_receipt_digest=target_receipt.validation_receipt_digest,
        aggregate_projection_digest=target["aggregate_projection_digest"],
        completed=completed,
        failures=(),
    )
    return G2D3TargetProjectionResult(target_raw_bytes, receipt)


def _validate_commit_api(
    boundary_raw_bytes: bytes,
    source_d3_raw_bytes: bytes,
    current_d3_raw_bytes: bytes,
    proposed_target_d3_raw_bytes: bytes,
    formation_enabled: bool,
    target_commit_registry: G2D3TargetCommitRegistry,
    amount_registry: G2D3HalvingAmountRegistry,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> None:
    if type(current_d3_raw_bytes) is not bytes:
        raise TypeError("current_d3_raw_bytes must be bytes")
    if type(proposed_target_d3_raw_bytes) is not bytes:
        raise TypeError("proposed_target_d3_raw_bytes must be bytes")
    _validate_api(
        boundary_raw_bytes,
        source_d3_raw_bytes,
        formation_enabled,
        target_commit_registry,
        amount_registry,
        boundary_registry,
        d3_registry,
    )


def _commit_receipt(
    *,
    boundary_input_digest: str,
    source_input_digest: str,
    current_input_digest: str,
    proposed_input_digest: str,
    formation_enabled: bool,
    projection_receipt_digest: str,
    source_record_digest: str,
    current_record_digest: str,
    expected_target_input_digest: str,
    proposed_record_digest: str,
    commit_status: str,
    committed_input_digest: str,
    completed: list[str],
    failures: tuple[str, ...],
) -> G2D3AtomicCommitReceipt:
    payload = {
        "receipt_schema_id": COMMIT_RECEIPT_SCHEMA_ID,
        "receipt_schema_version": COMMIT_RECEIPT_SCHEMA_VERSION,
        "boundary_input_bytes_digest": boundary_input_digest,
        "source_d3_input_bytes_digest": source_input_digest,
        "current_d3_input_bytes_digest": current_input_digest,
        "proposed_target_d3_input_bytes_digest": proposed_input_digest,
        "formation_enabled": formation_enabled,
        "recomputed_projection_receipt_digest": projection_receipt_digest,
        "source_anatomy_record_digest": source_record_digest,
        "current_anatomy_record_digest": current_record_digest,
        "expected_target_d3_input_bytes_digest": expected_target_input_digest,
        "proposed_target_anatomy_record_digest": proposed_record_digest,
        "commit_status": commit_status,
        "committed_d3_input_bytes_digest": committed_input_digest,
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": completed,
        "failure_reasons": list(failures),
        "accepted_projector_contract_digest": PROJECTOR_CONTRACT_DIGEST,
        "accepted_amount_operator_contract_digest": AMOUNT_OPERATOR_CONTRACT_DIGEST,
        "accepted_boundary_validator_contract_digest": BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
        "accepted_d3_validator_contract_digest": D3_VALIDATOR_CONTRACT_DIGEST,
        "commit_contract_digest": COMMIT_CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3AtomicCommitReceipt(
        **{
            **payload,
            "completed_checks": tuple(completed),
            "failure_reasons": failures,
            "commit_receipt_digest": receipt_digest,
        }
    )


def verify_and_commit_g2_d3_projected_target(
    boundary_raw_bytes: bytes,
    source_d3_raw_bytes: bytes,
    current_d3_raw_bytes: bytes,
    proposed_target_d3_raw_bytes: bytes,
    formation_enabled: bool,
    target_commit_registry: G2D3TargetCommitRegistry,
    amount_registry: G2D3HalvingAmountRegistry,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> G2D3AtomicCommitResult:
    """Select complete validated D3 bytes without publishing runtime state."""

    _validate_commit_api(
        boundary_raw_bytes,
        source_d3_raw_bytes,
        current_d3_raw_bytes,
        proposed_target_d3_raw_bytes,
        formation_enabled,
        target_commit_registry,
        amount_registry,
        boundary_registry,
        d3_registry,
    )
    boundary_input_digest = sha256_hex(boundary_raw_bytes)
    source_input_digest = sha256_hex(source_d3_raw_bytes)
    current_input_digest = sha256_hex(current_d3_raw_bytes)
    proposed_input_digest = sha256_hex(proposed_target_d3_raw_bytes)
    completed = ["api_intake"]
    projection_receipt_digest = _NOT_COMPUTABLE
    source_record_digest = _NOT_COMPUTABLE
    current_record_digest = _NOT_COMPUTABLE
    expected_target_input_digest = _NOT_COMPUTABLE
    proposed_record_digest = _NOT_COMPUTABLE

    def fail(code: str, status: str = _NOT_COMPUTABLE) -> G2D3AtomicCommitResult:
        completed.extend(("persistence_guard", "commit_receipt"))
        receipt = _commit_receipt(
            boundary_input_digest=boundary_input_digest,
            source_input_digest=source_input_digest,
            current_input_digest=current_input_digest,
            proposed_input_digest=proposed_input_digest,
            formation_enabled=formation_enabled,
            projection_receipt_digest=projection_receipt_digest,
            source_record_digest=source_record_digest,
            current_record_digest=current_record_digest,
            expected_target_input_digest=expected_target_input_digest,
            proposed_record_digest=proposed_record_digest,
            commit_status=status,
            committed_input_digest=_NOT_COMPUTABLE,
            completed=completed,
            failures=(code,),
        )
        return G2D3AtomicCommitResult(_NOT_COMPUTABLE, receipt)

    projection = project_g2_d3_conservative_target(
        boundary_raw_bytes,
        source_d3_raw_bytes,
        formation_enabled,
        target_commit_registry,
        amount_registry,
        boundary_registry,
        d3_registry,
    )
    completed.append("source_projection_recomputation")
    projection_receipt_digest = projection.receipt.projection_receipt_digest
    source_record_digest = projection.receipt.source_anatomy_record_digest
    if projection.receipt.evaluation_status != "valid":
        return fail("OK_COMMIT_PROJECTION_RECOMPUTATION_FAILED")
    if type(projection.target_d3_raw_bytes) is not bytes:
        raise RuntimeError("valid projection returned no target bytes")
    expected_target_input_digest = sha256_hex(projection.target_d3_raw_bytes)

    proposed_receipt = validate_g2_d3_anatomy_record(
        proposed_target_d3_raw_bytes, d3_registry
    )
    completed.append("proposed_target_validation")
    if proposed_receipt.validation_status != "valid":
        return fail("OK_COMMIT_PROPOSED_TARGET_INVALID")
    proposed_record_digest = proposed_receipt.computed_anatomy_record_digest

    completed.append("proposed_target_comparison")
    if proposed_target_d3_raw_bytes != projection.target_d3_raw_bytes:
        return fail("OK_COMMIT_PROPOSED_TARGET_MISMATCH")

    current_receipt = validate_g2_d3_anatomy_record(current_d3_raw_bytes, d3_registry)
    completed.append("current_source_validation")
    if current_receipt.validation_status != "valid":
        return fail("OK_COMMIT_CURRENT_SOURCE_INVALID")
    current_record_digest = current_receipt.computed_anatomy_record_digest

    completed.append("stale_source_gate")
    if current_record_digest != source_record_digest:
        return fail("OK_COMMIT_STALE_SOURCE", "STALE_SOURCE")

    completed.append("atomic_selection")
    if projection.receipt.projection_status == "NO_CHANGE":
        if (
            projection.target_d3_raw_bytes != source_d3_raw_bytes
            or proposed_target_d3_raw_bytes != source_d3_raw_bytes
            or current_d3_raw_bytes != source_d3_raw_bytes
        ):
            raise RuntimeError("NO_CHANGE selection is not byte-identical to its source")
        selected = current_d3_raw_bytes
        commit_status = "NO_CHANGE_COMMITTED"
    elif projection.receipt.projection_status == "PROJECTED":
        selected = proposed_target_d3_raw_bytes
        commit_status = "PROJECTED_COMMITTED"
    else:
        raise RuntimeError("valid projection returned an unbound projection status")

    completed.extend(("persistence_guard", "commit_receipt"))
    receipt = _commit_receipt(
        boundary_input_digest=boundary_input_digest,
        source_input_digest=source_input_digest,
        current_input_digest=current_input_digest,
        proposed_input_digest=proposed_input_digest,
        formation_enabled=formation_enabled,
        projection_receipt_digest=projection_receipt_digest,
        source_record_digest=source_record_digest,
        current_record_digest=current_record_digest,
        expected_target_input_digest=expected_target_input_digest,
        proposed_record_digest=proposed_record_digest,
        commit_status=commit_status,
        committed_input_digest=sha256_hex(selected),
        completed=completed,
        failures=(),
    )
    return G2D3AtomicCommitResult(selected, receipt)


__all__ = (
    "PROJECTION_RECEIPT_SCHEMA_ID",
    "PROJECTION_RECEIPT_SCHEMA_VERSION",
    "PROJECTION_STATUSES",
    "PROJECTION_PHASES",
    "PROJECTION_FAILURE_CODES",
    "COMMIT_RECEIPT_SCHEMA_ID",
    "COMMIT_RECEIPT_SCHEMA_VERSION",
    "COMMIT_STATUSES",
    "COMMIT_PHASES",
    "COMMIT_FAILURE_CODES",
    "BOUNDARY_VALIDATOR_CONTRACT_DIGEST",
    "D3_VALIDATOR_CONTRACT_DIGEST",
    "PROJECTOR_CONTRACT_DIGEST",
    "COMMIT_CONTRACT_DIGEST",
    "G2D3TargetCommitRegistry",
    "G2D3TargetProjectionReceipt",
    "G2D3TargetProjectionResult",
    "G2D3AtomicCommitReceipt",
    "G2D3AtomicCommitResult",
    "build_g2_d3_target_commit_registry",
    "project_g2_d3_conservative_target",
    "verify_and_commit_g2_d3_projected_target",
)
