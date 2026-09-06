"""One sealed PCM materialization; no applicability or memory operations."""

from __future__ import annotations

import ast
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[1]
PRESEAL = "reports/s2nc/s2nc-source-panel-preseal-20260906-01"
RUN_ID = "s2nc-receptor-materialization-20260906-01"
SEAL_DIGEST = "ac2ec3e0441fb463c2a1a80d8cb296bbc4934f7555899c5750aa32a0ea56679b"
EXECUTION_DIGEST = "00a0f5d177d11702b6ac08056d08b0501f125cefa8f0c0f1e3b651b894c67ae2"
PRESEAL_FILE_HASHES = {
    "execution-plan.json": "ab23d2dac4d5bbd10ba790d36ef92010f5bf417717087307510ee4ec891df282",
    "evaluation-plan.json": "0a2e61adb26fa93ed4607a059db87851720a7636c7253f65206827996ec9ae65",
    "seal.json": "5db84b737689a0d1284717132bc433515508fc2d172d1e4118b5de888162bf7d",
    "BEFUND.md": "68abb1b27de0aab04cb8fb6e0e34515869d733c0323c138efcfe958282d75bbb",
}
PROFILE = dict(sample_rate=48000, window_size=4800, hop_size=480,
               min_frequency=50.0, max_frequency=18000.0, band_count=48)
RECIPE_KEYS = ("source_id", "algorithm", "sample_rate", "sample_count", "groups")
MAX_RESULT_BYTES = 4_194_304


def canonical(value):
    return json.dumps(value, allow_nan=False, ensure_ascii=True,
                      sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def require(condition, code):
    if not condition:
        raise ValueError(code)


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_bound(name, digest_key):
    data = (ROOT / PRESEAL / name).read_bytes()
    value = json.loads(data)
    require(data == canonical(value) + b"\n", "NONCANONICAL_PLAN")
    require(value[digest_key] == digest({k: v for k, v in value.items()
                                       if k != digest_key}), "PLAN_DIGEST_INVALID")
    return value


def pcm_bytes(recipe):
    # Identical to the sealed generator function, checked by AST before use.
    oscillators = []
    for g in recipe["groups"]:
        for index, partial in enumerate(g["partials"]):
            seed = (g["seed"] + ":" + str(index)).encode("ascii")
            phase_word = int.from_bytes(hashlib.sha256(seed).digest()[:4], "little")
            phase = (float(phase_word) / 4294967296.0) * math.tau
            frequency = float(partial["frequency_millihz"]) / 1000.0
            numerator, denominator = partial["amplitude_ratio"]
            amplitude = float(numerator) / float(denominator)
            oscillators.append((frequency, amplitude, phase))
    encoded = bytearray(recipe["sample_count"] * 4)
    for sample_index in range(recipe["sample_count"]):
        time = float(sample_index) / float(recipe["sample_rate"])
        value = 0.0
        for frequency, amplitude, phase in oscillators:
            angle = ((math.tau * frequency) * time) + phase
            value = value + amplitude * math.sin(angle)
        if not math.isfinite(value) or not -1.0 <= value <= 1.0:
            raise ValueError("source sample outside canonical PCM domain")
        struct.pack_into("<f", encoded, sample_index * 4, value)
    return encoded


def generator_ast(path):
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    return ast.dump(next(node for node in tree.body
                         if isinstance(node, ast.FunctionDef) and node.name == "pcm_bytes"))


def main():
    output = ROOT / "reports/s2nc" / RUN_ID
    # Exclusive directory creation consumes this identity before any analysis.
    output.mkdir(exist_ok=False)
    phase = "SOURCE_BINDINGS"
    source_id = None
    ordinal = None
    attempted = returned = 0
    records = []
    bindings = {}
    profile_record = None
    failure = None
    sources_unchanged = False
    invalid_bands = []
    numpy_version = None
    try:
        execution = read_bound("execution-plan.json", "execution_digest")
        seal = read_bound("seal.json", "seal_digest")
        require(seal["seal_digest"] == SEAL_DIGEST, "SEAL_IDENTITY_INVALID")
        require(execution["execution_digest"] == seal["execution_digest"] == EXECUTION_DIGEST,
                "EXECUTION_IDENTITY_INVALID")
        require(sys.version == seal["python_version"], "PYTHON_BUILD_DIFFERS")
        bindings = dict(seal["source_hashes"])
        bindings["reports/s2nc/seal_inventory.py"] = seal["script_sha256"]
        for name, expected in PRESEAL_FILE_HASHES.items():
            relative = PRESEAL + "/" + name
            bindings[relative] = expected
        bindings[str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/")] = file_hash(Path(__file__))
        for relative, expected in bindings.items():
            require(file_hash(ROOT / relative) == expected, "BOUND_SOURCE_CHANGED")
        require(generator_ast(Path(__file__)) == generator_ast(ROOT / "reports/s2nc/seal_inventory.py"),
                "GENERATOR_AST_DIFFERS")
        require(execution["receptor_profile"] == PROFILE, "PROFILE_DIFFERS")
        sources = execution["sources"]
        require(len(sources) == 23, "SOURCE_COUNT_INVALID")
        for n, source in enumerate(sources, 1):
            source_id, ordinal = source["source_id"], n
            require(source_id == f"s{n:03d}" and source["ordinal"] == n, "SOURCE_ORDER_INVALID")
            require(source["clock_id"] == "s2nc-source-sample-clock", "SOURCE_CLOCK_INVALID")
            require((source["window_start_sample"], source["window_end_sample"])
                    == ((n - 1) * 4800, n * 4800), "SOURCE_WINDOW_INVALID")
            require(source["sample_rate"] == 48000 and source["sample_count"] == 4800
                    and source["pcm_byte_count"] == 19200, "PCM_SHAPE_INVALID")
            require(source["recipe_digest"] == digest({k: source[k] for k in RECIPE_KEYS}),
                    "RECIPE_DIGEST_INVALID")
        source_id = ordinal = None
        phase = "RECEPTOR_INIT"
        import numpy as np
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        numpy_version = np.__version__
        config = LogSpectralConfig(**execution["receptor_profile"])
        receptor = LogSpectralReceptor(config)
        require(asdict(config) == PROFILE, "ACTIVE_PROFILE_DIFFERS")
        profile_payload = {
            "config": asdict(config), "channel_ids": list(receptor.channel_ids),
            "bands": [asdict(band) for band in receptor.bands],
            "receptor_source_sha256": bindings["mcm_field_organism/log_spectral_receptor.py"],
            "method": "LogSpectralReceptor.analyze",
        }
        profile_record = {**profile_payload, "profile_digest": digest(profile_payload)}
        for source in sources:
            source_id, ordinal = source["source_id"], source["ordinal"]
            phase = "PCM_REGENERATION"
            payload = pcm_bytes({k: source[k] for k in RECIPE_KEYS})
            try:
                phase = "PCM_VALIDATION"
                require(len(payload) == source["pcm_byte_count"], "PCM_SIZE_DIFFERS")
                require(hashlib.sha256(payload).hexdigest() == source["pcm_sha256"], "PCM_DIGEST_DIFFERS")
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
            require(type(values) is tuple and len(values) == 48, "OUTPUT_DIMENSION_INVALID")
            invalid_bands = [i for i, value in enumerate(values)
                             if type(value) is not float or not math.isfinite(value)
                             or not 0.0 <= value <= 1.0]
            require(not invalid_bands, "OUTPUT_DOMAIN_INVALID")
            state = {
                "source_id": source_id, "ordinal": ordinal,
                "recipe_digest": source["recipe_digest"], "pcm_sha256": source["pcm_sha256"],
                "sample_count": 4800, "clock_id": source["clock_id"],
                "window_start_sample": source["window_start_sample"],
                "window_end_sample": source["window_end_sample"],
                "time_semantics": "DECLARED_PCM_SOURCE_WINDOW_NOT_RECEPTOR_TIMESTAMP",
                "execution_digest": EXECUTION_DIGEST,
                "profile_digest": profile_record["profile_digest"],
                "values": list(values), "values_digest": digest(list(values)),
                "values_f64le_sha256": hashlib.sha256(struct.pack("<48d", *values)).hexdigest(),
            }
            records.append({**state, "materialized_state_digest": digest(state)})
            del values
        source_id = ordinal = None
        phase = "FINAL_BINDINGS"
        require(attempted == returned == len(records) == 23, "ANALYSIS_COUNT_INVALID")
        sources_unchanged = all(file_hash(ROOT / p) == h for p, h in bindings.items())
        require(sources_unchanged, "BOUND_SOURCE_CHANGED")
    except Exception as exc:
        failure = {
            "source_id": source_id, "ordinal": ordinal, "phase": phase,
            "completed_analyses": len(records), "analyze_attempt_count": attempted,
            "analyze_return_count": returned, "exception_class": type(exc).__name__,
            "technical_detail": str(exc)[:512], "invalid_output_bands": invalid_bands,
        }
        try:
            sources_unchanged = bool(bindings) and all(file_hash(ROOT / p) == h for p, h in bindings.items())
        except OSError:
            sources_unchanged = False
    result = {
        "schema": "s2nc.receptor-materialization.v1", "run_id": RUN_ID,
        "technical_status": "RECEPTOR_MATERIALIZATION_COMPLETE" if failure is None else "NOT_EVALUABLE",
        "seal_digest": SEAL_DIGEST, "execution_digest": EXECUTION_DIGEST,
        "python_version": sys.version, "numpy_version": numpy_version,
        "input_hashes": bindings, "sources_unchanged": sources_unchanged,
        "receptor_profile": profile_record, "states": records, "failure": failure,
        "counts": {"analyze_attempt_count": attempted, "analyze_return_count": returned,
                   "completed_analyses": len(records), "receptor_values": len(records) * 48,
                   "distance_calculations": 0, "rule_calls": 0, "memory_calls": 0,
                   "context_calls": 0, "field_calls": 0, "runtime_calls": 0,
                   "pcm_payloads_persisted": 0},
    }
    result["record_digest"] = digest(result)
    data = canonical(result) + b"\n"
    require(len(data) <= MAX_RESULT_BYTES, "RESULT_SIZE_INVALID")
    temporary = output / ".result.json.tmp"
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, output / "result.json")
    print(json.dumps({"run_id": RUN_ID, "technical_status": result["technical_status"],
                      "counts": result["counts"], "failure": failure,
                      "sources_unchanged": sources_unchanged, "record_digest": result["record_digest"],
                      "file_sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}, sort_keys=True))
    return 0 if failure is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
