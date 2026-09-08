"""NT diagnostic pairs from already verified materializations, no sensor imports."""
from dataclasses import dataclass
import hashlib
import math
import struct
import sys

from tools import _s2nt_private_source_binding as b

canonical, digest, sealed = b.canonical, b.digest, b.sealed
MAX_OUTPUT_BYTES = 2097152
MAX_VERIFICATION_BYTES = 262144
LIMITS = dict(pairs_per_arm=25, primary_differences=1200, direct_differences=1200,
    equality_components=2400, offline_halvings=672, offline_terms=2400,
    offline_equalities=2400, offline_sums=50, offline_order_checks=24)


class S2NTComparisonError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NTComparisonError(code)


def check_root(obj,key):
    require(type(obj) is dict and obj.get(key) == digest({k:v for k,v in obj.items() if k != key}),"DIGEST_INVALID")


def validate_values(values,half=False):
    require(type(values) is tuple and len(values) == 48,"VALUE_SHAPE_INVALID")
    require(all(type(x) is float and math.isfinite(x) and x >= 0 and (not half or x <= 1) for x in values),"VALUE_DOMAIN_INVALID")


@dataclass(frozen=True, slots=True)
class Anchors:
    execution_digest: str
    materialization_digest: str
    verification_digest: str


@dataclass(frozen=True, slots=True)
class BoundSource:
    source_id: str
    materialized_digest: str
    raw: tuple[float,...]
    half: tuple[float,...]

    def __post_init__(self):
        validate_values(self.raw)
        validate_values(self.half,True)
        require(type(self.source_id) is str and type(self.materialized_digest) is str
            and len(self.materialized_digest) == 64,"SOURCE_FORM_INVALID")


def validate_pairs(plan):
    expected = [dict(pair_id=f"d{q:02d}-{r:02d}",source_id=f"nt-a{q:02d}",reference_id=f"nt-a{r:02d}") for q,r in b.PAIRS]
    require(plan.get("pairs") == expected,"PAIR_BINDING_INVALID")
    require(plan.get("diagnostic") == dict(indices=list(range(48)),arithmetic="historical sum in original index order / 48",
        threshold=None,direct_baseline=True,raw_and_half_equality_separate=True),"ARITHMETIC_BINDING_INVALID")


def bind_inputs(plan,materialization,proof,anchors):
    """Validate parent receipts without comparing any two source vectors."""
    require(type(anchors) is Anchors,"ANCHOR_TYPE_INVALID")
    for obj,key in ((plan,"execution_digest"),(materialization,"record_digest"),(proof,"verification_digest")):
        check_root(obj,key)
    require((plan["execution_digest"],materialization["record_digest"],proof["verification_digest"]) ==
        (anchors.execution_digest,anchors.materialization_digest,anchors.verification_digest),"ANCHOR_BINDING_INVALID")
    require(materialization["schema"] == "s2nt.receptor-nj-materialization.v1"
        and materialization["status"] == "RECEPTOR_NJ_MATERIALIZATION_COMPLETE" and materialization["failure"] is None
        and proof["status"] == "S2NT_MATERIALIZATION_VALID" and proof["read_only"] is True
        and proof["record_digest"] == anchors.materialization_digest and materialization["execution_digest"] == anchors.execution_digest,
        "MATERIALIZATION_NOT_VERIFIED")
    require(proof["file_sha256_before"] == proof["file_sha256_after"] == hashlib.sha256(canonical(materialization)).hexdigest()
        and proof["run_id"] == materialization["run_id"],"MATERIALIZATION_FILE_INVALID")
    require(plan["contract_sha256"] == b.PINS[b.CONTRACT] and plan["profiles"] == b.profile_binding(),"PROFILE_BINDING_INVALID")
    validate_pairs(plan)
    profile = materialization["profile"]
    check_root(profile,"profile_digest")
    require(profile["bound_profiles"] == plan["profiles"] and profile["config"] == plan["profiles"]["raw"]["config"]
        and len(profile["carriers"]) == len(set(profile["carriers"])) == 48,"PROFILE_BINDING_INVALID")
    require(len(plan["sources"]) == len(materialization["states"]) == 14
        and plan["source_order"] == [f"nt-a{i:02d}" for i in range(1,15)],"SOURCE_COUNT_INVALID")
    require(materialization["source_hashes_before"] == materialization["source_hashes_after"],"SOURCE_FILES_CHANGED")
    result = []
    for spec,source,row in zip(b.source_specs(),plan["sources"],materialization["states"],strict=True):
        require(source == b.bind_source(spec,source["pcm_sha256"]),"SOURCE_BINDING_INVALID")
        rawstate,p = row["raw_state"],row["projection"]
        raw,half = tuple(rawstate["energy"]),tuple(p["values"])
        validate_values(raw)
        validate_values(half,True)
        check_root(row,"materialized_state_digest")
        check_root(p,"projection_digest")
        require(all(row[k] == source[k] for k in ("source_id","ordinal","source_digest","recipe_digest","pcm_sha256","clock_id"))
            and row["payload_hash_checked_before_analysis"] is True,"SOURCE_BINDING_INVALID")
        require(row["raw_state_digest"] == p["source_state_digest"] == digest(rawstate)
            and row["raw_values_digest"] == p["source_values_digest"] == digest(list(raw)),"RAW_BINDING_INVALID")
        require(p["profile_id"] == plan["profiles"]["half"]["profile_id"]
            and p["profile_digest"] == plan["profiles"]["half_profile_digest"]
            and p["source_profile_digest"] == plan["profiles"]["raw_profile_digest"]
            and p["geometry_id"] == plan["profiles"]["half"]["geometry_id"]
            and rawstate["modality_id"] == "auditory" and rawstate["geometry_id"] == plan["profiles"]["raw"]["geometry_id"]
            and rawstate["carrier_ids"] == p["carrier_ids"] == profile["carriers"],"PROFILE_BINDING_INVALID")
        start,end,index = source["window_start_sample"],source["window_end_sample"],source["nj_snapshot_index"]
        require(rawstate["snapshot_index"] == p["snapshot_index"] == index and type(rawstate["snapshot_index"]) is type(p["snapshot_index"]) is int
            and all(type(x) is int for x in (rawstate["window_start_sample"],rawstate["window_end_sample"],p["window_start_tick"],p["window_end_tick"]))
            and rawstate["window_start_sample"] == p["window_start_tick"] == start
            and rawstate["window_end_sample"] == p["window_end_tick"] == end
            and p["clock_id"] == source["clock_id"] == "audio.sample","TIME_BINDING_INVALID")
        require(rawstate["contact"] == ("active_energy" if any(raw) else "active_zero"),"ACTIVITY_INVALID")
        for values,hexkey,bytekey in ((raw,"raw_values_hex","raw_values_f64le_sha256"),(half,"half_values_hex","half_values_f64le_sha256")):
            require(row[hexkey] == [x.hex() for x in values]
                and row[bytekey] == hashlib.sha256(struct.pack("<48d",*values)).hexdigest(),"VALUE_BYTES_INVALID")
        for flags,expected in ((row["raw_subnormal_band_indices"],[i for i,x in enumerate(raw) if 0 < x < sys.float_info.min]),
            (p["subnormal_band_indices"],[i for i,x in enumerate(half) if 0 < x < sys.float_info.min]),
            (p["underflow_band_indices"],[i for i,(x,z) in enumerate(zip(raw,half)) if x > 0 and z == 0])):
            require(type(flags) is list and all(type(i) is int for i in flags) and flags == expected,"MARKER_BINDING_INVALID")
        result.append(BoundSource(source["source_id"],row["materialized_state_digest"],raw,half))
    c = materialization["counts"]
    require(all(type(x) is int and x >= 0 for x in c.values()),"COUNTERS_INVALID")
    require(all(c[k] == 0 for k in ("rolling_hops","contact_frame_calls","pcm_payloads_persisted","distance_calls",
        "vector_pair_comparisons","order_criteria_evaluated","memory_calls","field_calls","context_calls","runtime_calls")),"FORBIDDEN_CALLS")
    require(all(c[k] == 14 for k in ("generation_attempts","payloads_validated","analyze_attempts","analyze_returns","nj_attempts","nj_returns","completed_sources"))
        and c["raw_value_count"] == c["half_value_count"] == proof["half_values_checked"] == 672,"COUNTERS_INVALID")
    require(proof["materialized_sources"] == 14 and proof["verification_calls"] == 1
        and materialization["main_gate_after"] is False and materialization["source_gate_after"] is False,"VERIFICATION_BINDING_INVALID")
    return tuple(result)


def compare_pair(pair,q,r):
    require(type(q) is BoundSource and type(r) is BoundSource,"INPUT_TYPE_INVALID")
    q.__post_init__()
    r.__post_init__()
    require((pair["source_id"],pair["reference_id"]) == (q.source_id,r.source_id),"PAIR_SOURCE_INVALID")
    terms = tuple(abs(q.half[i]-r.half[i]) for i in range(48))
    raw_different = [i for i in range(48) if struct.pack("<d",q.raw[i]) != struct.pack("<d",r.raw[i])]
    half_different = [i for i in range(48) if struct.pack("<d",q.half[i]) != struct.pack("<d",r.half[i])]
    return sealed(dict(**pair,source_state_digest=q.materialized_digest,reference_state_digest=r.materialized_digest,
        terms=[dict(original_index=i,value=t) for i,t in enumerate(terms)],mean=sum(terms)/48,
        raw_different_indices=raw_different,half_different_indices=half_different,
        raw_equal=not raw_different,half_equal=not half_different),"pair_digest")


def compare_all(plan,materialization,proof,anchors):
    from tools._s2nt_private_comparison_verification import direct_pair
    sources = bind_inputs(plan,materialization,proof,anchors)
    by_id = {s.source_id:s for s in sources}
    primary,direct = [],[]
    for pair in plan["pairs"]:
        q,r = by_id[pair["source_id"]],by_id[pair["reference_id"]]
        primary.append(compare_pair(pair,q,r))
        direct.append(direct_pair(pair,q,r))
    record = sealed(dict(schema="s2nt.diagnostic-comparison.v1",status="RECORDING_COMPLETE",
        inputs=dict(plan=plan,materialization=materialization,verification=proof),
        primary=primary,direct=direct,work=dict(primary_differences=1200,direct_differences=1200,equality_components=2400),
        limits=LIMITS,evaluation=None),"comparison_digest")
    require(len(canonical(record)) <= MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
    return record
