"""Receptor-free NV preseal; prediction formulae are metadata, not executable."""
import ast
from dataclasses import dataclass
import hashlib
import json
import math
import struct

from tools import _s2nu_private_source_binding as pure

common = pure.common
ROOT = common.ROOT
canonical, digest, sealed = common.canonical, common.digest, common.sealed
filehash, publish = common.filehash, common.publish
environment, profile_binding = common.environment, common.profile_binding
prepare_groups, group_value = pure.prepare_groups, pure.group_value
MAIN_GATE = False
QUAL_ID = "s2nv-source-binding-qualification-20260909-01"
RUN_ID = "s2nv-source-preseal-20260909-01"
QUAL_DIR = ROOT / "reports/s2nv" / QUAL_ID
CONTRACT = "docs/S2NV_STATISCHER_PLAN_PROSPEKTIVE_AUDITIVE_VERLAUFSVORHERSAGE.md"
PINS = {
    CONTRACT: "b2ac2c154fd81e7740e2bc16b96fff7d72d2739e90fd56675e16afd133366cee",
    "tools/_s2nu_private_source_binding.py": "8e0fa79f3ce66ce4228f46a52252de5d207c6cee29fefc42f957aa41dc56bce6",
    "tools/_s2np_private_source_binding.py": "004ea7c8841e5f0b68fe9191604b0a0a7337ac568af2205dca900dd2ae874b12",
    "reports/s2nd/seal_inventory.py": "9f72d2a9fc9676235cf69b23ea690d25f0a782222c54393ecf5b44107f0ce91c",
    "mcm_field_organism/log_spectral_receptor.py": "26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0",
    "tools/_s2nj_private_auditory_output_projection.py": "e052cc76cf4c9678e11673d95390dea21634bba8082187567a760faaaf4904e5",
}
OWN = ("tools/_s2nv_private_source_binding.py", "tools/_s2nv_private_preseal_verification.py",
       "tests/test_s2nv_private_source_binding.py", "reports/s2nv/qualify_once.py",
       "reports/s2nv/preseal_once.py", "reports/s2nv/QUALIFIKATIONSBINDUNG.md")
MAX_METADATA_BYTES = 65536
MAX_OUTPUT_BYTES = 2097152
GROUPS = (((470, 1410, 4230), "s2nv-pcm-001"), ((830, 2490, 7470), "s2nv-pcm-002"))
# Entries are (group index, numerator); every gain denominator is exactly 10.
ROWS = (((0, 4), (0, 5), (0, 6), (0, 7), (0, 8)),
        ((0, 4), (0, 5), (0, 6), (0, 5), (0, 4)),
        ((0, 4), (0, 5), (0, 6), (0, 6), (0, 6)),
        ((0, 4), (0, 5), (0, 6), (1, 6), (1, 6)))


class S2NVError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NVError(code)


def native_index(start):
    require(type(start) is int and start >= 0 and start % 480 == 0, "NATIVE_TIME_INVALID")
    return start // 480


@dataclass(frozen=True, slots=True)
class WindowSpec:
    stream: int
    window: int

    def __post_init__(self):
        require(type(self.stream) is int and 1 <= self.stream <= 4
                and type(self.window) is int and 0 <= self.window <= 4, "WINDOW_SPEC_INVALID")

    def recipe(self):
        group, numerator = ROWS[self.stream - 1][self.window]
        frequencies, seed = GROUPS[group]
        return dict(schema="s2nv.pcm-window-recipe.v1", sample_rate=48000, sample_count=4800,
            group=dict(seed=seed, partials=[dict(frequency_ratio=[f, 1], amplitude_ratio=[a, 20])
                for f, a in zip(frequencies, (4, 2, 1), strict=True)]),
            gain_ratio=[numerator, 10], synthesis_time="float(j)/48000.0; j=0..4799",
            rounding="binary64-group-sum-then-gain-then-single-f32le")

    def payload(self):
        start = (self.stream - 1) * 24000 + self.window * 4800
        recipe = self.recipe()
        return dict(source_id=f"nv-s{self.stream:02d}-w{self.window:02d}",
            ordinal=(self.stream - 1) * 5 + self.window + 1, stream_id=f"s{self.stream:02d}",
            window_ordinal=self.window, format="PCM_F32LE", channels=1, clock_id="audio.sample",
            window_start_sample=start, window_end_sample=start + 4800,
            nj_snapshot_index=native_index(start), pcm_byte_count=19200,
            recipe=recipe, recipe_digest=digest(recipe))


def specs():
    return tuple(WindowSpec(s, k) for s in range(1, 5) for k in range(5))


def bind_source(spec, sha):
    require(type(spec) is WindowSpec, "WINDOW_SPEC_INVALID")
    spec.__post_init__()
    require(type(sha) is str and len(sha) == 64 and all(x in "0123456789abcdef" for x in sha),
            "PAYLOAD_HASH_INVALID")
    return sealed({**spec.payload(), "pcm_sha256": sha}, "source_digest")


def render(group, gain_ratio, indices):
    require(type(indices) is tuple and 1 <= len(indices) <= 4800
            and all(type(j) is int and 0 <= j < 4800 for j in indices), "PAYLOAD_SIZE_INVALID")
    require(type(gain_ratio) in (tuple, list) and len(gain_ratio) == 2
            and all(type(x) is int for x in gain_ratio) and gain_ratio[1] == 10
            and 0 <= gain_ratio[0] <= 10, "GAIN_FORM_INVALID")
    gain = float(gain_ratio[0]) / 10.0
    payload = bytearray(4 * len(indices))
    for offset, j in enumerate(indices):
        value = gain * group_value(group, float(j) / 48000.0)
        require(math.isfinite(value) and abs(value) <= 1.0, "PCM_DOMAIN_INVALID")
        struct.pack_into("<f", payload, 4 * offset, value)
    return payload


def pcm_window(spec):
    require(type(spec) is WindowSpec, "WINDOW_SPEC_INVALID")
    spec.__post_init__()
    recipe = spec.recipe()
    return render(prepare_groups([recipe["group"]])[0], recipe["gain_ratio"], tuple(range(4800)))


def forecast_sites():
    return [dict(site_id=f"p{(s - 1) * 3 + k:02d}", stream_id=f"s{s:02d}", origin=k, target=k + 1,
        available_source_ids=[f"nv-s{s:02d}-w{j:02d}" for j in range(k + 1)],
        linear_source_ids=[f"nv-s{s:02d}-w{k - 1:02d}", f"nv-s{s:02d}-w{k:02d}"],
        persist_source_id=f"nv-s{s:02d}-w{k:02d}", target_source_id=f"nv-s{s:02d}-w{k + 1:02d}")
        for s in range(1, 5) for k in (1, 2, 3)]


def prediction_contract():
    return dict(arms=[
        dict(arm="LINEAR_TWO_STATE", functional_fields=["half_profile_digest", "previous_values", "last_values"],
             formula="d[i]=last[i]-previous[i];prediction[i]=last[i]+d[i]"),
        dict(arm="PERSIST_LAST", functional_fields=["half_profile_digest", "last_values"],
             formula="prediction[i]=bitcopy(last[i])")],
        error_formula="error[i]=abs(prediction[i]-target[i]);MAE=sum(error[i] for i=0..47)/48",
        gain_formula="gain=MAE_PERSIST_LAST-MAE_LINEAR_TWO_STATE",
        arithmetic="binary64; subtraction before addition; Python builtin sum in ascending original index order",
        indices=list(range(48)), finite_prediction_domain=[-1, 2], clipping=False, tolerance=False,
        forbidden_functional_fields=["source_id", "stream_id", "time", "ordinal", "target_ordinal", "recipe",
            "seed", "gain", "category", "evaluation", "future_values", "payload_sha256", "source_digest"],
        metadata_bindings_outside_predictor=True, future_analysis_after_prediction_binding=True,
        future_pcm_regeneration_after_prediction_binding=True, cross_stream_reuse=False,
        recursive_prediction=False, final_digest_alone_proves_chronology=False,
        standalone_materialization_authorized=False)


def budgets():
    return dict(windows=20,generated_samples=96000,generated_pcm_bytes=384000,max_live_payloads=1,max_live_pcm_bytes=19200,
        future_analyses=20,future_nj=20,future_values_per_scale=960,forecast_sites=12,
        predictions_per_implementation=24,linear_subtractions_per_implementation=576,
        linear_additions_per_implementation=576,persist_copies_per_implementation=576,
        error_terms_per_implementation=1152,mae_sums_per_implementation=24,gains_per_implementation=12,
        both_error_terms=2304,both_mae_sums=48,offline_halvings=960,offline_prediction_subtractions=1152,
        offline_prediction_additions=1152,offline_error_terms=2304,offline_sums=48,offline_gains=24,
        outcome_classifications=12,strict_criteria=6,max_metadata_bytes=65536,max_output_bytes=2097152,
        max_verification_bytes=262144,max_evaluation_bytes=262144)


def execution_plan(sources, env, hashes, generator):
    require(type(sources) is list and len(sources) == 20, "SOURCE_COUNT_INVALID")
    for spec, row in zip(specs(), sources, strict=True):
        require(type(row) is dict and row == bind_source(spec, row.get("pcm_sha256")), "SOURCE_BINDING_INVALID")
    return sealed(dict(schema="s2nv.source-execution-plan.v1",contract_sha256=PINS[CONTRACT],sources=sources,
        source_order=[s.payload()["source_id"] for s in specs()], profiles=profile_binding(),environment=env,
        source_hashes=hashes,generator=generator,forecast_sites=forecast_sites(),prediction_contract=prediction_contract(),
        budgets=budgets(),receptor_execution_authorized=False,nj_execution_authorized=False,
        prediction_execution_authorized=False,error_execution_authorized=False,system_execution_authorized=False),"execution_digest")


def evaluation_plan(execution):
    return sealed(dict(schema="s2nv.evaluation-plan.v1",execution_digest=execution["execution_digest"],
        contract_sha256=PINS[CONTRACT], categories=dict(s01="CONTINUATION",s02="REVERSAL",
            s03="STANDSTILL_AFTER_RISE",s04="UNEXPECTED_GROUP_CHANGE"),
        criteria=[dict(check_id=f"o{k:02d}",site_id=f"p{k:02d}",left="MAE_LINEAR_TWO_STATE",
            operator="LT",right="MAE_PERSIST_LAST",role="PRIMARY") for k in (1,2,3)] +
            [dict(check_id=f"o{n:02d}",site_id=site,left="MAE_LINEAR_TWO_STATE",operator="GT",
                right="MAE_PERSIST_LAST",role="SEPARATE_STRESS") for n,site in ((4,"p05"),(5,"p08"),(6,"p11"))],
        reporting=dict(per_stream_denominator=3,per_site=["MAE_LINEAR_TWO_STATE","MAE_PERSIST_LAST","signed_gain","WIN_TIE_LOSS"],
            target_phases={"2":"COMMON_RISE","3":"FIRST_BRANCH","4":"FOLLOWUP"},
            losses_separate=True,pooled_gain_compensation=False,common_prefix_is_independent_replication=False),
        primary_requires_all_three=True,ties_pass=False,stress_does_not_replace_primary=True,
        generation_categories_are_not_recognized=True,learning_proven=False,source_identity_proven=False,
        no_source_selection=True,no_parameter_search=True),"evaluation_digest")


def prefix_groups():
    return [[f"nv-s{s:02d}-w{k:02d}" for s in range(1,5)] for k in (0,1,2)]


def watched():
    require(all(filehash(ROOT/p) == h for p,h in PINS.items()), "PIN_CHANGED")
    return {p:filehash(ROOT/p) for p in sorted(set(PINS)|set(OWN))}


def generator_identity():
    bindings = []
    for path,names in (("tools/_s2nu_private_source_binding.py",("prepare_groups","group_value")),
                       (OWN[0],("render","pcm_window"))):
        tree = ast.parse((ROOT/path).read_text(encoding="utf-8"))
        nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        require(len(nodes)==len(names),"GENERATOR_IDENTITY_INVALID")
        bindings.append(dict(path=path,file_sha256=filehash(ROOT/path),functions=list(names),
            ast_digest=digest(ast.dump(ast.Module(body=nodes,type_ignores=[]),include_attributes=False))))
    return dict(bindings=bindings,historical_entry_executed=False)


def qualification(hashes):
    q = json.loads((QUAL_DIR/"result.json").read_bytes())
    require(q.get("result_digest")==digest({k:v for k,v in q.items() if k!="result_digest"})
        and q.get("run_id")==QUAL_ID and q.get("status")=="S2NV_SOURCE_BINDING_QUALIFIED"
        and q.get("passed_tests")==16 and q.get("unittest_calls")==1 and q.get("exit_code")==0
        and q.get("hashes_before")==q.get("hashes_after")==hashes,"QUALIFICATION_INVALID")
    return q


def preseal_once(run_id):
    require(run_id==RUN_ID and MAIN_GATE is False,"RUN_BINDING_INVALID")
    out = ROOT/"reports/s2nv"/run_id
    out.mkdir(exist_ok=False)
    phase,sid,attempted,rows,before = "QUALIFICATION_BINDING",None,0,[],{}
    try:
        before = watched()
        qualification(before)
        phase = "ENVIRONMENT_BINDING"
        env,gen = environment(),generator_identity()
        publish(out/"preregistration.json",dict(run_id=run_id,hashes=before,environment=env,generator=gen,
            windows=[s.payload() for s in specs()],forecast_sites=forecast_sites(),prediction_contract=prediction_contract(),
            evaluation=evaluation_plan(dict(execution_digest="0"*64)),budgets=budgets(),prefix_groups=prefix_groups(),retry=False),65536)
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
        phase,sid = "PREFIX_BINDING",None
        lookup = {x["source_id"]:x for x in rows}
        for ids in prefix_groups():
            require(len({lookup[s]["pcm_sha256"] for s in ids})==1
                    and len({lookup[s]["source_digest"] for s in ids})==4,"PREFIX_BINDING_INVALID")
        execution = execution_plan(rows,env,before,gen)
        evaluation = evaluation_plan(execution)
        after = watched()
        require(before==after and environment()==env,"BINDINGS_CHANGED")
        phase = "PUBLICATION"
        ef = publish(out/"execution-plan.json",execution,65536)
        vf = publish(out/"evaluation-plan.json",evaluation,65536)
        seal = sealed(dict(schema="s2nv.source-seal.v1",run_id=run_id,status="S2NV_SOURCES_PRESEALED",
            execution_digest=execution["execution_digest"],evaluation_digest=evaluation["evaluation_digest"],
            execution_file_sha256=ef,evaluation_file_sha256=vf,hashes_before=before,hashes_after=after,
            qualification_file_sha256=filehash(QUAL_DIR/"result.json"),attempted_sources=attempted,completed_sources=len(rows),
            generated_pcm_bytes=384000,max_live_payloads=1,raw_payloads_persisted=0,prefix_groups=prefix_groups(),
            collisions=common.collision_groups(rows),receptor_calls=0,nj_calls=0,prediction_calls=0,error_calls=0,
            memory_calls=0,field_calls=0,context_calls=0,runtime_calls=0,main_gate_after=MAIN_GATE),"seal_digest")
        publish(out/"seal.json",seal,65536)
    except Exception as exc:
        publish(out/"failure.json",sealed(dict(run_id=run_id,status="NOT_EVALUABLE",phase=phase,source_id=sid,
            attempted_sources=attempted,completed_sources=len(rows),error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),hashes_before=before,retry=False,main_gate_after=False),"failure_digest"),65536)
    return out
