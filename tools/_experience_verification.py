"""Independent read-only transition/scan verification, with explicit time positions."""
from dataclasses import asdict, replace
from tools import _experience_comparison as c

b, r, old = c.b, c.r, c.old
ngv, fv = old.ngv, old.fv


def verify_arm(core, manifest):
    before = b.digest(core)
    old.check(core,"record_digest")
    config = r.nn.profile.build_config()
    b.core_sizes(core)
    events = tuple(ngv.decode_input(x,config) for x in core["inputs"])
    c.need(len(events)==len(core["rows"])==len(core["source_receipts"])==len(manifest.events),"ARM_COMPLETENESS")
    binding = r.ng.build_binding(config,"ALL_BANDS_24")
    rc = r.ng.runtime.build_minimal_runtime_config(runtime_id=manifest.run_id,max_event_count=len(events),
        source_binding_digest=manifest.manifest_digest,component_binding_digest=binding.binding_digest)
    c.need(core["runtime_config"]==asdict(rc) and b.canonical(core["binding"])==b.canonical(asdict(binding))
           and core["config_digest"]==config.config_digest and core["main_gate"] is False,"ARM_BINDING_INVALID")
    states = {h:fv.old.decode_state(b.state_wire.decode(s),config) for h,s in core["states"].items()}
    c.need(all(h==s.state_digest for h,s in states.items()),"STATE_DIGEST_INVALID")
    prior = core["initial"]
    initial = states[prior["memory"]]
    c.need(initial==r.memory.initial_s2jv_composite_state(config) and prior["field"]["step_count"]==0
           and prior["field"]["last_end_tick"]==0,"INITIAL_STATE_INVALID")
    ngv.snapshot(prior["snapshot"],asdict(rc),prior["field"],initial.state_digest,0,0,None)
    scans = {(s["ordinal"],s["role"]):s["value"] for s in core["scans"]}
    c.need(len(scans)==len(core["scans"]),"SCAN_DUPLICATE")
    births, chain = [None]*24,b.digest(dict(initial=initial.state_digest,config=config.config_digest))
    work = {k:0 for k in r.WORK_LIMITS}
    work["state_validation_passes"] = len(states)
    contacts = forms = comparisons = 0
    used, checked = {initial.state_digest},set()
    transitions = []
    for i,(e,row,spec,g,src) in enumerate(zip(events,core["rows"],manifest.events,manifest.positions,core["source_receipts"],strict=True),1):
        c.need((e.event_id,e.ordinal,e.event_type)==(spec.event_id,i,spec.kind),"EVENT_POSITION_INVALID")
        times = b.expected_times(g,spec.kind)
        c.need(e.field_payload.start_tick==(0 if i==1 else times["field_window"][0])
               and e.field_payload.end_tick==times["field_window"][1],"GLOBAL_TIME_INVALID")
        # Only a source-validation view: the actual stored event/digest is checked
        # above and below; historical source validation retains its exact grammar.
        time_view = replace(e,ordinal=g,field_payload=replace(e.field_payload,start_tick=times["field_window"][0]))
        old.source_receipt(src,time_view,config)
        c.need(row["pre"]==prior["snapshot"],"CONTINUATION_INVALID")
        step, post, field = row["step"],row["post"],row["field"]
        payload = {k:v for k,v in step.items() if k not in ("step_digest","hypothesis")}
        payload["hypothesis_digest"] = None if step["hypothesis"] is None else step["hypothesis"]["hypothesis_digest"]
        c.need(step["step_digest"]==b.digest(payload) and step["event_digest"]==e.event_digest
               and step["prestate_digest"]==row["pre"]["snapshot_digest"]
               and step["poststate_digest"]==post["snapshot_digest"] and not step["error_codes"],"STEP_INVALID")
        count = sum(len(t.frame.values) for t in e.field_payload.timed_frames)
        c.need(step["perception_status"]=="FIELD_CONTACT_RECORDED" and field["phase"]=="COMPLETED"
               and field["step_count"]==prior["field"]["step_count"]+1
               and field["last_end_tick"]==e.field_payload.end_tick,"FIELD_PROGRESS_INVALID")
        fp = dict(schema=r.ng.field.S2LO_SCHEMA,phase=field["phase"],field_component_digest=field["field_component_digest"],
                  last_end_tick=field["last_end_tick"],step_count=field["step_count"])
        fr = dict(schema=r.ng.field.S2LO_SCHEMA,branch="FIELD",input_digest=e.field_projection_digest,
                  prestate_digest=prior["field"]["state_digest"],poststate_digest=field["state_digest"],
                  source_event_count=len(e.field_payload.timed_frames),contact_count=count)
        c.need(field["state_digest"]==b.digest(fp) and step["field_receipt_digest"]==b.digest(fr),"FIELD_BINDING_INVALID")
        contacts += count
        pre, state = states[prior["memory"]], states[row["memory"]]
        used.add(state.state_digest)
        if spec.kind==b.AV:
            forms += 1
            c.need(step["memory_status"]=="FORMATION_COMMITTED","FORMATION_MISSING")
            bound = r.memory.bind_s2jv_coordinator_input(config=config,source=e.operation_payload)
            context = r.formation_context(config,pre,state,bound,e,manifest.run_id,row["formation"]["result_digest"])
            form, owner = r.unpack_formation(row["formation"],context)
            tr = fv._formation(dict(spec=dict(event_id=e.event_id),formation=form,owner_before=owner),
                               pre,state,bound,config,manifest.run_id,work)
            c.need(form["receipt"]["receipt_digest"]==step["memory_receipt_digest"],"FORMATION_LINK_INVALID")
            gen = old.generations(pre,state,births,e,form["result_digest"],chain,tr,form["receipt"])
            c.need(gen==row["generations"],"GENERATION_INVALID")
            births, chain = gen["births"],gen["chain_digest"]
            transitions.append(dict(ordinal=i,selection=tr["fast_rank"]["selected_slot_id"],ppb=tr["ppb"]))
        else:
            c.need(state==pre and row["formation"] is None and row["generations"] is None
                   and step["memory_status"]=="READ_ONLY_UNCHANGED" and step["memory_receipt_digest"] is None,"READONLY_INVALID")
            results = []
            for role,key in (("PRIMARY","scan_receipt_digest"),("DIRECT_BASELINE","baseline_receipt_digest")):
                index = (i,role)
                c.need(index in scans,"SCAN_MISSING")
                checked.add(index)
                if spec.kind==b.A:
                    arm = fv.old.decode_arm(scans[index])
                    c.need(arm.rule=="ALL_BANDS_24" and arm.implementation==role,"RULE_INVALID")
                    r.ng.direct.verify_arm(arm=arm,config=config,state=state,cue=e.operation_payload.cue,band_plan=e.operation_payload.band_plan)
                    value, digest = arm.evidence,arm.arm_digest
                else:
                    value = ngv.decode_visual(scans[index])
                    ngv.verify_visual(value,config,state,e.operation_payload)
                    digest = value.result_digest
                c.need(step[key]==digest,"SCAN_LINK_INVALID")
                comparisons += value.resource_ledger.total_value_comparison_count
                work["state_validation_passes"] += 4
                results.append(value)
            a,d = results
            h = None if a.hypothesis is None else asdict(a.hypothesis)
            c.need(a.decision==d.decision and b.canonical(h)==b.canonical(None if d.hypothesis is None else asdict(d.hypothesis))
                   and b.canonical(step["hypothesis"])==b.canonical(h)
                   and step["context_status"]==("CONTEXT_CANDIDATE_AVAILABLE" if h is not None else a.decision),"BASELINE_INVALID")
        c.need(row["current_births"]==births and row["chain_digest"]==chain,"CURRENT_GENERATION_INVALID")
        ngv.snapshot(post,asdict(rc),field,state.state_digest,i,forms,e.event_digest)
        c.need(post["status"]=="OPEN","CLOSED_EARLY")
        prior = dict(snapshot=post,field=field,memory=state.state_digest)
    c.need(checked==set(scans) and used==set(states) and comparisons<=11712
           and all(work[k]<=r.WORK_LIMITS[k] for k in work),"WORK_OR_COMPLETENESS_INVALID")
    expected = b.sealed({**{k:v for k,v in prior["snapshot"].items() if k!="snapshot_digest"},"status":"CLOSED"},"snapshot_digest")
    c.need(core["final"]==expected and core["status"]=="RECORDING_COMPLETE" and b.digest(core)==before,"CLOSE_INVALID")
    return dict(contacts=contacts,formations=forms,scans=len(checked),work=work,
                comparisons=comparisons,transitions=transitions)


def verify(record):
    before = b.digest(record)
    old.check(record,"record_digest")
    c.need(record["version"]==c.VERSION and record["profile"]==c.PROFILE and record["main_gate"] is False,"PROFILE_INVALID")
    c.need(record["status"]=="RECORDING_COMPLETE" and record["failure"] is None,"INCOMPLETE")
    manifest = c.p.decode(record["manifest"])
    c.need(record["mode"] in ("NEUTRAL","MEDIA"),"MODE_INVALID")
    if record["mode"]=="MEDIA":
        material=record["materialization"]
        c.need(material["counts"]==dict(payloads=44,audio=22,nj=22,visual=22,materialized_events=24)
               and len(material["receipts"])==24,"MATERIALIZATION_COUNTS_INVALID")
        for event,receipt,src in zip(manifest.events,material["receipts"],record["arms"]["experienced"]["source_receipts"],strict=True):
            expected=c.p.selection_receipt(manifest,event,receipt["frame_pts"],receipt["next_frame_pts"],
                None if src["nj"] is None else src["nj"]["pcm_digest"],src["rgb_digest"])
            c.need(receipt==expected,"MEDIA_SELECTION_INVALID")
        c.need(material["decoder"]["selected_windows"]==20 and material["decoder"]["passes"]==2
               and material["decoder"]["container_read_bytes"]<=12*manifest.source.size,"DECODER_WORK_INVALID")
    else:
        c.need(record["materialization"] is None,"NEUTRAL_MEDIA_INVALID")
    c.need(set(record["arms"])=={"experienced","fresh"},"ARMS_INVALID")
    proofs = {name:verify_arm(core,c.arm_manifest(manifest,name)) for name,core in record["arms"].items()}
    left,right = record["arms"]["experienced"],record["arms"]["fresh"]
    for i in range(14):
        a,z = left["inputs"][i+10],right["inputs"][i]
        c.need(a["operation"]==z["operation"] and a["field"]["timed_frames"]==z["field"]["timed_frames"]
               and left["source_receipts"][i+10]==right["source_receipts"][i],"CURRENT_INPUTS_DIFFER")
    for key in ("contacts","formations","scans"):
        c.need(sum(x[key] for x in proofs.values())==c.EXPECTED[key],"TOTAL_COUNTS_INVALID")
    c.need(b.digest(record)==before,"VERIFICATION_MUTATED")
    proof = b.sealed(dict(version=c.VERSION,record_digest=record["record_digest"],read_only=True,
        evaluation_allowed=True,arms=proofs,boundary="Native transitions and scans checked; field trajectory and receptor values not replayed."),"verification_digest")
    # Two retained proofs (neutral qualification and future real run) share
    # the one 262144-byte comparison allowance.
    c.need(len(b.canonical(proof))<=131072,"PROOF_LIMIT")
    return proof
