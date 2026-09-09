"""NY functional evaluation, only after successful technical verification."""
from tools import _s2ny_private_prediction as p

b=p.b


def outcome(gain):
    return "WIN" if gain>0 else "LOSS" if gain<0 else "TIE"


def site_result(site,site_id,stream_id):
    selection=site["prediction_binding"]["primary"]["recommendation"]
    h=selection["history"]
    score=site["primary"]
    errors={a:s["mae"] for a,s in score["scores"].items()}
    if h is None:
        status=selection["status"]
    else:
        other="H2" if h=="H1" else "H1"
        status="NEXT_BEST" if errors[h]<errors[other] else "NEXT_WRONG" if errors[h]>errors[other] else "NEXT_TIE"
    return dict(site_id=site_id,stream_id=stream_id,target=site["prediction_binding"]["target"],
        recommendation=selection,recommendation_outcome=status,mae=errors,recommended_mae=score["recommended_mae"],
        recommendation_gains=score["recommendation_gains"],gains_vs_persist=score["gains_vs_persist"],
        recommendation_outcomes={a:outcome(g) for a,g in score["recommendation_gains"].items()},
        persist_outcomes={a:outcome(g) for a,g in score["gains_vs_persist"].items()})


def evaluate(record,proof,plan):
    for obj,key in ((record,"record_digest"),(proof,"verification_digest"),(plan,"evaluation_digest")):
        p.check(obj,key)
    p.require(proof.get("status")=="S2NY_PREDICTION_VERIFIED" and proof.get("evaluation_allowed") is True
        and proof.get("read_only") is True and proof.get("record_digest")==record["record_digest"]
        and record["status"]=="RECORDING_COMPLETE","EVALUATION_BEFORE_VERIFICATION")
    p.require(plan==b.evaluation_plan(dict(execution_digest=record["execution_digest"])),"EVALUATION_BINDING_INVALID")
    rows=[]
    for stream in record["streams"]:
        for site in stream["sites"]:
            rows.append(site_result(site,f"p{len(rows)+1:02d}",stream["stream_id"]))
    p.require(len(rows)==18,"SITE_COUNT_INVALID")
    lookup={r["site_id"]:r for r in rows}
    checks=[]
    for check in plan["criteria"]:
        r=lookup[check["site_id"]]
        emitted=r["recommendation"]["history"] is not None
        prefix=check["check_id"][0]
        if prefix=="R":
            passed=emitted and r["recommendation_outcome"]=="NEXT_BEST"
        else:
            control="LOCAL" if check["condition"].endswith("LOCAL") else "PERSIST"
            gain=r["recommendation_gains"].get(control)
            passed=emitted and (gain<0 if prefix=="W" else gain>0)
        checks.append({**check,"status":"CONFIRMED" if passed else "FALSIFIED",
            "recommendation_present":emitted,"not_emitted":not emitted})
    groups=[]
    for sid in (f"s{i:02d}" for i in range(1,7)):
        members=[r for r in rows if r["stream_id"]==sid]
        emitted=[r for r in members if r["recommendation"]["history"] is not None]
        groups.append(dict(stream_id=sid,category=plan["categories"][sid],N=3,D=len(emitted),
            sufficient_prefix_N=2,status="NUTZEN_NICHT_GEPRUEFT" if not emitted else "AUSWERTBAR",
            counts={status:sum(r["recommendation_outcome"]==status for r in members) for status in
                ("NEXT_BEST","NEXT_WRONG","NEXT_TIE","ABSTAIN_INSUFFICIENT_PREFIX","ABSTAIN_TIE")}))
    result=b.sealed(dict(status="FUNCTIONALLY_EVALUATED",record_digest=record["record_digest"],
        verification_digest=proof["verification_digest"],evaluation_digest=plan["evaluation_digest"],rows=rows,groups=groups,criteria=checks,
        blocks={name:dict(N=sum(c["check_id"].startswith(name) for c in checks),
            confirmed=sum(c["check_id"].startswith(name) and c["status"]=="CONFIRMED" for c in checks)) for name in ("R","L","P","W")},
        absolute_errors_reported=True,losses_compensated=False,tolerance=False,general_robustness_proven=False),"result_digest")
    p.require(len(b.canonical(result))<=262144,"EVALUATION_SIZE_EXCEEDED")
    return result
