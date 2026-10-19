"""One regular formation between two visual scans; no field or decoder."""
from dataclasses import asdict, replace
import json
from tools import _s2oe_immediate_visual_input as source
from tools import _s2nn_private_half_runtime_binding as nn
from tools import _s2ng_private_comparison_verification as ngv
from tools import _s2oa_private_runtime_binding as evidence
from tools import _s2ob_private_state_evidence as wire

MAIN_GATE = False
CLOCK = "immediate-visual-session-clock"
PRESENTATION_VERSION = "s2oe.frozen-presentation.v1"
PRESENTATIONS = (("immediate-visual-empty",9,10,300000000,333333333),
                 ("immediate-visual-form",14,15,466666666,500000000),
                 ("immediate-visual-after",15,16,500000000,533333333))


def presentation(p, index):
    source.need(type(index) is int and 0 <= index < 3, "PRESENTATION_INDEX_INVALID")
    identity,start,end,session_start,session_end = PRESENTATIONS[index]
    frames = p["input"]["field"]["timed_frames"]
    original = {x["frame"]["modality_id"]:x for x in frames}
    value = dict(version=PRESENTATION_VERSION,presentation_id=identity,index=index,
        parent_sha256=p["parent_sha256"],historical_event_digest=p["input"]["event"]["event_digest"],
        historical_frames_digest=source.sha(source.canonical(frames)),
        values_digest=source.sha(source.canonical([original[k]["frame"]["values"] for k in ("auditory","visual")])),
        visual_clock="video.frame",visual_window=[start,end],session_clock=CLOCK,
        visual_session_window=[session_start,session_end],
        auditory_clock="audio.sample" if index==1 else None,
        auditory_window=[19200,24000] if index==1 else None,
        auditory_session_window=[400000000,500000000] if index==1 else None,
        measurement=False)
    return source.canonical({**value,"presentation_digest":source.sha(source.canonical(value))})


def validate_presentation(blob,p,index):
    source.need(type(blob) is bytes and blob == presentation(p,index), "PRESENTATION_BINDING_INVALID")
    return json.loads(blob)


def run(excerpt, binding, *, run_id, neutral=False, progress=None):
    source.need(neutral is binding.neutral and (neutral or MAIN_GATE), "MAIN_GATE_CLOSED")
    reads = dict(bytes=0, operations=0)
    fresh = source.read_extract(binding, reads)
    source.need(excerpt == fresh, "EXTRACTION_RELATION_INVALID")
    p = json.loads(fresh)
    config = nn.profile.build_config()
    source.need(p["config_digest"] == config.config_digest, "PROFILE_BINDING_INVALID")
    original = ngv.decode_input(p["input"], config)
    frames = {t.frame.modality_id: t for t in original.field_payload.timed_frames}
    presentations = [presentation(p,i) for i in range(3)]
    descriptions = [validate_presentation(v,p,i) for i,v in enumerate(presentations)]
    form = descriptions[1]
    audio = replace(frames["auditory"], frame=replace(frames["auditory"].frame,
        snapshot_id="present.audio."+form["presentation_digest"],window_start_tick=19200,window_end_tick=24000),
        field_time=nn.CommonFieldTime(CLOCK,400000000,500000000))
    visual = replace(frames["visual"], frame=replace(frames["visual"].frame,
        snapshot_id="present.visual."+form["presentation_digest"],window_start_tick=14,window_end_tick=15),
        field_time=nn.CommonFieldTime(CLOCK,466666666,500000000))
    pair = nn.ng.pairing.build_s2jv_pairing_plan(pair_id="immediate-visual-form",
        source_contract_id="present."+form["presentation_digest"],
        profile=config.profile, auditory=audio, visual=visual,
        auditory_payload_digest=p["source_receipt"]["nj"]["pcm_digest"],
        visual_payload_digest=p["source_receipt"]["rgb_digest"])
    operation = nn.ng.pairing.bind_s2jv_default_live_pair(pairing_plan=pair,
        profile=config.profile, auditory=audio, visual=visual)
    m, scan, direct = nn.ng.memory, nn.ng.visual, nn.ng.visual_direct
    state = m.initial_s2jv_composite_state(config)
    scans, states = [], [wire.encode(asdict(state))]
    packed_formation = context = None
    def checkpoint(phase, completed):
        if progress is not None:
            progress(source.canonical(dict(phase=phase,completed_events=completed,
                states=states,scans=scans,formation=packed_formation,formation_context=context,
                parent_sha256=binding.sha256,historical_input=p["input"],presentations=descriptions,
                session_pair=asdict(pair),reads=reads,field_calls=0)))
    checkpoint("INITIALIZED",0)
    for index in (0,2):
        description = descriptions[index]
        start,end = description["visual_session_window"]
        cue = scan.build_masked_memory_cue_336(source_digest=description["presentation_digest"],
            config_digest=config.config_digest, field_clock_id=CLOCK,
            window_start_tick=start, window_end_tick=end,
            visual_source_clock_id=visual.frame.clock_id,
            visual_window_start_tick=description["visual_window"][0],
            visual_window_end_tick=description["visual_window"][1],
            values=tuple(v if i < 32 else None for i,v in enumerate(visual.frame.values)))
        before = source.canonical(asdict(state))
        a = scan.form_partial_cue_retrieval_336(config=config,state=state,cue=cue)
        b = direct.form_direct_partial_cue_slot_scan_baseline_336(config=config,state=state,cue=cue)
        source.need(before == source.canonical(asdict(state)), "READ_ONLY_INVALID")
        scans.append(dict(cue=asdict(cue),primary=asdict(a),direct=asdict(b)))
        checkpoint("EMPTY_CUE_COMPLETE" if index==0 else "REPEAT_CUE_COMPLETE",1 if index==0 else 3)
        if len(scans) == 1:
            bound = m.bind_s2jv_coordinator_input(config=config, source=operation)
            owner = m.S2JVFormationOwner("immediate-visual-form-owner",run_id,"immediate-visual-form-consume",
                config.config_digest,state.state_digest,bound.input_digest)
            prior = owner.snapshot()
            formation = m.advance_s2jv_atomic(config=config,prestate=state,source=bound,owner=owner)
            context = evidence.formation_context(config,state,formation.poststate,bound,
                replace(original,event_id="immediate-visual-form"),run_id,formation.result_digest)
            packed_formation = evidence.pack_formation(formation,prior,context)
            state = formation.poststate
            states.append(wire.encode(asdict(state)))
            checkpoint("FORMATION_COMPLETE",2)
    return dict(version="s2oe.immediate-visual-control.v2",status="RECORDING_COMPLETE",
        presentations=descriptions,
        parent_sha256=binding.sha256, historical_input=p["input"], session_pair=asdict(pair),
        states=states,formation=packed_formation,formation_context=context,scans=scans,reads=reads,
        field_calls=0,receptor_calls=0,nj_calls=0)
