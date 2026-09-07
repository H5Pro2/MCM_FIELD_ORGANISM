"""One source-bound direct analysis and NJ projection per NP source, no comparisons."""

from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys

from tools import _s2np_private_source_binding as b

ROOT = b.ROOT
MAIN_GATE = False
RUN_ID = "s2np-receptor-nj-materialization-20260907-01"
PRESEAL = ROOT / "reports/s2np/s2np-source-preseal-20260907-01"
EXECUTION_DIGEST = "bae2b0ef565a5117c28984d40753da39cc1ca82b576e59864c72d57212254664"
SEAL_DIGEST = "a72aa07c9dc153f29a187470bce76fb918ce8cbbaeb4f2666c700fb719bf307b"
PREVERIFICATION_DIGEST = "1de2a65b9fd918ebf95af524b877cec627a40de89695707aa258aa276ff1a7f7"


class S2NPMaterializationError(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise S2NPMaterializationError(code)


def read_root(path, key):
    data = path.read_bytes()
    value = json.loads(data)
    require(data == b.canonical(value) and value[key] == b.digest({k: v for k, v in value.items() if k != key}),
            "CANONICAL_ROOT_INVALID")
    return value


def watched():
    paths = {**b.watched()}
    for p in ("tools/_s2np_private_receptor_materialization.py", "tools/_s2np_private_materialization_verification.py",
              "reports/s2np/materialize_once.py", "mcm_field_organism/broadband_hearing_path.py"):
        paths[p] = b.filehash(ROOT / p)
    for name in ("execution-plan.json", "evaluation-plan.json", "seal.json", "verification.json", "preregistration.json"):
        p = PRESEAL / name
        paths[p.relative_to(ROOT).as_posix()] = b.filehash(p)
    return paths


def source_plan():
    execution = read_root(PRESEAL / "execution-plan.json", "execution_digest")
    seal = read_root(PRESEAL / "seal.json", "seal_digest")
    verification = read_root(PRESEAL / "verification.json", "verification_digest")
    require(execution["execution_digest"] == EXECUTION_DIGEST == seal["execution_digest"]
            and seal["seal_digest"] == SEAL_DIGEST == verification["seal_digest"]
            and verification["verification_digest"] == PREVERIFICATION_DIGEST, "PRESEAL_BINDING_INVALID")
    require(seal["status"] == "S2NP_SOURCES_PRESEALED"
            and verification["status"] == "S2NP_PRESEAL_BINDINGS_VALID", "PRESEAL_NOT_VALID")
    require(b.filehash(PRESEAL / "execution-plan.json") == seal["execution_file_sha256"]
            and b.filehash(PRESEAL / "evaluation-plan.json") == seal["evaluation_file_sha256"], "PLAN_FILE_CHANGED")
    require(b.watched() == seal["hashes_before"] == seal["hashes_after"] == execution["source_hashes"], "SOURCE_BINDINGS_CHANGED")
    require(execution["environment"] == b.environment(), "ENVIRONMENT_CHANGED")
    require(execution["profiles"] == b.profile_binding() and len(execution["sources"]) == 12, "PROFILE_OR_SOURCE_COUNT_INVALID")
    for spec, source in zip(b.source_specs(), execution["sources"], strict=True):
        require(source == b.bind_source(spec, source["pcm_sha256"]), "SOURCE_PLAN_INVALID")
    return execution


def binary_digest(values):
    return hashlib.sha256(struct.pack("<48d", *values)).hexdigest()


def atomic_result(out, result):
    result = b.sealed(result, "record_digest")
    data = b.canonical(result)
    require(len(data) <= b.MAX_OUTPUT_BYTES, "RESULT_SIZE_EXCEEDED")
    tmp = out / "result.json.pending"
    with tmp.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.rename(tmp, out / "result.json")
    return result


def run_once():
    out = ROOT / "reports/s2np" / RUN_ID
    out.mkdir(exist_ok=False)
    phase, sid, ordinal = "SOURCE_BINDINGS", None, None
    before, profile, loaded_numpy, rows = {}, None, None, []
    counts = dict(generation_attempts=0, payloads_validated=0, analyze_attempts=0, analyze_returns=0,
                  raw_value_count=0, nj_attempts=0, nj_returns=0, half_value_count=0, completed_sources=0,
                  rolling_hops=0, contact_frame_calls=0, pcm_payloads_persisted=0,
                  distance_calls=0, mask_comparison_calls=0, rule_calls=0,
                  memory_calls=0, context_calls=0, field_calls=0, runtime_calls=0)
    failure = None
    invalid_bands = []
    try:
        before = watched()
        execution = source_plan()
        generate, generator = b.pure_generator()
        require(generator == execution["generator"], "GENERATOR_CHANGED")
        b.publish(out / "preregistration.json", dict(run_id=RUN_ID, source_hashes=before,
            execution_digest=EXECUTION_DIGEST, seal_digest=SEAL_DIGEST,
            source_order=execution["source_order"], profiles=execution["profiles"],
            command=[sys.executable, "-m", "reports.s2np.materialize_once"], cwd=str(ROOT),
            limits=dict(source_windows=12, analyses=12, raw_values=576, nj_projections=12, half_values=576,
                        max_live_pcm_bytes=19200, max_live_pcm_payloads=1, nj_record_bytes=16384,
                        max_output_bytes=b.MAX_OUTPUT_BYTES),
            retry=False, verification_calls_limit=1, raw_and_half_values_retained=True,
            source_environment=execution["environment"]), b.MAX_METADATA_BYTES)
        phase = "RECEPTOR_INIT"
        import numpy as np
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
        from tools import _s2nj_private_auditory_output_projection as nj
        config = LogSpectralConfig(**execution["profiles"]["raw"]["config"])
        require(nj.raw_profile_payload() == execution["profiles"]["raw"]
                and nj.profile_payload() == execution["profiles"]["half"]
                and nj.PROFILE_DIGEST == execution["profiles"]["half_profile_digest"], "ACTIVE_PROFILE_INVALID")
        loaded_numpy = dict(version=np.__version__, path=str(Path(np.__file__).resolve()),
                            sha256=b.filehash(Path(np.__file__)))
        require(loaded_numpy["version"] == execution["environment"]["numpy"]["version"]
                and loaded_numpy["sha256"] == execution["environment"]["numpy"]["files"][loaded_numpy["path"]],
                "LOADED_NUMPY_INVALID")
        receptor = LogSpectralReceptor(config)
        profile = b.sealed(dict(bound_profiles=execution["profiles"], config=asdict(config),
            carriers=list(receptor.channel_ids), bands=[asdict(x) for x in receptor.bands],
            analysis_method="LogSpectralReceptor.analyze", projection_method="project_auditory_half_v1",
            raw_state_time_semantics="DIRECT_SOURCE_WINDOW_ON_BOUND_HOP_GRID_NOT_ROLLING_OUTPUT_COUNT"), "profile_digest")
        for source in execution["sources"]:
            sid, ordinal, invalid_bands = source["source_id"], source["ordinal"], []
            phase = "PCM_REGENERATION"
            counts["generation_attempts"] += 1
            payload = generate(source["recipe"])
            try:
                phase = "PCM_HASH_VALIDATION"
                require(type(payload) is bytearray and len(payload) == 19200
                        and hashlib.sha256(payload).hexdigest() == source["pcm_sha256"], "PCM_PAYLOAD_INVALID")
                samples = np.frombuffer(payload, dtype="<f4")
                try:
                    require(samples.shape == (4800,) and np.all(np.isfinite(samples))
                            and np.all(np.abs(samples) <= 1.0), "PCM_FORM_INVALID")
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
            require(type(values) is tuple and len(values) == 48, "RAW_SHAPE_INVALID")
            invalid_bands = [i for i, x in enumerate(values) if type(x) is not float or not math.isfinite(x) or x < 0]
            require(not invalid_bands, "RAW_NORMALFORM_INVALID")
            activity = AuditoryReceptorContact.ACTIVE_ENERGY if any(v != 0.0 for v in values) else AuditoryReceptorContact.ACTIVE_ZERO
            state = AuditoryReceptorState("auditory", nj.RAW_GEOMETRY, source["snapshot_index"],
                source["window_start_sample"], source["window_end_sample"], receptor.channel_ids, values, activity)
            raw_digest = state.digest()
            phase = "NJ_PROJECTION"
            counts["nj_attempts"] += 1
            projected = nj.project_auditory_half_v1(state, config=config, source_profile_digest=nj.RAW_PROFILE_DIGEST)
            counts["nj_returns"] += 1
            counts["half_value_count"] += len(projected.values)
            phase = "MATERIALIZED_STATE_BINDING"
            require(state.digest() == raw_digest, "RAW_STATE_MUTATED")
            projection = asdict(projected)
            require(len(b.canonical(projection)) <= 16384, "NJ_RECORD_SIZE_EXCEEDED")
            row = b.sealed(dict(source_id=sid, ordinal=ordinal, source_digest=source["source_digest"],
                recipe_digest=source["recipe_digest"], pcm_sha256=source["pcm_sha256"],
                payload_hash_checked_before_analysis=True, clock_id=source["clock_id"],
                raw_state=state.canonical_payload(), raw_state_digest=raw_digest,
                raw_values_digest=b.digest(list(values)), raw_values_f64le_sha256=binary_digest(values),
                raw_values_hex=[v.hex() for v in values],
                raw_subnormal_band_indices=[i for i, v in enumerate(values) if 0 < v < sys.float_info.min],
                projection=projection, half_values_f64le_sha256=binary_digest(projected.values),
                half_values_hex=[v.hex() for v in projected.values]), "materialized_state_digest")
            rows.append(row)
            counts["completed_sources"] += 1
            del projected, state, values
        phase, sid, ordinal = "FINAL_BINDINGS", None, None
        require(counts["completed_sources"] == counts["analyze_returns"] == counts["nj_returns"] == 12
                and counts["raw_value_count"] == counts["half_value_count"] == 576, "COUNTERS_INVALID")
        require(watched() == before, "BOUND_FILES_CHANGED")
    except Exception as exc:
        failure = dict(phase=phase, source_id=sid, ordinal=ordinal, exception_class=type(exc).__name__,
                       code=str(exc)[:256] if isinstance(exc, ValueError) else "TECHNICAL_EXECUTION_ERROR",
                       invalid_band_indices=invalid_bands, counters_at_failure=dict(counts))
    after = {p: b.filehash(ROOT / p) if (ROOT / p).is_file() else None for p in before}
    result = dict(schema="s2np.receptor-nj-materialization.v1", run_id=RUN_ID,
        status="RECEPTOR_NJ_MATERIALIZATION_COMPLETE" if failure is None else "NOT_EVALUABLE",
        execution_digest=EXECUTION_DIGEST, seal_digest=SEAL_DIGEST,
        source_hashes_before=before, source_hashes_after=after, profile=profile,
        numpy_loaded=loaded_numpy, states=rows, counts=counts, failure=failure,
        main_gate_after=False, source_gate_after=b.MAIN_GATE, record_values_are_reduced_not_pcm=True)
    if len(b.canonical(result)) + 128 > b.MAX_OUTPUT_BYTES:
        result.update(status="NOT_EVALUABLE", states=[], omitted_states_for_resource_failure=True,
            failure=dict(phase="RESULT_SIZE", source_id=sid, ordinal=ordinal, code="RESULT_SIZE_EXCEEDED",
                         counters_at_failure=dict(counts)))
    result = atomic_result(out, result)
    return out, result
