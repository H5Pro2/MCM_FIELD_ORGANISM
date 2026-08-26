"""S1-GQ separate real-transition schema and shared narrow envelope."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_formation_s1gn_live_field_carrier import (
    E1FormationS1GNLiveFieldCarrier,
    E1FormationS1GNLiveFieldCarrierTransition,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1GQCarrierTransitionSchemaError(ValueError):
    """Raised when a transition crosses its synthetic or real type boundary."""


S1_GQ_REAL_TRANSITION_ID = "e1.real-live-field-carrier-transition.s1gq.v1"
S1_GQ_ENVELOPE_ID = "e1.carrier-transition-envelope.s1gq.v1"
S1_GQ_TRANSITION_KINDS = ("synthetic-no-field-advance", "real-field-advance")
S1_GQ_COMMON_FIELDS = (
    "previous_carrier",
    "next_carrier",
    "binding_digest",
    "batch_index",
    "batch_step_start_tick",
    "batch_step_end_tick",
    "batch_source_support_count",
    "previous_field_digest",
    "next_field_digest",
    "field_object_replaced",
    "accounted_field_steps",
    "actual_field_steps_executed",
    "persistence_performed",
    "claims_permitted",
)


@dataclass(frozen=True, slots=True)
class E1FormationS1GQRealFieldCarrierTransition:
    """Schema for one future real step; this module provides no constructor."""

    transition_id: str
    previous_carrier: E1FormationS1GNLiveFieldCarrier = field(repr=False)
    next_carrier: E1FormationS1GNLiveFieldCarrier = field(repr=False)
    binding_digest: str
    batch_index: int
    batch_step_start_tick: int
    batch_step_end_tick: int
    batch_source_support_count: int
    previous_field_digest: str
    next_field_digest: str
    previous_field_object_carried_explicitly: bool
    next_field_object_carried_explicitly: bool
    synthetic_no_field_advance: bool
    field_object_replaced: bool
    accounted_field_steps: int
    actual_field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    transition_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name
            not in {
                "previous_carrier",
                "next_carrier",
                "transition_digest",
            }
        }
        if (
            self.transition_id != S1_GQ_REAL_TRANSITION_ID
            or not isinstance(
                self.previous_carrier, E1FormationS1GNLiveFieldCarrier
            )
            or not isinstance(self.next_carrier, E1FormationS1GNLiveFieldCarrier)
            or self.binding_digest != self.previous_carrier.binding_digest
            or self.binding_digest != self.next_carrier.binding_digest
            or self.previous_carrier.fresh_binding
            is not self.next_carrier.fresh_binding
            or self.batch_index != self.previous_carrier.completed_batch_count
            or self.batch_step_start_tick < 0
            or self.batch_step_end_tick <= self.batch_step_start_tick
            or self.batch_source_support_count < 0
            or self.previous_field_digest
            != self.previous_carrier.current_field_digest
            or self.next_field_digest != self.next_carrier.current_field_digest
            or self.previous_field_digest == self.next_field_digest
            or self.next_carrier.completed_batch_count
            != self.previous_carrier.completed_batch_count + 1
            or self.next_carrier.accounted_source_support_count
            != self.previous_carrier.accounted_source_support_count
            + self.batch_source_support_count
            or self.next_carrier.actual_field_steps_executed
            != self.previous_carrier.actual_field_steps_executed + 1
            or any(
                value is not True
                for value in (
                    self.previous_field_object_carried_explicitly,
                    self.next_field_object_carried_explicitly,
                    self.field_object_replaced,
                )
            )
            or self.synthetic_no_field_advance is not False
            or self.next_carrier.current_field
            is self.previous_carrier.current_field
            or self.accounted_field_steps != 1
            or self.actual_field_steps_executed != 1
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.transition_digest != _digest(payload)
        ):
            raise E1FormationS1GQCarrierTransitionSchemaError(
                "S1-GQ real transition lost explicit one-step field causality"
            )


CarrierTransition = (
    E1FormationS1GNLiveFieldCarrierTransition
    | E1FormationS1GQRealFieldCarrierTransition
)


@dataclass(frozen=True, slots=True)
class E1FormationS1GQCarrierTransitionEnvelope:
    envelope_id: str
    transition_kind: str
    transition_type_name: str
    transition_digest: str
    previous_carrier: E1FormationS1GNLiveFieldCarrier = field(repr=False)
    next_carrier: E1FormationS1GNLiveFieldCarrier = field(repr=False)
    binding_digest: str
    batch_index: int
    batch_step_start_tick: int
    batch_step_end_tick: int
    batch_source_support_count: int
    previous_field_digest: str
    next_field_digest: str
    field_object_replaced: bool
    accounted_field_steps: int
    actual_field_steps_executed: int
    persistence_performed: bool
    claims_permitted: bool
    envelope_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name
            not in {
                "previous_carrier",
                "next_carrier",
                "envelope_digest",
            }
        }
        synthetic = self.transition_kind == S1_GQ_TRANSITION_KINDS[0]
        real = self.transition_kind == S1_GQ_TRANSITION_KINDS[1]
        if (
            self.envelope_id != S1_GQ_ENVELOPE_ID
            or not (synthetic or real)
            or self.transition_type_name
            not in {
                E1FormationS1GNLiveFieldCarrierTransition.__name__,
                E1FormationS1GQRealFieldCarrierTransition.__name__,
            }
            or len(self.transition_digest) != 64
            or not isinstance(
                self.previous_carrier, E1FormationS1GNLiveFieldCarrier
            )
            or not isinstance(self.next_carrier, E1FormationS1GNLiveFieldCarrier)
            or self.binding_digest != self.previous_carrier.binding_digest
            or self.binding_digest != self.next_carrier.binding_digest
            or self.batch_index != self.previous_carrier.completed_batch_count
            or self.batch_step_start_tick < 0
            or self.batch_step_end_tick <= self.batch_step_start_tick
            or self.batch_source_support_count < 0
            or self.previous_field_digest
            != self.previous_carrier.current_field_digest
            or self.next_field_digest != self.next_carrier.current_field_digest
            or self.next_carrier.completed_batch_count
            != self.previous_carrier.completed_batch_count + 1
            or self.next_carrier.accounted_source_support_count
            != self.previous_carrier.accounted_source_support_count
            + self.batch_source_support_count
            or self.accounted_field_steps != 1
            or self.actual_field_steps_executed != (0 if synthetic else 1)
            or self.field_object_replaced is not real
            or (
                self.next_carrier.current_field
                is self.previous_carrier.current_field
            )
            is not synthetic
            or self.persistence_performed is not False
            or self.claims_permitted is not False
            or self.envelope_digest != _digest(payload)
        ):
            raise E1FormationS1GQCarrierTransitionSchemaError(
                "S1-GQ envelope merged synthetic and real transition semantics"
            )


def bind_e1_formation_s1gq_carrier_transition_envelope(
    transition: CarrierTransition,
) -> E1FormationS1GQCarrierTransitionEnvelope:
    """Normalize one typed transition without advancing or copying its field."""

    if isinstance(transition, E1FormationS1GNLiveFieldCarrierTransition):
        transition.__post_init__()
        kind = S1_GQ_TRANSITION_KINDS[0]
    elif isinstance(transition, E1FormationS1GQRealFieldCarrierTransition):
        transition.__post_init__()
        kind = S1_GQ_TRANSITION_KINDS[1]
    else:
        raise E1FormationS1GQCarrierTransitionSchemaError(
            "S1-GQ accepts only the exact synthetic or real transition type"
        )
    values = {
        "envelope_id": S1_GQ_ENVELOPE_ID,
        "transition_kind": kind,
        "transition_type_name": type(transition).__name__,
        "transition_digest": transition.transition_digest,
        "previous_carrier": transition.previous_carrier,
        "next_carrier": transition.next_carrier,
        "binding_digest": transition.binding_digest,
        "batch_index": transition.batch_index,
        "batch_step_start_tick": transition.batch_step_start_tick,
        "batch_step_end_tick": transition.batch_step_end_tick,
        "batch_source_support_count": transition.batch_source_support_count,
        "previous_field_digest": transition.previous_field_digest,
        "next_field_digest": transition.next_field_digest,
        "field_object_replaced": transition.field_object_replaced,
        "accounted_field_steps": transition.accounted_field_steps,
        "actual_field_steps_executed": transition.actual_field_steps_executed,
        "persistence_performed": transition.persistence_performed,
        "claims_permitted": transition.claims_permitted,
    }
    payload = {
        name: value
        for name, value in values.items()
        if name not in {"previous_carrier", "next_carrier"}
    }
    return E1FormationS1GQCarrierTransitionEnvelope(
        **values,
        envelope_digest=_digest(payload),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1GQCarrierTransitionSchemaAudit:
    common_fields: tuple[str, ...]
    transition_kinds: tuple[str, ...]
    synthetic_fields_complete: bool
    real_fields_complete: bool
    separate_semantics_enforced: bool
    shared_envelope_implemented: bool
    real_transition_builder_present: bool
    adapter_import_present: bool
    execution_permitted: bool
    persistence_performed: bool
    claims_permitted: bool
    decision: str
    audit_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "audit_digest"
        }
        if (
            self.common_fields != S1_GQ_COMMON_FIELDS
            or self.transition_kinds != S1_GQ_TRANSITION_KINDS
            or any(
                value is not True
                for value in (
                    self.synthetic_fields_complete,
                    self.real_fields_complete,
                    self.separate_semantics_enforced,
                    self.shared_envelope_implemented,
                )
            )
            or any(
                value is not False
                for value in (
                    self.real_transition_builder_present,
                    self.adapter_import_present,
                    self.execution_permitted,
                    self.persistence_performed,
                    self.claims_permitted,
                )
            )
            or self.decision
            != "SEPARATE_REAL_TRANSITION_SCHEMA_AND_SHARED_ENVELOPE_READY"
            or self.audit_digest != _digest(payload)
        ):
            raise E1FormationS1GQCarrierTransitionSchemaError(
                "S1-GQ schema audit changed or opened execution"
            )


def audit_e1_formation_s1gq_carrier_transition_schema(
) -> E1FormationS1GQCarrierTransitionSchemaAudit:
    """Report the type-only boundary; no real transition is constructed."""

    synthetic_fields = set(
        E1FormationS1GNLiveFieldCarrierTransition.__dataclass_fields__
    )
    real_fields = set(
        E1FormationS1GQRealFieldCarrierTransition.__dataclass_fields__
    )
    values = {
        "common_fields": S1_GQ_COMMON_FIELDS,
        "transition_kinds": S1_GQ_TRANSITION_KINDS,
        "synthetic_fields_complete": set(S1_GQ_COMMON_FIELDS).issubset(
            synthetic_fields
        ),
        "real_fields_complete": set(S1_GQ_COMMON_FIELDS).issubset(real_fields),
        "separate_semantics_enforced": True,
        "shared_envelope_implemented": True,
        "real_transition_builder_present": False,
        "adapter_import_present": False,
        "execution_permitted": False,
        "persistence_performed": False,
        "claims_permitted": False,
        "decision": (
            "SEPARATE_REAL_TRANSITION_SCHEMA_AND_SHARED_ENVELOPE_READY"
        ),
    }
    return E1FormationS1GQCarrierTransitionSchemaAudit(
        **values,
        audit_digest=_digest(values),
    )
