"""Closed NR connection v3; the source seal is immutable and separately bound."""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from tools import _s2nr_private_source_binding as source
from tools import _s2nr_private_runtime_binding as runtime
from tools import _s2no_private_half_materialization as receptors

nn, ng = runtime.nn, runtime.ng
ROOT = source.ROOT
canonical, digest, sealed = source.canonical, source.digest, source.sealed
SCHEMA = "s2nr.closed-runtime-connection.v3"
MAIN_GATE = False
_MAIN_USED = False
RUN_ID = "s2nr-mask-runtime-transfer-20260908-01"
QUAL_ID = "s2nr-main-binding-qualification-20260908-01"
SEAL_DIR = "reports/s2nr/s2nr-source-preseal-20260908-01"
PINS = {
    "execution-plan.json":"097fbae1667ee47288aad0a27634e94da93f6caf0863a2b9bdf2bd4f9c19437a",
    "evaluation-plan.json":"819e6292d5d77f90de2572457e258d0ffd06ed0d49667c2f7ba5247768b7de87",
    "seal.json":"33087a1b0714a8c6dff847471f8d15cfc6935d590f87f13a4f511f663ea672c3",
    "verification.json":"e24233a82140eba02d2ab97bc87c1c4c740abb34d7462e40d54f2f7a5b6c495e"}
EXECUTION_DIGEST = "3471deefa0e1eda1f1b2b4b28a6100494bdc5bece758ab0a4a466d175704295a"
MR_PATH = "tools/_s2mr_private_minimal_mcm_runtime.py"
MR_CONNECTION_SHA = "e419d72ad5b5dd668eb36a90081f21a2902ad900c166289a2e9de79db56e618d"
OWN = ("tools/_s2nr_private_run.py","tools/_s2nr_private_run_verification.py",
    "tools/_s2nr_private_evaluation.py","tests/test_s2nr_private_run.py",
    "reports/s2nr/qualify_main_once.py","reports/s2nr/MAIN_QUALIFIKATIONSBINDUNG.md")
PHASES = ("BINDINGS","INITIAL","PAYLOAD_GENERATION","PAYLOAD_HASH","RECEPTOR_ANALYSIS",
    "RECEPTOR_BINDING","NJ_CONTACT_BINDING","RUNTIME_INIT","EVENT_PROCESSING","RUNTIME_CLOSE","SERIALIZATION")
EXTRA_VERIFICATION_BUDGET = dict(parent_decodes=18,source_receipt_checks=18,modality_time_checks=32,
    projection_validation_passes=144,stored_projection_components=864,projection_component_visits=6912,raw_reconstruction_components=0,
    envelope_bytes=65536,total_envelope_bound=2665194+65536)


class S2NRRunError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NRRunError(code)


def check(p, key):
    require(type(p) is dict and p.get(key)==digest({k:v for k,v in p.items() if k!=key}),"DIGEST_INVALID")


def load_execution():
    require(all(source.filehash(ROOT/SEAL_DIR/p)==h for p,h in PINS.items()),"SEAL_CHANGED")
    p=json.loads((ROOT/SEAL_DIR/"execution-plan.json").read_bytes())
    check(p,"execution_digest")
    require(p["execution_digest"]==EXECUTION_DIGEST,"PLAN_CHANGED")
    # Exactly one historical path has a separately qualified type connection.
    expected={k:MR_CONNECTION_SHA if k==MR_PATH else v for k,v in p["source_hashes"].items()}
    require(MR_PATH in expected and all(source.filehash(ROOT/k)==v for k,v in expected.items()),"SOURCE_VERSION_CHANGED")
    _,_,gen=source.generators()
    require(gen==p["generators"] and source.environment()==p["environment"]
        and p["profiles"]==source.profiles(),"ENVIRONMENT_OR_PROFILE_CHANGED")
    return BoundExecution("MAIN",canonical(p).decode())


def watched():
    paths=set(OWN)|{p for p,_ in runtime.sources()}|{SEAL_DIR+"/"+p for p in PINS}
    p=json.loads((ROOT/SEAL_DIR/"execution-plan.json").read_bytes())
    paths.update(p["source_hashes"])
    return {p:source.filehash(ROOT/p) for p in sorted(paths)}


@dataclass(frozen=True,slots=True)
class BoundExecution:
    mode: str
    plan_json: str

    def __post_init__(self):
        p=self.payload()
        require(self.mode in ("MAIN","NEUTRAL") and canonical(p).decode()==self.plan_json,"PLAN_FORM_INVALID")
        check(p,"execution_digest")
        if self.mode=="MAIN":
            require(p["execution_digest"]==EXECUTION_DIGEST,"PLAN_CHANGED")
        else:
            require(0<len(p["events"])<=6 and all(x["source_id"].startswith("neutral-") for x in p["sources"]),"NEUTRAL_ONLY")
        require(len(canonical(p))<=65536 and len(p["sources"])<=17,"PLAN_SIZE_INVALID")
        catalog={r["source_id"]:r for r in p["sources"]}
        require(len(catalog)==len(p["sources"]),"DUPLICATE_SOURCE")
        for r in catalog.values():
            check(r,"source_digest")
            require(r["recipe_digest"]==digest(r["recipe"]) and runtime.s.hash_form(r["payload_sha256"]),"SOURCE_BINDING_INVALID")
        for n,e in enumerate(p["events"],1):
            end=n*100000000
            require(e["ordinal"]==n and e["event_type"] in (source.AV,source.A)
                and e["field_window"]==[(n-1)*100000000,end],"EVENT_TIME_INVALID")
            a,v=e["auditory"],e["visual"]
            require(catalog[a["source_id"]]["kind"]=="PCM" and a["clock_id"]=="audio.sample"
                and (a["start_tick"],a["end_tick"],a["endpoint_snapshot_index"],a["hop_start"],a["hop_end"])
                ==((n-1)*4800,n*4800,(n-1)*10,(n-1)*10,n*10)
                and a["common_window"]==[end-10000000,end],"AUDIO_TIME_INVALID")
            require((v is not None)==(e["event_type"]==source.AV),"EVENT_MODALITY_INVALID")
            if v is not None:
                require(catalog[v["source_id"]]["kind"]=="RGB" and v["clock_id"]=="video.frame"
                    and (v["start_tick"],v["end_tick"])==(3*n-1,3*n)
                    and v["common_window"]==[(3*n-1)*1000000000//30,end],"VIDEO_TIME_INVALID")
        require(len({e["field_clock_id"] for e in p["events"]})==1,"FIELD_CLOCK_INVALID")

    def payload(self):
        return json.loads(self.plan_json)


def metrics(n=0,visual=0):
    return dict(audio_windows=n,audio_hops=10*n,audio_snapshots=max(0,10*n-9),
        nj_projections=n,visual_frames=visual,completed_events=n)


class Materializer:
    def __init__(self,bound,config):
        require(type(bound) is BoundExecution and (bound.mode!="MAIN" or MAIN_GATE),"MAIN_GATE_CLOSED")
        nn.validate_config(config)
        self.bound,self.config=bound,config
        self.used=False
        self.phase,self.ordinal,self.source_id="INITIAL",None,None
        self.metrics=metrics()

    def run_once(self):
        require(not self.used and (self.bound.mode!="MAIN" or MAIN_GATE),"MATERIALIZATION_CLOSED")
        self.used=True
        p=self.bound.payload()
        pcm,rgb,_=source.generators()
        hearing=receptors.BroadbandHearingPath(receptors.LogSpectralReceptor(receptors.LogSpectralConfig()))
        vision=receptors.LocalChannelGridReceptor(receptors.VisualGridConfig())
        catalog={s["source_id"]:s for s in p["sources"]}
        inputs,receipts=[],[]
        for spec in p["events"]:
            self.ordinal=spec["ordinal"]
            raw=visual=None
            links={}
            for modality in ("auditory","visual"):
                part=spec[modality]
                if part is None:
                    links[modality]=None
                    continue
                row=catalog[part["source_id"]]
                self.source_id,self.phase=row["source_id"],"PAYLOAD_GENERATION"
                payload=(pcm if modality=="auditory" else rgb)(row["recipe"])
                try:
                    self.phase="PAYLOAD_HASH"
                    view=memoryview(payload).cast("B")
                    try:
                        require(view.nbytes==row["byte_count"] and hashlib.sha256(view).hexdigest()==row["payload_sha256"],"PAYLOAD_HASH_INVALID")
                    finally:
                        view.release()
                    self.phase="RECEPTOR_ANALYSIS"
                    if modality=="auditory":
                        samples=receptors.np.frombuffer(payload,dtype="<f4")
                        try:
                            for hop in range(10):
                                raw=hearing.push(tuple(float(x) for x in samples[480*hop:480*(hop+1)]))
                                self.metrics["audio_hops"]+=1
                                self.metrics["audio_snapshots"]=hearing.snapshot_count
                        finally:
                            del samples
                        self.metrics["audio_windows"]+=1
                        self.phase="RECEPTOR_BINDING"
                        require(raw is not None and (raw.snapshot_index,raw.window_start_sample,raw.window_end_sample)
                            ==(part["endpoint_snapshot_index"],part["start_tick"],part["end_tick"]),"AUDIO_ENDPOINT_INVALID")
                    else:
                        state=vision.analyze(payload,frame_index=part["start_tick"])
                        self.metrics["visual_frames"]+=1
                        visual=nn.OrganismTimedReceptorFrame(receptors.from_visual_receptor_state(state),
                            nn.CommonFieldTime(spec["field_clock_id"],*part["common_window"]))
                        del state
                finally:
                    del payload
                links[modality]=dict(source_id=row["source_id"],source_digest=row["source_digest"],payload_sha256=row["payload_sha256"])
            self.phase,self.source_id="NJ_CONTACT_BINDING",spec["auditory"]["source_id"]
            value=nn.bind_event(config=self.config,event_id="s2nr-event-"+spec["event_id"],ordinal=self.ordinal,
                event_type=spec["event_type"],field_start_tick=spec["field_window"][0],
                common_time=nn.CommonFieldTime(spec["field_clock_id"],*spec["auditory"]["common_window"]),
                raw_audio=raw,pcm_digest=links["auditory"]["payload_sha256"],visual=visual,
                rgb_digest=None if visual is None else links["visual"]["payload_sha256"],
                visual_time_binding=None if visual is None else visual.field_time)
            self.metrics["nj_projections"]+=1
            self.metrics["completed_events"]+=1
            inputs.append(value)
            receipts.append(sealed(dict(spec_digest=digest(spec),sources=links,parent_binding_digest=value.binding_digest,
                projection_digest=value.auditory_projection.projection_digest),"receipt_digest"))
            del raw,visual,value
        self.ordinal,self.source_id=None,None
        return tuple(inputs),receipts


def execute_once(bound,config,run_id,output):
    """Shared neutral/main path. Directory creation is the durable one-shot claim."""
    require(type(bound) is BoundExecution and (bound.mode!="MAIN" or MAIN_GATE),"MAIN_GATE_CLOSED")
    output=Path(output)
    output.mkdir(exist_ok=False)
    phase="BINDINGS"
    materializer=comparison=None
    receipt=[]
    record=failure=None
    hashes=watched()
    try:
        phase="INITIAL"
        materializer=Materializer(bound,config)
        inputs,receipt=materializer.run_once()
        phase="RUNTIME_INIT"
        comparison=runtime.MaskRuntimeComparison.__new__(runtime.MaskRuntimeComparison)
        comparison.__init__(inputs=inputs,config=config,comparison_id=run_id,
            field_clock_id=bound.payload()["events"][0]["field_clock_id"],mode=bound.mode)
        for n in range(len(inputs)):
            phase="EVENT_PROCESSING"
            comparison.process_next()
            if comparison.failed:
                break
        phase="RUNTIME_CLOSE"
        record=comparison.finish()
        phase="SERIALIZATION"
        require(hashes==watched(),"SOURCES_CHANGED")
    except Exception as exc:
        progress=len(getattr(comparison,"rows",()))
        snapshots=[asdict(v.snapshot()) for v in getattr(comparison,"subjects",())]
        failure=dict(phase=materializer.phase if phase=="INITIAL" and materializer else phase,
            ordinal=materializer.ordinal if phase=="INITIAL" and materializer else
                progress+1 if phase=="EVENT_PROCESSING" else None,
            source_id=materializer.source_id if phase=="INITIAL" and materializer else None,
            completed_runtime_events=progress,last_snapshot_digests=[v["snapshot_digest"] for v in snapshots],
            error_class=type(exc).__name__,code=exc.code if isinstance(exc,(S2NRRunError,runtime.s.S2NQError)) else "TECHNICAL_EXECUTION_ERROR")
    finally:
        for subject in getattr(comparison,"subjects",()):
            if subject.snapshot().status=="OPEN":
                subject.close()
    result=sealed(dict(schema=SCHEMA,run_id=run_id,mode=bound.mode,execution_digest=bound.payload()["execution_digest"],
        source_versions=hashes,config_digest=config.config_digest,profile_digest=nn.half.PROFILE_DIGEST,
        status="RECORDING_COMPLETE" if failure is None and record is not None and record["status"]=="RECORDING_COMPLETE" else "NOT_EVALUABLE",
        materialization=None if materializer is None else materializer.metrics,source_receipts=receipt,
        comparison=record if failure is None else None,failure=failure,main_gate_after=False),"record_digest")
    if len(canonical(result))>ng.MAX_BYTES or len(canonical({**result,"comparison":None}))>65536:
        result=sealed({**{k:v for k,v in result.items() if k!="record_digest"},"comparison":None,"source_receipts":[],
            "status":"NOT_EVALUABLE","failure":dict(phase="SERIALIZATION",ordinal=None,source_id=None,
                completed_runtime_events=len(getattr(comparison,"rows",())),
                last_snapshot_digests=[v.snapshot().snapshot_digest for v in getattr(comparison,"subjects",())],
                error_class="S2NRRunError",code="ENVELOPE_SIZE_EXCEEDED")},"record_digest")
        require(len(canonical(result))<=65536,"FAILURE_ENVELOPE_SIZE_EXCEEDED")
    ng.ne.atomic_write(output/"recording.json",result,limit=ng.MAX_BYTES)
    return result


def run_main_once(run_id,output):
    global MAIN_GATE,_MAIN_USED
    try:
        require(MAIN_GATE and not _MAIN_USED and not runtime.MAIN_GATE and not nn.MAIN_GATE and not ng.MAIN_GATE,"MAIN_GATE_CLOSED_OR_USED")
        require(run_id==RUN_ID and Path(output).resolve()==(ROOT/"reports/s2nr"/RUN_ID).resolve()
            and not Path(output).exists(),"RUN_DESTINATION_INVALID")
        _MAIN_USED=True
        try:
            qualification=json.loads((ROOT/"reports/s2nr"/QUAL_ID/"result.json").read_bytes())
            check(qualification,"result_digest")
            require(qualification["status"]=="S2NR_MAIN_BINDING_QUALIFIED" and qualification["hashes_after"]==watched()
                ==qualification["hashes_before"],"QUALIFICATION_REQUIRED")
            bound=load_execution()
        except Exception as exc:
            Path(output).mkdir(exist_ok=False)
            result=sealed(dict(schema=SCHEMA,run_id=run_id,mode="MAIN",execution_digest=EXECUTION_DIGEST,
                source_versions=watched(),config_digest=source.profiles()["coordinator_config_digest"],
                profile_digest=nn.half.PROFILE_DIGEST,status="NOT_EVALUABLE",materialization=None,
                source_receipts=[],comparison=None,main_gate_after=False,
                failure=dict(phase="BINDINGS",ordinal=None,source_id=None,completed_runtime_events=0,
                    last_snapshot_digests=[],error_class=type(exc).__name__,
                    code=exc.code if isinstance(exc,S2NRRunError) else "BINDING_EXECUTION_ERROR")),"record_digest")
            ng.ne.atomic_write(Path(output)/"recording.json",result)
            return result
        runtime.MAIN_GATE=True
        return execute_once(bound,nn.profile.build_config(),run_id,output)
    finally:
        MAIN_GATE=runtime.MAIN_GATE=False
