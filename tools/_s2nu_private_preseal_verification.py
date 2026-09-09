"""NU metadata-only verification; no PCM generator, sensor or metric calls."""
import json
from tools import _s2nu_private_source_binding as b


def check(value,key):
    b.require(type(value) is dict and value.get(key)==b.digest({k:v for k,v in value.items() if k!=key}),"SEALED_DIGEST_INVALID")


def verify_bundle(execution,evaluation,seal,hashes):
    for obj,key in ((execution,"execution_digest"),(evaluation,"evaluation_digest"),(seal,"seal_digest")):
        check(obj,key)
        b.require(len(b.canonical(obj))<=65536,"METADATA_SIZE_INVALID")
    b.require(set(execution)=={"schema","contract_sha256","sources","source_order","profiles","environment","source_hashes",
        "generator","controls","budgets","indices","arithmetic","cross_stream_deltas","receptor_execution_authorized",
        "nj_execution_authorized","comparison_execution_authorized","system_execution_authorized","execution_digest"},"EXECUTION_FORM_INVALID")
    b.require(execution["schema"]=="s2nu.source-execution-plan.v1" and evaluation["schema"]=="s2nu.evaluation-plan.v1"
        and seal["schema"]=="s2nu.source-seal.v1","SCHEMA_INVALID")
    b.require(execution["contract_sha256"]==evaluation["contract_sha256"]==b.PINS[b.CONTRACT]
        and execution["source_hashes"]==seal["hashes_before"]==seal["hashes_after"]==hashes,"CODE_BINDING_INVALID")
    b.require(execution["execution_digest"]==evaluation["execution_digest"]==seal["execution_digest"]
        and evaluation["evaluation_digest"]==seal["evaluation_digest"],"ROOT_BINDING_INVALID")
    expected_order = [f"nu-s{s:02d}-w{k:02d}" for s in range(1,7) for k in range(5)]
    b.require(execution["source_order"]==expected_order and len(execution["sources"])==30,"SOURCE_ORDER_INVALID")
    frequencies = ((430,1290,3870),(710,2130,6390),(5870,))
    amplitudes = (((4,20),(2,20),(1,20)),((4,20),(2,20),(1,20)),((1,20),))
    groups = [dict(seed=f"s2nu-pcm-{g+1:03d}",partials=[dict(frequency_ratio=[f,1],amplitude_ratio=list(a))
        for f,a in zip(frequencies[g],amplitudes[g],strict=True)]) for g in range(3)]
    for index,row in enumerate(execution["sources"]):
        check(row,"source_digest")
        s,k = index//5+1,index%5
        recipe = dict(schema="s2nu.pcm-window-recipe.v1",sample_rate=48000,sample_count=4800,
            expression_id=(1,2,2,4,5,6)[s-1],synthesis_window_index=(0,3,1,2,4)[k] if s==3 else k,
            groups=groups,rounding="binary64-expression-then-single-f32le")
        expected = dict(source_id=expected_order[index],ordinal=index+1,stream_id=f"s{s:02d}",window_ordinal=k,
            format="PCM_F32LE",channels=1,clock_id="audio.sample",window_start_sample=index*4800,
            window_end_sample=(index+1)*4800,nj_snapshot_index=index*10,pcm_byte_count=19200,
            recipe=recipe,recipe_digest=b.digest(recipe))
        b.require(b.canonical({k:v for k,v in row.items() if k not in ("source_digest","pcm_sha256")})==b.canonical(expected),"WINDOW_BINDING_INVALID")
        b.require(all(type(row[k]) is int for k in ("ordinal","window_ordinal","window_start_sample","window_end_sample","nj_snapshot_index")),"TIME_TYPE_INVALID")
        b.require(type(row["pcm_sha256"]) is str and len(row["pcm_sha256"])==64
            and all(c in "0123456789abcdef" for c in row["pcm_sha256"]),"PAYLOAD_HASH_INVALID")
    expected_controls = [dict(arm="ORDERED",functional_fields=["profile_digest","ordered_values","native_windows"],
        formula="delta[k,i]=z[k+1,i]-z[k,i];step[k]=sum(abs(delta[k,i]) for i=0..47)/48;T=sum(step[k] for k=0..3)"),
        dict(arm="ENDPOINTS",functional_fields=["profile_digest","first_values","last_values"],formula="E=sum(abs(last[i]-first[i]) for i=0..47)/48"),
        dict(arm="UNORDERED",functional_fields=["profile_digest","values_f64le_sorted"],
            formula="lexicographic byte sort of five <48d vectors; preserve multiplicity",
            forbidden_functional_fields=["source_id","stream_id","ordinal","window_ordinal","native_windows","clock_id",
                "snapshot_index","state_digest","source_digest","recipe","seed"],provenance_outside_functional_input=True)]
    b.require(execution["controls"]==expected_controls,"CONTROL_LEAKAGE_OR_FORM_INVALID")
    b.require(execution["indices"]==list(range(48)) and execution["cross_stream_deltas"] is False
        and execution["arithmetic"]=="binary64; Python builtin sum in ascending band and time order; no tolerance","MEASUREMENT_BINDING_INVALID")
    b.require(evaluation["categories"]==dict(s01="UNCHANGED_CONTINUATION",s02="CONTINUOUS_LEVEL",s03="ORDER_CONTROL",
        s04="CONTINUOUS_FREQUENCY",s05="COMPONENT_ADDITION_AND_REMOVAL",s06="SOURCE_CHANGE"),"CATEGORY_BINDING_INVALID")
    b.require(evaluation["criteria"]==[dict(check_id=f"o{n:02d}",left=l,right=r,operator="LT",role=role)
        for n,(l,r,role) in enumerate((("s02","s03","PRIMARY"),("s01","s02","DESCRIPTIVE"),("s01","s04","DESCRIPTIVE"),
            ("s01","s05","DESCRIPTIVE"),("s01","s06","DESCRIPTIVE")),1)],"CRITERIA_BINDING_INVALID")
    b.require(evaluation["required_control_equalities"]==["s02/s03:first-and-last-bitwise","s02/s03:entire-unordered-multiset-bitwise"]
        and all(evaluation[k] is True for k in ("primary_requires_both_equalities","descriptive_does_not_replace_primary",
            "generation_categories_are_not_recognized","no_threshold_fitting","no_replacement_source"))
        and all(evaluation[k] is False for k in ("ties_pass","source_continuity_proven","learning_binding_proven")),"EVALUATION_POLICY_INVALID")
    b.require("categories" not in execution and "criteria" not in execution,"EVALUATION_ROOT_LEAKAGE")
    b.require(execution["profiles"]==b.profile_binding() and execution["budgets"]==b.budgets(),"PROFILE_BUDGET_INVALID")
    b.require(all(execution[k] is False for k in ("receptor_execution_authorized","nj_execution_authorized",
        "comparison_execution_authorized","system_execution_authorized")),"AUTHORIZATION_INVALID")
    pairs = [[f"nu-s02-w{j:02d}",f"nu-s03-w{k:02d}"] for k,j in enumerate((0,3,1,2,4))]
    b.require(seal["payload_correspondences"]==pairs,"PERMUTATION_BINDING_INVALID")
    by_id = {x["source_id"]:x for x in execution["sources"]}
    for l,r in pairs:
        b.require(by_id[l]["pcm_sha256"]==by_id[r]["pcm_sha256"] and by_id[l]["source_digest"]!=by_id[r]["source_digest"]
            and by_id[l]["window_start_sample"]!=by_id[r]["window_start_sample"],"PAYLOAD_CORRESPONDENCE_INVALID")
    buckets = {}
    for row in execution["sources"]:
        buckets.setdefault(row["pcm_sha256"],[]).append(row["source_id"])
    collisions = [dict(pcm_sha256=h,source_ids=ss) for h,ss in sorted(buckets.items()) if len(ss)>1]
    b.require(seal["collisions"]==collisions,"COLLISION_BINDING_INVALID")
    b.require(seal["status"]=="S2NU_SOURCES_PRESEALED" and seal["attempted_sources"]==seal["completed_sources"]==30
        and seal["generated_pcm_bytes"]==576000 and seal["max_live_payloads"]==1 and seal["main_gate_after"] is False
        and all(seal[k]==0 for k in ("raw_payloads_persisted","receptor_calls","nj_calls","difference_calls","order_evaluations",
            "memory_calls","field_calls","context_calls","runtime_calls")),"COUNTERS_INVALID")
    return dict(windows=30,streams=6,payload_correspondences=5,criteria_bound_not_evaluated=5,collisions=collisions,
        unordered_functional_fields=expected_controls[2]["functional_fields"],payload_regenerations=0,
        payload_bytes_independently_recomputed=False,receptor_calls=0,nj_calls=0,difference_calls=0,order_evaluations=0)


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
        qualification = json.loads((b.QUAL_DIR/"result.json").read_bytes())
        check(qualification,"result_digest")
        b.require(qualification["status"]=="S2NU_SOURCE_BINDING_QUALIFIED" and qualification["passed_tests"]==16
            and qualification["unittest_calls"]==1 and qualification["hashes_before"]==qualification["hashes_after"]==execution["source_hashes"]
            and b.filehash(b.QUAL_DIR/"result.json")==seal["qualification_file_sha256"],"QUALIFICATION_INVALID")
        b.require(execution["environment"]==b.environment() and execution["generator"]==b.generator_identity(),"ENVIRONMENT_GENERATOR_INVALID")
        b.require(before=={n:b.filehash(out/n) for n in names} and b.MAIN_GATE is False,"READ_ONLY_INVALID")
        report = dict(run_id=out.name,status="S2NU_PRESEAL_VERIFIED",execution_digest=execution["execution_digest"],
            evaluation_digest=evaluation["evaluation_digest"],seal_digest=seal["seal_digest"],work=work,
            file_hashes_before=before,file_hashes_after=before,read_only=True,verification_calls=1,main_gate_after=False)
    except Exception as exc:
        report = dict(run_id=out.name,status="NOT_EVALUABLE",error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),verification_calls=1,retry=False)
    result = b.sealed(report,"verification_digest")
    b.publish(out/"verification.json",result,262144)
    return result
