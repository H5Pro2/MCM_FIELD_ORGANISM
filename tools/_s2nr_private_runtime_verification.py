"""Offline mask-composition checks using existing state/PPB/scan verifiers."""
from dataclasses import asdict
from tools import _s2nr_private_runtime_binding as run
from tools import _s2ng_private_comparison_verification as old
from tools import _s2nl_private_rank_verification as rank

s, ng = run.s, run.ng
require, digest, canonical = run.require, run.digest, run.canonical


def fast_relation(config,pre,post,source):
    evidence=rank.direct_scan(config,pre,source,mode="FAST_FORMATION")
    cfg=config.tspm_config.fast_config
    step=pre.generation+1
    slots=[type(x).free(x.slot_id) if x.occupied and step-x.last_selected_step>=cfg.expire_after_exposures
           else x for x in pre.tspm_state.fast_state.slots]
    matched=evidence.selected_slot_id is not None
    if matched:
        selected=next(x for x in slots if x.slot_id==evidence.selected_slot_id)
    else:
        free=[x for x in slots if not x.occupied]
        selected=min(free,key=lambda x:x.slot_id) if free else min(slots,key=lambda x:(x.last_selected_step,x.slot_id))
    support=min(cfg.consolidate_after,selected.support_count+1) if matched else 1
    eligible=matched and support>=cfg.consolidate_after
    rate=cfg.update_factor
    audio=tuple((1.0-rate)*x+rate*y for x,y in zip(selected.auditory_values,source.auditory_values,strict=True)) if matched else source.auditory_values
    visual=tuple((1.0-rate)*x+rate*y for x,y in zip(selected.visual_values,source.visual_values,strict=True)) if matched else source.visual_values
    expected=type(selected)(selected.slot_id,True,audio,visual,support,step,
        (selected.consolidation_count if matched else 0)+int(eligible),
        source.tspm_exposure.exposure_digest if eligible else selected.last_consolidation_exposure_digest if matched else None)
    slots=[expected if x.slot_id==selected.slot_id else x for x in slots]
    actual=post.tspm_state.fast_state
    require(actual.slots==tuple(slots) and actual.accepted_exposure_count==step,"FAST_TRANSITION_INVALID")
    for modality in ("auditory","visual"):
        frame=getattr(source.source,modality).timed_frame.frame
        require(getattr(actual,modality+"_source_clock_id")==frame.clock_id
            and getattr(actual,modality+"_last_end_tick")==frame.window_end_tick,"FAST_TIME_INVALID")
        a=getattr(pre.tspm_state,modality+"_ppb1_state")
        b=getattr(post.tspm_state,modality+"_ppb1_state")
        require(b.accepted_step_count==a.accepted_step_count+int(eligible),"FAST_PPB_LINK_INVALID")
    return dict(selected_slot=selected.slot_id,matched=matched,selected_key=evidence.selected_key,
        support=support,consolidation=eligible,term_count=evidence.term_count)


def verify_record(record, *, inputs, config):
    try:
        return _verify(record,inputs,config)
    except s.S2NQError:
        raise
    except (KeyError,TypeError,ValueError,AttributeError,IndexError,ng.memory.S2JWCoordinatorError) as exc:
        raise s.S2NQError("RUNTIME_RECORD_INVALID") from exc


def _verify(r,inputs,config):
    before=digest(r)
    old.check(r,"record_digest")
    packed=[run.pack_input(v,config) for v in inputs]
    require(r["schema"]==run.types.SCHEMA and r["mode"] in ("NEUTRAL","MAIN") and 0<len(inputs)<=18
        and canonical(packed)==canonical(r["inputs"]) and r["input_digest"]==digest(packed)
        and r["config_digest"]==config.config_digest and r["sources"]==[list(p) for p in run.sources()],"RECORD_BINDING_INVALID")
    events=[run.events_for(v,config) for v in inputs]
    require(r["limits"]==run.limits(tuple(v.event.event_type for v in inputs))
        and len(canonical(r))<=ng.MAX_BYTES,"LIMIT_INVALID")
    require((len(inputs)<=6 and r["limits"]["formations"]<=4) if r["mode"]=="NEUTRAL" else
        (len(inputs)==18 and r["limits"]["formations"]==28 and r["limits"]["field_contacts"]==9792
         and r["limits"]["scans"]==16),"MODE_EXTENT_INVALID")
    states={h:old.old.decode_state(p,config) for h,p in r["states"].items()}
    require(0<len(states)<=r["limits"]["formations"]//2+1
        and all(h==v.state_digest and len(canonical(r["states"][h]))<=ng.MAX_STATE_BYTES for h,v in states.items()),"STATE_POOL_INVALID")
    require(all(len(r[k])==2 for k in ("bindings","runtime_configs","initial","final")),"ARM_COUNT_INVALID")
    previous=[]
    for i,view in enumerate(s.VIEWS):
        bound=run.binding(config,view)
        require(canonical(bound)==canonical(r["bindings"][i]),"MASK_BINDING_INVALID")
        rc=ng.runtime.build_masked_runtime_config(view=view,memory_config_digest=config.config_digest,
            runtime_id=f'{r["comparison_id"]}-arm-{i}',max_event_count=len(inputs),
            source_binding_digest=r["input_digest"],component_binding_digest=bound["binding_digest"])
        require(r["runtime_configs"][i]==asdict(rc),"RUNTIME_CONFIG_INVALID")
        p=r["initial"][i]
        st=states[p["memory"]]
        require(st.generation==0 and not any(x.occupied for x in st.b4_state.entries)
            and not any(x.occupied for x in st.tspm_state.fast_state.slots)
            and p["field"]["phase"]=="PRE_CONTACT" and p["field"]["step_count"]==0,"INITIAL_INVALID")
        old.snapshot(p["snapshot"],asdict(rc),p["field"],st.state_digest,0,0,None)
        previous.append(p)
    require(previous[0]["field"]==previous[1]["field"] and previous[0]["memory"]==previous[1]["memory"],"INITIAL_SIBLINGS_DIFFER")
    scanmap={(p["arm"],p["ordinal"],p["role"]):p["value"] for p in r["scans"]}
    require(len(scanmap)==len(r["scans"])<=r["limits"]["scans"],"SCAN_COUNT_INVALID")
    require(0<len(r["pairs"])<=len(inputs) and
        (r["status"]!="RECORDING_COMPLETE" or len(r["pairs"])==len(inputs)),"EVENT_COUNT_INVALID")
    scanned,used=set(),{p["memory"] for p in previous}
    forms,contacts,terms,errors=0,0,0,[]
    fast_transitions=[]
    for n,pair in enumerate(r["pairs"],1):
        old.check(pair,"pair_digest")
        require(len(pair["arms"])==2 and pair["event_digest"]==inputs[n-1].event.event_digest
            and len(canonical(pair))<=ng.MAX_PAIR_BYTES,"PAIR_INVALID")
        full=inputs[n-1].event.event_type=="COMPLETE_AV_PERCEPTION"
        forms+=int(full)
        for i,arm in enumerate(pair["arms"]):
            event=events[n-1][i]
            prior=previous[i]
            require(arm["pre"]==prior["snapshot"],"SNAPSHOT_CHAIN_INVALID")
            step,post,f=arm["step"],arm["post"],arm["field"]
            h=step["hypothesis"]
            sp={k:v for k,v in step.items() if k not in ("step_digest","hypothesis")}
            sp["hypothesis_digest"]=None if h is None else h["hypothesis_digest"]
            require(step["step_digest"]==digest(sp) and step["event_digest"]==event.event_digest
                and step["prestate_digest"]==arm["pre"]["snapshot_digest"] and step["poststate_digest"]==post["snapshot_digest"],"STEP_INVALID")
            codes=step["error_codes"]
            require(all(x in ("FIELD_BRANCH_FAILED","MEMORY_BRANCH_FAILED","PRIMARY_SCAN_FAILED","BASELINE_SCAN_FAILED") for x in codes),"ERROR_CODE_INVALID")
            errors.extend(codes)
            if step["perception_status"]=="FIELD_CONTACT_RECORDED":
                require("FIELD_BRANCH_FAILED" not in codes and f["phase"]=="COMPLETED"
                    and f["step_count"]==prior["field"]["step_count"]+1 and f["last_end_tick"]==event.field_payload.end_tick
                    and f["state_digest"]!=prior["field"]["state_digest"],"FIELD_PROGRESS_INVALID")
                fp=dict(schema=ng.field.S2LO_SCHEMA,phase=f["phase"],field_component_digest=f["field_component_digest"],
                        last_end_tick=f["last_end_tick"],step_count=f["step_count"])
                require(f["state_digest"]==digest(fp),"FIELD_DIGEST_INVALID")
                count=sum(len(t.frame.values) for t in event.field_payload.timed_frames)
                receipt=dict(schema=ng.field.S2LO_SCHEMA,branch="FIELD",input_digest=event.field_projection_digest,
                    prestate_digest=prior["field"]["state_digest"],poststate_digest=f["state_digest"],
                    source_event_count=len(event.field_payload.timed_frames),contact_count=count)
                require(step["field_receipt_digest"]==digest(receipt),"FIELD_RECEIPT_INVALID")
                contacts+=count
            else:
                require(step["perception_status"]=="FIELD_CONTACT_FAILED" and "FIELD_BRANCH_FAILED" in codes
                    and f==prior["field"] and step["field_receipt_digest"] is None,"FIELD_FAILURE_INVALID")
            pre,state=states[prior["memory"]],states[arm["memory"]]
            used.add(state.state_digest)
            if full:
                require(step["context_status"]=="NOT_REQUESTED" and h is None and step["scan_receipt_digest"] is None
                    and step["baseline_receipt_digest"] is None,"FORMATION_SCAN_INVALID")
                if step["memory_status"]=="FORMATION_COMMITTED":
                    source=ng.memory.bind_s2jv_coordinator_input(config=config,source=event.operation_payload)
                    require(state.generation==pre.generation+1 and state.parent_state_digest==pre.state_digest
                        and state.last_input_digest==source.input_digest and s.hash_form(step["memory_receipt_digest"]),"FORMATION_CHAIN_INVALID")
                    for j,(a,b) in enumerate(zip(pre.b4_state.entries,state.b4_state.entries,strict=True)):
                        require((b.occupied and b.values==source.av_values and b.formation_index==state.generation)
                            if j==pre.generation%9 else a==b,"FORMATION_INPUT_INVALID")
                    old.old._ppb_relations(config,pre,state,source)
                    fast_transitions.append(dict(ordinal=n,arm=i,**fast_relation(config,pre,state,source)))
                else:
                    require(step["memory_status"]=="FORMATION_FAILED" and "MEMORY_BRANCH_FAILED" in codes
                        and state==pre and step["memory_receipt_digest"] is None,"FORMATION_FAILURE_INVALID")
            else:
                require(state==pre and step["memory_status"]=="READ_ONLY_UNCHANGED"
                    and step["memory_receipt_digest"] is None,"CUE_MUTATED_MEMORY")
                results=[]
                for role,key,failure in (("PRIMARY","scan_receipt_digest","PRIMARY_SCAN_FAILED"),
                    ("DIRECT_BASELINE","baseline_receipt_digest","BASELINE_SCAN_FAILED")):
                    sk=(i,n,role)
                    if failure in codes:
                        require(sk not in scanmap and step[key] is None,"FAILED_SCAN_INVALID")
                        continue
                    require(sk in scanmap,"SCAN_MISSING")
                    scanned.add(sk)
                    raw=scanmap[sk]
                    require(len(canonical(raw))<=ng.MAX_SCAN_BYTES,"SCAN_SIZE_EXCEEDED")
                    if event.event_type=="PARTIAL_AUDITORY_CUE":
                        result=s.decode_result(raw)
                        require(result.implementation==role and result.view==s.VIEWS[i],"SCAN_ROLE_INVALID")
                        work=run.direct.verify(result,config=config,state=state,cue=event.operation_payload.cue)
                        terms+=work["band_differences"]+work["equality_comparisons"]
                        hyp=run.types.wrap(result,event.operation_payload)
                        expected=None if hyp is None else {**asdict(hyp),"hypothesis_digest":hyp.hypothesis_digest}
                    else:
                        result=old.decode_visual(raw)
                        old.verify_visual(result,config,state,event.operation_payload)
                        terms+=result.resource_ledger.total_value_comparison_count
                        expected=None if result.hypothesis is None else asdict(result.hypothesis)
                    require(step[key]==result.result_digest,"SCAN_RECEIPT_INVALID")
                    results.append((result.decision,expected))
                if len(results)==2:
                    require(canonical(results[0])==canonical(results[1]) and canonical(h)==canonical(results[0][1])
                        and step["context_status"]==("CONTEXT_CANDIDATE_AVAILABLE" if h is not None else results[0][0]),"CONTEXT_BINDING_INVALID")
                else:
                    require(step["context_status"]=="SCAN_FAILED" and h is None,"SCAN_FAILURE_INVALID")
            old.snapshot(post,r["runtime_configs"][i],f,state.state_digest,n,forms,event.event_digest)
            require(post["status"]=="OPEN","EARLY_CLOSE")
            previous[i]=dict(snapshot=post,field=f,memory=state.state_digest)
        require(pair["arms"][0]["field"]==pair["arms"][1]["field"] and pair["arms"][0]["memory"]==pair["arms"][1]["memory"],"SIBLINGS_DIFFER")
        if errors:
            require(n==len(r["pairs"]),"ERROR_CONTINUED")
    require(used==set(states) and scanned==set(scanmap) and terms<=r["limits"]["verification_value_comparisons"],"COMPLETENESS_INVALID")
    require(sum(x["term_count"] for x in fast_transitions)<=r["limits"]["verification_fast_terms"],"FAST_VERIFICATION_LIMIT")
    require(r["status"]==("NOT_EVALUABLE" if errors else "RECORDING_COMPLETE"),"STATUS_INVALID")
    for i,final in enumerate(r["final"]):
        expected=ng.sealed({**{k:v for k,v in previous[i]["snapshot"].items() if k!="snapshot_digest"},"status":"CLOSED"},"snapshot_digest")
        require(final==expected,"CLOSE_INVALID")
    require(digest(r)==before,"RECORD_MUTATED")
    return ng.sealed(dict(status=r["status"],record_digest=r["record_digest"],read_only=True,
        baseline_equal=True,sibling_states_equal=True,events=len(r["pairs"]),scan_receipts=len(scanned),
        field_contacts=contacts,verification_value_comparisons=terms,
        fast_transitions=fast_transitions,
        input_validations=2*len(inputs),state_decodes=len(states),formation_relations=2*forms),"verification_digest")
