"""Receptor-free NU source extension using the existing preseal utilities."""
import ast
from dataclasses import dataclass
import hashlib
import json
import math
import struct

from tools import _s2np_private_source_binding as common

ROOT = common.ROOT
canonical,digest,sealed,filehash,publish = common.canonical,common.digest,common.sealed,common.filehash,common.publish
environment,profile_binding = common.environment,common.profile_binding
MAIN_GATE = False
QUAL_ID = "s2nu-source-binding-qualification-20260909-01"
RUN_ID = "s2nu-source-preseal-20260909-01"
QUAL_DIR = ROOT/"reports/s2nu"/QUAL_ID
CONTRACT = "docs/S2NU_STATISCHER_PLAN_AUDITIVE_VERLAUFSEVIDENZ.md"
PINS = {CONTRACT:"983057c24442de2c862a423525cb9c43c090caa69088724aefe8d912f9663d0f",
    "tools/_s2np_private_source_binding.py":"004ea7c8841e5f0b68fe9191604b0a0a7337ac568af2205dca900dd2ae874b12",
    "reports/s2nd/seal_inventory.py":"9f72d2a9fc9676235cf69b23ea690d25f0a782222c54393ecf5b44107f0ce91c",
    "mcm_field_organism/log_spectral_receptor.py":"26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0",
    "tools/_s2nj_private_auditory_output_projection.py":"e052cc76cf4c9678e11673d95390dea21634bba8082187567a760faaaf4904e5"}
OWN = ("tools/_s2nu_private_source_binding.py","tools/_s2nu_private_preseal_verification.py",
    "tests/test_s2nu_private_source_binding.py","reports/s2nu/qualify_once.py",
    "reports/s2nu/preseal_once.py","reports/s2nu/QUALIFIKATIONSBINDUNG.md")
MAX_METADATA_BYTES = 65536
MAX_OUTPUT_BYTES = 2097152
PERMUTATION = (0,3,1,2,4)
GROUPS = (((430,1290,3870),((4,20),(2,20),(1,20)),"s2nu-pcm-001"),
    ((710,2130,6390),((4,20),(2,20),(1,20)),"s2nu-pcm-002"),
    ((5870,),((1,20),),"s2nu-pcm-003"))


class S2NUError(ValueError):
    def __init__(self,code):
        self.code = code
        super().__init__(code)


def require(ok,code):
    if not ok:
        raise S2NUError(code)


def native_index(start):
    require(type(start) is int and start >= 0 and start % 480 == 0,"NATIVE_TIME_INVALID")
    return start//480


def groups_payload():
    return [dict(seed=seed,partials=[dict(frequency_ratio=[f,1],amplitude_ratio=list(a))
        for f,a in zip(fs,amps,strict=True)]) for fs,amps,seed in GROUPS]


@dataclass(frozen=True,slots=True)
class WindowSpec:
    stream: int
    window: int

    def __post_init__(self):
        require(type(self.stream) is int and 1 <= self.stream <= 6
            and type(self.window) is int and 0 <= self.window <= 4,"WINDOW_SPEC_INVALID")

    def recipe(self):
        return dict(schema="s2nu.pcm-window-recipe.v1",sample_rate=48000,sample_count=4800,
            expression_id=2 if self.stream == 3 else self.stream,
            synthesis_window_index=PERMUTATION[self.window] if self.stream == 3 else self.window,
            groups=groups_payload(),rounding="binary64-expression-then-single-f32le")

    def payload(self):
        start = (self.stream-1)*24000+self.window*4800
        recipe = self.recipe()
        return dict(source_id=f"nu-s{self.stream:02d}-w{self.window:02d}",ordinal=(self.stream-1)*5+self.window+1,
            stream_id=f"s{self.stream:02d}",window_ordinal=self.window,format="PCM_F32LE",channels=1,
            clock_id="audio.sample",window_start_sample=start,window_end_sample=start+4800,
            nj_snapshot_index=native_index(start),pcm_byte_count=19200,recipe=recipe,recipe_digest=digest(recipe))


def specs():
    return tuple(WindowSpec(s,k) for s in range(1,7) for k in range(5))


def bind_source(spec,sha):
    require(type(spec) is WindowSpec,"WINDOW_SPEC_INVALID")
    spec.__post_init__()
    require(type(sha) is str and len(sha)==64 and all(x in "0123456789abcdef" for x in sha),"PAYLOAD_HASH_INVALID")
    return sealed({**spec.payload(),"pcm_sha256":sha},"source_digest")


def prepare_groups(groups):
    result = []
    for group in groups:
        partials = []
        for index,partial in enumerate(group["partials"]):
            u = int.from_bytes(hashlib.sha256((group["seed"]+":"+str(index)).encode("ascii")).digest()[:4],"little")
            phase = (float(u)/4294967296.0)*math.tau
            f,a = partial["frequency_ratio"],partial["amplitude_ratio"]
            partials.append((float(f[0])/float(f[1]),float(a[0])/float(a[1]),phase))
        result.append(tuple(partials))
    return tuple(result)


def group_value(group,t):
    value = 0.0
    for f,a,phase in group:
        value += a*math.sin(((math.tau*f)*t)+phase)
    return value


def sample_value(expression,k,j,groups):
    require(expression in (1,2,4,5,6) and type(k) is int and 0 <= k <= 4
        and type(j) is int and 0 <= j < 4800,"SYNTHESIS_INDEX_INVALID")
    t = float(j)/48000.0
    if expression == 4:
        time = float(4800*k+j)/48000.0
        v = time+((4.0/100.0)*(time*time))
        return group_value(groups[0],v)
    x = group_value(groups[0],t)
    if expression == 1:
        return x
    if expression == 2:
        gain = 0.5+(0.5*(float(4800*k+j)/24000.0))
        return gain*x
    if expression == 5:
        h = (0.0,float(j)/4800.0,1.0,1.0-(float(j)/4800.0),0.0)[k]
        return x+(h*group_value(groups[2],t))
    w = (0.0,0.0,float(j)/4800.0,1.0,1.0)[k]
    return ((1.0-w)*x)+(w*group_value(groups[1],t))


def render(expression,k,groups,indices):
    require(type(indices) is tuple and 1 <= len(indices) <= 4800,"PAYLOAD_SIZE_INVALID")
    payload = bytearray(4*len(indices))
    for offset,j in enumerate(indices):
        value = sample_value(expression,k,j,groups)
        require(math.isfinite(value) and abs(value) <= 1.0,"PCM_DOMAIN_INVALID")
        struct.pack_into("<f",payload,offset*4,value)
    return payload


def pcm_window(spec):
    require(type(spec) is WindowSpec,"WINDOW_SPEC_INVALID")
    spec.__post_init__()
    recipe = spec.recipe()
    return render(recipe["expression_id"],recipe["synthesis_window_index"],
        prepare_groups(recipe["groups"]),tuple(range(4800)))


def controls():
    return [dict(arm="ORDERED",functional_fields=["profile_digest","ordered_values","native_windows"],
                 formula="delta[k,i]=z[k+1,i]-z[k,i];step[k]=sum(abs(delta[k,i]) for i=0..47)/48;T=sum(step[k] for k=0..3)"),
        dict(arm="ENDPOINTS",functional_fields=["profile_digest","first_values","last_values"],
             formula="E=sum(abs(last[i]-first[i]) for i=0..47)/48"),
        dict(arm="UNORDERED",functional_fields=["profile_digest","values_f64le_sorted"],
             formula="lexicographic byte sort of five <48d vectors; preserve multiplicity",
             forbidden_functional_fields=["source_id","stream_id","ordinal","window_ordinal","native_windows","clock_id",
                 "snapshot_index","state_digest","source_digest","recipe","seed"],provenance_outside_functional_input=True)]


def budgets():
    return dict(windows=30,generated_samples=144000,generated_pcm_bytes=576000,max_live_payloads=1,max_live_pcm_bytes=19200,
        future_analyses=30,future_nj=30,future_values_per_scale=1440,transitions_per_implementation=24,
        endpoint_pairs_per_implementation=6,both_differences=2880,both_control_equalities=672,
        offline_halvings=1440,offline_terms=2880,offline_sums=72,offline_control_equalities=672,
        order_checks=5,max_metadata_bytes=65536,max_output_bytes=2097152,max_verification_bytes=262144)


def execution_plan(sources,env,hashes,generator):
    require(len(sources)==30,"SOURCE_COUNT_INVALID")
    for spec,row in zip(specs(),sources,strict=True):
        require(row == bind_source(spec,row["pcm_sha256"]),"SOURCE_BINDING_INVALID")
    return sealed(dict(schema="s2nu.source-execution-plan.v1",contract_sha256=PINS[CONTRACT],sources=sources,
        source_order=[x.payload()["source_id"] for x in specs()],profiles=profile_binding(),environment=env,
        source_hashes=hashes,generator=generator,controls=controls(),budgets=budgets(),
        indices=list(range(48)),arithmetic="binary64; Python builtin sum in ascending band and time order; no tolerance",
        cross_stream_deltas=False,receptor_execution_authorized=False,nj_execution_authorized=False,
        comparison_execution_authorized=False,system_execution_authorized=False),"execution_digest")


def evaluation_plan(execution):
    return sealed(dict(schema="s2nu.evaluation-plan.v1",execution_digest=execution["execution_digest"],contract_sha256=PINS[CONTRACT],
        categories=dict(s01="UNCHANGED_CONTINUATION",s02="CONTINUOUS_LEVEL",s03="ORDER_CONTROL",s04="CONTINUOUS_FREQUENCY",
            s05="COMPONENT_ADDITION_AND_REMOVAL",s06="SOURCE_CHANGE"),
        criteria=[dict(check_id=f"o{n:02d}",left=l,right=r,operator="LT",role=role)
            for n,(l,r,role) in enumerate((("s02","s03","PRIMARY"),("s01","s02","DESCRIPTIVE"),
                ("s01","s04","DESCRIPTIVE"),("s01","s05","DESCRIPTIVE"),("s01","s06","DESCRIPTIVE")),1)],
        required_control_equalities=["s02/s03:first-and-last-bitwise","s02/s03:entire-unordered-multiset-bitwise"],
        primary_requires_both_equalities=True,ties_pass=False,descriptive_does_not_replace_primary=True,
        generation_categories_are_not_recognized=True,source_continuity_proven=False,learning_binding_proven=False,
        no_threshold_fitting=True,no_replacement_source=True),"evaluation_digest")


def correspondences():
    return [[f"nu-s02-w{j:02d}",f"nu-s03-w{k:02d}"] for k,j in enumerate(PERMUTATION)]


def watched():
    require(all(filehash(ROOT/p)==h for p,h in PINS.items()),"PIN_CHANGED")
    return {p:filehash(ROOT/p) for p in sorted(set(PINS)|set(OWN))}


def generator_identity():
    path = OWN[0]
    names = ("prepare_groups","group_value","sample_value","render","pcm_window")
    tree = ast.parse((ROOT/path).read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    require(len(nodes)==len(names),"GENERATOR_IDENTITY_INVALID")
    return dict(path=path,file_sha256=filehash(ROOT/path),functions=list(names),
        ast_digest=digest(ast.dump(ast.Module(body=nodes,type_ignores=[]),include_attributes=False)),historical_entry_executed=False)


def preseal_once(run_id):
    require(run_id==RUN_ID and MAIN_GATE is False,"RUN_BINDING_INVALID")
    out = ROOT/"reports/s2nu"/run_id
    out.mkdir(exist_ok=False)
    phase,sid,attempted,rows,before = "QUALIFICATION_BINDING",None,0,[],{}
    try:
        before = watched()
        q = json.loads((QUAL_DIR/"result.json").read_bytes())
        require(q["result_digest"]==digest({k:v for k,v in q.items() if k!="result_digest"})
            and q["status"]=="S2NU_SOURCE_BINDING_QUALIFIED" and q["passed_tests"]==16
            and q["unittest_calls"]==1 and q["exit_code"]==0
            and q["hashes_before"]==q["hashes_after"]==before,"QUALIFICATION_INVALID")
        phase = "ENVIRONMENT_BINDING"
        env,gen = environment(),generator_identity()
        publish(out/"preregistration.json",dict(run_id=run_id,hashes=before,environment=env,generator=gen,
            windows=[s.payload() for s in specs()],controls=controls(),evaluation=evaluation_plan(dict(execution_digest="0"*64)),
            budgets=budgets(),payload_correspondences=correspondences(),retry=False),MAX_METADATA_BYTES)
        for spec in specs():
            phase,sid = "PCM_GENERATION",spec.payload()["source_id"]
            attempted += 1
            payload = pcm_window(spec)
            try:
                require(type(payload) is bytearray and len(payload)==19200,"PAYLOAD_FORM_INVALID")
                sha = hashlib.sha256(payload).hexdigest()
            finally:
                del payload
            rows.append(bind_source(spec,sha))
        phase,sid = "CORRESPONDENCE_BINDING",None
        lookup = {x["source_id"]:x for x in rows}
        for left,right in correspondences():
            require(lookup[left]["pcm_sha256"]==lookup[right]["pcm_sha256"]
                and lookup[left]["source_digest"]!=lookup[right]["source_digest"],"PAYLOAD_CORRESPONDENCE_INVALID")
        execution = execution_plan(rows,env,before,gen)
        evaluation = evaluation_plan(execution)
        after = watched()
        require(before==after and environment()==env,"BINDINGS_CHANGED")
        phase = "PUBLICATION"
        ef = publish(out/"execution-plan.json",execution,MAX_METADATA_BYTES)
        vf = publish(out/"evaluation-plan.json",evaluation,MAX_METADATA_BYTES)
        seal = sealed(dict(schema="s2nu.source-seal.v1",run_id=run_id,status="S2NU_SOURCES_PRESEALED",
            execution_digest=execution["execution_digest"],evaluation_digest=evaluation["evaluation_digest"],
            execution_file_sha256=ef,evaluation_file_sha256=vf,hashes_before=before,hashes_after=after,
            qualification_file_sha256=filehash(QUAL_DIR/"result.json"),attempted_sources=attempted,completed_sources=len(rows),
            generated_pcm_bytes=576000,max_live_payloads=1,raw_payloads_persisted=0,
            payload_correspondences=correspondences(),collisions=common.collision_groups(rows),
            receptor_calls=0,nj_calls=0,difference_calls=0,order_evaluations=0,memory_calls=0,field_calls=0,
            context_calls=0,runtime_calls=0,main_gate_after=MAIN_GATE),"seal_digest")
        publish(out/"seal.json",seal,MAX_METADATA_BYTES)
    except Exception as exc:
        publish(out/"failure.json",sealed(dict(run_id=run_id,status="NOT_EVALUABLE",phase=phase,source_id=sid,
            attempted_sources=attempted,completed_sources=len(rows),error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),hashes_before=before,retry=False,main_gate_after=False),"failure_digest"),MAX_METADATA_BYTES)
    return out
