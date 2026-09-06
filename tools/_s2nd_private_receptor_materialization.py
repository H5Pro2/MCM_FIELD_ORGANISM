"""S2-ND one-shot source-bound receptor materialization; no matching."""

from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "s2nd-receptor-materialization-20260906-01"
OUT = ROOT / "reports/s2nd" / RUN_ID
CALL_PLAN = ROOT / "reports/s2nd/s2nd-receptor-materialization-call-plan.json"
PRESEAL = "reports/s2nd/s2nd-source-panel-preseal-20260906-02/"
EXECUTION_DIGEST = "e29682fe7606f533c068b3a57c5f986a18934cea2b7c0ca977c0c538a6052f22"
SEAL_DIGEST = "333f15e8ba0a69e50c12481503f089a348a367eec0c8bb2489cc9f184393b61a"
PROFILE = dict(sample_rate=48000, window_size=4800, hop_size=480,
               min_frequency=50.0, max_frequency=18000.0, band_count=48)
RECIPE_KEYS = ("source_id", "format", "channels", "sample_rate", "sample_count", "algorithm", "seed", "partials")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def filehash(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def require(condition, code):
    if not condition:
        raise ValueError(code)


def bound_json(relative, digest_key):
    data = (ROOT / relative).read_bytes()
    value = json.loads(data)
    require(canonical(value) == data, "CANONICAL_BINDING_INVALID")
    require(value[digest_key] == digest({k: v for k, v in value.items() if k != digest_key}), "ROOT_DIGEST_INVALID")
    return value


def main():
    OUT.mkdir(exist_ok=False)
    phase, source_id, ordinal = "SOURCE_BINDINGS", None, None
    attempted = returned = 0
    states, invalid_bands = [], []
    profile_record = numpy_identity = None
    failure, after, bindings = None, {}, {}
    call_plan_sha = filehash(CALL_PLAN)
    try:
        plan = json.loads(CALL_PLAN.read_bytes())
        require(plan["run_id"] == RUN_ID, "RUN_ID_INVALID")
        bindings = plan["source_hashes_before"]
        require(all(filehash(ROOT / p) == h for p, h in bindings.items()), "BOUND_FILE_CHANGED")
        seal = bound_json(PRESEAL + "seal.json", "seal_digest")
        execution = bound_json(PRESEAL + "execution-plan.json", "execution_digest")
        require(seal["seal_digest"] == SEAL_DIGEST and execution["execution_digest"] == EXECUTION_DIGEST
                == seal["execution_digest"], "SEALED_ROOT_INVALID")
        require(filehash(ROOT / PRESEAL / "execution-plan.json") == seal["execution_file_sha256"]
                and filehash(ROOT / PRESEAL / "evaluation-plan.json") == seal["evaluation_file_sha256"],
                "PLAN_FILE_BINDING_INVALID")
        require(seal["source_hashes_before"] == seal["source_hashes_after"]
                and all(bindings[p] == h for p, h in seal["source_hashes_before"].items()), "SEALED_SOURCE_INVALID")
        identity = execution["generator_identity"]
        require(identity == seal["generator_identity"] and sys.version == identity["python_version"]
                and sys.executable == identity["python_executable"]
                and filehash(Path(sys.executable)) == identity["python_executable_sha256"], "INTERPRETER_BINDING_INVALID")
        require(identity["generator_path"] == "reports/s2nd/seal_inventory.py"
                and bindings[identity["generator_path"]] == identity["generator_sha256"], "GENERATOR_BINDING_INVALID")
        from reports.s2nd import seal_inventory as generator
        require(generator.math_identity(math, sys.builtin_module_names) == identity["math_module"], "MATH_BINDING_INVALID")
        require(execution["receptor_profile"] == PROFILE
                and execution["receptor_profile_digest"] == digest(PROFILE), "PROFILE_BINDING_INVALID")
        sources = execution["sources"]
        require(len(sources) == 18, "SOURCE_COUNT_INVALID")
        for n, source in enumerate(sources, 1):
            source_id, ordinal = source["source_id"], n
            require(source_id == f"s{n:03d}" and source["ordinal"] == n, "SOURCE_ORDER_INVALID")
            require(source["clock_id"] == "s2nd-source-sample-clock"
                    and (source["window_start_sample"], source["window_end_sample"])
                    == ((n - 1) * 4800, n * 4800), "SOURCE_TIME_INVALID")
            require(source["format"] == "PCM_F32LE" and source["channels"] == 1
                    and source["sample_rate"] == 48000 and source["sample_count"] == 4800
                    and source["pcm_byte_count"] == 19200, "SOURCE_FORM_INVALID")
            require(source["recipe_digest"] == digest({k: source[k] for k in RECIPE_KEYS}), "RECIPE_DIGEST_INVALID")
        phase, source_id, ordinal = "RECEPTOR_INIT", None, None
        import numpy as np
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        numpy_identity = {"version": np.__version__, "module_file": np.__file__, "module_sha256": filehash(Path(np.__file__))}
        config = LogSpectralConfig(**execution["receptor_profile"])
        receptor = LogSpectralReceptor(config)
        require(asdict(config) == PROFILE, "ACTIVE_PROFILE_INVALID")
        profile = {"config": asdict(config), "config_digest": execution["receptor_profile_digest"],
                   "channel_ids": list(receptor.channel_ids), "bands": [asdict(b) for b in receptor.bands],
                   "method": "LogSpectralReceptor.analyze",
                   "receptor_source_sha256": bindings["mcm_field_organism/log_spectral_receptor.py"]}
        profile_record = {**profile, "profile_digest": digest(profile)}
        for source in sources:
            source_id, ordinal = source["source_id"], source["ordinal"]
            phase = "PCM_REGENERATION"
            payload = generator.pcm_payload({k: source[k] for k in RECIPE_KEYS})
            try:
                phase = "PCM_VALIDATION"
                require(len(payload) == 19200 and hashlib.sha256(payload).hexdigest() == source["pcm_sha256"],
                        "PCM_PAYLOAD_INVALID")
                samples = np.frombuffer(payload, dtype="<f4")
                try:
                    require(samples.shape == (4800,) and np.all(np.isfinite(samples))
                            and np.all(np.abs(samples) <= 1.0), "PCM_DOMAIN_INVALID")
                    phase = "RECEPTOR_ANALYZE"
                    attempted += 1
                    values = receptor.analyze(samples)
                    returned += 1
                finally:
                    del samples
            finally:
                del payload
            phase = "OUTPUT_VALIDATION"
            require(type(values) is tuple and len(values) == 48, "OUTPUT_SHAPE_INVALID")
            invalid_bands = [i for i, v in enumerate(values) if type(v) is not float or not math.isfinite(v) or not 0.0 <= v <= 1.0]
            require(not invalid_bands, "OUTPUT_DOMAIN_INVALID")
            state = {"source_id": source_id, "ordinal": ordinal, "recipe_digest": source["recipe_digest"],
                     "pcm_sha256": source["pcm_sha256"], "payload_validated_before_analysis": True,
                     "clock_id": source["clock_id"], "window_start_sample": source["window_start_sample"],
                     "window_end_sample": source["window_end_sample"], "sample_count": 4800,
                     "time_semantics": "DECLARED_PCM_SOURCE_WINDOW_NOT_RECEPTOR_TIMESTAMP",
                     "execution_digest": EXECUTION_DIGEST, "profile_digest": profile_record["profile_digest"],
                     "values": list(values), "values_digest": digest(list(values)),
                     "values_f64le_sha256": hashlib.sha256(struct.pack("<48d", *values)).hexdigest()}
            states.append({**state, "materialized_state_digest": digest(state)})
            del values
        phase, source_id, ordinal = "FINAL_BINDINGS", None, None
        require(attempted == returned == len(states) == 18, "ANALYSIS_COUNT_INVALID")
        after = {p: filehash(ROOT / p) for p in bindings}
        require(after == bindings, "BOUND_FILE_CHANGED")
    except Exception as error:
        failure = {"phase": phase, "source_id": source_id, "ordinal": ordinal,
                   "completed_analyses": len(states), "analyze_attempt_count": attempted,
                   "analyze_return_count": returned, "exception_class": type(error).__name__,
                   "technical_detail": str(error)[:512], "invalid_output_bands": invalid_bands}
        after = {p: filehash(ROOT / p) if (ROOT / p).is_file() else None for p in bindings}
    result = {"schema": "s2nd.receptor-materialization.v1", "run_id": RUN_ID,
              "technical_status": "RECEPTOR_MATERIALIZATION_COMPLETE" if failure is None else "NOT_EVALUABLE",
              "call_plan_sha256": call_plan_sha, "seal_digest": SEAL_DIGEST, "execution_digest": EXECUTION_DIGEST,
              "python_version": sys.version, "numpy_identity": numpy_identity,
              "input_hashes": bindings, "source_hashes_after": after, "sources_unchanged": bool(bindings) and bindings == after,
              "receptor_profile": profile_record, "states": states, "failure": failure,
              "counts": {"analyze_attempt_count": attempted, "analyze_return_count": returned,
                         "completed_analyses": len(states), "receptor_values": 48 * len(states),
                         "distance_calculations": 0, "rule_calls": 0, "memory_calls": 0, "context_calls": 0,
                         "field_calls": 0, "runtime_calls": 0, "pcm_payloads_persisted": 0}}
    result["record_digest"] = digest(result)
    data = canonical(result)
    require(len(data) <= 4194304, "RESULT_SIZE_INVALID")
    temporary = OUT / "result.json.pending"
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.rename(temporary, OUT / "result.json")
    print(json.dumps({"run_id": RUN_ID, "technical_status": result["technical_status"], "counts": result["counts"],
                      "failure": failure, "record_digest": result["record_digest"], "file_sha256": hashlib.sha256(data).hexdigest(),
                      "bytes": len(data), "sources_unchanged": result["sources_unchanged"]}, sort_keys=True))
    return 0 if failure is None else 1


if __name__ == "__main__":
    sys.exit(main())
