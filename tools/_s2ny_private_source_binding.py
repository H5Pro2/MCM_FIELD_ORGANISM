"""Receptor-free NY source and historical freeze binding; formulae are metadata."""
import ast
from dataclasses import dataclass
import hashlib
import json
import math

from tools import _s2nx_private_source_binding as pure

common = pure.common
ROOT = pure.ROOT
canonical, digest, sealed = pure.canonical, pure.digest, pure.sealed
filehash, publish = pure.filehash, pure.publish
environment, profile_binding = pure.environment, pure.profile_binding
prepare_groups, render = pure.prepare_groups, pure.render
MAIN_GATE = False
QUAL_ID = "s2ny-source-binding-qualification-20260909-01"
RUN_ID = "s2ny-source-preseal-20260909-01"
QUAL_DIR = ROOT / "reports/s2ny" / QUAL_ID
CONTRACT = "docs/S2NY_STATISCHER_PLAN_PRAEFIXGEBUNDENE_ANWENDBARKEIT.md"
NX_DIR = "reports/s2nx/s2nx-crossed-learning-20260909-01"
NX_RECORD = "c8b478c00ce4a83ecd7e8be138a8ba0aada0c52687a4845c7bc086272d71afd4"
NX_PROOF = "4fe83068ab7382a60730f6dfe987fca271c8d64bd98f8bdfa845d9dc0ffabed9"
FREEZE_DIGESTS = (
    "e2ac7055d38dfbda06dbd0073506df8251e4b8a7fd997e6253f78e3077483e45",
    "3ce3c6471d5bd71910cd59ca95e39d7e95de05822ee6a82b6e8236138f190205")
PINS = {**pure.PINS,
    CONTRACT: "503999db6660471221c48ed7e7a0691b8824bb62f628dfb08a4b3325a7de0fac",
    "tools/_s2nx_private_source_binding.py": "d5b16c7e8f2a997f63baaf500f53e96c930613e7f653f60ce6b10de97dc7aab3",
    NX_DIR+"/result.json": "c8a74fdf39fb64002d2c1d2b60f7e2618edb596e800d6e7d606637e0017ba48c",
    NX_DIR+"/verification.json": "d481054e20c5a7fe342bb145d16da384c447cf16224615c006714337a372ecf5"}
OWN = ("tools/_s2ny_private_source_binding.py", "tools/_s2ny_private_preseal_verification.py",
       "tests/test_s2ny_private_source_binding.py", "reports/s2ny/qualify_once.py",
       "reports/s2ny/preseal_once.py", "reports/s2ny/QUALIFIKATIONSBINDUNG.md")
GROUPS = (((670, 2010, 6030), "s2ny-pcm-001"), ((890, 2670, 8010), "s2ny-pcm-002"))
ROWS = (((0,128),(0,320),(0,368),(0,380),(0,383)),
        ((0,128),(0,320),(0,464),(0,572),(0,653)),
        ((0,128),(0,192),(0,320),(0,576),(0,960)),
        ((0,320),(0,320),(0,320),(0,320),(0,320)),
        ((0,128),(0,320),(0,368),(0,320),(0,308)),
        ((0,128),(0,320),(0,464),(1,464),(1,464)))
FORBIDDEN_CALLS = ("receptor_calls", "nj_calls", "recommendation_calls", "local_calls",
    "prediction_calls", "learning_calls", "error_calls", "memory_calls", "field_calls", "context_calls", "runtime_calls")


class S2NYError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NYError(code)


def check(obj, key):
    require(type(obj) is dict and obj.get(key) == digest({k:v for k,v in obj.items() if k != key}), "SEALED_DIGEST_INVALID")


def sha(value):
    return type(value) is str and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def native_index(start):
    require(type(start) is int and start >= 0 and start % 480 == 0, "NATIVE_TIME_INVALID")
    return start // 480


@dataclass(frozen=True, slots=True)
class WindowSpec:
    stream: int
    window: int

    def __post_init__(self):
        require(type(self.stream) is int and 0 <= self.stream < 6 and
                type(self.window) is int and 0 <= self.window < 5, "WINDOW_SPEC_INVALID")

    def recipe(self):
        group, numerator = ROWS[self.stream][self.window]
        frequencies, seed = GROUPS[group]
        return dict(schema="s2ny.pcm-window-recipe.v1", sample_rate=48000, sample_count=4800,
            group=dict(seed=seed, partials=[dict(frequency_ratio=[f,1], amplitude_ratio=[a,20])
                for f,a in zip(frequencies,(4,2,1),strict=True)]), gain_ratio=[numerator,1024],
            synthesis_time="float(j)/48000.0; j=0..4799", rounding="binary64-group-sum-then-gain-then-single-f32le")

    def payload(self):
        n = self.stream*5+self.window
        start, recipe = n*4800, self.recipe()
        return dict(source_id=f"ny-s{self.stream+1:02d}-w{self.window:02d}", ordinal=n+1,
            stream_id=f"s{self.stream+1:02d}", window_ordinal=self.window, format="PCM_F32LE",
            channels=1, clock_id="audio.sample", window_start_sample=start, window_end_sample=start+4800,
            nj_snapshot_index=native_index(start), pcm_byte_count=19200, recipe=recipe, recipe_digest=digest(recipe))


def specs():
    return tuple(WindowSpec(s,k) for s in range(6) for k in range(5))


def bind_source(spec, payload_hash):
    require(type(spec) is WindowSpec, "WINDOW_SPEC_INVALID")
    spec.__post_init__()
    require(sha(payload_hash), "PAYLOAD_HASH_INVALID")
    return sealed({**spec.payload(), "pcm_sha256":payload_hash}, "source_digest")


def pcm_window(spec):
    require(type(spec) is WindowSpec, "WINDOW_SPEC_INVALID")
    spec.__post_init__()
    recipe = spec.recipe()
    return render(prepare_groups([recipe["group"]])[0], recipe["gain_ratio"], tuple(range(4800)))


def read_canonical(path, limit):
    require(path.stat().st_size <= limit, "METADATA_SIZE_INVALID")
    data = path.read_bytes()
    obj = json.loads(data)
    require(data == canonical(obj), "CANONICAL_FORM_INVALID")
    return obj


def validate_nx_freezes(record, proof, file_digest, expected_record, expected_proof, expected_states):
    """Validate provenance and state form only; do not replay historical arithmetic."""
    check(record,"record_digest")
    check(proof,"verification_digest")
    require(record["record_digest"] == expected_record and proof["verification_digest"] == expected_proof
        and proof.get("record_digest") == expected_record, "NX_ROOT_BINDING_INVALID")
    require(record.get("status") == "RECORDING_COMPLETE" and proof.get("status") == "S2NX_LEARNING_VERIFIED"
        and proof.get("read_only") is True and proof.get("baseline_equal") is True
        and proof.get("verification_calls") == 1 and record.get("main_gate_after") is False,
        "NX_COMPLETION_INVALID")
    require(proof.get("file_sha256_before") == proof.get("file_sha256_after") == file_digest
        and proof.get("execution_digest") == record.get("execution_digest"), "NX_FILE_BINDING_INVALID")
    require(record.get("profiles") == profile_binding(), "NX_PROFILE_INVALID")
    learning = record.get("learning")
    require(type(learning) is dict and type(learning.get("frozen")) is dict
        and type(learning.get("closed")) is dict and set(learning["frozen"]) == set(learning["closed"]) == {"H1","H2"},
        "NX_FREEZE_FORM_INVALID")
    entries = []
    for name, expected in zip(("H1","H2"),expected_states,strict=True):
        frozen, closed = learning["frozen"][name], learning["closed"][name]
        require(type(frozen) is dict and set(frozen) == {"binding","states"}
            and type(closed) is dict and set(closed) == {"binding","states"}, "NX_FREEZE_FORM_INVALID")
        binding, states = frozen["binding"], frozen["states"]
        require(type(binding) is dict and set(binding) == {"history","history_digest","source_digests"}
            and binding["history"] == name and sha(binding["history_digest"])
            and type(binding["source_digests"]) is list and len(binding["source_digests"]) == 6
            and all(sha(x) for x in binding["source_digests"]) and closed["binding"] == binding,
            "NX_HISTORY_BINDING_INVALID")
        require(type(states) is dict and set(states) == {"primary","direct"}
            and canonical(states["primary"]) == canonical(states["direct"])
            and type(closed["states"]) is dict and set(closed["states"]) == {"primary","direct"}, "NX_STATE_PAIR_INVALID")
        state = states["primary"]
        check(state,"state_digest")
        require(set(state) == {"schema","profile_digest","n","Sxx","Sxy","alpha","phase",
            "predecessor","observation_digest","state_digest"}, "NX_STATE_FORM_INVALID")
        require(state["schema"] == "s2nw.learning-state.v1" and state["phase"] == "FROZEN"
            and type(state["n"]) is int and state["n"] == 4
            and state["profile_digest"] == record["profiles"]["half_profile_digest"]
            and sha(state["predecessor"]) and sha(state["observation_digest"])
            and all(type(state[k]) is float and math.isfinite(state[k]) for k in ("Sxx","Sxy","alpha"))
            and 0 <= state["Sxx"] <= 192 and abs(state["Sxy"]) <= 192, "NX_STATE_FORM_INVALID")
        require(state["state_digest"] == expected, "NX_STATE_BINDING_INVALID")
        require(len(canonical(state)) <= 4096, "NX_STATE_SIZE_INVALID")
        for arm in ("primary","direct"):
            c = closed["states"][arm]
            check(c,"state_digest")
            require(c.get("phase") == "CLOSED" and c.get("predecessor") == expected
                and {k:v for k,v in c.items() if k not in ("phase","predecessor","state_digest")}
                    == {k:v for k,v in state.items() if k not in ("phase","predecessor","state_digest")},
                "NX_CLOSED_BINDING_INVALID")
        entries.append(dict(history_id=name, binding=binding, frozen_payload=state,
            closed_state_digest=closed["states"]["primary"]["state_digest"], alpha_binary64_hex=state["alpha"].hex()))
    return sealed(dict(schema="s2ny.nx-freeze-import.v1", nx_record_digest=expected_record,
        nx_verification_digest=expected_proof, nx_record_file_sha256=file_digest,
        nx_execution_digest=record["execution_digest"], profiles=record["profiles"], histories=entries,
        historical_arithmetic_replayed=False, owners_reopened=False, read_only=True),"freeze_import_digest")


def load_freezes():
    paths = [ROOT/NX_DIR/n for n in ("result.json","verification.json")]
    require(all(filehash(p) == PINS[p.relative_to(ROOT).as_posix()] for p in paths), "NX_FILE_PIN_CHANGED")
    record, proof = [read_canonical(p,2097152 if p.name=="result.json" else 262144) for p in paths]
    return validate_nx_freezes(record,proof,PINS[NX_DIR+"/result.json"],NX_RECORD,NX_PROOF,FREEZE_DIGESTS)


def forecast_sites():
    result = []
    for s in range(1,7):
        for target in (2,3,4):
            n = (s-1)*3+target-1
            sid = f"s{s:02d}"
            result.append(dict(site_id=f"p{n:02d}",stream_id=sid,target=target,origin=target-1,
                available_source_ids=[f"ny-{sid}-w{k:02d}" for k in range(target)],
                target_source_id=f"ny-{sid}-w{target:02d}",
                delta_source_ids=[f"ny-{sid}-w{k:02d}" for k in (target-2,target-1)],
                local_source_ids=[f"ny-{sid}-w{k:02d}" for k in range(target-3,target)] if target>2 else [],
                previous_error_site=f"p{n-1:02d}" if target>2 else None,
                histories=["H1","H2"],local_available=target>2,updates_allowed=False))
    return result


def prediction_contract():
    return dict(history_formula="d=last-previous;h=last+(alpha*d)",persist_formula="bitcopy(last)",
        local_formula="xx=+0.0;xy=+0.0;for i=0..47:x=z[k-2][i]-z[k-3][i];y=z[k-1][i]-z[k-2][i];xx=xx+(x*x);xy=xy+(x*y);beta=xy/xx if xx>0.0 else +0.0;h=z[k-1]+(beta*(z[k-1]-z[k-2]))",
        error_formula="sum(abs(h[i]-target[i]) for i=0..47)/48",
        recommendation_formula="missing->ABSTAIN_INSUFFICIENT_PREFIX;E1<E2->H1;E2<E1->H2;else->ABSTAIN_TIE",
        gain_formula="MAE_control-MAE_recommendation",indices=list(range(48)),
        arithmetic="binary64-separate-operations;python-sum-ascending-indices;no-FMA",
        predictor_fields=["profile_digest","alpha","previous_values","last_values"],
        local_fields=["profile_digest","three_available_vectors"],recommendation_fields=["E1","E2"],
        excluded_fields=["recipe","source_id","time","ordinal","seed","category","expected_history","future_values"],
        prior_errors_bound_to_previous_site=True,predictions_and_recommendation_before_target_generation=True,
        stored_histories_frozen=True,local_reset_each_site=True,prefix_reset_each_stream=True,
        past_errors_recomputed=False,predicted_values_as_prefix=False,clipping=False,tolerance=False,
        fallback=False,posthoc_best_arm=False,standalone_materialization_authorized=False,
        chronology_qualified=False,preseal_is_not_prediction_execution=True)


def budgets():
    return dict(windows=30,generated_samples=144000,generated_pcm_bytes=576000,max_live_payloads=1,max_live_pcm_bytes=19200,
        future_analyses=30,future_nj=30,future_values_per_scale=1440,forecast_sites=18,local_sites=12,strict_criteria=20,
        predictions_per_implementation=66,prediction_subtractions_per_implementation=2304,
        prediction_multiplications_per_implementation=2304,prediction_additions_per_implementation=2304,
        persist_copies_per_implementation=864,local_fits_per_implementation=12,local_divisions_per_implementation=12,
        local_differences_per_implementation=1152,local_products_per_implementation=1152,local_additions_per_implementation=1152,
        error_terms_per_implementation=3168,mae_sums_per_implementation=66,recommendations_per_implementation=18,
        gains_per_implementation=96,implementations=2,offline_halvings=1440,
        offline_prediction_subtractions=4608,offline_prediction_multiplications=4608,offline_prediction_additions=4608,
        offline_persist_copies=1728,offline_local_differences=2304,offline_local_products=2304,offline_local_additions=2304,
        offline_local_divisions=24,offline_error_terms=6336,offline_sums=132,offline_recommendations=36,offline_gains=192,
        outcome_classifications=96,recommendation_outcomes=18,max_freeze_payload_bytes=4096,max_prefix_vectors=3,
        max_metadata_bytes=65536,max_output_bytes=2097152,max_verification_bytes=262144,max_evaluation_bytes=262144)


def execution_plan(sources, env, hashes, generator, freezes):
    require(type(sources) is list and len(sources)==30,"SOURCE_COUNT_INVALID")
    for spec,row in zip(specs(),sources,strict=True):
        require(type(row) is dict and row == bind_source(spec,row.get("pcm_sha256")),"SOURCE_BINDING_INVALID")
    check(freezes,"freeze_import_digest")
    return sealed(dict(schema="s2ny.source-execution-plan.v1",contract_sha256=PINS[CONTRACT],sources=sources,
        source_order=[s.payload()["source_id"] for s in specs()],environment=env,profiles=profile_binding(),
        source_hashes=hashes,generator=generator,freeze_import=freezes,forecast_sites=forecast_sites(),
        prediction_contract=prediction_contract(),budgets=budgets(),
        authorizations={name:False for name in FORBIDDEN_CALLS}),"execution_digest")


def evaluation_plan(execution):
    criteria = []
    for prefix,condition in (("R","recommendation_present_and_NEXT_BEST"),
            ("L","recommendation_present_and_MAE_LT_LOCAL"),("P","recommendation_present_and_MAE_LT_PERSIST")):
        for n,site in enumerate(("p02","p03","p05","p06"),1):
            criteria.append(dict(check_id=f"{prefix}{n:02d}",site_id=site,condition=condition))
    for i,site in enumerate(("p14","p15","p17","p18")):
        for j,control in enumerate(("PERSIST","LOCAL"),1):
            criteria.append(dict(check_id=f"W{i*2+j:02d}",site_id=site,
                condition=f"recommendation_present_and_MAE_GT_{control}"))
    return sealed(dict(schema="s2ny.evaluation-plan.v1",contract_sha256=PINS[CONTRACT],execution_digest=execution["execution_digest"],
        categories=dict(s01="CONTINUATION_H1",s02="CONTINUATION_H2",s03="ACCELERATED_UNMATCHED",
            s04="STILL",s05="REVERSAL",s06="GROUP_CHANGE"),expected_history=dict(s01="H1",s02="H2"),criteria=criteria,
        reporting=dict(total_sites=18,sufficient_prefix_sites=12,per_stream_sites=3,per_stream_local_sites=2,
            no_recommendation_mae=None,empty_emitted_denominator="NUTZEN_NICHT_GEPRUEFT",
            recommendation_outcomes=["NEXT_BEST","NEXT_WRONG","NEXT_TIE","ABSTAIN_INSUFFICIENT_PREFIX","ABSTAIN_TIE"],
            absolute_mae_and_gain_required=True,binary64_advantage_is_not_general_robustness=True,
            wins_ties_losses_separate=True,first_switch_and_followup_separate=True,gain_compensation=False,
            target_phases={"2":"INITIAL_TARGET","3":"FIRST_BRANCH","4":"FOLLOWUP"},
            all_control_mae_reported=True,common_prefix_is_independent_replication=False),
        separate_blocks=["R","L","P","W"],R_requires=4,L_requires=4,P_requires=4,W_loss_predictions=8,
        W_guaranteed=False,W_start_gate=False,ties_pass=False,no_functional_start_gate=True,
        descriptive_streams=["s03","s04"],descriptive_results_replace_R_L=False,
        recommendation_is_identity=False,ME_MI_unblocked=False),"evaluation_digest")


def watched():
    require(all(filehash(ROOT/p)==h for p,h in PINS.items()),"PIN_CHANGED")
    return {p:filehash(ROOT/p) for p in sorted(set(PINS)|set(OWN))}


def generator_identity():
    bindings = []
    for path,names in (("tools/_s2nu_private_source_binding.py",("prepare_groups","group_value")),
            ("tools/_s2nx_private_source_binding.py",("render",)),(OWN[0],("pcm_window",))):
        tree = ast.parse((ROOT/path).read_text(encoding="utf-8"))
        nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        require(len(nodes)==len(names),"GENERATOR_IDENTITY_INVALID")
        bindings.append(dict(path=path,file_sha256=filehash(ROOT/path),functions=list(names),
            ast_digest=digest(ast.dump(ast.Module(body=nodes,type_ignores=[]),include_attributes=False))))
    return dict(bindings=bindings,historical_entry_executed=False)


def qualification(hashes):
    q = read_canonical(QUAL_DIR/"result.json",65536)
    check(q,"result_digest")
    require(q.get("run_id")==QUAL_ID and q.get("status")=="S2NY_SOURCE_BINDING_QUALIFIED"
        and q.get("passed_tests")==24 and q.get("unittest_calls")==1 and q.get("exit_code")==0
        and q.get("hashes_before")==q.get("hashes_after")==hashes,"QUALIFICATION_INVALID")
    return q


def preseal_once(run_id):
    require(run_id==RUN_ID and MAIN_GATE is False,"RUN_BINDING_INVALID")
    out = ROOT/"reports/s2ny"/run_id
    out.mkdir(exist_ok=False)
    phase,sid,attempted,rows,before = "QUALIFICATION_BINDING",None,0,[],{}
    try:
        before = watched()
        qualification(before)
        phase = "NX_FREEZE_BINDING"
        freezes = load_freezes()
        phase = "ENVIRONMENT_BINDING"
        env,gen = environment(),generator_identity()
        publish(out/"preregistration.json",dict(run_id=run_id,hashes=before,environment=env,generator=gen,
            windows=[s.payload() for s in specs()],freeze_import=freezes,forecast_sites=forecast_sites(),
            prediction_contract=prediction_contract(),evaluation=evaluation_plan(dict(execution_digest="0"*64)),
            budgets=budgets(),retry=False),65536)
        for spec in specs():
            phase,sid = "PCM_GENERATION",spec.payload()["source_id"]
            attempted += 1
            payload = pcm_window(spec)
            try:
                require(type(payload) is bytearray and len(payload)==19200,"PAYLOAD_FORM_INVALID")
                payload_hash = hashlib.sha256(payload).hexdigest()
            finally:
                del payload
            rows.append(bind_source(spec,payload_hash))
        phase,sid = "PLAN_BINDING",None
        execution = execution_plan(rows,env,before,gen,freezes)
        evaluation = evaluation_plan(execution)
        after = watched()
        require(before==after and environment()==env,"BINDINGS_CHANGED")
        phase = "PUBLICATION"
        ef = publish(out/"execution-plan.json",execution,65536)
        vf = publish(out/"evaluation-plan.json",evaluation,65536)
        seal = sealed(dict(schema="s2ny.source-seal.v1",run_id=run_id,status="S2NY_SOURCES_PRESEALED",
            execution_digest=execution["execution_digest"],evaluation_digest=evaluation["evaluation_digest"],
            execution_file_sha256=ef,evaluation_file_sha256=vf,hashes_before=before,hashes_after=after,
            qualification_file_sha256=filehash(QUAL_DIR/"result.json"),freeze_import_digest=freezes["freeze_import_digest"],
            attempted_sources=attempted,completed_sources=len(rows),generated_pcm_bytes=576000,max_live_payloads=1,
            raw_payloads_persisted=0,collisions=common.collision_groups(rows),
            **{name:0 for name in FORBIDDEN_CALLS},main_gate_after=MAIN_GATE),"seal_digest")
        publish(out/"seal.json",seal,65536)
    except Exception as exc:
        publish(out/"failure.json",sealed(dict(run_id=run_id,status="NOT_EVALUABLE",phase=phase,source_id=sid,
            attempted_sources=attempted,completed_sources=len(rows),error_class=type(exc).__name__,
            code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"),hashes_before=before,retry=False,main_gate_after=False),"failure_digest"),65536)
    return out
