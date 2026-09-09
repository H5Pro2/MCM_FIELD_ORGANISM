"""Independent arithmetic and offline verification, never source generation."""
import hashlib
import math
import struct
import sys

from tools import _s2nv_private_prediction as p

b = p.b


def direct_predictions(linear_input, persist_input):
    p.require(type(linear_input) is p.LinearInput and type(persist_input) is p.PersistInput,"INPUT_TYPE_INVALID")
    linear_input.__post_init__()
    persist_input.__post_init__()
    answer,copy = [],[]
    for i in range(48):
        previous = linear_input.previous_values[i]
        last = linear_input.last_values[i]
        delta = last-previous
        answer.append(last+delta)
        copy.append(persist_input.last_values[i])
    return dict(LINEAR_TWO_STATE=answer,PERSIST_LAST=copy)


def direct_score(prediction, target):
    p.vector(tuple(prediction),-1.0,2.0)
    p.vector(tuple(target))
    terms = []
    for i in range(48):
        d = prediction[i]-target[i]
        terms.append(dict(original_index=i,value=-d if d<0 else 0.0 if d==0 else d))
    return dict(terms=terms,mae=sum([r["value"] for r in terms])/48)


def verify_window(row, source, profiles, carriers):
    p.check_root(row,"window_digest")
    p.require(row["source_digest"]==source["source_digest"] and row["source_id"]==source["source_id"]
        and row["pcm_sha256"]==source["pcm_sha256"] and row["payload_checked_before_analysis"] is True,"SOURCE_BINDING_INVALID")
    state,projection = row["raw_state"],row["projection"]
    p.check_root(projection,"projection_digest")
    raw,half = state["energy"],projection["values"]
    p.require(type(raw) is list and len(raw)==48 and all(type(x) is float and math.isfinite(x) and x>=0 for x in raw),"RAW_VALUES_INVALID")
    p.vector(tuple(half))
    start,end,index = source["window_start_sample"],source["window_end_sample"],source["nj_snapshot_index"]
    p.require(all(type(x) is int for x in (start,end,index)) and start>=0 and start%480==0
        and index==start//480 and end==start+4800 and source["clock_id"]=="audio.sample","SOURCE_TIME_INVALID")
    expected_state = dict(modality_id="auditory",geometry_id=profiles["raw"]["geometry_id"],snapshot_index=index,
        window_start_sample=start,window_end_sample=end,carrier_ids=carriers,energy=raw,
        contact="active_energy" if any(x!=0 for x in raw) else "active_zero")
    p.require(b.canonical(state)==b.canonical(expected_state) and row["raw_state_digest"]==b.digest(state),"RAW_BINDING_INVALID")
    expected_projection = dict(profile_id=profiles["half"]["profile_id"],profile_digest=profiles["half_profile_digest"],
        geometry_id=profiles["half"]["geometry_id"],source_profile_digest=profiles["raw_profile_digest"],
        source_state_digest=row["raw_state_digest"],source_values_digest=b.digest(raw),snapshot_index=index,
        clock_id="audio.sample",window_start_tick=start,window_end_tick=end,carrier_ids=carriers,values=half,
        subnormal_band_indices=[i for i,x in enumerate(half) if 0<x<sys.float_info.min],
        underflow_band_indices=[i for i,(x,z) in enumerate(zip(raw,half,strict=True)) if x>0 and z==0])
    p.require(b.canonical(projection)==b.canonical(b.sealed(expected_projection,"projection_digest")),"PROJECTION_BINDING_INVALID")
    p.require(len(b.canonical(projection))<=16384,"PROJECTION_SIZE_INVALID")
    for label,values in (("raw",raw),("half",half)):
        p.require(row[label+"_hex"]==[x.hex() for x in values] and
            row[label+"_f64le_sha256"]==hashlib.sha256(struct.pack("<48d",*values)).hexdigest(),"VALUE_BYTES_INVALID")
    p.require(row["raw_subnormal_indices"]==[i for i,x in enumerate(raw) if 0<x<sys.float_info.min],"MARKERS_INVALID")
    for raw_value,half_value in zip(raw,half,strict=True):
        p.require(struct.pack("<d",raw_value*0.5)==struct.pack("<d",half_value),"HALVING_INVALID")
    return tuple(half)


def verify_record(record, plan):
    p.require(len(b.canonical(record))<=p.MAX_OUTPUT_BYTES,"OUTPUT_SIZE_EXCEEDED")
    p.check_root(record,"record_digest")
    p.check_root(plan,"execution_digest")
    p.require(record["schema"]=="s2nv.prospective-prediction.v1" and record["execution_digest"]==plan["execution_digest"]
        and record["evaluation"] is None and record["main_gate_after"] is False,"RECORD_BINDING_INVALID")
    p.require(record["limits"]==p.work_limits() and record["verification_limits"]==p.verification_limits(),"LIMIT_BINDING_INVALID")
    p.require(record["status"] in ("RECORDING_COMPLETE","NOT_EVALUABLE"),"STATUS_INVALID")
    counts = record["work"]
    p.require(set(counts)==set(p.work_limits()) and all(type(n) is int and 0<=n<=p.work_limits()[k] for k,n in counts.items()),"COUNTERS_INVALID")
    p.require(counts["completed_windows"]<=counts["nj_returns"]<=counts["nj_attempts"]
        <=counts["analyze_returns"]<=counts["analyze_attempts"]<=counts["payloads_checked"]
        <=counts["generation_attempts"],"PROGRESS_INVALID")
    if record["status"]=="NOT_EVALUABLE":
        fail = record["failure"]
        p.require(type(fail) is dict and type(fail.get("phase")) is str and type(fail.get("code")) is str
            and fail.get("work")==counts and record["streams"]==[],"FAILURE_BINDING_INVALID")
        return b.sealed(dict(status="TECHNICAL_FAILURE_RECORDED",record_digest=record["record_digest"],
            evaluation_allowed=False,read_only=True),"verification_digest")
    p.require(record["failure"] is None and record["profiles"]==plan["profiles"]==b.profile_binding()
        and len(record["streams"])==4 and len(plan["sources"])==20,"COMPLETE_BINDING_INVALID")
    carriers = record["carriers"]
    p.require(type(carriers) is list and len(carriers)==len(set(carriers))==48 and
        all(type(c) is str and c.startswith("auditory.log_hz.") for c in carriers),"CARRIERS_INVALID")
    work = dict.fromkeys(p.verification_limits(),0)
    for s,stream in enumerate(record["streams"]):
        p.check_root(stream,"stream_digest")
        sources = plan["sources"][s*5:(s+1)*5]
        p.require(stream["stream_id"]==sources[0]["stream_id"] and len(stream["windows"])==5
            and len(stream["sites"])==3,"STREAM_BINDING_INVALID")
        values = [verify_window(row,source,plan["profiles"],carriers) for row,source in zip(stream["windows"],sources,strict=True)]
        work["windows"]+=5
        work["halvings"]+=240
        for k,site in enumerate(stream["sites"],1):
            p.check_root(site,"site_digest")
            binding = site["prediction_binding"]
            p.check_root(binding,"binding_digest")
            p.require(binding["stream_id"]==stream["stream_id"] and binding["origin"]==k and binding["target"]==k+1
                and binding["available_windows"]==k+1 and binding["completed_analyses_before"]==s*5+k+1
                and binding["prefix_digests"]==[r["window_digest"] for r in stream["windows"][:k+1]]
                and binding["half_profile_digest"]==p.PROFILE,"PREFIX_BINDING_INVALID")
            inputs = dict(previous_values=list(values[k-1]),last_values=list(values[k]),half_profile_digest=p.PROFILE)
            p.require(b.canonical(binding["functional_prefix"])==b.canonical(inputs),"FUNCTIONAL_INPUT_INVALID")
            p.require(site["target_window_digest"]==stream["windows"][k+1]["window_digest"]
                and site["completed_analyses_after"]==s*5+k+2,"TARGET_BINDING_INVALID")
            for arm in ("primary","direct"):
                expected = direct_predictions(p.LinearInput(p.PROFILE,values[k-1],values[k]),p.PersistInput(p.PROFILE,values[k]))
                p.require(b.canonical(binding[arm])==b.canonical(expected),"PREDICTION_INVALID")
                work["prediction_subtractions"]+=48
                work["prediction_additions"]+=48
                work["persist_copies"]+=48
                scores = {name:direct_score(pred,values[k+1]) for name,pred in expected.items()}
                scores["gain"] = scores["PERSIST_LAST"]["mae"]-scores["LINEAR_TWO_STATE"]["mae"]
                p.require(b.canonical(site[arm])==b.canonical(scores),"SCORE_INVALID")
                work["error_terms"]+=96
                work["mae_sums"]+=2
                work["gains"]+=1
            p.require(b.canonical(binding["primary"])==b.canonical(binding["direct"])
                and b.canonical(site["primary"])==b.canonical(site["direct"]),"BASELINE_DIFFERS")
            work["sites"]+=1
    p.require(work==p.verification_limits() and counts==p.work_limits(),"COMPLETE_COUNTERS_INVALID")
    return b.sealed(dict(status="S2NV_PREDICTION_VERIFIED",record_digest=record["record_digest"],
        execution_digest=plan["execution_digest"],work=work,baseline_equal=True,evaluation_allowed=True,read_only=True,
        payload_regenerations=0,receptor_calls=0,nj_calls=0,raw_reconstructed_from_half=False,
        chronology_independently_proven=False),"verification_digest")
