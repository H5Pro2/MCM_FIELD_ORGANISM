"""Private pure PPB-1 reference bank for reduced receptor states."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from .receptor_contract import ReceptorContactFrame


PPB1_SCHEMA_VERSION = "ppb1.private.v1"
PPB1_EVENTS = ("MATCHED", "CREATED", "REPLACED")

PPB1_INVALID_CONFIG = "PPB1_INVALID_CONFIG"
PPB1_INVALID_SLOT = "PPB1_INVALID_SLOT"
PPB1_INVALID_STATE = "PPB1_INVALID_STATE"
PPB1_INVALID_INPUT = "PPB1_INVALID_INPUT"
PPB1_CLOCK_ORDER = "PPB1_CLOCK_ORDER"
PPB1_ATOMIC_OUTPUT_REQUIRED = "PPB1_ATOMIC_OUTPUT_REQUIRED"

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


class PPB1ReferenceError(ValueError):
    """One fail-closed PPB-1 contract violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _identifier(value: object, role: str, code: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise PPB1ReferenceError(code, f"{role} must be a technical identifier")
    return value


def _positive_integer(value: object, role: str, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise PPB1ReferenceError(code, f"{role} must be a positive integer")
    return value


def _nonnegative_integer(value: object, role: str, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PPB1ReferenceError(code, f"{role} must be a nonnegative integer")
    return value


def _finite(value: object, role: str, code: str) -> float:
    if isinstance(value, bool):
        raise PPB1ReferenceError(code, f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise PPB1ReferenceError(code, f"{role} must be numeric") from exc
    if not math.isfinite(result):
        raise PPB1ReferenceError(code, f"{role} must be finite")
    return result


def _bounded_values(values: object, role: str, code: str) -> tuple[float, ...]:
    try:
        result = tuple(_finite(value, role, code) for value in values)  # type: ignore[arg-type]
    except TypeError as exc:
        raise PPB1ReferenceError(code, f"{role} must be iterable") from exc
    if not result or any(abs(value) > 1.0 for value in result):
        raise PPB1ReferenceError(code, f"{role} must be non-empty and in [-1,1]")
    return result


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class PPB1BankConfig:
    bank_id: str
    modality_id: str
    geometry_id: str
    carrier_ids: tuple[str, ...]
    capacity: int
    match_threshold: float
    update_rate: float
    stable_after: int
    expire_after_steps: int
    schema_version: str = PPB1_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != PPB1_SCHEMA_VERSION:
            raise PPB1ReferenceError(
                PPB1_INVALID_CONFIG, "schema_version does not match PPB-1 v1"
            )
        object.__setattr__(
            self,
            "bank_id",
            _identifier(self.bank_id, "bank_id", PPB1_INVALID_CONFIG),
        )
        if self.modality_id not in {"auditory", "visual"}:
            raise PPB1ReferenceError(
                PPB1_INVALID_CONFIG, "modality_id must be auditory or visual"
            )
        object.__setattr__(
            self,
            "geometry_id",
            _identifier(self.geometry_id, "geometry_id", PPB1_INVALID_CONFIG),
        )
        carrier_ids = tuple(self.carrier_ids)
        if not carrier_ids or len(set(carrier_ids)) != len(carrier_ids):
            raise PPB1ReferenceError(
                PPB1_INVALID_CONFIG,
                "carrier_ids must be non-empty and unique",
            )
        for carrier_id in carrier_ids:
            _identifier(carrier_id, "carrier_id", PPB1_INVALID_CONFIG)
        capacity = _positive_integer(
            self.capacity, "capacity", PPB1_INVALID_CONFIG
        )
        threshold = _finite(
            self.match_threshold, "match_threshold", PPB1_INVALID_CONFIG
        )
        if threshold < 0.0 or threshold > 2.0:
            raise PPB1ReferenceError(
                PPB1_INVALID_CONFIG, "match_threshold must be in [0,2]"
            )
        update_rate = _finite(
            self.update_rate, "update_rate", PPB1_INVALID_CONFIG
        )
        if update_rate <= 0.0 or update_rate > 1.0:
            raise PPB1ReferenceError(
                PPB1_INVALID_CONFIG, "update_rate must be in (0,1]"
            )
        stable_after = _positive_integer(
            self.stable_after, "stable_after", PPB1_INVALID_CONFIG
        )
        expire_after_steps = _positive_integer(
            self.expire_after_steps,
            "expire_after_steps",
            PPB1_INVALID_CONFIG,
        )
        object.__setattr__(self, "carrier_ids", carrier_ids)
        object.__setattr__(self, "capacity", capacity)
        object.__setattr__(self, "match_threshold", threshold)
        object.__setattr__(self, "update_rate", update_rate)
        object.__setattr__(self, "stable_after", stable_after)
        object.__setattr__(self, "expire_after_steps", expire_after_steps)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "bank_id": self.bank_id,
            "modality_id": self.modality_id,
            "geometry_id": self.geometry_id,
            "carrier_ids": list(self.carrier_ids),
            "capacity": self.capacity,
            "match_threshold": self.match_threshold,
            "update_rate": self.update_rate,
            "stable_after": self.stable_after,
            "expire_after_steps": self.expire_after_steps,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class PPB1PrototypeSlot:
    slot_id: str
    occupied: bool
    prototype_values: tuple[float, ...]
    support_count: int | None
    last_selected_step: int | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "slot_id",
            _identifier(self.slot_id, "slot_id", PPB1_INVALID_SLOT),
        )
        if not isinstance(self.occupied, bool):
            raise PPB1ReferenceError(
                PPB1_INVALID_SLOT, "occupied must be boolean"
            )
        values = tuple(self.prototype_values)
        if self.occupied:
            values = _bounded_values(values, "prototype_values", PPB1_INVALID_SLOT)
            support = _positive_integer(
                self.support_count, "support_count", PPB1_INVALID_SLOT
            )
            selected = _positive_integer(
                self.last_selected_step,
                "last_selected_step",
                PPB1_INVALID_SLOT,
            )
            object.__setattr__(self, "support_count", support)
            object.__setattr__(self, "last_selected_step", selected)
        elif values or self.support_count is not None or self.last_selected_step is not None:
            raise PPB1ReferenceError(
                PPB1_INVALID_SLOT,
                "free slot must not contain prototype state",
            )
        object.__setattr__(self, "prototype_values", values)

    @classmethod
    def free(cls, slot_id: str) -> PPB1PrototypeSlot:
        return cls(slot_id, False, (), None, None)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "slot_id": self.slot_id,
            "occupied": self.occupied,
            "prototype_values": list(self.prototype_values),
            "support_count": self.support_count,
            "last_selected_step": self.last_selected_step,
        }


@dataclass(frozen=True, slots=True)
class PPB1BankState:
    bank_id: str
    config_digest: str
    accepted_step_count: int
    source_clock_id: str | None
    last_source_window_end_tick: int | None
    slots: tuple[PPB1PrototypeSlot, ...]
    schema_version: str = PPB1_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != PPB1_SCHEMA_VERSION:
            raise PPB1ReferenceError(
                PPB1_INVALID_STATE, "schema_version does not match PPB-1 v1"
            )
        object.__setattr__(
            self,
            "bank_id",
            _identifier(self.bank_id, "bank_id", PPB1_INVALID_STATE),
        )
        if (
            not isinstance(self.config_digest, str)
            or not re.fullmatch(r"[0-9a-f]{64}", self.config_digest)
        ):
            raise PPB1ReferenceError(
                PPB1_INVALID_STATE, "config_digest must be a SHA-256 hex digest"
            )
        steps = _nonnegative_integer(
            self.accepted_step_count,
            "accepted_step_count",
            PPB1_INVALID_STATE,
        )
        if self.source_clock_id is None:
            if self.last_source_window_end_tick is not None or steps != 0:
                raise PPB1ReferenceError(
                    PPB1_INVALID_STATE,
                    "empty source clock requires an empty initial state",
                )
        else:
            object.__setattr__(
                self,
                "source_clock_id",
                _identifier(
                    self.source_clock_id,
                    "source_clock_id",
                    PPB1_INVALID_STATE,
                ),
            )
            _positive_integer(
                self.last_source_window_end_tick,
                "last_source_window_end_tick",
                PPB1_INVALID_STATE,
            )
            if steps == 0:
                raise PPB1ReferenceError(
                    PPB1_INVALID_STATE,
                    "bound source clock requires an accepted step",
                )
        slots = tuple(self.slots)
        if not slots or any(not isinstance(slot, PPB1PrototypeSlot) for slot in slots):
            raise PPB1ReferenceError(
                PPB1_INVALID_STATE, "slots must contain PPB1PrototypeSlot values"
            )
        slot_ids = [slot.slot_id for slot in slots]
        if len(set(slot_ids)) != len(slot_ids):
            raise PPB1ReferenceError(
                PPB1_INVALID_STATE, "slot identifiers must be unique"
            )
        object.__setattr__(self, "accepted_step_count", steps)
        object.__setattr__(self, "slots", tuple(sorted(slots, key=lambda slot: slot.slot_id)))

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "bank_id": self.bank_id,
            "config_digest": self.config_digest,
            "accepted_step_count": self.accepted_step_count,
            "source_clock_id": self.source_clock_id,
            "last_source_window_end_tick": self.last_source_window_end_tick,
            "slots": [slot.canonical_payload() for slot in self.slots],
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class PPB1Readout:
    bank_id: str
    modality_id: str
    event: str
    slot_id: str
    match_distance: float | None
    stabilized: bool
    support_count: int
    prototype_values: tuple[float, ...]
    config_digest: str
    prestate_digest: str
    input_digest: str
    poststate_digest: str
    schema_version: str = PPB1_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != PPB1_SCHEMA_VERSION or self.event not in PPB1_EVENTS:
            raise PPB1ReferenceError(
                PPB1_ATOMIC_OUTPUT_REQUIRED, "readout schema or event is invalid"
            )
        object.__setattr__(
            self,
            "bank_id",
            _identifier(
                self.bank_id, "bank_id", PPB1_ATOMIC_OUTPUT_REQUIRED
            ),
        )
        if self.modality_id not in {"auditory", "visual"}:
            raise PPB1ReferenceError(
                PPB1_ATOMIC_OUTPUT_REQUIRED, "readout modality is invalid"
            )
        object.__setattr__(
            self,
            "slot_id",
            _identifier(
                self.slot_id, "slot_id", PPB1_ATOMIC_OUTPUT_REQUIRED
            ),
        )
        if not isinstance(self.stabilized, bool):
            raise PPB1ReferenceError(
                PPB1_ATOMIC_OUTPUT_REQUIRED, "stabilized must be boolean"
            )
        if self.event == "MATCHED":
            distance = _finite(
                self.match_distance,
                "match_distance",
                PPB1_ATOMIC_OUTPUT_REQUIRED,
            )
            if distance < 0.0 or distance > 2.0:
                raise PPB1ReferenceError(
                    PPB1_ATOMIC_OUTPUT_REQUIRED,
                    "match_distance must be in [0,2]",
                )
            object.__setattr__(self, "match_distance", distance)
        elif self.match_distance is not None:
            raise PPB1ReferenceError(
                PPB1_ATOMIC_OUTPUT_REQUIRED,
                "only MATCHED readouts may contain match_distance",
            )
        _positive_integer(
            self.support_count, "support_count", PPB1_ATOMIC_OUTPUT_REQUIRED
        )
        values = _bounded_values(
            self.prototype_values,
            "prototype_values",
            PPB1_ATOMIC_OUTPUT_REQUIRED,
        )
        object.__setattr__(self, "prototype_values", values)
        for role in (
            "config_digest",
            "prestate_digest",
            "input_digest",
            "poststate_digest",
        ):
            value = getattr(self, role)
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise PPB1ReferenceError(
                    PPB1_ATOMIC_OUTPUT_REQUIRED,
                    f"{role} must be a SHA-256 hex digest",
                )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "bank_id": self.bank_id,
            "modality_id": self.modality_id,
            "event": self.event,
            "slot_id": self.slot_id,
            "match_distance": self.match_distance,
            "stabilized": self.stabilized,
            "support_count": self.support_count,
            "prototype_values": list(self.prototype_values),
            "config_digest": self.config_digest,
            "prestate_digest": self.prestate_digest,
            "input_digest": self.input_digest,
            "poststate_digest": self.poststate_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class PPB1StepResult:
    poststate: PPB1BankState
    readout: PPB1Readout

    def __post_init__(self) -> None:
        if (
            not isinstance(self.poststate, PPB1BankState)
            or not isinstance(self.readout, PPB1Readout)
            or self.readout.poststate_digest != self.poststate.digest()
        ):
            raise PPB1ReferenceError(
                PPB1_ATOMIC_OUTPUT_REQUIRED,
                "step result requires one matching poststate and readout",
            )


def initial_ppb1_bank_state(config: PPB1BankConfig) -> PPB1BankState:
    if not isinstance(config, PPB1BankConfig):
        raise PPB1ReferenceError(PPB1_INVALID_CONFIG, "config is required")
    slots = tuple(
        PPB1PrototypeSlot.free(f"{config.bank_id}.slot.{index:03d}")
        for index in range(config.capacity)
    )
    return PPB1BankState(config.bank_id, config.digest(), 0, None, None, slots)


def normalized_mean_l1_distance(
    first: tuple[float, ...], second: tuple[float, ...]
) -> float:
    first_values = _bounded_values(first, "first", PPB1_INVALID_INPUT)
    second_values = _bounded_values(second, "second", PPB1_INVALID_INPUT)
    if len(first_values) != len(second_values):
        raise PPB1ReferenceError(
            PPB1_INVALID_INPUT, "distance inputs must have equal dimensions"
        )
    return math.fsum(
        abs(left - right) for left, right in zip(first_values, second_values, strict=True)
    ) / len(first_values)


def _input_projection(frame: ReceptorContactFrame) -> dict[str, object]:
    return {
        "modality_id": frame.modality_id,
        "geometry_id": frame.geometry_id,
        "clock_id": frame.clock_id,
        "window_start_tick": frame.window_start_tick,
        "window_end_tick": frame.window_end_tick,
        "carrier_ids": list(frame.carrier_ids),
        "values": list(frame.values),
    }


def _validate_frame(config: PPB1BankConfig, frame: object) -> ReceptorContactFrame:
    if not isinstance(frame, ReceptorContactFrame):
        raise PPB1ReferenceError(
            PPB1_INVALID_INPUT, "input must be a ReceptorContactFrame"
        )
    try:
        modality_id = frame.modality_id
        geometry_id = frame.geometry_id
        carrier_ids = tuple(frame.carrier_ids)
        values = _bounded_values(frame.values, "input values", PPB1_INVALID_INPUT)
        clock_id = _identifier(frame.clock_id, "clock_id", PPB1_INVALID_INPUT)
        start_tick = frame.window_start_tick
        end_tick = frame.window_end_tick
    except AttributeError as exc:
        raise PPB1ReferenceError(PPB1_INVALID_INPUT, "input frame is incomplete") from exc
    if modality_id != config.modality_id:
        raise PPB1ReferenceError(PPB1_INVALID_INPUT, "input modality mismatch")
    if geometry_id != config.geometry_id:
        raise PPB1ReferenceError(PPB1_INVALID_INPUT, "input geometry mismatch")
    if carrier_ids != config.carrier_ids or len(values) != len(config.carrier_ids):
        raise PPB1ReferenceError(
            PPB1_INVALID_INPUT, "input carrier inventory or order mismatch"
        )
    if (
        isinstance(start_tick, bool)
        or isinstance(end_tick, bool)
        or not isinstance(start_tick, int)
        or not isinstance(end_tick, int)
        or start_tick < 0
        or end_tick <= start_tick
    ):
        raise PPB1ReferenceError(PPB1_INVALID_INPUT, "input window is invalid")
    _identifier(modality_id, "modality_id", PPB1_INVALID_INPUT)
    _identifier(geometry_id, "geometry_id", PPB1_INVALID_INPUT)
    return frame


def _validate_state(config: PPB1BankConfig, state: object) -> PPB1BankState:
    if not isinstance(state, PPB1BankState):
        raise PPB1ReferenceError(PPB1_INVALID_STATE, "bank state is required")
    try:
        if state.schema_version != PPB1_SCHEMA_VERSION:
            raise PPB1ReferenceError(PPB1_INVALID_STATE, "state schema mismatch")
        if state.bank_id != config.bank_id or state.config_digest != config.digest():
            raise PPB1ReferenceError(PPB1_INVALID_STATE, "state config mismatch")
        if len(state.slots) != config.capacity:
            raise PPB1ReferenceError(PPB1_INVALID_STATE, "state capacity mismatch")
        expected_ids = tuple(
            f"{config.bank_id}.slot.{index:03d}" for index in range(config.capacity)
        )
        if tuple(slot.slot_id for slot in state.slots) != expected_ids:
            raise PPB1ReferenceError(PPB1_INVALID_STATE, "slot inventory mismatch")
        _nonnegative_integer(
            state.accepted_step_count, "accepted_step_count", PPB1_INVALID_STATE
        )
        for slot in state.slots:
            if not isinstance(slot, PPB1PrototypeSlot):
                raise PPB1ReferenceError(PPB1_INVALID_STATE, "invalid slot type")
            if slot.occupied:
                values = _bounded_values(
                    slot.prototype_values,
                    "prototype_values",
                    PPB1_INVALID_STATE,
                )
                if len(values) != len(config.carrier_ids):
                    raise PPB1ReferenceError(
                        PPB1_INVALID_STATE, "prototype dimension mismatch"
                    )
                support = _positive_integer(
                    slot.support_count, "support_count", PPB1_INVALID_STATE
                )
                selected = _positive_integer(
                    slot.last_selected_step,
                    "last_selected_step",
                    PPB1_INVALID_STATE,
                )
                if support > config.stable_after or selected > state.accepted_step_count:
                    raise PPB1ReferenceError(
                        PPB1_INVALID_STATE, "slot counters exceed configured state"
                    )
            elif (
                slot.prototype_values
                or slot.support_count is not None
                or slot.last_selected_step is not None
            ):
                raise PPB1ReferenceError(
                    PPB1_INVALID_STATE, "free slot contains hidden state"
                )
        if state.source_clock_id is None:
            if state.last_source_window_end_tick is not None or state.accepted_step_count:
                raise PPB1ReferenceError(PPB1_INVALID_STATE, "initial clock state mismatch")
        else:
            _identifier(
                state.source_clock_id, "source_clock_id", PPB1_INVALID_STATE
            )
            _positive_integer(
                state.last_source_window_end_tick,
                "last_source_window_end_tick",
                PPB1_INVALID_STATE,
            )
    except AttributeError as exc:
        raise PPB1ReferenceError(PPB1_INVALID_STATE, "bank state is incomplete") from exc
    return state


def advance_ppb1_bank(
    config: PPB1BankConfig,
    prestate: PPB1BankState,
    frame: ReceptorContactFrame,
) -> PPB1StepResult:
    if not isinstance(config, PPB1BankConfig):
        raise PPB1ReferenceError(PPB1_INVALID_CONFIG, "config is required")
    state = _validate_state(config, prestate)
    input_frame = _validate_frame(config, frame)
    if state.source_clock_id is not None:
        if input_frame.clock_id != state.source_clock_id:
            raise PPB1ReferenceError(PPB1_CLOCK_ORDER, "source clock changed")
        assert state.last_source_window_end_tick is not None
        if input_frame.window_end_tick <= state.last_source_window_end_tick:
            raise PPB1ReferenceError(
                PPB1_CLOCK_ORDER, "source window end did not advance"
            )

    step = state.accepted_step_count + 1
    slots = []
    for slot in state.slots:
        if (
            slot.occupied
            and slot.last_selected_step is not None
            and step - slot.last_selected_step >= config.expire_after_steps
        ):
            slots.append(PPB1PrototypeSlot.free(slot.slot_id))
        else:
            slots.append(slot)

    matches = []
    for index, slot in enumerate(slots):
        if slot.occupied:
            distance = normalized_mean_l1_distance(
                input_frame.values, slot.prototype_values
            )
            if distance <= config.match_threshold:
                matches.append((distance, slot.slot_id, index))

    match_distance: float | None = None
    if matches:
        match_distance, _, selected_index = min(matches)
        selected = slots[selected_index]
        assert selected.support_count is not None
        updated = tuple(
            (1.0 - config.update_rate) * previous + config.update_rate * current
            for previous, current in zip(
                selected.prototype_values, input_frame.values, strict=True
            )
        )
        support = min(config.stable_after, selected.support_count + 1)
        slots[selected_index] = PPB1PrototypeSlot(
            selected.slot_id, True, updated, support, step
        )
        event = "MATCHED"
    else:
        free_indices = [index for index, slot in enumerate(slots) if not slot.occupied]
        if free_indices:
            selected_index = min(free_indices, key=lambda index: slots[index].slot_id)
            event = "CREATED"
        else:
            selected_index = min(
                range(len(slots)),
                key=lambda index: (
                    slots[index].last_selected_step,
                    slots[index].slot_id,
                ),
            )
            event = "REPLACED"
        selected = slots[selected_index]
        slots[selected_index] = PPB1PrototypeSlot(
            selected.slot_id, True, tuple(input_frame.values), 1, step
        )

    poststate = PPB1BankState(
        config.bank_id,
        config.digest(),
        step,
        input_frame.clock_id,
        input_frame.window_end_tick,
        tuple(slots),
    )
    selected_post = poststate.slots[selected_index]
    assert selected_post.support_count is not None
    readout = PPB1Readout(
        config.bank_id,
        config.modality_id,
        event,
        selected_post.slot_id,
        match_distance,
        selected_post.support_count >= config.stable_after,
        selected_post.support_count,
        selected_post.prototype_values,
        config.digest(),
        state.digest(),
        _digest(_input_projection(input_frame)),
        poststate.digest(),
    )
    if readout.poststate_digest != poststate.digest():
        raise PPB1ReferenceError(
            PPB1_ATOMIC_OUTPUT_REQUIRED, "poststate and readout digest mismatch"
        )
    return PPB1StepResult(poststate, readout)
