"""NR evaluation root is accessed only after complete technical verification."""
import json
from pathlib import Path
from tools import _s2nr_private_run as run
from tools._s2nq_private_evaluation import retention

require,digest,canonical=run.require,run.digest,run.canonical
s=run.runtime.s


def variation(values,indices,references):
    if not references or any(r is None for r in references):
        return None
    selected={tuple(r[i] for i in indices) for r in references}
    return None if len(selected)!=1 else tuple(values)!=next(iter(selected))


def inventory(state):
    return {
        "A_RECENT_B4":state["b4_state"]["entries"],
        "A_RECENT_FAST":state["tspm_state"]["fast_state"]["slots"],
        "B_STABLE_AUDITORY":state["tspm_state"]["auditory_ppb1_state"]["slots"],
        "B_STABLE_VISUAL":state["tspm_state"]["visual_ppb1_state"]["slots"]}


def advance(lineage,pre,post,spec):
    """Generation provenance follows actual writes, not expected support."""
    events=[]
    for bank,left in inventory(pre).items():
        right=inventory(post)[bank]
        changed=[]
        for a,b in zip(left,right,strict=True):
            key=(bank,b["slot_id"])
            if not b["occupied"]:
                lineage.pop(key,None)
            elif a!=b:
                reset=bank=="A_RECENT_B4" or not a["occupied"] or b["support_count"]==1
                previous=None if reset else lineage.get(key)
                require(reset or previous is not None,"PROVENANCE_CHAIN_MISSING")
                source=spec["visual" if bank=="B_STABLE_VISUAL" else "auditory"]["source_id"]
                origin=dict(generation=spec["event_id"] if reset else previous["generation"],
                    sources=sorted({source}|(set() if reset else set(previous["sources"]))))
                lineage[key]=origin
                changed.append(dict(slot_id=b["slot_id"],event="CREATED" if not a["occupied"] else "REPLACED" if reset else "MATCHED",
                    support=b.get("support_count"),pre_slot_digest=digest(a),post_slot_digest=digest(b),
                    prototype_digest=digest(b["prototype_values"]) if "prototype_values" in b else None,origin=origin))
        events.append(dict(bank=bank,changes=changed,event="NO_UPDATE" if not changed else "UPDATED"))
    return events


def summarize(observations):
    groups={}
    for o in observations:
        key=(o["phase"],o["subtype"],o["competition"],tuple(o["receptor_variation"]))
        groups.setdefault(key,[]).append(o)
    result=[]
    for key,rows in groups.items():
        public={area:retention([(o["correct"][0] and o["areas"][0]==area,
            o["correct"][1] and o["areas"][1]==area) for o in rows if o["target"] and o["target_available"]])
            for area in ("A_RECENT","B_STABLE_AUDITORY")}
        relationships={bank:retention([(r["contiguous"],r["distributed"]) for o in rows for r in o["relations"]
            if r["target"] and r["bank"]==bank]) for bank in s.ROLES}
        result.append(dict(phase=key[0],subtype=key[1],competition=key[2],receptor_variation=key[3],
            N=len(rows),public_retention=public,relationship_retention=relationships,
            gains=[o["event_id"] for o in rows if not o["correct"][0] and o["correct"][1]],
            losses=[o["event_id"] for o in rows if o["correct"][0] and not o["correct"][1]],
            false_admissions=[sum(o["false_admissions"][i] for o in rows) for i in range(2)],
            ambiguities=[sum("AMBIGU" in o["decisions"][i] for o in rows) for i in range(2)],
            abstentions=[sum(o["areas"][i] is None for o in rows) for i in range(2)],
            target_removal_controls=sum(o["target"] is not None and not o["target_available"] for o in rows),
            discarded_target_candidates=[dict(event_id=o["event_id"],**r) for o in rows for r in o["relations"]
                if r["target"] and r["contiguous"] and not r["distributed"]]))
    return result


def evaluate(record,proof,bound,evaluation):
    run.check(record,"record_digest")
    run.check(proof,"verification_digest")
    run.check(evaluation,"evaluation_digest")
    require(proof["record_digest"]==record["record_digest"] and proof["status"]==record["status"]=="RECORDING_COMPLETE"
        and evaluation["execution_digest"]==record["execution_digest"]==bound.payload()["execution_digest"],"EVALUATION_REQUIRES_VERIFICATION")
    if bound.mode=="MAIN":
        require(run.source.filehash(run.ROOT/run.SEAL_DIR/"evaluation-plan.json")==run.PINS["evaluation-plan.json"]
            and evaluation==json.loads((run.ROOT/run.SEAL_DIR/"evaluation-plan.json").read_bytes()),"EVALUATION_ROOT_CHANGED")
    c=record["comparison"]
    specs=bound.payload()["events"]
    expectations={e["event_id"]:e for e in evaluation["cases"]}
    require(len(expectations)==len(evaluation["cases"]) and set(expectations)=={e["event_id"] for e in specs if e["event_type"]==run.source.A},"EVALUATION_CASES_INVALID")
    scans={(r["ordinal"],r["arm"]):r["value"] for r in c["scans"] if r["role"]=="PRIMARY"}
    lineage,references,observations,formations={},{},[],[]
    for spec,p,pair in zip(specs,c["inputs"],c["pairs"],strict=True):
        pre=c["states"][pair["arms"][0]["pre"]["memory_state_digest"]]
        post=c["states"][pair["arms"][0]["memory"]]
        if spec["event_type"]==run.source.AV:
            changes=advance(lineage,pre,post,spec)
            references.setdefault(spec["auditory"]["source_id"],[]).append(p["projection"]["values"])
            formations.append(dict(event_id=spec["event_id"],prestate=pair["arms"][0]["pre"]["memory_state_digest"],
                poststate=pair["arms"][0]["memory"],transitions=changes,
                inventory=[dict(bank=b,slot_id=x["slot_id"],support=x.get("support_count"),
                    origin=lineage.get((b,x["slot_id"])),slot_digest=digest(x))
                    for b,slots in inventory(post).items() for x in slots if x["occupied"]]))
            continue
        ex=expectations[spec["event_id"]]
        require(ex["cue_id"]==spec["auditory"]["source_id"],"EVALUATION_CUE_INVALID")
        target=ex["target"]
        arms=[scans[(spec["ordinal"],i)] for i in range(2)]
        by_key=[{(r["bank"],r["slot_id"]):r for r in a["rows"]} for a in arms]
        origins={r["slot_digest"]:lineage.get(k) for k,r in by_key[0].items() if r["eligible"]}
        relations=[]
        for k,a in by_key[0].items():
            if not a["eligible"]:
                continue
            origin=lineage.get(k)
            require(origin is not None,"PROVENANCE_MISSING")
            relations.append(dict(bank=k[0],slot_id=k[1],origin=origin,target=bool(target and origin["sources"]==[target]),
                contiguous=a["matched"],distributed=by_key[1][k]["matched"]))
        correct,false,areas,deviation,variations=[],[],[],[],[]
        for i,arm in enumerate(arms):
            h=arm["hypothesis"]
            parents=[] if h is None else [origins.get(d) for d in h["provenance"]]
            good=bool(h and target and parents and all(o and o["sources"]==[target] for o in parents))
            correct.append(good)
            false.append(bool(h) and not good)
            areas.append(None if h is None else h["area"])
            op=p["operations"][i]["cue"]
            variations.append(variation(op["values"],s.plan(s.VIEWS[i]).observed,references.get(target,[])))
            target_rows=[r for k,r in by_key[i].items() if r["eligible"] and lineage.get(k,{}).get("sources")==[target]]
            deviation.append(None if not target_rows else any(any(t!=0.0 for t in r["terms"]) for r in target_rows))
        available=any(r["target"] for r in relations)
        predictions=[(areas[i] is None) if ex["prediction"]=="ABSTAIN" else correct[i] and areas[i]==ex["prediction"] for i in range(2)]
        observations.append(dict(event_id=spec["event_id"],phase=ex["phase"],subtype=ex["subtype"],target=target,
            target_available=available,competition=any(not r["target"] for r in relations),relations=relations,
            receptor_variation=variations,cue_candidate_deviation=deviation,correct=correct,false_admissions=false,
            areas=areas,decisions=[a["decision"] for a in arms],prediction_met=predictions))
    return run.sealed(dict(status="EVALUATED",record_digest=record["record_digest"],evaluation_root=evaluation["evaluation_digest"],
        observations=observations,formations=formations,groups=summarize(observations),
        prediction_matches=[sum(o["prediction_met"][i] for o in observations) for i in range(2)],
        prediction_denominator=len(observations),no_netting=True,
        interpretation="Bounded transfer; abstention is not unknown-source recognition; no semantic equivalence across profiles"),"evaluation_digest")


def evaluate_file_once(path):
    path=Path(path)
    with path.with_name("evaluation.claim").open("xb") as f:
        f.write(b"s2nr-evaluation-once-v3")
    record=json.loads(path.read_bytes())
    report=json.loads(path.with_name("verification.json").read_bytes())
    run.check(report,"report_digest")
    require(report["file_unchanged"] and report["file_sha256"]==run.source.filehash(path),"VERIFIED_FILE_CHANGED")
    bound=run.load_execution()
    evaluation=json.loads((run.ROOT/run.SEAL_DIR/"evaluation-plan.json").read_bytes())
    result=evaluate(record,report["proof"],bound,evaluation)
    ng=run.ng
    ng.ne.atomic_write(path.with_name("evaluation.json"),result,limit=ng.MAX_BYTES)
    return result
