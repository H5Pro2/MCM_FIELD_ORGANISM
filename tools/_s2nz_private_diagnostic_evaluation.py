"""NZ descriptive outcomes only; no threshold, practical success or oracle."""
from tools import _s2nz_private_diagnostic_run as run
from tools import _s2ny_private_prediction_evaluation as ny

b,p=run.b,run.p


def site_result(site,site_id,stream_id):
    selection=site["prediction_binding"]["primary"]["recommendation"]
    score=site["primary"]
    errors={a:s["mae"] for a,s in score["scores"].items()}
    h=selection["history"]
    if h is None:
        outcome=selection["status"]
    else:
        other="H2" if h=="H1" else "H1"
        outcome="NEXT_BEST" if errors[h]<errors[other] else "NEXT_WRONG" if errors[h]>errors[other] else "NEXT_TIE"
    row=dict(site_id=site_id,stream_id=stream_id,target=site["prediction_binding"]["target"],
        recommendation=selection,recommendation_outcome=outcome,mae=errors,recommended_mae=score["recommended_mae"],
        recommendation_gains=score["recommendation_gains"],gains_vs_persist=score["gains_vs_persist"],
        recommendation_outcomes={a:ny.outcome(g) for a,g in score["recommendation_gains"].items() if a in ("LOCAL","PERSIST")},
        persist_outcomes={a:ny.outcome(g) for a,g in score["gains_vs_persist"].items()})
    gains=None if "LOCAL" not in errors else {h:errors["LOCAL"]-errors[h] for h in ("H1","H2")}
    row.update(fixed_history_gains_vs_local=gains,
        fixed_history_outcomes_vs_local=None if gains is None else {h:ny.outcome(g) for h,g in gains.items()})
    return row


def summary(rows):
    emitted=[r for r in rows if r["recommendation"]["history"] is not None]
    comparisons={}
    for control in ("LOCAL","PERSIST"):
        for arm in ("H1","H2","RECOMMENDATION"):
            outcomes=[]
            for row in rows:
                if control not in row["mae"]:
                    continue
                if arm=="RECOMMENDATION":
                    outcome=row["recommendation_outcomes"].get(control)
                elif control=="LOCAL":
                    outcome=row["fixed_history_outcomes_vs_local"][arm]
                else:
                    outcome=row["persist_outcomes"][arm]
                if outcome is not None:
                    outcomes.append(outcome)
            comparisons[arm+"_VS_"+control]=dict(D=len(outcomes),WIN=outcomes.count("WIN"),
                TIE=outcomes.count("TIE"),LOSS=outcomes.count("LOSS"))
    return dict(N=len(rows),D=len(emitted),status="NUTZEN_NICHT_GEPRUEFT" if not emitted else "DESCRIBED",
        site_ids=[r["site_id"] for r in rows],comparisons=comparisons,
        recommendation_counts={status:sum(r["recommendation_outcome"]==status for r in rows) for status in
            ("NEXT_BEST","NEXT_WRONG","NEXT_TIE","ABSTAIN_INSUFFICIENT_PREFIX","ABSTAIN_TIE")})


def evaluate(record,proof,plan):
    for obj,key in ((record,"record_digest"),(proof,"verification_digest"),(plan,"evaluation_digest")):
        p.check(obj,key)
    p.require(proof.get("status")=="S2NZ_DIAGNOSTIC_VERIFIED" and proof.get("evaluation_allowed") is True
        and proof.get("read_only") is True and proof.get("record_digest")==record["record_digest"]
        and record["status"]=="RECORDING_COMPLETE","EVALUATION_BEFORE_VERIFICATION")
    p.require(plan==b.evaluation_plan(dict(execution_digest=record["execution_digest"])),"EVALUATION_BINDING_INVALID")
    rows=[]
    for stream in record["core"]["streams"]:
        for site in stream["sites"]:
            rows.append(site_result(site,f"p{len(rows)+1:02d}",stream["stream_id"]))
    p.require(len(rows)==18,"SITE_COUNT_INVALID")
    groups=[dict(stream_id=sid,category=category,**summary([r for r in rows if r["stream_id"]==sid]))
        for sid,category in plan["categories"].items()]
    lookup={r["site_id"]:r for r in rows}
    focus=[lookup[s] for s in plan["focus"]["site_ids"]]
    p.require(len(focus)==4 and plan["focus"]["N"]==4,"FOCUS_BINDING_INVALID")
    work=dict(fixed_local_gain_subtractions=24,win_tie_loss_comparisons=72+
        sum(len({"LOCAL","PERSIST"}&r["recommendation_gains"].keys()) for r in rows),recommendation_judgements=18,
        relevance_comparisons=0)
    p.require(work["win_tie_loss_comparisons"]<=96,"EVALUATION_WORK_EXCEEDED")
    result=b.sealed(dict(status="DIAGNOSTICALLY_DESCRIBED",record_digest=record["record_digest"],
        verification_digest=proof["verification_digest"],evaluation_digest=plan["evaluation_digest"],
        rows=rows,groups=groups,focus=summary(focus),control_pairs=plan["control_pairs"],work=work,
        target=plan["target"],clean_reconstruction_target=False,losses_compensated=False,tolerance=False,
        practical_threshold=None,practical_success_status=None,robustness_status=None),"result_digest")
    p.require(len(b.canonical(result))<=262144,"EVALUATION_SIZE_EXCEEDED")
    return result
