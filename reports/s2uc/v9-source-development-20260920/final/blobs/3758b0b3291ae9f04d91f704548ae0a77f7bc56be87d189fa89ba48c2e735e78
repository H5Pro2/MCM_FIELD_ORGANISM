"""Static S2-UC three-story source binding; it never opens PCM payloads."""
from __future__ import annotations

import hashlib
import json

from tools import _s2ts_temporal_trace_run as source


VERSION = "s2uc.source-binding.v1"
SOURCE_PLAN_SHA256 = "6e64fbd5b7e86f16156b6d68bd5f7dbda3fefa8f223b2a31114bf3293eaa5f10"
SOURCE_EXECUTION_DIGEST = "1d2787da42fe01e6bb960ad545bcfbf96a3e4abd036ce91033b325c450d7f2c7"
IDS = {"a": "nu-s02-w00", "b": "nu-s02-w01", "c": "nu-s02-w02", "d": "nu-s02-w03", "e": "nu-s02-w04"}


class S2UCBindingError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def need(ok: bool, code: str) -> None:
    if not ok:
        raise S2UCBindingError(code)


def canonical(value: object) -> bytes:
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def _endpoint(row: dict[str, object], profile: str) -> dict[str, object]:
    return {
        "source_id": row["source_id"], "pcm_sha256": row["pcm_sha256"], "profile": profile,
        "nj_snapshot_index": row["nj_snapshot_index"], "window_start_sample": row["window_start_sample"],
        "window_end_sample": row["window_end_sample"], "pcm_byte_count": row["pcm_byte_count"],
    }


def _stories() -> tuple[tuple[str, tuple[tuple[str, str | None], ...]], ...]:
    return (
        ("g1", (("FORMATION", "a"), ("FORMATION", "b"), ("FORMATION", "c"), ("FORMATION", "d"), ("CLOSE", None),
                ("FORMATION", "a"), ("FORMATION", "b"), ("FORMATION", "c"), ("FORMATION", "d"), ("CLOSE", None),
                ("HINT", "b"), ("HINT", "c"), ("FORMATION", "d"), ("FORMATION", "c"), ("FORMATION", "b"), ("FORMATION", "a"), ("CLOSE", None),
                ("FORMATION", "a"), ("FORMATION", "b"), ("FORMATION", "c"), ("FORMATION", "e"), ("CLOSE", None), ("HINT", "c"), ("HINT", "d"), ("HINT", "d"), ("HINT", "c"))),
        ("g2", (("FORMATION", "a"), ("FORMATION", "b"), ("FORMATION", "c"), ("FORMATION", "d"), ("CLOSE", None),
                ("FORMATION", "d"), ("FORMATION", "c"), ("FORMATION", "b"), ("FORMATION", "a"), ("CLOSE", None),
                ("HINT", "b"), ("HINT", "c"), ("FORMATION", "a"), ("FORMATION", "b"), ("FORMATION", "c"), ("FORMATION", "d"), ("CLOSE", None))),
        ("g3", (("FORMATION", "a"), ("FORMATION", "b"), ("FORMATION", "c"), ("FORMATION", "d"), ("CLOSE", None),
                ("FORMATION", "a"), ("FORMATION", "b"), ("FORMATION", "c"), ("FORMATION", "d"), ("CLOSE", None),
                ("FORMATION", "d"), ("FORMATION", "c"), ("FORMATION", "b"), ("FORMATION", "a"), ("CLOSE", None),
                ("HINT", "c"), ("HINT", "d"), ("FORMATION", "d"), ("FORMATION", "c"), ("FORMATION", "b"), ("FORMATION", "a"), ("CLOSE", None), ("HINT", "c"), ("HINT", "d"), ("HINT", "d"), ("HINT", "c"))),
    )


def manifest() -> dict[str, object]:
    rows, plan = source.source_rows()
    need(source.SOURCE_PLAN_SHA256 == SOURCE_PLAN_SHA256 and plan["execution_digest"] == SOURCE_EXECUTION_DIGEST, "SOURCE_PLAN_INVALID")
    profile = plan["profiles"]["half_profile_digest"]
    events: list[dict[str, object]] = []
    ordinal = 0
    for story, steps in _stories():
        segment = 0
        hint_segment = 0
        hint_position = 0
        for story_ordinal, (kind, symbol) in enumerate(steps, 1):
            ordinal += 1
            if kind == "FORMATION" and (story_ordinal == 1 or steps[story_ordinal - 2][0] != "FORMATION"):
                segment += 1
            if kind == "HINT" and hint_position == 0:
                hint_segment += 1
            event_segment = f"{story}-p{segment}" if kind != "HINT" else f"{story}-h{hint_segment}"
            item = {"ordinal": ordinal, "story": story, "story_ordinal": story_ordinal, "kind": kind,
                    "segment": event_segment,
                    "runtime_time": story_ordinal - 1}
            if symbol is not None:
                item["endpoint"] = _endpoint(rows[IDS[symbol]], profile)
            events.append(item)
            if kind == "HINT":
                hint_position = (hint_position + 1) % 2
    value = {"version": VERSION, "source_plan_sha256": SOURCE_PLAN_SHA256, "source_execution_digest": SOURCE_EXECUTION_DIGEST,
             "profile": profile, "source_reused": True, "events": events,
             "limits": {"stories": 3, "events_per_story": 28, "formations_per_story": 20, "endpoints_per_story": 22,
                        "trace_frames_per_arm": 12, "hint_frames_per_arm": 2}}
    validate(value)
    return {**value, "binding_digest": digest(value), "binding_bytes": len(canonical(value))}


def validate(value: dict[str, object]) -> None:
    need(type(value) is dict and value.get("version") == VERSION and len(value.get("profile", "")) == 64, "MANIFEST_INVALID")
    events = value.get("events")
    need(type(events) is list and len(events) == 69, "EVENT_COUNT_INVALID")
    counts = {"g1": (26, 16, 6, 4, 22), "g2": (17, 12, 2, 3, 14), "g3": (26, 16, 6, 4, 22)}
    for ordinal, event in enumerate(events, 1):
        need(event.get("ordinal") == ordinal and event.get("kind") in {"FORMATION", "HINT", "CLOSE"}, "EVENT_INVALID")
    for story, expected in counts.items():
        subset = [event for event in events if event["story"] == story]
        endpoints = sum("endpoint" in event for event in subset)
        actual = (len(subset), sum(event["kind"] == "FORMATION" for event in subset), sum(event["kind"] == "HINT" for event in subset), sum(event["kind"] == "CLOSE" for event in subset), endpoints)
        need(actual == expected, "STORY_SHAPE_INVALID")
        for event in subset:
            if event["kind"] == "CLOSE":
                need("endpoint" not in event, "CLOSE_ENDPOINT_INVALID")
            else:
                endpoint = event.get("endpoint")
                need(type(endpoint) is dict and endpoint.get("profile") == value["profile"] and len(endpoint.get("pcm_sha256", "")) == 64, "ENDPOINT_INVALID")
