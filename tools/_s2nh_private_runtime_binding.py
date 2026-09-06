"""Bound NH sources -> immutable inputs -> unchanged NG runtime composition."""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import CommonFieldTime, from_auditory_receptor_state, from_visual_receptor_state
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2nh_private_source_binding as source
from tools import _s2ng_private_runtime_comparison as ng

ROOT = source.ROOT
SEAL_DIR = "reports/s2nh/s2nh-source-preseal-20260906-01"
QUAL_ID = "s2nh-runtime-binding-qualification-20260906-01"
FIELD_CLOCK = "s2nh-transfer-field-clock"
EXECUTION_DIGEST = "47ac97a175e37d45f576479ba82c906e4b36c47ae3708fca7d8e6ced885298a4"
EVALUATION_DIGEST = "03bb9a881d5f03935104788f2a98083d2790c8dc0565c5a9664c5d5ba13e8cb2"
PINS = {"execution-plan.json":"776ddf73bcbd9f61ad64612bc7bfb0ddeaebb6c233026e9831a2bfdd5a607826",
        "evaluation-plan.json":"a2b07880702f33bbff6129fdfe11b96897503cef52f7e46f0c9d52b415c9a531",
        "seal.json":"65bb79bc8c0e65b433a1a9f5bb84969970e440a51745a85af8883e1dc99838bd"}
OWN = ("tools/_s2nh_private_runtime_binding.py", "tools/_s2nh_private_runtime_verification.py",
       "tests/test_s2nh_private_runtime_binding.py", "reports/s2nh/qualify_runtime_once.py",
       "reports/s2nh/RUNTIME_ANBINDUNG.md")
MAIN_GATE = False
_MAIN_USED = False
MAX_ENVELOPE_BYTES = 32768
digest, canonical = source.digest, source.canonical


class S2NHRuntimeError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NHRuntimeError(code)


def check_digest(value, key):
    require(type(value) is dict and value.get(key) == digest({k:v for k,v in value.items() if k != key}), "DIGEST_INVALID")


def watched():
    return {**source.watched(), **{p:source.filehash(ROOT/p) for p in OWN},
            **{SEAL_DIR+"/"+p:source.filehash(ROOT/SEAL_DIR/p) for p in PINS}}


@dataclass(frozen=True, slots=True)
class BoundExecution:
    mode: str
    canonical_json: str

    def payload(self):
        return json.loads(self.canonical_json)

    def __post_init__(self):
        require(self.mode in ("MAIN","NEUTRAL") and type(self.canonical_json) is str
                and canonical(self.payload()).decode("ascii") == self.canonical_json, "EXECUTION_FORM_INVALID")
        x = self.payload()
        check_digest(x,"execution_digest")
        require(type(x["events"]) is list and 0 < len(x["events"]) <= (28 if self.mode=="MAIN" else 6), "EVENT_LIMIT_INVALID")
        if self.mode == "MAIN":
            require(x["execution_digest"] == EXECUTION_DIGEST and x["events"] == source.events(), "NH_PLAN_INVALID")
        else:
            require(x["execution_digest"] != EXECUTION_DIGEST
                and all(s["recipe"]["seed"].startswith("neutral-") for s in x["sources"]), "NEUTRAL_SOURCE_REQUIRED")
            require(sum(e["event_type"]==source.AV for e in x["events"])<=2,"NEUTRAL_FORMATION_LIMIT")
        validate_events(x)


def validate_events(x):
    lookup = {s["source_id"]:s for s in x["sources"]}
    require(len(lookup)==len(x["sources"]),"SOURCE_DUPLICATED")
    for s in lookup.values():
        check_digest(s,"source_digest")
        spec=source.SourceSpec(s["source_id"],s["kind"],canonical(s["recipe"]).decode("ascii"))
        require(s==source.bind_source(spec,s["payload_sha256"],s["byte_count"]),"SOURCE_BINDING_INVALID")
    audio_count=0
    for k,e in enumerate(x["events"],1):
        kind=e["event_type"]
        require(kind in (source.AV,source.A,source.V) and e["ordinal"]==k
                and e["common_end_tick"]==k*100000000 and e["field_clock_id"]==FIELD_CLOCK,"EVENT_TIME_INVALID")
        for modality,present in (("auditory",kind!=source.V),("visual",kind!=source.A)):
            part=e[modality]
            require((part is not None)==present,"MODALITY_PRESENCE_INVALID")
            if not present:
                continue
            s=lookup.get(part["source_id"])
            require(s is not None,"SOURCE_ABSENT")
            if modality=="auditory":
                require(s["kind"]=="PCM" and part["clock_id"]=="audio.sample"
                    and (part["start_tick"],part["end_tick"],part["hop_start"],part["hop_end"],part["endpoint_snapshot_index"])
                    == (audio_count*4800,(audio_count+1)*4800,audio_count*10,(audio_count+1)*10,audio_count*10)
                    and part["common_window"]==[k*100000000-10000000,k*100000000],"AUDIO_TIME_INVALID")
                audio_count+=1
            else:
                frame=3*k-1
                require(s["kind"]==("RGB_CUE" if kind==source.V else "RGB")
                    and s["recipe"]["partial"] is (kind==source.V)
                    and part["clock_id"]=="video.frame" and (part["start_tick"],part["end_tick"])==(frame,frame+1)
                    and part["common_window"]==[frame*1000000000//30,k*100000000],"VISUAL_TIME_INVALID")
    require(audio_count<=24 and sum(e["visual"] is not None for e in x["events"])<=24,"MATERIALIZATION_LIMIT")


def load_execution():
    require(all(source.filehash(ROOT/SEAL_DIR/p)==h for p,h in PINS.items()),"PRESEAL_CHANGED")
    x=json.loads((ROOT/SEAL_DIR/"execution-plan.json").read_bytes())
    require(x["source_hashes"]==source.watched() and x["generator_identity"]==source.identity(),"GENERATOR_OR_SOURCE_CHANGED")
    return BoundExecution("MAIN",canonical(x).decode("ascii"))


def load_evaluation():
    require(source.filehash(ROOT/SEAL_DIR/"evaluation-plan.json")==PINS["evaluation-plan.json"],"EVALUATION_FILE_CHANGED")
    y=json.loads((ROOT/SEAL_DIR/"evaluation-plan.json").read_bytes())
    check_digest(y,"evaluation_digest")
    require(y["evaluation_digest"]==EVALUATION_DIGEST and y["execution_digest"]==EXECUTION_DIGEST,"EVALUATION_BINDING_INVALID")
    return y


@dataclass(frozen=True, slots=True)
class MaterializedInputs:
    events: tuple
    receipts_json: str
    metrics_json: str
    execution_digest: str


class Materializer:
    def __init__(self, bound, config):
        require(type(bound) is BoundExecution,"BOUND_EXECUTION_REQUIRED")
        require(bound.mode!="MAIN" or MAIN_GATE,"MAIN_GATE_CLOSED")
        self.bound,self.config=bound,config
        self.execution=bound.payload()
        require(self.execution["profile"]["coordinator_config_digest"]==config.config_digest,"CONFIG_INVALID")
        self.used=False
        self.phase,self.ordinal,self.source_id="INITIAL",None,None
        self.metrics=dict(audio_windows=0,visual_frames=0,audio_hops=0,audio_snapshots=0,completed_events=0)

    def run_once(self):
        require(not self.used,"MATERIALIZATION_ALREADY_USED")
        self.used=True
        hearing=BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        visual=LocalChannelGridReceptor(VisualGridConfig())
        band=ng.audio.kz.build_auditory_band_plan_48()
        sources={s["source_id"]:s for s in self.execution["sources"]}
        events,receipts=[],[]
        for e in self.execution["events"]:
            self.ordinal=e["ordinal"]
            frames=[]
            base=dict(execution_digest=self.execution["execution_digest"],spec_digest=digest(e),
                      source_occurrence_id=e["source_occurrence_id"],auditory=None,visual=None)
            for modality in ("auditory","visual"):
                part=e[modality]
                if part is None:
                    continue
                s=sources[part["source_id"]]
                self.source_id=s["source_id"]
                self.phase="PAYLOAD_GENERATION"
                payload=source.pcm_payload(s["recipe"]) if modality=="auditory" else source.rgb_payload(s["recipe"])
                try:
                    self.phase="PAYLOAD_HASH"
                    view=memoryview(payload).cast("B")
                    try:
                        require(view.nbytes==s["byte_count"] and hashlib.sha256(view).hexdigest()==s["payload_sha256"],"PAYLOAD_HASH_INVALID")
                    finally:
                        view.release()
                        del view
                    self.phase="RECEPTOR_ANALYSIS"
                    if modality=="auditory":
                        require(self.metrics["audio_windows"]<24,"AUDIO_WINDOW_LIMIT")
                        samples=np.frombuffer(payload,dtype="<f4")
                        try:
                            state=None
                            for hop in range(10):
                                state=hearing.push(tuple(float(v) for v in samples[hop*480:(hop+1)*480]))
                                self.metrics["audio_hops"]+=1
                        finally:
                            del samples
                        self.metrics["audio_windows"]+=1
                        self.metrics["audio_snapshots"]=hearing.snapshot_count
                        require(state is not None and state.snapshot_index==part["endpoint_snapshot_index"],"AUDIO_ENDPOINT_INVALID")
                        frame=from_auditory_receptor_state(state)
                    else:
                        require(self.metrics["visual_frames"]<24,"VISUAL_FRAME_LIMIT")
                        state=visual.analyze(payload,frame_index=part["start_tick"])
                        self.metrics["visual_frames"]+=1
                        frame=from_visual_receptor_state(state)
                finally:
                    del payload
                self.phase="RECEPTOR_BINDING"
                require((frame.clock_id,frame.window_start_tick,frame.window_end_tick)==
                    (part["clock_id"],part["start_tick"],part["end_tick"]),"NATIVE_TIME_INVALID")
                require(all(np.isfinite(v) and 0<=v<=1 for v in frame.values),"RECEPTOR_NORMALFORM_INVALID")
                frames.append(OrganismTimedReceptorFrame(frame,CommonFieldTime(FIELD_CLOCK,*part["common_window"])))
                base[modality]=dict(source_id=s["source_id"],payload_sha256=s["payload_sha256"],
                    receptor_state_digest=state.digest(),values_digest=digest(list(frame.values)))
            self.phase="EVENT_BINDING"
            bymod={f.frame.modality_id:f for f in frames}
            source_digest=digest(base)
            kind=e["event_type"]
            if kind==source.AV:
                plan=ng.pairing.build_s2jv_pairing_plan(pair_id=f"s2nh-pair-{self.ordinal:03d}",
                    source_contract_id="s2nh-presealed-source-v1",profile=self.config.profile,
                    auditory=bymod["auditory"],visual=bymod["visual"],
                    auditory_payload_digest=base["auditory"]["payload_sha256"],visual_payload_digest=base["visual"]["payload_sha256"])
                operation=ng.pairing.bind_s2jv_default_live_pair(pairing_plan=plan,profile=self.config.profile,
                    auditory=bymod["auditory"],visual=bymod["visual"])
                perception=operation.pairing_digest
            elif kind==source.A:
                f=bymod["auditory"].frame
                cue=ng.audio.kz.build_masked_auditory_cue_48(pcm_payload_digest=base["auditory"]["payload_sha256"],
                    receptor_state_digest=base["auditory"]["receptor_state_digest"],receptor_values_digest=digest(list(f.values)),
                    config_digest=self.config.config_digest,auditory_source_clock_id=f.clock_id,
                    auditory_window_start_tick=f.window_start_tick,auditory_window_end_tick=f.window_end_tick,
                    observed_values=tuple(f.values[i] for i in range(24)),band_plan=band)
                operation=ng.stream.AuditoryCueOperationV1(cue,band)
                perception=cue.cue_digest
            else:
                t=bymod["visual"]
                operation=ng.visual.build_masked_memory_cue_336(source_digest=source_digest,config_digest=self.config.config_digest,
                    field_clock_id=FIELD_CLOCK,window_start_tick=t.field_time.window_start_tick,window_end_tick=t.field_time.window_end_tick,
                    visual_source_clock_id=t.frame.clock_id,visual_window_start_tick=t.frame.window_start_tick,
                    visual_window_end_tick=t.frame.window_end_tick,values=tuple(v if i<32 else None for i,v in enumerate(t.frame.values)))
                perception=operation.cue_digest
            field=ng.field.S2LOFieldInputV1(perception,(self.ordinal-1)*100000000,self.ordinal*100000000,tuple(frames))
            event=ng.stream.build_perception_stream_event(event_id=f"s2nh-event-{e['event_id']}",ordinal=self.ordinal,event_type=kind,
                source_digest=source_digest,perception_digest=perception,field_projection_digest=perception,
                operation_projection_digest=perception,field_payload=field,operation_payload=operation)
            ng.pack_input(event,self.config)
            events.append(event)
            receipts.append(source.sealed(dict(base=base,source_digest=source_digest,event_digest=event.event_digest),"receipt_digest"))
            self.metrics["completed_events"]+=1
        self.phase,self.source_id="COMPLETE",None
        return MaterializedInputs(tuple(events),canonical(receipts).decode("ascii"),canonical(self.metrics).decode("ascii"),self.execution["execution_digest"])


def compose(materialized, config, comparison_id, mode):
    require(type(materialized) is MaterializedInputs and mode in ("NEUTRAL","MAIN"),"MATERIALIZED_INPUT_INVALID")
    require(mode!="MAIN" or MAIN_GATE,"MAIN_GATE_CLOSED")
    # MAIN gate is enabled by the bounded caller, never through source-file edits.
    composition=ng.RuntimeComparison.__new__(ng.RuntimeComparison)
    try:
        composition.__init__(config=config,events=materialized.events,field_clock_id=FIELD_CLOCK,
                             comparison_id=comparison_id,mode=mode)
        for _ in materialized.events:
            composition.process_next()
            if composition.failed:
                break
        return composition.finish()
    finally:
        for subject in getattr(composition,"subjects",()):
            if subject.snapshot().status=="OPEN":
                subject.close()


def envelope(run_id, bound, materialized, comparison, failure=None, binding_digest=None, materialization_calls=1):
    payload=dict(schema="s2nh.runtime-record.v1",run_id=run_id,execution_digest=bound.payload()["execution_digest"],
        status="RECORDING_COMPLETE" if comparison is not None and comparison["status"]=="RECORDING_COMPLETE" and failure is None else "NOT_EVALUABLE",
        comparison=comparison,source_receipts=[] if materialized is None else json.loads(materialized.receipts_json),
        materialization=None if materialized is None else json.loads(materialized.metrics_json),failure=failure,
        main_gate_after=False,materialization_calls=materialization_calls,binding_digest=binding_digest)
    result=source.sealed(payload,"record_digest")
    if len(canonical(result))>ng.MAX_BYTES or len(canonical({**result,"comparison":None}))>MAX_ENVELOPE_BYTES:
        payload.update(status="NOT_EVALUABLE",comparison=None,source_receipts=[],failure=dict(phase="SERIALIZATION",ordinal=None,
            source_id=None,code="RECORD_SIZE_EXCEEDED",error_class="S2NHRuntimeError"))
        result=source.sealed(payload,"record_digest")
    return result


def _run_main_once(run_id, output):
    global _MAIN_USED, MAIN_GATE
    require(MAIN_GATE and not _MAIN_USED and not ng.MAIN_GATE,"MAIN_GATE_CLOSED_OR_USED")
    require(re.fullmatch(r"s2nh-runtime-comparison-[0-9]{8}-[0-9]{2}",run_id)
            and Path(output).resolve()==(ROOT/"reports/s2nh"/run_id).resolve(),"RUN_DESTINATION_INVALID")
    _MAIN_USED=True
    output=Path(output)
    bound=materialized=comparison=materializer=None
    failure=None
    before=None
    created=False
    phase="BINDINGS"
    try:
        output.mkdir(exist_ok=False)
        created=True
        before=watched()
        q=json.loads((ROOT/"reports/s2nh"/QUAL_ID/"result.json").read_bytes())
        require(q["status"]=="S2NH_RUNTIME_BINDING_QUALIFIED" and q["hashes_after"]==before,"QUALIFICATION_REQUIRED")
        bound=load_execution()
        config=ng.ne.make_config()
        ng.ne.atomic_write(output/"preregistration.json",dict(run_id=run_id,hashes=before,execution_digest=EXECUTION_DIGEST,
            main_calls=1,materialization_calls=1,retry=False,limits=ng.budget(tuple(e["event_type"] for e in bound.payload()["events"]))))
        phase="MATERIALIZATION"
        materializer=Materializer(bound,config)
        materialized=materializer.run_once()
        phase="RUNTIME"
        ng.MAIN_GATE=True
        comparison=compose(materialized,config,run_id,"MAIN")
        require(before==watched(),"SOURCE_CHANGED")
    except Exception as error:
        failure=dict(phase=materializer.phase if phase=="MATERIALIZATION" and materializer else phase,
            ordinal=materializer.ordinal if materializer else None,source_id=materializer.source_id if materializer else None,
            metrics=None if materializer is None else dict(materializer.metrics),error_class=type(error).__name__,code=getattr(error,"code","NH_TECHNICAL_ERROR"))
    finally:
        MAIN_GATE=False
        ng.MAIN_GATE=False
    require(created,"OUTPUT_ALREADY_EXISTS_OR_UNAVAILABLE")
    if bound is None:
        result=source.sealed(dict(schema="s2nh.runtime-record.v1",run_id=run_id,status="NOT_EVALUABLE",execution_digest=EXECUTION_DIGEST,
            comparison=None,source_receipts=[],materialization=None,failure=failure,main_gate_after=False,materialization_calls=0),"record_digest")
    else:
        result=envelope(run_id,bound,materialized,comparison,failure,
            None if before is None else digest(before),int(materializer is not None and materializer.used))
    ng.ne.atomic_write(output/"recording.json",result)
    return result


def run_main_once(run_id, output):
    global MAIN_GATE
    try:
        return _run_main_once(run_id,output)
    finally:
        MAIN_GATE=False
        ng.MAIN_GATE=False
