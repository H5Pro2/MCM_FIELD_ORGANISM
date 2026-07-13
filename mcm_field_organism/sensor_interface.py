"""Immutable, passive boundary for sensor-specific MCM field states.

This module validates and compares technical state only. It contains no MCM
dynamics, multimodal coupling, learning, semantic classification, or action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
import re
from typing import Callable, Iterable, Mapping


class InterfaceValidationError(ValueError):
    """Raised when a state violates the preregistered interface contract."""


class Presence(str, Enum):
    MISSING = "missing"
    UNAVAILABLE = "unavailable"
    NO_CONTACT = "no_contact"
    ACTIVE_ZERO = "active_zero"
    ACTIVE_FIELD = "active_field"


class Validity(str, Enum):
    ABSENT = "absent"
    UNAVAILABLE = "unavailable"
    VALID = "valid"


_STATE_FIELDS = frozenset(
    {
        "modality_id",
        "channel_id",
        "snapshot_id",
        "timestamp",
        "geometry_id",
        "carrier_ids",
        "activation",
        "afterimage",
        "local_resources",
        "presence",
        "validity",
    }
)
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_.-]*$")


def _identifier(value: object, role: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise InterfaceValidationError(f"{role} must be a lowercase technical identifier")
    return value


def _float_tuple(values: Iterable[float], role: str) -> tuple[float, ...]:
    try:
        result = tuple(float(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise InterfaceValidationError(f"{role} must contain numeric values") from exc
    if any(not math.isfinite(value) for value in result):
        raise InterfaceValidationError(f"{role} must contain only finite values")
    return result


def _enum_value(enum_type: type[Enum], value: object, role: str) -> Enum:
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        raise InterfaceValidationError(f"unknown {role}: {value!r}") from exc


@dataclass(frozen=True, slots=True)
class SensorFieldState:
    """One completed sensor-specific MCM boundary state."""

    modality_id: str
    channel_id: str
    snapshot_id: str
    timestamp: int
    geometry_id: str | None
    carrier_ids: tuple[str, ...]
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    local_resources: tuple[float, ...]
    presence: Presence
    validity: Validity

    def __post_init__(self) -> None:
        object.__setattr__(self, "modality_id", _identifier(self.modality_id, "modality_id"))
        object.__setattr__(self, "channel_id", _identifier(self.channel_id, "channel_id"))
        object.__setattr__(self, "snapshot_id", _identifier(self.snapshot_id, "snapshot_id"))
        object.__setattr__(self, "geometry_id", _identifier(self.geometry_id, "geometry_id", optional=True))

        if isinstance(self.timestamp, bool) or not isinstance(self.timestamp, int) or self.timestamp < 0:
            raise InterfaceValidationError("timestamp must be a non-negative integer")

        carriers = tuple(self.carrier_ids)
        for carrier_id in carriers:
            _identifier(carrier_id, "carrier_id")
        if len(set(carriers)) != len(carriers):
            raise InterfaceValidationError("carrier_ids must be unique within a state")
        object.__setattr__(self, "carrier_ids", carriers)

        activation = _float_tuple(self.activation, "activation")
        afterimage = _float_tuple(self.afterimage, "afterimage")
        resources = _float_tuple(self.local_resources, "local_resources")
        object.__setattr__(self, "activation", activation)
        object.__setattr__(self, "afterimage", afterimage)
        object.__setattr__(self, "local_resources", resources)

        presence = _enum_value(Presence, self.presence, "presence")
        validity = _enum_value(Validity, self.validity, "validity")
        object.__setattr__(self, "presence", presence)
        object.__setattr__(self, "validity", validity)

        if presence is Presence.MISSING:
            self._validate_absent(Validity.ABSENT)
            return
        if presence is Presence.UNAVAILABLE:
            self._validate_absent(Validity.UNAVAILABLE)
            return

        if validity is not Validity.VALID:
            raise InterfaceValidationError("available presence states require validity=valid")
        if self.geometry_id is None or not carriers:
            raise InterfaceValidationError("available states require geometry and carriers")
        if len(activation) != len(carriers) or len(afterimage) != len(carriers):
            raise InterfaceValidationError("activation and afterimage must match carrier geometry")
        if resources and len(resources) != len(carriers):
            raise InterfaceValidationError("local_resources must be empty or match carrier geometry")
        if any(value < 0.0 for value in resources):
            raise InterfaceValidationError("local_resources cannot be negative")

        has_activation = any(value != 0.0 for value in activation)
        if presence in {Presence.NO_CONTACT, Presence.ACTIVE_ZERO} and has_activation:
            raise InterfaceValidationError(f"{presence.value} requires zero current activation")
        if presence is Presence.ACTIVE_FIELD and not has_activation:
            raise InterfaceValidationError("active_field requires non-zero current activation")

    def _validate_absent(self, required_validity: Validity) -> None:
        if self.validity is not required_validity:
            raise InterfaceValidationError(
                f"{self.presence.value} requires validity={required_validity.value}"
            )
        if self.geometry_id is not None:
            raise InterfaceValidationError(f"{self.presence.value} cannot carry geometry")
        if self.carrier_ids or self.activation or self.afterimage or self.local_resources:
            raise InterfaceValidationError(f"{self.presence.value} cannot carry field vectors")

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "SensorFieldState":
        keys = frozenset(payload)
        missing = sorted(_STATE_FIELDS - keys)
        unknown = sorted(keys - _STATE_FIELDS)
        if missing or unknown:
            raise InterfaceValidationError(
                f"state roles mismatch; missing={missing}, unknown={unknown}"
            )
        return cls(**{name: payload[name] for name in _STATE_FIELDS})

    def canonical_payload(self) -> dict[str, object]:
        return {
            "modality_id": self.modality_id,
            "channel_id": self.channel_id,
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "geometry_id": self.geometry_id,
            "carrier_ids": list(self.carrier_ids),
            "activation": list(self.activation),
            "afterimage": list(self.afterimage),
            "local_resources": list(self.local_resources),
            "presence": self.presence.value,
            "validity": self.validity.value,
        }


@dataclass(frozen=True, slots=True)
class CanonicalFrameSet:
    """B1 baseline: ordered transport without fusion or field interaction."""

    states: tuple[SensorFieldState, ...]

    def __post_init__(self) -> None:
        states = tuple(self.states)
        if not states:
            raise InterfaceValidationError("a frame set requires at least one explicit channel state")

        channel_keys = [(state.modality_id, state.channel_id) for state in states]
        if len(set(channel_keys)) != len(channel_keys):
            raise InterfaceValidationError("modality/channel pairs must be unique in a frame set")

        snapshot_ids = [state.snapshot_id for state in states]
        if len(set(snapshot_ids)) != len(snapshot_ids):
            raise InterfaceValidationError("snapshot_id values must be unique in a frame set")

        timestamps = {state.timestamp for state in states}
        if len(timestamps) != 1:
            raise InterfaceValidationError("a synchronous frame set cannot mix timestamps")

        object.__setattr__(self, "states", tuple(sorted(states, key=lambda item: channel_keys_for(item))))

    @property
    def timestamp(self) -> int:
        return self.states[0].timestamp

    @property
    def snapshot_ids(self) -> frozenset[str]:
        return frozenset(state.snapshot_id for state in self.states)

    def canonical_payload(self) -> list[dict[str, object]]:
        return [state.canonical_payload() for state in self.states]

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def channel_keys_for(state: SensorFieldState) -> tuple[str, str]:
    return state.modality_id, state.channel_id


Observer = Callable[[CanonicalFrameSet], object]


@dataclass(slots=True)
class PassiveSnapshotGate:
    """Technical chronology check with no field state or dynamics."""

    _last_timestamp: int | None = field(default=None, init=False, repr=False)
    _seen_snapshot_ids: set[str] = field(default_factory=set, init=False, repr=False)

    @property
    def last_timestamp(self) -> int | None:
        return self._last_timestamp

    @property
    def seen_snapshot_ids(self) -> frozenset[str]:
        return frozenset(self._seen_snapshot_ids)

    def accept(
        self,
        states: Iterable[SensorFieldState],
        *,
        observer: Observer | None = None,
    ) -> CanonicalFrameSet:
        frame_set = CanonicalFrameSet(tuple(states))
        if self._last_timestamp is not None and frame_set.timestamp <= self._last_timestamp:
            raise InterfaceValidationError("timestamps must advance monotonically between frame sets")
        duplicate_ids = frame_set.snapshot_ids & self._seen_snapshot_ids
        if duplicate_ids:
            raise InterfaceValidationError(f"snapshot_id already seen: {sorted(duplicate_ids)}")

        digest_before_observer = frame_set.digest()
        if observer is not None:
            observer(frame_set)
        if frame_set.digest() != digest_before_observer:
            raise InterfaceValidationError("observer changed the immutable frame set")

        self._last_timestamp = frame_set.timestamp
        self._seen_snapshot_ids.update(frame_set.snapshot_ids)
        return frame_set

    def reset(self) -> None:
        self._last_timestamp = None
        self._seen_snapshot_ids.clear()


def numeric_sum_baseline(states: Iterable[SensorFieldState]) -> tuple[float, ...]:
    """B2 baseline that intentionally discards modality and presence."""

    active_vectors = [state.activation for state in states if state.activation]
    if not active_vectors:
        return ()
    width = len(active_vectors[0])
    if any(len(vector) != width for vector in active_vectors):
        raise InterfaceValidationError("B2 requires geometrically compatible activation vectors")
    return tuple(sum(vector[index] for vector in active_vectors) for index in range(width))
