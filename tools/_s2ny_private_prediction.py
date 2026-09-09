"""Prefix-only NY arithmetic. No sources, owners or future values in predictors."""
from dataclasses import dataclass
import math
import sys
from tools import _s2nw_private_learning_prediction as nw
from tools import _s2ny_private_source_binding as b

PROFILE=nw.PROFILE
MAX_OUTPUT_BYTES=2097152
MAX_VERIFICATION_BYTES=262144


class S2NYPredictionError(ValueError):
    def __init__(self,code):
        self.code=code
        super().__init__(code)


def require(ok,code):
    if not ok:
        raise S2NYPredictionError(code)


def check(obj,key):
    require(type(obj) is dict and obj.get(key)==b.digest({k:v for k,v in obj.items() if k!=key}),"DIGEST_INVALID")


def vector(values,perception=True):
    try:
        nw.vector(values,perception)
    except nw.S2NWLearningError as exc:
        raise S2NYPredictionError(exc.code) from exc


@dataclass(frozen=True,slots=True)
class LocalInput:
    profile_digest: str
    first: tuple
    previous: tuple
    last: tuple

    def __post_init__(self):
        require(self.profile_digest==PROFILE,"PROFILE_INVALID")
        for values in (self.first,self.previous,self.last):
            vector(values)


def local_fit(value):
    require(type(value) is LocalInput,"LOCAL_INPUT_INVALID")
    value.__post_init__()
    xx,xy=0.0,0.0
    subnormal,underflow=[],[]
    for i in range(48):
        x=value.previous[i]-value.first[i]
        y=value.last[i]-value.previous[i]
        square,cross=x*x,x*y
        if any(0<abs(a)<sys.float_info.min for a in (x,y,square,cross)):
            subnormal.append(i)
        if (x!=0 and square==0) or (x!=0 and y!=0 and cross==0):
            underflow.append(i)
        xx=xx+square
        xy=xy+cross
    beta=xy/xx if xx>0.0 else 0.0
    require(all(math.isfinite(x) for x in (xx,xy,beta)),"LOCAL_NONFINITE")
    return dict(Sxx=xx,Sxy=xy,beta=beta,zero_denominator=xx==0.0,
        division_performed=xx>0.0,subnormal_indices=subnormal,product_underflow_indices=underflow)


def recommend(errors):
    if errors is None:
        return dict(status="ABSTAIN_INSUFFICIENT_PREFIX",history=None)
    require(type(errors) is tuple and len(errors)==2 and all(type(e) is float and math.isfinite(e) and e>=0 for e in errors),"ERROR_VALUES_INVALID")
    if errors[0]==errors[1]:
        return dict(status="ABSTAIN_TIE",history=None)
    return dict(status="RECOMMEND",history="H1" if errors[0]<errors[1] else "H2")


def predict(coefficients,prefix,errors):
    require(type(coefficients) is tuple and len(coefficients)==2,"FREEZE_FORM_INVALID")
    require(type(prefix) is tuple and len(prefix) in (2,3),"PREFIX_INVALID")
    for values in prefix:
        vector(values)
    require((len(prefix)==2)==(errors is None),"ERROR_EVIDENCE_MISSING")
    try:
        result={h:list(nw.learned(nw.LearnedInput(PROFILE,a,prefix[-2],prefix[-1])))
            for h,a in zip(("H1","H2"),coefficients,strict=True)}
        result["PERSIST"]=list(nw.historical.persist(nw.historical.PersistInput(PROFILE,prefix[-1])))
        local=local_fit(LocalInput(PROFILE,*prefix)) if len(prefix)==3 else None
        if local is not None:
            result["LOCAL"]=list(nw.learned(nw.LearnedInput(PROFILE,local["beta"],prefix[-2],prefix[-1])))
    except nw.S2NWLearningError as exc:
        raise S2NYPredictionError(exc.code) from exc
    return dict(predictions=result,local=local,recommendation=recommend(errors))


def score(output,target):
    vector(target)
    try:
        scores={a:nw.score(tuple(v),target) for a,v in output["predictions"].items()}
    except nw.S2NWLearningError as exc:
        raise S2NYPredictionError(exc.code) from exc
    h=output["recommendation"]["history"]
    gains={a:scores["PERSIST"]["mae"]-scores[a]["mae"] for a in scores if a!="PERSIST"}
    return dict(scores=scores,recommended_mae=None if h is None else scores[h]["mae"],
        recommendation_gains={} if h is None else {a:s["mae"]-scores[h]["mae"] for a,s in scores.items()},
        gains_vs_persist=gains)


def limits():
    result=dict(generation_attempts=30,payloads_checked=30,analyze_attempts=30,analyze_returns=30,
        nj_attempts=30,nj_returns=30,completed_windows=30,bound_sites=18,raw_payloads_persisted=0,
        rolling_hops=0,memory_calls=0,field_calls=0,context_calls=0,runtime_calls=0)
    for arm in ("primary","direct"):
        result.update({arm+"_"+k:v for k,v in dict(prediction_subtractions=2304,prediction_multiplications=2304,
            prediction_additions=2304,persist_copies=864,local_fits=12,local_divisions=12,local_differences=1152,
            local_products=1152,local_additions=1152,error_terms=3168,mae_sums=66,recommendations=18,gains=96).items()})
    return result


def verification_limits():
    return dict(halvings=1440,windows=30,sites=18,prediction_subtractions=4608,prediction_multiplications=4608,
        prediction_additions=4608,persist_copies=1728,local_fits=24,local_divisions=24,local_differences=2304,
        local_products=2304,local_additions=2304,error_terms=6336,mae_sums=132,recommendations=36,gains=192)


def step_work(output):
    local=output["local"]
    n=len(output["predictions"])
    return dict(prediction_subtractions=(n-1)*48,prediction_multiplications=(n-1)*48,
        prediction_additions=(n-1)*48,persist_copies=48,local_fits=int(local is not None),
        local_divisions=int(local is not None and local["division_performed"]),
        local_differences=96 if local is not None else 0,local_products=96 if local is not None else 0,
        local_additions=96 if local is not None else 0,error_terms=n*48,mae_sums=n,recommendations=1,
        gains=n-1+(n if output["recommendation"]["history"] is not None else 0))


def count_form(counts,bounds):
    require(type(counts) is dict and set(counts)==set(bounds)
        and all(type(v) is int and 0<=v<=bounds[k] for k,v in counts.items()),"COUNTERS_INVALID")


class Work:
    def __init__(self):
        self.values=dict.fromkeys(limits(),0)
        self.phase,self.source_id="INITIALIZATION",None

    def add(self,key,n=1):
        require(key in self.values and type(n) is int and n>=0 and self.values[key]+n<=limits()[key],"WORK_LIMIT_EXCEEDED")
        self.values[key]+=n
