"""Independent, read-only S2-TS verifier. It does not invoke trace helpers."""
from __future__ import annotations

import json
import math
from typing import Any

from tools import _s2ts_temporal_trace_run as run


class S2TSVerificationError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def need(ok: bool, code: str) -> None:
    if not ok:
        raise S2TSVerificationError(code)


def _values(row: dict[str, Any]) -> tuple[float, ...]:
    values = tuple(float.fromhex(value) for value in row["half_values_hex"])
    need(len(values) == 48 and all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in values), "VALUE_DOMAIN_INVALID")
    return values


def _decision(active: tuple[tuple[float, ...], ...] | None, hint: tuple[tuple[float, ...], tuple[float, ...]]) -> dict[str, object]:
    if active is None:
        return dict(decision="ABSTAIN_NO_TRACE", generation=None, offsets=[])
    offsets = [index for index in range(3) if active[index] == hint[0] and active[index + 1] == hint[1]]
    return dict(decision="TRACE_MATCH" if len(offsets) == 1 else "ABSTAIN_AMBIGUOUS_OFFSET" if offsets else "ABSTAIN_ORDER_MISMATCH",
                generation=1, offsets=offsets)


def _canonical_offsets(value: object) -> list[int]:
    need(type(value) is list, "OFFSET_FORM_INVALID")
    offsets = list(value)
    need(all(type(item) is int and 0 <= item <= 2 for item in offsets), "OFFSET_FORM_INVALID")
    return offsets


def _canonical_decisions(value: object) -> list[dict[str, object]]:
    need(type(value) is list, "TRACE_DECISIONS_INVALID")
    output = []
    for item in value:
        need(type(item) is dict and set(item) == {"ordinal", "result"} and type(item["result"]) is dict,
             "TRACE_DECISIONS_INVALID")
        result = dict(item["result"])
        need(set(result) == {"decision", "generation", "offsets"}, "TRACE_DECISIONS_INVALID")
        result["offsets"] = _canonical_offsets(result["offsets"])
        output.append(dict(ordinal=item["ordinal"], result=result))
    return output


def _canonical_baselines(value: object) -> list[dict[str, object]]:
    need(type(value) is list, "BASELINES_INVALID")
    output = []
    for item in value:
        need(type(item) is dict and set(item) == {"ordinal", "single", "unordered", "trace_digest"}, "BASELINES_INVALID")
        result = {"ordinal": item["ordinal"], "trace_digest": item["trace_digest"]}
        for key in ("single", "unordered"):
            data = item[key]
            need(type(data) is dict and set(data) == {"present", "multiset_digest"} and type(data["present"]) is list
                 and len(data["present"]) == 2 and all(type(flag) is bool for flag in data["present"])
                 and type(data["multiset_digest"]) is str and len(data["multiset_digest"]) == 64, "BASELINES_INVALID")
            result[key] = dict(present=list(data["present"]), multiset_digest=data["multiset_digest"])
        output.append(result)
    return output


def verify(record: dict[str, Any]) -> dict[str, object]:
    need(record["status"] == "RECORDING_COMPLETE", "RECORDING_STATUS_INVALID")
    bound = json.loads(run.canonical(run.binding()))
    need(record["binding"] == bound, "BINDING_INVALID")
    events = tuple(bound["events"]); endpoints = {row["ordinal"]: row for row in record["endpoints"]}
    need(len(endpoints) == 18 and len(record["endpoints"]) == 18, "ENDPOINT_COUNT_INVALID")
    source_by_id, _ = run.source_rows()
    traces: dict[str, dict[str, Any]] = {}
    decisions: list[dict[str, object]] = []; baselines: list[dict[str, object]] = []
    for event in events:
        ordinal, session, kind = int(event["ordinal"]), str(event["session"]), str(event["kind"])
        state = traces.setdefault(session, dict(forming=[], active=None, hint=[], closed=False))
        if kind == "CLOSE":
            state.update(forming=[], active=None, hint=[], closed=True); continue
        row = endpoints.get(ordinal); need(row is not None, "ENDPOINT_MISSING")
        source = source_by_id[str(event["source_id"])]
        need(row["source_id"] == event["source_id"] and row["pcm_sha256"] == source["pcm_sha256"] and row["payload_hash_checked"] is True,
             "SOURCE_RECEIPT_INVALID")
        need(row["frame"]["runtime_time"] == event["runtime_time"] and row["frame"]["native_end"] == source["window_end_sample"], "TIME_BINDING_INVALID")
        values = _values(row)
        if kind == "FORMATION":
            need(not state["closed"] and not state["hint"], "FORMATION_STATE_INVALID")
            if state["active"] is not None:
                state.update(active=None, forming=[]); continue
            state["forming"].append(values)
            if len(state["forming"]) == 4:
                state["active"] = tuple(state["forming"]); state["forming"] = []
            continue
        need(not state["closed"], "HINT_AFTER_CLOSE")
        state["hint"].append(values)
        if len(state["hint"]) != 2:
            continue
        hint = tuple(state["hint"]); active = state["active"]
        decisions.append(dict(ordinal=ordinal, result=_decision(active, hint)))
        if active is not None:
            present = [any(item == query for item in active) for query in hint]
            # Only the active four values participate; their ordered trace digest is retained separately.
            trace_values = [endpoints[event["ordinal"]]["frame"]["value_digest"] for event in events if event["session"] == session and event["kind"] == "FORMATION"][:4]
            multiset = run.digest(sorted(trace_values))
            item = dict(ordinal=ordinal, single=dict(present=present, multiset_digest=multiset), unordered=dict(present=present, multiset_digest=multiset),
                        trace_digest=run.digest(trace_values))
            baselines.append(item)
        state["hint"] = []
    expected = record["trace"]
    need(_canonical_decisions(expected["decisions"]) == decisions, "TRACE_DECISIONS_INVALID")
    need(_canonical_baselines(expected["baselines"]) == baselines,
         "BASELINES_INVALID")
    counts = record["counts"]
    need(counts == dict(audio=18, nj=18, endpoints=18, formations=8, hints=10, closes=2), "COUNTERS_INVALID")
    return dict(status="VERIFIED", decisions=len(decisions), baseline_checks=len(baselines), read_only=True)
