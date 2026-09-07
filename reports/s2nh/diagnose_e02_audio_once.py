"""One authorized audio-only reproduction; no NH main entry or contact creation."""

import ast
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "s2nh-e02-audio-endpoint-diagnostic-20260907-01"
OUT = ROOT / "reports/s2nh" / RUN_ID
PRESEAL = "reports/s2nh/s2nh-source-preseal-20260906-01/"
QUAL = "reports/s2nh/s2nh-runtime-binding-qualification-20260906-01/result.json"
HISTORY = "reports/s2nh/s2nh-runtime-comparison-20260907-01/recording.json"
GATES = ("tools/_s2nh_private_runtime_binding.py", "tools/_s2ng_private_runtime_comparison.py")
PINS = {
    PRESEAL + "execution-plan.json": "776ddf73bcbd9f61ad64612bc7bfb0ddeaebb6c233026e9831a2bfdd5a607826",
    PRESEAL + "seal.json": "65bb79bc8c0e65b433a1a9f5bb84969970e440a51745a85af8883e1dc99838bd",
    QUAL: "bd966c1672127cce85e48c72a7b0c0ca520be1140918bcb8555b85ec49468993",
    HISTORY: "20f1096586590aa6492836f9d3ad9beb3f51d4fe4e49d32fa17e6757c0dda9ee",
}
OWN = ("reports/s2nh/diagnose_e02_audio_once.py", "reports/s2nh/verify_e02_audio_diagnostic.py",
       "mcm_field_organism/receptor_contract.py", "mcm_field_organism/carrier_baselines.py",
       "mcm_field_organism/controlled_audio_source.py")
LIMITS = dict(audio_windows=2, audio_hops=20, rolling_outputs=11, endpoint_values=96,
              max_live_pcm_payloads=1, max_pcm_bytes=19200, max_record_bytes=131072)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def filehash(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def require(ok, code):
    if not ok:
        raise ValueError(code)


def publish(path, value):
    data = canonical(value)
    require(len(data) <= LIMITS["max_record_bytes"], "DIAGNOSTIC_SIZE_LIMIT")
    pending = path.with_suffix(".pending")
    with pending.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.link(pending, path)
    pending.unlink()


def gate_bindings():
    result = {}
    for name in GATES:
        nodes = ast.parse((ROOT / name).read_text(encoding="utf-8")).body
        values = [ast.literal_eval(n.value) for n in nodes if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "MAIN_GATE" for t in n.targets)]
        require(values == [False] and name[:-3].replace("/", ".") not in sys.modules,
                "MAIN_GATE_OR_IMPORT_INVALID")
        result[name] = False
    return result


def endpoint(state, event, source):
    part = event["auditory"]
    require((state.snapshot_index, state.window_start_sample, state.window_end_sample) ==
            (part["endpoint_snapshot_index"], part["start_tick"], part["end_tick"]), "ENDPOINT_TIME_INVALID")
    require(state.modality_id == "auditory" and len(state.energy) == len(state.carrier_ids) == 48
            and len(set(state.carrier_ids)) == 48, "ENDPOINT_FORM_INVALID")
    rows = []
    for i, v in enumerate(state.energy):
        require(type(v) is float, "ENDPOINT_VALUE_TYPE_INVALID")
        finite = math.isfinite(v)
        kind = "FINITE" if finite else "NAN" if math.isnan(v) else "POS_INF" if v > 0 else "NEG_INF"
        rows.append(dict(band_index=i, carrier_id=state.carrier_ids[i], kind=kind,
                         value=v if finite else None, binary64_hex=v.hex() if finite else None,
                         binary64_bits_be=struct.pack(">d", v).hex(), is_finite=finite, abs_gt_one=abs(v) > 1.0))
    payload = dict(event_id=event["event_id"], ordinal=event["ordinal"], source=source,
                   event_digest=digest(event), time_binding=part, field_clock_metadata=event["field_clock_id"],
                   modality_id=state.modality_id, geometry_id=state.geometry_id,
                   snapshot_index=state.snapshot_index, window_start_sample=state.window_start_sample,
                   window_end_sample=state.window_end_sample, hearing_activity=state.contact.value, values=rows,
                   nonfinite_band_indices=[r["band_index"] for r in rows if not r["is_finite"]],
                   abs_gt_one_band_indices=[r["band_index"] for r in rows if r["abs_gt_one"]])
    return {**payload, "diagnostic_endpoint_digest": digest(payload)}


def main():
    OUT.mkdir(exist_ok=False)
    phase, source_id, ordinal = "BINDINGS", None, None
    counters = dict(payload_generations=0, payload_hashes_verified=0, audio_windows=0,
                    hop_calls=0, audio_hops=0, rolling_outputs=0)
    record = dict(schema="s2nh.e02-audio-diagnostic.v1", run_id=RUN_ID, status="NOT_EVALUABLE",
                  outcome=None, failure=None, diagnostic_calls=1, limits=LIMITS, counters=counters,
                  endpoints=[], profile=None, generator_identity=None, execution_digest=None,
                  hashes_before={}, hashes_after={}, gates_before=None, gates_after=None,
                  calls_excluded=dict(video=0, receptor_contact=0, memory=0, field=0, context=0, runtime=0),
                  scope="NEW_REPRODUCTION_ONLY_NOT_HISTORICAL_ENDPOINT_RECOVERY")
    try:
        require(all(filehash(ROOT / p) == h for p, h in PINS.items()), "PIN_INVALID")
        plan = json.loads((ROOT / (PRESEAL + "execution-plan.json")).read_bytes())
        seal = json.loads((ROOT / (PRESEAL + "seal.json")).read_bytes())
        require(digest({k: v for k, v in plan.items() if k != "execution_digest"}) == plan["execution_digest"]
                == seal["execution_digest"], "PLAN_DIGEST_INVALID")
        q = json.loads((ROOT / QUAL).read_bytes())
        require(q["status"] == "S2NH_RUNTIME_BINDING_QUALIFIED" and q["hashes_before"] == q["hashes_after"],
                "QUALIFICATION_BINDING_INVALID")
        expected = {**plan["source_hashes"], **q["hashes_after"], **PINS}
        require(all(filehash(ROOT / p) == h for p, h in expected.items()), "CODE_BINDING_INVALID")
        before = {p: filehash(ROOT / p) for p in sorted(set(expected) | set(OWN) | set(GATES))}
        record.update(hashes_before=before, execution_digest=plan["execution_digest"], profile=plan["profile"],
                      gates_before=gate_bindings())
        from tools import _s2nh_private_source_binding as generator
        require(generator.identity() == plan["generator_identity"], "GENERATOR_IDENTITY_INVALID")
        record["generator_identity"] = plan["generator_identity"]
        events = plan["events"][:2]
        require([(e["event_id"], e["auditory"]["source_id"]) for e in events] ==
                [("e01", "nh-a00"), ("e02", "nh-a01")], "EVENT_SELECTION_INVALID")
        sources = {s["source_id"]: s for s in plan["sources"]}
        publish(OUT / "preregistration.json", dict(run_id=RUN_ID, hashes=before, limits=LIMITS,
                gates=record["gates_before"], execution_digest=plan["execution_digest"],
                generator_identity=record["generator_identity"], profile=plan["profile"],
                audio_events=[dict(event_id=e["event_id"], ordinal=e["ordinal"], auditory=e["auditory"],
                                   event_digest=digest(e)) for e in events]))
        phase = "HEARING_INIT"
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
        import numpy as np
        config = LogSpectralConfig()
        require(asdict(config) == plan["profile"]["auditory"], "PROFILE_INVALID")
        hearing = BroadbandHearingPath(LogSpectralReceptor(config))
        for event in events:
            ordinal, source_id = event["ordinal"], event["auditory"]["source_id"]
            s = sources[source_id]
            phase = "SOURCE_BINDING"
            require(s["kind"] == "PCM" and digest(s["recipe"]) == s["recipe_digest"]
                    and digest({k: v for k, v in s.items() if k != "source_digest"}) == s["source_digest"],
                    "SOURCE_DIGEST_INVALID")
            require(hearing.input_chunks == event["auditory"]["hop_start"], "HOP_CONTINUITY_INVALID")
            phase = "PAYLOAD_GENERATION"
            counters["payload_generations"] += 1
            payload = generator.pcm_payload(s["recipe"])
            try:
                phase = "PAYLOAD_HASH"
                require(len(payload) == s["byte_count"] == 19200 and
                        hashlib.sha256(payload).hexdigest() == s["payload_sha256"], "PAYLOAD_HASH_INVALID")
                counters["payload_hashes_verified"] += 1
                samples = np.frombuffer(payload, dtype="<f4")
                try:
                    phase = "AUDIO_HOPS"
                    for hop in range(10):
                        counters["hop_calls"] += 1
                        state = hearing.push(tuple(float(v) for v in samples[hop*480:(hop+1)*480]))
                        counters["audio_hops"] = hearing.input_chunks
                        counters["rolling_outputs"] = hearing.snapshot_count
                finally:
                    del samples
            finally:
                del payload
            counters["audio_windows"] += 1
            phase = "ENDPOINT_BEFORE_CONTACT"
            require(state is not None, "ENDPOINT_MISSING")
            record["endpoints"].append(endpoint(state, event, s))
            del state
        del hearing
        last = record["endpoints"][-1]
        record["outcome"] = ("CONTACT_NORMALFORM_VIOLATION_REPRODUCED" if
            last["nonfinite_band_indices"] or last["abs_gt_one_band_indices"] else "NOT_REPRODUCED")
        record["status"] = "DIAGNOSIS_COMPLETE"
    except Exception as exc:
        record.update(status="NOT_EVALUABLE", outcome=None,
                      failure=dict(phase=phase, source_id=source_id, ordinal=ordinal,
                                   error_class=type(exc).__name__, code="DIAGNOSTIC_TECHNICAL_ERROR"))
    record["hashes_after"] = {p: filehash(ROOT / p) for p in record["hashes_before"]}
    record["gates_after"] = gate_bindings()
    if record["hashes_before"] != record["hashes_after"]:
        record.update(status="NOT_EVALUABLE", outcome=None,
                      failure=dict(phase="FINAL_BINDINGS", source_id=source_id, ordinal=ordinal,
                                   error_class="ValueError", code="CODE_CHANGED"))
    record["record_digest"] = digest(record)
    publish(OUT / "recording.json", record)
    print(json.dumps(dict(run_id=RUN_ID, status=record["status"], outcome=record["outcome"],
                          counters=counters, failure=record["failure"])))
    return 0 if record["status"] == "DIAGNOSIS_COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
