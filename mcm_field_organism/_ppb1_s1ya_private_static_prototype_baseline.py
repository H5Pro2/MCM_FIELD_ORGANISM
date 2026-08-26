"""Private frozen static-prototype baseline for the S1-XZ fixture."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from ._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    _digest,
    _input_projection,
    _validate_frame,
    initial_ppb1_bank_state,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import (
    S1WQPerceptualTransitionRecord,
    _state_identity_payload,
    advance_s1wq_perceptual_state,
)
from ._ppb1_s1xz_private_temporal_update_fixture import (
    S1XZHistoryPlan,
    S1XZModalityFixture,
)
from .receptor_contract import ReceptorContactFrame


S1YA_SCHEMA_VERSION = "ppb1.s1ya.private-static-prototype-baseline.v1"
S1YA_PREFLIGHT_DIGEST = (
    "1bf316628b75ca6ee11fb05f290713b30b758c7a35b9cb9ede19b3142c577d06"
)
S1YA_FIXTURE_BUNDLE_DIGEST = (
    "0aac41828eb64ba0f2dfc8488ba6d9c1c636998cb66023ad6bc488a0671bbadb"
)
S1YA_INVALID_BASELINE = "S1YA_INVALID_STATIC_PROTOTYPE_BASELINE"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S1YAStaticPrototypeBaselineError(ValueError):
    """One fail-closed static baseline violation."""

    def __init__(self, detail: str) -> None:
        self.code = S1YA_INVALID_BASELINE
        self.detail = detail
        super().__init__(f"{self.code}: {detail}")


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _receipt_digest(payload: dict[str, object]) -> str:
    return _digest(
        {
            "schema_version": S1YA_SCHEMA_VERSION,
            "preflight_digest": S1YA_PREFLIGHT_DIGEST,
            "fixture_bundle_digest": S1YA_FIXTURE_BUNDLE_DIGEST,
            **payload,
        }
    )


def _value_map(modality: S1XZModalityFixture) -> dict[str, float]:
    return dict(modality.named_scalar_values)


def _config(
    modality: S1XZModalityFixture,
    plan: S1XZHistoryPlan,
) -> PPB1BankConfig:
    prefix = f"s1ya.{modality.modality_id}.{plan.history_id.lower()}"
    return PPB1BankConfig(
        f"ppb1.{prefix}",
        modality.modality_id,
        f"geometry.{prefix}",
        tuple(
            f"carrier.{prefix}.{index:03d}"
            for index in range(modality.carrier_count)
        ),
        modality.capacity,
        modality.match_threshold,
        modality.update_rate,
        modality.stable_after,
        modality.expire_after_steps,
    )


def _frame(
    config: PPB1BankConfig,
    history_id: str,
    role: str,
    scalar: float,
    start_tick: int,
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        config.modality_id,
        config.geometry_id,
        f"receptor.s1ya.{config.modality_id}.{history_id.lower()}.{role}",
        f"clock.s1ya.{config.modality_id}.{history_id.lower()}",
        start_tick,
        start_tick + 1,
        config.carrier_ids,
        (scalar,) * len(config.carrier_ids),
    )


@dataclass(frozen=True, slots=True)
class S1YABaselineFreezeReceipt:
    plan_id: str
    plan_digest: str
    config_digest: str
    frozen_state_digest: str
    state_identity_digest: str
    ordered_formation_events: tuple[str, ...]
    occupied_slot_count: int
    stabilized_slot_count: int
    frozen_after_formation: bool
    freeze_receipt_digest: str

    def __post_init__(self) -> None:
        if (
            not self.plan_id.startswith("s1xz.")
            or not all(
                _valid_digest(value)
                for value in (
                    self.plan_digest,
                    self.config_digest,
                    self.frozen_state_digest,
                    self.state_identity_digest,
                )
            )
            or not self.ordered_formation_events
            or any(event not in {"CREATED", "MATCHED"} for event in self.ordered_formation_events)
            or self.occupied_slot_count not in {1, 2}
            or self.stabilized_slot_count != self.occupied_slot_count
            or not self.frozen_after_formation
            or self.freeze_receipt_digest
            != _receipt_digest(self.payload_without_digest())
        ):
            raise S1YAStaticPrototypeBaselineError("invalid freeze receipt")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "plan_digest": self.plan_digest,
            "config_digest": self.config_digest,
            "frozen_state_digest": self.frozen_state_digest,
            "state_identity_digest": self.state_identity_digest,
            "ordered_formation_events": list(self.ordered_formation_events),
            "occupied_slot_count": self.occupied_slot_count,
            "stabilized_slot_count": self.stabilized_slot_count,
            "frozen_after_formation": self.frozen_after_formation,
        }


@dataclass(frozen=True, slots=True)
class S1YAFrozenBaselineCarry:
    config: PPB1BankConfig
    frozen_state: PPB1BankState
    plan_id: str
    plan_digest: str
    expected_update_roles: tuple[str, ...]
    expected_update_scalars: tuple[float, ...]
    formation_end_tick: int
    received_update_count: int
    last_received_window_end_tick: int
    frozen_state_digest: str
    state_identity_digest: str
    carry_digest: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.config, PPB1BankConfig)
            or not isinstance(self.frozen_state, PPB1BankState)
            or self.frozen_state.bank_id != self.config.bank_id
            or self.frozen_state.config_digest != self.config.digest()
            or self.frozen_state.digest() != self.frozen_state_digest
            or _digest(_state_identity_payload(self.frozen_state))
            != self.state_identity_digest
            or not self.plan_id.startswith("s1xz.")
            or not _valid_digest(self.plan_digest)
            or len(self.expected_update_roles) != len(self.expected_update_scalars)
            or not all(
                isinstance(role, str) and role
                for role in self.expected_update_roles
            )
            or not all(
                isinstance(value, float)
                and math.isfinite(value)
                and abs(value) <= 1.0
                for value in self.expected_update_scalars
            )
            or isinstance(self.formation_end_tick, bool)
            or self.formation_end_tick <= 0
            or isinstance(self.received_update_count, bool)
            or self.received_update_count < 0
            or self.received_update_count > len(self.expected_update_roles)
            or self.last_received_window_end_tick
            != self.formation_end_tick + self.received_update_count
            or self.carry_digest != _receipt_digest(self.payload_without_digest())
        ):
            raise S1YAStaticPrototypeBaselineError("invalid frozen baseline carry")

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "config_digest": self.config.digest(),
            "frozen_state_digest": self.frozen_state_digest,
            "plan_id": self.plan_id,
            "plan_digest": self.plan_digest,
            "expected_update_roles": list(self.expected_update_roles),
            "expected_update_scalars": list(self.expected_update_scalars),
            "formation_end_tick": self.formation_end_tick,
            "received_update_count": self.received_update_count,
            "last_received_window_end_tick": self.last_received_window_end_tick,
            "state_identity_digest": self.state_identity_digest,
        }


@dataclass(frozen=True, slots=True)
class S1YABaselineFormationResult:
    config: PPB1BankConfig
    carry: S1YAFrozenBaselineCarry
    formation_transitions: tuple[S1WQPerceptualTransitionRecord, ...]
    freeze_receipt: S1YABaselineFreezeReceipt

    def __post_init__(self) -> None:
        if (
            self.config != self.carry.config
            or not self.formation_transitions
            or tuple(
                item.reference_event for item in self.formation_transitions
            )
            != self.freeze_receipt.ordered_formation_events
            or self.freeze_receipt.config_digest != self.config.digest()
            or self.freeze_receipt.frozen_state_digest
            != self.carry.frozen_state_digest
            or self.freeze_receipt.plan_digest != self.carry.plan_digest
        ):
            raise S1YAStaticPrototypeBaselineError(
                "formation result is not atomic"
            )


@dataclass(frozen=True, slots=True)
class S1YAFrozenExposureReceipt:
    plan_id: str
    plan_digest: str
    modality_id: str
    history_id: str
    update_ordinal: int
    expected_role: str
    expected_scalar: float
    input_digest: str
    window_start_tick: int
    window_end_tick: int
    prestate_digest: str
    poststate_digest: str
    pre_carry_digest: str
    post_carry_digest: str
    state_unchanged: bool
    prototype_update_count: int
    expiration_count: int
    replacement_count: int
    exposure_receipt_digest: str

    def __post_init__(self) -> None:
        if (
            not self.plan_id.startswith("s1xz.")
            or not _valid_digest(self.plan_digest)
            or self.modality_id not in {"auditory", "visual"}
            or self.history_id not in {"H1", "H2", "H3", "H4", "H5"}
            or isinstance(self.update_ordinal, bool)
            or self.update_ordinal <= 0
            or not self.expected_role
            or isinstance(self.expected_scalar, bool)
            or not isinstance(self.expected_scalar, float)
            or not math.isfinite(self.expected_scalar)
            or not all(
                _valid_digest(value)
                for value in (
                    self.input_digest,
                    self.prestate_digest,
                    self.poststate_digest,
                    self.pre_carry_digest,
                    self.post_carry_digest,
                )
            )
            or self.window_end_tick != self.window_start_tick + 1
            or self.prestate_digest != self.poststate_digest
            or not self.state_unchanged
            or any(
                value != 0
                for value in (
                    self.prototype_update_count,
                    self.expiration_count,
                    self.replacement_count,
                )
            )
            or self.exposure_receipt_digest
            != _receipt_digest(self.payload_without_digest())
        ):
            raise S1YAStaticPrototypeBaselineError(
                "invalid frozen exposure receipt"
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "plan_digest": self.plan_digest,
            "modality_id": self.modality_id,
            "history_id": self.history_id,
            "update_ordinal": self.update_ordinal,
            "expected_role": self.expected_role,
            "expected_scalar": self.expected_scalar,
            "input_digest": self.input_digest,
            "window_start_tick": self.window_start_tick,
            "window_end_tick": self.window_end_tick,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "pre_carry_digest": self.pre_carry_digest,
            "post_carry_digest": self.post_carry_digest,
            "state_unchanged": self.state_unchanged,
            "prototype_update_count": self.prototype_update_count,
            "expiration_count": self.expiration_count,
            "replacement_count": self.replacement_count,
        }


@dataclass(frozen=True, slots=True)
class S1YAFrozenExposureResult:
    carry: S1YAFrozenBaselineCarry
    receipt: S1YAFrozenExposureReceipt

    def __post_init__(self) -> None:
        if (
            self.receipt.post_carry_digest != self.carry.carry_digest
            or self.receipt.poststate_digest != self.carry.frozen_state_digest
        ):
            raise S1YAStaticPrototypeBaselineError(
                "frozen exposure result is not atomic"
            )


def form_s1ya_static_baseline(
    modality: S1XZModalityFixture,
    plan: S1XZHistoryPlan,
) -> S1YABaselineFormationResult:
    """Form one baseline from its bound prefix and freeze it."""

    if (
        not isinstance(modality, S1XZModalityFixture)
        or not isinstance(plan, S1XZHistoryPlan)
        or plan.modality_id != modality.modality_id
    ):
        raise S1YAStaticPrototypeBaselineError(
            "matching modality fixture and history plan are required"
        )
    config = _config(modality, plan)
    state = initial_ppb1_bank_state(config)
    values = _value_map(modality)
    transitions = []
    events = []
    for index, role in enumerate(plan.formation_roles):
        step = advance_s1wq_perceptual_state(
            config,
            state,
            _frame(config, plan.history_id, role, values[role], index),
        )
        state = step.poststate
        transitions.append(step.transition)
        events.append(step.reference_readout.event)
    expected_events = plan.expected_candidate_events[: len(plan.formation_roles)]
    occupied = tuple(slot for slot in state.slots if slot.occupied)
    stabilized = tuple(
        slot
        for slot in occupied
        if slot.support_count is not None
        and slot.support_count >= config.stable_after
    )
    if (
        tuple(events) != expected_events
        or tuple(slot.prototype_values[0] for slot in occupied)
        != plan.expected_baseline_prototypes
        or len(stabilized) != len(occupied)
    ):
        raise S1YAStaticPrototypeBaselineError(
            "formation differs from static baseline fixture"
        )
    state_digest = state.digest()
    identity_digest = _digest(_state_identity_payload(state))
    freeze_values = {
        "plan_id": plan.plan_id,
        "plan_digest": plan.plan_digest,
        "config_digest": config.digest(),
        "frozen_state_digest": state_digest,
        "state_identity_digest": identity_digest,
        "ordered_formation_events": tuple(events),
        "occupied_slot_count": len(occupied),
        "stabilized_slot_count": len(stabilized),
        "frozen_after_formation": True,
    }
    freeze_receipt = S1YABaselineFreezeReceipt(
        **freeze_values,
        freeze_receipt_digest=_receipt_digest(freeze_values),
    )
    scalars = tuple(values[role] for role in plan.update_roles)
    carry_values = {
        "config": config,
        "frozen_state": state,
        "plan_id": plan.plan_id,
        "plan_digest": plan.plan_digest,
        "expected_update_roles": plan.update_roles,
        "expected_update_scalars": scalars,
        "formation_end_tick": len(plan.formation_roles),
        "received_update_count": 0,
        "last_received_window_end_tick": len(plan.formation_roles),
        "frozen_state_digest": state_digest,
        "state_identity_digest": identity_digest,
    }
    carry = S1YAFrozenBaselineCarry(
        **carry_values,
        carry_digest=_receipt_digest(
            {
                "config_digest": config.digest(),
                "frozen_state_digest": state_digest,
                "plan_id": plan.plan_id,
                "plan_digest": plan.plan_digest,
                "expected_update_roles": list(plan.update_roles),
                "expected_update_scalars": list(scalars),
                "formation_end_tick": len(plan.formation_roles),
                "received_update_count": 0,
                "last_received_window_end_tick": len(plan.formation_roles),
                "state_identity_digest": identity_digest,
            }
        ),
    )
    return S1YABaselineFormationResult(
        config,
        carry,
        tuple(transitions),
        freeze_receipt,
    )


def receive_s1ya_frozen_exposure(
    carry: S1YAFrozenBaselineCarry,
    frame: ReceptorContactFrame,
    expected_role: str,
) -> S1YAFrozenExposureResult:
    """Receipt one bound update exposure without changing the bank state."""

    if not isinstance(carry, S1YAFrozenBaselineCarry):
        raise S1YAStaticPrototypeBaselineError("frozen carry is required")
    index = carry.received_update_count
    if index >= len(carry.expected_update_roles):
        raise S1YAStaticPrototypeBaselineError("all bound updates are already received")
    role = carry.expected_update_roles[index]
    scalar = carry.expected_update_scalars[index]
    if expected_role != role:
        raise S1YAStaticPrototypeBaselineError("update role is out of order")
    validated = _validate_frame(carry.config, frame)
    if (
        validated.clock_id != carry.frozen_state.source_clock_id
        or validated.window_start_tick != carry.last_received_window_end_tick
        or validated.window_end_tick != validated.window_start_tick + 1
        or tuple(validated.values)
        != (scalar,) * len(carry.config.carrier_ids)
    ):
        raise S1YAStaticPrototypeBaselineError(
            "frozen exposure differs from bound value or clock order"
        )
    before_state = carry.frozen_state.digest()
    carry_values = {
        "config": carry.config,
        "frozen_state": carry.frozen_state,
        "plan_id": carry.plan_id,
        "plan_digest": carry.plan_digest,
        "expected_update_roles": carry.expected_update_roles,
        "expected_update_scalars": carry.expected_update_scalars,
        "formation_end_tick": carry.formation_end_tick,
        "received_update_count": index + 1,
        "last_received_window_end_tick": validated.window_end_tick,
        "frozen_state_digest": carry.frozen_state_digest,
        "state_identity_digest": carry.state_identity_digest,
    }
    next_carry_payload = {
        "config_digest": carry.config.digest(),
        "frozen_state_digest": carry.frozen_state_digest,
        "plan_id": carry.plan_id,
        "plan_digest": carry.plan_digest,
        "expected_update_roles": list(carry.expected_update_roles),
        "expected_update_scalars": list(carry.expected_update_scalars),
        "formation_end_tick": carry.formation_end_tick,
        "received_update_count": index + 1,
        "last_received_window_end_tick": validated.window_end_tick,
        "state_identity_digest": carry.state_identity_digest,
    }
    next_carry = S1YAFrozenBaselineCarry(
        **carry_values,
        carry_digest=_receipt_digest(next_carry_payload),
    )
    receipt_values = {
        "plan_id": carry.plan_id,
        "plan_digest": carry.plan_digest,
        "modality_id": carry.config.modality_id,
        "history_id": carry.plan_id.rsplit(".", 1)[-1].upper(),
        "update_ordinal": index + 1,
        "expected_role": role,
        "expected_scalar": scalar,
        "input_digest": _digest(_input_projection(validated)),
        "window_start_tick": validated.window_start_tick,
        "window_end_tick": validated.window_end_tick,
        "prestate_digest": before_state,
        "poststate_digest": carry.frozen_state.digest(),
        "pre_carry_digest": carry.carry_digest,
        "post_carry_digest": next_carry.carry_digest,
        "state_unchanged": before_state == carry.frozen_state.digest(),
        "prototype_update_count": 0,
        "expiration_count": 0,
        "replacement_count": 0,
    }
    receipt = S1YAFrozenExposureReceipt(
        **receipt_values,
        exposure_receipt_digest=_receipt_digest(receipt_values),
    )
    return S1YAFrozenExposureResult(next_carry, receipt)
