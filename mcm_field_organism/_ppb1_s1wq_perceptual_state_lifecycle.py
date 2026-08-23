"""Private S1-WQ lifecycle view over the existing pure PPB-1 kernel."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from ._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    PPB1Readout,
    advance_ppb1_bank,
)
from .receptor_contract import ReceptorContactFrame


S1WQ_SCHEMA_VERSION = "ppb1.s1wq.private.perceptual-state-lifecycle.v1"
S1WQ_REFERENCE_SOURCE_DIGEST = (
    "9fad3b04661fb9b8da053afd5599e3bdfe73019681ae50115263c39f3052ca9d"
)
S1WQ_TRANSITIONS = (
    "PERCEPTUAL_STATE_FORMED",
    "VALID_STATE_CONTINUATION_UPDATED",
    "PERCEPTUAL_STATE_STABILIZED",
    "STABILIZED_STATE_UPDATED",
    "CAPACITY_STATE_DISCARDED_AND_REFORMED",
)
S1WQ_INVALID_INPUT = "S1WQ_INVALID_INPUT"
S1WQ_INVALID_TRANSITION = "S1WQ_INVALID_TRANSITION"
S1WQ_PRODUCTION_EXECUTION_BLOCKED = "S1WQ_PRODUCTION_EXECUTION_BLOCKED"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S1WQLifecycleError(ValueError):
    """One fail-closed S1-WQ lifecycle boundary violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _digest(payload: object) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _state_identity_payload(state: PPB1BankState) -> dict[str, object]:
    return {
        "bank_id": state.bank_id,
        "config_digest": state.config_digest,
        "slot_ids": [slot.slot_id for slot in state.slots],
    }


def _due_slot_ids(
    config: PPB1BankConfig,
    prestate: PPB1BankState,
) -> tuple[str, ...]:
    next_step = prestate.accepted_step_count + 1
    return tuple(
        slot.slot_id
        for slot in prestate.slots
        if (
            slot.occupied
            and slot.last_selected_step is not None
            and next_step - slot.last_selected_step
            >= config.expire_after_steps
        )
    )


def _transition_role(
    config: PPB1BankConfig,
    prestate: PPB1BankState,
    readout: PPB1Readout,
) -> str:
    if readout.event == "CREATED":
        return "PERCEPTUAL_STATE_FORMED"
    if readout.event == "REPLACED":
        return "CAPACITY_STATE_DISCARDED_AND_REFORMED"
    selected_pre = next(
        slot for slot in prestate.slots if slot.slot_id == readout.slot_id
    )
    if selected_pre.support_count is None:
        raise S1WQLifecycleError(
            S1WQ_INVALID_TRANSITION,
            "matched transition requires an occupied selected prestate slot",
        )
    if (
        selected_pre.support_count < config.stable_after
        and readout.support_count == config.stable_after
    ):
        return "PERCEPTUAL_STATE_STABILIZED"
    if selected_pre.support_count >= config.stable_after:
        return "STABILIZED_STATE_UPDATED"
    return "VALID_STATE_CONTINUATION_UPDATED"


@dataclass(frozen=True, slots=True)
class S1WQPerceptualTransitionRecord:
    transition_role: str
    reference_event: str
    bank_id: str
    modality_id: str
    selected_slot_id: str
    state_identity_digest: str
    prestate_digest: str
    input_digest: str
    poststate_digest: str
    reference_readout_digest: str
    formed_slot_id: str | None
    updated_slot_id: str | None
    stabilized_slot_id: str | None
    discarded_slot_ids: tuple[str, ...]
    accepted_step_delta: int
    reference_advance_call_count: int
    partial_commit_count: int
    retry_count: int
    filesystem_operation_count: int
    field_feedback_count: int
    record_digest: str

    def __post_init__(self) -> None:
        digest_roles = (
            self.state_identity_digest,
            self.prestate_digest,
            self.input_digest,
            self.poststate_digest,
            self.reference_readout_digest,
        )
        optional_ids = (
            self.formed_slot_id,
            self.updated_slot_id,
            self.stabilized_slot_id,
        )
        if (
            self.transition_role not in S1WQ_TRANSITIONS
            or self.reference_event not in {"MATCHED", "CREATED", "REPLACED"}
            or not all(
                isinstance(value, str) and value
                for value in (
                    self.bank_id,
                    self.modality_id,
                    self.selected_slot_id,
                )
            )
            or not all(_valid_digest(value) for value in digest_roles)
            or any(
                value is not None
                and (not isinstance(value, str) or not value)
                for value in optional_ids
            )
            or tuple(sorted(set(self.discarded_slot_ids)))
            != self.discarded_slot_ids
            or any(
                not isinstance(value, str) or not value
                for value in self.discarded_slot_ids
            )
            or self.accepted_step_delta != 1
            or self.reference_advance_call_count != 1
            or any(
                value != 0
                for value in (
                    self.partial_commit_count,
                    self.retry_count,
                    self.filesystem_operation_count,
                    self.field_feedback_count,
                )
            )
            or self.record_digest != _digest(self.payload_without_digest())
        ):
            raise S1WQLifecycleError(
                S1WQ_INVALID_TRANSITION,
                "invalid perceptual lifecycle transition record",
            )
        self._validate_role_shape()

    def _validate_role_shape(self) -> None:
        formed = self.transition_role in {
            "PERCEPTUAL_STATE_FORMED",
            "CAPACITY_STATE_DISCARDED_AND_REFORMED",
        }
        updated = self.transition_role in {
            "VALID_STATE_CONTINUATION_UPDATED",
            "PERCEPTUAL_STATE_STABILIZED",
            "STABILIZED_STATE_UPDATED",
        }
        stabilized = self.transition_role == "PERCEPTUAL_STATE_STABILIZED"
        if (
            (self.formed_slot_id == self.selected_slot_id) is not formed
            or (self.updated_slot_id == self.selected_slot_id) is not updated
            or (self.stabilized_slot_id == self.selected_slot_id)
            is not stabilized
            or (
                self.transition_role
                == "CAPACITY_STATE_DISCARDED_AND_REFORMED"
                and self.selected_slot_id not in self.discarded_slot_ids
            )
        ):
            raise S1WQLifecycleError(
                S1WQ_INVALID_TRANSITION,
                "transition role and affected slot roles disagree",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": S1WQ_SCHEMA_VERSION,
            "reference_source_digest": S1WQ_REFERENCE_SOURCE_DIGEST,
            "transition_role": self.transition_role,
            "reference_event": self.reference_event,
            "bank_id": self.bank_id,
            "modality_id": self.modality_id,
            "selected_slot_id": self.selected_slot_id,
            "state_identity_digest": self.state_identity_digest,
            "prestate_digest": self.prestate_digest,
            "input_digest": self.input_digest,
            "poststate_digest": self.poststate_digest,
            "reference_readout_digest": self.reference_readout_digest,
            "formed_slot_id": self.formed_slot_id,
            "updated_slot_id": self.updated_slot_id,
            "stabilized_slot_id": self.stabilized_slot_id,
            "discarded_slot_ids": list(self.discarded_slot_ids),
            "accepted_step_delta": self.accepted_step_delta,
            "reference_advance_call_count": self.reference_advance_call_count,
            "partial_commit_count": self.partial_commit_count,
            "retry_count": self.retry_count,
            "filesystem_operation_count": self.filesystem_operation_count,
            "field_feedback_count": self.field_feedback_count,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "record_digest": self.record_digest,
        }


@dataclass(frozen=True, slots=True)
class S1WQPerceptualStateStepResult:
    poststate: PPB1BankState
    reference_readout: PPB1Readout
    transition: S1WQPerceptualTransitionRecord

    def __post_init__(self) -> None:
        if (
            not isinstance(self.poststate, PPB1BankState)
            or not isinstance(self.reference_readout, PPB1Readout)
            or not isinstance(
                self.transition,
                S1WQPerceptualTransitionRecord,
            )
            or self.reference_readout.poststate_digest
            != self.poststate.digest()
            or self.transition.poststate_digest != self.poststate.digest()
            or self.transition.reference_readout_digest
            != self.reference_readout.digest()
        ):
            raise S1WQLifecycleError(
                S1WQ_INVALID_TRANSITION,
                "poststate, reference readout and transition must commit atomically",
            )


def advance_s1wq_perceptual_state(
    config: PPB1BankConfig,
    prestate: PPB1BankState,
    frame: ReceptorContactFrame,
) -> S1WQPerceptualStateStepResult:
    """Advance the existing PPB-1 kernel once and expose its lifecycle role."""

    if (
        not isinstance(config, PPB1BankConfig)
        or not isinstance(prestate, PPB1BankState)
        or not isinstance(frame, ReceptorContactFrame)
    ):
        raise S1WQLifecycleError(
            S1WQ_INVALID_INPUT,
            "config, prestate and receptor frame are required",
        )
    prestate_digest = prestate.digest()
    state_identity_digest = _digest(_state_identity_payload(prestate))
    due_slot_ids = _due_slot_ids(config, prestate)
    step = advance_ppb1_bank(config, prestate, frame)
    poststate = step.poststate
    readout = step.readout
    if (
        prestate.digest() != prestate_digest
        or _digest(_state_identity_payload(poststate))
        != state_identity_digest
        or poststate.accepted_step_count - prestate.accepted_step_count != 1
        or readout.prestate_digest != prestate_digest
    ):
        raise S1WQLifecycleError(
            S1WQ_INVALID_TRANSITION,
            "reference step violated immutable identity or atomic progression",
        )

    transition_role = _transition_role(config, prestate, readout)
    discarded = set(due_slot_ids)
    if readout.event == "REPLACED":
        discarded.add(readout.slot_id)
    formed = transition_role in {
        "PERCEPTUAL_STATE_FORMED",
        "CAPACITY_STATE_DISCARDED_AND_REFORMED",
    }
    updated = transition_role in {
        "VALID_STATE_CONTINUATION_UPDATED",
        "PERCEPTUAL_STATE_STABILIZED",
        "STABILIZED_STATE_UPDATED",
    }
    stabilized = transition_role == "PERCEPTUAL_STATE_STABILIZED"
    values = {
        "transition_role": transition_role,
        "reference_event": readout.event,
        "bank_id": readout.bank_id,
        "modality_id": readout.modality_id,
        "selected_slot_id": readout.slot_id,
        "state_identity_digest": state_identity_digest,
        "prestate_digest": prestate_digest,
        "input_digest": readout.input_digest,
        "poststate_digest": poststate.digest(),
        "reference_readout_digest": readout.digest(),
        "formed_slot_id": readout.slot_id if formed else None,
        "updated_slot_id": readout.slot_id if updated else None,
        "stabilized_slot_id": readout.slot_id if stabilized else None,
        "discarded_slot_ids": tuple(sorted(discarded)),
        "accepted_step_delta": 1,
        "reference_advance_call_count": 1,
        "partial_commit_count": 0,
        "retry_count": 0,
        "filesystem_operation_count": 0,
        "field_feedback_count": 0,
    }
    payload = {
        "schema_version": S1WQ_SCHEMA_VERSION,
        "reference_source_digest": S1WQ_REFERENCE_SOURCE_DIGEST,
        **{
            key: list(value) if key == "discarded_slot_ids" else value
            for key, value in values.items()
        },
    }
    transition = S1WQPerceptualTransitionRecord(
        **values,
        record_digest=_digest(payload),
    )
    return S1WQPerceptualStateStepResult(
        poststate,
        readout,
        transition,
    )


def execute_s1wq_production_once() -> None:
    raise S1WQLifecycleError(
        S1WQ_PRODUCTION_EXECUTION_BLOCKED,
        "S1-WQ is a private pure lifecycle view without production runtime",
    )
