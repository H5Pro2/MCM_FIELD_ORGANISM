"""S1-HB ingress bridge for externally verified owner authorization events."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .e1_formation_s1gs_real_single_batch_gate_contract import (
    E1FormationS1GSRealSingleBatchGateContract,
)
from .e1_formation_s1gw_external_owner_authorization_schema import (
    E1FormationS1GWExternalOwnerAuthorization,
    S1_GW_AUTHORIZATION_ID,
    S1_GW_NON_AUTHORIZATION_MESSAGES,
    S1_GW_PROJECT_ID,
    S1_GW_REQUIRED_OWNER_CLAUSES,
)
from .e1_formation_s1gx_deterministic_single_batch_target import (
    E1FormationS1GXDeterministicSingleBatchTarget,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1HBExternalOwnerOriginBridgeError(ValueError):
    """Raised when external origin or exact authorization scope is absent."""


S1_HB_EVENT_ID = "e1.external-owner-origin-event.s1hb.v1"
S1_HB_ORIGIN_KIND = "external-host-owner-message"


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def _normalize_owner_message(message: str) -> str:
    if not isinstance(message, str) or not message.strip():
        raise E1FormationS1HBExternalOwnerOriginBridgeError(
            "S1-HB requires one nonempty owner message"
        )
    return " ".join(message.strip().lower().split())


@dataclass(frozen=True, slots=True)
class E1FormationS1HBExternalOwnerOriginEvent:
    """Host-produced event shape; construction alone proves no authenticity."""

    event_id: str
    origin_kind: str
    host_provider_id: str
    authenticated_owner_principal_digest: str
    task_or_session_binding_digest: str
    fresh_single_use_nonce_digest: str
    host_attestation_digest: str
    owner_message_digest: str
    project_id: str
    run_id: str
    gate_digest: str
    binding_digest: str
    batch_index: int
    carrier_digest: str
    maximum_adapter_calls: int
    maximum_field_steps: int
    required_owner_clauses: tuple[str, ...]
    explicit_owner_message: bool
    single_use: bool
    non_persistent: bool
    retry_permitted: bool
    reparametrization_permitted: bool
    partial_return_permitted: bool
    claims_permitted: bool
    expires_after_success_or_failure: bool
    host_sequence: int
    event_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "event_digest"
        }
        if (
            self.event_id != S1_HB_EVENT_ID
            or self.origin_kind != S1_HB_ORIGIN_KIND
            or not self.host_provider_id
            or not all(
                _valid_digest(value)
                for value in (
                    self.authenticated_owner_principal_digest,
                    self.task_or_session_binding_digest,
                    self.fresh_single_use_nonce_digest,
                    self.host_attestation_digest,
                    self.owner_message_digest,
                    self.gate_digest,
                    self.binding_digest,
                    self.carrier_digest,
                )
            )
            or self.project_id != S1_GW_PROJECT_ID
            or not self.run_id.startswith("S1-G")
            or isinstance(self.batch_index, bool)
            or not isinstance(self.batch_index, int)
            or self.batch_index < 0
            or self.maximum_adapter_calls != 1
            or self.maximum_field_steps != 1
            or self.required_owner_clauses != S1_GW_REQUIRED_OWNER_CLAUSES
            or any(
                value is not True
                for value in (
                    self.explicit_owner_message,
                    self.single_use,
                    self.non_persistent,
                    self.expires_after_success_or_failure,
                )
            )
            or any(
                value is not False
                for value in (
                    self.retry_permitted,
                    self.reparametrization_permitted,
                    self.partial_return_permitted,
                    self.claims_permitted,
                )
            )
            or isinstance(self.host_sequence, bool)
            or not isinstance(self.host_sequence, int)
            or self.host_sequence < 1
            or self.event_digest != _digest(payload)
        ):
            raise E1FormationS1HBExternalOwnerOriginBridgeError(
                "S1-HB external event lost origin evidence or exact scope"
            )


ExternalOriginVerifier = Callable[
    [E1FormationS1HBExternalOwnerOriginEvent],
    bool,
]


def bind_e1_formation_s1hb_external_owner_authorization(
    owner_message: str,
    origin_event: E1FormationS1HBExternalOwnerOriginEvent,
    gate: E1FormationS1GSRealSingleBatchGateContract,
    target: E1FormationS1GXDeterministicSingleBatchTarget,
    *,
    origin_verifier: ExternalOriginVerifier,
) -> E1FormationS1GWExternalOwnerAuthorization:
    """Bind a host-verified event; never infer origin from message text alone."""

    if (
        not isinstance(origin_event, E1FormationS1HBExternalOwnerOriginEvent)
        or not isinstance(gate, E1FormationS1GSRealSingleBatchGateContract)
        or not isinstance(target, E1FormationS1GXDeterministicSingleBatchTarget)
        or not callable(origin_verifier)
    ):
        raise E1FormationS1HBExternalOwnerOriginBridgeError(
            "S1-HB requires event, gate, target, and external verifier"
        )
    normalized = _normalize_owner_message(owner_message)
    if normalized in S1_GW_NON_AUTHORIZATION_MESSAGES:
        raise E1FormationS1HBExternalOwnerOriginBridgeError(
            "S1-HB continuation messages are not owner authorization"
        )
    origin_event.__post_init__()
    gate.__post_init__()
    target.__post_init__()
    try:
        externally_verified = origin_verifier(origin_event)
    except Exception as exc:
        raise E1FormationS1HBExternalOwnerOriginBridgeError(
            "S1-HB external origin verifier failed closed"
        ) from exc
    event = origin_event
    if (
        externally_verified is not True
        or event.owner_message_digest != _digest(normalized)
        or event.project_id != S1_GW_PROJECT_ID
        or event.run_id != target.run_id
        or event.gate_digest != gate.gate_digest
        or event.binding_digest != target.selected_binding_digest
        or event.batch_index != target.selected_batch_index
        or event.carrier_digest != target.selected_carrier_digest
        or event.maximum_adapter_calls != target.maximum_adapter_calls
        or event.maximum_field_steps != target.maximum_field_steps
        or event.required_owner_clauses != S1_GW_REQUIRED_OWNER_CLAUSES
        or event.explicit_owner_message is not True
    ):
        raise E1FormationS1HBExternalOwnerOriginBridgeError(
            "S1-HB external event is unverified or not bound to the exact target"
        )
    values = {
        "authorization_id": S1_GW_AUTHORIZATION_ID,
        "external_origin_receipt_digest": event.event_digest,
        "owner_message_digest": event.owner_message_digest,
        "project_id": event.project_id,
        "run_id": event.run_id,
        "gate_digest": event.gate_digest,
        "binding_digest": event.binding_digest,
        "batch_index": event.batch_index,
        "carrier_digest": event.carrier_digest,
        "maximum_adapter_calls": event.maximum_adapter_calls,
        "maximum_field_steps": event.maximum_field_steps,
        "single_use": event.single_use,
        "non_persistent": event.non_persistent,
        "retry_permitted": event.retry_permitted,
        "reparametrization_permitted": event.reparametrization_permitted,
        "partial_return_permitted": event.partial_return_permitted,
        "claims_permitted": event.claims_permitted,
        "expires_after_success_or_failure": (
            event.expires_after_success_or_failure
        ),
    }
    return E1FormationS1GWExternalOwnerAuthorization(
        **values,
        authorization_digest=_digest(values),
    )
