"""Post-verification provenance evaluation. Expectations never enter a scanner."""
from pathlib import Path
import json
from tools import _s2nq_private_run as run

s, io = run.s, run.io
EXPECTED = {
    "np-a07": ("np-a02","EXACT"), "np-a08": ("np-a02","LEVEL"),
    "np-a09": ("np-a02","FREQUENCY"), "np-a10": ("np-a02","SPECTRAL"),
    "np-a11": (None,"INDEPENDENT_CONTROL"), "np-a12": (None,"INDEPENDENT_CONTROL"),
}


def retention(rows):
    n = len(rows)
    d = sum(a for a,b in rows)
    r = sum(a and b for a,b in rows)
    lost = sum(a and not b for a,b in rows)
    return dict(N=n,D=d,R=r,L=lost,status="ERHALTUNG_NICHT_GEPRUEFT" if d==0 else "ASSESSED",
                gains=sum(not a and b for a,b in rows))


def evaluate(record, verification, expectations):
    s.require(verification["status"]==record["status"]=="RECORDING_COMPLETE"
              and verification["record_digest"]==record["record_digest"],"EVALUATION_REQUIRES_VERIFICATION")
    vp = {k:v for k,v in verification.items() if k not in ("report_digest","file_sha256","file_unchanged")}
    s.require(vp["verification_digest"]==s.digest({k:v for k,v in vp.items() if k!="verification_digest"}),"VERIFICATION_BINDING_INVALID")
    s.require(record["record_digest"]==s.digest({k:v for k,v in record.items() if k!="record_digest"}),"RECORD_BINDING_INVALID")
    lineages, observations = {}, []
    for e in record["events"]:
        history=e["spec"]["history"]
        lineage=lineages.setdefault(history,{})
        pre,post=(record["states"][e[k]] for k in ("prestate","poststate"))
        if e["kind"]=="FORMATION":
            for role, path in zip(s.ROLES,("b4_state","fast_state","auditory_ppb1_state"),strict=True):
                left=pre[path]["entries"] if path=="b4_state" else pre["tspm_state"][path]["slots"]
                right=post[path]["entries"] if path=="b4_state" else post["tspm_state"][path]["slots"]
                for a,b in zip(left,right,strict=True):
                    key=(role,b["slot_id"])
                    if not b["occupied"]:
                        lineage.pop(key,None)
                    elif a!=b:
                        reset=path=="b4_state" or not a["occupied"] or b["support_count"]==1
                        previous=() if reset else lineage[key]["sources"]
                        lineage[key]=dict(generation=e["spec"]["event_id"] if reset else lineage[key]["generation"],
                            sources=tuple(sorted(set(previous+(e["spec"]["audio_source"],)))))
            continue
        target,subtype=expectations[e["spec"]["audio_source"]]
        primary=(e["arms"][0],e["arms"][2])
        by_key=[{(r["bank"],r["slot_id"]):r for r in arm["rows"]} for arm in primary]
        source_by_hash={r["slot_digest"]:lineage.get(key) for key,r in by_key[0].items() if r["eligible"]}
        relations=[]
        for key,a in by_key[0].items():
            b=by_key[1][key]
            origin=lineage.get(key)
            is_target=bool(target and origin and origin["sources"]==(target,))
            if a["eligible"]:
                relations.append(dict(bank=key[0],slot_id=key[1],generation=origin["generation"],
                    sources=origin["sources"],target=is_target,contiguous=a["matched"],distributed=b["matched"]))
        correct, false, decisions=[],[],[]
        for arm in primary:
            h=arm["hypothesis"]
            origins=[] if h is None else [source_by_hash.get(k) for k in h["provenance"]]
            good=bool(h and target and origins and all(o and o["sources"]==(target,) for o in origins))
            correct.append(good)
            false.append(bool(h) and not good)
            decisions.append(arm["decision"])
        target_available=any(r["target"] for r in relations)
        # Exact source relation and actual projected variation are distinct axes.
        actual_variation=[]
        for arm in primary:
            target_rows=[r for r in arm["rows"] if r["eligible"] and lineage.get((r["bank"],r["slot_id"]),{}).get("sources")== (target,)]
            actual_variation.append(None if not target_rows else any(any(x!=0.0 for x in r["terms"]) for r in target_rows))
        observations.append(dict(event_id=e["spec"]["event_id"],history=history,source=e["spec"]["audio_source"],
            target=target,subtype=subtype,target_available=target_available,
            competition=any(not r["target"] for r in relations),actual_variation=actual_variation,
            relations=relations,decisions=decisions,correct=correct,false_admissions=false,
            hypotheses=[a["hypothesis"] for a in primary]))
    groups={}
    for o in observations:
        key=(o["history"],o["subtype"],o["competition"],tuple(o["actual_variation"]))
        groups.setdefault(key,[]).append(o)
    summaries=[]
    for key,rows in groups.items():
        relation_tables={bank:retention([(r["contiguous"],r["distributed"]) for o in rows for r in o["relations"]
                                        if r["target"] and r["bank"]==bank]) for bank in s.ROLES}
        public=retention([(o["correct"][0], o["correct"][1] and
            (not o["correct"][0] or o["hypotheses"][0]["area"]==o["hypotheses"][1]["area"]))
            for o in rows if o["target"] and o["target_available"]])
        summaries.append(dict(history=key[0],subtype=key[1],competition=key[2],actual_variation=key[3],
            relationship_retention=relation_tables,public_retention=public,cue_denominator=len(rows),
            target_removal_count=sum(bool(o["target"]) and not o["target_available"] for o in rows),
            false_admissions=[sum(o["false_admissions"][i] for o in rows) for i in range(2)],
            false_relationships=[sum(r[("contiguous","distributed")[i]] for o in rows for r in o["relations"] if not r["target"]) for i in range(2)],
            non_target_relationship_denominator=sum(not r["target"] for o in rows for r in o["relations"]),
            ambiguities=[sum(o["decisions"][i] in ("ABSTAIN_INTERNAL_AMBIGUITY","ABSTAIN_AMBIGUOUS_CONTEXT") for o in rows) for i in range(2)],
            correct_abstentions=[sum(o["hypotheses"][i] is None and (not o["target"] or not o["target_available"]) for o in rows) for i in range(2)]))
    return io.sealed(dict(status="EVALUATED",record_digest=record["record_digest"],observations=observations,
        groups=summaries,interpretation="Separate relationship and public denominators; no netting and no general robustness claim"),"evaluation_digest")


def evaluate_file_once(recording_path):
    path=Path(recording_path)
    s.require(not path.with_name("evaluation.json").exists(),"EVALUATION_ALREADY_EXISTS")
    record=json.loads(path.read_bytes())
    proof=json.loads(path.with_name("verification.json").read_bytes())
    s.require(proof["file_sha256"]==io.filehash(path) and proof["file_unchanged"],"VERIFIED_FILE_CHANGED")
    result=evaluate(record,proof,EXPECTED)
    io.atomic_write(path.with_name("evaluation.json"),result,run.MAX_BYTES)
    return result
