"""Offline whole-chain verification. No receptor, NJ or memory advancement."""
from dataclasses import asdict
import json
from pathlib import Path

from tools import _s2ns_private_run as run
from tools import _s2nq_private_verification as formation_check

s, src, io = run.s, run.src, run.io


def decode_result(p):
    try:
        scans = tuple(s.Scan(**{**x,"rows":tuple(s.Row(**{**r,"terms":tuple(r["terms"])}) for r in x["rows"])}) for x in p["scans"])
        admissions = tuple(s.Admission(**{**x,"provenance":tuple(x["provenance"]),"matched_slots":tuple(x["matched_slots"])}) for x in p["admissions"])
        result = s.Result(**{**p,"scans":scans,"admissions":admissions})
        s.require(s.canonical(asdict(result)) == s.canonical(p),"RESULT_FORM_INVALID")
        return result
    except (KeyError,TypeError) as exc:
        raise s.S2NSError("RESULT_FORM_INVALID") from exc


def decode_inventory(p):
    return s.Inventory(**{**p,"slots":tuple(s.SlotBinding(**{**z,"generation":
        None if z["generation"] is None else s.Generation(**z["generation"])}) for z in p["slots"])})


def derive_generation(config,history,pre,post,prior,spec,bound,form,transition):
    """Independent births follow independently proven selected slots, not claims."""
    result_hash = form["result_digest"]
    digest = s.digest(dict(previous=prior.verified_chain_digest,event_digest=s.digest(spec),
        prestate=pre.state_digest,poststate=post.state_digest,input_digest=bound.input_digest,result_digest=result_hash))
    fast_selected = next(z.slot_id for z in post.tspm_state.fast_state.slots if z.last_selected_step == post.generation and z.occupied)
    fast_match = transition["fast_rank"]["selected_slot_id"] is not None
    ppb = transition["ppb"][0]
    updated, bindings = [],[]
    for index,((bank,old),(_,new)) in enumerate(zip(s.slot_items(pre),s.slot_items(post),strict=True)):
        g = prior.slots[index].generation
        action = "UNCHANGED"
        if not new.occupied:
            action = "CLEARED" if old.occupied else "FREE"
            g = None
        else:
            selected = ((bank == 0 and new.slot_id == form["receipt"]["b4_slot_id"])
                or (bank == 1 and new.slot_id == fast_selected)
                or (bank == 2 and ppb["event"] != "NO_UPDATE" and new.slot_id == ppb["slot_id"]))
            if selected:
                matched = (bank == 1 and fast_match) or (bank == 2 and ppb["event"] == "MATCHED")
                action = "MATCHED" if matched else "REPLACED" if old.occupied else "CREATED"
                if not matched:
                    g = s.Generation(history,s.BANKS[bank],new.slot_id,spec["event_id"],spec["ordinal"],action,
                        pre.state_digest,bound.input_digest,s.slot_hash(bank,new),s.digest(dict(
                            transaction=result_hash,bank=s.BANKS[bank],slot_id=new.slot_id,event=action)))
            s.require(g is not None,"GENERATION_CHAIN_MISSING")
        values = s.slot_values(bank,new)
        bindings.append(s.SlotBinding(s.BANKS[bank],new.slot_id,s.slot_hash(bank,new),None if values is None else s.digest(list(values)),g))
        updated.append(dict(index=index,action=action,generation_digest=None if g is None else g.generation_digest))
    return s.Inventory(history,config.config_digest,s.profile.half.PROFILE_DIGEST,post.state_digest,digest,tuple(bindings)),updated


def verify_record(record,*,plan,config):
    try:
        return _verify(record,plan,config)
    except s.S2NSError:
        raise
    except (s.memory.S2JWCoordinatorError,s.memory.tspm1.TSPM1Error) as exc:
        raise s.S2NSError("STATE_BINDING_INVALID") from exc
    except (KeyError,ValueError,TypeError,AttributeError,IndexError,StopIteration) as exc:
        raise s.S2NSError("RECORD_BINDING_INVALID") from exc


def _verify(r,plan,config):
    before = s.digest(r)
    src.check(r,"record_digest")
    run.validate_plan(plan,r["mode"])
    s.require(r["schema"] == run.SCHEMA and r["source_schema"] == src.SCHEMA and
        r["plan_digest"] == plan["execution_digest"] and r["config_digest"] == config.config_digest
        and config == s.profile.build_config() and r["limits"] == run.LIMITS
        and r["verification_limits"] == run.VERIFY_LIMITS,"TOTAL_BINDING_INVALID")
    s.require(r["run_id"] == Path(r["output_directory"]).name and
        r["code_before"] == r["code_after"] == run.code_hashes(),"CODE_PATH_BINDING_INVALID")
    if r["mode"] == "MAIN":
        s.require(r["qualification_digest"] == run.qualification_binding(),"QUALIFICATION_REQUIRED")
    if r["status"] == "NOT_EVALUABLE":
        f,n = r["failure"],r["failure"]["completed_events"]
        events = plan["events"]
        s.require(type(n) is int and 0 <= n <= len(events) and f["phase"] in run.PHASES
            and r["events"] == [] and r["states"] == {} and r["initial_states"] == {},"FAILURE_FORM_INVALID")
        s.require((f["event_index"] is None and n == 0 and f["event_id"] is None) or
            (type(f["event_index"]) is int and 0 <= f["event_index"] < len(events)
             and f["event_id"] == events[f["event_index"]]["event_id"]
             and (f["event_index"] == n or n == len(events))),"FAILURE_PROGRESS_INVALID")
        s.require(r["counts"]["events"] == n and r["counts"]["formations"] == sum(x["event_type"] == run.b.AV for x in events[:n])
            and r["counts"]["cues"] == sum(x["event_type"] == run.b.A for x in events[:n])
            and (f["last_state_digest"] is None or s.hashes(f["last_state_digest"]))
            and run.re.fullmatch(r"[A-Z][A-Z0-9_]{0,95}",f["code"]),"FAILURE_BINDING_INVALID")
        s.require(all(type(v) is int and 0 <= v <= run.LIMITS[k] for k,v in r["counts"].items())
            and all(type(v) is int and 0 <= v <= run.LIMITS[k] for k,v in r["source_counts"].items()),"FAILURE_BUDGET_INVALID")
        return io.sealed(dict(status="NOT_EVALUABLE",record_digest=r["record_digest"],read_only=True,
            evaluation_allowed=False),"verification_digest")
    s.require(r["status"] == "RECORDING_COMPLETE" and r["failure"] is None and len(r["events"]) == len(plan["events"]),"RECORD_COMPLETENESS_INVALID")
    run.size_check(r)
    states = {h:formation_check.old.decode_state(p,config) for h,p in r["states"].items()}
    s.require(all(h == st.state_digest for h,st in states.items()),"STATE_POOL_INVALID")
    current = dict(r["initial_states"])
    s.require(set(current) == {e["history_id"] for e in plan["events"]},"HISTORY_BINDING_INVALID")
    inventories,origins,originals = {},{},{}
    for history,h in current.items():
        st = states[h]
        s.require(st.generation == 0 and st.parent_state_digest is None and st.last_input_digest is None
            and not any(x.occupied for x in st.tspm_state.visual_ppb1_state.slots),"INITIAL_STATE_INVALID")
        inventories[history] = run.initial_inventory(config,history,st)
        origins[history] = [() for _ in range(20)]
        originals[history] = []
    work = {k:0 for k in run.VERIFY_LIMITS}
    work.update(state_decodes=len(states),state_validation_passes=len(states))
    used,transitions,cases = set(current.values()),[],[]
    for spec,e in zip(plan["events"],r["events"],strict=True):
        src.check(e,"event_digest")
        history = spec["history_id"]
        s.require(e["event_id"] == spec["event_id"] and e["history_id"] == history and e["spec_digest"] == s.digest(spec)
            and e["prestate"] == current[history],"EVENT_CHAIN_INVALID")
        pre,post = states[e["prestate"]],states[e["poststate"]]
        used.update((pre.state_digest,post.state_digest))
        bound = src.restore(spec,e["source"],plan,config)
        work["source_bindings"] += 1
        work["halving_terms"] += 48
        if spec["event_type"] == run.b.AV:
            s.require(e["results"] == [] and e["inventory"] is None and e["view_digests"] == [],"FORMATION_FORM_INVALID")
            t = formation_check._formation({**e,"spec":spec},pre,post,bound,config,r["run_id"],work)
            inventory,updates = derive_generation(config,history,pre,post,inventories[history],spec,bound,e["formation"],t)
            inventories[history] = inventory
            source_id = spec["auditory"]["source_id"]
            for item in updates:
                i,action = item["index"],item["action"]
                if action in ("FREE","CLEARED"):
                    origins[history][i] = ()
                elif action in ("CREATED","REPLACED"):
                    origins[history][i] = (source_id,)
                elif action == "MATCHED":
                    origins[history][i] = tuple(sorted(set(origins[history][i]) | {source_id}))
            originals[history].append(dict(source_id=source_id,values=list(bound.auditory_values),
                source_binding_digest=e["source"]["source_binding_digest"],event_id=spec["event_id"]))
            transitions.append({**t,"generations":updates,"inventory_digest":inventory.inventory_digest})
        else:
            s.require(pre == post and e["formation"] is None and e["owner_before"] is None,"CUE_READ_ONLY_INVALID")
            inventory = inventories[history]
            s.require(s.canonical(e["inventory"]) == s.canonical(asdict(inventory)),"GENERATION_CHAIN_INVALID")
            s.require(e["view_digests"] == [v.view_digest for v in bound] and len(e["results"]) == 2,"CUE_COMPLETENESS_INVALID")
            primary,baseline = [decode_result(x) for x in e["results"]]
            proof = run.direct.verify_pair(primary,baseline,config=config,state=pre,inventory=inventory,lower=bound[0],upper=bound[1])
            work["state_validation_passes"] += 1
            for dest,key in (("scans","verification_scans"),("slot_rows","verification_slot_inspections"),
                             ("band_differences","verification_band_differences"),("equality_comparisons","verification_equality_comparisons")):
                work[dest] += proof[key]
            cases.append(dict(event_id=spec["event_id"],pair_verification=proof,slot_sources=origins[history][:],
                original_formations=originals[history][:],chain_digest=inventory.verified_chain_digest))
        current[history] = post.state_digest
    s.require(used == set(states),"UNUSED_STATE_INVALID")
    c = run.counts(r["events"])
    s.require(c == r["counts"] and all(v <= run.LIMITS[k] for k,v in c.items())
        and r["attempts"] == dict(formations=c["formations"],results=c["cues"]*2)
        and r["source_counts"]["nj"] == c["events"] and 0 <= r["source_counts"]["audio"] <= c["events"]
        and 0 <= r["source_counts"]["visual"] <= c["formations"],"COUNTS_INVALID")
    if r["mode"] == "MAIN":
        s.require(r["source_counts"] == dict(audio=31,nj=31,visual=16),"SOURCE_COUNTS_INVALID")
    s.require(all(v <= run.VERIFY_LIMITS[k] for k,v in work.items()),"VERIFICATION_BUDGET_EXCEEDED")
    s.require(before == s.digest(r),"RECORD_MUTATED")
    return io.sealed(dict(status="RECORDING_COMPLETE",record_digest=r["record_digest"],read_only=True,
        evaluation_allowed=True,final_states=current,transitions=transitions,cases=cases,baseline_equal=True,
        verification_work=work,source_limit="Payload and receptor provenance hash-bound, not regenerated. Stored raw-to-NJ multiplication independently checked.",
        generation_limit="Births and continuity derived after independent complete formation/selection/update checks; native receipt hash itself not replayed."),"verification_digest")


def verify_file_once(path,*,plan,config):
    path = Path(path).resolve(strict=True)
    output = path.with_name("verification.json")
    s.require(not output.exists(),"VERIFICATION_ALREADY_EXISTS")
    with output.with_suffix(".claim").open("xb"):
        pass
    before = io.filehash(path)
    try:
        s.require(path.stat().st_size <= run.LIMITS["record_bytes"],"RECORD_SIZE_EXCEEDED")
        data = path.read_bytes()
        r = json.loads(data)
        s.require(data == s.canonical(r) and r["output_directory"] == str(path.parent),"RECORD_FILE_INVALID")
        result = verify_record(r,plan=plan,config=config)
    except Exception as exc:
        result = dict(status="NOT_EVALUABLE",phase="VERIFICATION",code=getattr(exc,"code","INVALID_RECORDING"),evaluation_allowed=False)
    s.require(io.filehash(path) == before,"RECORD_FILE_CHANGED")
    result = io.sealed({**result,"file_sha256":before,"file_unchanged":True},"report_digest")
    io.atomic_write(output,result,run.LIMITS["record_bytes"])
    return output
