"""Independent NV metadata check; never regenerate payloads or predict values."""
import json
from tools import _s2nv_private_source_binding as b


def check(obj, key):
    b.require(type(obj) is dict and obj.get(key)==b.digest({k:v for k,v in obj.items() if k!=key}),"SEALED_DIGEST_INVALID")


def verify_bundle(execution, evaluation, seal, hashes):
    for obj,key in ((execution,"execution_digest"),(evaluation,"evaluation_digest"),(seal,"seal_digest")):
        check(obj,key)
        b.require(len(b.canonical(obj))<=65536,"METADATA_SIZE_INVALID")
    b.require(set(execution)=={"schema","contract_sha256","sources","source_order","profiles","environment",
        "source_hashes","generator","forecast_sites","prediction_contract","budgets","receptor_execution_authorized",
        "nj_execution_authorized","prediction_execution_authorized","error_execution_authorized",
        "system_execution_authorized","execution_digest"},"EXECUTION_FORM_INVALID")
    b.require(execution["schema"]=="s2nv.source-execution-plan.v1" and evaluation["schema"]=="s2nv.evaluation-plan.v1"
        and seal["schema"]=="s2nv.source-seal.v1","SCHEMA_INVALID")
    b.require(execution["contract_sha256"]==evaluation["contract_sha256"]==b.PINS[b.CONTRACT]
        and execution["source_hashes"]==seal["hashes_before"]==seal["hashes_after"]==hashes,"CODE_BINDING_INVALID")
    b.require(execution["execution_digest"]==evaluation["execution_digest"]==seal["execution_digest"]
        and evaluation["evaluation_digest"]==seal["evaluation_digest"],"ROOT_BINDING_INVALID")
    order = [f"nv-s{s:02d}-w{k:02d}" for s in range(1,5) for k in range(5)]
    b.require(execution["source_order"]==order and len(execution["sources"])==20,"SOURCE_ORDER_INVALID")
    gains = ((4,5,6,7,8),(4,5,6,5,4),(4,5,6,6,6),(4,5,6,6,6))
    for n,row in enumerate(execution["sources"]):
        check(row,"source_digest")
        s,k = n//5+1,n%5
        group = 1 if s==4 and k>=3 else 0
        frequencies = (830,2490,7470) if group else (470,1410,4230)
        recipe = dict(schema="s2nv.pcm-window-recipe.v1",sample_rate=48000,sample_count=4800,
            group=dict(seed=f"s2nv-pcm-{group+1:03d}",partials=[dict(frequency_ratio=[f,1],amplitude_ratio=[a,20])
                for f,a in zip(frequencies,(4,2,1),strict=True)]),gain_ratio=[gains[s-1][k],10],
            synthesis_time="float(j)/48000.0; j=0..4799",rounding="binary64-group-sum-then-gain-then-single-f32le")
        expected = dict(source_id=order[n],ordinal=n+1,stream_id=f"s{s:02d}",window_ordinal=k,
            format="PCM_F32LE",channels=1,clock_id="audio.sample",window_start_sample=n*4800,
            window_end_sample=(n+1)*4800,nj_snapshot_index=n*10,pcm_byte_count=19200,
            recipe=recipe,recipe_digest=b.digest(recipe))
        b.require(b.canonical({k:v for k,v in row.items() if k not in ("source_digest","pcm_sha256")})==b.canonical(expected),
            "WINDOW_BINDING_INVALID")
        b.require(type(row["pcm_sha256"]) is str and len(row["pcm_sha256"])==64
            and all(c in "0123456789abcdef" for c in row["pcm_sha256"]),"PAYLOAD_HASH_INVALID")
    sites = []
    for s in range(1,5):
        for k in (1,2,3):
            sites.append(dict(site_id=f"p{len(sites)+1:02d}",stream_id=f"s{s:02d}",origin=k,target=k+1,
                available_source_ids=order[(s-1)*5:(s-1)*5+k+1],
                linear_source_ids=[f"nv-s{s:02d}-w{k-1:02d}",f"nv-s{s:02d}-w{k:02d}"],
                persist_source_id=f"nv-s{s:02d}-w{k:02d}",target_source_id=f"nv-s{s:02d}-w{k+1:02d}"))
    b.require(b.canonical(execution["forecast_sites"])==b.canonical(sites),"FORECAST_SITE_INVALID")
    contract = dict(arms=[
        dict(arm="LINEAR_TWO_STATE",functional_fields=["half_profile_digest","previous_values","last_values"],
             formula="d[i]=last[i]-previous[i];prediction[i]=last[i]+d[i]"),
        dict(arm="PERSIST_LAST",functional_fields=["half_profile_digest","last_values"],formula="prediction[i]=bitcopy(last[i])")],
        error_formula="error[i]=abs(prediction[i]-target[i]);MAE=sum(error[i] for i=0..47)/48",
        gain_formula="gain=MAE_PERSIST_LAST-MAE_LINEAR_TWO_STATE",
        arithmetic="binary64; subtraction before addition; Python builtin sum in ascending original index order",
        indices=list(range(48)),finite_prediction_domain=[-1,2],clipping=False,tolerance=False,
        forbidden_functional_fields=["source_id","stream_id","time","ordinal","target_ordinal","recipe","seed",
            "gain","category","evaluation","future_values","payload_sha256","source_digest"],
        metadata_bindings_outside_predictor=True,future_analysis_after_prediction_binding=True,
        future_pcm_regeneration_after_prediction_binding=True,cross_stream_reuse=False,recursive_prediction=False,
        final_digest_alone_proves_chronology=False,standalone_materialization_authorized=False)
    b.require(b.canonical(execution["prediction_contract"])==b.canonical(contract),"PREDICTOR_BOUNDARY_INVALID")
    criteria = []
    for n,(site,operator,role) in enumerate((("p01","LT","PRIMARY"),("p02","LT","PRIMARY"),("p03","LT","PRIMARY"),
            ("p05","GT","SEPARATE_STRESS"),("p08","GT","SEPARATE_STRESS"),("p11","GT","SEPARATE_STRESS")),1):
        criteria.append(dict(check_id=f"o{n:02d}",site_id=site,left="MAE_LINEAR_TWO_STATE",operator=operator,
            right="MAE_PERSIST_LAST",role=role))
    expected_evaluation = b.sealed(dict(schema="s2nv.evaluation-plan.v1",execution_digest=execution["execution_digest"],
        contract_sha256=b.PINS[b.CONTRACT],categories=dict(s01="CONTINUATION",s02="REVERSAL",s03="STANDSTILL_AFTER_RISE",
            s04="UNEXPECTED_GROUP_CHANGE"),criteria=criteria,
        reporting=dict(per_stream_denominator=3,per_site=["MAE_LINEAR_TWO_STATE","MAE_PERSIST_LAST","signed_gain","WIN_TIE_LOSS"],
            target_phases={"2":"COMMON_RISE","3":"FIRST_BRANCH","4":"FOLLOWUP"},losses_separate=True,
            pooled_gain_compensation=False,common_prefix_is_independent_replication=False),
        primary_requires_all_three=True,ties_pass=False,stress_does_not_replace_primary=True,
        generation_categories_are_not_recognized=True,learning_proven=False,source_identity_proven=False,
        no_source_selection=True,no_parameter_search=True),"evaluation_digest")
    b.require(b.canonical(evaluation)==b.canonical(expected_evaluation),"EVALUATION_BINDING_INVALID")
    b.require(execution["profiles"]==b.profile_binding() and execution["budgets"]==b.budgets(),"PROFILE_BUDGET_INVALID")
    b.require(all(execution[k] is False for k in ("receptor_execution_authorized","nj_execution_authorized",
        "prediction_execution_authorized","error_execution_authorized","system_execution_authorized")),"AUTHORIZATION_INVALID")
    prefixes = [[f"nv-s{s:02d}-w{k:02d}" for s in (1,2,3,4)] for k in (0,1,2)]
    b.require(seal["prefix_groups"]==prefixes,"PREFIX_BINDING_INVALID")
    lookup = {row["source_id"]:row for row in execution["sources"]}
    for ids in prefixes:
        b.require(len({lookup[s]["pcm_sha256"] for s in ids})==1
            and len({lookup[s]["source_digest"] for s in ids})==4
            and len({lookup[s]["window_start_sample"] for s in ids})==4,"PREFIX_BINDING_INVALID")
    buckets = {}
    for row in execution["sources"]:
        buckets.setdefault(row["pcm_sha256"],[]).append(row["source_id"])
    collisions = [dict(pcm_sha256=h,source_ids=ids) for h,ids in sorted(buckets.items()) if len(ids)>1]
    b.require(seal["collisions"]==collisions,"COLLISION_BINDING_INVALID")
    b.require(seal["status"]=="S2NV_SOURCES_PRESEALED" and seal["attempted_sources"]==seal["completed_sources"]==20
        and seal["generated_pcm_bytes"]==384000 and seal["max_live_payloads"]==1 and seal["main_gate_after"] is False
        and all(type(seal[k]) is int and seal[k]==0 for k in ("raw_payloads_persisted","receptor_calls","nj_calls",
            "prediction_calls","error_calls","memory_calls","field_calls","context_calls","runtime_calls")),"COUNTERS_INVALID")
    return dict(windows=20,streams=4,forecast_sites_bound_not_executed=12,criteria_bound_not_evaluated=6,
        prefix_groups=prefixes,collisions=collisions,payload_regenerations=0,payload_bytes_independently_recomputed=False,
        chronological_predictor_execution_qualified=False,receptor_calls=0,nj_calls=0,prediction_calls=0,error_calls=0)


def verify_once(out):
    with (out/"verification.claim").open("xb"):
        pass
    try:
        names = ("execution-plan.json","evaluation-plan.json","seal.json")
        before = {n:b.filehash(out/n) for n in names}
        objects = []
        for name in names:
            data = (out/name).read_bytes()
            b.require(len(data)<=65536,"METADATA_SIZE_INVALID")
            obj = json.loads(data)
            b.require(data==b.canonical(obj),"CANONICAL_FORM_INVALID")
            objects.append(obj)
        execution,evaluation,seal = objects
        work = verify_bundle(execution,evaluation,seal,b.watched())
        b.require(seal["run_id"]==out.name==b.RUN_ID,"RUN_ID_INVALID")
        b.require(seal["execution_file_sha256"]==before[names[0]] and seal["evaluation_file_sha256"]==before[names[1]],"FILE_BINDING_INVALID")
        b.qualification(execution["source_hashes"])
        b.require(b.filehash(b.QUAL_DIR/"result.json")==seal["qualification_file_sha256"],"QUALIFICATION_INVALID")
        b.require(execution["environment"]==b.environment() and execution["generator"]==b.generator_identity(),"ENVIRONMENT_GENERATOR_INVALID")
        b.require(before=={n:b.filehash(out/n) for n in names} and b.MAIN_GATE is False,"READ_ONLY_INVALID")
        report = dict(run_id=out.name,status="S2NV_PRESEAL_VERIFIED",execution_digest=execution["execution_digest"],
            evaluation_digest=evaluation["evaluation_digest"],seal_digest=seal["seal_digest"],work=work,
            file_hashes_before=before,file_hashes_after=before,read_only=True,verification_calls=1,main_gate_after=False)
    except Exception as exc:
        report = dict(run_id=out.name,status="NOT_EVALUABLE",error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),verification_calls=1,retry=False)
    result = b.sealed(report,"verification_digest")
    b.publish(out/"verification.json",result,262144)
    return result
