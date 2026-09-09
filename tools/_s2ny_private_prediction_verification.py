"""Independent NY arithmetic and read-only record reconstruction."""
import math
import sys
from tools import _s2ny_private_prediction as p
from tools import _s2nw_private_learning_verification as old

b=p.b


def direct_predict(coefficients,prefix,errors):
    p.require(type(coefficients) is tuple and len(coefficients)==2 and all(type(a) is float and math.isfinite(a) for a in coefficients),"FREEZE_FORM_INVALID")
    p.require(type(prefix) is tuple and len(prefix) in (2,3) and (errors is None)==(len(prefix)==2),"PREFIX_INVALID")
    for vector in prefix:
        p.vector(vector)
    local=None
    if len(prefix)==3:
        squares,crosses=0.0,0.0
        sub,under=[],[]
        for i in range(48):
            x=prefix[1][i]-prefix[0][i]
            y=prefix[2][i]-prefix[1][i]
            a=x*x
            c=x*y
            if any(0<abs(z)<sys.float_info.min for z in (x,y,a,c)):
                sub.append(i)
            if (x!=0 and a==0) or (x!=0 and y!=0 and c==0):
                under.append(i)
            squares=squares+a
            crosses=crosses+c
        beta=crosses/squares if squares>0.0 else 0.0
        p.require(all(math.isfinite(z) for z in (squares,crosses,beta)),"LOCAL_NONFINITE")
        local=dict(Sxx=squares,Sxy=crosses,beta=beta,zero_denominator=squares==0.0,
            division_performed=squares>0.0,subnormal_indices=sub,product_underflow_indices=under)
    predicted={}
    for name,alpha in zip(("H1","H2"),coefficients,strict=True):
        predicted[name]=[]
        for i in range(48):
            delta=prefix[-1][i]-prefix[-2][i]
            scaled=alpha*delta
            predicted[name].append(prefix[-1][i]+scaled)
    predicted["PERSIST"]=list(prefix[-1])
    if local is not None:
        predicted["LOCAL"]=[]
        for i in range(48):
            delta=prefix[-1][i]-prefix[-2][i]
            scaled=local["beta"]*delta
            predicted["LOCAL"].append(prefix[-1][i]+scaled)
    for values in predicted.values():
        p.vector(tuple(values),False)
    if errors is None:
        recommendation=dict(status="ABSTAIN_INSUFFICIENT_PREFIX",history=None)
    else:
        p.require(type(errors) is tuple and len(errors)==2 and all(type(e) is float and math.isfinite(e) and e>=0 for e in errors),"ERROR_VALUES_INVALID")
        recommendation=dict(status="ABSTAIN_TIE",history=None) if errors[0]==errors[1] else dict(
            status="RECOMMEND",history=("H1" if errors[0]<errors[1] else "H2"))
    return dict(predictions=predicted,local=local,recommendation=recommendation)


def direct_score(output,target):
    p.vector(target)
    scores={}
    for name,values in output["predictions"].items():
        p.vector(tuple(values),False)
        terms=[]
        for i in range(48):
            terms.append(dict(original_index=i,value=abs(values[i]-target[i])))
        mean=sum(t["value"] for t in terms)/48
        p.require(math.isfinite(mean),"ERROR_NONFINITE")
        scores[name]=dict(terms=terms,mae=mean)
    selected=output["recommendation"]["history"]
    gains={name:scores["PERSIST"]["mae"]-s["mae"] for name,s in scores.items() if name!="PERSIST"}
    selected_gains={} if selected is None else {name:s["mae"]-scores[selected]["mae"] for name,s in scores.items()}
    return dict(scores=scores,recommended_mae=None if selected is None else scores[selected]["mae"],
        recommendation_gains=selected_gains,gains_vs_persist=gains)


def verify_record(record,plan):
    p.require(len(b.canonical(record))<=p.MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
    p.check(record,"record_digest")
    p.check(plan,"execution_digest")
    p.require(record["schema"]=="s2ny.prefix-recommendation.v1" and record["execution_digest"]==plan["execution_digest"]
        and record["main_gate_after"] is False and record["evaluation"] is None,"RECORD_BINDING_INVALID")
    p.require(record["limits"]==p.limits() and record["verification_limits"]==p.verification_limits(),"LIMIT_BINDING_INVALID")
    p.count_form(record["work"],p.limits())
    counts=record["work"]
    p.require(counts["completed_windows"]<=counts["nj_returns"]<=counts["nj_attempts"]<=counts["analyze_returns"]
        <=counts["analyze_attempts"]<=counts["payloads_checked"]<=counts["generation_attempts"],"PROGRESS_INVALID")
    if record["status"]=="NOT_EVALUABLE":
        f=record["failure"]
        p.require(type(f) is dict and type(f.get("phase")) is str and type(f.get("code")) is str
            and f.get("work")==counts and record["streams"]==[],"FAILURE_BINDING_INVALID")
        return b.sealed(dict(status="TECHNICAL_FAILURE_RECORDED",record_digest=record["record_digest"],
            evaluation_allowed=False,read_only=True),"verification_digest")
    p.require(record["status"]=="RECORDING_COMPLETE" and record["failure"] is None
        and record["profiles"]==plan["profiles"]==b.profile_binding()
        and b.canonical(record["freeze_import"])==b.canonical(plan["freeze_import"])
        and record["sources"]==plan["sources"] and record["closed"] is True
        and len(record["streams"])==6 and len(plan["sources"])==30,"COMPLETE_BINDING_INVALID")
    frozen=plan["freeze_import"]
    p.check(frozen,"freeze_import_digest")
    p.require(frozen["profiles"]==plan["profiles"] and len(frozen["histories"])==2,"FREEZE_FORM_INVALID")
    for history,row in zip(("H1","H2"),frozen["histories"],strict=True):
        state=row["frozen_payload"]
        p.check(state,"state_digest")
        p.require(row["history_id"]==row["binding"]["history"]==history and state["phase"]=="FROZEN"
            and state["n"]==4 and state["profile_digest"]==p.PROFILE
            and type(state["alpha"]) is float and math.isfinite(state["alpha"])
            and row["alpha_binary64_hex"]==state["alpha"].hex() and len(b.canonical(state))<=4096,"FREEZE_FORM_INVALID")
    carriers=record["carriers"]
    p.require(type(carriers) is list and len(carriers)==len(set(carriers))==48
        and all(type(c) is str and c.startswith("auditory.log_hz.") for c in carriers),"CARRIERS_INVALID")
    coefficients=tuple(h["frozen_payload"]["alpha"] for h in frozen["histories"])
    states=[h["frozen_payload"]["state_digest"] for h in frozen["histories"]]
    work=dict.fromkeys(p.verification_limits(),0)
    expected_counts=dict.fromkeys(p.limits(),0)
    for s,stream in enumerate(record["streams"]):
        p.check(stream,"stream_digest")
        sources=plan["sources"][s*5:s*5+5]
        p.require(stream["stream_id"]==sources[0]["stream_id"] and len(stream["windows"])==5
            and len(stream["sites"])==3 and stream["closed"] is True,"STREAM_BINDING_INVALID")
        values=[]
        for row,source in zip(stream["windows"],sources,strict=True):
            try:
                values.append(old.verify_window(row,source,plan["profiles"],record["carriers"]))
            except p.nw.S2NWLearningError as exc:
                raise p.S2NYPredictionError(exc.code) from exc
            work["halvings"]+=48
            work["windows"]+=1
        previous=None
        for k,site in enumerate(stream["sites"],2):
            p.check(site,"site_digest")
            binding=site["prediction_binding"]
            p.check(binding,"binding_digest")
            meta=dict(stream_id=stream["stream_id"],target=k,origin=k-1,completed_analyses_before=s*5+k,
                prefix_digests=[r["window_digest"] for r in stream["windows"][:k]],freeze_import_digest=frozen["freeze_import_digest"])
            p.require({key:v for key,v in binding.items() if key not in ("primary","direct","error_evidence","binding_digest")}==meta,"PREFIX_BINDING_INVALID")
            p.require(site["target_window_digest"]==stream["windows"][k]["window_digest"]
                and site["completed_analyses_after"]==s*5+k+1,"TARGET_BINDING_INVALID")
            for arm in ("primary","direct"):
                errors=None
                evidence=None
                if previous is not None:
                    evidence=[dict(history=h,state_digest=states[j],stream_id=stream["stream_id"],target=k-1,
                        site_digest=previous["site_digest"],target_window_digest=previous["target_window_digest"],
                        score_digest=b.digest(previous[arm]["scores"][h]),mae=previous[arm]["scores"][h]["mae"])
                        for j,h in enumerate(("H1","H2"))]
                    errors=tuple(row["mae"] for row in evidence)
                p.require(b.canonical(binding["error_evidence"][arm])==b.canonical(evidence),"ERROR_PROVENANCE_INVALID")
                output=direct_predict(coefficients,tuple(values[max(0,k-3):k]),errors)
                scored=direct_score(output,values[k])
                p.require(b.canonical(binding[arm])==b.canonical(output),"PREDICTION_INVALID")
                p.require(b.canonical(site[arm])==b.canonical(scored),"SCORE_INVALID")
                # Counts are checked separately from whether a recommendation succeeds.
                n=3 if k==2 else 4
                step=dict(prediction_subtractions=(n-1)*48,prediction_multiplications=(n-1)*48,
                    prediction_additions=(n-1)*48,persist_copies=48,local_fits=int(k>2),
                    local_divisions=int(k>2 and output["local"]["division_performed"]),
                    local_differences=96 if k>2 else 0,local_products=96 if k>2 else 0,local_additions=96 if k>2 else 0,
                    error_terms=n*48,mae_sums=n,recommendations=1,gains=n-1+(n if output["recommendation"]["history"] else 0))
                for key,num in step.items():
                    work[key]+=num
                    expected_counts[arm+"_"+key]+=num
            p.require(b.canonical(binding["primary"])==b.canonical(binding["direct"])
                and b.canonical(site["primary"])==b.canonical(site["direct"]),"BASELINE_DIFFERS")
            previous=site
            work["sites"]+=1
    for key in ("generation_attempts","payloads_checked","analyze_attempts","analyze_returns","nj_attempts","nj_returns","completed_windows"):
        expected_counts[key]=30
    expected_counts["bound_sites"]=18
    p.require(counts==expected_counts,"COMPLETE_COUNTERS_INVALID")
    p.count_form(work,p.verification_limits())
    return b.sealed(dict(status="S2NY_PREDICTION_VERIFIED",record_digest=record["record_digest"],
        execution_digest=plan["execution_digest"],work=work,evaluation_allowed=True,read_only=True,baseline_equal=True,
        payload_regenerations=0,receptor_calls=0,nj_calls=0,chronology_independently_proven=False),"verification_digest")
