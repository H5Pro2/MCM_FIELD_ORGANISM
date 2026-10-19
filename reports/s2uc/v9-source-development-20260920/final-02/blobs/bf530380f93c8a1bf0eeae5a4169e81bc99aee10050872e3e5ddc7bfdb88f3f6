"""Private bounded retention of completed exact temporal traces."""
from __future__ import annotations

from dataclasses import dataclass
import math


WIDTH, CAPACITY, RETAINED = 48, 4, 2


class S2TUError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def need(ok: bool, code: str) -> None:
    if not ok:
        raise S2TUError(code)


@dataclass(frozen=True, slots=True)
class Frame:
    values: tuple[float, ...]
    profile: str
    owner: str
    segment: str
    ordinal: int

    def __post_init__(self) -> None:
        need(len(self.values) == WIDTH and all(type(x) is float and math.isfinite(x) for x in self.values), "FRAME_VALUES_INVALID")
        need(type(self.profile) is str and len(self.profile) == 64 and type(self.owner) is str and self.owner and type(self.segment) is str and self.segment and type(self.ordinal) is int and self.ordinal >= 0, "FRAME_BINDING_INVALID")


@dataclass(frozen=True, slots=True)
class RetainedTrace:
    generation: int
    frames: tuple[Frame, ...]


class RetainedTraceStore:
    def __init__(self, profile: str, owner: str) -> None:
        self.profile, self.owner = profile, owner
        self._forming: dict[str, list[Frame]] = {}
        self._hints: dict[str, list[Frame]] = {}
        self._retained: list[RetainedTrace] = []
        self._generation = 0
        self._closed = False

    def _check(self, frame: Frame) -> None:
        need(not self._closed and frame.profile == self.profile and frame.owner == self.owner, "FRAME_SCOPE_INVALID")

    def form(self, frame: Frame) -> str:
        self._check(frame); buf = self._forming.setdefault(frame.segment, [])
        need(not self._hints.get(frame.segment), "HINT_BUFFER_PENDING")
        if buf: need(frame.ordinal > buf[-1].ordinal, "FORMATION_ORDER_INVALID")
        need(len(buf) < CAPACITY, "FORMATION_CAPACITY_INVALID")
        buf.append(frame)
        return "TRACE_COMPLETE" if len(buf) == CAPACITY else "TRACE_FORMING"

    def close_segment(self, segment: str) -> dict[str, object]:
        need(not self._closed and type(segment) is str and segment in self._forming, "SEGMENT_INVALID")
        buf = self._forming.pop(segment); self._hints.pop(segment, None)
        if len(buf) != CAPACITY:
            return {"action": "TRACE_DISCARDED_INCOMPLETE", "generation": None, "evicted": None}
        self._generation += 1
        trace = RetainedTrace(self._generation, tuple(buf))
        next_store = [*self._retained, trace]
        evicted = None if len(next_store) <= RETAINED else next_store.pop(0).generation
        self._retained = next_store
        return {"action": "TRACE_RETAINED", "generation": trace.generation, "evicted": evicted}

    def hint(self, frame: Frame) -> dict[str, object] | None:
        self._check(frame); buf = self._hints.setdefault(frame.segment, [])
        if buf: need(frame.ordinal > buf[-1].ordinal, "HINT_ORDER_INVALID")
        need(len(buf) < 2, "HINT_BUFFER_INVALID")
        buf.append(frame)
        if len(buf) == 1: return None
        hint = tuple(buf); self._hints[frame.segment] = []
        matches = [(trace.generation, offset) for trace in self._retained for offset in range(3)
                   if trace.frames[offset].values == hint[0].values and trace.frames[offset + 1].values == hint[1].values]
        if not matches: decision = "ABSTAIN_NO_RETAINED_TRACE"
        elif len(matches) == 1: decision = "TRACE_MATCH"
        else: decision = "ABSTAIN_AMBIGUOUS_RETAINED_TRACE"
        return {"decision": decision, "matches": matches}

    def close_owner(self) -> None:
        self._forming.clear(); self._hints.clear(); self._retained.clear(); self._closed = True

    @property
    def generations(self) -> tuple[int, ...]:
        return tuple(trace.generation for trace in self._retained)
