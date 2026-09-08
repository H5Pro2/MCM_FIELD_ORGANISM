"""Single direct NT materialization; no pair comparison or contact frame."""
from dataclasses import asdict
import hashlib
import math
from pathlib import Path
import sys

from tools import _s2nt_private_source_binding as b
from tools import _s2np_private_receptor_materialization as io

ROOT = b.ROOT
MAIN_GATE = False
RUN_ID = "s2nt-receptor-nj-materialization-20260908-01"
PRESEAL = ROOT/"reports/s2nt/s2nt-source-preseal-20260908-01"
EXECUTION_DIGEST = "512cab06237f98ca0481f6b16764e30bdd99bb18841f0fb204c5e4700ae8673d"
SEAL_DIGEST = "ab2f64627d3385592281b6b0b312968bd4ff6397dcc46ec72fafd5779dad676a"
PREVERIFICATION_DIGEST = "0b1ed1b7755ddd532d6af0c181a3abe1d8893e7c1fb8d9f3efa7a1a4817b229c"
EXTRA_PINS = {
    "tools/_s2np_private_receptor_materialization.py": "bcb7e37e2a3aa4a32eb35b40c60ec4ed7ccb59a298837e5889fa0ff4bff6f7e3",
    "mcm_field_organism/broadband_hearing_path.py": "a20456b24c04d099ba5ee2da6250e3d83dc657392603c41d816b13ca68a37fb7"}
OWN = ("tools/_s2nt_private_receptor_materialization.py", "tools/_s2nt_private_materialization_verification.py",
       "reports/s2nt/materialize_once.py")
read_root, binary_digest, atomic_result = io.read_root, io.binary_digest, io.atomic_result


class S2NTMaterializationError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NTMaterializationError(code)


def watched():
    result = b.watched()
    require(all(b.filehash(ROOT/p) == h for p,h in EXTRA_PINS.items()),"DEPENDENCY_CHANGED")
    for p in (*EXTRA_PINS,*OWN):
        result[p] = b.filehash(ROOT/p)
    for name in ("execution-plan.json","evaluation-plan.json","seal.json","verification.json","preregistration.json"):
        p = PRESEAL/name
        result[p.relative_to(ROOT).as_posix()] = b.filehash(p)
    return result


def source_plan():
    e = read_root(PRESEAL/"execution-plan.json","execution_digest")
    s = read_root(PRESEAL/"seal.json","seal_digest")
    v = read_root(PRESEAL/"verification.json","verification_digest")
    require(e["execution_digest"] == s["execution_digest"] == v["execution_digest"] == EXECUTION_DIGEST
        and s["seal_digest"] == v["seal_digest"] == SEAL_DIGEST
        and v["verification_digest"] == PREVERIFICATION_DIGEST,"PRESEAL_BINDING_INVALID")
    require(s["status"] == "S2NT_SOURCES_PRESEALED" and v["status"] == "S2NT_PRESEAL_VERIFIED",
        "PRESEAL_NOT_VALID")
    require(b.filehash(PRESEAL/"execution-plan.json") == s["execution_file_sha256"]
        and b.filehash(PRESEAL/"evaluation-plan.json") == s["evaluation_file_sha256"],"PLAN_FILE_CHANGED")
    require(b.watched() == s["hashes_before"] == s["hashes_after"] == e["source_hashes"],"SOURCE_BINDINGS_CHANGED")
    require(e["environment"] == b.environment() and e["profiles"] == b.profile_binding(),"ENVIRONMENT_PROFILE_CHANGED")
    require(len(e["sources"]) == 14 and e["source_order"] == [f"nt-a{i:02d}" for i in range(1,15)],"SOURCE_COUNT_ORDER_INVALID")
    for spec,row in zip(b.source_specs(),e["sources"],strict=True):
        require(row == b.bind_source(spec,row["pcm_sha256"]),"SOURCE_PLAN_INVALID")
    return e


def run_once():
    require(MAIN_GATE is True and b.MAIN_GATE is False and io.MAIN_GATE is False,"GATE_INVALID")
    out = ROOT/"reports/s2nt"/RUN_ID
    out.mkdir(exist_ok=False)
    phase,sid,ordinal,before = "SOURCE_BINDINGS",None,None,{}
    rows,profile,loaded_numpy,failure,invalid = [],None,None,None,[]
    counts = dict(generation_attempts=0,payloads_validated=0,analyze_attempts=0,analyze_returns=0,
        raw_value_count=0,nj_attempts=0,nj_returns=0,half_value_count=0,completed_sources=0,
        rolling_hops=0,contact_frame_calls=0,pcm_payloads_persisted=0,distance_calls=0,
        vector_pair_comparisons=0,order_criteria_evaluated=0,memory_calls=0,field_calls=0,context_calls=0,runtime_calls=0)
    try:
        before = watched()
        e = source_plan()
        generate,gen = b.pure_generator()
        require(gen == e["generator"],"GENERATOR_CHANGED")
        b.publish(out/"preregistration.json",dict(run_id=RUN_ID,source_hashes=before,
            execution_digest=EXECUTION_DIGEST,seal_digest=SEAL_DIGEST,source_order=e["source_order"],
            profiles=e["profiles"],source_environment=e["environment"],
            command=[sys.executable,"-m","reports.s2nt.materialize_once"],cwd=str(ROOT),
            limits=dict(windows=14,analyses=14,nj_projections=14,values_per_scale=672,
                max_live_pcm_payloads=1,max_live_pcm_bytes=19200,nj_record_bytes=16384,
                max_output_bytes=2097152,max_verification_bytes=262144),
            retry=False,verification_calls_limit=1,raw_and_half_values_retained=True,
            vector_pair_comparisons_authorized=False,order_evaluation_authorized=False),65536)
        phase = "RECEPTOR_INIT"
        import numpy as np
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
        from tools import _s2nj_private_auditory_output_projection as nj
        config = LogSpectralConfig(**e["profiles"]["raw"]["config"])
        require(nj.raw_profile_payload() == e["profiles"]["raw"] and nj.profile_payload() == e["profiles"]["half"]
            and nj.PROFILE_DIGEST == e["profiles"]["half_profile_digest"],"ACTIVE_PROFILE_INVALID")
        loaded_numpy = dict(version=np.__version__,path=str(Path(np.__file__).resolve()),sha256=b.filehash(Path(np.__file__)))
        require(loaded_numpy["version"] == e["environment"]["numpy"]["version"]
            and loaded_numpy["sha256"] == e["environment"]["numpy"]["files"][loaded_numpy["path"]],"LOADED_NUMPY_INVALID")
        receptor = LogSpectralReceptor(config)
        profile = b.sealed(dict(bound_profiles=e["profiles"],config=asdict(config),carriers=list(receptor.channel_ids),
            bands=[asdict(x) for x in receptor.bands],analysis_method="LogSpectralReceptor.analyze",
            projection_method="project_auditory_half_v1",time_semantics="NATIVE_WINDOW_START_DIV_480_NOT_ROLLING_COUNT"),"profile_digest")
        for source in e["sources"]:
            sid,ordinal,invalid = source["source_id"],source["ordinal"],[]
            phase = "NATIVE_TIME_BINDING"
            start,end,index = source["window_start_sample"],source["window_end_sample"],source["nj_snapshot_index"]
            require(all(type(x) is int for x in (start,end,index)) and start >= 0 and start % 480 == 0
                and index == start//480 and end == start+4800 and source["clock_id"] == "audio.sample","SOURCE_TIME_INVALID")
            phase = "PCM_REGENERATION"
            counts["generation_attempts"] += 1
            payload = generate(source["recipe"])
            try:
                phase = "PCM_HASH_VALIDATION"
                require(type(payload) is bytearray and len(payload) == 19200
                    and hashlib.sha256(payload).hexdigest() == source["pcm_sha256"],"PCM_PAYLOAD_INVALID")
                samples = np.frombuffer(payload,dtype="<f4")
                try:
                    require(samples.shape == (4800,) and np.all(np.isfinite(samples)) and np.all(np.abs(samples) <= 1.0),"PCM_FORM_INVALID")
                    counts["payloads_validated"] += 1
                    phase = "RECEPTOR_ANALYZE"
                    counts["analyze_attempts"] += 1
                    values = receptor.analyze(samples)
                    counts["analyze_returns"] += 1
                    counts["raw_value_count"] += len(values) if type(values) is tuple else 0
                finally:
                    del samples
            finally:
                del payload
            phase = "RAW_STATE_BINDING"
            require(type(values) is tuple and len(values) == 48,"RAW_SHAPE_INVALID")
            invalid = [i for i,x in enumerate(values) if type(x) is not float or not math.isfinite(x) or x < 0]
            require(not invalid,"RAW_VALUES_INVALID")
            activity = AuditoryReceptorContact.ACTIVE_ENERGY if any(x != 0 for x in values) else AuditoryReceptorContact.ACTIVE_ZERO
            state = AuditoryReceptorState("auditory",nj.RAW_GEOMETRY,index,start,end,receptor.channel_ids,values,activity)
            raw_digest = state.digest()
            phase = "NJ_PROJECTION"
            counts["nj_attempts"] += 1
            projected = nj.project_auditory_half_v1(state,config=config,source_profile_digest=nj.RAW_PROFILE_DIGEST)
            counts["nj_returns"] += 1
            counts["half_value_count"] += len(projected.values)
            phase = "MATERIALIZED_STATE_BINDING"
            require(state.digest() == raw_digest,"RAW_STATE_MUTATED")
            projection = asdict(projected)
            require(len(b.canonical(projection)) <= 16384,"NJ_RECORD_SIZE_EXCEEDED")
            rows.append(b.sealed(dict(source_id=sid,ordinal=ordinal,source_digest=source["source_digest"],
                recipe_digest=source["recipe_digest"],pcm_sha256=source["pcm_sha256"],clock_id=source["clock_id"],
                payload_hash_checked_before_analysis=True,raw_state=state.canonical_payload(),raw_state_digest=raw_digest,
                raw_values_digest=b.digest(list(values)),raw_values_f64le_sha256=binary_digest(values),
                raw_values_hex=[x.hex() for x in values],
                raw_subnormal_band_indices=[i for i,x in enumerate(values) if 0 < x < sys.float_info.min],
                projection=projection,half_values_f64le_sha256=binary_digest(projected.values),
                half_values_hex=[x.hex() for x in projected.values]),"materialized_state_digest"))
            counts["completed_sources"] += 1
            del state,values,projected
        phase,sid,ordinal = "FINAL_BINDINGS",None,None
        require(counts["completed_sources"] == counts["analyze_returns"] == counts["nj_returns"] == 14
            and counts["raw_value_count"] == counts["half_value_count"] == 672,"COUNTERS_INVALID")
        require(watched() == before,"BOUND_FILES_CHANGED")
    except Exception as exc:
        failure = dict(phase=phase,source_id=sid,ordinal=ordinal,exception_class=type(exc).__name__,
            code=getattr(exc,"code",str(exc)[:256] if isinstance(exc,ValueError) else "TECHNICAL_EXECUTION_ERROR"),
            invalid_band_indices=invalid,counters_at_failure=dict(counts))
    finally:
        close_gate()
    after = {p:b.filehash(ROOT/p) if (ROOT/p).is_file() else None for p in before}
    result = dict(schema="s2nt.receptor-nj-materialization.v1",run_id=RUN_ID,
        status="RECEPTOR_NJ_MATERIALIZATION_COMPLETE" if failure is None else "NOT_EVALUABLE",
        execution_digest=EXECUTION_DIGEST,seal_digest=SEAL_DIGEST,source_hashes_before=before,source_hashes_after=after,
        profile=profile,numpy_loaded=loaded_numpy,states=rows,counts=counts,failure=failure,
        main_gate_after=MAIN_GATE,source_gate_after=b.MAIN_GATE,record_values_are_reduced_not_pcm=True)
    if len(b.canonical(result))+128 > 2097152:
        result.update(status="NOT_EVALUABLE",states=[],omitted_states_for_resource_failure=True,
            failure=dict(phase="RESULT_SIZE",source_id=sid,ordinal=ordinal,code="RESULT_SIZE_EXCEEDED",counters_at_failure=dict(counts)))
    return out,atomic_result(out,result)


def close_gate():
    global MAIN_GATE
    MAIN_GATE = False
