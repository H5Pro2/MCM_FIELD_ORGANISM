"""Independent learner and arithmetic; offline reconstruction without source calls."""
import math
import sys
from tools import _s2nw_private_learning_prediction as p
from tools import _s2nv_private_prediction_verification as old

b = p.b


def direct_initial():
    return p.LearningState(p.PROFILE,0,0.0,0.0,0.0,"TRAIN",None,None)


def direct_update(state, previous, last, target, observation):
    state.__post_init__()
    p.require(state.phase == "TRAIN" and state.n < 4, "UPDATE_PHASE_INVALID")
    for v in (previous,last,target):
        p.vector(v)
    a,c = state.Sxx,state.Sxy
    small,zero = [],[]
    for i in range(48):
        u,v = last[i]-previous[i],target[i]-last[i]
        uu,uv = u*u,u*v
        if any(0 < abs(x) < sys.float_info.min for x in (u,v,uu,uv)):
            small.append(i)
        if (u != 0 and uu == 0) or (u != 0 and v != 0 and uv == 0):
            zero.append(i)
        a = a+uu
        c = c+uv
    coefficient = c/a if a > 0.0 else 0.0
    result = p.LearningState(p.PROFILE,state.n+1,a,c,coefficient,"TRAIN",state.payload()["state_digest"],observation)
    return result,dict(subnormal_indices=small,product_underflow_indices=zero,zero_denominator=a == 0.0,division_performed=a > 0.0)


def direct_transition(state, phase):
    state.__post_init__()
    p.require(state.n == 4 and (state.phase,phase) in (("TRAIN","FROZEN"),("FROZEN","CLOSED")), "FREEZE_PHASE_INVALID")
    return p.LearningState(p.PROFILE,state.n,state.Sxx,state.Sxy,state.alpha,phase,state.payload()["state_digest"],state.observation_digest)


def direct_predictions(value):
    p.require(type(value) is p.LearnedInput, "INPUT_TYPE_INVALID")
    value.__post_init__()
    learned,linear,persist = [],[],[]
    for i in range(48):
        a,z = value.previous_values[i],value.last_values[i]
        d = z-a
        scaled = value.alpha*d
        learned.append(z+scaled)
        linear.append(z+(z-a))
        persist.append(z)
    for v in (learned,linear,persist):
        p.vector(tuple(v),False)
    return dict(LEARNED_DELTA=learned,LINEAR=linear,PERSIST=persist)


def direct_score(prediction, target):
    p.vector(tuple(prediction),False)
    p.vector(tuple(target))
    terms = []
    for i in range(48):
        d = prediction[i]-target[i]
        terms.append(dict(original_index=i,value=-d if d < 0 else 0.0 if d == 0 else d))
    mae = sum([x["value"] for x in terms])/48
    p.require(math.isfinite(mae), "ERROR_NONFINITE")
    return dict(terms=terms,mae=mae)


def verify_window(*args):
    try:
        return old.verify_window(*args)
    except old.p.S2NVPredictionError as exc:
        raise p.S2NWLearningError(exc.code) from exc


def verify_record(record, plan):
    p.require(len(b.canonical(record)) <= p.MAX_OUTPUT_BYTES, "OUTPUT_SIZE_EXCEEDED")
    p.check_root(record,"record_digest")
    p.check_root(plan,"execution_digest")
    p.require(record["schema"] == "s2nw.learned-prediction.v1" and record["execution_digest"] == plan["execution_digest"]
        and record["evaluation"] is None and record["main_gate_after"] is False, "RECORD_BINDING_INVALID")
    p.require(record["limits"] == p.work_limits() and record["verification_limits"] == p.verification_limits(), "LIMIT_BINDING_INVALID")
    counts = record["work"]
    p.require(set(counts) == set(p.work_limits()) and all(type(n) is int and 0 <= n <= p.work_limits()[k] for k,n in counts.items()), "COUNTERS_INVALID")
    p.require(counts["completed_windows"] <= counts["nj_returns"] <= counts["nj_attempts"] <= counts["analyze_returns"]
        <= counts["analyze_attempts"] <= counts["payloads_checked"] <= counts["generation_attempts"], "PROGRESS_INVALID")
    if record["status"] == "NOT_EVALUABLE":
        fail = record["failure"]
        p.require(type(fail) is dict and type(fail.get("phase")) is str and type(fail.get("code")) is str
            and fail.get("work") == counts and record["streams"] == [] and record.get("learning") is None, "FAILURE_BINDING_INVALID")
        return b.sealed(dict(status="TECHNICAL_FAILURE_RECORDED",record_digest=record["record_digest"],evaluation_allowed=False,read_only=True),"verification_digest")
    p.require(record["status"] == "RECORDING_COMPLETE" and record["failure"] is None
        and record["profiles"] == plan["profiles"] == b.profile_binding()
        and len(record["streams"]) == 5 and len(plan["sources"]) == 26, "COMPLETE_BINDING_INVALID")
    carriers = record["carriers"]
    p.require(type(carriers) is list and len(carriers) == len(set(carriers)) == 48
        and all(type(c) is str and c.startswith("auditory.log_hz.") for c in carriers), "CARRIERS_INVALID")
    work = dict.fromkeys(p.verification_limits(),0)
    states = {arm:direct_initial() for arm in ("primary","direct")}
    p.require(record["learning"]["initial"] == {arm:s.payload() for arm,s in states.items()}, "INITIAL_BINDING_INVALID")
    divisions = dict(primary=0,direct=0)
    for s,(offset,length) in enumerate(((0,6),(6,5),(11,5),(16,5),(21,5))):
        stream = record["streams"][s]
        p.check_root(stream,"stream_digest")
        sources = plan["sources"][offset:offset+length]
        p.require(stream["stream_id"] == sources[0]["stream_id"] and len(stream["windows"]) == length
            and len(stream["sites"]) == length-2, "STREAM_BINDING_INVALID")
        values = [verify_window(row,src,plan["profiles"],carriers) for row,src in zip(stream["windows"],sources,strict=True)]
        work["windows"] += length
        work["halvings"] += length*48
        for k,site in enumerate(stream["sites"],1):
            p.check_root(site,"site_digest")
            binding = site["prediction_binding"]
            p.check_root(binding,"binding_digest")
            expected_states = {arm:state.payload() for arm,state in states.items()}
            p.require(b.canonical(binding["learning_before"]) == b.canonical(expected_states), "LEARNING_CHAIN_INVALID")
            p.require(binding["stream_id"] == stream["stream_id"] and binding["origin"] == k and binding["target"] == k+1
                and binding["available_windows"] == k+1 and binding["completed_analyses_before"] == offset+k+1
                and binding["phase"] == ("TRAIN" if s == 0 else "FROZEN")
                and binding["prefix_digests"] == [r["window_digest"] for r in stream["windows"][:k+1]], "PREFIX_BINDING_INVALID")
            expected_prefix = dict(half_profile_digest=p.PROFILE,previous_values=list(values[k-1]),last_values=list(values[k]))
            p.require(b.canonical(binding["functional_prefix"]) == b.canonical(expected_prefix), "FUNCTIONAL_INPUT_INVALID")
            p.require(site["target_window_digest"] == stream["windows"][k+1]["window_digest"]
                and site["completed_analyses_after"] == offset+k+2, "TARGET_BINDING_INVALID")
            for arm in ("primary","direct"):
                expected = direct_predictions(p.LearnedInput(p.PROFILE,states[arm].alpha,values[k-1],values[k]))
                p.require(b.canonical(binding[arm]) == b.canonical(expected), "PREDICTION_INVALID")
                work["prediction_subtractions"] += 96
                work["prediction_multiplications"] += 48
                work["prediction_additions"] += 96
                work["persist_copies"] += 48
                scores = {name:direct_score(pred,values[k+1]) for name,pred in expected.items()}
                scores["gains"] = {name:scores[name]["mae"]-scores["LEARNED_DELTA"]["mae"] for name in p.BASELINES}
                p.require(b.canonical(site[arm]) == b.canonical(scores), "SCORE_INVALID")
                work["error_terms"] += 144
                work["mae_sums"] += 3
                work["gains"] += 2
            observation = b.digest(dict(binding_digest=binding["binding_digest"],target_window_digest=site["target_window_digest"],
                completed_analyses_after=site["completed_analyses_after"],primary_score_digest=b.digest(site["primary"]),direct_score_digest=b.digest(site["direct"])))
            if s == 0:
                updated,markers = {},{}
                for arm in ("primary","direct"):
                    new,mark = direct_update(states[arm],values[k-1],values[k],values[k+1],observation)
                    states[arm],updated[arm],markers[arm] = new,new.payload(),mark
                    for key in ("update_differences","update_products","update_additions"):
                        work[key] += 96
                    work["updates"] += 1
                    work["update_divisions"] += int(mark["division_performed"])
                    divisions[arm] += int(mark["division_performed"])
                expected_update = dict(observation_digest=observation,states=updated,markers=markers)
                p.require(b.canonical(site["learning_update"]) == b.canonical(expected_update), "LEARNING_UPDATE_INVALID")
            else:
                p.require(site["learning_update"] is None, "TEST_UPDATE_FORBIDDEN")
            p.require(b.canonical(binding["primary"]) == b.canonical(binding["direct"])
                and b.canonical(site["primary"]) == b.canonical(site["direct"]), "BASELINE_DIFFERS")
            work["sites"] += 1
        if s == 0:
            states = {arm:direct_transition(state,"FROZEN") for arm,state in states.items()}
            p.require(b.canonical(record["learning"]["frozen"]) == b.canonical({arm:state.payload() for arm,state in states.items()}), "FREEZE_BINDING_INVALID")
    closed = {arm:direct_transition(state,"CLOSED").payload() for arm,state in states.items()}
    p.require(b.canonical(record["learning"]["closed"]) == b.canonical(closed), "CLOSE_BINDING_INVALID")
    p.complete_counts(work,p.verification_limits())
    p.complete_counts(counts,p.work_limits())
    p.require(all(counts[arm+"_update_divisions"] == n for arm,n in divisions.items()), "COMPLETE_COUNTERS_INVALID")
    return b.sealed(dict(status="S2NW_LEARNING_VERIFIED",record_digest=record["record_digest"],execution_digest=plan["execution_digest"],
        work=work,baseline_equal=True,evaluation_allowed=True,read_only=True,payload_regenerations=0,receptor_calls=0,nj_calls=0,
        raw_reconstructed_from_half=False,chronology_independently_proven=False),"verification_digest")
