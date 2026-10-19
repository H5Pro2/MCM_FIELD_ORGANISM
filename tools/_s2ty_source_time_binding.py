"""Static S2-TY source binding; it never reads or analyzes PCM payloads."""
from __future__ import annotations

import hashlib
import json
import math

from tools import _s2ts_temporal_trace_run as source
from tools import _s2tw_source_schedule as schedule


class S2TYBindingError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def need(ok, code):
    if not ok:
        raise S2TYBindingError(code)


def canonical(value):
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_manifest():
    sources, plan = source.source_rows()
    events = []
    for item in schedule.schedule():
        row = {
            "ordinal": item["ordinal"],
            "segment": item["segment"],
            "kind": "CLOSE" if item["kind"] == "SEGMENT_CLOSE" else item["kind"],
            "runtime_time": item["ordinal"] - 1,
        }
        if item["source_id"] is not None:
            source_row = sources[item["source_id"]]
            row["endpoint"] = {
                "source_id": source_row["source_id"],
                "pcm_sha256": source_row["pcm_sha256"],
                "profile": plan["profiles"]["half_profile_digest"],
                "nj_snapshot_index": source_row["nj_snapshot_index"],
                "window_start_sample": source_row["window_start_sample"],
                "window_end_sample": source_row["window_end_sample"],
            }
        events.append(row)
    manifest = {
        "version": "s2ty.source-time-binding.v2",
        "source_plan_sha256": source.SOURCE_PLAN_SHA256,
        "profile": plan["profiles"]["half_profile_digest"],
        "source_reused": True,
        "logical_clock": {"kind": "S2TY_LOGICAL_EVENT_CLOCK_V1", "start": 0, "tick": 1},
        "events": events,
        "owner_closes": [{"arm": "adapter", "runtime_time": 26}, {"arm": "direct", "runtime_time": 27}],
    }
    validate_static(manifest)
    return {**manifest, "binding_digest": digest(manifest), "binding_bytes": len(canonical(manifest))}


def reseal_manifest(manifest):
    """Refresh a manifest digest for a separate neutral fixture source only."""
    payload = {key: value for key, value in manifest.items() if key not in {"binding_digest", "binding_bytes"}}
    validate_static(payload)
    return {**payload, "binding_digest": digest(payload), "binding_bytes": len(canonical(payload))}


def validate_static(manifest):
    need(type(manifest) is dict and manifest.get("version") == "s2ty.source-time-binding.v2", "MANIFEST_INVALID")
    clock = manifest.get("logical_clock")
    need(clock == {"kind": "S2TY_LOGICAL_EVENT_CLOCK_V1", "start": 0, "tick": 1}, "LOGICAL_CLOCK_INVALID")
    events = manifest.get("events")
    need(type(events) is list and len(events) == 26, "EVENT_COUNT_INVALID")
    endpoints = [item for item in events if "endpoint" in item]
    need(len(endpoints) == 22 and sum(item["kind"] == "FORMATION" for item in events) == 16 and sum(item["kind"] == "HINT" for item in events) == 6 and sum(item["kind"] == "CLOSE" for item in events) == 4, "EVENT_SHAPE_INVALID")
    owner_closes = manifest.get("owner_closes")
    need(type(owner_closes) is list and len(owner_closes) == 2 and all(type(item) is dict for item in owner_closes) and [item.get("arm") for item in owner_closes] == ["adapter", "direct"], "OWNER_CLOSE_INVALID")
    last_runtime = -1
    for ordinal, item in enumerate(events, 1):
        need(item.get("ordinal") == ordinal and type(item.get("segment")) is str and item.get("kind") in {"FORMATION", "HINT", "CLOSE"}, "EVENT_INVALID")
        runtime = item.get("runtime_time")
        need(type(runtime) is int and runtime == clock["start"] + (ordinal - 1) * clock["tick"] and runtime > last_runtime, "RUNTIME_TIME_INVALID")
        last_runtime = runtime
        if item["kind"] == "CLOSE":
            need("endpoint" not in item, "CLOSE_ENDPOINT_INVALID")
            continue
        endpoint = item.get("endpoint")
        need(type(endpoint) is dict and endpoint.get("profile") == manifest["profile"], "ENDPOINT_MISSING")
        need(type(endpoint.get("source_id")) is str and len(endpoint.get("pcm_sha256", "")) == 64, "ENDPOINT_INVALID")
        snapshot, start, end = endpoint.get("nj_snapshot_index"), endpoint.get("window_start_sample"), endpoint.get("window_end_sample")
        need(all(type(value) is int for value in (snapshot, start, end)) and snapshot >= 0 and start == snapshot * 480 and end == start + 4800, "NATIVE_TIME_INVALID")
    for close_ordinal, item in enumerate(owner_closes, 26):
        need(type(item) is dict and type(item.get("runtime_time")) is int and item["runtime_time"] == clock["start"] + close_ordinal * clock["tick"] and item["runtime_time"] > last_runtime, "OWNER_CLOSE_TIME_INVALID")
        last_runtime = item["runtime_time"]
    return manifest


def endpoint_at(manifest, ordinal):
    validate_static(manifest)
    need(type(ordinal) is int and 1 <= ordinal <= len(manifest["events"]), "ENDPOINT_MISSING")
    endpoint = manifest["events"][ordinal - 1].get("endpoint")
    need(endpoint is not None, "ENDPOINT_MISSING")
    return endpoint


def handoff(manifest, ordinal, *, payload_sha256, profile, snapshot_index, window_start_sample, window_end_sample, values):
    endpoint = endpoint_at(manifest, ordinal)
    need(payload_sha256 == endpoint["pcm_sha256"], "PAYLOAD_HASH_INVALID")
    need(profile == endpoint["profile"], "PROFILE_INVALID")
    need((snapshot_index, window_start_sample, window_end_sample) == (endpoint["nj_snapshot_index"], endpoint["window_start_sample"], endpoint["window_end_sample"]), "NATIVE_TIME_INVALID")
    need(type(values) is tuple and len(values) == 48 and all(type(value) is float and math.isfinite(value) and 0.0 <= value <= 1.0 for value in values), "HALF_VALUES_INVALID")
    receipt = {"ordinal": ordinal, "half_values_digest": digest([value.hex() for value in values]), "same_instance": True}
    return values, values, receipt
