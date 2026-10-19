"""Private exact-repeat FIFO recency update; no value or generation change."""
from tools import _s2tu_retained_trace as tu
from tools import _s2tw_exact_confirmation as tw


class RecencyConfirmationStore(tw.ExactConfirmationStore):
    def close_segment(self, segment):
        tu.need(not self._closed and type(segment) is str and segment in self._forming, "SEGMENT_INVALID")
        forming = self._forming[segment]
        if len(forming) == tu.CAPACITY:
            matches = [trace for trace in self._retained if tuple(f.values for f in trace.frames) == tuple(f.values for f in forming)]
            if len(matches) == 1:
                trace = matches[0]; self._forming.pop(segment); self._hints.pop(segment, None)
                self._retained = [item for item in self._retained if item.generation != trace.generation] + [trace]
                return {"action": "TRACE_CONFIRMED_RECENT", "generation": trace.generation, "evicted": None}
        return super().close_segment(segment)
