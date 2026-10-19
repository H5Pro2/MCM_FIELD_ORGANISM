"""Independent read-only verifier for the S2TW two-arm record."""
from __future__ import annotations

import json
import math
from typing import Any

from tools import _s2ts_temporal_trace_run as source
from tools import _s2tw_run as run
from tools import _s2tw_source_schedule as schedule


class S2TWVerificationError(ValueError):
    pass


def need(ok: bool, code: str) -> None:
    if not ok: raise S2TWVerificationError(code)


def vector(row: dict[str, Any]) -> tuple[float, ...]:
    result = tuple(float.fromhex(value) for value in row["values"])
    need(len(result) == 48 and all(math.isfinite(value) and 0 <= value <= 1 for value in result), "VALUE_DOMAIN_INVALID")
    need(run.digest(row["values"]) == row["value_digest"], "VALUE_DIGEST_INVALID")
    return result


def read(retained, hint):
    matches = [[generation, offset] for generation, trace in retained for offset in range(3) if trace[offset] == hint[0] and trace[offset + 1] == hint[1]]
    return dict(decision="TRACE_MATCH" if len(matches) == 1 else "ABSTAIN_AMBIGUOUS_RETAINED_TRACE" if matches else "ABSTAIN_NO_RETAINED_TRACE", matches=matches)


def close(retained, generation, frames, confirm):
    matches = [trace for _, trace in retained if trace == tuple(frames)]
    if confirm and len(matches) == 1: return retained, generation, dict(action="TRACE_CONFIRMED", generation=next(g for g, t in retained if t == tuple(frames)), evicted=None)
    if confirm and len(matches) > 1: return retained, generation, dict(action="CONFIRMATION_AMBIGUOUS_EXISTING_TRACE", generation=None, evicted=None)
    generation += 1; evicted = retained[0][0] if len(retained) == 2 else None
    retained = (retained + [(generation, tuple(frames))])[-2:]
    return retained, generation, dict(action="TRACE_RETAINED", generation=generation, evicted=evicted)


def verify(record: dict[str, Any]) -> dict[str, object]:
    need(record.get("status") == "RECORDING_COMPLETE", "RECORDING_STATUS_INVALID")
    bound = json.loads(run.canonical(schedule.binding()))
    need(record.get("binding") == bound and record.get("binding_digest") == run.digest(bound), "BINDING_INVALID")
    need(record.get("counts") == dict(audio=22, nj=22, endpoints=22, formations=16, hints=6, segment_closes=4, owner_closes=2), "COUNTERS_INVALID")
    rows = record.get("endpoints"); need(type(rows) is list and len(rows) == 22, "ENDPOINT_COUNT_INVALID")
    indexed = {row.get("ordinal"): row for row in rows}; need(len(indexed) == 22, "ENDPOINT_ORDINAL_INVALID")
    sources, _ = source.source_rows(); retained = [[], []]; generation = [0, 0]; forming = [dict(), dict()]; hints = [dict(), dict()]
    transitions = []; decisions = []
    for event in bound["events"]:
        if event["kind"] == "SEGMENT_CLOSE":
            outputs = []
            for arm in range(2):
                frames = forming[arm].pop(event["segment"], None); need(frames is not None and len(frames) == 4, "FORMATION_CHAIN_INVALID")
                retained[arm], generation[arm], receipt = close(retained[arm], generation[arm], frames, arm == 1); outputs.append(receipt)
            transitions.append(dict(ordinal=event["ordinal"], baseline=outputs[0], confirmation=outputs[1], baseline_inventory=[g for g, _ in retained[0]], confirmation_inventory=[g for g, _ in retained[1]])); continue
        row = indexed.get(event["ordinal"]); src = sources.get(event["source_id"])
        need(type(row) is dict and src is not None and row.get("source_id") == event["source_id"] and row.get("pcm_sha256") == src["pcm_sha256"] and row.get("payload_hash_checked") is True, "SOURCE_BINDING_INVALID")
        values = vector(row)
        if event["kind"] == "FORMATION":
            for arm in range(2): forming[arm].setdefault(event["segment"], []).append(values)
        else:
            outputs=[]
            for arm in range(2):
                buf=hints[arm].setdefault(event["segment"], []); buf.append(values)
                if len(buf)==2: outputs.append(read(retained[arm], tuple(buf))); hints[arm][event["segment"]]=[]
            if outputs: need(len(outputs)==2, "HINT_CHAIN_INVALID"); decisions.append(dict(ordinal=event["ordinal"], baseline=outputs[0], confirmation=outputs[1]))
    need(record.get("transitions") == transitions, "TRANSITIONS_INVALID")
    need(record.get("decisions") == decisions, "DECISIONS_INVALID")
    need(record.get("inventories_before_owner_close") == dict(baseline=[3, 4], confirmation=[2, 3]) and record.get("owner_closed") is True, "OWNER_CLOSE_INVALID")
    return dict(status="VERIFIED", read_only=True, transitions=4, decisions=3, baseline_inventory=[3, 4], confirmation_inventory=[2, 3])
