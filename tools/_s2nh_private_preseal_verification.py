"""Independent read-only checks of S2-NH seals; never generate payloads."""

import json
import re
from tools import _s2nh_private_source_binding as b


def check(value, code):
    if not value:
        raise b.S2NHError(code)


def check_digest(value, key):
    check(type(value) is dict and value.get(key) == b.digest({k:v for k,v in value.items() if k != key}), "DIGEST_INVALID")


def check_plans(execution, evaluation):
    check_digest(execution, "execution_digest")
    check_digest(evaluation, "evaluation_digest")
    check(execution["schema"] == "s2nh.execution.v1" and evaluation["schema"] == "s2nh.evaluation.v1", "SCHEMA_INVALID")
    check(execution["masterseed"] == b.MASTER and execution["contract_sha256"] == b.filehash(b.ROOT / b.CONTRACT), "CONTRACT_INVALID")
    check(evaluation["execution_digest"] == execution["execution_digest"], "ROOT_LINK_INVALID")
    sources = execution["sources"]
    check(type(sources) is list and len(sources) == 32 and len({s["source_id"] for s in sources}) == 32, "SOURCE_COUNT_INVALID")
    for s, spec in zip(sources, b.source_specs(), strict=True):
        check_digest(s, "source_digest")
        check(set(s) == {"source_id","kind","recipe","recipe_digest","payload_sha256","byte_count","source_digest"}, "SOURCE_FORM_INVALID")
        check(all(s[k] == v for k,v in spec.payload().items()), "SOURCE_RECIPE_INVALID")
        check(type(s["byte_count"]) is int and s["byte_count"] == (19200 if spec.kind == "PCM" else 6220800)
              and type(s["payload_sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", s["payload_sha256"]), "PAYLOAD_BINDING_INVALID")
    check(sources[28]["source_id"] != sources[29]["source_id"] and sources[28]["payload_sha256"] == sources[29]["payload_sha256"], "EXACT_CUE_BINDING_INVALID")
    events = execution["events"]
    check(type(events) is list and len(events) == 28, "EVENT_COUNT_INVALID")
    literal = ("p00","p01","p00","p00","p02","p00","p01","p02","p00","p01","p02","p00","p01",
               "p03","p04","p05","p06","p07","p08","p09","p10","p11","p13","p13","p14","p14","p12","p12")
    audio_end = 0
    byid = {s["source_id"]:s for s in sources}
    for k, e in enumerate(events,1):
        kind = b.A if k in (3,23,25,27) else b.V if k in (4,24,26,28) else b.AV
        check(e["ordinal"] == k and e["event_id"] == f"e{k:02d}" and e["event_type"] == kind
              and e["recipe_id"] == literal[k-1] and e["source_occurrence_id"] == f"s2nh-source-e{k:02d}", "EVENT_ID_INVALID")
        check(e["common_end_tick"] == k*100000000 and e["field_clock_id"] == "s2nh-transfer-field-clock", "COMMON_TIME_INVALID")
        if kind == b.V:
            check(e["auditory"] is None, "AUDIO_PRESENCE_INVALID")
        else:
            a = e["auditory"]
            check(a == dict(source_id="nh-a"+literal[k-1][1:], clock_id="audio.sample", start_tick=audio_end,
                  end_tick=audio_end+4800, hop_start=audio_end//480, hop_end=audio_end//480+10,
                  endpoint_snapshot_index=audio_end//480, common_window=[k*100000000-10000000,k*100000000]), "AUDIO_TIME_INVALID")
            audio_end += 4800
        if kind == b.A:
            check(e["visual"] is None, "VISUAL_PRESENCE_INVALID")
        else:
            frame = 3*k-1
            v = e["visual"]
            check(v == dict(source_id=f"nh-vcue-e{k:02d}" if kind == b.V else "nh-v"+literal[k-1][1:],
                  clock_id="video.frame", start_tick=frame, end_tick=frame+1,
                  common_window=[frame*1000000000//30,k*100000000]), "VISUAL_TIME_INVALID")
        for part in (e["auditory"], e["visual"]):
            if part is not None:
                check(part["source_id"] in byid, "SOURCE_REFERENCE_INVALID")
    check(audio_end == 115200, "AUDIO_PROGRESS_INVALID")
    check(execution["profile"] == b.profile_binding() and execution["budgets"] == b.budgets(), "PROFILE_OR_BUDGET_INVALID")
    check(execution["rules"] == ["HISTORICAL_SUM_L1_24","ALL_BANDS_24"] and execution["observed_audio_bands"] == list(range(24))
          and execution["visible_visual_positions"] == list(range(32)) and execution["main_gate"] is False
          and execution["receptor_execution_authorized"] is False, "EXECUTION_BOUNDARY_INVALID")
    expected_cases = []
    for k in (3,4,23,24,25,26,27,28):
        expected_cases.append(dict(ordinal=k,target_recipe=None if k>=27 else "p01" if k>=25 else "p00",
            variant="UNKNOWN" if k>=27 else "GAIN" if k==23 else "FREQUENCY" if k==25 else "EXACT",
            expected_context=k<27,phase="EARLY_COMPETITION" if k<5 else "AFTER_PRESSURE"))
    check(evaluation["cases"] == expected_cases and evaluation["formation_roles"] == {"p00":"A","p01":"B","p02":"C"}
          and evaluation["pressure_recipes"] == [f"p{i:02d}" for i in range(3,12)]
          and evaluation["expected_support"] == {"p00":3,"p01":3,"p02":2}
          and evaluation["expected_recent_eviction"] == ["p00","p01","p02"], "EVALUATION_RELATION_INVALID")
    check(evaluation["retention_identity"] == "D=R+L" and evaluation["zero_denominator"] == "ERHALTUNG_NICHT_GEPRUEFT"
          and evaluation["offset_losses"] is False and evaluation["geometry_success_gate"] is False
          and evaluation["excluded_target_candidates_separate"] is True
          and evaluation["separate_axes"] == ["modality","phase","variant","observed_competition","pcm_bits","receptor_bits","observed_bits"], "EVALUATION_BOUNDARY_INVALID")
    check(set(execution) == {"schema","masterseed","sources","events","source_hashes","generator_identity","contract_sha256",
        "profile","rules","observed_audio_bands","visible_visual_positions","budgets","main_gate","receptor_execution_authorized","execution_digest"}, "EXECUTION_KEYS_INVALID")
    check(set(evaluation) == {"schema","execution_digest","cases","formation_roles","pressure_recipes","expected_support",
        "expected_recent_eviction","retention_identity","zero_denominator","offset_losses","separate_axes",
        "excluded_target_candidates_separate","geometry_success_gate","evaluation_digest"}, "EVALUATION_KEYS_INVALID")


def verify_once(out):
    b.publish(out / "verification-reservation.json", dict(verification_calls=1,payload_generations=0))
    before = {}
    try:
        names = ("execution-plan.json","evaluation-plan.json","seal.json","preregistration.json")
        check(all((out/n).stat().st_size <= b.MAX_BYTES for n in names), "FILE_LIMIT_INVALID")
        before = {n:b.filehash(out/n) for n in names}
        x,y,s,p = [json.loads((out/n).read_bytes()) for n in names]
        check_plans(x,y)
        check_digest(s,"seal_digest")
        check(s["run_id"] == p["run_id"] == out.name == b.RUN_ID and s["status"] == "S2NH_SOURCES_PRESEALED", "RUN_BINDING_INVALID")
        check(s["execution_file_sha256"] == before[names[0]] and s["evaluation_file_sha256"] == before[names[1]]
              and s["execution_digest"] == x["execution_digest"] and s["evaluation_digest"] == y["evaluation_digest"], "SEAL_BINDING_INVALID")
        check(x["source_hashes"] == s["hashes_before"] == s["hashes_after"] == p["hashes"] == b.watched(), "FILES_CHANGED")
        check(x["generator_identity"] == p["generator"] == b.identity(), "INTERPRETER_BINDING_INVALID")
        check(p["specifications"] == [v.payload() for v in b.source_specs()] and p["events"] == x["events"]
              and p["budgets"] == x["budgets"] and p["preseal_calls"] == 1 and p["retry"] is False
              and p["qualification_sha256"] == b.filehash(b.ROOT / "reports/s2nh" / b.QUAL_ID / "result.json"), "PREREGISTRATION_INVALID")
        check(s["counters"] == dict(pcm=15,rgb=13,visual_cues=4,events=28,receptor=0,memory=0,field=0,context=0,runtime=0,
              distances=0,rule_comparisons=0,raw_payloads_saved=0) and s["attempted_sources"] == s["completed_sources"] == 32
              and s["main_gate"] is False and b.MAIN_GATE is False, "COUNTERS_INVALID")
        groups = {}
        for source in x["sources"]:
            key = (source["kind"] == "PCM",source["payload_sha256"])
            groups.setdefault(key,[]).append(source["source_id"])
        check(s["collisions"] == [v for v in groups.values() if len(v)>1], "COLLISION_BINDING_INVALID")
        after = {n:b.filehash(out/n) for n in names}
        check(before == after,"ARTIFACTS_CHANGED")
        result = dict(run_id=out.name,status="S2NH_PRESEAL_BINDINGS_VERIFIED",execution_digest=x["execution_digest"],
            evaluation_digest=y["evaluation_digest"],seal_digest=s["seal_digest"], hashes_before=before,hashes_after=after,
            verification_calls=1,payload_generations=0,receptor_calls=0)
    except Exception as error:
        result = dict(run_id=out.name,status="NOT_EVALUABLE",phase="BINDING_VERIFICATION",error_class=type(error).__name__,
                      code=str(error) if isinstance(error,b.S2NHError) else "BINDING_ERROR",hashes_before=before,
                      verification_calls=1,payload_generations=0)
    b.publish(out / "verification.json", b.sealed(result,"verification_digest"))
    return result
