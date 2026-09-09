"""Fixed, prefix-only predictions. No source access, clock or future metadata."""
from dataclasses import dataclass
import math
import struct

from tools import _s2nv_private_source_binding as b

PROFILE = b.profile_binding()["half_profile_digest"]
MAX_OUTPUT_BYTES = 2097152
MAX_VERIFICATION_BYTES = 262144


class S2NVPredictionError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NVPredictionError(code)


def vector(values, low=0.0, high=1.0):
    require(type(values) is tuple and len(values)==48 and all(type(x) is float and math.isfinite(x)
        and low <= x <= high for x in values),"VECTOR_INVALID")


def bits(values):
    return struct.pack("<48d",*values)


def check_root(value, key):
    require(type(value) is dict and value.get(key)==b.digest({k:v for k,v in value.items() if k!=key}),"DIGEST_INVALID")


@dataclass(frozen=True, slots=True)
class LinearInput:
    half_profile_digest: str
    previous_values: tuple[float, ...]
    last_values: tuple[float, ...]

    def __post_init__(self):
        require(self.half_profile_digest==PROFILE,"PROFILE_INVALID")
        vector(self.previous_values)
        vector(self.last_values)


@dataclass(frozen=True, slots=True)
class PersistInput:
    half_profile_digest: str
    last_values: tuple[float, ...]

    def __post_init__(self):
        require(self.half_profile_digest==PROFILE,"PROFILE_INVALID")
        vector(self.last_values)


def linear(value):
    require(type(value) is LinearInput,"INPUT_TYPE_INVALID")
    value.__post_init__()
    differences = tuple(value.last_values[i]-value.previous_values[i] for i in range(48))
    result = tuple(value.last_values[i]+differences[i] for i in range(48))
    vector(result,-1.0,2.0)
    return result


def persist(value):
    require(type(value) is PersistInput,"INPUT_TYPE_INVALID")
    value.__post_init__()
    return tuple(x for x in value.last_values)


def score(prediction, target):
    vector(prediction,-1.0,2.0)
    vector(target)
    terms = [abs(prediction[i]-target[i]) for i in range(48)]
    return dict(terms=[dict(original_index=i,value=x) for i,x in enumerate(terms)],mae=sum(terms)/48)


def work_limits():
    return dict(generation_attempts=20,payloads_checked=20,analyze_attempts=20,analyze_returns=20,
        nj_attempts=20,nj_returns=20,completed_windows=20,
        primary_prediction_subtractions=576,primary_prediction_additions=576,primary_persist_copies=576,
        direct_prediction_subtractions=576,direct_prediction_additions=576,direct_persist_copies=576,
        primary_error_terms=1152,primary_mae_sums=24,primary_gains=12,
        direct_error_terms=1152,direct_mae_sums=24,direct_gains=12,
        bound_sites=12,raw_payloads_persisted=0,rolling_hops=0,memory_calls=0,field_calls=0,
        context_calls=0,runtime_calls=0)


def verification_limits():
    return dict(halvings=960,prediction_subtractions=1152,prediction_additions=1152,persist_copies=1152,
        error_terms=2304,mae_sums=48,gains=24,windows=20,sites=12)


class Work:
    def __init__(self):
        self.values = dict.fromkeys(work_limits(),0)
        self.phase = "INITIALIZATION"
        self.source_id = None

    def add(self, key, n=1):
        require(type(n) is int and n>=0 and key in self.values
            and self.values[key]+n <= work_limits()[key],"WORK_LIMIT_EXCEEDED")
        self.values[key] += n
