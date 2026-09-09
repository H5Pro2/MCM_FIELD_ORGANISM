"""Independent source evidence inspection, never payload regeneration."""
import hashlib
import json
from pathlib import Path
from tools import _s2oa_private_source_binding as b


def root(value,key):
    data = json.dumps({k:v for k,v in value.items() if k != key},allow_nan=False,
                      ensure_ascii=True,sort_keys=True,separators=(",",":")).encode("ascii")
    b.require(value.get(key) == hashlib.sha256(data).hexdigest(),"ROOT_DIGEST_INVALID")


def check_events(rows):
    b.require(len(rows) == 28,"EVENT_COUNT_INVALID")
    audio_cues, visual_cues = (3,8),(1,4,18,23,25,28)
    for n,e in enumerate(rows,1):
        g = n-1
        kind = b.A if n in audio_cues else b.V if n in visual_cues else b.AV
        b.require((e["ordinal"],e["event_id"],e["event_type"]) == (n,f"e{n:02d}",kind),"EVENT_ORDER_INVALID")
        b.require(e["field_clock_id"] == "s2oa-continuous-field-clock" and e["field_window"] ==
            [0 if n == 1 else 200000000*g-100000000,200000000*g+100000000],"FIELD_TIME_INVALID")
        a,v = e["auditory"],e["visual"]
        b.require((a is None) == (kind == b.V) and (v is None) == (kind == b.A),"MODALITY_INVALID")
        if a is not None:
            b.require(type(a["nj_snapshot_index"]) is int and (a["clock_id"],a["start_tick"],a["end_tick"],a["nj_snapshot_index"])
                == ("audio.sample",g*9600,g*9600+4800,g*20),"AUDIO_TIME_INVALID")
            b.require(a["common_window"] == [g*200000000,g*200000000+100000000],"AUDIO_WINDOW_INVALID")
        if v is not None:
            b.require((v["clock_id"],v["start_tick"],v["end_tick"]) == ("video.frame",6*g+2,6*g+3)
                and v["common_window"] == [(6*g+2)*1000000000//30,g*200000000+100000000],"VISUAL_TIME_INVALID")
        if a is not None and v is not None:
            b.require(max(a["common_window"][0],v["common_window"][0]) < min(a["common_window"][1],v["common_window"][1]),"WINDOW_OVERLAP_INVALID")


def check_plans(ex,ev):
    root(ex,"execution_digest"); root(ev,"evaluation_digest")
    check_events(ex["events"])
    b.require(ev["execution_digest"] == ex["execution_digest"],"EVALUATION_LINK_INVALID")
    b.require(ex == b.execution_plan(ex["sources"],ex["environment"],ex["source_hashes"],ex["generators"]),"EXECUTION_BINDING_INVALID")
    b.require(ev == b.evaluation_plan(ex),"EVALUATION_BINDING_INVALID")
    for s in ex["sources"]:
        root(s,"source_digest")
    b.require(len(set(s["source_id"] for s in ex["sources"])) == 48,"SOURCE_IDENTITY_INVALID")
    b.require(not any(f'"{key}"' in json.dumps(ex) for key in ("prediction","target_visual_ordinal","state_predictions","cue_id")),"EVALUATION_LEAK")
    b.require(len(b.canonical(ex)) <= b.MAX_METADATA_BYTES and len(b.canonical(ev)) <= b.MAX_METADATA_BYTES,"METADATA_SIZE_EXCEEDED")


def verify_once(directory):
    out = Path(directory)
    with (out/"verification.claim").open("xb") as handle:
        handle.write(b.canonical(dict(verification_calls=1)))
    names = ("execution-plan.json","evaluation-plan.json","seal.json","preregistration.json")
    before = {n:b.filehash(out/n) for n in names}
    ex,ev,z,pr = [json.loads((out/n).read_bytes()) for n in names]
    check_plans(ex,ev); root(z,"seal_digest")
    b.require(z["status"] == "S2OA_SOURCES_PRESEALED" and z["run_id"] == pr["run_id"] == out.name,"RUN_BINDING_INVALID")
    b.require((z["execution_digest"],z["evaluation_digest"],z["execution_file_sha256"],z["evaluation_file_sha256"])
        == (ex["execution_digest"],ev["evaluation_digest"],before[names[0]],before[names[1]]),"SEAL_LINK_INVALID")
    b.require(z["hashes_before"] == z["hashes_after"] == ex["source_hashes"] == pr["hashes"] == b.watched(),"CODE_BINDING_INVALID")
    b.require(ex["environment"] == pr["environment"] == b.environment(),"ENVIRONMENT_INVALID")
    _,_,gen = b.generators()  # Compile definitions only. Neither function is called.
    b.require(gen == ex["generators"] == pr["generators"],"GENERATOR_BINDING_INVALID")
    b.require(pr["specs"] == b.specs() and pr["events"] == ex["events"] and pr["profiles"] == ex["profiles"]
        and pr["budgets"] == z["budgets"] == b.budgets() and pr["retry"] is False
        and pr["qualification_sha256"] == b.filehash(b.QUAL_DIR/"result.json"),"PREREGISTRATION_INVALID")
    b.require(type(z["attempted_sources"]) is int and type(z["completed_sources"]) is int
        and z["attempted_sources"] == z["completed_sources"] == 48,"COUNTER_INVALID")
    for k in ("raw_payloads_persisted","receptor_calls","nj_calls","distance_calls","memory_calls","field_calls","runtime_calls"):
        b.require(type(z[k]) is int and z[k] == 0,"FORBIDDEN_EXECUTION")
    groups = {}
    for s in ex["sources"]:
        groups.setdefault((s["kind"],s["payload_sha256"]),[]).append(s["source_id"])
    expected = [dict(kind=k,payload_sha256=h,source_ids=ids) for (k,h),ids in sorted(groups.items()) if len(ids)>1]
    b.require(z["collisions"] == expected,"COLLISION_BINDING_INVALID")
    b.require(z["main_gate_after"] is False and b.MAIN_GATE is False,"GATE_INVALID")
    after = {n:b.filehash(out/n) for n in names}
    b.require(before == after and sum((out/n).stat().st_size for n in names) <= b.MAX_OUTPUT_BYTES,"EVIDENCE_CHANGED_OR_OVERSIZE")
    result = b.sealed(dict(run_id=out.name,status="S2OA_PRESEAL_BINDINGS_VALID",read_only=True,verification_calls=1,
        source_count=48,event_count=28,execution_digest=ex["execution_digest"],evaluation_digest=ev["evaluation_digest"],
        seal_digest=z["seal_digest"],file_hashes_before=before,file_hashes_after=after,
        payload_generation_calls=0,receptor_calls=0,nj_calls=0,
        limitation="Bindings, occurrences and declared hashes checked; no payload regeneration or receptor validity claim."),"verification_digest")
    b.publish(out/"verification.json",result,b.MAX_METADATA_BYTES)
    return result
