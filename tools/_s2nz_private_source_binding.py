"""Receptor-free NZ sources; frozen histories and predictions are metadata only."""
import ast
from dataclasses import dataclass
import hashlib
import math
import re
import struct
from tools import _s2ny_private_source_binding as old

ROOT, common = old.ROOT, old.common
canonical, digest, sealed = old.canonical, old.digest, old.sealed
filehash, publish, read_canonical = old.filehash, old.publish, old.read_canonical
environment, profile_binding = old.environment, old.profile_binding
prepare_groups, group_value = old.prepare_groups, old.pure.group_value
load_freezes = old.load_freezes
FORBIDDEN_CALLS = old.FORBIDDEN_CALLS
MAIN_GATE = False
QUAL_ID = "s2nz-source-binding-qualification-20260909-01"
RUN_ID = "s2nz-source-preseal-20260909-01"
QUAL_DIR = ROOT/"reports/s2nz"/QUAL_ID
CONTRACT = "docs/S2NZ_STATISCHER_PLAN_BELASTBARKEIT_GESPEICHERTER_VORHERSAGEN.md"
PINS = {**old.PINS, CONTRACT:"aec5a731d455bd05c2c043c7e4224d403f2634e0be046f89fd395ae04aaf9a6c",
    "tools/_s2ny_private_source_binding.py":"2d29d9005876c01215133a5a60f4dd2b7dfbeea848d956791814301186d8642d",
    "tools/_s2ny_private_preseal_verification.py":"2b8fcd5ef8e818c3b6ad2a888e6b5736dc3e4e1298cfb8d5e3531f1dc1bf5796",
    "tests/test_s2ny_private_source_binding.py":"a2ee9eef84fd6f600737404741b9d978569c31e327e15e018bf0ad9c31c98a77"}
OWN = ("tools/_s2nz_private_source_binding.py","tools/_s2nz_private_preseal_verification.py",
    "tests/test_s2nz_private_source_binding.py","reports/s2nz/qualify_once.py",
    "reports/s2nz/preseal_once.py","reports/s2nz/QUALIFIKATIONSBINDUNG.md")
GROUPS = (((730,2190,6570),"s2nz-pcm-001"),((1010,3030,9090),"s2nz-pcm-002"))
ROWS = (((0,128),(0,320),(0,368),(0,380),(0,383)),
        ((0,128),(0,320),(0,368),(0,380),(0,383)),
        ((0,128),(0,320),(0,464),(0,572),(0,653)),
        ((0,128),(0,320),(0,464),(0,572),(0,653)),
        ((0,128),(0,320),(0,464),(1,464),(1,464)),
        ((0,128),(0,320),(0,464),(1,464),(1,464)))
NOISE_SEEDS = (None,"s2nz-noise-001",None,"s2nz-noise-002",None,"s2nz-noise-003")


class S2NZError(ValueError):
    def __init__(self,code):
        self.code=code
        super().__init__(code)


def require(ok,code):
    if not ok:
        raise S2NZError(code)


def check(obj,key):
    require(type(obj) is dict and obj.get(key)==digest({k:v for k,v in obj.items() if k!=key}),"SEALED_DIGEST_INVALID")


def native_index(start):
    require(type(start) is int and start>=0 and start%480==0,"NATIVE_TIME_INVALID")
    return start//480


@dataclass(frozen=True,slots=True)
class WindowSpec:
    stream: int
    window: int

    def __post_init__(self):
        require(type(self.stream) is int and 0<=self.stream<6 and type(self.window) is int and 0<=self.window<5,"WINDOW_SPEC_INVALID")

    def recipe(self):
        group,numerator=ROWS[self.stream][self.window]
        frequencies,seed=GROUPS[group]
        noise_seed=NOISE_SEEDS[self.stream]
        return dict(schema="s2nz.pcm-window-recipe.v1",sample_rate=48000,sample_count=4800,
            group=dict(seed=seed,partials=[dict(frequency_ratio=[f,1],amplitude_ratio=[a,20])
                for f,a in zip(frequencies,(4,2,1),strict=True)]),gain_ratio=[numerator,1024],
            noise=dict(seed=noise_seed,window=self.window if noise_seed else None,amplitude_ratio=[1 if noise_seed else 0,1024]),
            synthesis_time="float(j)/48000.0; j=0..4799",rounding="group-sum;gain;optional-noise-add;single-f32le")

    def payload(self):
        n=self.stream*5+self.window
        recipe=self.recipe()
        return dict(source_id=f"nz-s{self.stream+1:02d}-w{self.window:02d}",ordinal=n+1,
            stream_id=f"s{self.stream+1:02d}",window_ordinal=self.window,format="PCM_F32LE",channels=1,
            clock_id="audio.sample",window_start_sample=n*4800,window_end_sample=(n+1)*4800,
            nj_snapshot_index=native_index(n*4800),pcm_byte_count=19200,recipe=recipe,recipe_digest=digest(recipe))


def specs():
    return tuple(WindowSpec(s,k) for s in range(6) for k in range(5))


def bind_source(spec,payload_hash):
    require(type(spec) is WindowSpec,"WINDOW_SPEC_INVALID")
    spec.__post_init__()
    require(old.sha(payload_hash),"PAYLOAD_HASH_INVALID")
    return sealed({**spec.payload(),"pcm_sha256":payload_hash},"source_digest")


def noise_value(seed,k,j):
    require(type(seed) is str and re.fullmatch(r"[a-z0-9-]{1,64}",seed) is not None,"NOISE_SEED_INVALID")
    require(type(k) is int and 0<=k<5 and type(j) is int and 0<=j<4800,"NOISE_INDEX_INVALID")
    u=int.from_bytes(hashlib.sha256(f"{seed}:{k}:{j}".encode("ascii")).digest()[:4],"little")
    v=(float(u)/4294967296.0)*2.0-1.0
    return (1.0/1024.0)*v


def render(group,gain_ratio,indices,seed=None,window=None):
    require(type(indices) is tuple and 1<=len(indices)<=4800 and
        all(type(j) is int and 0<=j<4800 for j in indices),"PAYLOAD_SIZE_INVALID")
    require(type(gain_ratio) in (tuple,list) and len(gain_ratio)==2 and
        all(type(x) is int for x in gain_ratio) and gain_ratio[1]==1024 and 0<=gain_ratio[0]<=1024,"GAIN_FORM_INVALID")
    require((seed is None and window is None) or (type(seed) is str and
        re.fullmatch(r"[a-z0-9-]{1,64}",seed) is not None and type(window) is int and 0<=window<5),"NOISE_BINDING_INVALID")
    gain=float(gain_ratio[0])/1024.0
    payload=bytearray(4*len(indices))
    for offset,j in enumerate(indices):
        value=group_value(group,float(j)/48000.0)
        value=value*gain
        if seed is not None:
            value=value+noise_value(seed,window,j)
        require(math.isfinite(value) and abs(value)<=1.0,"PCM_DOMAIN_INVALID")
        struct.pack_into("<f",payload,4*offset,value)
    return payload


def pcm_window(spec):
    require(type(spec) is WindowSpec,"WINDOW_SPEC_INVALID")
    spec.__post_init__()
    r=spec.recipe()
    return render(prepare_groups([r["group"]])[0],r["gain_ratio"],tuple(range(4800)),r["noise"]["seed"],r["noise"]["window"])


def noise_contract():
    return dict(schema="s2nz.additive-pcm-noise.v1",numerator=1,denominator=1024,
        input="ASCII(seed+':'+str(k)+':'+str(j))",digest="SHA256",integer="unsigned-LE-first-four-bytes",
        formula="u/4294967296.0;*2.0;-1.0;*(1.0/1024.0)",application="after-gain-before-single-f32le",
        clean_addition=False,clipping=False,normalization=False,seed_search=False)


def forecast_sites():
    result=[]
    for s in range(1,7):
        for k in (2,3,4):
            n=(s-1)*3+k-1
            names=[f"nz-s{s:02d}-w{j:02d}" for j in range(k)]
            result.append(dict(site_id=f"p{n:02d}",stream_id=f"s{s:02d}",target=k,origin=k-1,
                available_source_ids=names,target_source_id=f"nz-s{s:02d}-w{k:02d}",delta_source_ids=names[-2:],
                local_source_ids=names[-3:] if k>2 else [],previous_error_site=f"p{n-1:02d}" if k>2 else None,
                histories=["H1","H2"],local_available=k>2,updates_allowed=False))
    return result


def prediction_contract():
    return {**old.prediction_contract(),"target":"next-actually-observed-half-vector-in-same-stream",
        "clean_counterpart_as_input":False,"clean_counterpart_as_target":False,"functional_run_authorized":False}


def budgets():
    limits=old.budgets()
    limits.pop("strict_criteria")
    return {**limits,"relevance_comparisons_reserved":12,"relevance_comparisons_used":0,
        "noise_hashes":72000,"disturbed_windows":15,"diagnostic_focus_N":4}


def execution_plan(sources,env,hashes,generator,freezes):
    require(type(sources) is list and len(sources)==30,"SOURCE_COUNT_INVALID")
    for spec,row in zip(specs(),sources,strict=True):
        require(type(row) is dict and row==bind_source(spec,row.get("pcm_sha256")),"SOURCE_BINDING_INVALID")
    check(freezes,"freeze_import_digest")
    return sealed(dict(schema="s2nz.source-execution-plan.v1",contract_sha256=PINS[CONTRACT],sources=sources,
        source_order=[s.payload()["source_id"] for s in specs()],environment=env,profiles=profile_binding(),
        source_hashes=hashes,generator=generator,freeze_import=freezes,forecast_sites=forecast_sites(),
        noise_contract=noise_contract(),prediction_contract=prediction_contract(),budgets=budgets(),
        authorizations={name:False for name in FORBIDDEN_CALLS}),"execution_digest")


def evaluation_plan(ex):
    return sealed(dict(schema="s2nz.diagnostic-evaluation-plan.v1",contract_sha256=PINS[CONTRACT],
        execution_digest=ex["execution_digest"],categories=dict(s01="H1_CLEAN",s02="H1_DISTURBED",
            s03="H2_CLEAN",s04="H2_DISTURBED",s05="CHANGE_CLEAN",s06="CHANGE_DISTURBED"),
        control_pairs=[["s01","s02"],["s03","s04"],["s05","s06"]],
        focus=dict(site_ids=["p05","p06","p11","p12"],N=4,emitted_denominator="D_SEPARATE",abstention_removes_case=False),
        reporting=dict(N=18,sufficient_prefix_N=12,per_stream_N=3,per_stream_local_N=2,
            absolute_mae=True,absolute_gains=True,clean_disturbed_separate=True,fixed_histories_recommendations_separate=True,
            compare_LOCAL=True,compare_PERSIST=True,no_recommendation_mae=None,empty_D="NUTZEN_NICHT_GEPRUEFT",
            target_phases={"2":"INITIAL_TARGET","3":"FIRST_BRANCH","4":"FOLLOWUP"},
            wins_losses_separate=True,gain_compensation=False,common_prefix_independent_replication=False),
        target="next-actually-observed-half-vector-in-same-stream",clean_reconstruction_target=False,
        criteria=[],practical_threshold=None,practical_success_status=False,robustness_status=False,
        later_application_decision="analyst-after-complete-diagnostic-evidence",
        integration_authorized=False,further_noise_search=False),"evaluation_digest")


def watched():
    require(all(filehash(ROOT/p)==h for p,h in PINS.items()),"PIN_CHANGED")
    return {p:filehash(ROOT/p) for p in sorted(set(PINS)|set(OWN))}


def generator_identity():
    bindings=[]
    for path,names in (("tools/_s2nu_private_source_binding.py",("prepare_groups","group_value")),
            (OWN[0],("noise_value","render","pcm_window"))):
        tree=ast.parse((ROOT/path).read_text(encoding="utf-8"))
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        require(len(nodes)==len(names),"GENERATOR_IDENTITY_INVALID")
        bindings.append(dict(path=path,file_sha256=filehash(ROOT/path),functions=list(names),
            ast_digest=digest(ast.dump(ast.Module(body=nodes,type_ignores=[]),include_attributes=False))))
    return dict(bindings=bindings,historical_entry_executed=False)


def qualification(hashes):
    q=read_canonical(QUAL_DIR/"result.json",65536)
    check(q,"result_digest")
    require(q.get("run_id")==QUAL_ID and q.get("status")=="S2NZ_SOURCE_BINDING_QUALIFIED"
        and q.get("passed_tests")==24 and q.get("unittest_calls")==1 and q.get("exit_code")==0
        and q.get("hashes_before")==q.get("hashes_after")==hashes,"QUALIFICATION_INVALID")
    return q


def preseal_once(run_id):
    require(run_id==RUN_ID and MAIN_GATE is False,"RUN_BINDING_INVALID")
    out=ROOT/"reports/s2nz"/run_id
    out.mkdir(exist_ok=False)
    phase,sid,attempted,rows,before="QUALIFICATION_BINDING",None,0,[],{}
    try:
        before=watched()
        qualification(before)
        phase="NX_FREEZE_BINDING"
        freezes=load_freezes()
        phase="ENVIRONMENT_BINDING"
        env,gen=environment(),generator_identity()
        publish(out/"preregistration.json",dict(run_id=run_id,hashes=before,environment=env,generator=gen,
            windows=[s.payload() for s in specs()],freeze_import=freezes,forecast_sites=forecast_sites(),
            noise_contract=noise_contract(),prediction_contract=prediction_contract(),
            evaluation=evaluation_plan(dict(execution_digest="0"*64)),budgets=budgets(),retry=False),65536)
        for spec in specs():
            phase,sid="PCM_GENERATION",spec.payload()["source_id"]
            attempted+=1
            payload=pcm_window(spec)
            try:
                require(type(payload) is bytearray and len(payload)==19200,"PAYLOAD_FORM_INVALID")
                h=hashlib.sha256(payload).hexdigest()
            finally:
                del payload
            rows.append(bind_source(spec,h))
        phase,sid="PLAN_BINDING",None
        ex=execution_plan(rows,env,before,gen,freezes)
        ev=evaluation_plan(ex)
        after=watched()
        require(before==after and environment()==env,"BINDINGS_CHANGED")
        phase="PUBLICATION"
        ef=publish(out/"execution-plan.json",ex,65536)
        vf=publish(out/"evaluation-plan.json",ev,65536)
        seal=sealed(dict(schema="s2nz.source-seal.v1",run_id=run_id,status="S2NZ_SOURCES_PRESEALED",
            execution_digest=ex["execution_digest"],evaluation_digest=ev["evaluation_digest"],
            execution_file_sha256=ef,evaluation_file_sha256=vf,hashes_before=before,hashes_after=after,
            qualification_file_sha256=filehash(QUAL_DIR/"result.json"),freeze_import_digest=freezes["freeze_import_digest"],
            attempted_sources=attempted,completed_sources=len(rows),generated_pcm_bytes=576000,max_live_payloads=1,
            noise_hashes=72000,raw_payloads_persisted=0,collisions=common.collision_groups(rows),
            **{name:0 for name in FORBIDDEN_CALLS},main_gate_after=MAIN_GATE),"seal_digest")
        publish(out/"seal.json",seal,65536)
    except Exception as exc:
        publish(out/"failure.json",sealed(dict(run_id=run_id,status="NOT_EVALUABLE",phase=phase,source_id=sid,
            attempted_sources=attempted,completed_sources=len(rows),error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),hashes_before=before,retry=False,
            main_gate_after=False),"failure_digest"),65536)
    return out
