"""Single-instance OA connection. No source generation; main remains closed."""
from dataclasses import asdict, dataclass, fields
import json
from tools import _s2nn_private_half_runtime_binding as nn
from tools import _s2oa_private_administrative_binding as admin

ng, memory, half = nn.ng, nn.ng.memory, nn.half
digest, canonical = ng.digest, ng.canonical
MAIN_GATE = False
CLOCK = "s2oa-continuous-field-clock"
SCHEMA = "s2oa.single-runtime.v1"
QUAL_ID = "s2oa-single-runtime-qualification-20260910-01"
PHASES = ("BINDINGS","INITIAL","EVENT","EVIDENCE","CLOSE","SERIALIZATION")
WORK_LIMITS = dict(formation_checks=20,state_validation_passes=116,fast_rank_terms=20160,
                  ppb_selection_terms=30720,update_components=13440)


class S2OAError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2OAError(code)


def sealed(x, key="digest"):
    return {**x,key:digest(x)}


@dataclass(frozen=True,slots=True)
class Input:
    event: ng.stream.PerceptionStreamEvent336V1
    nj_json: str


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


def null_field(config):
    frames = []
    for modality,clock,end in (("auditory","audio.sample",4800),("visual","video.frame",1)):
        p = getattr(config.profile.profile,modality+"_config")
        frames.append(nn.ReceptorContactFrame(modality,p.geometry_id,"s2oa-zero-anatomy",clock,0,end,p.carrier_ids,(0.0,)*len(p.carrier_ids)))
    field = ng.field.build_shared_mcm_field(tuple(frames),ng.field.field_path.s2jt_default_dock_anatomies(),
                                           sample_offsets=ng.field.ORTHOGONAL_FIELD_SAMPLE_OFFSETS)
    return ng.field._field_state(field,0,0)


def slots(state):
    return tuple((k,x) for k,bank in enumerate((state.b4_state.entries,state.tspm_state.fast_state.slots,
        state.tspm_state.auditory_ppb1_state.slots,state.tspm_state.visual_ppb1_state.slots)) for x in bank)


def generation_step(pre,post,prior,event,transaction,chain):
    births, actions = [],[]
    for i,((bank,a),(_,z)) in enumerate(zip(slots(pre),slots(post),strict=True)):
        birth = prior[i]
        if not z.occupied:
            action,birth = ("CLEARED" if a.occupied else "FREE"),None
        elif a == z:
            action = "UNCHANGED"
        elif bank == 0 or z.support_count == 1:
            expired = bank == 1 and a.occupied and post.generation-a.last_selected_step >= 8
            action = "CREATED" if not a.occupied or expired else "REPLACED"
            birth = event.ordinal
        else:
            action = "MATCHED"
        require(not z.occupied or birth is not None,"GENERATION_MISSING")
        births.append(birth); actions.append(action)
    row = dict(event=event.ordinal,previous=chain,transaction=transaction,births=births,actions=actions)
    return sealed(row,"chain_digest")


def formation_context(config,pre,post,bound,event,run_id,result_digest):
    return [config.config_digest,pre.state_digest,post.state_digest,memory._b4_digest(post.b4_state),
        post.tspm_state.composite_state_digest,bound.input_digest,event.event_id+"-owner",run_id,event.event_id+"-consume",
        config.profile.binding_digest,config.ledger_limits.limits_digest,memory.S2JW_COORDINATOR_SCHEMA,
        "s2jw.profiled-memory-ledger.v1",result_digest]


def pack_formation(result,prior,context):
    def row(obj):
        return [["ref",context.index(x)] if x in context else x for x in asdict(obj).values()]
    value = dict(schema="s2oa.formation-positional.v1",receipt=row(result.receipt),ledger=row(result.ledger),
                 owner_before=row(prior),owner_after=row(result.owner_poststate),result_digest=result.result_digest)
    require(len(canonical(value))<=1536,"FORMATION_ITEM_LIMIT")
    return value


def unpack_formation(value,context):
    def row(key,cls):
        xs = value[key]
        require(len(xs)==len(fields(cls)),"FORMATION_FORM_INVALID")
        out=[]
        for x in xs:
            if isinstance(x,list):
                require(len(x)==2 and x[0]=="ref" and type(x[1]) is int and 0<=x[1]<len(context),"FORMATION_REF_INVALID")
                x=context[x[1]]
            out.append(x)
        return dict(zip((f.name for f in fields(cls)),out,strict=True))
    from tools._s2jw_profiled_memory_ledger import S2JVResourceLedgerV1
    require(value["schema"]=="s2oa.formation-positional.v1","FORMATION_SCHEMA_INVALID")
    return dict(receipt=row("receipt",memory.S2JVFormationReceiptV1),ledger=row("ledger",S2JVResourceLedgerV1),
        owner_poststate=row("owner_after",memory.S2JVFormationOwnerSnapshotV1),result_digest=value["result_digest"],
        schema=memory.S2JW_COORDINATOR_SCHEMA),row("owner_before",memory.S2JVFormationOwnerSnapshotV1)


class MemoryBranch:
    def __init__(self,config,run_id,state):
        self.config,self.run_id,self.state=config,run_id,state
        self.last=None
    def __call__(self,state,event):
        require(state is self.state,"MEMORY_OWNER_INVALID")
        bound = memory.bind_s2jv_coordinator_input(config=self.config,source=event.operation_payload)
        owner = memory.S2JVFormationOwner(event.event_id+"-owner",self.run_id,event.event_id+"-consume",
                                        self.config.config_digest,state.state_digest,bound.input_digest)
        prior=owner.snapshot()
        result=memory.advance_s2jv_atomic(config=self.config,prestate=state,source=bound,owner=owner)
        self.last=(bound,prior,result)
        self.state=result.poststate
        return ng.stream.StreamBranchResultV1("MEMORY",event.operation_projection_digest,state.state_digest,
                                             result.poststate,result.poststate.state_digest,result.receipt.receipt_digest)


class SingleRuntime:
    def __init__(self,inputs,run_id,*,mode="NEUTRAL"):
        require(mode=="NEUTRAL","MAIN_GATE_CLOSED")
        require(type(inputs) is tuple and 0<len(inputs)<=21 and all(type(x) is Input for x in inputs),"INPUTS_INVALID")
        require([x.event.ordinal for x in inputs]==list(range(1,len(inputs)+1)),"EVENT_ORDER_INVALID")
        kinds=[x.event.event_type for x in inputs]
        require(kinds.count("COMPLETE_AV_PERCEPTION")<=16 and kinds.count("PARTIAL_AUDITORY_CUE")<=2
                and kinds.count("PARTIAL_VISUAL_CUE")<=6,"NEUTRAL_LIMIT")
        self.config=nn.profile.build_config(); self.inputs=inputs; self.run_id=run_id
        self.packed=[ng.pack_input(x.event,self.config) for x in inputs]
        self.source=[json.loads(x.nj_json) for x in inputs]
        self.binding=ng.build_binding(self.config,"ALL_BANDS_24")
        fs=null_field(self.config); ms=memory.initial_s2jv_composite_state(self.config)
        self.fb=ng.ObservedBranch(ng.field.build_s2lo_field_adapter(CLOCK),fs)
        self.mb=MemoryBranch(self.config,run_id,ms); self.scans={}
        processor=ng.stream.RoleFreePerceptionStreamProcessor(field_adapter=self.fb,memory_adapter=self.mb,
            auditory_scan=ng.AudioAdapter(self.binding,self.config,False,self.scans),
            auditory_baseline=ng.AudioAdapter(self.binding,self.config,True,self.scans),
            visual_scan=ng.VisualAdapter(self.config,False,self.scans),visual_baseline=ng.VisualAdapter(self.config,True,self.scans))
        rc=ng.runtime.build_minimal_runtime_config(runtime_id=run_id,max_event_count=len(inputs),
            source_binding_digest=digest(self.packed),component_binding_digest=self.binding.binding_digest)
        initial=ng.stream.initial_perception_stream_state(stream_id=run_id,field_state=fs,field_state_digest=fs.state_digest,
            memory_state=ms,memory_state_digest=ms.state_digest)
        self.subject=ng.runtime.MinimalMCMRuntime336(config=rc,processor=processor,initial_state=initial)
        self.rc=asdict(rc); self.rows=[]; self.states={ms.state_digest:asdict(ms)}
        self.initial=dict(snapshot=asdict(self.subject.snapshot()),field=ng.field_record(fs),memory=ms.state_digest)
        self.births=[None]*24; self.chain=digest(dict(initial=ms.state_digest,config=self.config.config_digest))
        self.failed=False; self.phase="INITIAL"; self.failure=None; self.closed=False

    def process_next(self):
        require(not self.closed and not self.failed and len(self.rows)<len(self.inputs),"LIFECYCLE_INVALID")
        i=len(self.rows); event=self.inputs[i].event
        self.phase="EVENT"; pre=self.mb.state; snapshot=asdict(self.subject.snapshot()); self.mb.last=None
        step=self.subject.process_once(event)
        post=self.mb.state
        self.phase="EVIDENCE"
        form=gen=None
        if self.mb.last is not None:
            bound,prior,result=self.mb.last
            context=formation_context(self.config,pre,post,bound,event,self.run_id,result.result_digest)
            form=pack_formation(result,prior,context)
            # Exact round-trip of observed receipts, not newly synthesized owner evidence.
            restored,owner=unpack_formation(form,context)
            require(canonical(restored)==canonical({k:v for k,v in asdict(result).items() if k!="poststate"})
                    and canonical(owner)==canonical(asdict(prior)),"FORMATION_COMPACTION_INVALID")
            gen=generation_step(pre,post,self.births,event,result.result_digest,self.chain)
            require(len(canonical(gen))<=1536,"GENERATION_ITEM_LIMIT")
            self.births,self.chain=gen["births"],gen["chain_digest"]
        else:
            require(pre.state_digest==post.state_digest,"UNRECEIPTED_MEMORY_CHANGE")
        self.states[post.state_digest]=asdict(post)
        row=dict(pre=snapshot,step=asdict(step),post=asdict(self.subject.snapshot()),field=ng.field_record(self.fb.state),
                 memory=post.state_digest,formation=form,generations=gen,current_births=list(self.births),chain_digest=self.chain)
        self.rows.append(row)
        self.failed=bool(step.error_codes)
        if self.failed:
            self.failure=dict(phase="EVENT",ordinal=event.ordinal,completed_events=len(self.rows),
                              code="BRANCH_FAILURE",errors=list(step.error_codes),last_snapshot_digest=row["post"]["snapshot_digest"])
        return row

    def finish(self):
        require(not self.closed,"LIFECYCLE_INVALID")
        require(self.failed or len(self.rows)==len(self.inputs),"INCOMPLETE")
        self.phase="CLOSE"
        final=asdict(self.subject.close()); self.closed=True
        prior=self.rows[-1]["post"] if self.rows else self.initial["snapshot"]
        require(final["memory_state_digest"]==prior["memory_state_digest"] and final["field_state_digest"]==prior["field_state_digest"],"CLOSE_MUTATED")
        r=sealed(dict(schema=SCHEMA,status="NOT_EVALUABLE" if self.failed else "RECORDING_COMPLETE",run_id=self.run_id,
            config_digest=self.config.config_digest,runtime_config=self.rc,binding=asdict(self.binding),initial=self.initial,final=final,
            inputs=self.packed,source_receipts=self.source,rows=self.rows,states=self.states,
            scans=[dict(ordinal=n,role=role,value=asdict(x)) for (n,role),x in sorted(self.scans.items())],
            failure=self.failure,main_gate=False),"record_digest")
        self.phase="SERIALIZATION"; size_check(r)
        return r


def execute(inputs,run_id):
    c=None
    try:
        c=SingleRuntime(inputs,run_id)
        for _ in inputs:
            c.process_next()
            if c.failed: break
        return c.finish()
    except Exception as exc:
        final=None
        if c is not None and c.subject.snapshot().status=="OPEN":
            final=asdict(c.subject.close()); c.closed=True
        return sealed(dict(schema=SCHEMA,status="NOT_EVALUABLE",run_id=run_id,record=None,final=final,main_gate=False,
            failure=dict(phase="BINDINGS" if c is None else c.phase,ordinal=None if c is None else len(c.rows)+1,
                         completed_events=0 if c is None else len(c.rows),code=getattr(exc,"code","OA_TECHNICAL_ERROR"),
                         error_class=type(exc).__name__)),"record_digest")


def size_check(r):
    size=lambda x:len(canonical(x))
    require(len(r["states"])<=21 and all(size(s)<=98304 for s in r["states"].values()),"STATE_LIMIT")
    require(len(r["inputs"])<=28 and all(size(s)<=16384 for s in r["inputs"]),"INPUT_LIMIT")
    require(len(r["scans"])<=16 and all(size(s)<32768 for s in r["scans"]),"SCAN_LIMIT")
    forms=[x["formation"] for x in r["rows"] if x["formation"] is not None]
    gens=[x["generations"] for x in r["rows"] if x["generations"] is not None]
    nj=[x for x in r["source_receipts"] if x["nj"] is not None]
    for category,xs in (("nj",nj),("formations",forms),("generations",gens)):
        admin.reserve_items(category,[size(x) for x in xs])
    steps=[{k:v for k,v in row.items() if k not in ("formation","generations")} for row in r["rows"]]
    require(all(size(x)<=16384 for x in steps),"STEP_LIMIT")
    data=sum(size(x) for x in [*r["states"].values(),*r["inputs"],*r["scans"],*steps,*forms,*gens,*nj])
    metadata=size(r)-data
    # Previously consumed references stay charged without reloading OA source files.
    ledger=admin.ledger({"administrative":25438,"runtime":metadata},{"historical":162321},
        {"nj":sum(map(size,nj)),"formations":sum(map(size,forms)),"generations":sum(map(size,gens))},
        other_total=data-sum(map(size,[*forms,*gens,*nj])))
    require(size(r)+25438+162321<=4194304,"TOTAL_LIMIT")
    return dict(record_bytes=size(r),metadata_runtime_bytes=metadata,
        nj_sizes=list(map(size,nj)),formation_sizes=list(map(size,forms)),generation_sizes=list(map(size,gens)),ledger=ledger)


def generation_identity(record,event_index,slot_index):
    row=record["rows"][event_index]
    birth=row["current_births"][slot_index]
    if birth is None: return None
    e=record["inputs"][birth-1]["event"]
    origin=record["rows"][birth-1]
    require(origin["formation"] is not None,"GENERATION_ORIGIN_INVALID")
    return digest(dict(config=record["config_digest"],slot=slot_index,event=e["event_digest"],
        prestate=origin["pre"]["memory_state_digest"],poststate=origin["memory"],transaction=origin["formation"]["result_digest"]))


def current_evidence(record,historical_index,current_index,slot_index):
    return (record["rows"][historical_index]["memory"]==record["rows"][current_index]["memory"]
            and generation_identity(record,historical_index,slot_index) is not None
            and generation_identity(record,historical_index,slot_index)==generation_identity(record,current_index,slot_index))
