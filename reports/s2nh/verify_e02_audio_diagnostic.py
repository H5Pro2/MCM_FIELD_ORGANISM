"""Independent stdlib-only reader. No source generation or receptor imports."""

import hashlib
import json
import math
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "s2nh-e02-audio-endpoint-diagnostic-20260907-01"
OUT = ROOT / "reports/s2nh" / RUN_ID
PLAN = ROOT / "reports/s2nh/s2nh-source-preseal-20260906-01/execution-plan.json"
PLAN_SHA = "776ddf73bcbd9f61ad64612bc7bfb0ddeaebb6c233026e9831a2bfdd5a607826"


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("ascii")


def sha(v):
    return hashlib.sha256(v).hexdigest()


def reject_constant(v):
    raise ValueError("NON_JSON_NUMBER")


def load(path):
    return json.loads(path.read_bytes(), parse_constant=reject_constant)


def check(ok, code):
    if not ok:
        raise ValueError(code)


def main():
    # Exclusive reservation prevents a second verification of this diagnosis.
    with (OUT / "verification-reservation.json").open("xb") as f:
        f.write(canonical(dict(run_id=RUN_ID, verification_calls=1, receptor_calls=0)))
    path = OUT / "recording.json"
    before = path.read_bytes()
    result = dict(run_id=RUN_ID, verification_calls=1, receptor_calls=0, payload_generations=0,
                  read_only=True, evidence_valid=False, error=None, record_file_sha256=sha(before))
    try:
        r = load(path)
        check(r["record_digest"] == sha(canonical({k: v for k, v in r.items() if k != "record_digest"})), "RECORD_DIGEST")
        check(r["run_id"] == RUN_ID and r["schema"] == "s2nh.e02-audio-diagnostic.v1"
              and r["diagnostic_calls"] == 1, "IDENTITY")
        check(sha(PLAN.read_bytes()) == PLAN_SHA, "PLAN_FILE")
        plan = load(PLAN)
        check(r["execution_digest"] == plan["execution_digest"] and r["profile"] == plan["profile"]
              and r["generator_identity"] == plan["generator_identity"], "SOURCE_PROFILE_IDENTITY")
        pre = load(OUT / "preregistration.json")
        check(pre["limits"] == r["limits"] == dict(audio_windows=2, audio_hops=20, rolling_outputs=11,
              endpoint_values=96, max_live_pcm_payloads=1, max_pcm_bytes=19200, max_record_bytes=131072), "LIMIT_BINDING")
        check(pre["execution_digest"] == plan["execution_digest"] and pre["profile"] == plan["profile"]
              and pre["generator_identity"] == plan["generator_identity"] and pre["audio_events"] ==
              [dict(event_id=e["event_id"], ordinal=e["ordinal"], auditory=e["auditory"],
                    event_digest=sha(canonical(e))) for e in plan["events"][:2]], "PREREGISTRATION")
        check(pre["run_id"] == RUN_ID and pre["hashes"] == r["hashes_before"] == r["hashes_after"]
              and bool(pre["hashes"]), "CODE_BINDINGS")
        for p, h in pre["hashes"].items():
            with (ROOT / p).open("rb") as f:
                check(hashlib.file_digest(f, "sha256").hexdigest() == h, "CODE_FILE")
        check(pre["gates"] == r["gates_before"] == r["gates_after"] and
              len(r["gates_after"]) == 2 and all(v is False for v in r["gates_after"].values()), "GATES")
        check(r["calls_excluded"] == dict(video=0, receptor_contact=0, memory=0, field=0, context=0, runtime=0), "EXCLUDED_CALLS")
        check(r["scope"] == "NEW_REPRODUCTION_ONLY_NOT_HISTORICAL_ENDPOINT_RECOVERY", "HISTORICAL_BOUNDARY")
        c = r["counters"]
        for k, upper in dict(payload_generations=2, payload_hashes_verified=2, audio_windows=2,
                             hop_calls=20, audio_hops=20, rolling_outputs=11).items():
            check(type(c[k]) is int and 0 <= c[k] <= upper, "COUNTERS")
        check(c["audio_windows"] <= c["payload_hashes_verified"] <= c["payload_generations"]
              and c["audio_hops"] <= c["hop_calls"] and c["rolling_outputs"] == max(0, c["audio_hops"]-9), "PROGRESS")
        sources = {s["source_id"]: s for s in plan["sources"]}
        check(len(r["endpoints"]) <= c["audio_windows"] <= 2 and len(before) <= 131072, "SIZE")
        for i, ep in enumerate(r["endpoints"]):
            event = plan["events"][i]
            part = event["auditory"]
            check(ep["diagnostic_endpoint_digest"] == sha(canonical({k: v for k, v in ep.items()
                       if k != "diagnostic_endpoint_digest"})), "ENDPOINT_DIGEST")
            check(ep["event_id"] == event["event_id"] and ep["ordinal"] == i+1
                  and ep["event_digest"] == sha(canonical(event)) and ep["time_binding"] == part
                  and ep["source"] == sources[part["source_id"]]
                  and ep["field_clock_metadata"] == event["field_clock_id"], "ENDPOINT_SOURCE")
            check((ep["snapshot_index"], ep["window_start_sample"], ep["window_end_sample"]) ==
                  (i*10, i*4800, (i+1)*4800) and part["clock_id"] == "audio.sample", "NATIVE_TIME")
            check(ep["modality_id"] == "auditory" and ep["geometry_id"] == "auditory.log48.50-18000.w4800.h480.v1"
                  and len(ep["values"]) == 48 and len({v["carrier_id"] for v in ep["values"]}) == 48, "GEOMETRY")
            nonfinite, outside = [], []
            for j, v in enumerate(ep["values"]):
                check(v["band_index"] == j, "BAND_ORDER")
                number = struct.unpack(">d", bytes.fromhex(v["binary64_bits_be"]))[0]
                finite = math.isfinite(number)
                kind = "FINITE" if finite else "NAN" if math.isnan(number) else "POS_INF" if number > 0 else "NEG_INF"
                check(v["kind"] == kind and v["is_finite"] is finite and v["abs_gt_one"] is (abs(number) > 1.0), "VALUE_FLAGS")
                if finite:
                    check(type(v["value"]) is float and struct.pack(">d", v["value"]).hex() == v["binary64_bits_be"]
                          and v["binary64_hex"] == number.hex(), "BINARY64_VALUE")
                else:
                    nonfinite.append(j)
                    check(v["value"] is None and v["binary64_hex"] is None, "NONFINITE_ENCODING")
                if abs(number) > 1.0:
                    outside.append(j)
            check(ep["nonfinite_band_indices"] == nonfinite and ep["abs_gt_one_band_indices"] == outside, "PREDICATES")
            check(ep["hearing_activity"] == ("active_energy" if any(
                  struct.unpack(">d", bytes.fromhex(v["binary64_bits_be"]))[0] != 0.0
                  for v in ep["values"]) else "active_zero"), "HEARING_ACTIVITY")
        if r["status"] == "DIAGNOSIS_COMPLETE":
            check(r["failure"] is None and len(r["endpoints"]) == 2 and c == dict(payload_generations=2,
                  payload_hashes_verified=2, audio_windows=2, hop_calls=20, audio_hops=20, rolling_outputs=11), "COMPLETENESS")
            last = r["endpoints"][-1]
            expected = "CONTACT_NORMALFORM_VIOLATION_REPRODUCED" if last["nonfinite_band_indices"] or last["abs_gt_one_band_indices"] else "NOT_REPRODUCED"
            check(r["outcome"] == expected, "OUTCOME")
        else:
            check(r["status"] == "NOT_EVALUABLE" and r["outcome"] is None and isinstance(r["failure"], dict)
                  and r["failure"]["phase"] in ("BINDINGS", "HEARING_INIT", "SOURCE_BINDING", "PAYLOAD_GENERATION",
                      "PAYLOAD_HASH", "AUDIO_HOPS", "ENDPOINT_BEFORE_CONTACT", "FINAL_BINDINGS"), "FAILURE")
        result.update(evidence_valid=True, status=r["status"], record_digest=r["record_digest"])
    except Exception as exc:
        result["error"] = dict(error_class=type(exc).__name__, code="DIAGNOSTIC_EVIDENCE_INVALID")
    result["file_unchanged"] = path.read_bytes() == before
    result["evidence_valid"] = result["evidence_valid"] and result["file_unchanged"]
    result["verification_digest"] = sha(canonical(result))
    with (OUT / "verification.json").open("xb") as f:
        f.write(canonical(result))
    print(json.dumps(result))
    return 0 if result["evidence_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
