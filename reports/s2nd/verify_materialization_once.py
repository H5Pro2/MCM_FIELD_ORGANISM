"""Independent read-only S2-ND artifact check; no generator or receptor imports."""

import hashlib
import json
import math
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "s2nd-receptor-materialization-20260906-01"
OUT = ROOT / "reports/s2nd" / RUN_ID
PRESEAL = ROOT / "reports/s2nd/s2nd-source-panel-preseal-20260906-02"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def check(condition, code):
    if not condition:
        raise ValueError(code)


def check_record(value, key):
    check(value[key] == digest({k: v for k, v in value.items() if k != key}), key + "_INVALID")


def main():
    with (OUT / "verification-invocation.json").open("x", encoding="ascii") as handle:
        json.dump({"run_id": RUN_ID, "verification_invocations": 1}, handle)
    receipt = {"run_id": RUN_ID, "read_only": True, "pcm_regenerations": 0, "receptor_repetitions": 0,
               "distance_calculations": 0}
    try:
        raw = (OUT / "result.json").read_bytes()
        result = json.loads(raw)
        check(raw == canonical(result), "CANONICAL_RESULT_INVALID")
        check_record(result, "record_digest")
        plan_raw = (ROOT / "reports/s2nd/s2nd-receptor-materialization-call-plan.json").read_bytes()
        plan = json.loads(plan_raw)
        check(plan["run_id"] == result["run_id"] == RUN_ID and result["call_plan_sha256"] == hashlib.sha256(plan_raw).hexdigest(),
              "CALL_BINDING_INVALID")
        for name, expected in plan["source_hashes_before"].items():
            check(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, "SOURCE_HASH_INVALID")
        check(result["input_hashes"] == result["source_hashes_after"] == plan["source_hashes_before"]
              and result["sources_unchanged"] is True, "SOURCE_BINDINGS_INVALID")
        execution = json.loads((PRESEAL / "execution-plan.json").read_bytes())
        seal = json.loads((PRESEAL / "seal.json").read_bytes())
        check_record(execution, "execution_digest")
        check_record(seal, "seal_digest")
        check(result["execution_digest"] == execution["execution_digest"] == seal["execution_digest"]
              and result["seal_digest"] == seal["seal_digest"], "ROOT_BINDING_INVALID")
        counts, states, profile = result["counts"], result["states"], result["receptor_profile"]
        check(0 <= len(states) <= counts["analyze_return_count"] <= counts["analyze_attempt_count"] <= 18,
              "COUNT_ORDER_INVALID")
        check(counts["completed_analyses"] == len(states) and counts["receptor_values"] == 48 * len(states), "COUNTERS_INVALID")
        check(all(counts[k] == 0 for k in ("distance_calculations", "rule_calls", "memory_calls", "context_calls",
                                          "field_calls", "runtime_calls", "pcm_payloads_persisted")), "SCOPE_INVALID")
        if profile is not None:
            check_record(profile, "profile_digest")
            check(profile["config"] == execution["receptor_profile"]
                  and profile["config_digest"] == execution["receptor_profile_digest"] == digest(profile["config"])
                  and profile["method"] == "LogSpectralReceptor.analyze"
                  and profile["receptor_source_sha256"] == plan["source_hashes_before"]["mcm_field_organism/log_spectral_receptor.py"],
                  "PROFILE_INVALID")
            check(len(profile["channel_ids"]) == len(set(profile["channel_ids"])) == len(profile["bands"]) == 48,
                  "CHANNELS_INVALID")
            check(profile["channel_ids"] == [b["channel_id"] for b in profile["bands"]], "BANDS_INVALID")
        for i, state in enumerate(states, 1):
            source = execution["sources"][i - 1]
            check_record(state, "materialized_state_digest")
            check(state["ordinal"] == source["ordinal"] == i and state["source_id"] == source["source_id"] == f"s{i:03d}",
                  "STATE_ORDER_INVALID")
            for key in ("recipe_digest", "pcm_sha256", "clock_id", "window_start_sample", "window_end_sample", "sample_count"):
                check(state[key] == source[key], "STATE_SOURCE_INVALID")
            check(state["payload_validated_before_analysis"] is True and state["execution_digest"] == execution["execution_digest"]
                  and state["profile_digest"] == profile["profile_digest"], "STATE_PARENT_INVALID")
            values = state["values"]
            check(type(values) is list and len(values) == 48 and all(type(v) is float and math.isfinite(v) and 0.0 <= v <= 1.0 for v in values),
                  "VALUE_DOMAIN_INVALID")
            check(state["values_digest"] == digest(values)
                  and state["values_f64le_sha256"] == hashlib.sha256(struct.pack("<48d", *values)).hexdigest(), "VALUES_DIGEST_INVALID")
        if result["technical_status"] == "RECEPTOR_MATERIALIZATION_COMPLETE":
            check(result["failure"] is None and len(states) == counts["analyze_attempt_count"] == counts["analyze_return_count"] == 18,
                  "COMPLETION_INVALID")
            status = "MATERIALIZATION_EVIDENCE_VALID"
        else:
            check(result["technical_status"] == "NOT_EVALUABLE" and type(result["failure"]) is dict
                  and result["failure"]["completed_analyses"] == len(states), "FAILURE_FORM_INVALID")
            status = "NOT_EVALUABLE_RECORD_INTEGRITY_VALID"
        check((OUT / "result.json").read_bytes() == raw, "RESULT_MUTATED")
        receipt.update(verification_status=status, record_digest=result["record_digest"],
                       result_file_sha256=hashlib.sha256(raw).hexdigest(), state_count=len(states), value_count=48 * len(states),
                       result_unchanged=True, source_hashes_unchanged=True)
        code = 0
    except Exception as error:
        receipt.update(verification_status="NOT_EVALUABLE", error_class=type(error).__name__, error_code=str(error))
        code = 1
    receipt["verification_digest"] = digest(receipt)
    with (OUT / "verification.json").open("xb") as handle:
        handle.write(canonical(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
