"""NU temporal views from already verified materializations, no sensor imports."""
from dataclasses import dataclass
import hashlib
import math
import struct
import sys

from tools import _s2nu_private_source_binding as b

canonical, digest, sealed = b.canonical, b.digest, b.sealed
MAX_OUTPUT_BYTES = 2097152
MAX_VERIFICATION_BYTES = 262144
LIMITS = dict(primary_differences=1440,direct_differences=1440,
    primary_equalities=336,direct_equalities=336,offline_halvings=1440,
    offline_terms=2880,offline_equalities=672,offline_sums=72,order_checks=5)


class S2NUComparisonError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NUComparisonError(code)


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


def validate_plan(plan):
    require(plan.get("controls") == b.controls() and plan.get("indices") == list(range(48))
        and plan.get("arithmetic") == "binary64; Python builtin sum in ascending band and time order; no tolerance"
        and plan.get("cross_stream_deltas") is False and plan.get("budgets") == b.budgets(),
        "CONTROL_PLAN_INVALID")


def bind_inputs(plan,materialization,proof,anchors):
    """Validate parent receipts without comparing any two source vectors."""
    require(type(anchors) is Anchors,"ANCHOR_TYPE_INVALID")
    for obj,key in ((plan,"execution_digest"),(materialization,"record_digest"),(proof,"verification_digest")):
        check_root(obj,key)
    require((plan["execution_digest"],materialization["record_digest"],proof["verification_digest"]) ==
        (anchors.execution_digest,anchors.materialization_digest,anchors.verification_digest),"ANCHOR_BINDING_INVALID")
    require(materialization["schema"] == "s2nu.receptor-nj-materialization.v1"
        and materialization["status"] == "RECEPTOR_NJ_MATERIALIZATION_COMPLETE" and materialization["failure"] is None
        and proof["status"] == "S2NU_MATERIALIZATION_VALID" and proof["read_only"] is True
        and proof["record_digest"] == anchors.materialization_digest and materialization["execution_digest"] == anchors.execution_digest,
        "MATERIALIZATION_NOT_VERIFIED")
    require(proof["file_sha256_before"] == proof["file_sha256_after"] == hashlib.sha256(canonical(materialization)).hexdigest()
        and proof["run_id"] == materialization["run_id"],"MATERIALIZATION_FILE_INVALID")
    require(plan["contract_sha256"] == b.PINS[b.CONTRACT] and plan["profiles"] == b.profile_binding(),"PROFILE_BINDING_INVALID")
    validate_plan(plan)
    profile = materialization["profile"]
    check_root(profile,"profile_digest")
    require(profile["bound_profiles"] == plan["profiles"] and profile["config"] == plan["profiles"]["raw"]["config"]
        and len(profile["carriers"]) == len(set(profile["carriers"])) == 48,"PROFILE_BINDING_INVALID")
    require(len(plan["sources"]) == len(materialization["states"]) == 30
        and plan["source_order"] == [s.payload()["source_id"] for s in b.specs()],"SOURCE_COUNT_INVALID")
    require(materialization["source_hashes_before"] == materialization["source_hashes_after"],"SOURCE_FILES_CHANGED")
    result = []
    for spec,source,row in zip(b.specs(),plan["sources"],materialization["states"],strict=True):
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
        and c["raw_value_count"] == c["half_value_count"] == proof["half_values_checked"] == 1440,"COUNTERS_INVALID")
    require(proof["materialized_sources"] == 14 and proof["verification_calls"] == 1
        and materialization["main_gate_after"] is False and materialization["source_gate_after"] is False,"VERIFICATION_BINDING_INVALID")
    return tuple(result)


def profile_valid(profile):
    require(profile == b.profile_binding()["half_profile_digest"],"VIEW_PROFILE_INVALID")


@dataclass(frozen=True,slots=True)
class OrderedView:
    profile_digest: str
    values: tuple[tuple[float,...],...]

    def __post_init__(self):
        profile_valid(self.profile_digest)
        require(type(self.values) is tuple and len(self.values) == 5,"WINDOW_COUNT_INVALID")
        for vector in self.values:
            validate_values(vector,True)


@dataclass(frozen=True,slots=True)
class EndpointView:
    profile_digest: str
    first_values: tuple[float,...]
    last_values: tuple[float,...]

    def __post_init__(self):
        profile_valid(self.profile_digest)
        validate_values(self.first_values,True)
        validate_values(self.last_values,True)


@dataclass(frozen=True,slots=True)
class UnorderedView:
    profile_digest: str
    values_f64le_sorted: tuple[bytes,...]

    def __post_init__(self):
        profile_valid(self.profile_digest)
        items = self.values_f64le_sorted
        require(type(items) is tuple and len(items) == 5
            and all(type(x) is bytes and len(x) == 384 for x in items),"MULTISET_FORM_INVALID")
        require(items == tuple(sorted(items)),"MULTISET_ORDER_INVALID")
        for item in items:
            validate_values(struct.unpack("<48d",item),True)


def unordered_from_payload(payload):
    require(type(payload) is dict and set(payload) == {"profile_digest","values_f64le_sorted"},
        "UNORDERED_METADATA_FORBIDDEN")
    return UnorderedView(**payload)


def ordered_measure(view):
    require(type(view) is OrderedView,"VIEW_TYPE_INVALID")
    view.__post_init__()
    transitions = []
    for k in range(4):
        delta = [view.values[k+1][i]-view.values[k][i] for i in range(48)]
        transitions.append(dict(transition=k,terms=[dict(original_index=i,value=x) for i,x in enumerate(delta)],
            step=sum(abs(x) for x in delta)/48))
    return dict(transitions=transitions,T=sum(x["step"] for x in transitions))


def endpoint_measure(view):
    require(type(view) is EndpointView,"VIEW_TYPE_INVALID")
    view.__post_init__()
    terms = [abs(view.last_values[i]-view.first_values[i]) for i in range(48)]
    return dict(profile_digest=view.profile_digest,first_values=list(view.first_values),last_values=list(view.last_values),
        terms=[dict(original_index=i,value=x) for i,x in enumerate(terms)],E=sum(terms)/48)


def unordered_measure(view):
    require(type(view) is UnorderedView,"VIEW_TYPE_INVALID")
    view.__post_init__()
    return dict(profile_digest=view.profile_digest,values_f64le_sorted=[x.hex() for x in view.values_f64le_sorted])


def primary_stream(ordered,endpoints,unordered):
    return dict(ordered=ordered_measure(ordered),endpoints=endpoint_measure(endpoints),unordered=unordered_measure(unordered))


def control_equalities(rows):
    left,right = rows[1]["measurement"],rows[2]["measurement"]
    endpoint_bits = []
    for name in ("first_values","last_values"):
        endpoint_bits.extend(struct.pack("<d",x) == struct.pack("<d",y)
            for x,y in zip(left["endpoints"][name],right["endpoints"][name],strict=True))
    multiset_bits = []
    for x,y in zip(left["unordered"]["values_f64le_sorted"],right["unordered"]["values_f64le_sorted"],strict=True):
        a,z = bytes.fromhex(x),bytes.fromhex(y)
        multiset_bits.extend(a[i*8:(i+1)*8] == z[i*8:(i+1)*8] for i in range(48))
    require(len(endpoint_bits) == 96 and len(multiset_bits) == 240,"CONTROL_COUNT_INVALID")
    return dict(endpoint_bits=endpoint_bits,multiset_bits=multiset_bits,
        endpoints_equal=all(endpoint_bits),multiset_equal=all(multiset_bits),components_checked=336)


def views_for(sources,profile):
    values = tuple(s.half for s in sources)
    return (OrderedView(profile,values),EndpointView(profile,values[0],values[-1]),
        UnorderedView(profile,tuple(sorted(struct.pack("<48d",*x) for x in values))))


def compare_all(plan,materialization,proof,anchors):
    from tools import _s2nu_private_comparison_verification as direct
    sources = bind_inputs(plan,materialization,proof,anchors)
    primary,baseline = [],[]
    for n in range(6):
        group = sources[n*5:(n+1)*5]
        views = views_for(group,plan["profiles"]["half_profile_digest"])
        binding = dict(stream_id=f"s{n+1:02d}",source_ids=[s.source_id for s in group],
            materialized_digests=[s.materialized_digest for s in group])
        primary.append(sealed(dict(**binding,measurement=primary_stream(*views)),"stream_digest"))
        baseline.append(sealed(dict(**binding,measurement=direct.direct_stream(*views)),"stream_digest"))
    record = sealed(dict(schema="s2nu.temporal-comparison.v1",status="RECORDING_COMPLETE",
        inputs=dict(plan=plan,materialization=materialization,verification=proof),primary=primary,direct=baseline,
        controls=dict(primary=control_equalities(primary),direct=direct.direct_controls(baseline)),
        work=dict(primary_differences=1440,direct_differences=1440,primary_equalities=336,direct_equalities=336),
        limits=LIMITS,evaluation=None),"comparison_digest")
    require(len(canonical(record)) <= MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
    return record
