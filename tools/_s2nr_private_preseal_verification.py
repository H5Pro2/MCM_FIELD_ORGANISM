"""Offline NR seal inspection; never regenerates a payload."""
import hashlib
import json
from pathlib import Path

from tools import _s2nr_private_source_binding as b


def sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")).hexdigest()


def root(value,key):
    b.require(type(value) is dict and value.get(key)==sha({k:v for k,v in value.items() if k!=key}),"ROOT_DIGEST_INVALID")


def check_plans(execution,evaluation):
    root(execution,"execution_digest")
    root(evaluation,"evaluation_digest")
    b.require(evaluation["execution_digest"]==execution["execution_digest"],"ROOT_LINK_INVALID")
    b.require(execution["contract_sha256"]==evaluation["contract_sha256"]==b.PINS[b.CONTRACT],"CONTRACT_INVALID")
    specs=b.source_specs()
    b.require(execution["source_order"]==[s.source_id for s in specs] and len(execution["sources"])==17,"SOURCE_ORDER_INVALID")
    for spec,row in zip(specs,execution["sources"],strict=True):
        root(row,"source_digest")
        b.require(row==b.bind_source(spec,row["payload_sha256"]),"SOURCE_FORM_INVALID")
    # Independent checks of chronological clocks and modality presence.
    events=execution["events"]
    b.require(len(events)==18 and [e["ordinal"] for e in events]==list(range(1,19)),"EVENT_ORDER_INVALID")
    b.require([e["ordinal"] for e in events if e["event_type"]==b.A]==[2,4,17,18],"EVENT_KIND_INVALID")
    for i,e in enumerate(events):
        audio=e["auditory"]
        b.require((audio["clock_id"],audio["start_tick"],audio["end_tick"],audio["endpoint_snapshot_index"])
            ==("audio.sample",4800*i,4800*(i+1),10*i),"AUDIO_TIME_INVALID")
        b.require(audio["common_window"]==[100000000*(i+1)-10000000,100000000*(i+1)],"AUDIO_COMMON_TIME_INVALID")
        visual=e["visual"]
        b.require((visual is None)==(e["event_type"]==b.A),"MODALITY_FORM_INVALID")
        if visual is not None:
            b.require((visual["clock_id"],visual["start_tick"],visual["end_tick"])
                ==("video.frame",3*i+2,3*i+3),"VISUAL_TIME_INVALID")
            b.require(visual["common_window"]==[(3*i+2)*1000000000//30,100000000*(i+1)],"VISUAL_COMMON_TIME_INVALID")
    b.require(execution==b.execution_plan(execution["sources"],execution["environment"],
        execution["source_hashes"],execution["generators"]),"EXECUTION_FORM_INVALID")
    expected=[("e02","nr-a03","nr-a01","EXACT","BEFORE_TARGET","ABSTAIN"),
              ("e04","nr-a04","nr-a01","LEVEL","EARLY","A_RECENT"),
              ("e17","nr-a05","nr-a01","FREQUENCY","LATE","B_STABLE_AUDITORY"),
              ("e18","nr-a06",None,"INDEPENDENT_CONTROL","LATE","ABSTAIN")]
    b.require([tuple(row[k] for k in ("event_id","cue_id","target","subtype","phase","prediction"))
               for row in evaluation["cases"]]==expected and evaluation==b.evaluation_plan(execution),"EVALUATION_FORM_INVALID")
    b.require(not any(k in json.dumps(execution) for k in ('"target"','"prediction"','"subtype"','"retention_identity"')),
              "EVALUATION_LEAK")
    b.require(all(len(b.canonical(p))<=b.MAX_METADATA_BYTES for p in (execution,evaluation)),"METADATA_SIZE_EXCEEDED")


def verify_once(directory):
    out=Path(directory)
    target=out/"verification.json"
    pending=out/"verification.json.pending"
    b.require(not target.exists(),"VERIFICATION_ALREADY_EXISTS")
    # Claim this one attempt even if inspection fails.
    with pending.open("xb") as handle:
        handle.write(b.canonical(dict(run_id=out.name,verification_calls=1)))
    names=("execution-plan.json","evaluation-plan.json","seal.json","preregistration.json")
    before={n:b.filehash(out/n) for n in names}
    x,y,z,p=[json.loads((out/n).read_bytes()) for n in names]
    check_plans(x,y)
    root(z,"seal_digest")
    b.require(z["run_id"]==p["run_id"]==out.name and z["status"]=="S2NR_SOURCES_PRESEALED","RUN_BINDING_INVALID")
    b.require(z["execution_digest"]==x["execution_digest"] and z["evaluation_digest"]==y["evaluation_digest"]
        and z["execution_file_sha256"]==before[names[0]] and z["evaluation_file_sha256"]==before[names[1]],"SEAL_LINK_INVALID")
    b.require(z["hashes_before"]==z["hashes_after"]==x["source_hashes"]==p["hashes"]==b.watched(),"SOURCE_FILES_CHANGED")
    b.require(x["environment"]==p["environment"]==b.environment(),"ENVIRONMENT_CHANGED")
    _,_,gen=b.generators()  # Definition identity only, no generator calls.
    b.require(gen==x["generators"]==p["generators"],"GENERATOR_BINDING_INVALID")
    b.require(p["specs"]==[s.payload() for s in b.source_specs()] and p["events"]==x["events"]
        and p["profiles"]==x["profiles"] and p["budgets"]==b.budgets() and p["retry"] is False
        and p["qualification_sha256"]==b.filehash(b.QUAL_DIR/"result.json"),"PREREGISTRATION_INVALID")
    for k,v in dict(attempted_sources=17,completed_sources=17,generated_pcm_sources=6,generated_rgb_sources=11,
            generated_pcm_bytes=115200,generated_rgb_bytes=68428800,max_live_pcm_payloads=1,max_live_rgb_payloads=1).items():
        b.require(type(z[k]) is int and z[k]==v,"COUNTER_INVALID")
    for k in ("raw_payloads_persisted","receptor_calls","nj_calls","distance_calls","memory_calls","context_calls","field_calls","runtime_calls"):
        b.require(type(z[k]) is int and z[k]==0,"FORBIDDEN_EXECUTION")
    a,c=x["sources"][0],x["sources"][2]
    b.require(a["payload_sha256"]==c["payload_sha256"] and a["source_digest"]!=c["source_digest"]
        and z["exact_pairs"]==[["nr-a01","nr-a03"]],"EXACT_COPY_BINDING_INVALID")
    groups={}
    for row in x["sources"]:
        groups.setdefault((row["kind"],row["payload_sha256"]),[]).append(row["source_id"])
    collisions=[dict(kind=k,payload_sha256=h,source_ids=ids) for (k,h),ids in sorted(groups.items()) if len(ids)>1]
    b.require(z["collisions"]==collisions,"COLLISION_BINDING_INVALID")
    b.require(z["main_gate_after"] is False and b.MAIN_GATE is False,"GATE_INVALID")
    after={n:b.filehash(out/n) for n in names}
    b.require(before==after and sum((out/n).stat().st_size for n in names)<=b.MAX_OUTPUT_BYTES,"EVIDENCE_CHANGED_OR_OVERSIZE")
    result=b.sealed(dict(run_id=out.name,status="S2NR_PRESEAL_BINDINGS_VALID",verification_calls=1,read_only=True,
        execution_digest=x["execution_digest"],evaluation_digest=y["evaluation_digest"],seal_digest=z["seal_digest"],
        file_hashes_before=before,file_hashes_after=after,source_count=17,event_count=18,payload_generation_calls=0,
        payload_bytes_recomputed=False,receptor_calls=0,nj_calls=0,
        limitation="Recipe, time, profile, code and digest links checked; payload hashes not regenerated."),"verification_digest")
    b.publish(target,result,b.MAX_METADATA_BYTES)
    pending.unlink()
    return result
