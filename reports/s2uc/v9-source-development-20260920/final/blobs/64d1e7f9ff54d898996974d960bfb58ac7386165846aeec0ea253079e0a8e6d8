"""Private exact temporal trace; separate from field and A/B memory."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math


SCHEMA = "s2ts.temporal-trace.v1"
WIDTH = 48
CAPACITY = 4


class S2TSError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _require(ok: bool, code: str) -> None:
    if not ok:
        raise S2TSError(code)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True)
class Frame:
    values: tuple[float, ...]
    profile: str
    session: str
    ordinal: int
    native_end: int
    runtime_time: int

    def __post_init__(self) -> None:
        _require(len(self.values) == WIDTH and all(type(v) is float and math.isfinite(v) for v in self.values), "FRAME_VALUES_INVALID")
        _require(all(type(v) is int and v >= 0 for v in (self.ordinal, self.native_end, self.runtime_time)), "FRAME_TIME_INVALID")
        _require(type(self.profile) is str and len(self.profile) == 64 and type(self.session) is str and self.session, "FRAME_BINDING_INVALID")

    @property
    def value_digest(self) -> str:
        return _digest([value.hex() for value in self.values])


@dataclass(frozen=True, slots=True)
class Trace:
    generation: int
    profile: str
    session: str
    frames: tuple[Frame, ...]


class TemporalTrace:
    """One bounded trace; hints use a disposable two-frame buffer."""

    def __init__(self, profile: str, session: str) -> None:
        self.profile, self.session = profile, session
        self._forming: list[Frame] = []
        self._active: Trace | None = None
        self._hint: list[Frame] = []
        self._generation = 0
        self._closed = False

    def form(self, frame: Frame) -> str:
        self._validate(frame)
        _require(not self._closed, "SESSION_CLOSED")
        _require(not self._hint, "HINT_BUFFER_PENDING")
        if self._active is not None:
            self._active = None
            self._forming.clear()
            return "TRACE_CAPACITY_EXPIRED"
        if self._forming:
            prior = self._forming[-1]
            # A source window may be deliberately reused. Event and runtime order,
            # not the source-native endpoint, define this trace's chronology.
            _require(frame.ordinal > prior.ordinal and frame.runtime_time > prior.runtime_time, "FORMATION_ORDER_INVALID")
        self._forming.append(frame)
        if len(self._forming) != CAPACITY:
            return "TRACE_FORMING"
        self._generation += 1
        self._active = Trace(self._generation, self.profile, self.session, tuple(self._forming))
        self._forming.clear()
        return "TRACE_CREATED"

    def hint(self, frame: Frame) -> dict[str, object] | None:
        self._validate(frame)
        _require(not self._closed, "SESSION_CLOSED")
        _require(len(self._hint) < 2, "HINT_BUFFER_INVALID")
        if self._hint:
            prior = self._hint[-1]
            _require(frame.ordinal > prior.ordinal and frame.runtime_time > prior.runtime_time, "HINT_ORDER_INVALID")
        self._hint.append(frame)
        if len(self._hint) == 1:
            return None
        try:
            return self._compare(tuple(self._hint))
        finally:
            self._hint.clear()

    def close(self) -> str:
        self._hint.clear(); self._forming.clear(); self._active = None; self._closed = True
        return "TRACE_SESSION_CLOSED"

    def _validate(self, frame: Frame) -> None:
        _require(type(frame) is Frame and frame.profile == self.profile and frame.session == self.session, "FRAME_SCOPE_INVALID")

    def _compare(self, hint: tuple[Frame, Frame]) -> dict[str, object]:
        if self._active is None:
            return {"decision": "ABSTAIN_NO_TRACE", "generation": None, "offsets": ()}
        offsets = tuple(index for index in range(3) if self._active.frames[index].values == hint[0].values and self._active.frames[index + 1].values == hint[1].values)
        if len(offsets) == 1:
            decision = "TRACE_MATCH"
        elif len(offsets) > 1:
            decision = "ABSTAIN_AMBIGUOUS_OFFSET"
        else:
            decision = "ABSTAIN_ORDER_MISMATCH"
        return {"decision": decision, "generation": self._active.generation, "offsets": offsets}


def unordered_membership(trace: Trace, hint: tuple[Frame, Frame]) -> dict[str, object]:
    _require(type(trace) is Trace and len(hint) == 2, "BASELINE_FORM_INVALID")
    values = tuple(frame.values for frame in trace.frames)
    return {"present": tuple(any(query.values == item for item in values) for query in hint),
            "multiset_digest": _digest(sorted(frame.value_digest for frame in trace.frames))}


def single_membership(trace: Trace, hint: tuple[Frame, Frame]) -> dict[str, object]:
    return unordered_membership(trace, hint)
