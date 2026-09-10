"""Versioned OA-only main connection. Historical neutral limits stay unchanged."""
from dataclasses import asdict, dataclass
import hashlib
import json
import re
from pathlib import Path
import numpy as np
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import from_visual_receptor_state
from tools import _s2oa_private_runtime_binding as r
from tools import _s2oa_private_source_binding as source
from tools import _s2oa_private_administrative_verification as av
from tools import _s2oa_private_event_ids as ids

ROOT = r.admin.ROOT
MAIN_GATE = False
_USED = False
SCHEMA = "s2oa.bound-main.v2"
QUAL_ID = "s2oa-main-binding-qualification-20260910-01"
OLD_QUAL = ROOT/"reports/s2oa"/r.QUAL_ID
ADMIN_DIR = ROOT/"reports/s2oa"/r.admin.RUN_ID
PHASES = ("BINDINGS","PAYLOAD_GENERATION","PAYLOAD_HASH","AUDIO_ANALYSIS","VISUAL_ANALYSIS",
          "NJ_CONTACT","RUNTIME_INIT","FORMATION","CUE","EVIDENCE","CLOSE","SERIALIZATION")
COUNTS = dict(payloads=48,audio=22,visual=26,nj=22,materialized_events=28)
OWN = ("tools/_s2oa_private_main_binding.py","tools/_s2oa_private_main_verification.py",
       "tests/test_s2oa_private_main_binding.py","reports/s2oa/qualify_main_binding_once.py",
       "reports/s2oa/MAIN_QUALIFIKATIONSBINDUNG.md")
require, digest, canonical, sealed = r.require,r.digest,r.canonical,r.sealed


@dataclass(frozen=True, slots=True)
class BoundOA:
    execution_json: str
    provenance_json: str

    def execution(self):
        return json.loads(self.execution_json)

    def provenance(self):
        return json.loads(self.provenance_json)


def watched():
    from reports.s2oa.qualify_runtime_once import watched as prior
    return {**prior(),**source.watched(),**{p:r.admin.filehash(ROOT/p) for p in OWN},
            "tools/_s2oa_private_source_binding.py":r.admin.filehash(ROOT/"tools/_s2oa_private_source_binding.py"),
            "mcm_field_organism/finite_video_path.py":r.admin.filehash(ROOT/"mcm_field_organism/finite_video_path.py"),
            **{p:r.admin.filehash(ROOT/p) for p in ids.OWN}}


def validate_id_qualification_manifest(p,previous,hashes):
    require(p["run_id"]==ids.QUAL_ID,"ID_QUAL_BASE_INVALID")
    require(p["replaced_hashes"]==ids.OLD_HASHES
            and all(previous[k]==h for k,h in ids.OLD_HASHES.items()),"ID_QUAL_DELTA_INVALID")
    expected={**previous,**p["hashes"]}
    require(set(p["hashes"])==set(ids.OLD_HASHES)|set(ids.OWN)
            and expected==hashes and p["full_hashes_digest"]==digest(hashes),"ID_QUAL_CODE_INVALID")


def id_qualification(hashes):
    directory=ROOT/"reports/s2oa"/ids.QUAL_ID
    p=json.loads((directory/"preregistration.json").read_bytes())
    base=ROOT/"reports/s2oa"/QUAL_ID/"preregistration.json"
    require(p["base_sha256"]==r.admin.filehash(base),"ID_QUAL_BASE_INVALID")
    validate_id_qualification_manifest(p,json.loads(base.read_bytes())["hashes"],hashes)
    refs=qualification(directory,"S2OA_EVENT_IDS_QUALIFIED",ids.TEST_COUNT,hashes)
    q=json.loads((directory/"result.json").read_bytes())
    metrics=directory/"metrics.json"
    require(q["metrics_sha256"]==r.admin.filehash(metrics),"ID_QUAL_METRICS_INVALID")
    refs["metrics.json"]=dict(path=metrics.relative_to(ROOT).as_posix(),sha256=r.admin.filehash(metrics),bytes=metrics.stat().st_size)
    require(sum(x["bytes"] for x in refs.values())<=ids.QUAL_BYTES,"ID_QUAL_SIZE_INVALID")
    return refs


def qualification(directory, status, count, hashes):
    q=json.loads((directory/"result.json").read_bytes())
    p=json.loads((directory/"preregistration.json").read_bytes())
    r.admin.check_root(q,"result_digest")
    require(q["status"]==status and q["passed_tests"]==count and q["exit_code"]==0
            and q["test_calls"]==1 and q["hashes_unchanged"] is True,"QUALIFICATION_INVALID")
    require(q["preregistration_sha256"]==r.admin.filehash(directory/"preregistration.json")
            and q["hashes_before_digest"]==q["hashes_after_digest"]==digest(p["hashes"]),"QUALIFICATION_BINDING_INVALID")
    require(all(hashes.get(k)==v for k,v in p["hashes"].items()),"QUALIFIED_CODE_CHANGED")
    for name in ("stdout","stderr"):
        require(q[name+"_sha256"]==r.admin.filehash(directory/(name+".txt")),"QUALIFICATION_LOG_INVALID")
    return {n:dict(path=(directory/n).relative_to(ROOT).as_posix(),sha256=r.admin.filehash(directory/n),
                   bytes=(directory/n).stat().st_size) for n in ("preregistration.json","result.json","stdout.txt","stderr.txt")}


def load_bound():
    hashes=watched()
    old=qualification(OLD_QUAL,"S2OA_RUNTIME_QUALIFIED",20,hashes)
    idq=id_qualification(hashes)
    # Exact historical bytes remain historical; only the separately qualified delta is new.
    new=qualification(ROOT/"reports/s2oa"/QUAL_ID,"S2OA_MAIN_BINDING_QUALIFIED",14,{**hashes,**ids.OLD_HASHES})
    blobs=r.admin.read_archive()
    pr=json.loads((ADMIN_DIR/"preregistration.json").read_bytes())
    binding=json.loads((ADMIN_DIR/"binding.json").read_bytes())
    proof=json.loads((ADMIN_DIR/"verification.json").read_bytes())
    r.admin.check_root(binding,"binding_digest");r.admin.check_root(proof,"verification_digest")
    require(binding["status"]=="ADMINISTRATIVE_BINDING_COMPLETE" and proof["status"]=="ADMINISTRATIVE_BINDINGS_VALID"
            and proof["binding_digest"]==binding["binding_digest"],"ADMIN_BINDING_INVALID")
    require(binding["preregistration_sha256"]==r.admin.filehash(ADMIN_DIR/"preregistration.json")
            and pr["code_hashes"]==r.admin.watched(),"ADMIN_CODE_INVALID")
    av.check_archive_manifest(pr["archives"],blobs)
    av.verify_references(binding["execution"],binding["evaluation"],blobs)
    for name in ("binding.json","preregistration.json"):
        require(proof["hashes_before"][name]==proof["hashes_after"][name]==r.admin.filehash(ADMIN_DIR/name),"ADMIN_FILE_INVALID")
    for ref in pr["qualification"].values():
        require(r.admin.filehash(ROOT/ref["path"])==ref["sha256"],"ADMIN_QUAL_INVALID")
    actual_meta={n:(ADMIN_DIR/n).stat().st_size for n in ("binding.json","preregistration.json")}
    actual_meta.update({"qualification/"+n:(ROOT/ref["path"]).stat().st_size for n,ref in pr["qualification"].items()})
    actual_balance=av.check_totals(actual_meta,{k:len(v) for k,v in blobs.items()},r.admin.RESERVES,r.admin.OTHER_RESERVED)
    require(proof["balance"]==actual_balance,"ADMIN_ACCOUNTING_INVALID")
    ex=json.loads(blobs["execution"])
    require(ex["source_hashes"]==source.watched() and ex["environment"]==source.environment()
            and ex["profiles"]==source.profiles(),"SOURCE_ENVIRONMENT_INVALID")
    source.validate_events(ex["events"])
    prov=dict(execution_digest=ex["execution_digest"],evaluation_digest=json.loads(blobs["evaluation"])["evaluation_digest"],
        admin_binding_digest=binding["binding_digest"],admin_verification_digest=proof["verification_digest"],
        admin_files={n:dict(path=(ADMIN_DIR/n).relative_to(ROOT).as_posix(),sha256=r.admin.filehash(ADMIN_DIR/n))
                     for n in ("binding.json","preregistration.json","verification.json")},
        qualifications=dict(previous=old,main=new,event_ids=dict(qualification_id=ids.QUAL_ID,
            files={n:[z["sha256"],z["bytes"]] for n,z in idq.items()})),code_digest=digest(hashes),event_ids=ids.build(ex),
        metadata_bytes=proof["balance"]["metadata_bytes"]+sum(z["bytes"] for qs in (old,new,idq) for z in qs.values()),
        source_bytes=proof["balance"]["source_bytes"],prior_verification_bytes=(ADMIN_DIR/"verification.json").stat().st_size)
    bound=BoundOA(canonical(ex).decode(),canonical(prov).decode())
    validate_bound(bound)
    return bound


def validate_bound(bound):
    require(type(bound) is BoundOA,"OA_BINDING_REQUIRED")
    ex=bound.execution();p=bound.provenance();r.admin.check_root(ex,"execution_digest")
    require("event_ids" in p,"ID_BINDING_MISSING")
    ids.validate(p["event_ids"],ex)
    require(ex["execution_digest"]==p["execution_digest"] and ex["profiles"]["coordinator_config_digest"]==r.nn.profile.build_config().config_digest,"PROFILE_BINDING_INVALID")
    rows=ex["events"];ss=ex["sources"]
    require(len(rows)==28 and len(ss)==48 and ex["source_order"]==[s["source_id"] for s in ss]
            and len(set(ex["source_order"]))==48,"OA_COUNTS_INVALID")
    require([e["ordinal"] for e in rows]==list(range(1,29)) and len({e["event_id"] for e in rows})==28,"OA_ORDER_INVALID")
    kinds=[e["event_type"] for e in rows]
    require(kinds.count(source.AV)==20 and kinds.count(source.A)==2 and kinds.count(source.V)==6,"OA_COUNTS_INVALID")
    ordered=[]
    byid={s["source_id"]:s for s in ss}
    for g,e in enumerate(rows):
        require(type(e["ordinal"]) is int and all(type(t) is int for t in e["field_window"]),"OA_FIELD_TIME_INVALID")
        require(e["field_clock_id"]==r.CLOCK and e["field_window"]==[0 if g==0 else 200000000*g-100000000,200000000*g+100000000],"OA_FIELD_TIME_INVALID")
        for m,absent in (("auditory",source.V),("visual",source.A)):
            t=e[m]
            require((t is None)==(e["event_type"]==absent),"OA_MODALITY_INVALID")
            if t is None:continue
            require(all(type(t[k]) is int for k in ("start_tick","end_tick"))
                    and all(type(z) is int for z in t["common_window"]),"OA_NATIVE_TIME_INVALID")
            s=byid[t["source_id"]];ordered.append(s["source_id"]);r.admin.check_root(s,"source_digest")
            require(s["event_id"]==e["event_id"] and s["event_ordinal"]==g+1 and s["time_binding"]==t
                    and s["recipe_digest"]==digest(s["recipe"]),"OA_SOURCE_INVALID")
            if m=="auditory":
                require(type(t["nj_snapshot_index"]) is int and t["start_tick"]>=0 and t["start_tick"]%480==0
                        and t["nj_snapshot_index"]==t["start_tick"]//480,"OA_AUDIO_TIME_INVALID")
                expected=dict(source_id=s["source_id"],clock_id="audio.sample",start_tick=9600*g,end_tick=9600*g+4800,
                              nj_snapshot_index=20*g,common_window=[200000000*g,200000000*g+100000000])
                require(s["kind"]=="PCM" and s["byte_count"]==19200 and t==expected,"OA_AUDIO_TIME_INVALID")
            else:
                expected=dict(source_id=s["source_id"],clock_id="video.frame",start_tick=6*g+2,end_tick=6*g+3,
                    common_window=[(6*g+2)*1000000000//30,200000000*g+100000000])
                require(s["kind"]=="RGB" and s["byte_count"]==6220800 and t==expected,"OA_VISUAL_TIME_INVALID")
                require(s["recipe"]["visible_positions"]==(list(range(32)) if e["event_type"]==source.V else None),"OA_OCCLUSION_INVALID")
    require(ordered==ex["source_order"],"OA_SOURCE_ORDER_INVALID")
    return ex


class Materializer:
    def __init__(self,bound):
        self.ex=validate_bound(bound);self.bound=bound;self.config=r.nn.profile.build_config()
        self.phase="BINDINGS";self.ordinal=None;self.source_id=None;self.used=False
        self.counts={k:0 for k in COUNTS}

    def run_once(self):
        require(not self.used,"MATERIALIZER_ALREADY_USED");self.used=True
        pcm,rgb,identity=source.generators()
        require(identity==self.ex["generators"],"GENERATOR_BINDING_INVALID")
        audio=r.half.spectral.LogSpectralReceptor(r.nn.LogSpectralConfig())
        video=LocalChannelGridReceptor(VisualGridConfig())
        byid={s["source_id"]:s for s in self.ex["sources"]};out=[]
        for e in self.ex["events"]:
            self.ordinal=e["ordinal"];raw=visual=None;pd=vd=None
            for m in ("auditory","visual"):
                t=e[m]
                if t is None:continue
                s=byid[t["source_id"]];self.source_id=s["source_id"];self.phase="PAYLOAD_GENERATION"
                payload=pcm(s["recipe"]) if m=="auditory" else rgb(s["recipe"]["ordinal"])
                try:
                    if m=="visual":
                        if s["recipe"]["visible_positions"] is not None:source.occlude(payload,s["recipe"]["visible_positions"])
                        require(type(payload) is np.ndarray and payload.shape==(1080,1920,3)
                                and payload.dtype==np.uint8 and payload.flags.c_contiguous,"RGB_FORM_INVALID")
                        payload.flags.writeable=False
                    else:require(type(payload) is bytearray and len(payload)==19200,"PCM_FORM_INVALID")
                    self.phase="PAYLOAD_HASH"
                    with memoryview(payload).cast("B") as view:
                        require(view.nbytes==s["byte_count"] and hashlib.sha256(view).hexdigest()==s["payload_sha256"],"PAYLOAD_HASH_INVALID")
                    self.counts["payloads"]+=1
                    if m=="auditory":
                        self.phase="AUDIO_ANALYSIS"
                        samples=np.frombuffer(payload,dtype="<f4")
                        try:
                            require(np.all(np.isfinite(samples)) and np.all(np.abs(samples)<=1.0),"PCM_VALUES_INVALID")
                            values=audio.analyze(samples);self.counts["audio"]+=1
                        finally:del samples
                        activity=r.half.AuditoryReceptorContact.ACTIVE_ENERGY if any(values) else r.half.AuditoryReceptorContact.ACTIVE_ZERO
                        raw=r.half.AuditoryReceptorState("auditory",r.half.RAW_GEOMETRY,t["nj_snapshot_index"],t["start_tick"],t["end_tick"],audio.channel_ids,values,activity)
                        pd=s["payload_sha256"]
                    else:
                        self.phase="VISUAL_ANALYSIS"
                        state=video.analyze(payload,frame_index=t["start_tick"]);self.counts["visual"]+=1
                        visual=r.nn.OrganismTimedReceptorFrame(from_visual_receptor_state(state),r.nn.CommonFieldTime(r.CLOCK,*t["common_window"]))
                        vd=s["payload_sha256"];del state
                finally:del payload
            self.phase="NJ_CONTACT"
            item=bind_event(self.bound,e,config=self.config,
                raw_audio=raw,visual=visual,pcm_digest=pd,rgb_digest=vd)
            self.counts["nj"]+=int(raw is not None);self.counts["materialized_events"]+=1
            out.append(item);del raw,visual
        require(self.counts==COUNTS,"MATERIALIZATION_COUNTS_INVALID")
        return tuple(out)


def bind_event(bound,event,**kwargs):
    ex=bound.execution();mapping=bound.provenance().get("event_ids")
    ids.validate(mapping,ex)
    n=event.get("ordinal")
    require(type(n) is int and 1<=n<=28 and event==ex["events"][n-1],"ID_EVENT_INVALID")
    return r.bind_input(ordinal=n,event_id=ids.technical_id(mapping,event),kind=event["event_type"],**kwargs)


def check_inputs(inputs,bound):
    ex=validate_bound(bound)
    require(type(inputs) is tuple and len(inputs)==28 and all(type(x) is r.Input for x in inputs),"OA_INPUTS_INVALID")
    byid={s["source_id"]:s for s in ex["sources"]}
    for item,spec in zip(inputs,ex["events"],strict=True):
        event=item.event;src=json.loads(item.nj_json)
        require((event.event_id,event.ordinal,event.event_type)==(ids.technical_id(bound.provenance()["event_ids"],spec),spec["ordinal"],spec["event_type"]),"OA_EVENT_BINDING_INVALID")
        for m,key in (("auditory","pcm_digest"),("visual","rgb_digest")):
            t=spec[m]
            observed=None if m=="auditory" and src["nj"] is None else src["nj"][key] if m=="auditory" else src[key]
            require(observed==(None if t is None else byid[t["source_id"]]["payload_sha256"]),"OA_PAYLOAD_BINDING_INVALID")


class OARuntime(r.SingleRuntime):
    """Explicit 28/20/2/6 connection; inherited transitions/receipts are unchanged."""
    def __init__(self,inputs,run_id,*,bound,mode="OA"):
        require(mode=="OA" and MAIN_GATE,"OA_GATE_CLOSED");check_inputs(inputs,bound)
        self.config=r.nn.profile.build_config();self.inputs=inputs;self.run_id=run_id
        self.packed=[r.ng.pack_input(x.event,self.config) for x in inputs]
        self.source=[json.loads(x.nj_json) for x in inputs]
        self.binding=r.ng.build_binding(self.config,"ALL_BANDS_24")
        fs=r.null_field(self.config);ms=r.memory.initial_s2jv_composite_state(self.config)
        self.fb=r.ng.ObservedBranch(r.ng.field.build_s2lo_field_adapter(r.CLOCK),fs)
        self.mb=r.MemoryBranch(self.config,run_id,ms);self.scans={}
        processor=r.ng.stream.RoleFreePerceptionStreamProcessor(field_adapter=self.fb,memory_adapter=self.mb,
            auditory_scan=r.ng.AudioAdapter(self.binding,self.config,False,self.scans),
            auditory_baseline=r.ng.AudioAdapter(self.binding,self.config,True,self.scans),
            visual_scan=r.ng.VisualAdapter(self.config,False,self.scans),visual_baseline=r.ng.VisualAdapter(self.config,True,self.scans))
        rc=r.ng.runtime.build_minimal_runtime_config(runtime_id=run_id,max_event_count=28,
            source_binding_digest=digest(self.packed),component_binding_digest=self.binding.binding_digest)
        initial=r.ng.stream.initial_perception_stream_state(stream_id=run_id,field_state=fs,field_state_digest=fs.state_digest,
            memory_state=ms,memory_state_digest=ms.state_digest)
        self.subject=r.ng.runtime.MinimalMCMRuntime336(config=rc,processor=processor,initial_state=initial)
        self.rc=asdict(rc);self.rows=[];self.states={ms.state_digest:asdict(ms)}
        self.initial=dict(snapshot=asdict(self.subject.snapshot()),field=r.ng.field_record(fs),memory=ms.state_digest)
        self.births=[None]*24;self.chain=digest(dict(initial=ms.state_digest,config=self.config.config_digest))
        self.failed=False;self.phase="INITIAL";self.failure=None;self.closed=False


def envelope_size(value):
    p=value["bindings"]
    core=value["execution"]
    sizes=None if core is None else r.size_check(core)
    core_size=0 if core is None else len(canonical(core))
    shell=len(canonical(value))-core_size
    reserves={k:0 for k in r.admin.RESERVES} if sizes is None else sizes["ledger"]["reservations"]
    runtime_meta=0 if sizes is None else sizes["metadata_runtime_bytes"]
    balance=r.admin.ledger(dict(prior=p["metadata_bytes"],runtime=runtime_meta,shell=shell),
        dict(historical=p["source_bytes"]),reserves,other_total=core_size-runtime_meta-sum(reserves.values()))
    return dict(whole_record_bytes=len(canonical(value)),balance=balance,components=sizes)


def run_main_once(run_id):
    global MAIN_GATE,_USED
    out=None;c=None;m=None;bound=None;phase="BINDINGS";ordinal=None
    try:
        require(MAIN_GATE and not _USED and not r.MAIN_GATE and not source.MAIN_GATE,"MAIN_GATE_CLOSED")
        require(re.fullmatch(r"s2oa-continuous-runtime-\d{8}-\d{2}",run_id) is not None,"RUN_ID_INVALID")
        _USED=True
        target=ROOT/"reports/s2oa"/run_id;target.mkdir(exist_ok=False);out=target
        bound=load_bound();m=Materializer(bound)
        xs=m.run_once();phase="RUNTIME_INIT"
        c=OARuntime(xs,run_id,bound=bound)
        for item in xs:
            ordinal=item.event.ordinal
            phase="FORMATION" if item.event.event_type==source.AV else "CUE"
            c.process_next()
            if c.failed:break
        phase="CLOSE";core=c.finish()
        failure=None
        if c.failed:
            n=core["failure"]["ordinal"]
            failure={**core["failure"],"phase":"FORMATION" if xs[n-1].event.event_type==source.AV else "CUE",
                     "source_id":None,"error_class":"StreamBranchFailure"}
        value=sealed(dict(schema=SCHEMA,mode="OA",run_id=run_id,status=core["status"],bindings=bound.provenance(),
            counts=m.counts,execution=core,failure=failure,evaluation=None,main_gate=False),"record_digest")
        phase="SERIALIZATION";envelope_size(value)
        r.ng.ne.atomic_write(out/"record.json",value,4194304)
        return out
    except Exception as exc:
        if out is None or not out.exists() or (out/"record.json").exists():raise
        final=None
        if c is not None:
            if c.phase in ("EVIDENCE","CLOSE","SERIALIZATION"):phase=c.phase
            final=asdict(c.subject.close() if c.subject.snapshot().status=="OPEN" else c.subject.snapshot())
        if m is not None and c is None and m.counts["materialized_events"]<28:
            phase,ordinal=m.phase,m.ordinal
        failure=dict(phase=phase,ordinal=ordinal,source_id=None if m is None or c is not None else m.source_id,
            completed_events=0 if final is None else final["processed_event_count"],
            error_class=type(exc).__name__,code=getattr(exc,"code","OA_TECHNICAL_ERROR"),
            last_snapshot_digest=None if final is None else final["snapshot_digest"],final=final)
        value=sealed(dict(schema=SCHEMA,mode="OA",run_id=run_id,status="NOT_EVALUABLE",
            bindings=None if bound is None else bound.provenance(),counts={k:0 for k in COUNTS} if m is None else m.counts,
            execution=None,failure=failure,evaluation=None,main_gate=False),"record_digest")
        r.ng.ne.atomic_write(out/"record.json",value,65536)
        return out
    finally:MAIN_GATE=False
