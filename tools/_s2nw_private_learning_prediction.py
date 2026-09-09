"""Bound scalar transition learner; no source or future access."""
from dataclasses import asdict, dataclass
import math
import sys
from tools import _s2nw_private_source_binding as b
from tools import _s2nv_private_prediction as historical

PROFILE = historical.PROFILE
MAX_OUTPUT_BYTES = 2097152
MAX_VERIFICATION_BYTES = 262144
ARMS = ("LEARNED_DELTA", "LINEAR", "PERSIST")
BASELINES = ("PERSIST", "LINEAR")
bits = historical.bits


class S2NWLearningError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NWLearningError(code)


def vector(v, perception=True):
    require(type(v) is tuple and len(v) == 48 and all(type(x) is float and math.isfinite(x)
        and (not perception or 0.0 <= x <= 1.0) for x in v), "VECTOR_INVALID")


def check_root(obj, key):
    require(type(obj) is dict and obj.get(key) == b.digest({k:v for k,v in obj.items() if k != key}), "DIGEST_INVALID")


def sha(value):
    return type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


@dataclass(frozen=True, slots=True)
class LearningState:
    profile_digest: str
    n: int
    Sxx: float
    Sxy: float
    alpha: float
    phase: str
    predecessor: str | None
    observation_digest: str | None

    def __post_init__(self):
        require(self.profile_digest == PROFILE, "PROFILE_INVALID")
        require(type(self.n) is int and 0 <= self.n <= 4 and self.phase in ("TRAIN","FROZEN","CLOSED"), "STATE_PHASE_INVALID")
        require(all(type(x) is float and math.isfinite(x) for x in (self.Sxx,self.Sxy,self.alpha))
            and 0 <= self.Sxx <= 192 and abs(self.Sxy) <= 192, "STATE_VALUES_INVALID")
        require((self.predecessor is None or sha(self.predecessor))
            and (self.observation_digest is None or sha(self.observation_digest)), "STATE_CHAIN_INVALID")
        if self.n == 0:
            require(self.phase == "TRAIN" and self.predecessor is None and self.observation_digest is None
                and all(x.hex() == "0x0.0p+0" for x in (self.Sxx,self.Sxy,self.alpha)), "INITIAL_STATE_INVALID")
        else:
            require(sha(self.predecessor) and sha(self.observation_digest), "STATE_CHAIN_INVALID")
        require(self.phase == "TRAIN" or self.n == 4, "STATE_PHASE_INVALID")

    def payload(self):
        self.__post_init__()
        obj = b.sealed(dict(schema="s2nw.learning-state.v1", **asdict(self)), "state_digest")
        require(len(b.canonical(obj)) <= 4096, "STATE_SIZE_INVALID")
        return obj


def initial():
    return LearningState(PROFILE,0,0.0,0.0,0.0,"TRAIN",None,None)


def update(state, previous, last, target, observation_digest):
    require(type(state) is LearningState, "STATE_TYPE_INVALID")
    state.__post_init__()
    require(state.phase == "TRAIN" and state.n < 4, "UPDATE_PHASE_INVALID")
    require(sha(observation_digest), "OBSERVATION_BINDING_INVALID")
    for v in (previous,last,target):
        vector(v)
    xx,xy = state.Sxx,state.Sxy
    subnormal,underflow = [],[]
    for i in range(48):
        x = last[i]-previous[i]
        y = target[i]-last[i]
        square = x*x
        cross = x*y
        if any(0 < abs(a) < sys.float_info.min for a in (x,y,square,cross)):
            subnormal.append(i)
        if (x != 0 and square == 0) or (x != 0 and y != 0 and cross == 0):
            underflow.append(i)
        xx = xx+square
        xy = xy+cross
    alpha = xy/xx if xx > 0.0 else 0.0
    result = LearningState(PROFILE,state.n+1,xx,xy,alpha,"TRAIN",state.payload()["state_digest"],observation_digest)
    return result,dict(subnormal_indices=subnormal,product_underflow_indices=underflow,zero_denominator=xx == 0.0,
                       division_performed=xx > 0.0)


def transition(state, phase):
    require(type(state) is LearningState, "STATE_TYPE_INVALID")
    state.__post_init__()
    require(state.n == 4 and (state.phase,phase) in (("TRAIN","FROZEN"),("FROZEN","CLOSED")), "FREEZE_PHASE_INVALID")
    return LearningState(PROFILE,state.n,state.Sxx,state.Sxy,state.alpha,phase,state.payload()["state_digest"],state.observation_digest)


@dataclass(frozen=True, slots=True)
class LearnedInput:
    half_profile_digest: str
    alpha: float
    previous_values: tuple[float, ...]
    last_values: tuple[float, ...]

    def __post_init__(self):
        require(self.half_profile_digest == PROFILE, "PROFILE_INVALID")
        require(type(self.alpha) is float and math.isfinite(self.alpha), "COEFFICIENT_INVALID")
        vector(self.previous_values)
        vector(self.last_values)


def learned(value):
    require(type(value) is LearnedInput, "INPUT_TYPE_INVALID")
    value.__post_init__()
    result = []
    for i in range(48):
        d = value.last_values[i]-value.previous_values[i]
        scaled = value.alpha*d
        result.append(value.last_values[i]+scaled)
    vector(tuple(result),False)
    return tuple(result)


def predictions(value):
    value.__post_init__()
    return dict(LEARNED_DELTA=list(learned(value)),
        LINEAR=list(historical.linear(historical.LinearInput(PROFILE,value.previous_values,value.last_values))),
        PERSIST=list(historical.persist(historical.PersistInput(PROFILE,value.last_values))))


def score(prediction, target):
    vector(prediction,False)
    vector(target)
    terms = [abs(prediction[i]-target[i]) for i in range(48)]
    mae = sum(terms)/48
    require(math.isfinite(mae), "ERROR_NONFINITE")
    return dict(terms=[dict(original_index=i,value=x) for i,x in enumerate(terms)],mae=mae)


def work_limits():
    result = dict(generation_attempts=26,payloads_checked=26,analyze_attempts=26,analyze_returns=26,
        nj_attempts=26,nj_returns=26,completed_windows=26,bound_sites=16,
        raw_payloads_persisted=0,rolling_hops=0,memory_calls=0,field_calls=0,context_calls=0,runtime_calls=0)
    for arm in ("primary","direct"):
        result.update({arm+"_"+key:value for key,value in dict(
            prediction_subtractions=1536,prediction_multiplications=768,prediction_additions=1536,persist_copies=768,
            update_differences=384,update_products=384,update_additions=384,updates=4,update_divisions=4,
            error_terms=2304,mae_sums=48,gains=32).items()})
    return result


def verification_limits():
    return dict(halvings=1248,prediction_subtractions=3072,prediction_multiplications=1536,prediction_additions=3072,
        persist_copies=1536,update_differences=768,update_products=768,update_additions=768,updates=8,update_divisions=8,
        error_terms=4608,mae_sums=96,gains=64,windows=26,sites=16)


def complete_counts(counts, limits):
    require(set(counts) == set(limits) and all(type(x) is int and 0 <= x <= limits[k] for k,x in counts.items()), "COUNTERS_INVALID")
    require(all(counts[k] == v for k,v in limits.items() if not k.endswith("update_divisions")), "COMPLETE_COUNTERS_INVALID")


class Work:
    def __init__(self):
        self.values = dict.fromkeys(work_limits(),0)
        self.phase,self.source_id = "INITIALIZATION",None

    def add(self, key, n=1):
        require(type(n) is int and n >= 0 and key in self.values and self.values[key]+n <= work_limits()[key], "WORK_LIMIT_EXCEEDED")
        self.values[key] += n
