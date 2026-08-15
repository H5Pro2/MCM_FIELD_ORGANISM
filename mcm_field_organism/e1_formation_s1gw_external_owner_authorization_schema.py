"""S1-GW schema for one future externally originated owner authorization."""

from __future__ import annotations

from dataclasses import dataclass

from .e1_formation_s1gs_real_single_batch_gate_contract import (
    build_e1_formation_s1gs_real_single_batch_gate_contract,
)
from .e1_formation_s1gv_real_adapter_call_receipt_schema import (
    audit_e1_formation_s1gv_real_adapter_call_receipt_schema,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GWExternalOwnerAuthorizationSchemaError(ValueError):
    """Raised when authorization scope, origin, or one-shot limits are invalid."""


S1_GW_AUTHORIZATION_ID = "e1.external-owner-single-batch-authorization.s1gw.v1"
S1_GW_PROJECT_ID = "MCM_FIELD_ORGANISM"
S1_GW_REQUIRED_FIELDS = (
    "authorization_id",
    "external_origin_receipt_digest",
    "owner_message_digest",
    "project_id",
    "run_id",
    "gate_digest",
    "binding_digest",
    "batch_index",
    "carrier_digest",
    "maximum_adapter_calls",
    "maximum_field_steps",
    "single_use",
    "non_persistent",
    "retry_permitted",
    "reparametrization_permitted",
    "partial_return_permitted",
    "claims_permitted",
    "expires_after_success_or_failure",
    "authorization_digest",
)
S1_GW_REQUIRED_OWNER_CLAUSES = (
    "explicitly-authorize-the-named-run",
    "exactly-one-real-carrier-batch",
    "maximum-one-adapter-call",
    "maximum-one-field-step",
    "non-persistent",
    "no-retry",
    "no-reparametrization",
    "no-partial-return",
    "no-memory-fieldtime-organization-or-ai-claim",
    "expires-after-success-or-failure",
)
S1_GW_NON_AUTHORIZATION_MESSAGES = (
    "ok weiter",
    "weiter",
    "okay weiter",
    "mach weiter",
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GWExternalOwnerAuthorization:
    """Integrity schema only; construction does not authenticate its origin."""

    authorization_id: str
    external_origin_receipt_digest: str
    owner_message_digest: str
    project_id: str
    run_id: str
    gate_digest: str
    binding_digest: str
    batch_index: int
    carrier_digest: str
    maximum_adapter_calls: int
    maximum_field_steps: int
    single_use: bool
    non_persistent: bool
    retry_permitted: bool
    reparametrization_permitted: bool
    partial_return_permitted: bool
    claims_permitted: bool
    expires_after_success_or_failure: bool
    authorization_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "authorization_digest"
        }
        if (
            self.authorization_id != S1_GW_AUTHORIZATION_ID
            or not _valid_digest(self.external_origin_receipt_digest)
            or not _valid_digest(self.owner_message_digest)
            or self.project_id != S1_GW_PROJECT_ID
            or not self.run_id.startswith("S1-G")
            or not _valid_digest(self.gate_digest)
            or not _valid_digest(self.binding_digest)
            or isinstance(self.batch_index, bool)
            or not isinstance(self.batch_index, int)
            or self.batch_index < 0
            or not _valid_digest(self.carrier_digest)
            or self.maximum_adapter_calls != 1
            or self.maximum_field_steps != 1
            or self.single_use is not True
            or self.non_persistent is not True
            or self.retry_permitted is not False
            or self.reparametrization_permitted is not False
            or self.partial_return_permitted is not False
            or self.claims_permitted is not False
            or self.expires_after_success_or_failure is not True
            or self.authorization_digest != _digest(payload)
        ):
            raise E1FormationS1GWExternalOwnerAuthorizationSchemaError(
                "S1-GW authorization lost external origin or exact run scope"
            )


@dataclass(frozen=True, slots=True)
class E1FormationS1GWExternalOwnerAuthorizationSchemaAudit:
    source_s1gs_gate_digest: str
    source_s1gv_audit_digest: str
    schema_fields: tuple[str, ...]
    required_fields: tuple[str, ...]
    missing_required_fields: tuple[str, ...]
    required_owner_clauses: tuple[str, ...]
    non_authorization_messages: tuple[str, ...]
    schema_frozen: bool
    schema_slotted: bool
    exact_target_binding_required: bool
    external_origin_receipt_required: bool
    structural_validity_is_external_authenticity: bool
    authorization_factory_implemented: bool
    authorization_instance_created: bool
    current_continue_message_is_authorization: bool
    target_selected: bool
    token_creation_permitted: bool
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
            not _valid_digest(self.source_s1gs_gate_digest)
            or not _valid_digest(self.source_s1gv_audit_digest)
            or self.schema_fields
            != tuple(E1FormationS1GWExternalOwnerAuthorization.__dataclass_fields__)
            or self.required_fields != S1_GW_REQUIRED_FIELDS
            or self.missing_required_fields
            or self.required_owner_clauses != S1_GW_REQUIRED_OWNER_CLAUSES
            or self.non_authorization_messages != S1_GW_NON_AUTHORIZATION_MESSAGES
            or any(
                value is not True
                for value in (
                    self.schema_frozen,
                    self.schema_slotted,
                    self.exact_target_binding_required,
                    self.external_origin_receipt_required,
                )
            )
            or any(
                value is not False
                for value in (
                    self.structural_validity_is_external_authenticity,
                    self.authorization_factory_implemented,
                    self.authorization_instance_created,
                    self.current_continue_message_is_authorization,
                    self.target_selected,
                    self.token_creation_permitted,
                    self.execution_permitted,
                    self.persistence_permitted,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "EXTERNAL_OWNER_AUTHORIZATION_SCHEMA_BOUND_TARGET_AND_ORIGIN_REQUIRED"
            or not self.reason
            or self.audit_digest != _digest(payload)
        ):
            raise E1FormationS1GWExternalOwnerAuthorizationSchemaError(
                "S1-GW audit invented authorization or omitted target binding"
            )


def audit_e1_formation_s1gw_external_owner_authorization_schema(
) -> E1FormationS1GWExternalOwnerAuthorizationSchemaAudit:
    """Audit the authorization schema without interpreting a user message."""

    gate = build_e1_formation_s1gs_real_single_batch_gate_contract()
    receipt_schema = audit_e1_formation_s1gv_real_adapter_call_receipt_schema()
    schema_fields = tuple(
        E1FormationS1GWExternalOwnerAuthorization.__dataclass_fields__
    )
    missing = tuple(
        field for field in S1_GW_REQUIRED_FIELDS if field not in schema_fields
    )
    params = E1FormationS1GWExternalOwnerAuthorization.__dataclass_params__
    values = {
        "source_s1gs_gate_digest": gate.gate_digest,
        "source_s1gv_audit_digest": receipt_schema.audit_digest,
        "schema_fields": schema_fields,
        "required_fields": S1_GW_REQUIRED_FIELDS,
        "missing_required_fields": missing,
        "required_owner_clauses": S1_GW_REQUIRED_OWNER_CLAUSES,
        "non_authorization_messages": S1_GW_NON_AUTHORIZATION_MESSAGES,
        "schema_frozen": params.frozen,
        "schema_slotted": "__dict__"
        not in E1FormationS1GWExternalOwnerAuthorization.__dict__,
        "exact_target_binding_required": True,
        "external_origin_receipt_required": True,
        "structural_validity_is_external_authenticity": False,
        "authorization_factory_implemented": False,
        "authorization_instance_created": False,
        "current_continue_message_is_authorization": False,
        "target_selected": False,
        "token_creation_permitted": False,
        "execution_permitted": False,
        "persistence_permitted": False,
        "claims_permitted": False,
        "decision": (
            "EXTERNAL_OWNER_AUTHORIZATION_SCHEMA_BOUND_TARGET_AND_ORIGIN_REQUIRED"
        ),
        "reason": (
            "one-future-owner-authorization-must-bind-an-externally-attested-"
            "message-to-project-run-gate-binding-batch-and-carrier;generic-"
            "continue-messages-do-not-authorize-real-execution;no-target-"
            "authorization-instance-token-or-execution-exists"
        ),
    }
    return E1FormationS1GWExternalOwnerAuthorizationSchemaAudit(
        **values,
        audit_digest=_digest(values),
    )
