"""Read-only NY binding checks; no payload, learner or predictor calls."""
from tools import _s2ny_private_source_binding as b


def verify_bundle(ex, ev, seal, hashes, freezes):
    for obj,key in ((ex,"execution_digest"),(ev,"evaluation_digest"),(seal,"seal_digest")):
        b.require(len(b.canonical(obj))<=65536,"METADATA_SIZE_INVALID")
        b.check(obj,key)
    b.require(set(ex)=={"schema","contract_sha256","sources","source_order","environment","profiles",
        "source_hashes","generator","freeze_import","forecast_sites","prediction_contract","budgets",
        "authorizations","execution_digest"},"EXECUTION_FORM_INVALID")
    b.require(ex["schema"]=="s2ny.source-execution-plan.v1" and ev["schema"]=="s2ny.evaluation-plan.v1"
        and seal["schema"]=="s2ny.source-seal.v1","SCHEMA_INVALID")
    b.require(ex["contract_sha256"]==ev["contract_sha256"]==b.PINS[b.CONTRACT]
        and ex["source_hashes"]==seal["hashes_before"]==seal["hashes_after"]==hashes,"CODE_BINDING_INVALID")
    b.require(ex["execution_digest"]==ev["execution_digest"]==seal["execution_digest"]
        and ev["evaluation_digest"]==seal["evaluation_digest"],"ROOT_BINDING_INVALID")
    b.check(ex["freeze_import"],"freeze_import_digest")
    b.require(b.canonical(ex["freeze_import"])==b.canonical(freezes)
        and seal["freeze_import_digest"]==freezes["freeze_import_digest"],"FREEZE_IMPORT_INVALID")
    b.require(ex["profiles"]==b.profile_binding() and ex["budgets"]==b.budgets(),"PROFILE_BUDGET_INVALID")
    b.require(ex["authorizations"]=={key:False for key in b.FORBIDDEN_CALLS}
        and all(value is False for value in ex["authorizations"].values()),"AUTHORIZATION_INVALID")
    # Independent literal reconstruction, not WindowSpec or the source-plan builder.
    gains = ((128,320,368,380,383),(128,320,464,572,653),(128,192,320,576,960),
             (320,320,320,320,320),(128,320,368,320,308),(128,320,464,464,464))
    order = [f"ny-s{s:02d}-w{k:02d}" for s in range(1,7) for k in range(5)]
    b.require(ex["source_order"]==order and len(ex["sources"])==30,"SOURCE_ORDER_INVALID")
    for n,row in enumerate(ex["sources"]):
        s,k = divmod(n,5)
        group = 1 if s==5 and k>=3 else 0
        frequencies = (670,2010,6030) if group==0 else (890,2670,8010)
        recipe = dict(schema="s2ny.pcm-window-recipe.v1",sample_rate=48000,sample_count=4800,
            group=dict(seed=f"s2ny-pcm-{group+1:03d}",partials=[dict(frequency_ratio=[f,1],amplitude_ratio=[a,20])
                for f,a in zip(frequencies,(4,2,1),strict=True)]),gain_ratio=[gains[s][k],1024],
            synthesis_time="float(j)/48000.0; j=0..4799",rounding="binary64-group-sum-then-gain-then-single-f32le")
        expected = dict(source_id=order[n],ordinal=n+1,stream_id=f"s{s+1:02d}",window_ordinal=k,
            format="PCM_F32LE",channels=1,clock_id="audio.sample",window_start_sample=n*4800,
            window_end_sample=(n+1)*4800,nj_snapshot_index=n*10,pcm_byte_count=19200,
            recipe=recipe,recipe_digest=b.digest(recipe))
        b.check(row,"source_digest")
        b.require(b.sha(row.get("pcm_sha256")),"PAYLOAD_HASH_INVALID")
        b.require(b.canonical({a:v for a,v in row.items() if a not in ("source_digest","pcm_sha256")})
            == b.canonical(expected),"WINDOW_BINDING_INVALID")
    sites = []
    for s in range(1,7):
        for k in (2,3,4):
            n = (s-1)*3+k-1
            names = [f"ny-s{s:02d}-w{j:02d}" for j in range(k)]
            sites.append(dict(site_id=f"p{n:02d}",stream_id=f"s{s:02d}",target=k,origin=k-1,
                available_source_ids=names,target_source_id=f"ny-s{s:02d}-w{k:02d}",
                delta_source_ids=names[-2:],local_source_ids=names[-3:] if k>=3 else [],
                previous_error_site=f"p{n-1:02d}" if k>=3 else None,histories=["H1","H2"],
                local_available=k>=3,updates_allowed=False))
    b.require(b.canonical(ex["forecast_sites"])==b.canonical(sites),"FORECAST_SITE_INVALID")
    # Formulae/budgets are shared immutable metadata, never evaluated here.
    b.require(b.canonical(ex["prediction_contract"])==b.canonical(b.prediction_contract()),"PREDICTOR_BOUNDARY_INVALID")
    b.require(b.canonical(ev)==b.canonical(b.evaluation_plan(ex)),"EVALUATION_BINDING_INVALID")
    buckets, recipes = {},{}
    for row in ex["sources"]:
        buckets.setdefault(row["pcm_sha256"],[]).append(row["source_id"])
        recipes.setdefault(row["recipe_digest"],[]).append(row)
    for rows in recipes.values():
        b.require(len({x["pcm_sha256"] for x in rows})==1 and len({x["source_digest"] for x in rows})==len(rows),
            "EXACT_COPY_BINDING_INVALID")
    collisions = [dict(pcm_sha256=h,source_ids=ids) for h,ids in sorted(buckets.items()) if len(ids)>1]
    b.require(seal["collisions"]==collisions,"COLLISION_BINDING_INVALID")
    b.require(seal["status"]=="S2NY_SOURCES_PRESEALED" and
        all(type(seal[k]) is int and seal[k]==30 for k in ("attempted_sources","completed_sources"))
        and seal["generated_pcm_bytes"]==576000 and seal["max_live_payloads"]==1
        and seal["main_gate_after"] is False and seal["raw_payloads_persisted"]==0
        and all(type(seal[k]) is int and seal[k]==0 for k in b.FORBIDDEN_CALLS),"COUNTERS_INVALID")
    return dict(windows=30,streams=6,freeze_payloads_bound=2,forecast_sites_bound=18,local_sites_bound=12,
        criteria_bound_not_evaluated=20,W_loss_predictions_bound_not_guaranteed=8,collisions=collisions,
        payload_regenerations=0,payload_bytes_independently_recomputed=False,
        nx_learning_arithmetic_replayed=False,chronological_recommendation_execution_qualified=False,
        shared_formula_metadata=True,**{key:0 for key in b.FORBIDDEN_CALLS})


def verify_once(out):
    with (out/"verification.claim").open("xb"):
        pass
    try:
        names = ("execution-plan.json","evaluation-plan.json","seal.json")
        before = {n:b.filehash(out/n) for n in names}
        ex,ev,seal = [b.read_canonical(out/n,65536) for n in names]
        work = verify_bundle(ex,ev,seal,b.watched(),b.load_freezes())
        b.require(seal["run_id"]==out.name==b.RUN_ID,"RUN_ID_INVALID")
        b.require(seal["execution_file_sha256"]==before[names[0]]
            and seal["evaluation_file_sha256"]==before[names[1]],"FILE_BINDING_INVALID")
        b.qualification(ex["source_hashes"])
        b.require(b.filehash(b.QUAL_DIR/"result.json")==seal["qualification_file_sha256"],"QUALIFICATION_INVALID")
        b.require(ex["environment"]==b.environment() and ex["generator"]==b.generator_identity(),"ENVIRONMENT_GENERATOR_INVALID")
        b.require(before=={n:b.filehash(out/n) for n in names} and b.MAIN_GATE is False,"READ_ONLY_INVALID")
        report = dict(run_id=out.name,status="S2NY_PRESEAL_VERIFIED",execution_digest=ex["execution_digest"],
            evaluation_digest=ev["evaluation_digest"],seal_digest=seal["seal_digest"],work=work,
            file_hashes_before=before,file_hashes_after=before,read_only=True,verification_calls=1,main_gate_after=False)
    except Exception as exc:
        report = dict(run_id=out.name,status="NOT_EVALUABLE",error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),verification_calls=1,retry=False)
    result = b.sealed(report,"verification_digest")
    b.publish(out/"verification.json",result,262144)
    return result
