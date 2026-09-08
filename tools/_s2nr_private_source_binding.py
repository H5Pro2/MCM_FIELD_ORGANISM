"""NR source-only specialization of existing NP/ND sealing utilities."""
import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from tools import _s2np_private_source_binding as common

ROOT=common.ROOT
CONTRACT="docs/S2NR_PRIVATER_RUNTIME_ANBINDUNGSPLAN_VERTEILTE_AUDIOBANDSICHT.md"
RGB_GENERATOR="tools/_s2nh_private_source_binding.py"
MAIN_GATE=False
QUAL_ID="s2nr-source-binding-qualification-20260908-01"
QUAL_DIR=ROOT/"reports/s2nr"/QUAL_ID
MAX_METADATA_BYTES=65536
MAX_OUTPUT_BYTES=4194304
canonical,digest,filehash,publish,sealed=common.canonical,common.digest,common.filehash,common.publish,common.sealed
PINS={**{p:h for p,h in common.PINS.items() if p!=common.CONTRACT},
    CONTRACT:"c8fde31c841fab4a61cf1166a35084d39dda53738ec8d36e7364807bb3ec7791",
    RGB_GENERATOR:"766d55bbed5ca0ebdf78b894034568a2c472f57a258a6a4d19aa8308dcbbfa9f",
    "tools/_s2np_private_source_binding.py":"004ea7c8841e5f0b68fe9191604b0a0a7337ac568af2205dca900dd2ae874b12",
    "tools/_s2nl_private_half_profile_binding.py":"1e668ed283524b8815b58c7a360068781b858781b1329778c5b871540d628067",
    "tools/_s2nn_private_half_runtime_binding.py":"41fafcaea48d9029fa2a6e84c0c5477e468761e59499e1f8bfdc952317afddc6",
    "tools/_s2no_private_half_materialization.py":"5d007cbff7156a98f017dcb1af8f7c761698e8e9559e458d024bfb5e8c2a3e3c"}
OWN=("tools/_s2nr_private_source_binding.py","tools/_s2nr_private_preseal_verification.py",
    "tests/test_s2nr_private_source_binding.py","reports/s2nr/qualify_once.py",
    "reports/s2nr/preseal_once.py","reports/s2nr/QUALIFIKATIONSBINDUNG.md")
CODE=("tools/_s2nq_private_mask_scan.py","tools/_s2nq_private_direct.py",
    "tools/_s2mr_private_minimal_mcm_runtime.py","tools/_s2lm_private_role_free_stream_processor.py",
    "tools/_s2jw_profiled_memory_coordinator.py","tools/_s2jw_default_live_profile.py",
    "tools/_s2jw_default_live_av_pairing.py","mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/finite_video_path.py","mcm_field_organism/broadband_hearing_path.py")
AV,A="COMPLETE_AV_PERCEPTION","PARTIAL_AUDITORY_CUE"
ROWS=((AV,2,2),(A,3,None),(AV,1,1),(A,4,None),(AV,1,1),(AV,1,1),(AV,1,1),
      (AV,2,3),(AV,2,4),(AV,2,5),(AV,2,6),(AV,2,7),(AV,2,8),(AV,2,9),(AV,2,10),(AV,2,11),
      (A,5,None),(A,6,None))
AUDIO=(
    ((1837000,3674000,5511000),common.A0,"s2nr-pcm-001"),
    ((443000,886000,1329000),common.A0,"s2nr-pcm-002"),
    ((1837000,3674000,5511000),common.A0,"s2nr-pcm-001"),
    ((1837000,3674000,5511000),common.A1,"s2nr-pcm-001"),
    ((1892110,3784220,5676330),common.A0,"s2nr-pcm-001"),
    ((739000,3181000,9473000),common.A0,"s2nr-pcm-003"))
VIEWS=common.VIEWS[:2]


class S2NRBindingError(ValueError):
    pass


def require(ok,code):
    if not ok:
        raise S2NRBindingError(code)


def watched():
    require(all(filehash(ROOT/p)==h for p,h in PINS.items()),"PIN_CHANGED")
    return {p:filehash(ROOT/p) for p in sorted(set(PINS)|set(OWN)|set(CODE))}


@dataclass(frozen=True,slots=True)
class SourceSpec:
    source_id: str
    kind: str
    recipe_json: str

    def __post_init__(self):
        require(type(self.source_id) is str and re.fullmatch(r"[a-z][a-z0-9-]{2,95}",self.source_id),"SOURCE_ID_INVALID")
        require(self.kind in ("PCM","RGB") and type(self.recipe_json) is str,"SOURCE_FORM_INVALID")
        recipe=json.loads(self.recipe_json)
        require(self.recipe_json==canonical(recipe).decode("ascii"),"RECIPE_CANONICAL_INVALID")

    def recipe(self):
        return json.loads(self.recipe_json)

    def payload(self):
        return dict(source_id=self.source_id,kind=self.kind,recipe=self.recipe(),
                    recipe_digest=digest(self.recipe()),byte_count=19200 if self.kind=="PCM" else 6220800)


def source_specs():
    specs=[]
    for i,(freq,amps,seed) in enumerate(AUDIO,1):
        recipe=dict(sample_count=4800,sample_rate=48000,groups=[dict(seed=seed,partials=[
            dict(frequency_millihz=f,amplitude_ratio=list(a)) for f,a in zip(freq,amps,strict=True)])])
        specs.append(SourceSpec(f"nr-a{i:02d}","PCM",canonical(recipe).decode()))
    for i in range(1,12):
        recipe=dict(algorithm="NH_SHA_GRID_RGB8_V1",seed=f"s2nr-independent-av-20260908-v1:visual:v{i:02d}",
            width=1920,height=1080,rows=8,columns=12,channels=3,format="RGB8",partial=False,visible_positions=None)
        specs.append(SourceSpec(f"nr-v{i:02d}","RGB",canonical(recipe).decode()))
    return tuple(specs)


def events():
    rows=[]
    for n,(kind,a,v) in enumerate(ROWS,1):
        end=n*100000000
        audio=dict(source_id=f"nr-a{a:02d}",clock_id="audio.sample",start_tick=(n-1)*4800,end_tick=n*4800,
            hop_start=(n-1)*10,hop_end=n*10,endpoint_snapshot_index=(n-1)*10,common_window=[end-10000000,end])
        frame=3*(n-1)+2
        visual=None if v is None else dict(source_id=f"nr-v{v:02d}",clock_id="video.frame",start_tick=frame,
            end_tick=frame+1,common_window=[frame*1000000000//30,end])
        rows.append(dict(event_id=f"e{n:02d}",ordinal=n,event_type=kind,source_occurrence_id=f"s2nr-source-e{n:02d}",
            field_clock_id="s2nr-transfer-field-clock",field_window=[(n-1)*100000000,end],auditory=audio,visual=visual))
    return rows


def bind_source(spec,sha):
    require(type(spec) is SourceSpec,"SOURCE_TYPE_INVALID")
    require(type(sha) is str and re.fullmatch(r"[0-9a-f]{64}",sha),"PAYLOAD_DIGEST_INVALID")
    occurrences=[dict(event_id=e["event_id"],ordinal=e["ordinal"],**part) for e in events()
                 for part in (e["auditory"],e["visual"]) if part is not None and part["source_id"]==spec.source_id]
    return sealed({**spec.payload(),"payload_sha256":sha,"occurrences":occurrences},"source_digest")


def generators():
    pcm,pcm_identity=common.pure_generator()
    require(filehash(ROOT/RGB_GENERATOR)==PINS[RGB_GENERATOR],"RGB_GENERATOR_CHANGED")
    tree=ast.parse((ROOT/RGB_GENERATOR).read_text(encoding="utf-8"))
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ("rgb_recipe","rgb_payload")]
    require([n.name for n in nodes]==["rgb_recipe","rgb_payload"],"RGB_GENERATOR_SELECTION_INVALID")
    namespace=dict(np=np,hashlib=hashlib,require=require)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(ROOT/RGB_GENERATOR),"exec"),namespace)
    identity=dict(pcm=pcm_identity,rgb=dict(path=RGB_GENERATOR,file_sha256=PINS[RGB_GENERATOR],
        functions=[n.name for n in nodes],ast_digest=digest(ast.dump(ast.Module(body=nodes,type_ignores=[]),include_attributes=False)),
        historical_entry_executed=False))
    return pcm,namespace["rgb_payload"],identity


def environment():
    return {**common.environment(),"numpy_imported":True,"numpy_role":"RGB_GENERATION_ONLY"}


def profiles():
    return dict(auditory=common.profile_binding(),
        visual=dict(source_width=1920,source_height=1080,grid_columns=12,grid_rows=8,frames_per_second=30.0,
                    carrier_order="grid_row-grid_column-rgb_channel"),
        coordinator_config_digest="55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e",
        fast_audio_threshold=0.1,fast_visual_threshold=0.2,ppb_audio_threshold=0.01,ppb_visual_threshold=0.01,
        fast_rank="max(2*d_audio,d_visual),2*d_audio+d_visual,slot_id",
        binding_method="literal qualified half-profile metadata; no configuration functions executed")


def budgets():
    return dict(pcm_sources=6,rgb_sources=11,events=18,formations_per_arm=14,auditory_cues_per_arm=4,
        generated_pcm_bytes=115200,generated_rgb_bytes=68428800,max_live_pcm_payloads=1,max_live_rgb_payloads=1,
        max_pcm_bytes=19200,max_rgb_bytes=6220800,metadata_bytes=MAX_METADATA_BYTES,output_bytes=MAX_OUTPUT_BYTES,
        future_audio_windows=18,future_hops=180,future_audio_snapshots=171,future_nj=18,future_visual_analyses=14,
        future_scan_receipts=16,future_field_contacts=9792)


def execution_plan(sources,env,hashes,gen):
    specs=source_specs()
    require(type(sources) is list and len(sources)==17,"SOURCE_COUNT_INVALID")
    for spec,row in zip(specs,sources,strict=True):
        require(row==bind_source(spec,row.get("payload_sha256")),"SOURCE_BINDING_INVALID")
    result=sealed(dict(schema="s2nr.source-execution-plan.v1",contract_sha256=PINS[CONTRACT],
        sources=sources,source_order=[s.source_id for s in specs],events=events(),profiles=profiles(),
        views=[dict(view_id=name,indices=list(indices),complement=[i for i in range(48) if i not in indices])
               for name,indices in VIEWS],
        retrieval=dict(a_rule="ALL_BANDS_24",a_arithmetic="max",a_threshold=0.1,
            slow_arithmetic="historical sum in original index order / 24",slow_threshold=0.01),
        environment=env,generators=gen,source_hashes=hashes,budgets=budgets(),
        receptor_execution_authorized=False,nj_execution_authorized=False,runtime_execution_authorized=False),"execution_digest")
    require(len(canonical(result))<=MAX_METADATA_BYTES,"METADATA_SIZE_EXCEEDED")
    return result


def evaluation_plan(execution):
    return sealed(dict(schema="s2nr.evaluation-plan.v1",execution_digest=execution["execution_digest"],
        contract_sha256=PINS[CONTRACT],target_source="nr-a01",competition_source="nr-a02",
        cases=[dict(event_id=e,cue_id=c,target=t,subtype=sub,phase=p,prediction=prediction) for e,c,t,sub,p,prediction in (
            ("e02","nr-a03","nr-a01","EXACT","BEFORE_TARGET","ABSTAIN"),
            ("e04","nr-a04","nr-a01","LEVEL","EARLY","A_RECENT"),
            ("e17","nr-a05","nr-a01","FREQUENCY","LATE","B_STABLE_AUDITORY"),
            ("e18","nr-a06",None,"INDEPENDENT_CONTROL","LATE","ABSTAIN"))],
        retention_identity="D=R+L",zero_denominator="ERHALTUNG_NICHT_GEPRUEFT",
        relationship_and_public_denominators_separate=True,a_and_b_retention_separate=True,
        receptor_variation_reference="prior source-bound formation input on the same original indices",
        missing_reference=None,slot_deviation_separate=True,offset_losses_with_gains=False,
        no_success_start_gate=True,no_replacement_source=True),"evaluation_digest")


def collisions(sources):
    groups={}
    for row in sources:
        groups.setdefault((row["kind"],row["payload_sha256"]),[]).append(row["source_id"])
    return [dict(kind=k,payload_sha256=h,source_ids=ids) for (k,h),ids in sorted(groups.items()) if len(ids)>1]


def preseal_once(run_id):
    require(type(run_id) is str and re.fullmatch(r"s2nr-source-preseal-\d{8}-\d{2}",run_id),"RUN_ID_INVALID")
    out=ROOT/"reports/s2nr"/run_id
    out.mkdir(exist_ok=False)
    before,rows,attempted={},[],0
    phase,sid="QUALIFICATION_BINDING",None
    try:
        q=json.loads((QUAL_DIR/"result.json").read_bytes())
        require(q["result_digest"]==digest({k:v for k,v in q.items() if k!="result_digest"})
            and q["status"]=="S2NR_SOURCE_BINDING_QUALIFIED" and q["passed_tests"]==12
            and q["unittest_calls"]==1 and q["exit_code"]==0,"QUALIFICATION_REQUIRED")
        before=watched()
        require(before==q["hashes_after"]==q["hashes_before"],"QUALIFIED_SOURCES_CHANGED")
        phase="ENVIRONMENT_BINDING"
        env=environment()
        pcm,rgb,gen=generators()
        publish(out/"preregistration.json",dict(run_id=run_id,hashes=before,environment=env,generators=gen,
            specs=[s.payload() for s in source_specs()],events=events(),profiles=profiles(),budgets=budgets(),
            qualification_sha256=filehash(QUAL_DIR/"result.json"),retry=False),MAX_METADATA_BYTES)
        for spec in source_specs():
            phase,sid="PAYLOAD_GENERATION",spec.source_id
            attempted+=1
            payload=(pcm if spec.kind=="PCM" else rgb)(spec.recipe())
            try:
                phase="PAYLOAD_BINDING"
                if spec.kind=="PCM":
                    require(type(payload) is bytearray and len(payload)==19200,"PCM_FORM_INVALID")
                else:
                    require(type(payload) is np.ndarray and payload.shape==(1080,1920,3)
                            and payload.dtype==np.uint8 and payload.flags.c_contiguous and not payload.flags.writeable,"RGB_FORM_INVALID")
                view=memoryview(payload).cast("B")
                try:
                    require(view.nbytes==spec.payload()["byte_count"],"PAYLOAD_SIZE_INVALID")
                    h=hashlib.sha256(view).hexdigest()
                finally:
                    view.release()
                    del view
            finally:
                del payload
            rows.append(bind_source(spec,h))
        phase,sid="PLAN_BINDING",None
        require(rows[0]["payload_sha256"]==rows[2]["payload_sha256"]
                and rows[0]["source_digest"]!=rows[2]["source_digest"],"EXACT_COPY_DIFFERS")
        execution=execution_plan(rows,env,before,gen)
        evaluation=evaluation_plan(execution)
        after=watched()
        require(before==after and env==environment(),"BINDINGS_CHANGED")
        phase="PUBLICATION"
        a=publish(out/"execution-plan.json",execution,MAX_METADATA_BYTES)
        b=publish(out/"evaluation-plan.json",evaluation,MAX_METADATA_BYTES)
        seal=sealed(dict(schema="s2nr.source-seal.v1",run_id=run_id,status="S2NR_SOURCES_PRESEALED",
            execution_digest=execution["execution_digest"],evaluation_digest=evaluation["evaluation_digest"],
            execution_file_sha256=a,evaluation_file_sha256=b,hashes_before=before,hashes_after=after,
            attempted_sources=attempted,completed_sources=len(rows),generated_pcm_sources=6,generated_rgb_sources=11,
            generated_pcm_bytes=115200,generated_rgb_bytes=68428800,max_live_pcm_payloads=1,max_live_rgb_payloads=1,
            raw_payloads_persisted=0,receptor_calls=0,nj_calls=0,distance_calls=0,memory_calls=0,context_calls=0,
            field_calls=0,runtime_calls=0,main_gate_after=MAIN_GATE,
            exact_pairs=[["nr-a01","nr-a03"]],collisions=collisions(rows)),"seal_digest")
        publish(out/"seal.json",seal,MAX_METADATA_BYTES)
    except Exception as exc:
        publish(out/"failure.json",sealed(dict(run_id=run_id,status="NOT_EVALUABLE",phase=phase,source_id=sid,
            attempted_sources=attempted,completed_sources=len(rows),error_class=type(exc).__name__,
            code=str(exc) if isinstance(exc,S2NRBindingError) else "TECHNICAL_EXECUTION_ERROR",
            hashes_before=before,main_gate_after=MAIN_GATE),"failure_digest"))
    return out
