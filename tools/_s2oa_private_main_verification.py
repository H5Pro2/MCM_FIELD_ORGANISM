"""OA full-record verification and separate functional evaluation, no replay."""
import json
from tools import _s2oa_private_main_binding as b
from tools import _s2oa_private_runtime_verification as prior

r=b.r


def verify_event_ids(mapping,ex,packed):
    """Direct identifier derivation; no producer mapping/lookup helpers."""
    b.require(type(mapping) is dict and set(mapping)=={"schema","execution_digest","columns","rows","id_binding_digest"},"ID_FORM_INVALID")
    b.require(mapping["schema"]=="s2oa.event-id-binding.v1" and mapping["columns"]==["ordinal","plan_id","technical_id"],"ID_FORM_INVALID")
    b.require(mapping["execution_digest"]==ex["execution_digest"],"ID_ROOT_INVALID")
    b.require(type(mapping["rows"]) is list and len(mapping["rows"])==len(ex["events"])==28,"ID_COUNT_INVALID")
    for index in range(28):
        n=index+1;e=ex["events"][index];row=mapping["rows"][index]
        plan="e"+str(n).zfill(2);technical="s2oa-event-"+plan
        b.require(type(row) is list and len(row)==3 and type(row[0]) is int
                  and row==[n,plan,technical] and type(e["ordinal"]) is int
                  and (e["ordinal"],e["event_id"])==(n,plan),"ID_ROW_INVALID")
    prior.check(mapping,"id_binding_digest")
    b.require(len(b.canonical(mapping))<=2048,"ID_SIZE_INVALID")
    b.require(type(packed) is list and len(packed)==28,"ID_INPUT_COUNT_INVALID")
    for n,item in enumerate(packed,1):
        a=item["event"];e=ex["events"][n-1]
        b.require((a["event_id"],a["ordinal"],a["event_type"])==
                  ("s2oa-event-e"+str(n).zfill(2),n,e["event_type"]),"MAIN_EVENT_BINDING_INVALID")
    return mapping["id_binding_digest"]


def verify(value,bound):
    try:return _verify(value,bound)
    except r.S2OAError:raise
    except (KeyError,TypeError,ValueError,IndexError) as exc:
        raise r.S2OAError("MAIN_EVIDENCE_INVALID") from exc


def _verify(value,bound):
    before=b.digest(value);prior.check(value,"record_digest")
    b.require(value["schema"]==b.SCHEMA and value["mode"]=="OA" and value["main_gate"] is False
              and value["evaluation"] is None,"MAIN_FORM_INVALID")
    counts=value["counts"]
    b.require(set(counts)==set(b.COUNTS) and all(type(counts[k]) is int and 0<=counts[k]<=b.COUNTS[k] for k in counts),"MAIN_COUNTS_INVALID")
    if value["bindings"] is not None:
        b.validate_bound(bound)
        b.require(value["bindings"]==bound.provenance(),"MAIN_PROVENANCE_INVALID")
    core=value["execution"]
    if core is None:
        f=value["failure"]
        b.require(value["status"]=="NOT_EVALUABLE" and f["phase"] in b.PHASES and type(f["code"]) is str
            and type(f["error_class"]) is str and type(f["completed_events"]) is int
            and 0<=f["completed_events"]<=28,"MAIN_FAILURE_INVALID")
        b.require(f["ordinal"] is None or type(f["ordinal"]) is int and 1<=f["ordinal"]<=28,"MAIN_FAILURE_INVALID")
        final=f["final"]
        if final is not None:
            prior.check(final,"snapshot_digest")
            b.require(final["status"]=="CLOSED" and final["processed_event_count"]==f["completed_events"]
                and final["snapshot_digest"]==f["last_snapshot_digest"],"MAIN_FAILURE_CLOSE_INVALID")
        else:b.require(f["completed_events"]==0 and f["last_snapshot_digest"] is None,"MAIN_FAILURE_INVALID")
        return b.sealed(dict(status="NOT_EVALUABLE",evaluation_allowed=False,record_digest=value["record_digest"],
            failure_phase=f["phase"],read_only=True),"verification_digest")
    b.require(value["bindings"] is not None and counts==b.COUNTS,"MAIN_COUNTS_INVALID")
    ex=bound.execution();config=r.nn.profile.build_config()
    b.require(core["run_id"]==value["run_id"] and len(core["inputs"])==28,"MAIN_RUNTIME_BINDING_INVALID")
    id_digest=verify_event_ids(value["bindings"]["event_ids"],ex,core["inputs"])
    sources={s["source_id"]:s for s in ex["sources"]}
    for packed,src,e in zip(core["inputs"],core["source_receipts"],ex["events"],strict=True):
        actual=packed["event"]
        for m in ("auditory","visual"):
            t=e[m]
            observed=(None if src["nj"] is None else src["nj"]["pcm_digest"]) if m=="auditory" else src["rgb_digest"]
            b.require(observed==(None if t is None else sources[t["source_id"]]["payload_sha256"]),"MAIN_SOURCE_BINDING_INVALID")
    p=prior.verify(core,config)
    b.require(value["status"]==core["status"]==p["status"],"MAIN_STATUS_INVALID")
    if p["evaluation_allowed"]:
        b.require(value["failure"] is None and len(core["rows"])==28 and p["scan_receipts"]==16
            and p["field_contacts"]==8544 and len(p["transitions"])==20,"MAIN_COMPLETENESS_INVALID")
    else:
        f=value["failure"];n=core["failure"]["ordinal"]
        b.require(f["ordinal"]==n and f["completed_events"]==len(core["rows"])
            and f["phase"]==("FORMATION" if ex["events"][n-1]["event_type"]==b.source.AV else "CUE")
            and f["code"]==core["failure"]["code"] and f["errors"]==core["failure"]["errors"],"MAIN_FAILURE_INVALID")
    sizes=b.envelope_size(value)
    # A separate independent accounting includes all referenced source/qualification bytes.
    q=sizes["components"];res=q["ledger"]["reservations"];prov=bound.provenance()
    balance=b.av.check_totals(dict(prior=prov["metadata_bytes"],runtime=q["metadata_runtime_bytes"],
        shell=len(b.canonical(value))-len(b.canonical(core))),dict(historical=prov["source_bytes"]),res,
        len(b.canonical(core))-q["metadata_runtime_bytes"]-sum(res.values()))
    b.require(balance==sizes["balance"] and b.digest(value)==before,"MAIN_ACCOUNTING_INVALID")
    result=b.sealed(dict(status=value["status"],record_digest=value["record_digest"],read_only=True,
        evaluation_allowed=p["evaluation_allowed"],runtime_verification=p,sizes=sizes,event_id_binding_digest=id_digest,
        source_links=48,source_values_recomputed=False,raw_half_numerics_recomputed=False),"verification_digest")
    b.require(len(b.canonical(result))+prov["prior_verification_bytes"]+64<=262144,"MAIN_PROOF_LIMIT")
    return result


def verify_once(out):
    with (out/"verification.claim").open("xb") as f:f.write(b"once")
    before=r.admin.filehash(out/"record.json")
    value=json.loads((out/"record.json").read_bytes())
    try:
        bound=None if value["bindings"] is None else b.load_bound()
        proof=verify(value,bound)
        b.require(r.admin.filehash(out/"record.json")==before,"RECORD_CHANGED")
    except Exception as exc:
        proof=b.sealed(dict(status="NOT_EVALUABLE",evaluation_allowed=False,record_digest=value.get("record_digest"),
            phase="VERIFICATION",code=getattr(exc,"code","VERIFICATION_TECHNICAL_ERROR"),error_class=type(exc).__name__),"verification_digest")
    r.ng.ne.atomic_write(out/"verification.json",proof,262144)
    return proof


def flat_state(state):
    return (state["b4_state"]["entries"]+state["tspm_state"]["fast_state"]["slots"]+
            state["tspm_state"]["auditory_ppb1_state"]["slots"]+state["tspm_state"]["visual_ppb1_state"]["slots"])


def evaluate(value,proof,bound,ev):
    prior.check(proof,"verification_digest");prior.check(value,"record_digest");prior.check(ev,"evaluation_digest")
    b.require(proof["record_digest"]==value["record_digest"] and proof["evaluation_allowed"] is True
        and value["status"]=="RECORDING_COMPLETE","EVALUATION_BLOCKED")
    b.require(ev["evaluation_digest"]==bound.provenance()["evaluation_digest"] and ev["execution_digest"]==bound.execution()["execution_digest"],"EVALUATION_BINDING_INVALID")
    core=value["execution"];ex=bound.execution();sources={s["source_id"]:s for s in ex["sources"]}
    history=[set() for _ in range(24)];inventories=[];forms=[]
    for row,e in zip(core["rows"],ex["events"],strict=True):
        slots=flat_state(core["states"][row["memory"]]);gen=row["generations"]
        if gen is not None:
            current=e["ordinal"]
            for j in range(12):
                action=gen["actions"][j]
                if action in ("CLEARED","FREE"):history[j]=set()
                elif action in ("CREATED","REPLACED"):history[j]={current}
                elif action=="MATCHED":history[j].add(current)
            selected=next(j for j in range(9,12) if slots[j]["occupied"] and slots[j]["last_selected_step"]==len(forms)+1)
            for j in range(12,24):
                action=gen["actions"][j]
                if action in ("CLEARED","FREE"):history[j]=set()
                elif action in ("CREATED","REPLACED"):history[j]=set(history[selected])
                elif action=="MATCHED":history[j]|=history[selected]
            forms.append(dict(formation=len(forms)+1,event=current,actions=gen["actions"],births=gen["births"]))
        inventories.append([dict(slot_id=s["slot_id"],occupied=s["occupied"],support=s.get("support_count"),
            generation_birth=row["current_births"][j],source_events=sorted(history[j])) for j,s in enumerate(slots)])
    cases=[]
    for expected in ev["cases"]:
        n=next(i for i,e in enumerate(ex["events"]) if e["event_id"]==expected["event_id"])
        step=core["rows"][n]["step"];h=step["hypothesis"];area=None if h is None else h["area"]
        scan=next(s["value"] for s in core["scans"] if s["ordinal"]==n+1 and s["role"]=="PRIMARY")
        scan=scan["evidence"] if "evidence" in scan else scan
        records=[z for bank in scan["bank_scans"] for z in bank["records"]]
        chosen=[]
        if h is not None:
            ids={z["slot_id"] for z in records if z["slot_digest"] in h["provenance_slot_digests"]}
            chosen=[i for i in inventories[n] if i["slot_id"] in ids]
        origins=sorted({o for s in chosen for o in s["source_events"]})
        correct_origin=None
        if h is not None:
            if expected["modality"]=="visual":
                correct_origin=bool(origins) and all(sources[ex["events"][o-1]["visual"]["source_id"]]["recipe"]["ordinal"]==expected["target_visual_ordinal"] for o in origins)
            else:
                cue=sources[ex["events"][n]["auditory"]["source_id"]]["recipe_digest"]
                correct_origin=bool(origins) and all(sources[ex["events"][o-1]["auditory"]["source_id"]]["recipe_digest"]==cue for o in origins)
        prediction=expected["prediction"]
        if prediction in ("A_RECENT","B_STABLE"):ok=area==prediction and correct_origin is True
        elif prediction=="INTERNAL_AMBIGUITY":ok=step["context_status"]=="ABSTAIN_INTERNAL_AMBIGUITY" and h is None
        else:ok=h is None and not any(z["observed_match"] for z in records)
        cases.append(dict(cue_id=expected["cue_id"],event_id=expected["event_id"],prediction=prediction,
            observed=step["context_status"],area=area,source_events=origins,correct_origin=correct_origin,
            confirmed=ok,false_admission=h is not None and (prediction not in ("A_RECENT","B_STABLE") or correct_origin is not True)))
    criteria=[]
    def add(name,observed,expected):criteria.append(dict(name=name,observed=observed,expected=expected,confirmed=observed==expected))
    pred=ev["state_predictions"]
    add("fast_expiry_formations",[f["formation"] for f in forms if "CLEARED" in f["actions"][9:12]],pred["fast_expiry_formations"])
    add("visual_replacement_formations",[f["formation"] for f in forms if "REPLACED" in f["actions"][20:]],[pred["visual_slow_replacement_formation"]])
    add("replaced_visual_slot_orders",[j for f in forms for j,a in enumerate(f["actions"][20:]) if a=="REPLACED"],[pred["visual_slow_replaced_slot_order"]])
    for bank,span in (("audio",slice(12,20)),("visual",slice(20,24))):
        add(bank+"_ppb_calls",sum(a in ("CREATED","MATCHED","REPLACED") for f in forms for a in f["actions"][span]),pred["ppb_calls_per_modality"])
    add("final_visual_supports",[s["support"] for s in inventories[-1][20:]],pred["final_visual_supports"])
    def visual_origins(entry):
        return sorted({sources[ex["events"][o-1]["visual"]["source_id"]]["recipe"]["ordinal"] for o in entry["source_events"]})
    add("final_fast_origins",[visual_origins(s) for s in inventories[-1][9:12]],[[4],[5],[]])
    add("final_visual_origins",[visual_origins(s) for s in inventories[-1][20:]],[[5],[2],[3],[4]])
    add("final_fast_supports",[s["support"] if s["occupied"] else None for s in inventories[-1][9:12]],[4,4,None])
    final_b4=sorted(inventories[-1][:9],key=lambda s:s["generation_birth"] or 0)
    add("final_b4_origins",[visual_origins(s) for s in final_b4],[[3],[4],[4],[4],[4],[5],[5],[5],[5]])
    # Per-formation predictions remain evaluation, including unexpectedly shared slots.
    for f in forms:
        k=f["formation"];block=(k-1)//4;position=(k-1)%4
        add(f"f{k:02d}_fast_selected",next(j for j in range(3) if f["actions"][9+j] in ("CREATED","REPLACED","MATCHED")),block%3)
        if position:
            j=20+block%4;action=("REPLACED" if block==4 else "CREATED") if position==1 else "MATCHED"
            add(f"f{k:02d}_visual_transition",f["actions"][j],action)
            inv=inventories[f["event"]-1]
            add(f"f{k:02d}_visual_support",inv[j]["support"],position)
            add(f"f{k:02d}_audio_support",inv[12]["support"],block*3+position)
    q5=next(i for i,e in enumerate(ev["cases"]) if e["cue_id"]=="q05")
    q7=next(i for i,e in enumerate(ev["cases"]) if e["cue_id"]=="q07")
    n5=next(i for i,e in enumerate(ex["events"]) if e["event_id"]==cases[q5]["event_id"])
    n7=next(i for i,e in enumerate(ex["events"]) if e["event_id"]==cases[q7]["event_id"])
    add("q05_not_current_at_q07",r.current_evidence(core,n5,n7,20),False)
    result=b.sealed(dict(record_digest=value["record_digest"],verification_digest=proof["verification_digest"],
        evaluation_digest=ev["evaluation_digest"],status="CONFIRMED" if all(c["confirmed"] for c in cases+criteria) else "FALSIFIED",
        cues=cases,state_criteria=criteria,inventories=inventories,formations=forms,
        false_admissions=sum(c["false_admission"] for c in cases),hypotheses_applied=0),"evaluation_result_digest")
    b.require(len(b.canonical(result))<=262144,"EVALUATION_LIMIT")
    return result


def evaluate_once(out):
    with (out/"evaluation.claim").open("xb") as f:f.write(b"once")
    value=json.loads((out/"record.json").read_bytes());proof=json.loads((out/"verification.json").read_bytes())
    b.require(proof.get("evaluation_allowed") is True,"EVALUATION_BLOCKED")
    bound=b.load_bound()
    ev=json.loads((b.ROOT/r.admin.ARCHIVE["evaluation"][0]).read_bytes())
    result=evaluate(value,proof,bound,ev)
    r.ng.ne.atomic_write(out/"evaluation.json",result,262144)
    return result
