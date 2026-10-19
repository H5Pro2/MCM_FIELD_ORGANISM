"""Static S2TX source binding; no payload generation."""
from tools import _s2ts_temporal_trace_run as source


def schedule():
    ids={c:f"nu-s0{2+i//4}-w0{i%4}" for i,c in enumerate("abcdefghijkl")}; rows=[]
    def add(seg, kind, value=None): rows.append(dict(ordinal=len(rows)+1,segment=seg,kind=kind,source_id=ids.get(value)))
    for seg, seq in (("p1","abcd"),("p2","efgh"),("p3","abcd"),("p4","ijkl"),("p5","efgh")):
        for value in seq: add(seg,"FORMATION",value)
        add(seg,"SEGMENT_CLOSE")
        if seg=="p4":
            for value in "cd": add("h1","HINT",value)
    assert len(rows)==27 and sum(row["source_id"] is not None for row in rows)==22
    return tuple(rows)


def binding():
    _, plan=source.source_rows()
    return dict(version="s2tx.recency-confirmation.v1",source_plan_sha256=source.SOURCE_PLAN_SHA256,profile=plan["profiles"]["half_profile_digest"],events=schedule(),resources=dict(events=27,audio_endpoints=22,formations=20,hint_frames=2,segment_closes=5,owner_closes=2,field_contacts=0,scans=0,active_peak_bytes=10752,state_limit=98304,metadata_limit=65536,shared_limit=262144))
