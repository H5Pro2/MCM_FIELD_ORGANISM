"""Independent offline whole-record verification, separately charged arithmetic."""
from dataclasses import asdict
import json
import math
from pathlib import Path

from tools import _s2nq_private_run as run
from tools import _s2ne_private_run_verification as old
from tools import _s2nl_private_rank_verification as rank

s, src, io, memory = run.s, run.sources, run.io, run.memory


def check(p, key):
    s.require(type(p) is dict and key in p and p[key] == s.digest({k:v for k,v in p.items() if k != key}), "DIGEST_INVALID")


def _formation(e, pre, post, bound, config, run_id, budget):
    d = e["formation"]
    receipt = memory.S2JVFormationReceiptV1(**d["receipt"])
    ledger = old.ledgers.S2JVResourceLedgerV1(**d["ledger"])
    prior = memory.S2JVFormationOwnerSnapshotV1(**e["owner_before"])
    owner = memory.S2JVFormationOwnerSnapshotV1(**d["owner_poststate"])
    result = memory.S2JVFormationResultV1(post,receipt,ledger,owner,d["result_digest"],d["schema"])
    for obj, key in ((receipt,"receipt_digest"),(prior,"owner_state_digest"),(owner,"owner_state_digest")):
        s.require(getattr(obj,key) == s.digest(obj.payload_without_digest()) and obj.schema == memory.S2JW_COORDINATOR_SCHEMA, "FORMATION_RECEIPT_INVALID")
    # The existing owner/receipt envelope is historical; its config digest binds the half profile.
    s.require(result.schema == memory.S2JW_COORDINATOR_SCHEMA and result.result_digest == s.digest(result.payload_without_digest()), "FORMATION_RESULT_INVALID")
    s.require((prior.status,prior.attempt_count,prior.use_count,prior.committed_result_digest,prior.failure_code)
              == ("AUTHORIZED",0,0,None,None) and
              (owner.status,owner.attempt_count,owner.use_count,owner.committed_result_digest,owner.failure_code)
              == ("CONSUMED",1,1,result.result_digest,None), "OWNER_LIFECYCLE_INVALID")
    for o in (prior,owner):
        s.require((o.owner_id,o.authorization_id,o.consumption_id,o.authorized_config_digest,
                   o.authorized_prestate_digest,o.authorized_input_digest) ==
            (e["spec"]["event_id"]+"-owner",run_id,e["spec"]["event_id"]+"-consume",config.config_digest,
             pre.state_digest,bound.input_digest), "OWNER_BINDING_INVALID")
    s.require((receipt.config_digest,receipt.input_digest,receipt.owner_prestate_digest,
        receipt.composite_prestate_digest,receipt.composite_poststate_digest,receipt.b4_poststate_digest,
        receipt.tspm_poststate_digest,receipt.ledger_digest) ==
        (config.config_digest,bound.input_digest,prior.owner_state_digest,pre.state_digest,post.state_digest,
         memory._b4_digest(post.b4_state),post.tspm_state.composite_state_digest,ledger.ledger_digest), "FORMATION_BINDING_INVALID")
    s.require(s.hash_form(receipt.tspm_result_digest), "NATIVE_RECEIPT_BINDING_INVALID")
    s.require(post.generation == pre.generation+1 and post.parent_state_digest == pre.state_digest
              and post.last_input_digest == bound.input_digest
              and post.tspm_state.parent_composite_state_digest == pre.tspm_state.composite_state_digest
              and post.tspm_state.last_exposure_digest == bound.tspm_exposure.exposure_digest, "FORMATION_CHAIN_INVALID")
    relation = s.digest(dict(schema=memory.S2JW_COORDINATOR_SCHEMA,prestate_digest=pre.state_digest,input_digest=bound.input_digest,
        b4_poststate_digest=receipt.b4_poststate_digest,tspm_poststate_digest=receipt.tspm_poststate_digest,
        composite_poststate_digest=post.state_digest))
    expected_ledger = old.ledgers.derive_s2jv_resource_ledger(profile=config.profile,limits=config.ledger_limits,
        operation_id=owner.consumption_id,operation_role="FORMATION",result_digest=relation)
    s.require(expected_ledger == ledger, "FORMATION_LEDGER_INVALID")
    pos = pre.generation % 9
    s.require(receipt.b4_event == ("B4_APPENDED" if pre.generation < 9 else "B4_EVICTED_AND_APPENDED"), "B4_EVENT_INVALID")
    for i,(a,b) in enumerate(zip(pre.b4_state.entries,post.b4_state.entries,strict=True)):
        if i == pos:
            s.require(b.slot_id == receipt.b4_slot_id and b.occupied and b.values == bound.av_values
                      and b.formation_index == post.generation, "B4_FORMATION_INVALID")
        else:
            s.require(a == b,"B4_UNRELATED_CHANGE")
    fast = post.tspm_state.fast_state
    s.require((fast.auditory_source_clock_id,fast.auditory_last_end_tick,fast.visual_source_clock_id,fast.visual_last_end_tick)
              == ("audio.sample",bound.source.auditory.timed_frame.frame.window_end_tick,
                  "video.frame",bound.source.visual.timed_frame.frame.window_end_tick), "FAST_TIME_INVALID")
    evidence = rank.direct_scan(config,pre,bound,mode="FAST_FORMATION")
    budget["fast_rank_terms"] += evidence.term_count
    slots = pre.tspm_state.fast_state.slots
    fc = config.tspm_config.fast_config
    if evidence.selected_slot_id is not None:
        selected_id = evidence.selected_slot_id
    else:
        free = [x for x in slots if not x.occupied or post.generation-x.last_selected_step >= fc.expire_after_exposures]
        selected_id = (min(free,key=lambda x:x.slot_id) if free else min(slots,key=lambda x:(x.last_selected_step,x.slot_id))).slot_id
    selected = None
    for a,b in zip(slots,fast.slots,strict=True):
        if b.slot_id == selected_id:
            selected = b
            s.require(b.occupied and b.last_selected_step == post.generation,"FAST_SELECTED_INVALID")
            if evidence.selected_slot_id is None:
                s.require(b.auditory_values+b.visual_values == bound.av_values and b.support_count == 1
                          and b.consolidation_count == 0 and b.last_consolidation_exposure_digest is None,"FAST_CREATED_INVALID")
            else:
                expected = tuple((1.0-fc.update_factor)*x+fc.update_factor*y
                                 for x,y in zip(a.auditory_values+a.visual_values,bound.av_values,strict=True))
                s.require(tuple(x.hex() for x in b.auditory_values+b.visual_values) == tuple(x.hex() for x in expected)
                          and b.support_count == min(fc.consolidate_after,a.support_count+1)
                          and b.consolidation_count == a.consolidation_count+1
                          and b.last_consolidation_exposure_digest == bound.tspm_exposure.exposure_digest,"FAST_UPDATE_INVALID")
        else:
            expired = a.occupied and post.generation-a.last_selected_step >= fc.expire_after_exposures
            s.require(b == (old.tspm.TSPM1FastSlot.free(a.slot_id) if expired else a),"FAST_UNRELATED_CHANGE")
    transitions = old._ppb_relations(config,pre,post,bound)
    for transition in transitions:
        transition.pop("masked_digest",None)  # Historical complement is not the distributed mask.
    s.require((transitions[0]["event"] != "NO_UPDATE") == (selected.support_count >= fc.consolidate_after),"PPB_TRIGGER_INVALID")
    # Independent PPB choice, not just validation of the changed slot's values.
    for modality, transition in zip(("auditory","visual"),transitions,strict=True):
        if transition["event"] == "NO_UPDATE":
            continue
        bank = getattr(pre.tspm_state,modality+"_ppb1_state")
        bc = getattr(config.profile.profile,modality+"_config")
        incoming = getattr(bound,modality+"_values")
        live = [x for x in bank.slots if x.occupied and bank.accepted_step_count+1-x.last_selected_step < bc.expire_after_steps]
        matches = []
        for slot in live:
            distance = math.fsum(abs(x-y) for x,y in zip(incoming,slot.prototype_values,strict=True))/len(incoming)
            budget["ppb_selection_terms"] += len(incoming)
            if distance <= bc.match_threshold:
                matches.append((distance,slot.slot_id))
        if matches:
            chosen = min(matches)[1]
        else:
            free = [x for x in bank.slots if x not in live]
            chosen = (min(free,key=lambda x:x.slot_id) if free else min(live,key=lambda x:(x.last_selected_step,x.slot_id))).slot_id
        s.require(chosen == transition["slot_id"],"PPB_CHOICE_INVALID")
    budget["formation_checks"] += 1
    budget["state_validation_passes"] += 1
    budget["update_components"] += 672  # Conservative charge, including NO_UPDATE branches.
    return dict(event_id=e["spec"]["event_id"], fast_rank=asdict(evidence), ppb=transitions)


def verify_record(record, *, events, catalog, config):
    try:
        return _verify(record,events,catalog,config)
    except s.S2NQError:
        raise
    except memory.S2JWCoordinatorError as exc:
        raise s.S2NQError("STATE_BINDING_INVALID") from exc
    except (KeyError,TypeError,ValueError,AttributeError,IndexError) as exc:
        raise s.S2NQError("RECORD_BINDING_INVALID") from exc


def _verify(r,events,catalog,config):
    before = s.digest(r)
    s.require(len(s.canonical(r)) <= run.MAX_BYTES,"RECORDING_SIZE_EXCEEDED")
    check(r,"record_digest")
    s.require(r["schema"] == run.SCHEMA and r["mode"] in ("MAIN","NEUTRAL")
              and config == s.profile.build_config(),"PROFILE_INVALID")
    src.validate_plan(events,neutral=r["mode"]=="NEUTRAL")
    s.require(r["plan"] == [asdict(e) for e in events] and r["plan_digest"] == s.digest(r["plan"])
              and r["limits"] == run.LIMITS and r["verification_limits"] == run.VERIFY_LIMITS,"PLAN_BINDING_INVALID")
    s.require(r["run_id"] == Path(r["output_directory"]).name,"RUN_PATH_INVALID")
    if r["status"] == "NOT_EVALUABLE":
        f = r["failure"]
        s.require(type(f) is dict and f["phase"] in run.PHASES and type(f["completed_events"]) is int
                  and 0 <= f["completed_events"] <= len(events),"FAILURE_PROGRESS_INVALID")
        n = f["completed_events"]
        s.require(r["config_digest"]==config.config_digest or
                  r["config_digest"] is None and f["phase"]=="BINDINGS", "PROFILE_INVALID")
        s.require(r["code_after"] == {p:io.filehash(run.ROOT/p) if (run.ROOT/p).is_file() else None
                                    for p in r["code_before"]}, "FAILURE_CODE_BINDING_INVALID")
        s.require(r["events"] == [] and r["states"] == {} and r["initial_states"] == {}
                  and (r["catalog_digest"] == s.digest(catalog) or r["catalog_digest"] is None and f["phase"]=="BINDINGS"),"FAILURE_FORM_INVALID")
        s.require(r["counts"]["events"] == n and r["counts"]["formations"] == sum(e.kind=="FORMATION" for e in events[:n])
                  and r["counts"]["cues"] == sum(e.kind=="CUE" for e in events[:n])
                  and r["counts"]["arms"] == r["counts"]["cues"]*4,"FAILURE_COUNTS_INVALID")
        s.require((f["event_index"] is None and n==0 and f["event_id"] is None) or
                  (type(f["event_index"]) is int and 0<=f["event_index"]<len(events)
                   and f["event_id"]==events[f["event_index"]].event_id and (f["event_index"]==n or n==len(events))),"FAILURE_EVENT_INVALID")
        s.require(f["last_state_digest"] is None or s.hash_form(f["last_state_digest"]),"FAILURE_DIGEST_INVALID")
        s.require(type(f["code"]) is str and s.re.fullmatch(r"[A-Z][A-Z0-9_]{0,95}",f["code"]) is not None,"FAILURE_CODE_INVALID")
        s.require(type(f["error_class"]) is str and s.re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,95}",f["error_class"]) is not None,"FAILURE_CLASS_INVALID")
        s.require(r["counts"]["formations"]<=r["attempts"]["formations"]<=r["counts"]["formations"]+1
                  and r["counts"]["arms"]<=r["attempts"]["arms"]<=r["counts"]["arms"]+4
                  and all(v<=run.LIMITS[k] for k,v in r["counts"].items()),"FAILURE_ATTEMPTS_INVALID")
        return io.sealed(dict(status="NOT_EVALUABLE",record_digest=r["record_digest"],read_only=True),"verification_digest")
    s.require(r["status"]=="RECORDING_COMPLETE" and r["failure"] is None
              and r["catalog_digest"]==s.digest(catalog) and r["config_digest"]==config.config_digest,"TERMINAL_BINDING_INVALID")
    s.require(r["code_before"] == r["code_after"] == run.code_hashes(),"CODE_BINDING_INVALID")
    s.require(len(r["states"]) <= 20 and len(r["events"])==len(events),"RECORD_COUNT_INVALID")
    states = {h:old.decode_state(p,config) for h,p in r["states"].items()}
    s.require(all(h==v.state_digest for h,v in states.items()),"STATE_POOL_INVALID")
    history_ids = set(e.history for e in events)
    s.require(set(r["initial_states"]) == history_ids,"HISTORY_BINDING_INVALID")
    current, used = dict(r["initial_states"]), set(r["initial_states"].values())
    for key in current.values():
        st = states[key]
        s.require(st.generation==0 and st.parent_state_digest is None and st.last_input_digest is None
                  and not any(x.occupied for x in st.b4_state.entries)
                  and not any(x.occupied for x in st.tspm_state.fast_state.slots)
                  and not any(x.occupied for x in st.tspm_state.auditory_ppb1_state.slots)
                  and not any(x.occupied for x in st.tspm_state.visual_ppb1_state.slots),"INITIAL_STATE_INVALID")
    budget = {k:0 for k in run.VERIFY_LIMITS}
    budget.update(state_decodes=len(states),state_validation_passes=len(states),max_input_bytes=len(s.canonical(r)))
    transitions = []
    for spec,e in zip(events,r["events"],strict=True):
        check(e,"event_digest")
        s.require(e["spec"]==asdict(spec) and e["kind"]==spec.kind and e["prestate"]==current[spec.history],"EVENT_CONTINUITY_INVALID")
        pre,post = states[e["prestate"]],states[e["poststate"]]
        used.update((pre.state_digest,post.state_digest))
        bound = src.restore(spec,e["source"],config,catalog)
        budget["source_bindings"]+=1
        budget["source_projection_validation_passes"]+=3
        budget["input_value_checks"]+=48+(288 if spec.kind=="FORMATION" else 0)
        if spec.kind=="FORMATION":
            s.require(e["arms"]==[] and e["cues"]==[],"FORMATION_FORM_INVALID")
            transitions.append(_formation(e,pre,post,bound,config,r["run_id"],budget))
        else:
            s.require(pre==post and e["formation"] is None and e["owner_before"] is None
                      and s.canonical(e["cues"])==s.canonical([asdict(c) for c in bound]),"CUE_READ_ONLY_INVALID")
            s.require(len(e["arms"])==4 and tuple((x["view"],x["implementation"]) for x in e["arms"])==run.ORDER,"ARM_ORDER_INVALID")
            results = [s.decode_result(p) for p in e["arms"]]
            for i,result in enumerate(results):
                charge = run.baseline.verify(result,config=config,state=pre,cue=bound[i//2])
                budget["arm_checks"]+=1
                budget["state_validation_passes"]+=1
                for k,v in charge.items():
                    budget[k]+=v
            s.require(run.baseline.semantics(results[0])==run.baseline.semantics(results[1])
                      and run.baseline.semantics(results[2])==run.baseline.semantics(results[3]),"BASELINE_DIFFERENCE")
        current[spec.history]=post.state_digest
    s.require(used==set(states),"UNUSED_STATE_INVALID")
    c=run.counts(r["events"])
    s.require(c==r["counts"] and all(v<=run.LIMITS[k] for k,v in c.items()),"COUNTS_INVALID")
    s.require(r["attempts"]==dict(formations=c["formations"],arms=c["arms"]),"ATTEMPT_COUNT_INVALID")
    if r["mode"]=="MAIN":
        s.require((c["events"],c["formations"],c["cues"],c["arms"])==(36,16,20,80)
                  and r["source_counts"]==dict(audio=36,nj=36,visual=16),"MAIN_COUNTS_INVALID")
    budget["state_value_validation_limit"] = budget["state_validation_passes"] * 5568
    s.require(all(v<=run.VERIFY_LIMITS[k] for k,v in budget.items()),"VERIFICATION_BUDGET_EXCEEDED")
    s.require(before==s.digest(r),"RECORD_MUTATED")
    return io.sealed(dict(status="RECORDING_COMPLETE",record_digest=r["record_digest"],read_only=True,
        final_states=current,transitions=transitions,baseline_equal=True,verification_work=budget,
        offline_limit="NJ bindings and rounded values validated; raw spectra and native TSPM receipt not reconstructed"),"verification_digest")


def verify_file_once(path, *, events, catalog, config):
    path=Path(path).resolve(strict=True)
    target=path.with_name("verification.json")
    pending=target.with_name("verification.json.pending")
    s.require(not target.exists(),"VERIFICATION_ALREADY_EXISTS")
    with pending.open("xb") as handle:
        before=io.filehash(path)
        try:
            s.require(path.stat().st_size<=run.MAX_BYTES,"RECORDING_SIZE_EXCEEDED")
            data=path.read_bytes()
            record=json.loads(data)
            s.require(data==s.canonical(record) and record["output_directory"]==str(path.parent),"RECORD_PATH_INVALID")
            result=verify_record(record,events=events,catalog=catalog,config=config)
        except Exception as exc:
            result=dict(status="NOT_EVALUABLE",phase="VERIFICATION",code=exc.code if isinstance(exc,s.S2NQError) else "INVALID_RECORDING")
        result=io.sealed({**result,"file_sha256":before,"file_unchanged":io.filehash(path)==before},"report_digest")
        handle.write(s.canonical(result))
        handle.flush()
        io.os.fsync(handle.fileno())
    io.os.link(pending,target)
    pending.unlink()
    return target
