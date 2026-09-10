"""Finite caller-owned payloads; unchanged half-profile mechanics, no generators."""
from dataclasses import asdict, dataclass
import ast
import hashlib
import json
from pathlib import Path
import platform
import re
import sys
import numpy as np
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import from_visual_receptor_state
from tools import _s2oa_private_runtime_binding as r

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "s2ob.caller.v1"
CLOCK = "s2ob-caller-field-clock"
AV, A, V = "COMPLETE_AV_PERCEPTION", "PARTIAL_AUDITORY_CUE", "PARTIAL_VISUAL_CUE"
MAIN_GATE = False
QUAL_ID = "s2ob-caller-qualification-20260910-01"
QUAL_DIR = ROOT / "reports/s2ob" / QUAL_ID
CONFIG_DIGEST = "55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e"
OWN = ("tools/_s2ob_private_caller_binding.py", "tools/_s2ob_private_caller_verification.py",
       "tests/test_s2ob_private_caller_binding.py", "reports/s2ob/qualify_once.py",
       "reports/s2ob/QUALIFIKATION.md")
PHASES = ("BINDINGS", "RUNTIME_INIT", "PAYLOAD_READ", "PAYLOAD_HASH", "AUDIO_ANALYSIS",
          "VISUAL_ANALYSIS", "NJ_CONTACT", "EVENT", "EVIDENCE", "CLOSE", "SERIALIZATION")
LIMITS = dict(metadata=65536, sources=174080, nj=22528, formations=30720,
              generations=30720, shared=262144, total=4194304, verification=262144)
RESERVED = dict(qualification=4096, report=512, verification=262144)
digest, canonical, sealed = r.digest, r.canonical, r.sealed


class S2OBError(ValueError):
    def __init__(self, code, balance=None):
        self.code, self.balance = code, balance
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2OBError(code)


def check_root(value, key):
    require(type(value) is dict and value.get(key) == digest({k:v for k,v in value.items() if k != key}), "DIGEST_INVALID")


def identifier(value):
    # Reserve room for the unchanged -owner / -consume suffixes.
    require(type(value) is str and re.fullmatch(r"[a-z][a-z0-9-]{7,79}", value) is not None, "ID_INVALID")


@dataclass(frozen=True, slots=True)
class Payload:
    source_id: str
    path: str
    sha256: str
    byte_count: int


@dataclass(frozen=True, slots=True)
class Event:
    event_id: str
    ordinal: int
    kind: str
    field_window: tuple[int, int]
    audio_window: tuple[int, int] | None
    audio_index: int | None
    audio_common: tuple[int, int] | None
    visual_window: tuple[int, int] | None
    visual_common: tuple[int, int] | None
    pcm: Payload | None
    rgb: Payload | None


@dataclass(frozen=True, slots=True)
class Manifest:
    schema: str
    run_id: str
    field_clock_id: str
    config_digest: str
    profile_digest: str
    code_digest: str
    events: tuple[Event, ...]
    manifest_digest: str


def expected_times(ordinal, kind):
    g = ordinal - 1
    ha, hv = kind != V, kind != A
    return dict(field_window=(0 if g == 0 else 200000000*g-100000000, 200000000*g+100000000),
        audio_window=(9600*g, 9600*g+4800) if ha else None, audio_index=20*g if ha else None,
        audio_common=(200000000*g, 200000000*g+100000000) if ha else None,
        visual_window=(6*g+2, 6*g+3) if hv else None,
        visual_common=((6*g+2)*1000000000//30, 200000000*g+100000000) if hv else None)


def payload_path(p):
    require(type(p) is Payload and type(p.path) is str and not Path(p.path).is_absolute(), "PAYLOAD_BINDING_INVALID")
    path = (ROOT/p.path).resolve()
    require(path.is_relative_to(ROOT) and path.as_posix() == (ROOT/p.path).as_posix(), "PAYLOAD_PATH_INVALID")
    identifier(p.source_id)
    require(r.ng.stream._valid_digest(p.sha256) and type(p.byte_count) is int, "PAYLOAD_BINDING_INVALID")
    return path


def validate_manifest(m):
    require(type(m) is Manifest and type(m.events) is tuple and 1 <= len(m.events) <= 28, "MANIFEST_INVALID")
    identifier(m.run_id)
    require(m.schema == SCHEMA and m.field_clock_id == CLOCK, "MANIFEST_PROFILE_INVALID")
    require(m.config_digest == CONFIG_DIGEST and m.profile_digest == r.half.PROFILE_DIGEST, "PROFILE_INVALID")
    require(r.ng.stream._valid_digest(m.code_digest), "CODE_BINDING_INVALID")
    check_root(asdict(m), "manifest_digest")
    ids, sources = set(), set()
    for n, e in enumerate(m.events, 1):
        require(type(e) is Event and type(e.ordinal) is int and e.ordinal == n and e.kind in (AV,A,V), "EVENT_ORDER_INVALID")
        identifier(e.event_id)
        require(e.event_id not in ids, "ID_DUPLICATE"); ids.add(e.event_id)
        for key, value in expected_times(n,e.kind).items():
            observed = getattr(e,key)
            require(observed == value and (observed is None or
                (type(observed) is int if key == "audio_index" else
                 type(observed) is tuple and all(type(x) is int for x in observed))), "TIME_INVALID")
        for p, needed, size in ((e.pcm,e.kind != V,19200),(e.rgb,e.kind != A,6220800)):
            require((p is not None) == needed, "MODALITY_INVALID")
            if p is not None:
                payload_path(p)
                require(p.byte_count == size and p.source_id not in sources, "SOURCE_BINDING_INVALID")
                sources.add(p.source_id)
    kinds = [e.kind for e in m.events]
    f,a,v = (kinds.count(k) for k in (AV,A,V))
    require(f <= 20 and a <= 2 and v <= 6, "EVENT_LIMIT")
    require(len(canonical(asdict(m))) <= 32768, "MANIFEST_SIZE_LIMIT")
    return dict(events=len(kinds),formations=f,auditory_cues=a,visual_cues=v,
        audio=f+a,nj=f+a,visual=f+v,payloads=2*f+a+v,scans=2*(a+v),contacts=336*f+48*a+288*v)


def build_manifest(run_id, events, code_digest):
    value = dict(schema=SCHEMA,run_id=run_id,field_clock_id=CLOCK,config_digest=CONFIG_DIGEST,
                 profile_digest=r.half.PROFILE_DIGEST,code_digest=code_digest,events=events)
    m = Manifest(**value,manifest_digest=digest({**value,"events":[asdict(e) for e in events]}))
    validate_manifest(m)
    return m


def decode_manifest(value):
    require(type(value) is dict and set(value)==set(Manifest.__dataclass_fields__), "MANIFEST_INVALID")
    try:
        rows=[]
        for row in value["events"]:
            e=dict(row)
            for key in ("field_window","audio_window","audio_common","visual_window","visual_common"):
                if e[key] is not None: e[key]=tuple(e[key])
            for key in ("pcm","rgb"):
                if e[key] is not None: e[key]=Payload(**e[key])
            rows.append(Event(**e))
        m=Manifest(**{**value,"events":tuple(rows)})
        validate_manifest(m)
        return m
    except (TypeError,KeyError) as exc:
        raise S2OBError("MANIFEST_INVALID") from exc


def code_inventory():
    """Conservative static local import closure plus historical digest dependencies.

    Source files are software prerequisites, not duplicated research artifacts.
    Their full path/hash/byte inventory is itself a charged source attachment.
    """
    pending=set(OWN)|set(r.ng.SOURCE_PATHS)|{p for p,_ in r.nn.sources()}
    found={}
    while pending:
        path=pending.pop()
        if path in found: continue
        raw=(ROOT/path).read_bytes()
        found[path]=[hashlib.sha256(raw).hexdigest(),len(raw)]
        if not path.endswith(".py"): continue
        tree=ast.parse(raw.decode("utf-8-sig"))
        package=path.replace("/",".").rsplit(".",1)[0].split(".")[:-1]
        names=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import): names.extend(a.name for a in node.names)
            elif isinstance(node,ast.ImportFrom):
                prefix=".".join(package[:len(package)-node.level+1]) if node.level else ""
                base=".".join(x for x in (prefix,node.module) if x)
                names.append(base); names.extend(base+"."+a.name for a in node.names if a.name!="*")
        for name in names:
            if name.split(".")[0] not in ("tools","mcm_field_organism","reports","tests"): continue
            parts=name.split(".")
            for i in range(1,len(parts)+1):
                stem="/".join(parts[:i])
                for candidate in (stem+".py",stem+"/__init__.py"):
                    if (ROOT/candidate).is_file() and candidate not in found: pending.add(candidate)
    return dict(schema="s2ob.code-closure.v1",files=dict(sorted(found.items())),
        environment=dict(python=sys.version,implementation=platform.python_implementation(),
            executable_sha256=hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),numpy=np.__version__))


def read_payload(p):
    with payload_path(p).open("rb") as f:
        raw=f.read(p.byte_count+1)
    require(len(raw)==p.byte_count, "PAYLOAD_SIZE_INVALID")
    require(hashlib.sha256(raw).hexdigest()==p.sha256, "PAYLOAD_HASH_INVALID")
    return raw


class Materializer:
    def __init__(self, manifest):
        self.manifest=manifest; self.expected=validate_manifest(manifest)
        self.config=r.nn.profile.build_config()
        r.nn.validate_config(self.config)
        self.audio=r.half.spectral.LogSpectralReceptor(r.nn.LogSpectralConfig())
        self.video=LocalChannelGridReceptor(VisualGridConfig())
        self.counts=dict(payloads=0,audio=0,nj=0,visual=0,materialized_events=0)
        self.phase="BINDINGS"; self.ordinal=None; self.source_id=None

    def next(self, event):
        require(event == self.manifest.events[self.counts["materialized_events"]], "MATERIALIZATION_ORDER_INVALID")
        self.ordinal=event.ordinal; raw_audio=visual=None
        for modality,p in (("auditory",event.pcm),("visual",event.rgb)):
            if p is None: continue
            self.source_id=p.source_id; self.phase="PAYLOAD_READ"
            self.phase="PAYLOAD_HASH"; payload=read_payload(p)
            try:
                self.counts["payloads"]+=1
                if modality=="auditory":
                    self.phase="AUDIO_ANALYSIS"
                    samples=np.frombuffer(payload,dtype="<f4")
                    try:
                        require(np.all(np.isfinite(samples)) and np.all(np.abs(samples)<=1.0), "PCM_VALUES_INVALID")
                        values=self.audio.analyze(samples); self.counts["audio"]+=1
                    finally: del samples
                    activity=r.half.AuditoryReceptorContact.ACTIVE_ENERGY if any(values) else r.half.AuditoryReceptorContact.ACTIVE_ZERO
                    raw_audio=r.half.AuditoryReceptorState("auditory",r.half.RAW_GEOMETRY,event.audio_index,
                        *event.audio_window,self.audio.channel_ids,values,activity)
                else:
                    self.phase="VISUAL_ANALYSIS"
                    frame=np.frombuffer(payload,dtype=np.uint8).reshape(1080,1920,3)
                    try:
                        if event.kind==V:
                            cells=frame.reshape(8,135,12,160,3)
                            for i in range(32,288):
                                cell,channel=divmod(i,3); row,col=divmod(cell,12)
                                require(not np.any(cells[row,:,col,:,channel]), "CUE_NOT_OCCLUDED")
                            del cells
                        state=self.video.analyze(frame,frame_index=event.visual_window[0]); self.counts["visual"]+=1
                    finally: del frame
                    visual=r.nn.OrganismTimedReceptorFrame(from_visual_receptor_state(state),
                        r.nn.CommonFieldTime(CLOCK,*event.visual_common))
            finally: del payload
        self.phase="NJ_CONTACT"
        item=bind_input(config=self.config,ordinal=event.ordinal,event_id=event.event_id,kind=event.kind,
            raw_audio=raw_audio,visual=visual,pcm_digest=None if event.pcm is None else event.pcm.sha256,
            rgb_digest=None if event.rgb is None else event.rgb.sha256)
        self.counts["nj"]+=int(raw_audio is not None); self.counts["materialized_events"]+=1
        return item


# Same canonical contact construction; separately bound caller clock and schema.
# Historical OA validation remains unchanged.
nn, ng, half = r.nn, r.ng, r.half
Input = r.Input


def bind_input(*,config,ordinal,event_id,kind,raw_audio=None,visual=None,pcm_digest=None,rgb_digest=None):
    nn.validate_config(config)
    require(type(ordinal) is int and 1 <= ordinal <= 28,"ORDINAL_INVALID")
    g = ordinal-1
    audio_time = nn.CommonFieldTime(CLOCK,200000000*g,200000000*g+100000000)
    visual_time = nn.CommonFieldTime(CLOCK,(6*g+2)*1000000000//30,200000000*g+100000000)
    full = kind == "COMPLETE_AV_PERCEPTION"
    ha, hv = full or kind == "PARTIAL_AUDITORY_CUE", full or kind == "PARTIAL_VISUAL_CUE"
    require(kind in ng.stream.EVENT_TYPES and (raw_audio is not None)==ha and (visual is not None)==hv,"MODALITY_INVALID")
    require((ng.audio.kz._valid_digest(pcm_digest) if ha else pcm_digest is None)
            and (ng.audio.kz._valid_digest(rgb_digest) if hv else rgb_digest is None),"SOURCE_INVALID")
    if hv:
        require(visual.field_time == visual_time and visual.frame.clock_id == "video.frame"
                and (visual.frame.window_start_tick,visual.frame.window_end_tick)==(6*g+2,6*g+3),"VISUAL_TIME_INVALID")
        ng.pairing._validate_timed_frame(visual,modality="visual",profile=config.profile.profile)
    p = None
    if ha:
        require(type(raw_audio) is half.AuditoryReceptorState and
                (raw_audio.snapshot_index,raw_audio.window_start_sample,raw_audio.window_end_sample)==(20*g,9600*g,9600*g+4800),"RAW_TIME_INVALID")
        p = half.project_auditory_half_v1(raw_audio,config=nn.LogSpectralConfig(),source_profile_digest=half.RAW_PROFILE_DIGEST)
        auditory = nn.OrganismTimedReceptorFrame(nn.ReceptorContactFrame("auditory",p.geometry_id,
            "half."+p.projection_digest,p.clock_id,p.window_start_tick,p.window_end_tick,p.carrier_ids,p.values),audio_time)
    if full:
        op = nn.profile.bind_pair(projection=p,visual=visual,common_time=audio_time,
                                 pcm_digest=pcm_digest,rgb_digest=rgb_digest,pair_id=event_id)
        frames, perception = (op.auditory.timed_frame,visual),op.pairing_digest
    elif ha:
        cue = nn.profile.bind_cue(projection=p,pcm_digest=pcm_digest,config=config)
        op = ng.stream.AuditoryCueOperationV1(cue,ng.audio.kz.build_auditory_band_plan_48())
        frames, perception = (auditory,),cue.cue_digest
    else:
        require(all(visual.frame.values[i]==0.0 for i in ng.visual.MASKED_POSITIONS),"CUE_NOT_OCCLUDED")
        op = ng.visual.build_masked_memory_cue_336(source_digest=rgb_digest,config_digest=config.config_digest,
            field_clock_id=CLOCK,window_start_tick=visual_time.window_start_tick,window_end_tick=visual_time.window_end_tick,
            visual_source_clock_id="video.frame",visual_window_start_tick=6*g+2,visual_window_end_tick=6*g+3,
            values=tuple(visual.frame.values[i] if i<32 else None for i in range(288)))
        frames,perception = (visual,),op.cue_digest
    nj = None if p is None else dict(source_state_digest=p.source_state_digest,source_values_digest=p.source_values_digest,
        projection_digest=p.projection_digest,subnormal_band_indices=list(p.subnormal_band_indices),
        underflow_band_indices=list(p.underflow_band_indices),pcm_digest=pcm_digest)
    source = digest(dict(schema=SCHEMA,nj=nj,rgb_digest=rgb_digest,profile=half.PROFILE_DIGEST))
    f = ng.field.S2LOFieldInputV1(perception,0 if g==0 else 200000000*g-100000000,audio_time.window_end_tick,frames)
    event = ng.stream.build_perception_stream_event(event_id=event_id,ordinal=ordinal,event_type=kind,
        source_digest=source,perception_digest=perception,field_projection_digest=perception,
        operation_projection_digest=perception,field_payload=f,operation_payload=op)
    ng.pack_input(event,config)
    # RGB provenance already belongs to the operation/source contract, no full duplicate frame.
    receipt = dict(nj=nj,rgb_digest=rgb_digest,source_digest=source)
    require(len(canonical(receipt))<=1024,"NJ_ITEM_LIMIT")
    return Input(event,canonical(receipt).decode("ascii"))


class CallerRuntime:
    """One fresh MR instance, incremental materialized inputs, no section reset."""
    def __init__(self, manifest):
        self.expected=validate_manifest(manifest); self.manifest=manifest
        self.config=r.nn.profile.build_config(); self.run_id=manifest.run_id
        self.inputs=[]; self.packed=[]; self.source=[]
        self.binding=r.ng.build_binding(self.config,"ALL_BANDS_24")
        fs=r.null_field(self.config); ms=r.memory.initial_s2jv_composite_state(self.config)
        self.fb=r.ng.ObservedBranch(r.ng.field.build_s2lo_field_adapter(CLOCK),fs)
        self.mb=r.MemoryBranch(self.config,self.run_id,ms); self.scans={}
        processor=r.ng.stream.RoleFreePerceptionStreamProcessor(field_adapter=self.fb,memory_adapter=self.mb,
            auditory_scan=r.ng.AudioAdapter(self.binding,self.config,False,self.scans),
            auditory_baseline=r.ng.AudioAdapter(self.binding,self.config,True,self.scans),
            visual_scan=r.ng.VisualAdapter(self.config,False,self.scans),
            visual_baseline=r.ng.VisualAdapter(self.config,True,self.scans))
        rc=r.ng.runtime.build_minimal_runtime_config(runtime_id=self.run_id,max_event_count=len(manifest.events),
            source_binding_digest=manifest.manifest_digest,component_binding_digest=self.binding.binding_digest)
        initial=r.ng.stream.initial_perception_stream_state(stream_id=self.run_id,field_state=fs,field_state_digest=fs.state_digest,
            memory_state=ms,memory_state_digest=ms.state_digest)
        self.subject=r.ng.runtime.MinimalMCMRuntime336(config=rc,processor=processor,initial_state=initial)
        self.rc=asdict(rc); self.rows=[]; self.states={ms.state_digest:asdict(ms)}
        self.initial=dict(snapshot=asdict(self.subject.snapshot()),field=r.ng.field_record(fs),memory=ms.state_digest)
        self.births=[None]*24; self.chain=digest(dict(initial=ms.state_digest,config=self.config.config_digest))
        self.failed=False; self.phase="INITIAL"; self.failure=None; self.closed=False

    def process(self,item):
        require(not self.closed and not self.failed and len(self.rows)<len(self.manifest.events), "LIFECYCLE_INVALID")
        spec=self.manifest.events[len(self.rows)]
        require(type(item) is Input and (item.event.event_id,item.event.ordinal,item.event.event_type)==
                (spec.event_id,spec.ordinal,spec.kind), "EVENT_BINDING_INVALID")
        self.inputs.append(item); self.packed.append(r.ng.pack_input(item.event,self.config))
        self.source.append(json.loads(item.nj_json))
        # Reuse the qualified atomic transaction, generation and MR receipt path.
        return r.SingleRuntime.process_next(self)

    def close(self):
        if self.closed: return asdict(self.subject.snapshot())
        self.phase="CLOSE"; prior=self.subject.snapshot()
        final=self.subject.close(); self.closed=True
        require((prior.field_state_digest,prior.memory_state_digest)==
                (final.field_state_digest,final.memory_state_digest), "CLOSE_MUTATED")
        return asdict(final)

    def record(self):
        require(self.failed or len(self.rows)==len(self.manifest.events), "INCOMPLETE")
        final=self.close()
        result=sealed(dict(schema=SCHEMA,status="NOT_EVALUABLE" if self.failed else "RECORDING_COMPLETE",run_id=self.run_id,
            config_digest=self.config.config_digest,runtime_config=self.rc,binding=asdict(self.binding),initial=self.initial,final=final,
            inputs=self.packed,source_receipts=self.source,rows=self.rows,states=self.states,
            scans=[dict(ordinal=n,role=role,value=asdict(x)) for (n,role),x in sorted(self.scans.items())],
            failure=self.failure,main_gate=False),"record_digest")
        core_sizes(result)
        return result


def core_sizes(x):
    size=lambda a:len(canonical(a))
    states=list(x["states"].values()); inputs=x["inputs"]; scans=x["scans"]
    forms=[z["formation"] for z in x["rows"] if z["formation"] is not None]
    gens=[z["generations"] for z in x["rows"] if z["generations"] is not None]
    nj=[z for z in x["source_receipts"] if z["nj"] is not None]
    steps=[{k:v for k,v in z.items() if k not in ("formation","generations")} for z in x["rows"]]
    violations=[]
    groups=dict(states=(states,21,98304),inputs=(inputs,28,16384),scans=(scans,16,32767),
        steps=(steps,28,16384),nj=(nj,22,1024),formations=(forms,20,1536),generations=(gens,20,1536))
    sizes={k:list(map(size,v[0])) for k,v in groups.items()}
    for k,(_,count,cap) in groups.items():
        if len(sizes[k])>count or any(n>cap for n in sizes[k]): violations.append(k.upper()+"_LIMIT")
    data=sum(sum(ns) for ns in sizes.values())
    out=dict(record_bytes=size(x),metadata_runtime_bytes=size(x)-data,items=sizes)
    if violations: raise S2OBError("ITEM_LIMIT",dict(**out,violations=violations))
    return out


def balance(value, references, *, proof_bytes=RESERVED["verification"], report_bytes=RESERVED["report"]):
    require(type(references) is tuple and all(type(z) is tuple and len(z)==3 and z[0] in ("metadata","sources","verification")
        and type(z[1]) is str and type(z[2]) is int and z[2]>=0 for z in references), "REFERENCE_SIZE_INVALID")
    require(len({p for _,p,_ in references})==len(references), "REFERENCE_DUPLICATE")
    core=value.get("execution"); c=None if core is None else core_sizes(core)
    items={} if c is None else c["items"]
    sums={k:sum(items.get(k,[])) for k in ("nj","formations","generations")}
    record_bytes=len(canonical(value))
    meta=record_bytes-(0 if c is None else c["record_bytes"]-c["metadata_runtime_bytes"])
    contributions=dict(metadata=[["record_metadata",meta],["qualification_reserve",4096],["report_reserve",report_bytes]],
                       sources=[],verification=[["closure_proof",proof_bytes]])
    for kind,path,n in references: contributions[kind].append([path,n])
    totals={k:sum(n for _,n in rows) for k,rows in contributions.items()}
    totals.update(sums); totals["shared"]=totals["sources"]+sum(sums.values())
    totals["total"]=record_bytes+sum(n for _,_,n in references)+4096+report_bytes+proof_bytes
    violations=[k.upper()+"_LIMIT" for k,n in totals.items() if n>LIMITS[k]]
    return dict(record_bytes=record_bytes,contributions=contributions,items=items,totals=totals,
                remaining={k:LIMITS[k]-n for k,n in totals.items()},violations=violations)


def enforce(value):
    if value["violations"]: raise S2OBError("ENVELOPE_LIMIT",value)
    return value


def qualified_references(inventory):
    pr=json.loads((QUAL_DIR/"preregistration.json").read_bytes())
    q=json.loads((QUAL_DIR/"result.json").read_bytes()); check_root(q,"result_digest")
    inv=(QUAL_DIR/"code-inventory.json").read_bytes()
    require(q["status"]=="QUALIFIED" and q["test_calls"]==1 and q["hashes_unchanged"] is True
        and pr["code_digest"]==digest(inventory)==digest(json.loads(inv)), "QUALIFICATION_INVALID")
    for name in ("preregistration.json","stdout.txt","stderr.txt"):
        require(q["files"][name]==hashlib.sha256((QUAL_DIR/name).read_bytes()).hexdigest(), "QUALIFICATION_FILE_INVALID")
    refs=[]
    for name in ("code-inventory.json","preregistration.json","result.json","stdout.txt","stderr.txt"):
        path=QUAL_DIR/name
        refs.append(("sources" if name=="code-inventory.json" else "metadata",path.relative_to(ROOT).as_posix(),path.stat().st_size))
    require(sum(n for k,_,n in refs if k=="metadata")<=4096, "QUALIFICATION_LIMIT")
    # The files occupy the single already bound qualification reserve.
    return tuple(z for z in refs if z[0]=="sources")


def run_once(manifest, directory, *, mode="CALLER"):
    global MAIN_GATE
    require(MAIN_GATE and mode in ("CALLER","NEUTRAL"), "MAIN_GATE_CLOSED")
    out=Path(directory); c=m=None; phase="BINDINGS"; ordinal=None; refs=(); created=False
    try:
        require(not out.exists() and out.parent.is_dir(), "OUTPUT_EXISTS_OR_PARENT_MISSING")
        out.mkdir(); created=True
        expected=validate_manifest(manifest)
        inventory=code_inventory()
        require(manifest.code_digest==digest(inventory), "CODE_BINDING_INVALID")
        refs=qualified_references(inventory) if mode=="CALLER" else (
            ("sources",OWN[0]+":neutral-inventory",len(canonical(inventory))),)
        # Before opening input files, reserve the real manifest and dependency attachments.
        shell=dict(schema=SCHEMA,manifest=asdict(manifest),mode=mode,execution=None)
        enforce(balance(shell,refs))
        phase="RUNTIME_INIT"; c=CallerRuntime(manifest); m=Materializer(manifest)
        for event in manifest.events:
            ordinal=event.ordinal; phase="MATERIALIZATION"
            item=m.next(event)
            phase="EVENT"; c.process(item)
            del item
            if c.failed: break
        phase="CLOSE"; core=c.record()
        if not c.failed:
            require(m.counts==dict(payloads=expected["payloads"],audio=expected["audio"],nj=expected["nj"],
                visual=expected["visual"],materialized_events=expected["events"]), "COUNTS_INVALID")
        value=sealed(dict(schema=SCHEMA,mode=mode,run_id=manifest.run_id,manifest=asdict(manifest),
            code_digest=digest(inventory),references=refs,status=core["status"],counts=m.counts,
            execution=core,failure=None if not c.failed else core["failure"],evaluation=None,main_gate=False),"record_digest")
        phase="SERIALIZATION"; enforce(balance(value,refs))
        r.ng.ne.atomic_write(out/"record.json",value,LIMITS["total"])
        return value
    except Exception as exc:
        if not created or (out/"record.json").exists(): raise
        if phase=="MATERIALIZATION" and m is not None: phase=m.phase
        if c is not None and c.phase=="EVIDENCE": phase=c.phase
        failure_phase=phase
        final=None if c is None else c.close()
        failure=dict(phase=failure_phase,ordinal=ordinal,source_id=None if m is None else m.source_id,
            completed_events=0 if final is None else final["processed_event_count"],
            code=getattr(exc,"code","CALLER_TECHNICAL_ERROR"),error_class=type(exc).__name__,
            last_snapshot_digest=None if final is None else final["snapshot_digest"],final=final,
            balance=getattr(exc,"balance",None))
        value=sealed(dict(schema=SCHEMA,mode=mode,run_id=getattr(manifest,"run_id",None),
            manifest=asdict(manifest) if type(manifest) is Manifest else None,code_digest=getattr(manifest,"code_digest",None),
            references=refs,status="NOT_EVALUABLE",counts=None if m is None else m.counts,
            execution=None,failure=failure,evaluation=None,main_gate=False),"record_digest")
        r.ng.ne.atomic_write(out/"record.json",value,LIMITS["metadata"])
        return value
    finally:
        MAIN_GATE=False
        if c is not None and not c.closed: c.close()
