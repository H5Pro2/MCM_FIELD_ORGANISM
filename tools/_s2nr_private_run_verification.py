"""One offline NR check; no payload, receptor, projection or runtime execution."""
from dataclasses import asdict
import json
from pathlib import Path
from tools import _s2nr_private_run as run
from tools import _s2nr_private_runtime_verification as composition

nn,ng=run.nn,run.ng
require,check,digest,canonical=run.require,run.check,run.digest,run.canonical


def decode_parent(p,config):
    q=dict(p["projection"])
    for k in ("carrier_ids","values","subnormal_band_indices","underflow_band_indices"):
        q[k]=tuple(q[k])
    projection=nn.half.HalfScaleAuditory48V1(**q)
    nn.half.validate_projection(projection)
    operation=p["operations"][0]
    if p["event"]["event_type"]==run.source.A:
        cue=nn.profile.bind_cue(projection=projection,pcm_digest=p["pcm_digest"],config=config)
        operation=asdict(ng.stream.AuditoryCueOperationV1(cue,ng.audio.kz.build_auditory_band_plan_48()))
    event=composition.old.decode_input(dict(event=p["event"],field=p["field"],operation=operation),config)
    value=nn.HalfRuntimeInputV1(event,projection,p["pcm_digest"],p["rgb_digest"],config.config_digest,
        nn.sources(),p["parent_binding_digest"])
    nn.validate_input(value,config)
    require(canonical(run.runtime.pack_input(value,config))==canonical(p),"PACKED_INPUT_INVALID")
    return value


def source_receipts(record,bound,inputs):
    plan=bound.payload()
    catalog={s["source_id"]:s for s in plan["sources"]}
    require(len(inputs)==len(record["source_receipts"])==len(plan["events"]),"SOURCE_COUNT_INVALID")
    for spec,p,row in zip(plan["events"],inputs,record["source_receipts"],strict=True):
        check(row,"receipt_digest")
        require(row["spec_digest"]==digest(spec) and row["parent_binding_digest"]==p.binding_digest
            and row["projection_digest"]==p.auditory_projection.projection_digest
            and p.event.event_id=="s2nr-event-"+spec["event_id"] and p.event.ordinal==spec["ordinal"]
            and p.event.event_type==spec["event_type"],"EVENT_SOURCE_INVALID")
        f=p.event.field_payload
        require([f.start_tick,f.end_tick]==spec["field_window"],"FIELD_WINDOW_INVALID")
        frames={t.frame.modality_id:t for t in f.timed_frames}
        require(set(frames)==({"auditory","visual"} if spec["visual"] else {"auditory"}),"MODALITY_INVALID")
        for mod in ("auditory","visual"):
            part=spec[mod]
            if part is None:
                require(row["sources"][mod] is None and p.rgb_digest is None,"UNEXPECTED_SOURCE")
                continue
            s=catalog[part["source_id"]]
            require(row["sources"][mod]==dict(source_id=s["source_id"],source_digest=s["source_digest"],payload_sha256=s["payload_sha256"])
                and (p.pcm_digest if mod=="auditory" else p.rgb_digest)==s["payload_sha256"],"PAYLOAD_SOURCE_INVALID")
            t=frames[mod]
            require((t.frame.clock_id,t.frame.window_start_tick,t.frame.window_end_tick)==(part["clock_id"],part["start_tick"],part["end_tick"])
                and (t.field_time.clock_id,t.field_time.window_start_tick,t.field_time.window_end_tick)
                ==(spec["field_clock_id"],*part["common_window"]),"MODALITY_TIME_INVALID")
        require(p.auditory_projection.snapshot_index==spec["auditory"]["endpoint_snapshot_index"],"ENDPOINT_INVALID")


def verify_failure(record,bound):
    f=record["failure"]
    require(record["status"]=="NOT_EVALUABLE" and record["comparison"] is None and type(f) is dict
        and f["phase"] in run.PHASES and type(f["code"]) is str and type(f["error_class"]) is str,"FAILURE_FORM_INVALID")
    p=bound.payload()
    n=f["ordinal"]
    require(n is None or type(n) is int and 1<=n<=len(p["events"]),"FAILURE_ORDINAL_INVALID")
    require(type(f["completed_runtime_events"]) is int and 0<=f["completed_runtime_events"]<=len(p["events"])
        and len(f["last_snapshot_digests"])<=2 and all(run.runtime.s.hash_form(h) for h in f["last_snapshot_digests"]),"FAILURE_PROGRESS_INVALID")
    if f["source_id"] is not None:
        require(n is not None and f["source_id"] in [t["source_id"] for t in (p["events"][n-1]["auditory"],p["events"][n-1]["visual"]) if t],"FAILURE_SOURCE_INVALID")
    m=record["materialization"]
    if m is not None:
        require(set(m)==set(run.metrics()) and all(type(v) is int and v>=0 for v in m.values()),"FAILURE_COUNTER_INVALID")
        require(m["audio_windows"]<=len(p["events"]) and m["audio_hops"]<=10*len(p["events"])
            and m["audio_snapshots"]==max(0,m["audio_hops"]-9)
            and m["audio_windows"]*10<=m["audio_hops"]<=m["audio_windows"]*10+10
            and m["completed_events"]<=m["nj_projections"]<=m["audio_windows"]
            and m["visual_frames"]<=sum(e["visual"] is not None for e in p["events"]),"FAILURE_COUNTER_INVALID")
        if f["phase"] in run.PHASES[2:8]:
            require(n is not None and m["completed_events"]==n-1 and f["completed_runtime_events"]==0
                and f["last_snapshot_digests"]==[],"FAILURE_PHASE_PROGRESS_INVALID")


def verify_record(record,*,bound,config):
    try:
        return _verify(record,bound,config)
    except run.S2NRRunError:
        raise
    except (KeyError,ValueError,TypeError,AttributeError,IndexError,ng.memory.S2JWCoordinatorError) as exc:
        raise run.S2NRRunError("TOTAL_BINDING_INVALID") from exc


def _verify(record,bound,config):
    before=digest(record)
    check(record,"record_digest")
    nn.validate_config(config)
    require(record["schema"]==run.SCHEMA and record["mode"]==bound.mode
        and record["execution_digest"]==bound.payload()["execution_digest"]
        and record["config_digest"]==config.config_digest and record["profile_digest"]==nn.half.PROFILE_DIGEST
        and record["source_versions"]==run.watched() and record["main_gate_after"] is False,"TOTAL_BINDING_INVALID")
    require(len(canonical(record))<=ng.MAX_BYTES and len(canonical({**record,"comparison":None}))<=65536,"ENVELOPE_SIZE_EXCEEDED")
    proof=None
    if record["failure"] is not None:
        verify_failure(record,bound)
    else:
        c=record["comparison"]
        require(c["mode"]==bound.mode and c["comparison_id"]==record["run_id"]
            and record["status"]==c["status"],"COMPOSITION_BINDING_INVALID")
        inputs=tuple(decode_parent(p,config) for p in c["inputs"])
        source_receipts(record,bound,inputs)
        p=bound.payload()
        require(record["materialization"]==run.metrics(len(p["events"]),sum(e["visual"] is not None for e in p["events"])),"MATERIALIZATION_COUNT_INVALID")
        proof=composition.verify_record(c,inputs=inputs,config=config)
        if bound.mode=="MAIN" and record["status"]=="RECORDING_COMPLETE":
            require((proof["events"],proof["scan_receipts"],proof["field_contacts"],proof["formation_relations"])
                ==(18,16,9792,28),"MAIN_COUNT_INVALID")
    require(digest(record)==before,"RECORD_MUTATED")
    return run.sealed(dict(status=record["status"],record_digest=record["record_digest"],read_only=True,
        composition=proof,source_time_bindings=True,
        numeric_scope="Stored rounded projection, contacts, scans and state relations; no raw-to-half reconstruction",
        raw_provenance_scope="Digest links only; no raw values retained and no independent numerical NJ recomputation"),"verification_digest")


def verify_file_once(path):
    path=Path(path)
    proof_path=path.with_name("verification.json")
    require(not proof_path.exists(),"VERIFICATION_ALREADY_EXISTS")
    # Claim before verification; a failed check cannot silently be retried.
    with path.with_name("verification.claim").open("xb") as f:
        f.write(b"s2nr-read-only-once-v3")
    before=run.source.filehash(path)
    record=json.loads(path.read_bytes())
    proof=verify_record(record,bound=run.load_execution(),config=nn.profile.build_config())
    require(run.source.filehash(path)==before,"RECORD_FILE_CHANGED")
    result=run.sealed(dict(proof=proof,file_sha256=before,file_unchanged=True),"report_digest")
    ng.ne.atomic_write(proof_path,result)
    return result
