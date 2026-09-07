"""Read-only numeric half-scale check from stored raw values, never inverse reconstruction."""

import hashlib
import json
import math
from pathlib import Path
import struct
import sys

from tools import _s2np_private_source_binding as b
from tools import _s2np_private_receptor_materialization as m


def sha(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")
    return hashlib.sha256(data).hexdigest()


def check_root(value, key):
    m.require(value.get(key) == sha({k: v for k, v in value.items() if k != key}), "EVIDENCE_DIGEST_INVALID")


def verify_once(directory):
    out = Path(directory)
    m.require(not (out / "verification.json").exists(), "VERIFICATION_ALREADY_EXISTS")
    file_before = b.filehash(out / "result.json")
    raw_bytes = (out / "result.json").read_bytes()
    result = json.loads(raw_bytes)
    m.require(len(raw_bytes) <= b.MAX_OUTPUT_BYTES and b.canonical(result) == raw_bytes, "RESULT_FORM_INVALID")
    check_root(result, "record_digest")
    m.require(result["run_id"] == out.name == m.RUN_ID and result["execution_digest"] == m.EXECUTION_DIGEST
              and result["seal_digest"] == m.SEAL_DIGEST, "RUN_BINDING_INVALID")
    complete = result["status"] == "RECEPTOR_NJ_MATERIALIZATION_COMPLETE"
    m.require(complete or result["status"] == "NOT_EVALUABLE", "STATUS_INVALID")
    if complete:
        m.require(result["failure"] is None, "FAILURE_STATUS_INVALID")
    else:
        m.require(type(result["failure"]) is dict and type(result["failure"].get("phase")) is str,
                  "FAILURE_EVIDENCE_INVALID")
    execution = m.read_root(m.PRESEAL / "execution-plan.json", "execution_digest")
    m.require(execution["execution_digest"] == m.EXECUTION_DIGEST, "PLAN_CHANGED")
    before = result["source_hashes_before"]
    m.require(before == result["source_hashes_after"] and all(b.filehash(b.ROOT / p) == h for p, h in before.items()),
              "INPUT_FILES_CHANGED")
    if complete:
        m.require(before == m.watched(), "INPUT_INVENTORY_INVALID")
    if (out / "preregistration.json").exists():
        pre = json.loads((out / "preregistration.json").read_bytes())
        m.require(pre["source_hashes"] == before and pre["run_id"] == result["run_id"]
                  and pre["execution_digest"] == result["execution_digest"] and pre["seal_digest"] == result["seal_digest"]
                  and pre["source_order"] == execution["source_order"] and pre["profiles"] == execution["profiles"],
                  "PREREGISTRATION_INVALID")
    else:
        m.require(not complete and result["counts"]["analyze_attempts"] == 0, "PREREGISTRATION_MISSING")
    profile = result["profile"]
    if profile is not None:
        check_root(profile, "profile_digest")
        m.require(profile["bound_profiles"] == execution["profiles"] == b.profile_binding()
                  and profile["config"] == execution["profiles"]["raw"]["config"], "PROFILE_INVALID")
        m.require(len(profile["carriers"]) == len(profile["bands"]) == 48, "CARRIER_FORM_INVALID")
    checked = 0
    for source, row in zip(execution["sources"], result["states"]):
        check_root(row, "materialized_state_digest")
        for key in ("source_id", "ordinal", "source_digest", "recipe_digest", "pcm_sha256", "clock_id"):
            m.require(row[key] == source[key], "SOURCE_BINDING_INVALID")
        m.require(row["payload_hash_checked_before_analysis"] is True, "PAYLOAD_CHECK_ORDER_INVALID")
        state, projection = row["raw_state"], row["projection"]
        m.require(sha(state) == row["raw_state_digest"], "RAW_STATE_DIGEST_INVALID")
        check_root(projection, "projection_digest")
        m.require(len(b.canonical(projection)) <= 16384, "NJ_SIZE_INVALID")
        raw, half = state["energy"], projection["values"]
        m.require(type(raw) is list and type(half) is list and len(raw) == len(half) == 48
                  and all(type(v) is float and math.isfinite(v) and v >= 0 for v in raw)
                  and all(type(v) is float and math.isfinite(v) and 0 <= v <= 1 for v in half), "VALUE_FORM_INVALID")
        for name in ("snapshot_index", "window_start_sample", "window_end_sample"):
            m.require(type(state[name]) is int and state[name] == source[name], "RAW_TIME_INVALID")
        m.require(state["modality_id"] == "auditory" and state["geometry_id"] == execution["profiles"]["raw"]["geometry_id"]
                  and state["carrier_ids"] == projection["carrier_ids"] == profile["carriers"], "RAW_GEOMETRY_INVALID")
        m.require(state["contact"] == ("active_energy" if any(v != 0 for v in raw) else "active_zero"), "ACTIVITY_FLAG_INVALID")
        m.require(projection["source_state_digest"] == row["raw_state_digest"]
                  and projection["source_values_digest"] == row["raw_values_digest"] == sha(raw)
                  and projection["source_profile_digest"] == execution["profiles"]["raw_profile_digest"]
                  and projection["profile_digest"] == execution["profiles"]["half_profile_digest"]
                  and projection["profile_id"] == execution["profiles"]["half"]["profile_id"]
                  and projection["geometry_id"] == execution["profiles"]["half"]["geometry_id"], "PROJECTION_BINDING_INVALID")
        m.require(projection["clock_id"] == source["clock_id"]
                  and projection["snapshot_index"] == source["snapshot_index"]
                  and projection["window_start_tick"] == source["window_start_sample"]
                  and projection["window_end_tick"] == source["window_end_sample"], "PROJECTION_TIME_INVALID")
        m.require(row["raw_values_hex"] == [v.hex() for v in raw] and row["half_values_hex"] == [v.hex() for v in half],
                  "BINARY64_HEX_INVALID")
        for values, key in ((raw, "raw_values_f64le_sha256"), (half, "half_values_f64le_sha256")):
            m.require(hashlib.sha256(struct.pack("<48d", *values)).hexdigest() == row[key], "BINARY_DIGEST_INVALID")
        # Independent forward arithmetic only; no NJ function or raw = half*2.
        for x, z in zip(raw, half, strict=True):
            m.require(struct.pack("<d", x * 0.5) == struct.pack("<d", z), "HALF_MULTIPLICATION_DIFFERS")
            checked += 1
        m.require(row["raw_subnormal_band_indices"] == [i for i, x in enumerate(raw) if 0 < x < sys.float_info.min]
                  and projection["subnormal_band_indices"] == [i for i, z in enumerate(half) if 0 < z < sys.float_info.min]
                  and projection["underflow_band_indices"] == [i for i, (x, z) in enumerate(zip(raw, half)) if x > 0 and z == 0],
                  "NUMERIC_MARKERS_INVALID")
    c = result["counts"]
    m.require(all(type(n) is int and n >= 0 for n in c.values()), "COUNTER_FORM_INVALID")
    m.require(c["completed_sources"] == len(result["states"]) <= c["nj_returns"] <= c["nj_attempts"]
              <= c["analyze_returns"] <= c["analyze_attempts"] <= c["payloads_validated"] <= c["generation_attempts"] <= 12,
              "PROGRESS_INVALID")
    if complete:
        m.require(all(c[k] == 12 for k in ("generation_attempts", "payloads_validated", "analyze_attempts", "analyze_returns",
                                          "nj_attempts", "nj_returns", "completed_sources"))
                  and c["raw_value_count"] == c["half_value_count"] == checked == 576, "COUNTERS_INVALID")
    for k in ("rolling_hops", "contact_frame_calls", "pcm_payloads_persisted", "distance_calls", "mask_comparison_calls",
              "rule_calls", "memory_calls", "context_calls", "field_calls", "runtime_calls"):
        m.require(c[k] == 0, "FORBIDDEN_CALLS")
    m.require(result["main_gate_after"] is False and result["source_gate_after"] is False and not m.MAIN_GATE and not b.MAIN_GATE,
              "GATE_INVALID")
    file_after = b.filehash(out / "result.json")
    m.require(file_before == file_after, "RESULT_CHANGED")
    verification = b.sealed(dict(run_id=m.RUN_ID, status="S2NP_MATERIALIZATION_VALID" if complete else "TECHNICAL_FAILURE_RECORDED",
        verification_calls=1, read_only=True, record_digest=result["record_digest"], file_sha256_before=file_before,
        file_sha256_after=file_after, materialized_sources=len(result["states"]), half_values_checked=checked,
        numeric_checks=["finite_domains", "stored_binary64_hex_and_bytes", "forward_raw_times_half_bitwise",
                        "raw_and_half_subnormals", "positive_raw_underflow_to_zero"],
        binding_checks=["sources_and_payload_hash_links", "native_time", "profile_and_carriers", "raw_state_and_projection_digests",
                        "code_hashes", "counts", "record_size_and_immutability"],
        payload_regeneration_calls=0, receptor_calls=0, nj_projection_calls=0,
        fft_filterbank_recomputed=False, pcm_hash_recomputed=False,
        raw_reconstructed_from_half=False, distance_calls=0, comparison_calls=0), "verification_digest")
    b.publish(out / "verification.json", verification, b.MAX_METADATA_BYTES)
    return verification
