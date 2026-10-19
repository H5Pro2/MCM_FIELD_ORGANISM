"""Static S2TW source/event binding; no payload generation."""
from __future__ import annotations

from tools import _s2ts_temporal_trace_run as source


def schedule():
    ids = dict(a="nu-s02-w00", b="nu-s02-w01", c="nu-s02-w02", d="nu-s02-w03", e="nu-s02-w04")
    rows = []
    def add(segment, kind, value=None):
        rows.append(dict(ordinal=len(rows) + 1, segment=segment, kind=kind,
                         source_id=None if value is None else ids[value]))
    for segment, sequence in (("p1", "abcd"), ("p2", "abcd")):
        for value in sequence: add(segment, "FORMATION", value)
        add(segment, "SEGMENT_CLOSE")
    for value in "bc": add("h1", "HINT", value)
    for value in "dcba": add("p3", "FORMATION", value)
    add("p3", "SEGMENT_CLOSE")
    for value in "dc": add("h2", "HINT", value)
    for value in "abce": add("p4", "FORMATION", value)
    add("p4", "SEGMENT_CLOSE")
    for value in "da": add("h3", "HINT", value)
    assert len(rows) == 26 and sum(row["source_id"] is not None for row in rows) == 22
    return tuple(rows)


def binding():
    _, plan = source.source_rows()
    return dict(version="s2tw.exact-confirmation.v1", source_plan_sha256=source.SOURCE_PLAN_SHA256,
                profile=plan["profiles"]["half_profile_digest"], events=schedule(),
                resources=dict(events=26, audio_endpoints=22, formations=16, hint_frames=6,
                               decisions_per_arm=3, segment_closes_per_arm=4, owner_closes_per_arm=1,
                               field_contacts=0, scans=0, native_vector_peak_both_arms=10752,
                               state_limit=98304, metadata_limit=65536, shared_limit=262144))
