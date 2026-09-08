"""Independent offline NS source-binding inspection; no payload regeneration."""
import hashlib
import json
from pathlib import Path

from tools import _s2ns_private_source_binding as b


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False).encode("ascii")).hexdigest()


def root(value, key):
    b.require(type(value) is dict and value.get(key) == sha({k:v for k,v in value.items() if k != key}), "ROOT_DIGEST_INVALID")


def check_plans(x, y):
    root(x, "execution_digest")
    root(y, "evaluation_digest")
    b.require(y["execution_digest"] == x["execution_digest"], "ROOT_LINK_INVALID")
    b.require(x["contract_sha256"] == y["contract_sha256"] == b.PINS[b.CONTRACT], "CONTRACT_INVALID")
    specs = b.source_specs()
    b.require(x["source_order"] == [s.source_id for s in specs] and len(x["sources"]) == 18, "SOURCE_ORDER_INVALID")
    for spec, row in zip(specs, x["sources"], strict=True):
        root(row, "source_digest")
        b.require(row == b.bind_source(spec, row["payload_sha256"]), "SOURCE_FORM_INVALID")
    events = x["events"]
    b.require(len(events) == 31 and [e["ordinal"] for e in events] == list(range(1, 32)), "EVENT_ORDER_INVALID")
    b.require([e["ordinal"] for e in events if e["event_type"] == b.A] ==
        [3,4,5,6,7,9,10,11,12,13,27,28,29,30,31], "EVENT_KIND_INVALID")
    for i, e in enumerate(events):
        n = i + 1
        a, v = e["auditory"], e["visual"]
        history = "h01" if n <= 7 else "h02" if n <= 13 else "h03"
        b.require(e["history_id"] == history and e["starts_fresh_history"] is (n in (1, 8, 14)), "HISTORY_INVALID")
        b.require((a["clock_id"], a["start_tick"], a["end_tick"], a["endpoint_snapshot_index"])
            == ("audio.sample", 4800*i, 4800*n, i), "AUDIO_TIME_INVALID")
        b.require(a["common_window"] == [100000000*n-10000000, 100000000*n]
            and e["pairing_clock_id"] == "s2ns-pairing-clock", "COMMON_TIME_INVALID")
        b.require((v is None) == (e["event_type"] == b.A), "MODALITY_FORM_INVALID")
        if v is not None:
            b.require((v["clock_id"], v["start_tick"], v["end_tick"]) == ("video.frame", 3*n-1, 3*n)
                and v["common_window"] == [(3*n-1)*1000000000//30, 100000000*n], "VISUAL_TIME_INVALID")
    for row, name, indices in zip(x["views"], ("LOWER_24", "UPPER_24"), (list(range(24)), list(range(24,48))), strict=True):
        b.require(row == dict(view_id=name, indices=indices, complement=[i for i in range(48) if i not in indices]), "VIEW_INVALID")
    b.require(x == b.execution_plan(x["sources"], x["environment"], x["source_hashes"], x["generators"]), "EXECUTION_FORM_INVALID")
    expected = []
    for history, first, area in (("h01",3,"A_RECENT"),("h02",9,"ABSTAIN"),("h03",27,"B_STABLE_AUDITORY")):
        for i, sub in enumerate(("EXACT","LEVEL","FREQUENCY","MIXED_CONTROL","INDEPENDENT_CONTROL")):
            expected.append(dict(event_id=f"e{first+i:02d}", history_id=history, cue_id=f"ns-a{i+3:02d}",
                target="ns-a01" if i < 3 else None, subtype=sub, prediction=area if i < 3 else "ABSTAIN"))
    b.require(y["cases"] == expected and y == b.evaluation_plan(x), "EVALUATION_FORM_INVALID")
    b.require(not any(k in json.dumps(x) for k in ('"target"','"prediction"','"subtype"','"retention_identity"')), "EVALUATION_LEAK")
    b.require(all(len(b.canonical(p)) <= b.MAX_METADATA_BYTES for p in (x, y)), "METADATA_SIZE_EXCEEDED")


def verify_once(directory):
    out = Path(directory)
    target, claim = out / "verification.json", out / "verification.claim"
    b.require(not target.exists(), "VERIFICATION_ALREADY_EXISTS")
    with claim.open("xb") as handle:
        handle.write(b"s2ns-read-only-preseal-once-v1")
    names = ("execution-plan.json", "evaluation-plan.json", "seal.json", "preregistration.json")
    before = {n:b.filehash(out/n) for n in names}
    x,y,z,p = [json.loads((out/n).read_bytes()) for n in names]
    check_plans(x,y)
    root(z, "seal_digest")
    b.require(z["run_id"] == p["run_id"] == out.name and z["status"] == "S2NS_SOURCES_PRESEALED", "RUN_BINDING_INVALID")
    b.require(z["execution_digest"] == x["execution_digest"] and z["evaluation_digest"] == y["evaluation_digest"]
        and z["execution_file_sha256"] == before[names[0]] and z["evaluation_file_sha256"] == before[names[1]], "SEAL_LINK_INVALID")
    b.require(z["hashes_before"] == z["hashes_after"] == x["source_hashes"] == p["hashes"] == b.watched(), "SOURCE_FILES_CHANGED")
    b.require(x["environment"] == p["environment"] == b.environment(), "ENVIRONMENT_CHANGED")
    _, _, gen = b.generators()  # Read/compile definition identities, do not call generators.
    b.require(gen == x["generators"] == p["generators"], "GENERATOR_BINDING_INVALID")
    b.require(p["specs"] == [s.payload() for s in b.source_specs()] and p["events"] == x["events"]
        and p["profiles"] == x["profiles"] and p["budgets"] == b.budgets() and p["retry"] is False
        and p["qualification_sha256"] == b.filehash(b.QUAL_DIR/"result.json"), "PREREGISTRATION_INVALID")
    for k, v in dict(attempted_sources=18, completed_sources=18, generated_pcm_sources=7, generated_rgb_sources=11,
        generated_pcm_bytes=134400, generated_rgb_bytes=68428800, max_live_pcm_payloads=1, max_live_rgb_payloads=1).items():
        b.require(type(z[k]) is int and z[k] == v, "COUNTER_INVALID")
    for k in ("raw_payloads_persisted","receptor_calls","nj_calls","distance_calls","memory_calls","context_calls","field_calls","runtime_calls"):
        b.require(type(z[k]) is int and z[k] == 0, "FORBIDDEN_EXECUTION")
    a, c = x["sources"][0], x["sources"][2]
    b.require(a["payload_sha256"] == c["payload_sha256"] and a["source_digest"] != c["source_digest"]
        and z["exact_pairs"] == [["ns-a01","ns-a03"]], "EXACT_COPY_BINDING_INVALID")
    groups = {}
    for row in x["sources"]:
        groups.setdefault((row["kind"],row["payload_sha256"]),[]).append(row["source_id"])
    collisions = [dict(kind=k,payload_sha256=h,source_ids=ids) for (k,h),ids in sorted(groups.items()) if len(ids)>1]
    b.require(z["collisions"] == collisions, "COLLISION_BINDING_INVALID")
    b.require(z["main_gate_after"] is False and b.MAIN_GATE is False, "GATE_INVALID")
    after = {n:b.filehash(out/n) for n in names}
    b.require(before == after and sum((out/n).stat().st_size for n in names) <= b.MAX_OUTPUT_BYTES-65536, "EVIDENCE_CHANGED_OR_OVERSIZE")
    result = b.sealed(dict(run_id=out.name, status="S2NS_PRESEAL_BINDINGS_VALID", verification_calls=1, read_only=True,
        execution_digest=x["execution_digest"], evaluation_digest=y["evaluation_digest"], seal_digest=z["seal_digest"],
        file_hashes_before=before, file_hashes_after=after, source_count=18, event_count=31,
        payload_generation_calls=0, payload_bytes_recomputed=False, receptor_calls=0, nj_calls=0,
        limitation="Recipe/time/profile/code/digest links checked; no payload hash regeneration or receptor evidence."), "verification_digest")
    b.publish(target, result, b.MAX_METADATA_BYTES)
    return result
