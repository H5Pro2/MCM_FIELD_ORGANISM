"""Independent NH binding checks and post-verification, role-separated reporting."""

import json
from pathlib import Path

from tools import _s2nh_private_runtime_binding as run
from tools import _s2ng_private_comparison_verification as direct
from tools import _s2ng_private_comparison_evaluation as evaluation

require, digest, canonical = run.require, run.digest, run.canonical


def receptor_payload(frame, part):
    common=dict(modality_id=frame.modality_id,geometry_id=frame.geometry_id,carrier_ids=list(frame.carrier_ids))
    zero=not any(frame.values)
    if frame.modality_id=="auditory":
        return dict(common,snapshot_index=part["endpoint_snapshot_index"],window_start_sample=part["start_tick"],
            window_end_sample=part["end_tick"],energy=list(frame.values),contact="active_zero" if zero else "active_energy")
    return dict(common,frame_index=part["start_tick"],channel_values=list(frame.values),contact="active_zero" if zero else "active_light")


def verify_bindings(record, bound, config):
    """No payload regeneration or receptor analysis; no functional expectations."""
    try:
        return _verify_bindings(record,bound,config)
    except run.S2NHRuntimeError:
        raise
    except (KeyError,TypeError,ValueError,AttributeError,IndexError) as error:
        raise run.S2NHRuntimeError("NH_RECORD_FORM_INVALID") from error


def _verify_bindings(record,bound,config):
    before=digest(record)
    run.check_digest(record,"record_digest")
    x=bound.payload()
    require(record["schema"]=="s2nh.runtime-record.v1" and record["execution_digest"]==x["execution_digest"]
        and record["main_gate_after"] is False and len(canonical(record))<=run.ng.MAX_BYTES
        and len(canonical({**record,"comparison":None}))<=run.MAX_ENVELOPE_BYTES,"NH_RECORD_BINDING_INVALID")
    require(record["materialization_calls"] in (0,1),"MATERIALIZATION_CALLS_INVALID")
    r=record["comparison"]
    if r is None:
        f=record["failure"]
        require(record["status"]=="NOT_EVALUABLE" and type(f) is dict
            and f["phase"] in ("BINDINGS","INITIAL","PAYLOAD_GENERATION","PAYLOAD_HASH","RECEPTOR_ANALYSIS",
                "RECEPTOR_BINDING","EVENT_BINDING","MATERIALIZATION","RUNTIME","SERIALIZATION")
            and (f["ordinal"] is None or type(f["ordinal"]) is int and 1<=f["ordinal"]<=len(x["events"]))
            and (f["source_id"] is None or f["source_id"] in {s["source_id"] for s in x["sources"]})
            and type(f["code"]) is str and type(f["error_class"]) is str,"FAILURE_BINDING_INVALID")
        return run.source.sealed(dict(status="NOT_EVALUABLE",record_digest=record["record_digest"],
            evidence_valid=True,read_only=True,comparison_verification=None),"verification_digest")
    require(r["mode"]==bound.mode and r["field_clock_id"]==run.FIELD_CLOCK
        and len(r["inputs"])==len(record["source_receipts"])==len(x["events"]),"EVENT_COVERAGE_INVALID")
    sources={s["source_id"]:s for s in x["sources"]}
    counts=dict(audio_windows=0,visual_frames=0,audio_hops=0,audio_snapshots=0,completed_events=len(x["events"]))
    for spec,packed,receipt in zip(x["events"],r["inputs"],record["source_receipts"],strict=True):
        run.check_digest(receipt,"receipt_digest")
        event=direct.decode_input(packed,config)
        require(event.ordinal==spec["ordinal"] and event.event_id=="s2nh-event-"+spec["event_id"]
            and event.event_type==spec["event_type"],"EVENT_SPEC_INVALID")
        base=dict(execution_digest=x["execution_digest"],spec_digest=digest(spec),
            source_occurrence_id=spec["source_occurrence_id"],auditory=None,visual=None)
        frames={t.frame.modality_id:t for t in event.field_payload.timed_frames}
        require(len(frames)==len(event.field_payload.timed_frames)
            and set(frames)=={m for m in ("auditory","visual") if spec[m] is not None},"MODALITY_BINDING_INVALID")
        for modality,t in frames.items():
            p=spec[modality]
            s=sources[p["source_id"]]
            f=t.frame
            require((f.clock_id,f.window_start_tick,f.window_end_tick)==(p["clock_id"],p["start_tick"],p["end_tick"])
                and (t.field_time.clock_id,t.field_time.window_start_tick,t.field_time.window_end_tick)
                ==(run.FIELD_CLOCK,*p["common_window"]),"SOURCE_TIME_INVALID")
            require(f.snapshot_id==("auditory.receptor."+str(p["endpoint_snapshot_index"]) if modality=="auditory"
                else "visual.receptor."+str(p["start_tick"])),"SNAPSHOT_BINDING_INVALID")
            base[modality]=dict(source_id=s["source_id"],payload_sha256=s["payload_sha256"],
                receptor_state_digest=digest(receptor_payload(f,p)),values_digest=digest(list(f.values)))
            counts["audio_windows" if modality=="auditory" else "visual_frames"]+=1
        require(receipt["base"]==base and receipt["source_digest"]==digest(base)==event.source_digest
            and receipt["event_digest"]==event.event_digest,"SOURCE_RECEIPT_INVALID")
        op=event.operation_payload
        if event.event_type==run.source.A:
            require(op.cue.pcm_payload_digest==base["auditory"]["payload_sha256"]
                and op.cue.receptor_state_digest==base["auditory"]["receptor_state_digest"]
                and op.cue.receptor_values_digest==base["auditory"]["values_digest"],"AUDIO_CUE_SOURCE_INVALID")
        elif event.event_type==run.source.V:
            require(op.source_digest==digest(base) and all(v==0.0 for v in frames["visual"].frame.values[32:]),
                "OCCLUDED_CUE_SOURCE_INVALID")
        else:
            require(packed["operation"]["auditory_payload_digest"]==base["auditory"]["payload_sha256"]
                and packed["operation"]["visual_payload_digest"]==base["visual"]["payload_sha256"],"FORMATION_SOURCE_INVALID")
    counts["audio_hops"]=counts["audio_windows"]*10
    counts["audio_snapshots"]=max(0,counts["audio_hops"]-9)
    require(record["materialization"]==counts and record["materialization_calls"]==1,"MATERIALIZATION_COUNTS_INVALID")
    if bound.mode=="MAIN":
        require(counts==dict(audio_windows=24,visual_frames=24,audio_hops=240,audio_snapshots=231,completed_events=28),"NH_COUNTS_INVALID")
    proof=direct.verify_record(r,config=config)
    require(record["status"]==proof["status"] and (record["status"]!="RECORDING_COMPLETE" or record["failure"] is None)
        and digest(record)==before,"TECHNICAL_STATUS_INVALID")
    return run.source.sealed(dict(status=record["status"],record_digest=record["record_digest"],
        evidence_valid=True,read_only=True,comparison_verification=proof),"verification_digest")


def verify_once(path,bound,config):
    path=Path(path)
    destination=path.with_name("verification.json")
    require(not destination.exists(),"VERIFICATION_ALREADY_EXISTS")
    before=run.source.filehash(path)
    data=path.read_bytes()
    try:
        require(len(data)<=run.ng.MAX_BYTES,"RECORD_SIZE_EXCEEDED")
        record=json.loads(data)
        require(canonical(record)==data,"RECORD_CANONICAL_INVALID")
        if bound.mode=="MAIN":
            registration=json.loads(path.with_name("preregistration.json").read_bytes())
            require(registration["run_id"]==record["run_id"] and registration["hashes"]==run.watched()
                and record["binding_digest"]==digest(registration["hashes"]),"EXECUTION_SOURCES_CHANGED")
        proof=verify_bindings(record,bound,config)
    except Exception as error:
        proof=dict(status="NOT_EVALUABLE",evidence_valid=False,read_only=True,
            code=getattr(error,"code","VERIFICATION_FORM_INVALID"),error_class=type(error).__name__)
    proof=run.source.sealed(dict(proof,result_file_sha256=before,file_unchanged=run.source.filehash(path)==before,
        verification_calls=1),"file_verification_digest")
    run.ng.ne.atomic_write(destination,proof)
    return proof


def advance_lineage(pre,post,spec,history,config):
    """Classify actual PPB changes, including saturated MATCHED and replacement."""
    transitions=[]
    for modality in ("auditory","visual"):
        bank=modality+"_ppb1_state"
        a,b=pre["tspm_state"][bank],post["tspm_state"][bank]
        changes=[(l,r) for l,r in zip(a["slots"],b["slots"],strict=True) if l!=r]
        if not changes:
            transitions.append(dict(ordinal=spec["ordinal"],modality=modality,event="NO_UPDATE",slot_id=None))
        for left,right in changes:
            key=right["slot_id"]
            fresh=not left["occupied"] or right["support_count"]==1
            event=("REPLACED" if left["occupied"] else "CREATED") if fresh else "MATCHED"
            if fresh:
                history[modality][key]=[]
            history[modality].setdefault(key,[]).append(dict(ordinal=spec["ordinal"],recipe_id=spec["recipe_id"]))
            transitions.append(dict(ordinal=spec["ordinal"],modality=modality,event=event,slot_id=key,
                support=right["support_count"],stable=right["support_count"]>=getattr(config.profile.profile,modality+"_config").stable_after,
                pre_slot_digest=digest(left),post_slot_digest=digest(right),values_digest=digest(right["prototype_values"]),
                lineage=list(history[modality][key]),mixed=len({v["recipe_id"] for v in history[modality][key]})>1))
    return transitions


def evaluate(record,proof,bound,root,config):
    """Only here are the evaluation root, expected support and roles consumed."""
    run.check_digest(proof,"verification_digest")
    require(proof["status"]==record["status"]=="RECORDING_COMPLETE" and proof["evidence_valid"]
        and proof["record_digest"]==record["record_digest"],"TECHNICAL_VERIFICATION_REQUIRED")
    run.check_digest(root,"evaluation_digest")
    require(root["execution_digest"]==bound.payload()["execution_digest"]
        and (bound.mode!="MAIN" or root["evaluation_digest"]==run.EVALUATION_DIGEST),"EVALUATION_ROOT_INVALID")
    before=digest(record)
    r=record["comparison"]
    history={m:{} for m in ("auditory","visual")}
    fast_lineage,formation_recipes={},{}
    original,original_payloads,transitions,inventories,expectations,diagnostics={}, {},[],[],[],[]
    cases={c["ordinal"]:c for c in root["cases"]}
    specs=bound.payload()["events"]
    require(len(cases)==len(root["cases"]) and set(cases)=={s["ordinal"] for s in specs if s["event_type"]!=run.source.AV},"CASE_COVERAGE_INVALID")
    for spec,packed,pair in zip(specs,r["inputs"],r["pairs"],strict=True):
        arm=pair["arms"][0]
        pre,post=r["states"][arm["pre"]["memory_state_digest"]],r["states"][arm["memory"]]
        frames={t["frame"]["modality_id"]:t["frame"]["values"] for t in packed["field"]["timed_frames"]}
        if spec["event_type"]==run.source.AV:
            for m,values in frames.items():
                original.setdefault((spec["recipe_id"],m),values)
                original_payloads.setdefault((spec["recipe_id"],m),record["source_receipts"][spec["ordinal"]-1]["base"][m]["payload_sha256"])
            transitions.extend(advance_lineage(pre,post,spec,history,config))
            selected=[s for s in post["tspm_state"]["fast_state"]["slots"] if s["occupied"] and s["last_selected_step"]==post["generation"]]
            formation_recipes[post["generation"]]=spec["recipe_id"]
            occupied={s["slot_id"] for s in post["tspm_state"]["fast_state"]["slots"] if s["occupied"]}
            fast_lineage={k:v for k,v in fast_lineage.items() if k in occupied}
            for slot in selected:
                if slot["consolidation_count"]==0:
                    fast_lineage[slot["slot_id"]]=[]
                fast_lineage.setdefault(slot["slot_id"],[]).append(spec["recipe_id"])
            inventories.append(dict(ordinal=spec["ordinal"],prestate_digest=arm["pre"]["memory_state_digest"],
                poststate_digest=arm["memory"],b4=post["b4_state"],fast=post["tspm_state"]["fast_state"],
                fast_selected_slot_ids=[s["slot_id"] for s in selected],
                fast_lineage=deepcopy_json(fast_lineage),
                auditory_slow=post["tspm_state"]["auditory_ppb1_state"],visual_slow=post["tspm_state"]["visual_ppb1_state"]))
            continue
        c=cases[spec["ordinal"]]
        m="auditory" if spec["event_type"]==run.source.A else "visual"
        target=c["target_recipe"]
        targets=[] if (target,m) not in original else [digest(original[target,m])]
        for slot in pre["tspm_state"][m+"_ppb1_state"]["slots"]:
            lineage=history[m].get(slot["slot_id"],[])
            if slot["occupied"] and lineage and {x["recipe_id"] for x in lineage}=={target}:
                targets.append(digest(slot["prototype_values"]))
        scan=next(s["value"] for s in r["scans"] if s["ordinal"]==spec["ordinal"] and s["arm"]==0 and s["role"]=="PRIMARY")
        scan=scan["evidence"] if m=="auditory" else scan
        candidates=[s for bank in scan["bank_scans"] for s in bank["records"] if s["candidate_values_digest"] is not None]
        competition="COMPETITION_PRESENT" if any(s["candidate_values_digest"] not in targets for s in candidates) else "NO_COMPETITION"
        expectations.append(evaluation.ExpectationV1(spec["ordinal"],m,tuple(dict.fromkeys(targets)),c["expected_context"],c["variant"],competition))
        width=24 if m=="auditory" else 32
        reference=original.get((target,m))
        variations=None if reference is None else dict(payload_bits_changed=record["source_receipts"][spec["ordinal"]-1]["base"][m]["payload_sha256"]!=original_payloads[target,m],
            receptor_bits_changed=frames[m]!=reference,
            observed_bits_changed=frames[m][:width]!=reference[:width])
        diagnostics.append(dict(ordinal=spec["ordinal"],phase=c["phase"],variation=variations,
            current_target_candidate_count=sum(s["candidate_values_digest"] in targets for s in candidates),
            current_other_candidate_count=sum(s["candidate_values_digest"] not in targets for s in candidates),
            state_digest=arm["memory"]))
    result=evaluation.evaluate(r,proof["comparison_verification"],tuple(expectations))
    byordinal={d["ordinal"]:d for d in diagnostics}
    phase_groups={phase:evaluation.summarize([row for row in result["rows"] if byordinal[row["ordinal"]]["phase"]==phase])
        for phase in sorted({d["phase"] for d in diagnostics})}
    variation_groups={key:{str(value):evaluation.summarize([row for row in result["rows"]
        if byordinal[row["ordinal"]]["variation"] is not None and byordinal[row["ordinal"]]["variation"][key] is value])
        for value in (False,True)} for key in ("payload_bits_changed","receptor_bits_changed","observed_bits_changed")}
    require(digest(record)==before,"EVALUATION_MUTATED_RECORD")
    final=r["states"][r["final"][0]["memory_state_digest"]]
    eviction=[dict(recipe_id=recipe,
        b4_slots=[s["slot_id"] for s in final["b4_state"]["entries"] if s["occupied"] and formation_recipes[s["formation_index"]]==recipe],
        fast_slots=[k for k,v in fast_lineage.items() if recipe in v]) for recipe in root.get("expected_recent_eviction",[])]
    support_report=[]
    for recipe,expected_support in root["expected_support"].items():
        for m in ("auditory","visual"):
            own=[s for s in final["tspm_state"][m+"_ppb1_state"]["slots"] if s["occupied"]
                 and {e["recipe_id"] for e in history[m].get(s["slot_id"],[])}=={recipe}]
            support_report.append(dict(recipe_id=recipe,modality=m,expected_support=expected_support,
                actual_pure_slots=[dict(slot_id=s["slot_id"],support=s["support_count"],
                    stable=s["support_count"]>=getattr(config.profile.profile,m+"_config").stable_after) for s in own],
                predicted_support_present=any(s["support_count"]==expected_support for s in own)))
    answer=run.source.sealed(dict(comparison=result,phase_groups=phase_groups,variation_groups=variation_groups,cue_diagnostics=diagnostics,
        formation_inventories=inventories,ppb_transitions=transitions,final_lineages=history,
        support_report=support_report,recent_eviction=eviction,support_is_evaluation_only=True,
        conclusion="BOUNDED_TRANSFER_COMPARISON_NOT_GENERAL_ROBUSTNESS"),"evaluation_digest")
    require(len(canonical(answer))<=run.ng.MAX_BYTES,"EVALUATION_SIZE_EXCEEDED")
    return answer


def deepcopy_json(value):
    return json.loads(canonical(value))
