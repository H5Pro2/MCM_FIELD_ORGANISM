"""Offline NO provenance checks; never invert the half-scale projection."""

from dataclasses import asdict
import json
from pathlib import Path

from tools import _s2no_private_half_materialization as run
from tools import _s2ng_private_comparison_verification as direct
from tools import _s2nh_private_runtime_verification as nhv

require, check, digest, canonical = run.require, run.check, run.digest, run.canonical
OFFLINE_SCOPE = dict(payload_regenerated=False, raw_receptor_recomputed=False,
    half_multiplication_recomputed=False, raw_underflow_claim_recomputed=False,
    source_plan_and_native_times_checked=True, raw_digest_links_checked=True,
    nj_digest_and_rounded_values_checked=True, rounded_subnormals_checked=True)


def decode_projection(metadata, frame, part):
    """Rebuild NJ's NEW value object, not the unrecorded raw state or raw energies."""
    require(type(metadata) is dict and set(metadata) == {"source_state_digest", "source_values_digest",
        "projection_digest", "subnormal_band_indices", "underflow_band_indices"}, "NJ_RECEIPT_FORM_INVALID")
    h = run.half
    return h.HalfScaleAuditory48V1(profile_id=h.PROFILE_ID, profile_digest=h.PROFILE_DIGEST,
        geometry_id=h.GEOMETRY, source_profile_digest=h.RAW_PROFILE_DIGEST,
        source_state_digest=metadata["source_state_digest"], source_values_digest=metadata["source_values_digest"],
        snapshot_index=part["endpoint_snapshot_index"], clock_id=part["clock_id"],
        window_start_tick=part["start_tick"], window_end_tick=part["end_tick"],
        carrier_ids=frame.carrier_ids, values=frame.values,
        subnormal_band_indices=tuple(metadata["subnormal_band_indices"]),
        underflow_band_indices=tuple(metadata["underflow_band_indices"]), projection_digest=metadata["projection_digest"])


def verify_bindings(record, bound, config):
    try:
        return _verify_bindings(record, bound, config)
    except run.S2NOError:
        raise
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as error:
        raise run.S2NOError("NO_RECORD_BINDING_INVALID") from error


def _verify_bindings(record, bound, config):
    before = digest(record)
    check(record, "record_digest")
    require(type(bound) is run.nh.BoundExecution, "BOUND_EXECUTION_REQUIRED")
    x = bound.payload()
    require(record["schema"] == run.SCHEMA and record["execution_digest"] == x["execution_digest"]
        and record["profile"] == run.profile_binding(config) and record["main_gate_after"] is False,
        "RECORD_PROFILE_INVALID")
    require(len(canonical(record)) <= run.ng.MAX_BYTES
        and len(canonical({**record, "comparison":None})) <= run.MAX_ENVELOPE_BYTES, "RECORD_SIZE_EXCEEDED")
    r = record["comparison"]
    if r is None:
        f = record["failure"]
        require(record["status"] == "NOT_EVALUABLE" and record["materialization"] is None
            and record["source_receipts"] == [] and type(f) is dict and f["phase"] in run.PHASES
            and type(f["code"]) is str and 0 < len(f["code"]) <= 96
            and type(f["error_class"]) is str and f["error_class"].isidentifier(), "FAILURE_FORM_INVALID")
        n = f["ordinal"]
        require(n is None or type(n) is int and 1 <= n <= len(x["events"]), "FAILURE_ORDINAL_INVALID")
        require(f["source_id"] is None or n is not None and f["source_id"] in
            [p["source_id"] for p in (x["events"][n-1]["auditory"], x["events"][n-1]["visual"]) if p],
            "FAILURE_SOURCE_INVALID")
        if f["metrics"] is not None:
            m = f["metrics"]
            require(set(m) == {"audio_windows", "visual_frames", "audio_hops", "audio_snapshots", "nj_projections", "completed_events"}
                and all(type(v) is int and v >= 0 for v in m.values()) and n is not None
                and m["completed_events"] == n-1, "FAILURE_PROGRESS_INVALID")
            prefix = x["events"][:n]
            a = sum(s["auditory"] is not None for s in prefix)
            v = sum(s["visual"] is not None for s in prefix)
            require(m["audio_windows"] <= a and m["visual_frames"] <= v
                and m["audio_hops"] <= a*10 and m["audio_snapshots"] == max(0,m["audio_hops"]-9)
                and m["nj_projections"] <= m["audio_windows"], "FAILURE_COUNTS_INVALID")
        require(digest(record) == before, "VERIFICATION_MUTATED_RECORD")
        return run.sealed(dict(status="NOT_EVALUABLE", record_digest=record["record_digest"], evidence_valid=True,
            read_only=True, comparison_verification=None, offline_scope=OFFLINE_SCOPE), "verification_digest")
    require(record["failure"] is None and r["comparison_id"] == record["run_id"] and r["mode"] == bound.mode
        and r["field_clock_id"] == run.FIELD_CLOCK
        and len(r["inputs"]) == len(record["source_receipts"]) == len(x["events"]), "COVERAGE_INVALID")
    sources = {s["source_id"]:s for s in x["sources"]}
    counts = dict(audio_windows=0, visual_frames=0, audio_hops=0, audio_snapshots=0,
                  nj_projections=0, completed_events=len(x["events"]))
    for spec, packed, receipt in zip(x["events"], r["inputs"], record["source_receipts"], strict=True):
        check(receipt, "receipt_digest")
        event = direct.decode_input(packed, config)
        require(event.ordinal == spec["ordinal"] and event.event_id == "s2no-event-"+spec["event_id"]
            and event.event_type == spec["event_type"] and receipt["event_digest"] == event.event_digest
            and event.field_payload.start_tick == (spec["ordinal"]-1)*100000000
            and event.field_payload.end_tick == spec["common_end_tick"], "EVENT_BINDING_INVALID")
        frames = {t.frame.modality_id:t for t in event.field_payload.timed_frames}
        require(len(frames) == len(event.field_payload.timed_frames)
            and set(frames) == {m for m in ("auditory", "visual") if spec[m] is not None}, "MODALITY_INVALID")
        base = dict(spec_digest=digest(spec), auditory=None, visual=None)
        for m,t in frames.items():
            p, f = spec[m], t.frame
            s = sources[p["source_id"]]
            require((f.clock_id, f.window_start_tick, f.window_end_tick) == (p["clock_id"], p["start_tick"], p["end_tick"])
                and asdict(t.field_time) == asdict(run.nn.CommonFieldTime(run.FIELD_CLOCK,*p["common_window"])), "SOURCE_TIME_INVALID")
            base[m] = dict(source_id=s["source_id"], payload_sha256=s["payload_sha256"])
            counts["audio_windows" if m == "auditory" else "visual_frames"] += 1
            if m == "visual":
                require(f.snapshot_id == "visual.receptor."+str(p["start_tick"]), "VISUAL_SNAPSHOT_INVALID")
        require(receipt["base"] == base, "SOURCE_RECEIPT_INVALID")
        projection = None
        if "auditory" in frames:
            projection = decode_projection(receipt["nj"], frames["auditory"].frame, spec["auditory"])
            counts["nj_projections"] += 1
        else:
            require(receipt["nj"] is None, "UNEXPECTED_NJ_RECEIPT")
        # NN checks the NJ/contact/source links without calling the projector.
        value = run.nn.HalfRuntimeInputV1(event, projection,
            None if base["auditory"] is None else base["auditory"]["payload_sha256"],
            None if base["visual"] is None else base["visual"]["payload_sha256"],
            config.config_digest, run.nn.sources(), "")
        value = run.nn.HalfRuntimeInputV1(event, projection, value.pcm_digest, value.rgb_digest,
            value.config_digest, value.component_sources, digest(value.payload_without_digest()))
        run.nn.validate_input(value, config)
    counts["audio_hops"] = counts["audio_windows"]*10
    counts["audio_snapshots"] = max(0, counts["audio_hops"]-9)
    require(record["materialization"] == counts, "COUNTS_INVALID")
    if bound.mode == "MAIN":
        require(counts == dict(audio_windows=24,visual_frames=24,audio_hops=240,audio_snapshots=231,
                              nj_projections=24,completed_events=28), "MAIN_COUNTS_INVALID")
    proof = direct.verify_record(r, config=config)
    require(record["status"] == proof["status"] and digest(record) == before, "TECHNICAL_STATUS_INVALID")
    return run.sealed(dict(status=record["status"], record_digest=record["record_digest"], evidence_valid=True,
        read_only=True, comparison_verification=proof, offline_scope=OFFLINE_SCOPE), "verification_digest")


def verify_once(path, bound, config):
    path = Path(path)
    destination = path.with_name("verification.json")
    require(not destination.exists(), "VERIFICATION_ALREADY_EXISTS")
    before = run.source.filehash(path)
    try:
        require(path.stat().st_size <= run.ng.MAX_BYTES, "RECORD_SIZE_EXCEEDED")
        data = path.read_bytes()
        record = json.loads(data)
        require(canonical(record) == data, "CANONICAL_RECORD_INVALID")
        if bound.mode == "MAIN":
            require(record["binding_digest"] == digest(run.watched()) and path.parent.name == record["run_id"],
                    "CODE_OR_RUN_BINDING_INVALID")
        proof = verify_bindings(record, bound, config)
    except (run.S2NOError, ValueError, KeyError, TypeError) as error:
        proof = dict(status="NOT_EVALUABLE", evidence_valid=False, read_only=True,
                     code=getattr(error, "code", "VERIFICATION_FORM_INVALID"))
    proof = run.sealed(dict(proof, file_sha256=before, file_unchanged=run.source.filehash(path)==before,
                           verification_calls=1), "file_verification_digest")
    run.ng.ne.atomic_write(destination, proof)
    return proof


def evaluate(record, proof, bound, root, config):
    """Use the existing NH evaluator, only after the independent NO proof."""
    check(proof, "verification_digest")
    require(proof["offline_scope"] == OFFLINE_SCOPE, "OFFLINE_SCOPE_INVALID")
    # NH's evaluator operates on new stored values and actual transitions, not raw audio.
    answer = nhv.evaluate(record, proof, bound, root, config)
    # Value collisions cannot substitute for an unambiguous formation origin.
    r = record["comparison"]
    specs = bound.payload()["events"]
    cases = {c["ordinal"]:c for c in root["cases"]}
    recipes = {k:s["recipe_id"] for k,s in enumerate((s for s in specs if s["event_type"] == run.source.AV),1)}
    scans = {(s["arm"],s["ordinal"]):s["value"] for s in r["scans"] if s["role"] == "PRIMARY"}
    for row in answer["comparison"]["rows"]:
        n, m = row["ordinal"], row["modality"]
        previous = [i for i in answer["formation_inventories"] if i["ordinal"] < n]
        inventory = previous[-1] if previous else None
        origins = {}
        if inventory:
            for s in inventory["b4"]["entries"]:
                if s["occupied"]:
                    origins["B4_RECENT",s["slot_id"]] = {recipes[s["formation_index"]]}
            for slot, lineage in inventory["fast_lineage"].items():
                origins["TSPM_FAST",slot] = set(lineage)
            for t in answer["ppb_transitions"]:
                if t["ordinal"] < n and t["modality"] == m and t["event"] != "NO_UPDATE":
                    origins["B_STABLE_"+m.upper(),t["slot_id"]] = {v["recipe_id"] for v in t["lineage"]}
        row["origin_checks"] = {}
        for arm, name in enumerate(("reference", "alternative")):
            scan = scans[arm,n]
            scan = scan["evidence"] if m == "auditory" else scan
            hypothesis = scan["hypothesis"]
            witnesses = []
            if hypothesis:
                witnesses = [s for b in scan["bank_scans"] for s in b["records"]
                    if s["slot_digest"] in hypothesis["provenance_slot_digests"]]
            target = cases[n]["target_recipe"]
            pure = bool(witnesses) and all(origins.get((s["bank_role"],s["slot_id"]),set()) == {target} for s in witnesses)
            row["origin_checks"][name] = dict(pure_target_origin=pure,
                witnesses=[dict(bank=s["bank_role"],slot=s["slot_id"],
                    recipes=sorted(origins.get((s["bank_role"],s["slot_id"]),set()))) for s in witnesses])
            row[name+"_correct"] = row[name+"_correct"] and pure
            row[name+"_false_admission"] = hypothesis is not None and not row[name+"_correct"]
    rows = answer["comparison"]["rows"]
    answer["comparison"]["groups"] = nhv.evaluation.summarize(rows)
    answer["comparison"].pop("evaluation_digest")
    answer["comparison"] = run.sealed(answer["comparison"], "evaluation_digest")
    diagnostics = {d["ordinal"]:d for d in answer["cue_diagnostics"]}
    answer["phase_groups"] = {p:nhv.evaluation.summarize([r for r in rows if diagnostics[r["ordinal"]]["phase"] == p])
        for p in sorted({d["phase"] for d in diagnostics.values()})}
    answer["variation_groups"] = {key:{str(v):nhv.evaluation.summarize([r for r in rows
        if diagnostics[r["ordinal"]]["variation"] is not None and diagnostics[r["ordinal"]]["variation"][key] is v])
        for v in (False,True)} for key in ("payload_bits_changed","receptor_bits_changed","observed_bits_changed")}
    answer.pop("evaluation_digest")
    answer = run.sealed(dict(answer, origin_is_not_implied_by_numeric_equality=True), "evaluation_digest")
    require(len(canonical(answer)) <= run.ng.MAX_BYTES, "EVALUATION_SIZE_EXCEEDED")
    return answer
