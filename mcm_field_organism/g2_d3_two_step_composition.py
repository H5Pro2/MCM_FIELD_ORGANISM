"""Pure fail-closed composition of two fresh G2/D3 continuation steps."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
from typing import Any

from .g2_d3_halving_amount import (
    G2D3HalvingAmountRegistry,
    OPERATOR_CONTRACT_DIGEST as AMOUNT_OPERATOR_CONTRACT_DIGEST,
)
from .g2_d3_schema_validator import G2D3ValidationRegistry
from .g2_d3_target_projection import (
    COMMIT_CONTRACT_DIGEST,
    PROJECTOR_CONTRACT_DIGEST,
    G2D3TargetCommitRegistry,
    project_g2_d3_conservative_target,
    verify_and_commit_g2_d3_projected_target,
)
from .g2_d3_transient_boundary_validator import (
    D3_VALIDATOR_CONTRACT_DIGEST,
    VALIDATOR_CONTRACT_DIGEST as BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
    G2D3TransientBoundaryRegistry,
    validate_g2_d3_transient_boundary,
)
from .kfs1_schema_validator import canonical_json_bytes, sha256_hex


RECEIPT_SCHEMA_ID = "g2_d3_two_step_composition_receipt"
RECEIPT_SCHEMA_VERSION = "s1oq.v1"
COMPOSITION_CLASS_ID = "G2_D3_TWO_FRESH_CONTINUATION_COMPOSITION"
COMPOSITION_STATUSES = ("TWO_STEP_COMPOSED", "not_computable")
COMPOSITION_PHASES = (
    "api_intake",
    "chain_binding",
    "first_projection",
    "first_commit",
    "intermediate_identity_gate",
    "second_boundary_validation",
    "second_source_binding_gate",
    "second_contact_link_gate",
    "second_projection",
    "second_commit",
    "final_identity_gate",
    "persistence_guard",
    "composition_receipt",
)
FAILURE_CODES = (
    "OQ_UNKNOWN_CHAIN_BINDING",
    "OQ_FORMATION_DISABLED",
    "OQ_FIRST_PROJECTION_FAILED",
    "OQ_FIRST_COMMIT_FAILED",
    "OQ_INTERMEDIATE_IDENTITY_MISMATCH",
    "OQ_SECOND_BOUNDARY_INVALID",
    "OQ_SECOND_SOURCE_BINDING_MISMATCH",
    "OQ_SECOND_CONTACT_LINK_MISMATCH",
    "OQ_SECOND_PROJECTION_FAILED",
    "OQ_SECOND_COMMIT_FAILED",
    "OQ_FINAL_IDENTITY_MISMATCH",
)
COMPOSITION_CONTRACT_DIGEST = (
    "e68646a2d4a605ecdd36125dcd5f97cd849091d5af1bbcf1f587b1c01e1c2e06"
)
_NOT_COMPUTABLE = "not_computable"


@dataclass(frozen=True)
class G2D3TwoStepChainRecord:
    chain_role: str
    first_boundary_input_digest: str
    second_boundary_input_digest: str
    first_current_contact_digest: str
    second_prior_contact_digest: str
    initial_d3_input_digest: str
    initial_anatomy_record_digest: str
    intermediate_d3_input_digest: str
    intermediate_anatomy_record_digest: str
    final_d3_input_digest: str
    final_anatomy_record_digest: str


@dataclass(frozen=True)
class G2D3TwoStepCompositionRegistry:
    receipt_schema_id: str
    receipt_schema_version: str
    composition_class_id: str
    composition_statuses: tuple[str, ...]
    composition_phases: tuple[str, ...]
    failure_codes: tuple[str, ...]
    chain_records: tuple[G2D3TwoStepChainRecord, ...]
    accepted_projector_contract_digest: str
    accepted_commit_contract_digest: str
    accepted_amount_operator_contract_digest: str
    accepted_boundary_validator_contract_digest: str
    accepted_d3_validator_contract_digest: str
    composition_contract_digest: str


@dataclass(frozen=True)
class G2D3TwoStepCompositionReceipt:
    receipt_schema_id: str
    receipt_schema_version: str
    composition_class_id: str
    first_boundary_input_bytes_digest: str
    second_boundary_input_bytes_digest: str
    initial_d3_input_bytes_digest: str
    formation_enabled: bool
    chain_role: str
    first_current_contact_digest: str
    second_prior_contact_digest: str
    first_projection_receipt_digest: str
    first_commit_receipt_digest: str
    intermediate_d3_input_bytes_digest: str
    intermediate_anatomy_record_digest: str
    second_boundary_validation_receipt_digest: str
    second_source_d3_anatomy_record_digest: str
    second_projection_receipt_digest: str
    second_commit_receipt_digest: str
    final_d3_input_bytes_digest: str
    final_anatomy_record_digest: str
    composition_status: str
    validation_status: str
    completed_checks: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    accepted_projector_contract_digest: str
    accepted_commit_contract_digest: str
    accepted_amount_operator_contract_digest: str
    accepted_boundary_validator_contract_digest: str
    accepted_d3_validator_contract_digest: str
    composition_contract_digest: str
    composition_receipt_digest: str

    def canonical_payload(self) -> dict[str, Any]:
        payload = {item.name: getattr(self, item.name) for item in fields(self)}
        payload["completed_checks"] = list(self.completed_checks)
        payload["failure_reasons"] = list(self.failure_reasons)
        return payload


@dataclass(frozen=True)
class G2D3TwoStepCompositionResult:
    final_d3_raw_bytes: bytes | str
    receipt: G2D3TwoStepCompositionReceipt


@dataclass(frozen=True)
class _G2D3TwoStepExecutionTrace:
    composition_result: G2D3TwoStepCompositionResult
    validated_initial_d3_raw_bytes: bytes | str
    committed_intermediate_d3_raw_bytes: bytes | str
    committed_final_d3_raw_bytes: bytes | str


def _chain(
    role: str,
    first_boundary_digest: str,
    second_boundary_digest: str,
    contact_digest: str,
) -> G2D3TwoStepChainRecord:
    return G2D3TwoStepChainRecord(
        chain_role=role,
        first_boundary_input_digest=first_boundary_digest,
        second_boundary_input_digest=second_boundary_digest,
        first_current_contact_digest=contact_digest,
        second_prior_contact_digest=contact_digest,
        initial_d3_input_digest="d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7",
        initial_anatomy_record_digest="1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f",
        intermediate_d3_input_digest="2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8",
        intermediate_anatomy_record_digest="d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c",
        final_d3_input_digest="a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab",
        final_anatomy_record_digest="efba6284b3e56cfe2041465eb8acc76b00de34ee8303f6a2caa20b2a3fc66681",
    )


def build_g2_d3_two_step_composition_registry() -> G2D3TwoStepCompositionRegistry:
    return G2D3TwoStepCompositionRegistry(
        receipt_schema_id=RECEIPT_SCHEMA_ID,
        receipt_schema_version=RECEIPT_SCHEMA_VERSION,
        composition_class_id=COMPOSITION_CLASS_ID,
        composition_statuses=COMPOSITION_STATUSES,
        composition_phases=COMPOSITION_PHASES,
        failure_codes=FAILURE_CODES,
        chain_records=(
            _chain(
                "OP_CHAIN_XXX",
                "c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c",
                "6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a",
                "0df023f42e8be41504bbad49fc8c5d89b7d16e25a2904c773f0845a841ffea15",
            ),
            _chain(
                "OP_CHAIN_YYY",
                "2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b",
                "dc772636ed23e9cf9a904fd9943a7a1bcfacafe08aed9e60a65ac93f3d266d32",
                "d270f4a888136e4a6dc182b15468c3e7dc4c0567b4bb92eee75818638088f356",
            ),
        ),
        accepted_projector_contract_digest=PROJECTOR_CONTRACT_DIGEST,
        accepted_commit_contract_digest=COMMIT_CONTRACT_DIGEST,
        accepted_amount_operator_contract_digest=AMOUNT_OPERATOR_CONTRACT_DIGEST,
        accepted_boundary_validator_contract_digest=BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
        accepted_d3_validator_contract_digest=D3_VALIDATOR_CONTRACT_DIGEST,
        composition_contract_digest=COMPOSITION_CONTRACT_DIGEST,
    )


def _validate_api(
    first_boundary_raw_bytes: bytes,
    second_boundary_raw_bytes: bytes,
    initial_d3_raw_bytes: bytes,
    formation_enabled: bool,
    sequence_registry: G2D3TwoStepCompositionRegistry,
    target_commit_registry: G2D3TargetCommitRegistry,
    amount_registry: G2D3HalvingAmountRegistry,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> None:
    if type(first_boundary_raw_bytes) is not bytes:
        raise TypeError("first_boundary_raw_bytes must be bytes")
    if type(second_boundary_raw_bytes) is not bytes:
        raise TypeError("second_boundary_raw_bytes must be bytes")
    if type(initial_d3_raw_bytes) is not bytes:
        raise TypeError("initial_d3_raw_bytes must be bytes")
    if type(formation_enabled) is not bool:
        raise TypeError("formation_enabled must be bool")
    if type(sequence_registry) is not G2D3TwoStepCompositionRegistry:
        raise TypeError("sequence_registry must be G2D3TwoStepCompositionRegistry")
    if sequence_registry != build_g2_d3_two_step_composition_registry():
        raise ValueError("sequence_registry does not match the bound S1-OR registry")
    if type(target_commit_registry) is not G2D3TargetCommitRegistry:
        raise TypeError("target_commit_registry must be G2D3TargetCommitRegistry")
    if type(amount_registry) is not G2D3HalvingAmountRegistry:
        raise TypeError("amount_registry must be G2D3HalvingAmountRegistry")
    if type(boundary_registry) is not G2D3TransientBoundaryRegistry:
        raise TypeError("boundary_registry must be G2D3TransientBoundaryRegistry")
    if type(d3_registry) is not G2D3ValidationRegistry:
        raise TypeError("d3_registry must be G2D3ValidationRegistry")


def _build_receipt(
    *,
    first_boundary_digest: str,
    second_boundary_digest: str,
    initial_d3_digest: str,
    formation_enabled: bool,
    chain_role: str,
    first_contact_digest: str,
    second_prior_digest: str,
    first_projection_digest: str,
    first_commit_digest: str,
    intermediate_input_digest: str,
    intermediate_record_digest: str,
    second_boundary_receipt_digest: str,
    second_source_record_digest: str,
    second_projection_digest: str,
    second_commit_digest: str,
    final_input_digest: str,
    final_record_digest: str,
    status: str,
    completed: list[str],
    failures: tuple[str, ...],
) -> G2D3TwoStepCompositionReceipt:
    payload = {
        "receipt_schema_id": RECEIPT_SCHEMA_ID,
        "receipt_schema_version": RECEIPT_SCHEMA_VERSION,
        "composition_class_id": COMPOSITION_CLASS_ID,
        "first_boundary_input_bytes_digest": first_boundary_digest,
        "second_boundary_input_bytes_digest": second_boundary_digest,
        "initial_d3_input_bytes_digest": initial_d3_digest,
        "formation_enabled": formation_enabled,
        "chain_role": chain_role,
        "first_current_contact_digest": first_contact_digest,
        "second_prior_contact_digest": second_prior_digest,
        "first_projection_receipt_digest": first_projection_digest,
        "first_commit_receipt_digest": first_commit_digest,
        "intermediate_d3_input_bytes_digest": intermediate_input_digest,
        "intermediate_anatomy_record_digest": intermediate_record_digest,
        "second_boundary_validation_receipt_digest": second_boundary_receipt_digest,
        "second_source_d3_anatomy_record_digest": second_source_record_digest,
        "second_projection_receipt_digest": second_projection_digest,
        "second_commit_receipt_digest": second_commit_digest,
        "final_d3_input_bytes_digest": final_input_digest,
        "final_anatomy_record_digest": final_record_digest,
        "composition_status": status,
        "validation_status": "invalid" if failures else "valid",
        "completed_checks": completed,
        "failure_reasons": list(failures),
        "accepted_projector_contract_digest": PROJECTOR_CONTRACT_DIGEST,
        "accepted_commit_contract_digest": COMMIT_CONTRACT_DIGEST,
        "accepted_amount_operator_contract_digest": AMOUNT_OPERATOR_CONTRACT_DIGEST,
        "accepted_boundary_validator_contract_digest": BOUNDARY_VALIDATOR_CONTRACT_DIGEST,
        "accepted_d3_validator_contract_digest": D3_VALIDATOR_CONTRACT_DIGEST,
        "composition_contract_digest": COMPOSITION_CONTRACT_DIGEST,
    }
    receipt_digest = sha256_hex(canonical_json_bytes(payload))
    return G2D3TwoStepCompositionReceipt(
        **{
            **payload,
            "completed_checks": tuple(completed),
            "failure_reasons": failures,
            "composition_receipt_digest": receipt_digest,
        }
    )


def _execute_g2_d3_two_step(
    first_boundary_raw_bytes: bytes,
    second_boundary_raw_bytes: bytes,
    initial_d3_raw_bytes: bytes,
    formation_enabled: bool,
    sequence_registry: G2D3TwoStepCompositionRegistry,
    target_commit_registry: G2D3TargetCommitRegistry,
    amount_registry: G2D3HalvingAmountRegistry,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> _G2D3TwoStepExecutionTrace:
    """Compose two validated projection/commit steps without persistence."""

    _validate_api(
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
    first_boundary_digest = sha256_hex(first_boundary_raw_bytes)
    second_boundary_digest = sha256_hex(second_boundary_raw_bytes)
    initial_d3_digest = sha256_hex(initial_d3_raw_bytes)
    completed = ["api_intake"]
    chain_role = _NOT_COMPUTABLE
    first_contact_digest = _NOT_COMPUTABLE
    second_prior_digest = _NOT_COMPUTABLE
    first_projection_digest = _NOT_COMPUTABLE
    first_commit_digest = _NOT_COMPUTABLE
    intermediate_input_digest = _NOT_COMPUTABLE
    intermediate_record_digest = _NOT_COMPUTABLE
    second_boundary_receipt_digest = _NOT_COMPUTABLE
    second_source_record_digest = _NOT_COMPUTABLE
    second_projection_digest = _NOT_COMPUTABLE
    second_commit_digest = _NOT_COMPUTABLE
    final_input_digest = _NOT_COMPUTABLE
    final_record_digest = _NOT_COMPUTABLE

    def fail(code: str) -> _G2D3TwoStepExecutionTrace:
        completed.extend(("persistence_guard", "composition_receipt"))
        receipt = _build_receipt(
            first_boundary_digest=first_boundary_digest,
            second_boundary_digest=second_boundary_digest,
            initial_d3_digest=initial_d3_digest,
            formation_enabled=formation_enabled,
            chain_role=chain_role,
            first_contact_digest=first_contact_digest,
            second_prior_digest=second_prior_digest,
            first_projection_digest=first_projection_digest,
            first_commit_digest=first_commit_digest,
            intermediate_input_digest=intermediate_input_digest,
            intermediate_record_digest=intermediate_record_digest,
            second_boundary_receipt_digest=second_boundary_receipt_digest,
            second_source_record_digest=second_source_record_digest,
            second_projection_digest=second_projection_digest,
            second_commit_digest=second_commit_digest,
            final_input_digest=final_input_digest,
            final_record_digest=final_record_digest,
            status=_NOT_COMPUTABLE,
            completed=completed,
            failures=(code,),
        )
        return _G2D3TwoStepExecutionTrace(
            G2D3TwoStepCompositionResult(_NOT_COMPUTABLE, receipt),
            _NOT_COMPUTABLE,
            _NOT_COMPUTABLE,
            _NOT_COMPUTABLE,
        )

    chain = next(
        (
            item
            for item in sequence_registry.chain_records
            if item.first_boundary_input_digest == first_boundary_digest
            and item.initial_d3_input_digest == initial_d3_digest
        ),
        None,
    )
    completed.append("chain_binding")
    if chain is None:
        return fail("OQ_UNKNOWN_CHAIN_BINDING")
    chain_role = chain.chain_role
    first_contact_digest = chain.first_current_contact_digest
    if not formation_enabled:
        return fail("OQ_FORMATION_DISABLED")

    first_projection = project_g2_d3_conservative_target(
        first_boundary_raw_bytes,
        initial_d3_raw_bytes,
        formation_enabled,
        target_commit_registry,
        amount_registry,
        boundary_registry,
        d3_registry,
    )
    completed.append("first_projection")
    first_projection_digest = first_projection.receipt.projection_receipt_digest
    if first_projection.receipt.evaluation_status != "valid":
        return fail("OQ_FIRST_PROJECTION_FAILED")
    if type(first_projection.target_d3_raw_bytes) is not bytes:
        return fail("OQ_FIRST_PROJECTION_FAILED")

    first_commit = verify_and_commit_g2_d3_projected_target(
        first_boundary_raw_bytes,
        initial_d3_raw_bytes,
        initial_d3_raw_bytes,
        first_projection.target_d3_raw_bytes,
        formation_enabled,
        target_commit_registry,
        amount_registry,
        boundary_registry,
        d3_registry,
    )
    completed.append("first_commit")
    first_commit_digest = first_commit.receipt.commit_receipt_digest
    if (
        first_commit.receipt.validation_status != "valid"
        or first_commit.receipt.commit_status != "PROJECTED_COMMITTED"
        or type(first_commit.committed_d3_raw_bytes) is not bytes
    ):
        return fail("OQ_FIRST_COMMIT_FAILED")

    intermediate_raw = first_commit.committed_d3_raw_bytes
    intermediate_input_digest = sha256_hex(intermediate_raw)
    intermediate = json.loads(intermediate_raw.decode("utf-8"))
    intermediate_record_digest = intermediate["anatomy_record_digest"]
    completed.append("intermediate_identity_gate")
    if (
        intermediate_input_digest != chain.intermediate_d3_input_digest
        or intermediate_record_digest != chain.intermediate_anatomy_record_digest
    ):
        return fail("OQ_INTERMEDIATE_IDENTITY_MISMATCH")

    second_boundary_receipt = validate_g2_d3_transient_boundary(
        second_boundary_raw_bytes,
        intermediate_raw,
        boundary_registry,
        d3_registry,
    )
    completed.append("second_boundary_validation")
    second_boundary_receipt_digest = (
        second_boundary_receipt.boundary_validation_receipt_digest
    )
    try:
        second_boundary = json.loads(second_boundary_raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return fail("OQ_SECOND_BOUNDARY_INVALID")
    second_source_record_digest = second_boundary.get(
        "source_d3_anatomy_record_digest", _NOT_COMPUTABLE
    )
    if second_boundary_receipt.validation_status != "valid":
        if second_boundary_receipt.failure_reasons == ("OA_D3_SOURCE_DIGEST_MISMATCH",):
            completed.append("second_source_binding_gate")
            return fail("OQ_SECOND_SOURCE_BINDING_MISMATCH")
        return fail("OQ_SECOND_BOUNDARY_INVALID")

    completed.append("second_source_binding_gate")
    if second_source_record_digest != chain.intermediate_anatomy_record_digest:
        return fail("OQ_SECOND_SOURCE_BINDING_MISMATCH")

    second_prior_digest = second_boundary.get("prior_contact_digest", _NOT_COMPUTABLE)
    completed.append("second_contact_link_gate")
    if (
        second_prior_digest != chain.first_current_contact_digest
        or second_prior_digest != chain.second_prior_contact_digest
    ):
        return fail("OQ_SECOND_CONTACT_LINK_MISMATCH")
    if second_boundary_digest != chain.second_boundary_input_digest:
        return fail("OQ_SECOND_BOUNDARY_INVALID")

    second_projection = project_g2_d3_conservative_target(
        second_boundary_raw_bytes,
        intermediate_raw,
        formation_enabled,
        target_commit_registry,
        amount_registry,
        boundary_registry,
        d3_registry,
    )
    completed.append("second_projection")
    second_projection_digest = second_projection.receipt.projection_receipt_digest
    if second_projection.receipt.evaluation_status != "valid":
        return fail("OQ_SECOND_PROJECTION_FAILED")
    if type(second_projection.target_d3_raw_bytes) is not bytes:
        return fail("OQ_SECOND_PROJECTION_FAILED")

    second_commit = verify_and_commit_g2_d3_projected_target(
        second_boundary_raw_bytes,
        intermediate_raw,
        intermediate_raw,
        second_projection.target_d3_raw_bytes,
        formation_enabled,
        target_commit_registry,
        amount_registry,
        boundary_registry,
        d3_registry,
    )
    completed.append("second_commit")
    second_commit_digest = second_commit.receipt.commit_receipt_digest
    if (
        second_commit.receipt.validation_status != "valid"
        or second_commit.receipt.commit_status != "PROJECTED_COMMITTED"
        or type(second_commit.committed_d3_raw_bytes) is not bytes
    ):
        return fail("OQ_SECOND_COMMIT_FAILED")

    final_raw = second_commit.committed_d3_raw_bytes
    final_input_digest = sha256_hex(final_raw)
    final = json.loads(final_raw.decode("utf-8"))
    final_record_digest = final["anatomy_record_digest"]
    completed.append("final_identity_gate")
    if (
        final_input_digest != chain.final_d3_input_digest
        or final_record_digest != chain.final_anatomy_record_digest
    ):
        return fail("OQ_FINAL_IDENTITY_MISMATCH")

    completed.extend(("persistence_guard", "composition_receipt"))
    receipt = _build_receipt(
        first_boundary_digest=first_boundary_digest,
        second_boundary_digest=second_boundary_digest,
        initial_d3_digest=initial_d3_digest,
        formation_enabled=formation_enabled,
        chain_role=chain_role,
        first_contact_digest=first_contact_digest,
        second_prior_digest=second_prior_digest,
        first_projection_digest=first_projection_digest,
        first_commit_digest=first_commit_digest,
        intermediate_input_digest=intermediate_input_digest,
        intermediate_record_digest=intermediate_record_digest,
        second_boundary_receipt_digest=second_boundary_receipt_digest,
        second_source_record_digest=second_source_record_digest,
        second_projection_digest=second_projection_digest,
        second_commit_digest=second_commit_digest,
        final_input_digest=final_input_digest,
        final_record_digest=final_record_digest,
        status="TWO_STEP_COMPOSED",
        completed=completed,
        failures=(),
    )
    return _G2D3TwoStepExecutionTrace(
        G2D3TwoStepCompositionResult(final_raw, receipt),
        initial_d3_raw_bytes,
        intermediate_raw,
        final_raw,
    )


def compose_g2_d3_two_step_continuation(
    first_boundary_raw_bytes: bytes,
    second_boundary_raw_bytes: bytes,
    initial_d3_raw_bytes: bytes,
    formation_enabled: bool,
    sequence_registry: G2D3TwoStepCompositionRegistry,
    target_commit_registry: G2D3TargetCommitRegistry,
    amount_registry: G2D3HalvingAmountRegistry,
    boundary_registry: G2D3TransientBoundaryRegistry,
    d3_registry: G2D3ValidationRegistry,
) -> G2D3TwoStepCompositionResult:
    """Compose two validated projection/commit steps without persistence."""

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
    return trace.composition_result


__all__ = (
    "RECEIPT_SCHEMA_ID",
    "RECEIPT_SCHEMA_VERSION",
    "COMPOSITION_CLASS_ID",
    "COMPOSITION_STATUSES",
    "COMPOSITION_PHASES",
    "FAILURE_CODES",
    "COMPOSITION_CONTRACT_DIGEST",
    "G2D3TwoStepChainRecord",
    "G2D3TwoStepCompositionRegistry",
    "G2D3TwoStepCompositionReceipt",
    "G2D3TwoStepCompositionResult",
    "build_g2_d3_two_step_composition_registry",
    "compose_g2_d3_two_step_continuation",
)
