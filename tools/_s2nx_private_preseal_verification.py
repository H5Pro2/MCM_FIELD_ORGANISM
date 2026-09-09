"""Independent NX metadata checks; no PCM or predictor execution."""
import json
from tools import _s2nx_private_source_binding as b

sealed,PINS,CONTRACT = b.sealed,b.PINS,b.CONTRACT


def check(obj, key):
    b.require(type(obj) is dict and obj.get(key) == b.digest({k:v for k,v in obj.items() if k != key}),
              "SEALED_DIGEST_INVALID")


def _schedule():
    return dict(histories=[
        dict(history_id=f"H{s}",training_stream=f"l{s:02d}",
             update_sites=[f"t{(s-1)*4+k:02d}" for k in (1,2,3,4)],
             update_after_observed_targets=[f"nx-l{s:02d}-w{k:02d}" for k in (2,3,4,5)],
             freeze_after_site=f"t{s*4:02d}",updates_required=4,
             initial_state=dict(n=0,Sxx=0.0,Sxy=0.0,alpha=0.0),expected_learned_coefficient=None)
        for s in (1,2)],training_order=["H1","H2"],independent_initial_states=True,
        no_cross_history_updates=True,both_frozen_before_source="nx-s01-w00",
        test_streams=["s01","s02","s03","s04"],frozen_test_sites=12,
        same_test_inputs_for_all_arms=True,reset_prefix_each_stream=True,
        reset_learning_between_test_streams=False,same_frozen_states_all_test_sites=True,
        test_updates_allowed=False,close_after_source="nx-s04-w04",
        phase_order=["TRAIN","FROZEN","CLOSED"],learned_values_are_not_start_gates=True)


def _contract():
    return dict(arms=[
        *[dict(arm=name,functional_fields=["half_profile_digest","alpha","previous_values","last_values"],
            formula="d[i]=last[i]-previous[i];h[i]=last[i]+(alpha*d[i])") for name in ("H1","H2")],
        dict(arm="FIXED_HALF",functional_fields=["half_profile_digest","previous_values","last_values"],
            formula="d[i]=last[i]-previous[i];h[i]=last[i]+(0.5*d[i])"),
        dict(arm="LINEAR",functional_fields=["half_profile_digest","previous_values","last_values"],
            formula="d[i]=last[i]-previous[i];h[i]=last[i]+d[i]"),
        dict(arm="PERSIST",functional_fields=["half_profile_digest","last_values"],formula="h[i]=bitcopy(last[i])")],
        fixed_control=dict(value=0.5,binary64_hex="0x1.0000000000000p-1",source_estimated=False,mutable=False),
        update_formula="for i=0..47: x=last[i]-previous[i];y=target[i]-last[i];Sxx=Sxx+(x*x);Sxy=Sxy+(x*y); then n=n+1;alpha=Sxy/Sxx if Sxx>0.0 else +0.0",
        update_functional_fields=["prior_learning_state","previous_values","last_values","observed_target_values"],
        error_formula="error[i]=abs(h[i]-target[i]);MAE=sum(error[i] for i=0..47)/48",
        gain_formula="gain_vs_baseline=MAE_baseline-MAE_Hj",cross_gain_formula="MAE_H2-MAE_H1",
        arithmetic="binary64; separate subtraction/multiplication/addition; no FMA; Python builtin sum in ascending original index order",
        indices=list(range(48)),finite_predictions_only=True,clipping=False,tolerance=False,
        coefficient_clipping=False,regularization=False,model_selection=False,
        forbidden_functional_fields=["source_id","stream_id","history_id","time","ordinal","target_ordinal","recipe",
            "seed","gain","category","evaluation","future_values","payload_sha256","source_digest"],
        metadata_bindings_outside_predictor=True,future_analysis_after_prediction_binding=True,
        future_pcm_regeneration_after_prediction_binding=True,update_after_target_observation=True,
        freeze_before_test_payload_generation=True,preseal_is_not_prediction_execution=True,
        independent_direct_learning_states=True,cross_stream_prefix_reuse=False,recursive_prediction=False,
        final_digest_alone_proves_chronology=False,standalone_materialization_authorized=False)


def _budgets():
    return dict(windows=32,generated_samples=153600,generated_pcm_bytes=614400,max_live_payloads=1,max_live_pcm_bytes=19200,
        future_analyses=32,future_nj=32,future_values_per_scale=1536,training_sites=8,test_sites=12,forecast_sites=20,
        predictions_per_implementation=92,both_predictions=184,
        prediction_subtractions_per_implementation=3456,prediction_multiplications_per_implementation=2496,
        prediction_additions_per_implementation=3456,persist_copies_per_implementation=960,
        update_differences_per_implementation=768,update_products_per_implementation=768,update_additions_per_implementation=768,
        updates_per_implementation=8,max_update_divisions_per_implementation=8,
        error_terms_per_implementation=4416,mae_sums_per_implementation=92,gains_per_implementation=108,
        both_error_terms=8832,both_mae_sums=184,both_gains=216,
        offline_halvings=1536,offline_prediction_subtractions=6912,offline_prediction_multiplications=4992,
        offline_prediction_additions=6912,offline_persist_copies=1920,
        offline_update_differences=1536,offline_update_products=1536,offline_update_additions=1536,
        offline_updates=16,offline_max_update_divisions=16,offline_error_terms=8832,offline_sums=184,offline_gains=216,
        outcome_classifications=108,training_outcome_classifications=24,strict_criteria=28,
        max_learning_state_bytes=4096,max_learning_states=4,max_prefix_vectors=3,max_metadata_bytes=65536,
        max_output_bytes=2097152,max_verification_bytes=262144,max_evaluation_bytes=262144)


def _evaluation(execution):
    criteria = []
    for prefix,role in (("K","CROSS_HISTORY"),("F","FIXED_CONTROL")):
        for s,history,other in ((1,"H1","H2"),(2,"H2","H1")):
            for k in (1,2,3):
                criteria.append(dict(check_id=f"{prefix}{(s-1)*3+k:02d}",site_id=f"p{(s-1)*3+k:02d}",
                    left="MAE_"+history,operator="LT",right="MAE_"+(other if prefix=="K" else "FIXED_HALF"),role=role))
    for s,history in ((1,"H1"),(2,"H2")):
        for k in (1,2,3):
            for j,arm in enumerate(("PERSIST","LINEAR"),1):
                criteria.append(dict(check_id=f"B{(s-1)*6+(k-1)*2+j:02d}",site_id=f"p{(s-1)*3+k:02d}",
                    left="MAE_"+history,operator="LT",right="MAE_"+arm,role="SEPARATE_BASELINE"))
    for n,site in enumerate(("p08","p11")):
        for j,history in enumerate(("H1","H2"),1):
            criteria.append(dict(check_id=f"W{n*2+j:02d}",site_id=site,left="MAE_"+history,
                operator="GT",right="MAE_PERSIST",role="SEPARATE_SWITCH_LOSS"))
    return sealed(dict(schema="s2nx.evaluation-plan.v1",execution_digest=execution["execution_digest"],
        contract_sha256=PINS[CONTRACT],categories=dict(l01="TRAINING_QUARTER_INCREMENT",l02="TRAINING_THREE_QUARTER_INCREMENT",
            s01="CONTINUATION_QUARTER",s02="CONTINUATION_THREE_QUARTER",s03="REVERSAL",s04="UNEXPECTED_GROUP_CHANGE"),
        expected_history=dict(s01="H1",s02="H2"),criteria=criteria,
        full_success_requires=dict(all_K=True,all_F=True,observed_updates_each=4,noninitial_frozen_states=True,
            Sxx_each_strictly_positive=True,actual_alphas_different=True),
        reporting=dict(per_test_stream_history_baseline_denominator=3,per_phase_denominator=1,per_training_stream_denominator=4,
            target_phases={"2":"INITIAL_TARGET","3":"FIRST_BRANCH","4":"FOLLOWUP"},
            training_separate=True,losses_separate=True,pooled_gain_compensation=False,
            common_prefix_is_independent_replication=False,cross_and_fixed_results_separate=True,
            cross_gain_orientation="MAE_H2-MAE_H1"),
        ties_pass=False,baseline_or_switch_results_do_not_replace_K_F=True,
        no_expected_learned_coefficients=True,no_functional_start_gate=True,generation_categories_are_not_recognized=True,
        source_identity_proven=False,automatic_history_selection_proven=False,ME_MI_unblocked=False,
        preseal_learning_claim=False,no_source_selection=True,no_parameter_search=True),"evaluation_digest")


def verify_bundle(execution, evaluation, seal, hashes):
    for obj,key in ((execution,"execution_digest"),(evaluation,"evaluation_digest"),(seal,"seal_digest")):
        check(obj,key)
        b.require(len(b.canonical(obj)) <= 65536,"METADATA_SIZE_INVALID")
    b.require(set(execution) == {"schema","contract_sha256","sources","source_order","profiles","environment",
        "source_hashes","generator","forecast_sites","prediction_contract","learning_schedule","budgets",
        "receptor_execution_authorized","nj_execution_authorized","prediction_execution_authorized",
        "learning_execution_authorized","error_execution_authorized","system_execution_authorized","execution_digest"},
        "EXECUTION_FORM_INVALID")
    b.require(execution["schema"] == "s2nx.source-execution-plan.v1" and evaluation["schema"] == "s2nx.evaluation-plan.v1"
        and seal["schema"] == "s2nx.source-seal.v1","SCHEMA_INVALID")
    b.require(execution["contract_sha256"] == evaluation["contract_sha256"] == b.PINS[b.CONTRACT]
        and execution["source_hashes"] == seal["hashes_before"] == seal["hashes_after"] == hashes,"CODE_BINDING_INVALID")
    b.require(execution["execution_digest"] == evaluation["execution_digest"] == seal["execution_digest"]
        and evaluation["evaluation_digest"] == seal["evaluation_digest"],"ROOT_BINDING_INVALID")
    layout = (("l01",(128,384,448,464,468,469)),("l02",(128,384,576,720,828,909)),
        ("s01",(192,320,352,360,362)),("s02",(192,320,416,488,542)),
        ("s03",(192,320,352,320,312)),("s04",(192,320,416,416,416)))
    order = [f"nx-{sid}-w{k:02d}" for sid,gains in layout for k in range(len(gains))]
    b.require(execution["source_order"] == order and len(execution["sources"]) == 32,"SOURCE_ORDER_INVALID")
    n = 0
    for sid,gains in layout:
        for k,gain in enumerate(gains):
            row = execution["sources"][n]
            check(row,"source_digest")
            group = 0 if sid.startswith("l") else (2 if sid == "s04" and k >= 3 else 1)
            frequencies = ((610,1830,5490),(790,2370,7110),(970,2910,8730))[group]
            recipe = dict(schema="s2nx.pcm-window-recipe.v1",sample_rate=48000,sample_count=4800,
                group=dict(seed=f"s2nx-pcm-{group+1:03d}",partials=[dict(frequency_ratio=[f,1],amplitude_ratio=[a,20])
                    for f,a in zip(frequencies,(4,2,1),strict=True)]),gain_ratio=[gain,1024],
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
            training = s < 2
            sites.append(dict(site_id=f"t{s*4+k:02d}" if training else f"p{(s-2)*3+k:02d}",stream_id=sid,
                origin=k,target=k+1,phase="TRAIN" if training else "FROZEN",
                available_source_ids=[f"nx-{sid}-w{j:02d}" for j in range(k+1)],
                delta_source_ids=[f"nx-{sid}-w{k-1:02d}",f"nx-{sid}-w{k:02d}"],
                persist_source_id=f"nx-{sid}-w{k:02d}",target_source_id=f"nx-{sid}-w{k+1:02d}",
                active_histories=[f"H{s+1}"] if training else ["H1","H2"],update_after_target=training))
    b.require(b.canonical(execution["forecast_sites"]) == b.canonical(sites),"FORECAST_SITE_INVALID")
    b.require(b.canonical(execution["learning_schedule"]) == b.canonical(_schedule()),"LEARNING_SCHEDULE_INVALID")
    b.require(b.canonical(execution["prediction_contract"]) == b.canonical(_contract()),"PREDICTOR_BOUNDARY_INVALID")
    b.require(b.canonical(evaluation) == b.canonical(_evaluation(execution)),"EVALUATION_BINDING_INVALID")
    b.require(execution["profiles"] == b.profile_binding() and execution["budgets"] == _budgets(),"PROFILE_BUDGET_INVALID")
    b.require(all(execution[k] is False for k in ("receptor_execution_authorized","nj_execution_authorized",
        "prediction_execution_authorized","learning_execution_authorized","error_execution_authorized",
        "system_execution_authorized")),"AUTHORIZATION_INVALID")
    prefixes = [["nx-l01-w00","nx-l02-w00"],["nx-l01-w01","nx-l02-w01"],
        ["nx-s01-w00","nx-s02-w00","nx-s03-w00","nx-s04-w00"],
        ["nx-s01-w01","nx-s02-w01","nx-s03-w01","nx-s04-w01"],
        ["nx-s01-w02","nx-s03-w02"],["nx-s02-w02","nx-s04-w02"]]
    b.require(seal["prefix_groups"] == prefixes,"PREFIX_BINDING_INVALID")
    lookup = {row["source_id"]:row for row in execution["sources"]}
    for ids in prefixes:
        b.require(len({lookup[s]["pcm_sha256"] for s in ids}) == 1
            and len({lookup[s]["source_digest"] for s in ids}) == len(ids)
            and len({lookup[s]["window_start_sample"] for s in ids}) == len(ids),"PREFIX_BINDING_INVALID")
    buckets = {}
    for row in execution["sources"]:
        buckets.setdefault(row["pcm_sha256"],[]).append(row["source_id"])
    collisions = [dict(pcm_sha256=h,source_ids=ids) for h,ids in sorted(buckets.items()) if len(ids)>1]
    b.require(seal["collisions"] == collisions,"COLLISION_BINDING_INVALID")
    b.require(seal["status"] == "S2NX_SOURCES_PRESEALED" and seal["attempted_sources"] == seal["completed_sources"] == 32
        and seal["generated_pcm_bytes"] == 614400 and seal["max_live_payloads"] == 1 and seal["main_gate_after"] is False
        and all(type(seal[k]) is int and seal[k] == 0 for k in ("raw_payloads_persisted","receptor_calls","nj_calls",
            "prediction_calls","learning_calls","error_calls","memory_calls","field_calls","context_calls","runtime_calls")),
        "COUNTERS_INVALID")
    return dict(windows=32,streams=6,training_histories=2,training_update_sites_bound_not_executed=8,
        frozen_test_sites_bound_not_executed=12,criteria_bound_not_evaluated=28,fixed_control_bound=0.5,
        freeze_boundaries_bound=True,prefix_groups=prefixes,collisions=collisions,
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
        report = dict(run_id=out.name,status="S2NX_PRESEAL_VERIFIED",execution_digest=execution["execution_digest"],
            evaluation_digest=evaluation["evaluation_digest"],seal_digest=seal["seal_digest"],work=work,
            file_hashes_before=before,file_hashes_after=before,read_only=True,verification_calls=1,main_gate_after=False)
    except Exception as exc:
        report = dict(run_id=out.name,status="NOT_EVALUABLE",error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),verification_calls=1,retry=False)
    result = b.sealed(report,"verification_digest")
    b.publish(out/"verification.json",result,262144)
    return result

