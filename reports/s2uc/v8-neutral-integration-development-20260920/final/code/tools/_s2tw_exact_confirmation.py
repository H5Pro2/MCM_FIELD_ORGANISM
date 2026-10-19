"""Private exact-repeat confirmation; S2TU remains unchanged."""
from __future__ import annotations

from tools import _s2tu_retained_trace as tu


class ExactConfirmationStore(tu.RetainedTraceStore):
    """Confirm one complete equal retained trace without renewing its FIFO age."""

    def close_segment(self, segment: str) -> dict[str, object]:
        tu.need(not self._closed and type(segment) is str and segment in self._forming, "SEGMENT_INVALID")
        forming = self._forming[segment]
        if len(forming) != tu.CAPACITY:
            return super().close_segment(segment)
        matches = [trace for trace in self._retained if tuple(frame.values for frame in trace.frames) == tuple(frame.values for frame in forming)]
        if len(matches) == 1:
            self._forming.pop(segment); self._hints.pop(segment, None)
            return {"action": "TRACE_CONFIRMED", "generation": matches[0].generation, "evicted": None}
        if len(matches) > 1:
            self._forming.pop(segment); self._hints.pop(segment, None)
            return {"action": "CONFIRMATION_AMBIGUOUS_EXISTING_TRACE", "generation": None, "evicted": None}
        return super().close_segment(segment)

    @property
    def inventory(self) -> tuple[int, ...]:
        return self.generations
