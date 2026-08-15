"""S1-GV immutable schema for one future real adapter-call receipt."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_formation_s1gu_real_transition_builder_contract import (
    S1_GU_REQUIRED_ADAPTER_RECEIPT_FIELDS,
    audit_e1_formation_s1gu_real_transition_builder_contract,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GVRealAdapterCallReceiptSchemaError(ValueError):
    """Raised when receipt integrity, scope, or one-step accounting is invalid."""


S1_GV_RECEIPT_ID = "e1.real-single-batch-adapter-call-receipt.s1gv.v1"
S1_GV_KERNEL_NAME = "advance_fixed_e1_adapter_fast_shared_field_transient"


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GVRealAdapterCallReceipt:
    """Integrity schema only; no receipt factory exists in S1-GV."""

    receipt_id: str
    gate_digest: str
    authorization_digest: str
    consumed_token_digest: str
    binding_digest: str
    batch_index: int
    batch_step_start_tick: int
    batch_step_end_tick: int
    previous_carrier_digest: str
    previous_field_digest: str
    next_field_digest: str
    source_state_digest_before: str
    source_state_digest_after: str
    fixed_adapter_digest_before: str
    fixed_adapter_digest_after: str
    kernel_name: str
    token_consumed_before_adapter: bool
    next_field_object_replaced: bool
    adapter_calls: int
    field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    receipt_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "receipt_digest"
        }
        digest_fields = (
            self.gate_digest,
            self.authorization_digest,
            self.consumed_token_digest,
            self.binding_digest,
            self.previous_carrier_digest,
            self.previous_field_digest,
            self.next_field_digest,
            self.source_state_digest_before,
            self.source_state_digest_after,
            self.fixed_adapter_digest_before,
            self.fixed_adapter_digest_after,
        )
        if (
            self.receipt_id != S1_GV_RECEIPT_ID
            or not all(_valid_digest(value) for value in digest_fields)
            or isinstance(self.batch_index, bool)
            or not isinstance(self.batch_index, int)
            or self.batch_index < 0
            or self.batch_step_start_tick < 0
            or self.batch_step_end_tick <= self.batch_step_start_tick
            or self.previous_field_digest == self.next_field_digest
            or self.source_state_digest_before
            != self.source_state_digest_after
            or self.fixed_adapter_digest_before
            != self.fixed_adapter_digest_after
            or self.kernel_name != S1_GV_KERNEL_NAME
            or self.token_consumed_before_adapter is not True
            or self.next_field_object_replaced is not True
            or self.adapter_calls != 1
            or self.field_steps_executed != 1
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.receipt_digest != _digest(payload)
        ):
            raise E1FormationS1GVRealAdapterCallReceiptSchemaError(
                "S1-GV receipt lost integrity or exact one-step scope"
            )


@dataclass(frozen=True, slots=True)
class E1FormationS1GVRealAdapterCallReceiptSchemaAudit:
    source_s1gu_contract_digest: str
    schema_fields: tuple[str, ...]
    required_fields: tuple[str, ...]
    missing_required_fields: tuple[str, ...]
    schema_frozen: bool
    schema_slotted: bool
    digest_integrity_enforced: bool
    one_call_one_step_enforced: bool
    token_consumption_marker_required: bool
    new_field_object_marker_required: bool
    source_state_attestation_preserved: bool
    fixed_adapter_attestation_preserved: bool
    receipt_factory_implemented: bool
    receipt_instance_created: bool
    structural_integrity_is_execution_authenticity: bool
    external_authenticity_path_required: bool
    adapter_or_kernel_access_permitted: bool
    execution_permitted: bool
    persistence_permitted: bool
    claims_permitted: bool
    decision: str
    reason: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if (
            len(self.source_s1gu_contract_digest) != 64
            or self.schema_fields
            != tuple(E1FormationS1GVRealAdapterCallReceipt.__dataclass_fields__)
            or self.required_fields != S1_GU_REQUIRED_ADAPTER_RECEIPT_FIELDS
            or self.missing_required_fields
            or any(
                value is not True
                for value in (
                    self.schema_frozen,
                    self.schema_slotted,
                    self.digest_integrity_enforced,
                    self.one_call_one_step_enforced,
                    self.token_consumption_marker_required,
                    self.new_field_object_marker_required,
                    self.source_state_attestation_preserved,
                    self.fixed_adapter_attestation_preserved,
                    self.external_authenticity_path_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.receipt_factory_implemented,
                    self.receipt_instance_created,
                    self.structural_integrity_is_execution_authenticity,
                    self.adapter_or_kernel_access_permitted,
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "REAL_ADAPTER_CALL_RECEIPT_SCHEMA_READY_AUTHENTICITY_PATH_ABSENT"
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1FormationS1GVRealAdapterCallReceiptSchemaError(
                "S1-GV audit confused structural integrity with authenticity"
            )


def audit_e1_formation_s1gv_real_adapter_call_receipt_schema(
) -> E1FormationS1GVRealAdapterCallReceiptSchemaAudit:
    """Audit the schema without constructing a receipt or calling an adapter."""

    source_contract = audit_e1_formation_s1gu_real_transition_builder_contract()
    schema_fields = tuple(
        E1FormationS1GVRealAdapterCallReceipt.__dataclass_fields__
    )
    missing = tuple(
        field
        for field in S1_GU_REQUIRED_ADAPTER_RECEIPT_FIELDS
        if field not in schema_fields
    )
    params = E1FormationS1GVRealAdapterCallReceipt.__dataclass_params__
    values = {
        "source_s1gu_contract_digest": source_contract.contract_digest,
        "schema_fields": schema_fields,
        "required_fields": S1_GU_REQUIRED_ADAPTER_RECEIPT_FIELDS,
        "missing_required_fields": missing,
        "schema_frozen": params.frozen,
        "schema_slotted": "__dict__"
        not in E1FormationS1GVRealAdapterCallReceipt.__dict__,
        "digest_integrity_enforced": True,
        "one_call_one_step_enforced": True,
        "token_consumption_marker_required": True,
        "new_field_object_marker_required": True,
        "source_state_attestation_preserved": True,
        "fixed_adapter_attestation_preserved": True,
        "receipt_factory_implemented": False,
        "receipt_instance_created": False,
        "structural_integrity_is_execution_authenticity": False,
        "external_authenticity_path_required": True,
        "adapter_or_kernel_access_permitted": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "claims_permitted": False,
        "decision": (
            "REAL_ADAPTER_CALL_RECEIPT_SCHEMA_READY_AUTHENTICITY_PATH_ABSENT"
        ),
        "reason": (
            "the-frozen-schema-enforces-digests-one-call-one-step-token-"
            "consumption-field-replacement-and-unchanged-attestations-but-"
            "structural-validity-alone-cannot-authenticate-an-external-owner-"
            "authorization-token-or-atomic-kernel-call"
        ),
    }
    return E1FormationS1GVRealAdapterCallReceiptSchemaAudit(
        **values,
        audit_digest=_digest(values),
    )
