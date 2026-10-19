"""Offline verification; never calls formation or public retrieval entries."""
from dataclasses import asdict, replace
import hashlib
import json
from tools import _s2oe_immediate_visual_control as c
from tools import _s2nq_private_verification as relations


def verify(record, binding, parent_bytes, run_id):
    p=c.source
    before=p.canonical(record)
    binding.validate()
    p.need(len(parent_bytes)==binding.byte_count and hashlib.sha256(parent_bytes).hexdigest()==binding.sha256,
           "VERIFICATION_PARENT_INVALID")
    parent=json.loads(parent_bytes)["record"]["execution"]
    historical=parent["inputs"][2]
    p.need(record["status"]=="RECORDING_COMPLETE" and record["parent_sha256"]==binding.sha256
           and p.canonical(record["historical_input"])==p.canonical(historical)
           and historical["event"]["event_digest"]==binding.event_digest
           and parent["config_digest"]==binding.config_digest, "VERIFICATION_INPUT_INVALID")
    config=c.nn.profile.build_config()
    original=c.ngv.decode_input(historical,config)
    frames={f.frame.modality_id:f for f in original.field_payload.timed_frames}
    descriptions=record["presentations"]
    p.need(len(descriptions)==3 and len(record["states"])==2 and len(record["scans"])==2,
           "VERIFICATION_SEQUENCE_INVALID")
    # Independent reconstruction of the closed presentation contract.
    specs=(("immediate-visual-empty",9,10,300000000,333333333),
           ("immediate-visual-form",14,15,466666666,500000000),
           ("immediate-visual-after",15,16,500000000,533333333))
    by={t["frame"]["modality_id"]:t for t in historical["field"]["timed_frames"]}
    for i,(d,spec) in enumerate(zip(descriptions,specs,strict=True)):
        identity,start,end,t0,t1=spec
        expected=dict(version="s2oe.frozen-presentation.v1",presentation_id=identity,index=i,
            parent_sha256=binding.sha256,historical_event_digest=binding.event_digest,
            historical_frames_digest=p.sha(p.canonical(historical["field"]["timed_frames"])),
            values_digest=p.sha(p.canonical([by[k]["frame"]["values"] for k in ("auditory","visual")])),
            visual_clock="video.frame",visual_window=[start,end],session_clock=c.CLOCK,
            visual_session_window=[t0,t1],auditory_clock="audio.sample" if i==1 else None,
            auditory_window=[19200,24000] if i==1 else None,
            auditory_session_window=[400000000,500000000] if i==1 else None,measurement=False)
        p.need(d=={**expected,"presentation_digest":p.sha(p.canonical(expected))},"VERIFICATION_PRESENTATION_INVALID")
    d=descriptions[1]
    audio=replace(frames["auditory"],frame=replace(frames["auditory"].frame,
        snapshot_id="present.audio."+d["presentation_digest"],window_start_tick=19200,window_end_tick=24000),
        field_time=c.nn.CommonFieldTime(c.CLOCK,400000000,500000000))
    visual=replace(frames["visual"],frame=replace(frames["visual"].frame,
        snapshot_id="present.visual."+d["presentation_digest"],window_start_tick=14,window_end_tick=15),
        field_time=c.nn.CommonFieldTime(c.CLOCK,466666666,500000000))
    pairing=c.nn.ng.pairing
    plan=pairing.build_s2jv_pairing_plan(pair_id="immediate-visual-form",
        source_contract_id="present."+d["presentation_digest"],profile=config.profile,auditory=audio,visual=visual,
        auditory_payload_digest=parent["source_receipts"][2]["nj"]["pcm_digest"],
        visual_payload_digest=parent["source_receipts"][2]["rgb_digest"])
    p.need(p.canonical(record["session_pair"])==p.canonical(asdict(plan)),"VERIFICATION_PAIR_INVALID")
    pair=pairing.bind_s2jv_default_live_pair(pairing_plan=plan,profile=config.profile,auditory=audio,visual=visual)
    m=c.nn.ng.memory
    bound=m.bind_s2jv_coordinator_input(config=config,source=pair)
    pre,post=[relations.old.decode_state(c.wire.decode(x),config) for x in record["states"]]
    p.need(pre.generation==0 and all(not x.occupied for _,x in c.evidence.slots(pre)),"VERIFICATION_INITIAL_INVALID")
    context=c.evidence.formation_context(config,pre,post,bound,
        replace(original,event_id="immediate-visual-form"),run_id,record["formation"]["result_digest"])
    p.need(context==record["formation_context"],"VERIFICATION_FORMATION_CONTEXT_INVALID")
    form,owner=c.evidence.unpack_formation(record["formation"],context)
    work={k:0 for k in c.evidence.WORK_LIMITS}
    transition=relations._formation(dict(spec=dict(event_id="immediate-visual-form"),formation=form,owner_before=owner),
                                   pre,post,bound,config,run_id,work)
    comparisons=0
    for i,(step,state) in enumerate(zip(record["scans"],(pre,post),strict=True)):
        d=descriptions[0 if i==0 else 2]
        cue=c.nn.ng.visual.build_masked_memory_cue_336(source_digest=d["presentation_digest"],config_digest=config.config_digest,
            field_clock_id=c.CLOCK,window_start_tick=d["visual_session_window"][0],window_end_tick=d["visual_session_window"][1],
            visual_source_clock_id="video.frame",visual_window_start_tick=d["visual_window"][0],visual_window_end_tick=d["visual_window"][1],
            values=tuple(v if n<32 else None for n,v in enumerate(visual.frame.values)))
        p.need(p.canonical(asdict(cue))==p.canonical(step["cue"]),"VERIFICATION_CUE_INVALID")
        for key,role in (("primary","PRIMARY"),("direct","DIRECT_SLOT_SCAN_BASELINE")):
            result=c.ngv.decode_visual(step[key])
            c.ngv.verify_visual(result,config,state,cue)
            comparisons+=result.resource_ledger.total_value_comparison_count
        p.need(c.ngv.visual_semantics(c.ngv.decode_visual(step["primary"]))==
               c.ngv.visual_semantics(c.ngv.decode_visual(step["direct"])),"VERIFICATION_BASELINE_INVALID")
    p.need(comparisons<=3200 and all(work[k]<=c.evidence.WORK_LIMITS[k] for k in work),"VERIFICATION_WORK_LIMIT")
    p.need(record["field_calls"]==record["receptor_calls"]==record["nj_calls"]==0
           and record["reads"]==dict(bytes=binding.byte_count,operations=1),"VERIFICATION_COUNTS_INVALID")
    p.need(before==p.canonical(record),"VERIFICATION_MUTATION")
    return dict(version="s2oe.immediate-proof.v1",status="EVIDENCE_VALID",evaluation_allowed=True,
        record_sha256=p.sha(before),parent_sha256=binding.sha256,work=work,scan_comparisons=comparisons,
        fast_selected=transition["fast_rank"]["selected_slot_id"])


def evaluate(record, proof):
    c.source.need(proof.get("evaluation_allowed") is True and proof.get("status")=="EVIDENCE_VALID"
                  and proof["record_sha256"]==c.source.sha(c.source.canonical(record)),"EVALUATION_BLOCKED")
    return dict(version="s2oe.immediate-evaluation.v1",decisions=[
        dict(position=i,actual=s["primary"]["decision"],expected=e,
             agrees=s["primary"]["decision"]==e)
        for i,s,e in zip((0,2),record["scans"],("ABSTAIN_NO_CONTEXT","ADMIT_SINGLE_CONTEXT"),strict=True)],
        boundary="Immediate retrieval of frozen perception only; no new receptor measurement.")
