"""Pure read-only O3 checkpoints over one validated G2/D3 two-step trace."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from .g2_d3_admissibility import (
    OPERATOR_CONTRACT_DIGEST as O3_OPERATOR_CONTRACT_DIGEST,
    evaluate_g2_d3_local_admissible_engagement,
)
from .g2_d3_halving_amount import (
    G2D3HalvingAmountRegistry,
    OPERATOR_CONTRACT_DIGEST as AMOUNT_OPERATOR_CONTRACT_DIGEST,
)
from .g2_d3_schema_validator import G2D3ValidationRegistry
from .g2_d3_target_projection import (
    COMMIT_CONTRACT_DIGEST,
    PROJECTOR_CONTRACT_DIGEST,
    G2D3TargetCommitRegistry,
)
from .g2_d3_transient_boundary_validator import (
    D3_VALIDATOR_CONTRACT_DIGEST,
    VALIDATOR_CONTRACT_DIGEST as BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
    G2D3TransientBoundaryRegistry,
)
from .g2_d3_two_step_composition import (
    COMPOSITION_CONTRACT_DIGEST,
    G2D3TwoStepCompositionRegistry,
    _execute_g2_d3_two_step,
)
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


RECEIPT_SCHEMA_ID = "g2_d3_two_step_o3_checkpoint_receipt"
RECEIPT_SCHEMA_VERSION = "s1ou.v1"
CHECKPOINT_CLASS_ID = "G2_D3_TWO_STEP_THREE_READ_ONLY_O3_CHECKPOINTS"
CHECKPOINT_ROLES = ("CP0_INITIAL", "CP1_INTERMEDIATE", "CP2_FINAL")
CHECKPOINT_STATUSES = ("THREE_CHECKPOINTS_EVALUATED", "not_computable")
CHECKPOINT_PHASES = (
    "api_intake",
    "two_step_execution",
    "composition_validation",
    "cp0_evaluation",
    "cp1_evaluation",
    "cp2_evaluation",
    "checkpoint_identity_gate",
    "component_evaluation",
    "persistence_guard",
    "checkpoint_receipt",
)
FAILURE_CODES = (
    "OU_TWO_STEP_EXECUTION_FAILED",
    "OU_COMPOSITION_IDENTITY_MISMATCH",
    "OU_CP0_EVALUATION_FAILED",
    "OU_CP1_EVALUATION_FAILED",
    "OU_CP2_EVALUATION_FAILED",
    "OU_CHECKPOINT_IDENTITY_MISMATCH",
    "OU_COMPONENT_IDENTITY_MISMATCH",
)
CHECKPOINT_CONTRACT_DIGEST = (
    "582e0fa653c8843cb56e848abc1ea34b1e97b455f8b0a130f22678afb555191f"
)
COMPARISON_DIGEST = (
    "5c8d3b60bbc205594974f632a878472bf628426dc914af72514cf7b42e8a86a5"
)
_NOT_COMPUTABLE = "not_computable"


@dataclass(frozen=True)
class G2D3TwoStepO3CheckpointRecord:
    checkpoint_role: str
    checkpoint_position: int
    d3_input_bytes_digest: str
    anatomy_record_digest: str
    expected_o3_value: float


@dataclass(frozen=True)
class G2D3TwoStepO3CheckpointRegistry:
    receipt_schema_id: str
    receipt_schema_version: str
    checkpoint_class_id: str
    checkpoint_roles: tuple[str, ...]
    checkpoint_statuses: tuple[str, ...]
    checkpoint_phases: tuple[str, ...]
    failure_codes: tuple[str, ...]
    checkpoint_records: tuple[G2D3TwoStepO3CheckpointRecord, ...]
    accepted_composition_contract_digest: str
    accepted_o3_operator_contract_digest: str
    accepted_projector_contract_digest: str
    accepted_commit_contract_digest: str
    accepted_amount_operator_contract_digest: str
    accepted_boundary_validator_contract_digest: str
    accepted_d3_validator_contract_digest: str
    checkpoint_contract_digest: str


@dataclass(frozen=True)
class G2D3TwoStepO3CheckpointReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    checkpoint_class_id: str
    first_boundary_input_bytes_digest: str
    second_boundary_input_bytes_digest: str
    initial_d3_input_bytes_digest: str
    formation_enabled: bool
    chain_role: str
    composition_receipt_digest: str
    cp0_d3_input_bytes_digest: str
    cp0_anatomy_record_digest: str
    cp0_o3_receipt_digest: str
    cp0_value: float | str
    cp1_d3_input_bytes_digest: str
    cp1_anatomy_record_digest: str
    cp1_o3_receipt_digest: str
    cp1_value: float | str
    cp2_d3_input_bytes_digest: str
    cp2_anatomy_record_digest: str
    cp2_o3_receipt_digest: str
    cp2_value: float | str
    delta_cp1_cp0: float | str
    delta_cp2_cp1: float | str
    delta_cp2_cp0: float | str
    comparison_digest: str
    checkpoint_status: str
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    accepted_composition_contract_digest: str
    accepted_o3_operator_contract_digest: str
    accepted_projector_contract_digest: str
    accepted_commit_contract_digest: str
    accepted_amount_operator_contract_digest: str
    accepted_boundary_validator_contract_digest: str
    accepted_d3_validator_contract_digest: str
    checkpoint_contract_digest: str
    checkpoint_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        payload["completed_checks"] = list(self.completed_checks)
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


@dataclass(frozen=True)
class G2D3TwoStepO3CheckpointResult:
    checkpoint_values: tuple[float, float, float] | str
    receipt: G2D3TwoStepO3CheckpointReceipt


def build_g2_d3_two_step_o3_checkpoint_registry() -> G2D3TwoStepO3CheckpointRegistry:
    records = (
        G2D3TwoStepO3CheckpointRecord(
            "CP0_INITIAL",
            0,
            "d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
            "1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f",
            0.5,
        ),
        G2D3TwoStepO3CheckpointRecord(
            "CP1_INTERMEDIATE",
            1,
            "2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
            "d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c",
            0.25,
        ),
        G2D3TwoStepO3CheckpointRecord(
            "CP2_FINAL",
            2,
            "a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab",
            "efba6284b3e56cfe2041465eb8acc76b00de34ee8303f6a2caa20b2a3fc66681",
            0.125,
        ),
    )
    return G2D3TwoStepO3CheckpointRegistry(
        receipt_schema_id=RECEIPT_SCHEMA_ID,
        receipt_schema_version=RECEIPT_SCHEMA_VERSION,
        checkpoint_class_id=CHECKPOINT_CLASS_ID,
        checkpoint_roles=CHECKPOINT_ROLES,
        checkpoint_statuses=CHECKPOINT_STATUSES,
        checkpoint_phases=CHECKPOINT_PHASES,
        failure_codes=FAILURE_CODES,
        checkpoint_records=records,
        accepted_composition_contract_digest=COMPOSITION_CONTRACT_DIGEST,
        accepted_o3_operator_contract_digest=O3_OPERATOR_CONTRACT_DIGEST,
        accepted_projector_contract_digest=PROJECTOR_CONTRACT_DIGEST,
        accepted_commit_contract_digest=COMMIT_CONTRACT_DIGEST,
        accepted_amount_operator_contract_digest=AMOUNT_OPERATOR_CONTRACT_DIGEST,
        accepted_boundary_validator_contract_digest=BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
        accepted_d3_validator_contract_digest=D3_VALIDATOR_CONTRACT_DIGEST,
        checkpoint_contract_digest=CHECKPOINT_CONTRACT_DIGEST,
    )


def _validate_checkpoint_api(
    first_boundary_raw_bytes: bytes,
    second_boundary_raw_bytes: bytes,
    initial_d3_raw_bytes: bytes,
    formation_enabled: bool,
    checkpoint_registry: G2D3TwoStepO3CheckpointRegistry,
) -> None:
    if type(first_boundary_raw_bytes) is not bytes:
        raise TypeError("first_boundary_raw_bytes must be bytes")
    if type(second_boundary_raw_bytes) is not bytes:
        raise TypeError("second_boundary_raw_bytes must be bytes")
    if type(initial_d3_raw_bytes) is not bytes:
        raise TypeError("initial_d3_raw_bytes must be bytes")
    if type(formation_enabled) is not bool:
        raise TypeError("formation_enabled must be bool")
    if type(checkpoint_registry) is not G2D3TwoStepO3CheckpointRegistry:
        raise TypeError("checkpoint_registry must be G2D3TwoStepO3CheckpointRegistry")
    if checkpoint_registry != build_g2_d3_two_step_o3_checkpoint_registry():
        raise ValueError("checkpoint_registry does not match the bound S1-OU registry")


def _build_checkpoint_receipt(
    *,
    first_boundary_digest: str,
    second_boundary_digest: str,
    initial_d3_digest: str,
    formation_enabled: bool,
    chain_role: str,
    composition_receipt_digest: str,
    checkpoint_digests: tuple[str, str, str],
    checkpoint_record_digests: tuple[str, str, str],
    o3_receipt_digests: tuple[str, str, str],
    values: tuple[float, float, float] | None,
    components: tuple[float, float, float] | None,
    comparison_digest: str,
    status: str,
    completed: list[str],
    failures: tuple[str, ...],
) -> G2D3TwoStepO3CheckpointReceipt:
    public_values = values or (_NOT_COMPUTABLE,) * 3
    public_components = components or (_NOT_COMPUTABLE,) * 3
    payload = {
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "checkpoint_class_id": CHECKPOINT_CLASS_ID,
        "first_boundary_input_bytes_digest": first_boundary_digest,
        "second_boundary_input_bytes_digest": second_boundary_digest,
        "initial_d3_input_bytes_digest": initial_d3_digest,
        "formation_enabled": formation_enabled,
        "chain_role": chain_role,
        "composition_receipt_digest": composition_receipt_digest,
        "cp0_d3_input_bytes_digest": checkpoint_digests[0],
        "cp0_anatomy_record_digest": checkpoint_record_digests[0],
        "cp0_o3_receipt_digest": o3_receipt_digests[0],
        "cp0_value": public_values[0],
        "cp1_d3_input_bytes_digest": checkpoint_digests[1],
        "cp1_anatomy_record_digest": checkpoint_record_digests[1],
        "cp1_o3_receipt_digest": o3_receipt_digests[1],
        "cp1_value": public_values[1],
        "cp2_d3_input_bytes_digest": checkpoint_digests[2],
        "cp2_anatomy_record_digest": checkpoint_record_digests[2],
        "cp2_o3_receipt_digest": o3_receipt_digests[2],
        "cp2_value": public_values[2],
        "delta_cp1_cp0": public_components[0],
        "delta_cp2_cp1": public_components[1],
        "delta_cp2_cp0": public_components[2],
        "comparison_digest": comparison_digest,
        "checkpoint_status": status,
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": completed,
        "failure_reasons": list(failures),
        "accepted_composition_contract_digest": COMPOSITION_CONTRACT_DIGEST,
        "accepted_o3_operator_contract_digest": O3_OPERATOR_CONTRACT_DIGEST,
        "accepted_projector_contract_digest": PROJECTOR_CONTRACT_DIGEST,
        "accepted_commit_contract_digest": COMMIT_CONTRACT_DIGEST,
        "accepted_amount_operator_contract_digest": AMOUNT_OPERATOR_CONTRACT_DIGEST,
        "accepted_boundary_validator_contract_digest": BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
        "accepted_d3_validator_contract_digest": D3_VALIDATOR_CONTRACT_DIGEST,
        "checkpoint_contract_digest": CHECKPOINT_CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3TwoStepO3CheckpointReceipt(
        **{
            **payload,
            "completed_checks": tuple(completed),
            "failure_reasons": failures,
            "checkpoint_receipt_digest": receipt_digest,
        }
    )


def evaluate_g2_d3_two_step_o3_checkpoints(
    first_boundary_raw_bytes: bytes,
    second_boundary_raw_bytes: bytes,
    initial_d3_raw_bytes: bytes,
    formation_enabled: bool,
    checkpoint_registry: G2D3TwoStepO3CheckpointRegistry,
    sequence_registry: G2D3TwoStepCompositionRegistry,
    target_commit_registry: G2D3TargetCommitRegistry,
    amount_registry: G2D3HalvingAmountRegistry,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> G2D3TwoStepO3CheckpointResult:
    """Evaluate three O3 values only after one complete two-step execution."""

    _validate_checkpoint_api(
        first_boundary_raw_bytes,
        second_boundary_raw_bytes,
        initial_d3_raw_bytes,
        formation_enabled,
        checkpoint_registry,
    )
    first_digest = sha256_hex(first_boundary_raw_bytes)
    second_digest = sha256_hex(second_boundary_raw_bytes)
    initial_digest = sha256_hex(initial_d3_raw_bytes)
    completed = ["api_intake"]
    chain_role = _NOT_COMPUTABLE
    composition_receipt_digest = _NOT_COMPUTABLE
    checkpoint_digests = [_NOT_COMPUTABLE] * 3
    checkpoint_record_digests = [_NOT_COMPUTABLE] * 3
    o3_receipt_digests = [_NOT_COMPUTABLE] * 3

    def fail(code: str) -> G2D3TwoStepO3CheckpointResult:
        completed.extend(("persistence_guard", "checkpoint_receipt"))
        receipt = _build_checkpoint_receipt(
            first_boundary_digest=first_digest,
            second_boundary_digest=second_digest,
            initial_d3_digest=initial_digest,
            formation_enabled=formation_enabled,
            chain_role=chain_role,
            composition_receipt_digest=composition_receipt_digest,
            checkpoint_digests=tuple(checkpoint_digests),
            checkpoint_record_digests=tuple(checkpoint_record_digests),
            o3_receipt_digests=tuple(o3_receipt_digests),
            values=None,
            components=None,
            comparison_digest=_NOT_COMPUTABLE,
            status=_NOT_COMPUTABLE,
            completed=completed,
            failures=(code,),
        )
        return G2D3TwoStepO3CheckpointResult(_NOT_COMPUTABLE, receipt)

    trace = _execute_g2_d3_two_step(
        first_boundary_raw_bytes,
        second_boundary_raw_bytes,
        initial_d3_raw_bytes,
        formation_enabled,
        sequence_registry,
        target_commit_registry,
        amount_registry,
        boundary_registry,
        d3_registry,
    )
    completed.append("two_step_execution")
    composition = trace.composition_result
    composition_receipt_digest = composition.receipt.composition_receipt_digest
    chain_role = composition.receipt.chain_role
    if composition.receipt.validation_status != "valid":
        return fail("OU_TWO_STEP_EXECUTION_FAILED")

    chain = next(
        (item for item in sequence_registry.chain_records if item.chain_role == chain_role),
        None,
    )
    completed.append("composition_validation")
    checkpoint_bytes = (
        trace.validated_initial_d3_raw_bytes,
        trace.committed_intermediate_d3_raw_bytes,
        trace.committed_final_d3_raw_bytes,
    )
    if (
        chain is None
        or composition.receipt.composition_status != "TWO_STEP_COMPOSED"
        or composition.receipt.failure_reasons
        or any(type(raw_bytes) is not bytes for raw_bytes in checkpoint_bytes)
        or composition.final_d3_raw_bytes != checkpoint_bytes[2]
        or sha256_hex(checkpoint_bytes[2]) != chain.final_d3_input_digest
        or composition.receipt.final_d3_input_bytes_digest
        != chain.final_d3_input_digest
        or composition.receipt.final_anatomy_record_digest
        != chain.final_anatomy_record_digest
    ):
        return fail("OU_COMPOSITION_IDENTITY_MISMATCH")

    values: list[float] = []
    phase_names = ("cp0_evaluation", "cp1_evaluation", "cp2_evaluation")
    failure_codes = (
        "OU_CP0_EVALUATION_FAILED",
        "OU_CP1_EVALUATION_FAILED",
        "OU_CP2_EVALUATION_FAILED",
    )
    o3_receipts = []
    for index, raw_bytes in enumerate(checkpoint_bytes):
        o3_receipt = evaluate_g2_d3_local_admissible_engagement(raw_bytes, d3_registry)
        completed.append(phase_names[index])
        o3_receipt_digests[index] = o3_receipt.admissibility_receipt_digest
        if (
            o3_receipt.evaluation_status != "valid"
            or o3_receipt.failure_reasons
            or type(o3_receipt.local_admissible_engagement) is not float
        ):
            return fail(failure_codes[index])
        o3_receipts.append(o3_receipt)
        values.append(o3_receipt.local_admissible_engagement)

    completed.append("checkpoint_identity_gate")
    for index, (record, o3_receipt) in enumerate(
        zip(checkpoint_registry.checkpoint_records, o3_receipts, strict=True)
    ):
        checkpoint_digests[index] = o3_receipt.input_bytes_digest
        checkpoint_record_digests[index] = o3_receipt.source_anatomy_record_digest
        if (
            record.checkpoint_position != index
            or record.checkpoint_role != CHECKPOINT_ROLES[index]
            or o3_receipt.input_bytes_digest != record.d3_input_bytes_digest
            or o3_receipt.source_anatomy_record_digest != record.anatomy_record_digest
            or o3_receipt.operator_contract_digest != O3_OPERATOR_CONTRACT_DIGEST
            or values[index] != record.expected_o3_value
        ):
            return fail("OU_CHECKPOINT_IDENTITY_MISMATCH")

    components = (
        values[1] - values[0],
        values[2] - values[1],
        values[2] - values[0],
    )
    completed.append("component_evaluation")
    comparison_payload = {
        "checkpoint_values": values,
        "directed_components": list(components),
    }
    comparison_digest = sha256_hex(canonical_json_bytes(comparison_payload))
    if components != (-0.25, -0.125, -0.375) or comparison_digest != COMPARISON_DIGEST:
        return fail("OU_COMPONENT_IDENTITY_MISMATCH")

    completed.extend(("persistence_guard", "checkpoint_receipt"))
    values_tuple = (values[0], values[1], values[2])
    receipt = _build_checkpoint_receipt(
        first_boundary_digest=first_digest,
        second_boundary_digest=second_digest,
        initial_d3_digest=initial_digest,
        formation_enabled=formation_enabled,
        chain_role=chain_role,
        composition_receipt_digest=composition_receipt_digest,
        checkpoint_digests=tuple(checkpoint_digests),
        checkpoint_record_digests=tuple(checkpoint_record_digests),
        o3_receipt_digests=tuple(o3_receipt_digests),
        values=values_tuple,
        components=components,
        comparison_digest=comparison_digest,
        status="THREE_CHECKPOINTS_EVALUATED",
        completed=completed,
        failures=(),
    )
    return G2D3TwoStepO3CheckpointResult(values_tuple, receipt)


__all__ = (
    "RECEIPT_SCHEMA_ID",
    "RECEIPT_SCHEMA_VERSION",
    "CHECKPOINT_CLASS_ID",
    "CHECKPOINT_ROLES",
    "CHECKPOINT_STATUSES",
    "CHECKPOINT_PHASES",
    "FAILURE_CODES",
    "CHECKPOINT_CONTRACT_DIGEST",
    "COMPARISON_DIGEST",
    "G2D3TwoStepO3CheckpointRecord",
    "G2D3TwoStepO3CheckpointRegistry",
    "G2D3TwoStepO3CheckpointReceipt",
    "G2D3TwoStepO3CheckpointResult",
    "build_g2_d3_two_step_o3_checkpoint_registry",
    "evaluate_g2_d3_two_step_o3_checkpoints",
)
