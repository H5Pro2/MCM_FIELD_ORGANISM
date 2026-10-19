"""Independent, read-only verifier for S2TU retention records."""
from __future__ import annotations

import json
import math
from typing import Any

from tools import _s2ts_temporal_trace_run as source
from tools import _s2tu_run as run
from tools import _s2tu_source_schedule as schedule


class S2TUVerificationError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def need(ok: bool, code: str) -> None:
    if not ok:
        raise S2TUVerificationError(code)


def values(row: dict[str, Any]) -> tuple[float, ...]:
    result = tuple(float.fromhex(value) for value in row["values"])
    need(len(result) == 48 and all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in result), "VALUE_DOMAIN_INVALID")
    need(run.digest(row["values"]) == row["value_digest"], "VALUE_DIGEST_INVALID")
    return result


def decision(retained: list[tuple[int, tuple[tuple[float, ...], ...]]], hint: tuple[tuple[float, ...], tuple[float, ...]]) -> dict[str, object]:
    matches = [[generation, offset] for generation, trace in retained for offset in range(3)
               if trace[offset] == hint[0] and trace[offset + 1] == hint[1]]
    return dict(decision="TRACE_MATCH" if len(matches) == 1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE" if matches else "ABSTAIN_NO_RETAINED_TRACE", matches=matches)


def verify(record: dict[str, Any]) -> dict[str, object]:
    need(record.get("status") == "RECORDING_COMPLETE", "RECORDING_STATUS_INVALID")
    bound = json.loads(run.canonical(schedule.binding()))
    need(record.get("binding") == bound and record.get("binding_digest") == run.digest(bound), "BINDING_INVALID")
    need(record.get("counts") == dict(audio=20, nj=20, endpoints=20, formations=12, hints=8, segment_closes=3, owner_closes=1), "COUNTERS_INVALID")
    rows = record.get("endpoints")
    need(type(rows) is list and len(rows) == 20, "ENDPOINT_COUNT_INVALID")
    by_ordinal = {row.get("ordinal"): row for row in rows}
    need(len(by_ordinal) == 20, "ENDPOINT_ORDINAL_INVALID")
    sources, _ = source.source_rows()
    retained: list[tuple[int, tuple[tuple[float, ...], ...]]] = []
    forming: dict[str, list[tuple[float, ...]]] = {}
    hints: dict[str, list[tuple[float, ...]]] = {}
    transitions: list[dict[str, object]] = []
    decisions: list[dict[str, object]] = []
    generation = 0
    for event in bound["events"]:
        if event["kind"] == "SEGMENT_CLOSE":
            current = forming.pop(event["segment"], None)
            need(current is not None and len(current) == 4, "FORMATION_CHAIN_INVALID")
            generation += 1
            evicted = retained[0][0] if len(retained) == 2 else None
            if evicted is not None:
                retained.pop(0)
            retained.append((generation, tuple(current)))
            transitions.append(dict(action="TRACE_RETAINED", generation=generation, evicted=evicted))
            continue
        row = by_ordinal.get(event["ordinal"])
        need(type(row) is dict, "ENDPOINT_MISSING")
        src = sources.get(event["source_id"])
        need(src is not None and row.get("source_id") == event["source_id"] and row.get("pcm_sha256") == src["pcm_sha256"] and row.get("payload_hash_checked") is True, "SOURCE_BINDING_INVALID")
        frame = row.get("frame")
        need(frame == dict(owner=event["owner"], segment=event["segment"], ordinal=event["ordinal"], native_end=src["window_end_sample"], runtime_time=event["ordinal"]), "FRAME_BINDING_INVALID")
        vector = values(row)
        if event["kind"] == "FORMATION":
            forming.setdefault(event["segment"], []).append(vector)
        else:
            buffer = hints.setdefault(event["segment"], [])
            buffer.append(vector)
            if len(buffer) == 2:
                decisions.append(dict(ordinal=event["ordinal"], result=decision(retained, (buffer[0], buffer[1]))))
                hints[event["segment"]] = []
    need(record.get("transitions") == transitions, "TRANSITIONS_INVALID")
    need(record.get("decisions") == decisions, "DECISIONS_INVALID")
    need(record.get("retained_generations_before_owner_close") == [2, 3] and record.get("owner_closed") is True, "OWNER_CLOSE_INVALID")
    return dict(status="VERIFIED", read_only=True, decisions=len(decisions), transitions=len(transitions), retained_generations=[2, 3])
