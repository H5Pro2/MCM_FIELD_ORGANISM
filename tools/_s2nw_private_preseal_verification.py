"""Independent NW metadata verification; no synthesis, receptor or learned values."""
import json
from tools import _s2nw_private_source_binding as b


def check(obj, key):
    b.require(type(obj) is dict and obj.get(key) == b.digest({k:v for k,v in obj.items() if k != key}),
              "SEALED_DIGEST_INVALID")


def verify_bundle(execution, evaluation, seal, hashes):
    for obj,key in ((execution,"execution_digest"),(evaluation,"evaluation_digest"),(seal,"seal_digest")):
        check(obj,key)
        b.require(len(b.canonical(obj)) <= 65536,"METADATA_SIZE_INVALID")
    b.require(set(execution) == {"schema","contract_sha256","sources","source_order","profiles","environment",
        "source_hashes","generator","forecast_sites","prediction_contract","learning_schedule","budgets",
        "receptor_execution_authorized","nj_execution_authorized","prediction_execution_authorized",
        "learning_execution_authorized","error_execution_authorized","system_execution_authorized","execution_digest"},
        "EXECUTION_FORM_INVALID")
    b.require(execution["schema"] == "s2nw.source-execution-plan.v1" and evaluation["schema"] == "s2nw.evaluation-plan.v1"
        and seal["schema"] == "s2nw.source-seal.v1","SCHEMA_INVALID")
    b.require(execution["contract_sha256"] == evaluation["contract_sha256"] == b.PINS[b.CONTRACT]
        and execution["source_hashes"] == seal["hashes_before"] == seal["hashes_after"] == hashes,"CODE_BINDING_INVALID")
    b.require(execution["execution_digest"] == evaluation["execution_digest"] == seal["execution_digest"]
        and evaluation["evaluation_digest"] == seal["evaluation_digest"],"ROOT_BINDING_INVALID")
    layout = (("l01",(16,32,40,44,46,47)),("s01",(20,28,32,34,35)),
              ("s02",(20,28,32,28,26)),("s03",(20,28,32,32,32)),("s04",(20,28,32,32,32)))
    order = [f"nw-{sid}-w{k:02d}" for sid,gains in layout for k in range(len(gains))]
    b.require(execution["source_order"] == order and len(execution["sources"]) == 26,"SOURCE_ORDER_INVALID")
    n = 0
    for sid,gains in layout:
        for k,gain in enumerate(gains):
            row = execution["sources"][n]
            check(row,"source_digest")
            group = 0 if sid == "l01" else (2 if sid == "s04" and k >= 3 else 1)
            frequencies = ((530,1590,4770),(710,2130,6390),(890,2670,8010))[group]
            recipe = dict(schema="s2nw.pcm-window-recipe.v1",sample_rate=48000,sample_count=4800,
                group=dict(seed=f"s2nw-pcm-{group+1:03d}",partials=[dict(frequency_ratio=[f,1],amplitude_ratio=[a,20])
                    for f,a in zip(frequencies,(4,2,1),strict=True)]),gain_ratio=[gain,64],
                synthesis_time="float(j)/48000.0; j=0..4799",rounding="binary64-group-sum-then-gain-then-single-f32le")
            expected = dict(source_id=order[n],ordinal=n+1,stream_id=sid,window_ordinal=k,
                format="PCM_F32LE",channels=1,clock_id="audio.sample",window_start_sample=n*4800,
                window_end_sample=(n+1)*4800,nj_snapshot_index=n*10,pcm_byte_count=19200,
                recipe=recipe,recipe_digest=b.digest(recipe))
            b.require(b.canonical({key:value for key,value in row.items() if key not in ("source_digest","pcm_sha256")})
                == b.canonical(expected),"WINDOW_BINDING_INVALID")
            sha = row.get("pcm_sha256")
            b.require(type(sha) is str and len(sha) == 64 and all(c in "0123456789abcdef" for c in sha),"PAYLOAD_HASH_INVALID")
            n += 1
    sites = []
    for s,(sid,gains) in enumerate(layout):
        for k in range(1,len(gains)-1):
            sites.append(dict(site_id=f"t{k:02d}" if s == 0 else f"p{(s-1)*3+k:02d}",stream_id=sid,
                origin=k,target=k+1,phase="TRAIN" if s == 0 else "FROZEN",
                available_source_ids=[f"nw-{sid}-w{j:02d}" for j in range(k+1)],
                delta_source_ids=[f"nw-{sid}-w{k-1:02d}",f"nw-{sid}-w{k:02d}"],
                persist_source_id=f"nw-{sid}-w{k:02d}",target_source_id=f"nw-{sid}-w{k+1:02d}",update_after_target=s == 0))
    b.require(b.canonical(execution["forecast_sites"]) == b.canonical(sites),"FORECAST_SITE_INVALID")
    schedule = dict(training_stream="l01",update_sites=["t01","t02","t03","t04"],
        update_after_observed_targets=["nw-l01-w02","nw-l01-w03","nw-l01-w04","nw-l01-w05"],
        freeze_after_site="t04",freeze_before_source="nw-s01-w00",updates_required=4,
        test_streams=["s01","s02","s03","s04"],frozen_test_sites=12,reset_prefix_each_stream=True,
        reset_learning_between_test_streams=False,same_frozen_state_all_test_sites=True,test_updates_allowed=False,
        close_after_source="nw-s04-w04",initial_state=dict(n=0,Sxx=0.0,Sxy=0.0,alpha=0.0),
        phase_order=["TRAIN","FROZEN","CLOSED"],expected_learned_coefficient=None)
    b.require(b.canonical(execution["learning_schedule"]) == b.canonical(schedule),"LEARNING_SCHEDULE_INVALID")
    contract = dict(arms=[
        dict(arm="LEARNED_DELTA",functional_fields=["half_profile_digest","alpha","previous_values","last_values"],
             formula="d[i]=last[i]-previous[i];h[i]=last[i]+(alpha*d[i])"),
        dict(arm="LINEAR",functional_fields=["half_profile_digest","previous_values","last_values"],
             formula="d[i]=last[i]-previous[i];h[i]=last[i]+d[i]"),
        dict(arm="PERSIST",functional_fields=["half_profile_digest","last_values"],formula="h[i]=bitcopy(last[i])")],
        update_formula="for i=0..47: x=last[i]-previous[i];y=target[i]-last[i];Sxx=Sxx+(x*x);Sxy=Sxy+(x*y); then n=n+1;alpha=Sxy/Sxx if Sxx>0.0 else +0.0",
        update_functional_fields=["prior_learning_state","previous_values","last_values","observed_target_values"],
        error_formula="error[i]=abs(h[i]-target[i]);MAE=sum(error[i] for i=0..47)/48",
        gain_formula="gain_vs_baseline=MAE_baseline-MAE_LEARNED_DELTA",
        arithmetic="binary64; separate subtraction/multiplication/addition; no FMA; Python builtin sum in ascending original index order",
        indices=list(range(48)),finite_predictions_only=True,clipping=False,tolerance=False,
        coefficient_clipping=False,regularization=False,model_selection=False,
        forbidden_functional_fields=["source_id","stream_id","time","ordinal","target_ordinal","recipe",
            "seed","gain","category","evaluation","future_values","payload_sha256","source_digest"],
        metadata_bindings_outside_predictor=True,future_analysis_after_prediction_binding=True,
        future_pcm_regeneration_after_prediction_binding=True,update_after_target_observation=True,
        freeze_before_test_payload_generation=True,preseal_is_not_prediction_execution=True,
        independent_direct_learning_state=True,cross_stream_prefix_reuse=False,recursive_prediction=False,
        final_digest_alone_proves_chronology=False,standalone_materialization_authorized=False)
    b.require(b.canonical(execution["prediction_contract"]) == b.canonical(contract),"PREDICTOR_BOUNDARY_INVALID")
    criteria = []
    for p in (1,2,3):
        for arm in ("PERSIST","LINEAR"):
            criteria.append(dict(check_id=f"o{len(criteria)+1:02d}",site_id=f"p{p:02d}",left="MAE_LEARNED_DELTA",
                operator="LT",right="MAE_"+arm,role="PRIMARY"))
    for site in ("p05","p08","p11"):
        criteria.append(dict(check_id=f"o{len(criteria)+1:02d}",site_id=site,left="MAE_LEARNED_DELTA",
            operator="GT",right="MAE_PERSIST",role="SEPARATE_SWITCH_LOSS"))
    expected_eval = b.sealed(dict(schema="s2nw.evaluation-plan.v1",execution_digest=execution["execution_digest"],
        contract_sha256=b.PINS[b.CONTRACT],categories=dict(l01="TRAINING_DECAYING_INCREMENT",s01="CONTINUATION",
            s02="REVERSAL",s03="STANDSTILL_AFTER_RISE",s04="UNEXPECTED_GROUP_CHANGE"),criteria=criteria,
        positive_learning_requires=dict(observed_updates=4,noninitial_frozen_state=True,Sxx_strictly_positive=True),
        reporting=dict(per_test_stream_per_baseline_denominator=3,per_phase_denominator=1,
            per_site=["MAE_LEARNED_DELTA","MAE_LINEAR","MAE_PERSIST","two_signed_gains","two_WIN_TIE_LOSS"],
            target_phases={"2":"COMMON_RISE","3":"FIRST_BRANCH","4":"FOLLOWUP"},training_separate=True,
            losses_separate=True,pooled_gain_compensation=False,common_prefix_is_independent_replication=False),
        primary_requires_all_six=True,ties_pass=False,switch_losses_do_not_replace_primary=True,
        no_expected_coefficient=True,no_functional_start_gate=True,generation_categories_are_not_recognized=True,
        source_identity_proven=False,general_sequence_learning_proven=False,ME_MI_unblocked=False,
        preseal_learning_claim=False,no_source_selection=True,no_parameter_search=True),"evaluation_digest")
    b.require(b.canonical(evaluation) == b.canonical(expected_eval),"EVALUATION_BINDING_INVALID")
    b.require(execution["profiles"] == b.profile_binding() and execution["budgets"] == b.budgets(),"PROFILE_BUDGET_INVALID")
    b.require(all(execution[k] is False for k in ("receptor_execution_authorized","nj_execution_authorized",
        "prediction_execution_authorized","learning_execution_authorized","error_execution_authorized",
        "system_execution_authorized")),"AUTHORIZATION_INVALID")
    prefixes = [[f"nw-s{s:02d}-w{k:02d}" for s in (1,2,3,4)] for k in (0,1,2)]
    b.require(seal["prefix_groups"] == prefixes,"PREFIX_BINDING_INVALID")
    lookup = {row["source_id"]:row for row in execution["sources"]}
    for ids in prefixes:
        b.require(len({lookup[s]["pcm_sha256"] for s in ids}) == 1
            and len({lookup[s]["source_digest"] for s in ids}) == 4
            and len({lookup[s]["window_start_sample"] for s in ids}) == 4,"PREFIX_BINDING_INVALID")
    buckets = {}
    for row in execution["sources"]:
        buckets.setdefault(row["pcm_sha256"],[]).append(row["source_id"])
    collisions = [dict(pcm_sha256=h,source_ids=ids) for h,ids in sorted(buckets.items()) if len(ids)>1]
    b.require(seal["collisions"] == collisions,"COLLISION_BINDING_INVALID")
    b.require(seal["status"] == "S2NW_SOURCES_PRESEALED" and seal["attempted_sources"] == seal["completed_sources"] == 26
        and seal["generated_pcm_bytes"] == 499200 and seal["max_live_payloads"] == 1 and seal["main_gate_after"] is False
        and all(type(seal[k]) is int and seal[k] == 0 for k in ("raw_payloads_persisted","receptor_calls","nj_calls",
            "prediction_calls","learning_calls","error_calls","memory_calls","field_calls","context_calls","runtime_calls")),
        "COUNTERS_INVALID")
    return dict(windows=26,streams=5,training_update_sites_bound_not_executed=4,frozen_test_sites_bound_not_executed=12,
        criteria_bound_not_evaluated=9,freeze_boundary_bound=True,prefix_groups=prefixes,collisions=collisions,
        payload_regenerations=0,payload_bytes_independently_recomputed=False,
        chronological_predictor_execution_qualified=False,receptor_calls=0,nj_calls=0,prediction_calls=0,learning_calls=0,error_calls=0)


def verify_once(out):
    with (out/"verification.claim").open("xb"):
        pass
    try:
        names = ("execution-plan.json","evaluation-plan.json","seal.json")
        before = {n:b.filehash(out/n) for n in names}
        objects = []
        for name in names:
            data = (out/name).read_bytes()
            b.require(len(data) <= 65536,"METADATA_SIZE_INVALID")
            obj = json.loads(data)
            b.require(data == b.canonical(obj),"CANONICAL_FORM_INVALID")
            objects.append(obj)
        execution,evaluation,seal = objects
        work = verify_bundle(execution,evaluation,seal,b.watched())
        b.require(seal["run_id"] == out.name == b.RUN_ID,"RUN_ID_INVALID")
        b.require(seal["execution_file_sha256"] == before[names[0]]
            and seal["evaluation_file_sha256"] == before[names[1]],"FILE_BINDING_INVALID")
        b.qualification(execution["source_hashes"])
        b.require(b.filehash(b.QUAL_DIR/"result.json") == seal["qualification_file_sha256"],"QUALIFICATION_INVALID")
        b.require(execution["environment"] == b.environment() and execution["generator"] == b.generator_identity(),
                  "ENVIRONMENT_GENERATOR_INVALID")
        b.require(before == {n:b.filehash(out/n) for n in names} and b.MAIN_GATE is False,"READ_ONLY_INVALID")
        report = dict(run_id=out.name,status="S2NW_PRESEAL_VERIFIED",execution_digest=execution["execution_digest"],
            evaluation_digest=evaluation["evaluation_digest"],seal_digest=seal["seal_digest"],work=work,
            file_hashes_before=before,file_hashes_after=before,read_only=True,verification_calls=1,main_gate_after=False)
    except Exception as exc:
        report = dict(run_id=out.name,status="NOT_EVALUABLE",error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),verification_calls=1,retry=False)
    result = b.sealed(report,"verification_digest")
    b.publish(out/"verification.json",result,262144)
    return result
