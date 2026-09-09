"""Receptor-free NX preseal; prediction formulae are metadata, not executable."""
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
QUAL_ID = "s2nx-source-binding-qualification-20260909-01"
RUN_ID = "s2nx-source-preseal-20260909-01"
QUAL_DIR = ROOT / "reports/s2nx" / QUAL_ID
CONTRACT = "docs/S2NX_STATISCHER_PLAN_GEKREUZTE_LERNHISTORIEN.md"
PINS = {
    "tools/_s2nw_private_source_binding.py": "84687bf236bf383772ceca6791019d8de64e3fd6598e2557b27ff59ae36fe9e1",
    CONTRACT: "e9c156a77f5e22ca2a5765179cf9093b6d7e5c10a38a349c7399a09c0c8fb496",
    "tools/_s2nu_private_source_binding.py": "8e0fa79f3ce66ce4228f46a52252de5d207c6cee29fefc42f957aa41dc56bce6",
    "tools/_s2np_private_source_binding.py": "004ea7c8841e5f0b68fe9191604b0a0a7337ac568af2205dca900dd2ae874b12",
    "reports/s2nd/seal_inventory.py": "9f72d2a9fc9676235cf69b23ea690d25f0a782222c54393ecf5b44107f0ce91c",
    "mcm_field_organism/log_spectral_receptor.py": "26a6bd8f2d190db60c75ad29f275b3bd8b09b6d26d4ad54e4396176c4a36d2b0",
    "tools/_s2nj_private_auditory_output_projection.py": "e052cc76cf4c9678e11673d95390dea21634bba8082187567a760faaaf4904e5",
}
OWN = ("tools/_s2nx_private_source_binding.py", "tools/_s2nx_private_preseal_verification.py",
       "tests/test_s2nx_private_source_binding.py", "reports/s2nx/qualify_once.py",
       "reports/s2nx/preseal_once.py", "reports/s2nx/QUALIFIKATIONSBINDUNG.md")
MAX_METADATA_BYTES = 65536
MAX_OUTPUT_BYTES = 2097152
GROUPS = (((610, 1830, 5490), "s2nx-pcm-001"), ((790, 2370, 7110), "s2nx-pcm-002"),
          ((970, 2910, 8730), "s2nx-pcm-003"))
# Literal streams: two independent training histories, then four test streams.
ROWS = (((0,128),(0,384),(0,448),(0,464),(0,468),(0,469)),
        ((0,128),(0,384),(0,576),(0,720),(0,828),(0,909)),
        ((1,192),(1,320),(1,352),(1,360),(1,362)),
        ((1,192),(1,320),(1,416),(1,488),(1,542)),
        ((1,192),(1,320),(1,352),(1,320),(1,312)),
        ((1,192),(1,320),(1,416),(2,416),(2,416)))


class S2NXError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NXError(code)


def native_index(start):
    require(type(start) is int and start >= 0 and start % 480 == 0, "NATIVE_TIME_INVALID")
    return start // 480


@dataclass(frozen=True, slots=True)
class WindowSpec:
    stream: int
    window: int

    def __post_init__(self):
        require(type(self.stream) is int and 0 <= self.stream <= 5
                and type(self.window) is int and 0 <= self.window < (6 if self.stream < 2 else 5), "WINDOW_SPEC_INVALID")

    def recipe(self):
        group, numerator = ROWS[self.stream][self.window]
        frequencies, seed = GROUPS[group]
        return dict(schema="s2nx.pcm-window-recipe.v1", sample_rate=48000, sample_count=4800,
            group=dict(seed=seed, partials=[dict(frequency_ratio=[f, 1], amplitude_ratio=[a, 20])
                for f, a in zip(frequencies, (4, 2, 1), strict=True)]),
            gain_ratio=[numerator, 1024], synthesis_time="float(j)/48000.0; j=0..4799",
            rounding="binary64-group-sum-then-gain-then-single-f32le")

    def payload(self):
        n = self.stream*6+self.window if self.stream < 2 else 12+(self.stream-2)*5+self.window
        stream_id = f"l{self.stream+1:02d}" if self.stream < 2 else f"s{self.stream-1:02d}"
        start = n * 4800
        recipe = self.recipe()
        return dict(source_id=f"nx-{stream_id}-w{self.window:02d}",
            ordinal=n + 1, stream_id=stream_id, window_ordinal=self.window,
            format="PCM_F32LE", channels=1, clock_id="audio.sample",
            window_start_sample=start, window_end_sample=start + 4800,
            nj_snapshot_index=native_index(start), pcm_byte_count=19200,
            recipe=recipe, recipe_digest=digest(recipe))


def specs():
    return tuple(WindowSpec(s, k) for s in range(6) for k in range(6 if s < 2 else 5))



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
            and all(type(x) is int for x in gain_ratio) and gain_ratio[1] == 1024
            and 0 <= gain_ratio[0] <= 1024, "GAIN_FORM_INVALID")
    gain = float(gain_ratio[0]) / 1024.0
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
    sites = []
    for s in range(6):
        training = s < 2
        sid = f"l{s+1:02d}" if training else f"s{s-1:02d}"
        for origin in range(1,5 if training else 4):
            sites.append(dict(site_id=f"t{s*4+origin:02d}" if training else f"p{(s-2)*3+origin:02d}",
                stream_id=sid,origin=origin,target=origin+1,phase="TRAIN" if training else "FROZEN",
                available_source_ids=[f"nx-{sid}-w{j:02d}" for j in range(origin+1)],
                delta_source_ids=[f"nx-{sid}-w{origin-1:02d}",f"nx-{sid}-w{origin:02d}"],
                persist_source_id=f"nx-{sid}-w{origin:02d}",target_source_id=f"nx-{sid}-w{origin+1:02d}",
                active_histories=[f"H{s+1}"] if training else ["H1","H2"],
                update_after_target=training))
    return sites

def learning_schedule():
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

def prediction_contract():
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

def budgets():
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

def execution_plan(sources, env, hashes, generator):
    require(type(sources) is list and len(sources) == 32, "SOURCE_COUNT_INVALID")
    for spec, row in zip(specs(), sources, strict=True):
        require(type(row) is dict and row == bind_source(spec, row.get("pcm_sha256")), "SOURCE_BINDING_INVALID")
    return sealed(dict(schema="s2nx.source-execution-plan.v1",contract_sha256=PINS[CONTRACT],sources=sources,
        source_order=[s.payload()["source_id"] for s in specs()], profiles=profile_binding(),environment=env,
        source_hashes=hashes,generator=generator,forecast_sites=forecast_sites(),prediction_contract=prediction_contract(),
        learning_schedule=learning_schedule(),budgets=budgets(),receptor_execution_authorized=False,nj_execution_authorized=False,
        prediction_execution_authorized=False,learning_execution_authorized=False,error_execution_authorized=False,system_execution_authorized=False),"execution_digest")


def evaluation_plan(execution):
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

def prefix_groups():
    return [[f"nx-l{s:02d}-w{k:02d}" for s in (1,2)] for k in (0,1)] + [
        [f"nx-s{s:02d}-w{k:02d}" for s in (1,2,3,4)] for k in (0,1)] + [
        ["nx-s01-w02","nx-s03-w02"],["nx-s02-w02","nx-s04-w02"]]

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
        and q.get("run_id")==QUAL_ID and q.get("status")=="S2NX_SOURCE_BINDING_QUALIFIED"
        and q.get("passed_tests")==24 and q.get("unittest_calls")==1 and q.get("exit_code")==0
        and q.get("hashes_before")==q.get("hashes_after")==hashes,"QUALIFICATION_INVALID")
    return q


def preseal_once(run_id):
    require(run_id==RUN_ID and MAIN_GATE is False,"RUN_BINDING_INVALID")
    out = ROOT/"reports/s2nx"/run_id
    out.mkdir(exist_ok=False)
    phase,sid,attempted,rows,before = "QUALIFICATION_BINDING",None,0,[],{}
    try:
        before = watched()
        qualification(before)
        phase = "ENVIRONMENT_BINDING"
        env,gen = environment(),generator_identity()
        publish(out/"preregistration.json",dict(run_id=run_id,hashes=before,environment=env,generator=gen,
            windows=[s.payload() for s in specs()],forecast_sites=forecast_sites(),prediction_contract=prediction_contract(),learning_schedule=learning_schedule(),
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
                    and len({lookup[s]["source_digest"] for s in ids})==len(ids),"PREFIX_BINDING_INVALID")
        execution = execution_plan(rows,env,before,gen)
        evaluation = evaluation_plan(execution)
        after = watched()
        require(before==after and environment()==env,"BINDINGS_CHANGED")
        phase = "PUBLICATION"
        ef = publish(out/"execution-plan.json",execution,65536)
        vf = publish(out/"evaluation-plan.json",evaluation,65536)
        seal = sealed(dict(schema="s2nx.source-seal.v1",run_id=run_id,status="S2NX_SOURCES_PRESEALED",
            execution_digest=execution["execution_digest"],evaluation_digest=evaluation["evaluation_digest"],
            execution_file_sha256=ef,evaluation_file_sha256=vf,hashes_before=before,hashes_after=after,
            qualification_file_sha256=filehash(QUAL_DIR/"result.json"),attempted_sources=attempted,completed_sources=len(rows),
            generated_pcm_bytes=614400,max_live_payloads=1,raw_payloads_persisted=0,prefix_groups=prefix_groups(),
            collisions=common.collision_groups(rows),receptor_calls=0,nj_calls=0,prediction_calls=0,learning_calls=0,error_calls=0,
            memory_calls=0,field_calls=0,context_calls=0,runtime_calls=0,main_gate_after=MAIN_GATE),"seal_digest")
        publish(out/"seal.json",seal,65536)
    except Exception as exc:
        publish(out/"failure.json",sealed(dict(run_id=run_id,status="NOT_EVALUABLE",phase=phase,source_id=sid,
            attempted_sources=attempted,completed_sources=len(rows),error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),hashes_before=before,retry=False,main_gate_after=False),"failure_digest"),65536)
    return out
