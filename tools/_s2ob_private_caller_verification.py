"""Caller-only technical closure. No payload reads, field advances or retrieval repeats."""
from dataclasses import asdict
import json
from tools import _s2ob_private_caller_binding as b
from tools import _s2oa_private_runtime_verification as prior
from tools import _s2ng_private_comparison_verification as ngv
from tools import _s2nq_private_verification as fv

r = b.r
check, generations = prior.check, prior.generations

def source_receipt(value,event,config):
    r.require(set(value)=={"nj","rgb_digest","source_digest"},"SOURCE_FORM_INVALID")
    frames={x.frame.modality_id:x for x in event.field_payload.timed_frames}
    g=event.ordinal-1
    r.require(event.field_payload.start_tick==(0 if g==0 else 200000000*g-100000000)
              and event.field_payload.end_tick==200000000*g+100000000,"FIELD_TIME_INVALID")
    for modality,t in frames.items():
        start=200000000*g if modality=="auditory" else (6*g+2)*1000000000//30
        r.require(t.field_time==r.nn.CommonFieldTime(b.CLOCK,start,200000000*g+100000000),"MODALITY_TIME_INVALID")
    if "auditory" in frames:
        t=frames["auditory"].frame; n=value["nj"]
        r.require(type(n) is dict and set(n)=={"source_state_digest","source_values_digest","projection_digest",
            "subnormal_band_indices","underflow_band_indices","pcm_digest"},"NJ_FORM_INVALID")
        p=r.half.HalfScaleAuditory48V1(r.half.PROFILE_ID,r.half.PROFILE_DIGEST,r.half.GEOMETRY,r.half.RAW_PROFILE_DIGEST,
            n["source_state_digest"],n["source_values_digest"],20*g,"audio.sample",9600*g,9600*g+4800,
            t.carrier_ids,t.values,tuple(n["subnormal_band_indices"]),tuple(n["underflow_band_indices"]),n["projection_digest"])
        r.require(t.snapshot_id=="half."+p.projection_digest and (t.window_start_tick,t.window_end_tick)==(9600*g,9600*g+4800),"NJ_FRAME_INVALID")
        op=event.operation_payload
        pcm=op.plan.auditory_payload_digest if event.event_type=="COMPLETE_AV_PERCEPTION" else op.cue.pcm_payload_digest
        r.require(pcm==n["pcm_digest"],"PCM_BINDING_INVALID")
    else:
        r.require(value["nj"] is None,"UNEXPECTED_NJ")
    if "visual" in frames:
        t=frames["visual"].frame
        r.require((t.window_start_tick,t.window_end_tick)==(6*g+2,6*g+3),"VISUAL_TIME_INVALID")
        op=event.operation_payload
        rgb=op.plan.visual_payload_digest if event.event_type=="COMPLETE_AV_PERCEPTION" else op.source_digest
        r.require(rgb==value["rgb_digest"],"RGB_BINDING_INVALID")
        if event.event_type=="PARTIAL_VISUAL_CUE":
            r.require(all(t.values[i]==0.0 for i in range(32,288)),"CUE_NOT_OCCLUDED")
    else:
        r.require(value["rgb_digest"] is None,"UNEXPECTED_RGB")
    r.require(value["source_digest"]==event.source_digest==r.digest(dict(schema=b.SCHEMA,nj=value["nj"],
        rgb_digest=value["rgb_digest"],profile=r.half.PROFILE_DIGEST)),"SOURCE_DIGEST_INVALID")


def verify_core(x,config,manifest):
    before=r.digest(x);check(x,"record_digest");r.nn.validate_config(config)
    r.require(x["schema"]==b.SCHEMA and x["main_gate"] is False,"RECORD_BINDING_INVALID")
    sizes=b.core_sizes(x)
    events=tuple(ngv.decode_input(p,config) for p in x["inputs"])
    r.require([e.ordinal for e in events]==list(range(1,len(events)+1)) and len(events)==len(x["source_receipts"]),"INPUT_ORDER_INVALID")
    for e,s in zip(events,x["source_receipts"],strict=True):source_receipt(s,e,config)
    binding=r.ng.build_binding(config,"ALL_BANDS_24")
    rc=r.ng.runtime.build_minimal_runtime_config(runtime_id=x["run_id"],max_event_count=len(manifest.events),
        source_binding_digest=manifest.manifest_digest,component_binding_digest=binding.binding_digest)
    r.require(x["config_digest"]==config.config_digest and r.canonical(x["binding"])==r.canonical(asdict(binding))
              and x["runtime_config"]==asdict(rc),"CONFIGURATION_INVALID")
    states={h:fv.old.decode_state(s,config) for h,s in x["states"].items()}
    r.require(all(h==s.state_digest for h,s in states.items()),"STATE_KEY_INVALID")
    prior=x["initial"]; initial=states[prior["memory"]]
    r.require(initial.generation==0 and all(not s.occupied for _,s in r.slots(initial))
              and prior["field"]["step_count"]==0 and prior["field"]["last_end_tick"]==0,"INITIAL_INVALID")
    ngv.snapshot(prior["snapshot"],asdict(rc),prior["field"],initial.state_digest,0,0,None)
    scans={(z["ordinal"],z["role"]):z["value"] for z in x["scans"]}
    r.require(len(scans)==len(x["scans"]),"SCAN_DUPLICATE")
    used={initial.state_digest}; checked=set(); births=[None]*24
    chain=r.digest(dict(initial=initial.state_digest,config=config.config_digest))
    work={k:0 for k in r.WORK_LIMITS}; work["state_validation_passes"]=len(states)
    trans=[]; contacts=0; comparisons=0; forms=0; errors=[]
    r.require(len(x["rows"])<=len(events) and (x["status"]!="RECORDING_COMPLETE" or len(x["rows"])==len(events)),"EVENT_COMPLETENESS_INVALID")
    for i,row in enumerate(x["rows"]):
        e=events[i]; n=i+1; full=e.event_type=="COMPLETE_AV_PERCEPTION"; forms+=int(full)
        r.require(row["pre"]==prior["snapshot"],"CONTINUATION_INVALID")
        step=row["step"]; post=row["post"]; field=row["field"]
        payload={k:v for k,v in step.items() if k not in ("step_digest","hypothesis")}
        payload["hypothesis_digest"]=None if step["hypothesis"] is None else step["hypothesis"]["hypothesis_digest"]
        r.require(step["step_digest"]==r.digest(payload) and step["event_digest"]==e.event_digest
            and step["prestate_digest"]==row["pre"]["snapshot_digest"] and step["poststate_digest"]==post["snapshot_digest"],"STEP_INVALID")
        errors.extend(step["error_codes"])
        if step["perception_status"]=="FIELD_CONTACT_RECORDED":
            count=sum(len(t.frame.values) for t in e.field_payload.timed_frames)
            r.require(field["phase"]=="COMPLETED" and field["step_count"]==prior["field"]["step_count"]+1
                and field["last_end_tick"]==e.field_payload.end_tick,"FIELD_PROGRESS_INVALID")
            fp=dict(schema=r.ng.field.S2LO_SCHEMA,phase=field["phase"],field_component_digest=field["field_component_digest"],
                    last_end_tick=field["last_end_tick"],step_count=field["step_count"])
            fr=dict(schema=r.ng.field.S2LO_SCHEMA,branch="FIELD",input_digest=e.field_projection_digest,
                prestate_digest=prior["field"]["state_digest"],poststate_digest=field["state_digest"],
                source_event_count=len(e.field_payload.timed_frames),contact_count=count)
            r.require(field["state_digest"]==r.digest(fp) and step["field_receipt_digest"]==r.digest(fr),"FIELD_RECEIPT_INVALID")
            contacts+=count
        else:
            r.require("FIELD_BRANCH_FAILED" in step["error_codes"] and field==prior["field"] and step["field_receipt_digest"] is None,"FIELD_FAILURE_INVALID")
        pre,st=states[prior["memory"]],states[row["memory"]]; used.add(st.state_digest)
        if full and step["memory_status"]=="FORMATION_COMMITTED":
            bound=r.memory.bind_s2jv_coordinator_input(config=config,source=e.operation_payload)
            context=r.formation_context(config,pre,st,bound,e,x["run_id"],row["formation"]["result_digest"])
            form,owner=r.unpack_formation(row["formation"],context)
            tr=fv._formation(dict(spec=dict(event_id=e.event_id),formation=form,owner_before=owner),pre,st,bound,config,x["run_id"],work)
            r.require(form["receipt"]["receipt_digest"]==step["memory_receipt_digest"],"RECEIPT_LINK_INVALID")
            gen=generations(pre,st,births,e,form["result_digest"],chain,tr,form["receipt"])
            r.require(row["generations"]==gen,"GENERATION_CHAIN_INVALID")
            births,chain=gen["births"],gen["chain_digest"]
            # No full rank term tables in the proof: preserve their digest, selected slot and PPB findings.
            trans.append(dict(event=n,fast_selected=tr["fast_rank"]["selected_slot_id"],
                fast_rank_digest=r.digest(tr["fast_rank"]),ppb=tr["ppb"],generations=gen))
        elif full:
            r.require("MEMORY_BRANCH_FAILED" in step["error_codes"] and st==pre and row["formation"] is None
                and row["generations"] is None and step["memory_receipt_digest"] is None,"ATOMIC_FAILURE_INVALID")
        else:
            r.require(st==pre and row["formation"] is None and row["generations"] is None
                and step["memory_status"]=="READ_ONLY_UNCHANGED" and step["memory_receipt_digest"] is None,"CUE_MUTATED_MEMORY")
            results=[]
            for role,key,failure in (("PRIMARY","scan_receipt_digest","PRIMARY_SCAN_FAILED"),
                                     ("DIRECT_BASELINE","baseline_receipt_digest","BASELINE_SCAN_FAILED")):
                index=(n,role)
                if failure in step["error_codes"]:
                    r.require(index not in scans and step[key] is None,"SCAN_FAILURE_INVALID");continue
                r.require(index in scans,"SCAN_MISSING"); checked.add(index)
                if e.event_type=="PARTIAL_AUDITORY_CUE":
                    arm=fv.old.decode_arm(scans[index])
                    r.require(arm.rule=="ALL_BANDS_24" and arm.implementation==role,"AUDIO_RULE_INVALID")
                    r.ng.direct.verify_arm(arm=arm,config=config,state=st,cue=e.operation_payload.cue,band_plan=e.operation_payload.band_plan)
                    value=arm.evidence; rh=arm.arm_digest
                else:
                    value=ngv.decode_visual(scans[index]);ngv.verify_visual(value,config,st,e.operation_payload);rh=value.result_digest
                r.require(step[key]==rh,"SCAN_LINK_INVALID");results.append(value)
                work["state_validation_passes"]+=4
                comparisons+=value.resource_ledger.total_value_comparison_count
            if len(results)==2:
                a,b=results
                h=None if a.hypothesis is None else asdict(a.hypothesis)
                r.require(a.decision==b.decision and r.canonical(h)==r.canonical(None if b.hypothesis is None else asdict(b.hypothesis))
                    and r.canonical(step["hypothesis"])==r.canonical(h)
                    and step["context_status"]==("CONTEXT_CANDIDATE_AVAILABLE" if h is not None else a.decision),"BASELINE_INVALID")
            else:r.require(step["context_status"]=="SCAN_FAILED" and step["hypothesis"] is None,"SCAN_FAILURE_INVALID")
        r.require(row["current_births"]==births and row["chain_digest"]==chain,"CURRENT_GENERATION_INVALID")
        ngv.snapshot(post,asdict(rc),field,st.state_digest,n,forms,e.event_digest)
        r.require(post["status"]=="OPEN","CLOSED_EARLY")
        prior=dict(snapshot=post,field=field,memory=st.state_digest)
        if errors:r.require(i==len(x["rows"])-1,"ERROR_CONTINUED")
    r.require(checked==set(scans) and used==set(states) and comparisons<=11712,"EVIDENCE_COMPLETENESS_INVALID")
    r.require(all(work[k]<=r.WORK_LIMITS[k] for k in work),"VERIFICATION_BUDGET_INVALID")
    r.require(bool(errors)==(x["status"]=="NOT_EVALUABLE"),"STATUS_INVALID")
    expected=r.sealed({**{k:v for k,v in prior["snapshot"].items() if k!="snapshot_digest"},"status":"CLOSED"},"snapshot_digest")
    r.require(x["final"]==expected and r.digest(x)==before,"CLOSE_OR_MUTATION_INVALID")
    proof=r.sealed(dict(status=x["status"],record_digest=x["record_digest"],read_only=True,evaluation_allowed=not errors,
        field_contacts=contacts,transitions=trans,verification_work=work,scan_comparisons=comparisons,
        source_bindings=len(events),generation_slot_checks=24*len(trans),
        scan_receipts=len(checked),sizes=sizes,baseline_equal=True,
        boundary="Stored states, inputs, receipts and generation changes independently checked. Field trajectory and raw-to-half numerics not rerun."),"verification_digest")
    r.require(len(r.canonical(proof))<=262144,"PROOF_LIMIT")
    return proof


def verify(value, manifest, references):
    before=b.digest(value)
    try:
        expected=b.validate_manifest(manifest)
        b.check_root(value,"record_digest")
        b.require(value["schema"]==b.SCHEMA and value["run_id"]==manifest.run_id
            and value["manifest"]==json.loads(b.canonical(asdict(manifest)))
            and value["code_digest"]==manifest.code_digest
            and value["main_gate"] is False and value["evaluation"] is None, "TOTAL_BINDING_INVALID")
        b.require(b.canonical(value["references"])==b.canonical(references), "REFERENCES_INVALID")
        sizes=b.enforce(b.balance(value,references))
        x=value["execution"]
        if x is None:
            f=value["failure"]
            b.require(value["status"]=="NOT_EVALUABLE" and f["phase"] in b.PHASES
                and type(f["completed_events"]) is int and 0<=f["completed_events"]<=expected["events"]
                and (f["ordinal"] is None or type(f["ordinal"]) is int and 1<=f["ordinal"]<=expected["events"])
                and type(f["code"]) is str, "FAILURE_INVALID")
            if f["final"] is None:
                b.require(f["completed_events"]==0 and f["last_snapshot_digest"] is None,"FAILURE_PROGRESS_INVALID")
            else:
                b.check_root(f["final"],"snapshot_digest")
                b.require(f["final"]["status"]=="CLOSED" and f["final"]["processed_event_count"]==f["completed_events"]
                    and f["final"]["snapshot_digest"]==f["last_snapshot_digest"],"FAILURE_PROGRESS_INVALID")
            return b.sealed(dict(status="NOT_EVALUABLE",evaluation_allowed=False,record_digest=value["record_digest"],
                boundary="Typed failure and progress bindings only; no functional partial evaluation.",sizes=sizes),"verification_digest")
        config=r.nn.profile.build_config()
        b.require(len(x["inputs"])==len(x["source_receipts"])==len(x["rows"]),"EVENT_COMPLETENESS_INVALID")
        b.require(len(x["inputs"])<=len(manifest.events),"EVENT_COMPLETENESS_INVALID")
        for e,p,s in zip(manifest.events[:len(x["inputs"])],x["inputs"],x["source_receipts"],strict=True):
            b.require((p["event"]["event_id"],p["event"]["ordinal"],p["event"]["event_type"])==
                (e.event_id,e.ordinal,e.kind),"EVENT_BINDING_INVALID")
            b.require(s["rgb_digest"]==(None if e.rgb is None else e.rgb.sha256)
                and (None if s["nj"] is None else s["nj"]["pcm_digest"])==(None if e.pcm is None else e.pcm.sha256),"SOURCE_BINDING_INVALID")
        # The independent historical transition calculations do not advance owners.
        proof=verify_core(x,config,manifest)
        b.require(value["status"]==x["status"],"STATUS_INVALID")
        if value["status"]=="RECORDING_COMPLETE":
            b.require(len(x["rows"])==expected["events"] and proof["field_contacts"]==expected["contacts"]
                and proof["scan_receipts"]==expected["scans"] and len(proof["transitions"])==expected["formations"],"COUNTS_INVALID")
            b.require(value["counts"]==dict(payloads=expected["payloads"],audio=expected["audio"],nj=expected["nj"],
                visual=expected["visual"],materialized_events=expected["events"]) and value["failure"] is None,"COUNTS_INVALID")
        else:
            b.require(value["failure"]==x["failure"] and bool(x["failure"]),"FAILURE_INVALID")
        b.require(before==b.digest(value),"VERIFICATION_MUTATED")
        out=b.sealed(dict(status=value["status"],record_digest=value["record_digest"],evaluation_allowed=proof["evaluation_allowed"],
            read_only=True,core=proof,sizes=sizes,
            boundary="No PCM/RGB, FFT, NJ, field or memory execution. Raw-to-half numerics and raw visual provenance remain digest bindings, not numerical replay."),"verification_digest")
        b.require(len(b.canonical(out))<=b.LIMITS["verification"],"PROOF_LIMIT")
        return out
    except b.S2OBError:
        raise
    except (r.memory.S2JWCoordinatorError,r.memory.tspm1.TSPM1Error) as exc:
        raise b.S2OBError("STATE_BINDING_INVALID") from exc
    except r.S2OAError as exc:
        raise b.S2OBError(exc.code) from exc
    except (ValueError,KeyError,TypeError,IndexError,AttributeError,StopIteration) as exc:
        raise b.S2OBError("EVIDENCE_BINDING_INVALID") from exc


def verify_once(directory):
    path=b.Path(directory)
    claim=path/"verification.claim"
    with claim.open("xb") as f: f.write(b"once")
    raw=(path/"record.json").read_bytes(); value=json.loads(raw)
    m=b.decode_manifest(value["manifest"])
    inventory=b.code_inventory()
    b.require(m.code_digest==b.digest(inventory),"CODE_BINDING_INVALID")
    refs=b.qualified_references(inventory) if value["mode"]=="CALLER" else (
        ("sources",b.OWN[0]+":neutral-inventory",len(b.canonical(inventory))),)
    proof=verify(value,m,refs)
    b.require(raw==(path/"record.json").read_bytes(),"RECORD_CHANGED")
    b.enforce(b.balance(value,refs,proof_bytes=len(b.canonical(proof))+4))
    r.ng.ne.atomic_write(path/"verification.json",proof,b.LIMITS["verification"]-4)
    return proof
