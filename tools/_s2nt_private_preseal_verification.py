"""Independent offline NT inventory verification, without payload generation."""
import ast
import json

from tools import _s2nt_private_source_binding as b


def check_sealed(value, key):
    b.require(type(value) is dict and value.get(key) == b.digest({k:v for k,v in value.items() if k != key}),
              "SEALED_DIGEST_INVALID")


def verify_bundle(execution, evaluation, seal, hashes):
    for obj,key in ((execution,"execution_digest"),(evaluation,"evaluation_digest"),(seal,"seal_digest")):
        check_sealed(obj,key)
    b.require(set(execution) == {"schema","contract_sha256","sources","source_order","pairs","diagnostic",
        "environment","generator","profiles","source_hashes","budgets","receptor_execution_authorized",
        "nj_execution_authorized","comparison_execution_authorized","system_execution_authorized","execution_digest"},
        "EXECUTION_FORM_INVALID")
    b.require(execution["schema"] == "s2nt.source-execution-plan.v1"
        and evaluation["schema"] == "s2nt.evaluation-plan.v1" and seal["schema"] == "s2nt.source-seal.v1",
        "SCHEMA_INVALID")
    b.require(execution["contract_sha256"] == evaluation["contract_sha256"] == b.PINS[b.CONTRACT]
        and execution["source_hashes"] == seal["hashes_before"] == seal["hashes_after"] == hashes,
        "CODE_BINDING_INVALID")
    b.require(execution["execution_digest"] == evaluation["execution_digest"] == seal["execution_digest"]
        and evaluation["evaluation_digest"] == seal["evaluation_digest"],"ROOT_BINDING_INVALID")
    ids = [f"nt-a{i:02d}" for i in range(1,15)]
    b.require(execution["source_order"] == ids and len(execution["sources"]) == 14,"SOURCE_ORDER_INVALID")
    # Literal second transcription of the approved tables, not the binding builder.
    frequencies = ((310000,1240000,5580000),(470000,1880000,8460000),
        (319300,1277200,5747400),(484100,1936400,8713800),
        (733000,2932000,11728000),(887000,3548000,14192000))
    seeds = ("s2nt-pcm-001","s2nt-pcm-002","s2nt-pcm-001","s2nt-pcm-002","s2nt-pcm-003","s2nt-pcm-004")
    amps = (((4,20),(2,20),(1,20)),((3,20),(3,40),(3,80)),((4,20),(2,20),(0,1)),((0,1),(0,1),(1,20)))
    recipes = (((0,0),),((1,0),),((0,0),),((0,1),),((2,0),),((0,0),(1,3)),((0,2),(1,3)),
               ((1,0),),((1,1),),((3,0),),((1,0),(0,3)),((1,2),(0,3)),((4,0),),((5,0),))
    for n,(row,recipe) in enumerate(zip(execution["sources"],recipes,strict=True),1):
        check_sealed(row,"source_digest")
        groups = [dict(seed=seeds[g],partials=[dict(frequency_millihz=f,amplitude_ratio=list(a))
            for f,a in zip(frequencies[g],amps[k],strict=True)]) for g,k in recipe]
        expected_recipe = dict(sample_count=4800,sample_rate=48000,groups=groups)
        expected = dict(source_id=ids[n-1],ordinal=n,format="PCM_F32LE",channels=1,recipe=expected_recipe,
            recipe_digest=b.digest(expected_recipe),clock_id="audio.sample",window_start_sample=(n-1)*4800,
            window_end_sample=n*4800,nj_snapshot_index=(n-1)*10,pcm_byte_count=19200)
        b.require({k:v for k,v in row.items() if k not in ("source_digest","pcm_sha256")} == expected,
            "SOURCE_METADATA_INVALID")
        b.require(type(row.get("pcm_sha256")) is str and len(row["pcm_sha256"]) == 64
            and all(c in "0123456789abcdef" for c in row["pcm_sha256"]),"PAYLOAD_HASH_INVALID")
    pairs = [dict(pair_id=f"d{q:02d}-{r:02d}",source_id=f"nt-a{q:02d}",reference_id=f"nt-a{r:02d}")
        for q in range(3,15) for r in (1,2)]
    pairs.append(dict(pair_id="d01-02",source_id="nt-a01",reference_id="nt-a02"))
    b.require(execution["pairs"] == pairs,"PAIR_BINDING_INVALID")
    checks = []
    for r,variants,mixes in ((1,(4,5),(6,7)),(2,(9,10),(11,12))):
        for v in variants:
            for m in mixes:
                checks.append(("PRIMARY",f"d{v:02d}-{r:02d}",f"d{m:02d}-{r:02d}"))
    for r,variants in ((1,(4,5)),(2,(9,10))):
        for v in variants:
            checks.append(("ATTRIBUTION",f"d{v:02d}-{r:02d}",f"d{v:02d}-{3-r:02d}"))
    for r,variants in ((1,(4,5)),(2,(9,10))):
        for v in variants:
            for right in (f"d13-{r:02d}",f"d14-{r:02d}","d01-02"):
                checks.append(("CONTROL",f"d{v:02d}-{r:02d}",right))
    b.require(evaluation["order_checks"] == [dict(check_id=f"o{i:02d}",group=g,left=l,operator="LT",right=r)
        for i,(g,l,r) in enumerate(checks,1)],"ORDER_BINDING_INVALID")
    b.require(evaluation["families"] == [dict(reference="nt-a01",exact="nt-a03",level="nt-a04",frequency="nt-a05",addition="nt-a06",replacement="nt-a07"),
        dict(reference="nt-a02",exact="nt-a08",level="nt-a09",frequency="nt-a10",addition="nt-a11",replacement="nt-a12")]
        and evaluation["independent_controls"] == ["nt-a13","nt-a14"],"EVALUATION_ROLES_INVALID")
    b.require(evaluation["operational_admission"] is None and all(evaluation[k] is True for k in
        ("ties_separate","exact_not_variation","nominal_variation_requires_changed_values","no_semantic_identity",
         "components_are_generator_provenance_only","no_threshold_fitting","no_success_start_gate",
         "no_replacement_source","negative_l1_not_universal_representation_failure")),"EVALUATION_POLICY_INVALID")
    b.require(execution["diagnostic"] == dict(indices=list(range(48)),arithmetic="historical sum in original index order / 48",
        threshold=None,direct_baseline=True,raw_and_half_equality_separate=True),"DIAGNOSTIC_BINDING_INVALID")
    b.require(execution["profiles"] == b.profile_binding() and execution["budgets"] == b.budgets(),"PROFILE_BUDGET_INVALID")
    b.require(all(execution[k] is False for k in ("receptor_execution_authorized","nj_execution_authorized",
        "comparison_execution_authorized","system_execution_authorized")),"AUTHORIZATION_INVALID")
    for a,c in ((0,2),(1,7)):
        x,y = execution["sources"][a],execution["sources"][c]
        b.require(x["pcm_sha256"] == y["pcm_sha256"] and x["source_digest"] != y["source_digest"],"EXACT_COPY_INVALID")
    buckets = {}
    for row in execution["sources"]:
        buckets.setdefault(row["pcm_sha256"],[]).append(row["source_id"])
    collisions = [dict(pcm_sha256=h,source_ids=ss) for h,ss in sorted(buckets.items()) if len(ss)>1]
    b.require(seal["collisions"] == collisions and seal["exact_pairs"] == [["nt-a01","nt-a03"],["nt-a02","nt-a08"]],
        "COLLISION_BINDING_INVALID")
    b.require(seal["status"] == "S2NT_SOURCES_PRESEALED" and seal["attempted_sources"] == seal["completed_sources"] == 14
        and seal["generated_pcm_bytes"] == 268800 and seal["max_live_payloads"] == 1
        and seal["main_gate_after"] is False and all(seal[k] == 0 for k in ("raw_payloads_persisted","receptor_calls",
            "nj_calls","distance_calls","memory_calls","field_calls","context_calls","runtime_calls")),"COUNTERS_INVALID")
    b.require(all(len(b.canonical(x)) <= b.MAX_METADATA_BYTES for x in (execution,evaluation,seal)),"SIZE_INVALID")
    return dict(sources=14,pairs=25,order_checks=24,exact_pairs=2,collisions=collisions,
        payload_regenerations=0,receptor_calls=0,nj_calls=0,distance_calls=0,
        payload_bytes_independently_recomputed=False)


def verify_once(out):
    with (out/"verification.claim").open("xb"):
        pass
    try:
        execution,evaluation,seal = [json.loads((out/n).read_bytes()) for n in ("execution-plan.json","evaluation-plan.json","seal.json")]
        work = verify_bundle(execution,evaluation,seal,b.watched())
        b.require(seal["run_id"] == out.name == b.RUN_ID,"RUN_ID_INVALID")
        b.require(seal["execution_file_sha256"] == b.filehash(out/"execution-plan.json")
            and seal["evaluation_file_sha256"] == b.filehash(out/"evaluation-plan.json"),"PLAN_FILE_INVALID")
        q = json.loads((b.QUAL_DIR/"result.json").read_bytes())
        check_sealed(q,"result_digest")
        b.require(b.filehash(b.QUAL_DIR/"result.json") == seal["qualification_file_sha256"]
            and q["status"] == "S2NT_SOURCE_BINDING_QUALIFIED"
            and q["hashes_before"] == q["hashes_after"] == execution["source_hashes"],"QUALIFICATION_INVALID")
        tree = ast.parse((b.ROOT/b.GENERATOR).read_text(encoding="utf-8"))
        node = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == "pcm_bytes")
        b.require(execution["generator"] == dict(path=b.GENERATOR,file_sha256=b.PINS[b.GENERATOR],function="pcm_bytes",
            ast_digest=b.digest(ast.dump(node,include_attributes=False)),historical_entry_executed=False)
            and execution["environment"] == b.environment(),"GENERATOR_ENVIRONMENT_INVALID")
        report = dict(run_id=out.name,status="S2NT_PRESEAL_VERIFIED",seal_digest=seal["seal_digest"],
            execution_digest=execution["execution_digest"],evaluation_digest=evaluation["evaluation_digest"],
            work=work,main_gate_after=b.MAIN_GATE,verification_calls=1)
    except Exception as exc:
        report = dict(run_id=out.name,status="NOT_EVALUABLE",error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),verification_calls=1,retry=False)
    result = b.sealed(report,"verification_digest")
    b.publish(out/"verification.json",result,262144)
    return result
