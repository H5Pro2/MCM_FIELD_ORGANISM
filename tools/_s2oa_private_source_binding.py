"""Source-only OA binding. Historical generators are extracted, not imported."""
import ast
import hashlib
import json
import re
import numpy as np
from tools import _s2np_private_source_binding as common

ROOT = common.ROOT
canonical, digest, filehash, publish, sealed = common.canonical, common.digest, common.filehash, common.publish, common.sealed
CONTRACT = "docs/S2OA_STATISCHER_FUNKTIONSPLAN_FORTGESETZTER_MCM_BETRIEB.md"
JX = "tools/_s2jx_default_live_memory_fixtures.py"
NP_DIR = "reports/s2np/s2np-source-preseal-20260907-01/"
QUAL_ID = "s2oa-source-binding-qualification-20260909-01"
QUAL_DIR = ROOT / "reports/s2oa" / QUAL_ID
MAIN_GATE = False
MAX_METADATA_BYTES, MAX_OUTPUT_BYTES = 262144, 4194304
TEST_COUNT = 18
PINS = {**{p:h for p,h in common.PINS.items() if p != common.CONTRACT},
    CONTRACT:"bb87f2a89621d2df6ee248d8b917e59db3758ecdeede2a9ac154fdde93a6a69d",
    JX:"5313888d81b946c7ca87f6cf140a04d7810fdb0ecd1eaa0650e9fc1bb1854936",
    "tools/_s2np_private_source_binding.py":"004ea7c8841e5f0b68fe9191604b0a0a7337ac568af2205dca900dd2ae874b12",
    NP_DIR+"execution-plan.json":"3e7814f75d5c8d05b24290a04509d1d3eb85cb6aec2b1d3afa1d948b8b19b4f0",
    NP_DIR+"seal.json":"3812a12c6aea93a7c706cd5233eb7e171f8b68f46d89492a1c0e240a145fe828",
    "tools/_s2nn_private_half_runtime_binding.py":"41fafcaea48d9029fa2a6e84c0c5477e468761e59499e1f8bfdc952317afddc6",
    "tools/_s2jw_default_live_profile.py":"7173ba0b4913560e0f8ab02991808940fae76842042146bdaf945bd15d862f96"}
OWN = ("tools/_s2oa_private_source_binding.py", "tools/_s2oa_private_preseal_verification.py",
       "tests/test_s2oa_private_source_binding.py", "reports/s2oa/qualify_once.py",
       "reports/s2oa/preseal_once.py", "reports/s2oa/QUALIFIKATIONSBINDUNG.md")
AV, A, V = "COMPLETE_AV_PERCEPTION", "PARTIAL_AUDITORY_CUE", "PARTIAL_VISUAL_CUE"
ROWS = ((V,0),(AV,0),(A,None),(V,0),(AV,0),(AV,0),(AV,0),(A,None),
        (AV,2),(AV,2),(AV,2),(AV,2),(AV,3),(AV,3),(AV,3),(AV,3),
        (AV,4),(V,0),(AV,4),(AV,4),(AV,4),(AV,5),(V,5),(AV,5),
        (V,0),(AV,5),(AV,5),(V,5))
FIELD_CLOCK = "s2oa-continuous-field-clock"


class S2OABindingError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2OABindingError(code)


def root(value, key):
    require(type(value) is dict and value.get(key) == digest({k:v for k,v in value.items() if k != key}), "DIGEST_INVALID")


def watched():
    require(all(filehash(ROOT/p) == h for p,h in PINS.items()), "PIN_CHANGED")
    return {p:filehash(ROOT/p) for p in sorted(set(PINS)|set(OWN))}


def history():
    for p in (NP_DIR+"execution-plan.json", NP_DIR+"seal.json", JX):
        require(filehash(ROOT/p) == PINS[p], "HISTORICAL_SOURCE_CHANGED")
    ex = json.loads((ROOT/NP_DIR/"execution-plan.json").read_bytes())
    seal = json.loads((ROOT/NP_DIR/"seal.json").read_bytes())
    root(ex,"execution_digest"); root(seal,"seal_digest")
    require(seal["execution_digest"] == ex["execution_digest"], "HISTORICAL_ROOT_INVALID")
    pcm = next(s for s in ex["sources"] if s["source_id"] == "np-a02")
    root(pcm,"source_digest")
    require(pcm["recipe"] == common.source_specs()[1].recipe(), "HISTORICAL_RECIPE_INVALID")
    tree = ast.parse((ROOT/JX).read_text(encoding="utf-8"))
    values = next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id == "_ROWS" for t in n.targets))
    rgb = {r[1]:r[3] for r in ast.literal_eval(values)}
    return pcm, rgb, dict(np_execution_digest=ex["execution_digest"],np_seal_digest=seal["seal_digest"],
        np_source_digest=pcm["source_digest"],jx_file_sha256=PINS[JX])


def native_index(start):
    require(type(start) is int and start >= 0 and start % 480 == 0, "NATIVE_INDEX_INVALID")
    return start // 480


def events():
    result = []
    for g,(kind,o) in enumerate(ROWS):
        n = g+1
        audio = None if kind == V else dict(source_id=f"oa-e{n:02d}-audio",clock_id="audio.sample",
            start_tick=9600*g,end_tick=9600*g+4800,nj_snapshot_index=native_index(9600*g),
            common_window=[200000000*g,200000000*g+100000000])
        video = None if kind == A else dict(source_id=f"oa-e{n:02d}-visual",clock_id="video.frame",
            start_tick=6*g+2,end_tick=6*g+3,common_window=[(6*g+2)*1000000000//30,200000000*g+100000000])
        result.append(dict(event_id=f"e{n:02d}",ordinal=n,event_type=kind,
            field_clock_id=FIELD_CLOCK,field_window=[0 if g == 0 else 200000000*g-100000000,200000000*g+100000000],
            auditory=audio,visual=video))
    return result


def validate_events(rows):
    require(type(rows) is list and rows == events(), "EVENT_BINDING_INVALID")
    return rows


def specs():
    pcm, rgb, parent = history()
    result = []
    for e,(_,o) in zip(events(),ROWS,strict=True):
        for key in ("auditory","visual"):
            part = e[key]
            if part is None:
                continue
            audio, partial = key == "auditory", e["event_type"] == V
            recipe = pcm["recipe"] if audio else dict(algorithm="JX_GRID_RGB8_V1",ordinal=o,
                width=1920,height=1080,rows=8,columns=12,channels=3,
                visible_positions=list(range(32)) if partial else None)
            result.append(dict(source_id=part["source_id"],event_id=e["event_id"],event_ordinal=e["ordinal"],
                kind="PCM" if audio else "RGB",recipe=recipe,recipe_digest=digest(recipe),
                byte_count=19200 if audio else 6220800,time_binding=part,
                historical_recipe_id="np-a02" if audio else f"jx-visual-ordinal-{o}",
                historical_parent=parent if audio else dict(jx_file_sha256=PINS[JX],ordinal=o,base_payload_sha256=rgb[o]),
                historical_payload_sha256=pcm["pcm_sha256"] if audio else None if partial else rgb[o],
                transformation="NONE" if audio or not partial else "RGB_OCCLUSION_BEFORE_RECEPTOR_0_31"))
    return result


def bind_source(spec, sha):
    require(type(sha) is str and re.fullmatch(r"[0-9a-f]{64}",sha), "PAYLOAD_DIGEST_INVALID")
    require(spec in specs(), "SOURCE_BINDING_INVALID")
    expected = spec["historical_payload_sha256"]
    require(expected is None or sha == expected, "HISTORICAL_PAYLOAD_MISMATCH")
    return sealed({**spec,"payload_sha256":sha},"source_digest")


def generators():
    pcm, pidentity = common.pure_generator()
    require(filehash(ROOT/JX) == PINS[JX], "GENERATOR_CHANGED")
    tree = ast.parse((ROOT/JX).read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == "_visual_image"]
    require(len(nodes) == 1, "GENERATOR_SELECTION_INVALID")
    namespace = dict(np=np)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(ROOT/JX),"exec"),namespace)
    return pcm, namespace["_visual_image"], dict(pcm=pidentity,
        rgb=dict(path=JX,file_sha256=PINS[JX],function="_visual_image",ast_digest=digest(ast.dump(nodes[0],include_attributes=False))),
        occlusion="in-place channel-cell zeroing after JX before receptor",historical_entries_executed=False)


def occlude(image, visible):
    require(type(image) is np.ndarray and image.shape == (1080,1920,3) and image.dtype == np.uint8
            and image.flags.c_contiguous and image.flags.writeable, "RGB_FORM_INVALID")
    require(visible == list(range(32)), "MASK_BINDING_INVALID")
    for i in range(32,288):
        cell, channel = divmod(i,3)
        row,col = divmod(cell,12)
        image[row*135:(row+1)*135,col*160:(col+1)*160,channel] = 0
    return image


def environment():
    return {**common.environment(),"numpy_imported":True,"numpy_role":"RGB_GENERATION_ONLY"}


def profiles():
    return dict(audio=common.profile_binding(),visual=dict(width=1920,height=1080,rows=8,columns=12,channels=3,fps=30),
        coordinator_config_digest="55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e",
        audio_observed=list(range(24)),audio_complement=list(range(24,48)),visual_observed=list(range(32)),
        visual_complement=list(range(32,288)),a_audio_rule="ALL_BANDS_24",a_audio_threshold=0.1,
        slow_audio_rule="historical sum / 24",slow_audio_threshold=0.01,
        visual_rule="EXACT_KQ",fast_audio_threshold=0.1,fast_visual_threshold=0.2,
        ppb_audio_threshold=0.01,ppb_visual_threshold=0.01,fast_rank="max(2*d_audio,d_visual),2*d_audio+d_visual,slot_id")


def budgets():
    return dict(events=28,source_occurrences=48,pcm_payloads=22,rgb_payloads=26,
        generated_pcm_bytes=422400,generated_rgb_bytes=161740800,max_live_pcm_payloads=1,max_live_rgb_payloads=1,
        max_pcm_bytes=19200,max_rgb_bytes=6220800,metadata_bytes=MAX_METADATA_BYTES,total_bytes=MAX_OUTPUT_BYTES,
        future_formations=20,future_audio_analyses=22,future_nj=22,future_visual_analyses=26,
        future_scan_receipts=16,future_field_contacts=8544)


def execution_plan(sources,env,hashes,gen):
    expected = specs()
    require(type(sources) is list and len(sources) == 48, "SOURCE_COUNT_INVALID")
    for spec,row in zip(expected,sources,strict=True):
        require(row == bind_source(spec,row.get("payload_sha256")), "SOURCE_BINDING_INVALID")
    value = sealed(dict(schema="s2oa.source-execution-plan.v1",contract_sha256=PINS[CONTRACT],
        source_order=[s["source_id"] for s in expected],sources=sources,events=events(),profiles=profiles(),
        budgets=budgets(),environment=env,generators=gen,source_hashes=hashes,
        future_runtime_instances=1,reset_between_sections=False,receptor_execution_authorized=False,
        nj_execution_authorized=False,memory_execution_authorized=False,field_execution_authorized=False,
        runtime_execution_authorized=False),"execution_digest")
    require(len(canonical(value)) <= MAX_METADATA_BYTES, "METADATA_SIZE_EXCEEDED")
    return value


def evaluation_plan(ex):
    cases = ((1,"q01","visual",0,"NONE"),(3,"q02","auditory",None,"A_RECENT"),
        (4,"q03","visual",0,"A_RECENT"),(8,"q04","auditory",None,"INTERNAL_AMBIGUITY"),
        (18,"q05","visual",0,"B_STABLE"),(23,"q06","visual",5,"A_RECENT"),
        (25,"q07","visual",0,"NONE_AFTER_REPLACEMENT"),(28,"q08","visual",5,"INTERNAL_AMBIGUITY"))
    return sealed(dict(schema="s2oa.source-evaluation-plan.v1",execution_digest=ex["execution_digest"],
        contract_sha256=PINS[CONTRACT],cases=[dict(event_id=f"e{n:02d}",cue_id=q,modality=m,
            target_visual_ordinal=o,prediction=p) for n,q,m,o,p in cases],
        state_predictions=dict(fast_expiry_formations=[12,16,20],visual_slow_replacement_formation=18,
            visual_slow_replaced_slot_order=0,ppb_calls_per_modality=15,final_visual_supports=[3,3,3,3]),
        generation_from_actual_transactions=True,q05_not_current_evidence_for_q07=True,
        unexpected_valid_states_evaluable=True,abstentions_evaluable=True,
        auditory_slow_replacement_covered=False,general_continuous_operation_covered=False,
        functional_predictions_are_start_gates=False),"evaluation_digest")


def collisions(sources):
    groups = {}
    for s in sources:
        groups.setdefault((s["kind"],s["payload_sha256"]),[]).append(s["source_id"])
    return [dict(kind=k,payload_sha256=h,source_ids=ids) for (k,h),ids in sorted(groups.items()) if len(ids)>1]


def preseal_once(run_id):
    global MAIN_GATE
    require(MAIN_GATE and re.fullmatch(r"s2oa-source-preseal-\d{8}-\d{2}",run_id), "GATE_OR_ID_INVALID")
    out = ROOT/"reports/s2oa"/run_id
    out.mkdir(exist_ok=False)
    phase,sid,attempted,rows,before = "QUALIFICATION",None,0,[],{}
    try:
        before = watched()
        q = json.loads((QUAL_DIR/"result.json").read_bytes()); root(q,"result_digest")
        require(q["status"] == "S2OA_SOURCE_BINDING_QUALIFIED" and q["passed_tests"] == TEST_COUNT
            and q["hashes_before"] == q["hashes_after"] == before and q["unittest_calls"] == 1
            and q["exit_code"] == 0, "QUALIFICATION_REQUIRED")
        phase = "PREREGISTRATION"
        env = environment(); pcm,rgb,gen = generators()
        publish(out/"preregistration.json",dict(run_id=run_id,hashes=before,environment=env,generators=gen,
            specs=specs(),events=events(),profiles=profiles(),budgets=budgets(),retry=False,
            qualification_sha256=filehash(QUAL_DIR/"result.json")),MAX_METADATA_BYTES)
        for spec in specs():
            phase,sid = "PAYLOAD_GENERATION",spec["source_id"]
            attempted += 1
            payload = pcm(spec["recipe"]) if spec["kind"] == "PCM" else rgb(spec["recipe"]["ordinal"])
            try:
                phase = "PAYLOAD_FORM"
                if spec["kind"] == "RGB":
                    if spec["recipe"]["visible_positions"] is not None:
                        occlude(payload,spec["recipe"]["visible_positions"])
                    require(payload.shape == (1080,1920,3) and payload.dtype == np.uint8 and payload.flags.c_contiguous,"RGB_FORM_INVALID")
                    payload.flags.writeable = False
                else:
                    require(type(payload) is bytearray and len(payload) == 19200,"PCM_FORM_INVALID")
                view = memoryview(payload).cast("B")
                try:
                    require(view.nbytes == spec["byte_count"],"PAYLOAD_SIZE_INVALID")
                    sha = hashlib.sha256(view).hexdigest()
                finally:
                    view.release(); del view
            finally:
                del payload
            phase = "PAYLOAD_BINDING"
            rows.append(bind_source(spec,sha))
        phase,sid = "PLAN_PUBLICATION",None
        ex = execution_plan(rows,env,before,gen); ev = evaluation_plan(ex)
        require(before == watched() and env == environment(),"BINDINGS_CHANGED")
        eh = publish(out/"execution-plan.json",ex,MAX_METADATA_BYTES)
        vh = publish(out/"evaluation-plan.json",ev,MAX_METADATA_BYTES)
        z = sealed(dict(run_id=run_id,status="S2OA_SOURCES_PRESEALED",execution_digest=ex["execution_digest"],
            evaluation_digest=ev["evaluation_digest"],execution_file_sha256=eh,evaluation_file_sha256=vh,
            hashes_before=before,hashes_after=watched(),attempted_sources=attempted,completed_sources=len(rows),
            budgets=budgets(),collisions=collisions(rows),raw_payloads_persisted=0,
            receptor_calls=0,nj_calls=0,distance_calls=0,memory_calls=0,field_calls=0,runtime_calls=0,
            main_gate_after=False),"seal_digest")
        publish(out/"seal.json",z,MAX_METADATA_BYTES)
    except Exception as exc:
        publish(out/"failure.json",sealed(dict(run_id=run_id,status="NOT_EVALUABLE",phase=phase,source_id=sid,
            attempted_sources=attempted,completed_sources=len(rows),hashes_before=before,
            error_class=type(exc).__name__,code=getattr(exc,"code","TECHNICAL_BINDING_ERROR"),
            main_gate_after=False,retry=False),"failure_digest"),MAX_METADATA_BYTES)
    finally:
        MAIN_GATE = False
    return out
