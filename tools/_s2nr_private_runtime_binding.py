"""Mask-only composition of qualified half inputs, MR/LM and NQ scans."""
from dataclasses import asdict, dataclass, replace
import hashlib
from tools import _s2nn_private_half_runtime_binding as nn
from tools import _s2nr_private_runtime_types as types
from tools import _s2nq_private_direct as direct

ng, s = nn.ng, types.scan
digest, canonical, require = s.digest, s.canonical, s.require
MAIN_GATE = False
SOURCE_PATHS = ("tools/_s2nr_private_runtime_types.py","tools/_s2nr_private_runtime_binding.py",
    "tools/_s2nr_private_runtime_verification.py","tools/_s2mr_private_minimal_mcm_runtime.py",
    "tools/_s2nq_private_mask_scan.py","tools/_s2nq_private_direct.py")


def sources():
    return tuple((p,hashlib.sha256((nn.ROOT/p).read_bytes()).hexdigest())
                 for p in dict.fromkeys((*ng.SOURCE_PATHS,*nn.SOURCE_PATHS,*SOURCE_PATHS)))


def binding(config, view):
    nn.validate_config(config)
    return ng.sealed(dict(schema=types.SCHEMA,view=view,band_plan=asdict(s.plan(view)),
        profile_digest=nn.half.PROFILE_DIGEST,config_digest=config.config_digest,
        a_rule="ALL_BANDS_24",a_threshold=0.1,slow_rule="historical sum/24",slow_threshold=0.01,
        sources=[list(p) for p in sources()]),"binding_digest")


def events_for(value, config):
    """Parent validated once; only its operation is specialized for each view."""
    nn.validate_input(value,config)
    e=value.event
    if e.event_type != "PARTIAL_AUDITORY_CUE":
        return (e,e)
    return tuple(replace(e,operation_payload=types.MaskedAudioOperationV2(
        s.bind_cue(value.auditory_projection,value.pcm_digest,config,view),e.perception_digest,e.source_digest))
        for view in s.VIEWS)


def pack_event(event,config,view):
    if event.event_type != "PARTIAL_AUDITORY_CUE":
        return ng.pack_input(event,config)
    require(type(event) is ng.stream.PerceptionStreamEvent336V1
        and event.event_digest == digest(event.payload_without_digest()),"EVENT_INVALID")
    op=event.operation_payload
    require(type(op) is types.MaskedAudioOperationV2 and type(op.cue) is s.Cue,"CUE_TYPE_INVALID")
    cue=op.cue
    cue.__post_init__()
    require(cue.band_plan == s.plan(view) and cue.config_digest == config.config_digest
        and op.source_digest == event.source_digest and op.perception_digest == event.perception_digest,
        "CUE_PARENT_INVALID")
    f=event.field_payload
    require(type(f) is ng.field.S2LOFieldInputV1 and type(f.timed_frames) is tuple and len(f.timed_frames)==1
        and f.perception_digest == event.perception_digest == event.field_projection_digest == event.operation_projection_digest,
        "FIELD_PARENT_INVALID")
    timed=f.timed_frames[0]
    ng.pairing._validate_timed_frame(timed,modality="auditory",profile=config.profile.profile)
    t=timed.frame
    require(f.start_tick <= timed.field_time.window_start_tick < timed.field_time.window_end_tick == f.end_tick
        and (cue.clock_id,cue.start,cue.end)==(t.clock_id,t.window_start_tick,t.window_end_tick)
        and cue.parent_values_digest == digest(list(t.values)) and t.snapshot_id == "half."+cue.parent_digest
        and cue.values == tuple(t.values[i] for i in cue.band_plan.observed),"CUE_SOURCE_INVALID")
    packed=asdict(f)
    del packed["timed_frames"][0]["frame"]["carrier_ids"]
    result=dict(event={**event.payload_without_digest(),"event_digest":event.event_digest},
        field=packed,operation=asdict(op))
    require(len(canonical(result))<=ng.MAX_INPUT_BYTES,"INPUT_SIZE_EXCEEDED")
    return result


def pack_input(value,config):
    events=events_for(value,config)
    left,right=(pack_event(e,config,v) for e,v in zip(events,s.VIEWS,strict=True))
    require(left["field"]==right["field"] and left["event"]==right["event"],"PARENT_DIFFERS")
    packed=dict(parent_binding_digest=value.binding_digest,source_digest=value.event.source_digest,
        pcm_digest=value.pcm_digest,rgb_digest=value.rgb_digest,
        projection=None if value.auditory_projection is None else asdict(value.auditory_projection),
        event=left["event"],field=left["field"],operations=[left["operation"],right["operation"]])
    require(len(canonical(packed))<=ng.MAX_INPUT_BYTES,"INPUT_SIZE_EXCEEDED")
    return packed


def limits(kinds):
    require(type(kinds) is tuple and 0<len(kinds)<=18 and all(k in ng.stream.EVENT_TYPES for k in kinds),"EVENT_LIMIT")
    f=kinds.count("COMPLETE_AV_PERCEPTION")
    a=kinds.count("PARTIAL_AUDITORY_CUE")
    v=kinds.count("PARTIAL_VISUAL_CUE")
    require(f<=14 and a<=4 and v<=1,"EVENT_LIMIT")
    return dict(events=len(kinds),formations=2*f,scans=4*(a+v),
        slot_visits=80*a+64*v,band_differences=1920*a,equality_comparisons=192*a,
        visual_comparisons=3200*v,field_contacts=2*(336*f+48*a+288*v),
        formation_l1=2*f*3552,verification_scan_calls=4*(a+v),
        verification_value_comparisons=2112*a+3200*v,
        verification_state_decodes=f+1,verification_formation_relations=2*f,
        verification_fast_terms=2*f*1008,verification_ppb_terms=2*f*1536,
        verification_update_components=2*f*672,
        input_pack_calls_max=4*len(kinds),hypothesis_validation_calls_max=16*(a+v),
        source_hash_checks_max=32*len(kinds)+32,
        max_record_bytes=ng.MAX_BYTES,max_metadata_bytes=ng.MAX_METADATA_BYTES,
        # Include enclosing maps, source projections and both operation forms.
        serialization_bound=15*(ng.MAX_STATE_BYTES+70)+18*(ng.MAX_INPUT_BYTES+ng.MAX_PAIR_BYTES+8)
            +16*(ng.MAX_SCAN_BYTES+100)+ng.MAX_METADATA_BYTES+8192)


@dataclass(frozen=True,slots=True)
class AudioAdapter:
    config: object
    view: str
    baseline: bool
    receipts: dict
    binding_digest: str

    def __call__(self,state,event):
        require(binding(self.config,self.view)["binding_digest"]==self.binding_digest,"BINDING_CHANGED")
        op=event.operation_payload
        require(type(op) is types.MaskedAudioOperationV2 and op.cue.band_plan==s.plan(self.view)
            and op.source_digest==event.source_digest and op.perception_digest==event.perception_digest,"OPERATION_BINDING_INVALID")
        key=(event.ordinal,"DIRECT_BASELINE" if self.baseline else "PRIMARY")
        require(key not in self.receipts,"SCAN_ALREADY_USED")
        before=digest(asdict(state))
        result=(direct.direct if self.baseline else s.retrieve)(config=self.config,state=state,cue=op.cue)
        require(before==digest(asdict(state)),"SCAN_MUTATED_MEMORY")
        hypothesis=types.wrap(result,op)
        self.receipts[key]=result
        return ng.stream.StreamScanResultV1(key[1],event.operation_projection_digest,result.prestate_digest,
            result.poststate_digest,result.decision,None if hypothesis is None else hypothesis.hypothesis_digest,
            result.result_digest,hypothesis)


class MaskRuntimeComparison(ng.RuntimeComparison):
    """Reuse branch observation, state pooling and isolation; never open a main gate."""
    def __init__(self,*,inputs,config,comparison_id,field_clock_id,mode="NEUTRAL"):
        require(mode=="NEUTRAL","MAIN_GATE_CLOSED")
        require(type(inputs) is tuple and 0<len(inputs)<=6,"NEUTRAL_LIMIT")
        self.limits=limits(tuple(v.event.event_type for v in inputs))
        require(self.limits["formations"]<=4,"NEUTRAL_LIMIT")
        ng.stream._identifier(comparison_id,"comparison id")
        self.parents=inputs
        self.events=tuple(v.event for v in inputs)
        self.arm_events=tuple(events_for(v,config) for v in inputs)
        require([e.ordinal for e in self.events]==list(range(1,len(inputs)+1))
            and self.events[0].event_type=="COMPLETE_AV_PERCEPTION","EVENT_ORDER_INVALID")
        require(all(t.field_time.clock_id==field_clock_id for e in self.events for t in e.field_payload.timed_frames),"CLOCK_INVALID")
        self.inputs=tuple(pack_input(v,config) for v in inputs)
        self.config,self.comparison_id,self.mode=config,comparison_id,mode
        self.input_digest,self.source_hashes=digest(self.inputs),sources()
        self.rows,self.states,self.subjects,self.branches,self.scans,self.bindings=[],{},[],[],[],[]
        self.initial,self.configs=[],[]
        self.failed=self.closed=False
        for i,view in enumerate(s.VIEWS):
            bound=binding(config,view)
            fs=ng.field.initial_s2lo_field_state(self.events[0].field_payload)
            ms=ng.memory.initial_s2jv_composite_state(config)
            initial=ng.stream.initial_perception_stream_state(stream_id=f"{comparison_id}-arm-{i}",
                field_state=fs,field_state_digest=fs.state_digest,memory_state=ms,memory_state_digest=ms.state_digest)
            fb=ng.ObservedBranch(ng.field.build_s2lo_field_adapter(field_clock_id),fs)
            mb=ng.ObservedBranch(ng.stream.build_s2jw_memory_adapter(config),ms)
            receipts={}
            processor=ng.stream.RoleFreePerceptionStreamProcessor(field_adapter=fb,memory_adapter=mb,
                auditory_scan=AudioAdapter(config,view,False,receipts,bound["binding_digest"]),
                auditory_baseline=AudioAdapter(config,view,True,receipts,bound["binding_digest"]),
                visual_scan=ng.VisualAdapter(config,False,receipts),visual_baseline=ng.VisualAdapter(config,True,receipts))
            rc=ng.runtime.build_masked_runtime_config(view=view,memory_config_digest=config.config_digest,
                runtime_id=f"{comparison_id}-arm-{i}",max_event_count=len(inputs),
                source_binding_digest=self.input_digest,component_binding_digest=bound["binding_digest"])
            subject=ng.runtime.MinimalMCMRuntime336(config=rc,processor=processor,initial_state=initial)
            self.bindings.append(bound); self.subjects.append(subject); self.branches.append((fb,mb)); self.scans.append(receipts)
            self.initial.append(dict(snapshot=asdict(subject.snapshot()),field=ng.field_record(fs),memory=ms.state_digest))
            self.configs.append(asdict(rc)); self._remember(ms)
        self._isolation()

    def process_next(self):
        require(not self.closed and not self.failed and len(self.rows)<len(self.events),"COMPARISON_NOT_OPEN")
        n=len(self.rows)
        require(pack_input(self.parents[n],self.config)==self.inputs[n],"INPUT_CHANGED")
        pair=[]
        for i,subject in enumerate(self.subjects):
            before=subject.snapshot()
            step=subject.process_once(self.arm_events[n][i])
            fb,mb=self.branches[i]
            self._remember(mb.state)
            pair.append(dict(pre=asdict(before),step={**asdict(step),"hypothesis":None if step.hypothesis is None else
                {**asdict(step.hypothesis),"hypothesis_digest":step.hypothesis.hypothesis_digest}},
                post=asdict(subject.snapshot()),field=ng.field_record(fb.state),memory=mb.state.state_digest))
        self._isolation()
        row=ng.sealed(dict(event_digest=self.events[n].event_digest,arms=pair),"pair_digest")
        require(len(canonical(row))<=ng.MAX_PAIR_BYTES,"PAIR_SIZE_EXCEEDED")
        self.rows.append(row)
        self.failed=any(a["step"]["error_codes"] for a in pair)
        return row

    def finish(self):
        require(not self.closed and (self.failed or len(self.rows)==len(self.events)),"COMPARISON_INCOMPLETE")
        final=[asdict(subject.close()) for subject in self.subjects]
        self.closed=True
        scans=[dict(arm=i,ordinal=n,role=role,value=asdict(value))
            for i,pool in enumerate(self.scans) for (n,role),value in sorted(pool.items())]
        require(all(len(canonical(row["value"]))<=ng.MAX_SCAN_BYTES for row in scans),"SCAN_SIZE_EXCEEDED")
        metadata=dict(schema=types.SCHEMA,comparison_id=self.comparison_id,mode=self.mode,
            status="NOT_EVALUABLE" if self.failed else "RECORDING_COMPLETE",input_digest=self.input_digest,
            config_digest=self.config.config_digest,sources=[list(p) for p in self.source_hashes],bindings=self.bindings,
            runtime_configs=self.configs,initial=self.initial,final=final,limits=self.limits)
        require(sources()==self.source_hashes and len(canonical(metadata))<=ng.MAX_METADATA_BYTES,"METADATA_BINDING_OR_SIZE")
        record=ng.sealed({**metadata,"inputs":list(self.inputs),"pairs":self.rows,"states":self.states,"scans":scans},"record_digest")
        require(len(canonical(record))<=ng.MAX_BYTES,"RECORD_SIZE_EXCEEDED")
        return record
