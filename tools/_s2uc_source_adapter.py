"""Demand-driven S2-UC source adapter; supplier injection keeps neutral tests source-free."""
from __future__ import annotations

from tools import _s2ty_audio_materialization as ty

class S2UCSourceAdapterError(ValueError):
    def __init__(self, code): self.code=code; super().__init__(code)

class SourceAdapter:
    def __init__(self, bound, supplier):
        self._uses = list(bound["endpoint_uses"])
        self._sources = bound["sources"]
        self._supplier = supplier
        self._index = 0
        self._successes = 0
        self.counters = ty.MaterializationCounters()

    def __call__(self, endpoint):
        if self._index >= len(self._uses) or endpoint != self._uses[self._index]:
            raise S2UCSourceAdapterError("ENDPOINT_ORDER_INVALID")
        source = self._sources.get(endpoint["source_id"])
        if source is None or any(endpoint[key] != source[key] for key in source):
            raise S2UCSourceAdapterError("SOURCE_BINDING_INVALID")
        self._index += 1
        payload = self._supplier(endpoint)
        result = ty.materialize(endpoint, payload, counters=self.counters)
        self._successes += 1
        return result

    def complete(self):
        if self._index != len(self._uses) or self._successes != len(self._uses): raise S2UCSourceAdapterError("ENDPOINT_COUNT_INVALID")
        return {"attempts": self._index, "successes": self._successes, "counters": self.counters.snapshot()}
