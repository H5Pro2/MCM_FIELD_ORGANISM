"""Offline NU raw-to-half verification; no receptor, NJ or source-pair calls."""
import hashlib
import json
import math
import struct
import sys

from tools import _s2nu_private_receptor_materialization as m
from tools import _s2nu_private_source_binding as b


def sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,
        allow_nan=False).encode("ascii")).hexdigest()


def check_root(value,key):
    m.require(type(value) is dict and value.get(key) == sha({k:v for k,v in value.items() if k != key}),"EVIDENCE_DIGEST_INVALID")


def inspect_record(out):
    file_before = b.filehash(out/"result.json")
    data = (out/"result.json").read_bytes()
    result = json.loads(data)
    m.require(len(data) <= 2097152 and b.canonical(result) == data,"RESULT_FORM_INVALID")
    check_root(result,"record_digest")
    m.require(result["schema"] == "s2nu.receptor-nj-materialization.v1" and result["run_id"] == out.name == m.RUN_ID
        and result["execution_digest"] == m.EXECUTION_DIGEST and result["seal_digest"] == m.SEAL_DIGEST,"RUN_BINDING_INVALID")
    complete = result["status"] == "RECEPTOR_NJ_MATERIALIZATION_COMPLETE"
    m.require(complete or result["status"] == "NOT_EVALUABLE","STATUS_INVALID")
    m.require(result["failure"] is None if complete else type(result["failure"]) is dict
        and type(result["failure"].get("phase")) is str,"FAILURE_STATUS_INVALID")
    execution = m.read_root(m.PRESEAL/"execution-plan.json","execution_digest")
    seal = m.read_root(m.PRESEAL/"seal.json","seal_digest")
    m.require(execution["execution_digest"] == m.EXECUTION_DIGEST == seal["execution_digest"]
        and seal["seal_digest"] == m.SEAL_DIGEST,"PLAN_CHANGED")
    hashes = result["source_hashes_before"]
    m.require(hashes == result["source_hashes_after"] and all(b.filehash(b.ROOT/p) == h for p,h in hashes.items()),"INPUT_FILES_CHANGED")
    if complete:
        m.require(hashes == m.watched(),"INPUT_INVENTORY_INVALID")
    if (out/"preregistration.json").exists():
        pre = json.loads((out/"preregistration.json").read_bytes())
        m.require(pre["source_hashes"] == hashes and pre["run_id"] == m.RUN_ID
            and pre["execution_digest"] == m.EXECUTION_DIGEST and pre["seal_digest"] == m.SEAL_DIGEST
            and pre["source_order"] == execution["source_order"] and pre["profiles"] == execution["profiles"]
            and pre["vector_pair_comparisons_authorized"] is False and pre["order_evaluation_authorized"] is False,
            "PREREGISTRATION_INVALID")
        m.require(pre["verification_limits"] == dict(records=30,forward_halvings=1440,values_per_scale=1440,
            temporal_terms=0,step_sums=0,total_variation_sums=0,endpoint_distances=0,multiset_comparisons=0,order_checks=0)
            and pre["verification_calls_limit"] == 1 and pre["byte_equal_sources_analyzed_separately"] is True,
            "VERIFICATION_LIMITS_INVALID")
    else:
        m.require(not complete and result["counts"]["analyze_attempts"] == 0,"PREREGISTRATION_MISSING")
    profile = result["profile"]
    if result["numpy_loaded"] is not None:
        loaded = result["numpy_loaded"]
        m.require(loaded["version"] == execution["environment"]["numpy"]["version"]
            and loaded["sha256"] == execution["environment"]["numpy"]["files"].get(loaded["path"]),
            "NUMPY_BINDING_INVALID")
    if complete:
        m.require(profile is not None and result["numpy_loaded"] is not None
            and execution["environment"] == b.environment(),"ENVIRONMENT_BINDING_INVALID")
    if profile is not None:
        check_root(profile,"profile_digest")
        m.require(profile["bound_profiles"] == execution["profiles"] == b.profile_binding()
            and profile["config"] == execution["profiles"]["raw"]["config"],"PROFILE_INVALID")
        m.require(len(profile["carriers"]) == len(profile["bands"]) == 48
            and len(set(profile["carriers"])) == 48
            and [band["channel_id"] for band in profile["bands"]] == profile["carriers"],"CARRIER_FORM_INVALID")
    m.require(type(result["states"]) is list and len(result["states"]) <= 30,"STATE_COUNT_INVALID")
    checked = 0
    for source,row in zip(execution["sources"],result["states"]):
        check_root(row,"materialized_state_digest")
        for key in ("source_id","ordinal","source_digest","recipe_digest","pcm_sha256","clock_id"):
            m.require(row[key] == source[key],"SOURCE_BINDING_INVALID")
        m.require(row["payload_hash_checked_before_analysis"] is True,"PAYLOAD_CHECK_ORDER_INVALID")
        state,proj = row["raw_state"],row["projection"]
        m.require(sha(state) == row["raw_state_digest"],"RAW_STATE_DIGEST_INVALID")
        check_root(proj,"projection_digest")
        m.require(len(b.canonical(proj)) <= 16384,"NJ_SIZE_INVALID")
        raw,half = state["energy"],proj["values"]
        m.require(type(raw) is list and type(half) is list and len(raw) == len(half) == 48
            and all(type(x) is float and math.isfinite(x) and x >= 0 for x in raw)
            and all(type(x) is float and math.isfinite(x) and 0 <= x <= 1 for x in half),"VALUE_FORM_INVALID")
        for key,expected in (("snapshot_index",source["nj_snapshot_index"]),
            ("window_start_sample",source["window_start_sample"]),("window_end_sample",source["window_end_sample"])):
            m.require(type(state[key]) is int and state[key] == expected,"RAW_TIME_INVALID")
        start,end = state["window_start_sample"],state["window_end_sample"]
        m.require(start >= 0 and start % 480 == 0 and state["snapshot_index"] == start//480
            and end == start+4800,"NATIVE_INDEX_INVALID")
        m.require(state["modality_id"] == "auditory" and state["geometry_id"] == execution["profiles"]["raw"]["geometry_id"]
            and state["carrier_ids"] == proj["carrier_ids"] == profile["carriers"],"RAW_GEOMETRY_INVALID")
        m.require(state["contact"] == ("active_energy" if any(x != 0 for x in raw) else "active_zero"),"ACTIVITY_FLAG_INVALID")
        m.require(proj["source_state_digest"] == row["raw_state_digest"]
            and proj["source_values_digest"] == row["raw_values_digest"] == sha(raw)
            and proj["source_profile_digest"] == execution["profiles"]["raw_profile_digest"]
            and proj["profile_digest"] == execution["profiles"]["half_profile_digest"]
            and proj["profile_id"] == execution["profiles"]["half"]["profile_id"]
            and proj["geometry_id"] == execution["profiles"]["half"]["geometry_id"],"PROJECTION_BINDING_INVALID")
        m.require(proj["clock_id"] == source["clock_id"] == "audio.sample"
            and type(proj["snapshot_index"]) is int and proj["snapshot_index"] == source["nj_snapshot_index"]
            and type(proj["window_start_tick"]) is int and proj["window_start_tick"] == start
            and type(proj["window_end_tick"]) is int and proj["window_end_tick"] == end,"PROJECTION_TIME_INVALID")
        m.require(row["raw_values_hex"] == [x.hex() for x in raw] and row["half_values_hex"] == [x.hex() for x in half],"BINARY64_HEX_INVALID")
        for values,key in ((raw,"raw_values_f64le_sha256"),(half,"half_values_f64le_sha256")):
            m.require(hashlib.sha256(struct.pack("<48d",*values)).hexdigest() == row[key],"BINARY_DIGEST_INVALID")
        # Forward check of each saved raw value only; no inverse reconstruction.
        for x,z in zip(raw,half,strict=True):
            m.require(struct.pack("<d",x*0.5) == struct.pack("<d",z),"HALF_MULTIPLICATION_DIFFERS")
            checked += 1
        for flags in (row["raw_subnormal_band_indices"],proj["subnormal_band_indices"],proj["underflow_band_indices"]):
            m.require(type(flags) is list and all(type(i) is int and 0 <= i < 48 for i in flags)
                and flags == sorted(set(flags)),"MARKER_FORM_INVALID")
        m.require(row["raw_subnormal_band_indices"] == [i for i,x in enumerate(raw) if 0 < x < sys.float_info.min]
            and proj["subnormal_band_indices"] == [i for i,z in enumerate(half) if 0 < z < sys.float_info.min]
            and proj["underflow_band_indices"] == [i for i,(x,z) in enumerate(zip(raw,half)) if x > 0 and z == 0],"NUMERIC_MARKERS_INVALID")
    c = result["counts"]
    m.require(all(type(n) is int and n >= 0 for n in c.values()),"COUNTER_FORM_INVALID")
    m.require(c["completed_sources"] == len(result["states"]) <= c["nj_returns"] <= c["nj_attempts"]
        <= c["analyze_returns"] <= c["analyze_attempts"] <= c["payloads_validated"] <= c["generation_attempts"] <= 30,"PROGRESS_INVALID")
    if complete:
        m.require(all(c[k] == 30 for k in ("generation_attempts","payloads_validated","analyze_attempts","analyze_returns",
            "nj_attempts","nj_returns","completed_sources")) and c["raw_value_count"] == c["half_value_count"] == checked == 1440,"COUNTERS_INVALID")
    for key in ("rolling_hops","contact_frame_calls","pcm_payloads_persisted","distance_calls","vector_pair_comparisons",
        "order_criteria_evaluated","memory_calls","field_calls","context_calls","runtime_calls"):
        m.require(c[key] == 0,"FORBIDDEN_CALLS")
    m.require(result["main_gate_after"] is False and result["source_gate_after"] is False
        and m.MAIN_GATE is False and b.MAIN_GATE is False and m.io.MAIN_GATE is False,"GATE_INVALID")
    file_after = b.filehash(out/"result.json")
    m.require(file_before == file_after,"RESULT_CHANGED")
    return dict(run_id=m.RUN_ID,status="S2NU_MATERIALIZATION_VALID" if complete else "TECHNICAL_FAILURE_RECORDED",
        verification_calls=1,read_only=True,record_digest=result["record_digest"],file_sha256_before=file_before,
        file_sha256_after=file_after,materialized_sources=len(result["states"]),half_values_checked=checked,
        numeric_checks=["finite_domains","binary64_hex_and_bytes","forward_raw_times_half_bitwise","subnormal_and_underflow_markers"],
        binding_checks=["source_payload_hash_links","native_indices_and_windows","profiles_and_carriers","state_projection_digests",
            "code_hashes","complete_counts","record_size_and_immutability"],
        payload_regeneration_calls=0,receptor_calls=0,nj_projection_calls=0,fft_filterbank_recomputed=False,
        pcm_hash_recomputed=False,raw_reconstructed_from_half=False,distance_calls=0,vector_pair_comparisons=0,order_criteria_evaluated=0)


def verify_once(out):
    with (out/"verification.claim").open("xb"):
        pass
    try:
        report = inspect_record(out)
    except Exception as exc:
        report = dict(run_id=m.RUN_ID,status="NOT_EVALUABLE",phase="READ_ONLY_VERIFICATION",
            error_class=type(exc).__name__,code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),
            verification_calls=1,retry=False)
    result = b.sealed(report,"verification_digest")
    b.publish(out/"verification.json",result,262144)
    return result
