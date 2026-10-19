"""Static S2TU source/event binding; no payload generation."""
from __future__ import annotations
from tools import _s2ts_temporal_trace_run as ts


def schedule():
    ids = dict(a="nu-s02-w00", b="nu-s02-w01", c="nu-s02-w02", d="nu-s02-w03")
    rows = []
    def add(segment, kind, label=None):
        rows.append(dict(ordinal=len(rows)+1, owner="s2tu-owner-01", segment=segment, kind=kind,
                         label=label, source_id=None if label is None else ids[label]))
    for segment, values in (("t1", "abcd"), ("t2", "cbda")):
        for value in values: add(segment, "FORMATION", value)
        add(segment, "SEGMENT_CLOSE")
    for values in ("bc", "cb"):
        for value in values: add("h1", "HINT", value)
    for value in "acbd": add("t3", "FORMATION", value)
    add("t3", "SEGMENT_CLOSE")
    for values in ("bc", "cb"):
        for value in values: add("h2", "HINT", value)
    assert len(rows) == 23 and sum(x["source_id"] is not None for x in rows) == 20
    return tuple(rows)


def binding():
    sources, plan = ts.source_rows(); events = schedule()
    return dict(version="s2tu.source-schedule.v1", source_plan_sha256=ts.SOURCE_PLAN_SHA256,
                profile=plan["profiles"]["half_profile_digest"], events=events,
                lifecycle_calls=dict(segment_closes=3, owner_close=1),
                resources=dict(events=23, audio_endpoints=20, formations=12, hint_frames=8,
                               decisions=4, field_contacts=0, scans=0, active_peak_bytes=5376,
                               state_limit=98304, metadata_limit=65536, shared_limit=262144))
