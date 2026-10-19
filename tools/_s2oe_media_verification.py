"""Read-only media provenance and native OC verification, without decoding."""
from dataclasses import asdict
from pathlib import Path

from tools import _s2oe_media_session as m
from tools import _s2ob_private_caller_verification as native

p, b, s = m.p, m.b, m.s


def verify_record(record, session, common, inv):
    manifest = p.decode(common["manifest"])
    full_file = manifest.schema == p.FULL_VERSION
    m.check_common(manifest, common, inv)
    before = b.digest(record)
    b.check_root(record, "record_digest")
    returned = s.prior.old.verify_binding(session, record, inv)
    p.need(record["manifest"] == common["manifest"] and record["code_digest"] == manifest.code_digest
        and record["mode"] == "MEDIA" and record["main_gate"] is False and record["evaluation"] is None,
        "RECORD_BINDING_INVALID")
    media = record["media"]
    p.need(set(media) == {"receipts", "decoder", "resources"}, "MEDIA_EVIDENCE_INVALID")
    resource = media["resources"]
    if resource is not None:
        (m.full if full_file else m.uhd).verify_resources(manifest,common,resource)
        profile = common["decoder_resource_profile"]
        p.need(resource["version"] == profile["version"]
            and resource["slot_bytes"] == profile["slot_bytes"]
            and resource["queue_capacity"] == 1
            and resource["request_seconds"] == profile["request_seconds"]
            and resource["process_commit_limit"] == profile["process_commit_bytes"]
            and resource["job_commit_limit"] == profile["job_commit_bytes"]
            and resource["flags"] == 0x2308 and resource["active_process_limit"] == 1
            and resource["job_confirmed_before_media"] is True
            and resource["worker_closed"] is True
            and type(resource["read_counters_complete"]) is bool
            and len(b.canonical(dict(decoder=media["decoder"], resources=resource))) <= 2048,
            "DECODER_RESOURCE_BINDING_INVALID")
        p.need(media["decoder"]["container_read_bytes"] == record["input_reads"]["actual_read_bytes"],
            "DECODER_READ_BINDING_INVALID")
    if record["status"] == "RECORDING_COMPLETE":
        p.need(resource is not None and resource["read_counters_complete"] is True,
            "DECODER_COMPLETE_EVIDENCE_MISSING")
        if full_file:
            ends = resource.get("stream_ends",{})
            p.need(set(ends) == {"video_eof","audio_eof","last_video_pts","audio_end_sample","selected_windows"}
                and ends["video_eof"] is True and ends["audio_eof"] is True
                and ends["selected_windows"] == 20 and type(ends["last_video_pts"]) is int
                and ends["last_video_pts"] >= 0 and type(ends["audio_end_sample"]) is int
                and ends["audio_end_sample"] >= 1281600, "EOF_BINDING_INVALID")
    if full_file:
        p.need(all(media["decoder"][k] <= limit for k,limit in m.full.WORK.items())
            and media["decoder"]["passes"] <= 1 and media["decoder"]["selected_windows"] <= 20,
            "DECODER_WORK_INVALID")
    receipts = media["receipts"]
    p.need(len(receipts) <= 24, "MEDIA_RECEIPT_LIMIT")
    for n, receipt in enumerate(receipts, 1):
        event = manifest.events[n-1]
        p.need(set(receipt) == {"version", "manifest", "ordinal", "frame_pts", "next_frame_pts", "pcm", "rgb"}
            and receipt["version"] == p.TIME_VERSION and receipt["manifest"] == manifest.manifest_digest
            and receipt["ordinal"] == n and len(b.canonical(receipt)) <= 512, "MEDIA_RECEIPT_INVALID")
        if event.kind != b.A:
            x, y = receipt["frame_pts"], receipt["next_frame_pts"]
            num, den = manifest.source.video_time_base
            # Independent integer comparison: no selector or Fraction helper used.
            p.need(type(x) is int and type(y) is int and 0 <= x < y
                and 20*x*num <= ((28 if full_file else 10)*event.window_number+1)*den < 20*y*num,
                "FRAME_SELECTION_INVALID")
        else:
            p.need(receipt["frame_pts"] is None and receipt["next_frame_pts"] is None, "UNEXPECTED_FRAME")
    reads = record["input_reads"]
    p.need(reads["input_stock_bytes"] == manifest.source.size
        and reads["planned_read_bytes"] == 12*manifest.source.size
        and type(reads["actual_read_bytes"]) is int and 0 <= reads["actual_read_bytes"] <= reads["planned_read_bytes"],
        "MEDIA_READ_LIMIT")
    core = record["execution"]
    if core is not None:
        p.need(core["run_id"] == manifest.run_id and len(core["inputs"]) == len(receipts), "MEDIA_CORE_INVALID")
        for spec, item, src, receipt in zip(manifest.events[:len(receipts)], core["inputs"], core["source_receipts"], receipts, strict=True):
            e = item["event"]
            p.need((e["event_id"], e["ordinal"], e["event_type"]) == (spec.event_id, spec.ordinal, spec.kind), "EVENT_BINDING_INVALID")
            p.need(receipt["pcm"] == (None if src["nj"] is None else src["nj"]["pcm_digest"])
                and receipt["rgb"] == src["rgb_digest"], "MEDIA_PAYLOAD_BINDING_INVALID")
        proof = native.verify_core(core, m.r.nn.profile.build_config(), manifest)
        if record["status"] == "RECORDING_COMPLETE":
            expected = p.counts(manifest.events)
            p.need(len(receipts) == returned == expected["events"] and record["counts"] ==
                {k:expected[k] for k in ("payloads","audio","nj","visual")} | dict(materialized_events=expected["events"]), "COMPLETENESS_INVALID")
            p.need(proof["field_contacts"] == expected["contacts"] and proof["scan_receipts"] == expected["scans"], "OPERATIONS_INVALID")
    else:
        failure = record["failure"]
        p.need(record["status"] == "NOT_EVALUABLE" and type(failure) is dict
            and type(failure["code"]) is str and failure["completed_events"] >= returned,
            "FAILURE_INVALID")
        final = failure["final"]
        if final is not None:
            b.check_root(final, "snapshot_digest")
            p.need(final["status"] == "CLOSED" and final["processed_event_count"] == failure["completed_events"], "FAILURE_PROGRESS_INVALID")
        proof = dict(status="NOT_EVALUABLE", evaluation_allowed=False, read_only=True)
    ledger = p.ledger(record, session, common, attachments=m.oc.ATTACHMENTS)
    p.need(not ledger["violations"] and b.digest(record) == before, "EVIDENCE_LIMIT_OR_MUTATION")
    return b.sealed(dict(version=p.VERSION, status=record["status"], native=proof,
        evaluation_allowed=record["status"] == "RECORDING_COMPLETE" and proof["evaluation_allowed"],
        read_only=True, source_receipts=len(receipts), record_digest=record["record_digest"],
        boundary="PTS/digests and recorded job limits checked, not historical OS enforcement. No PCM/RGB or FFT reconstruction. Failed-worker read counts may be a lower bound."), "verification_digest")


def verify_once(directory, inv):
    path = Path(directory)
    with (path/"verification.claim").open("xb") as f:
        f.write(b"once")
    common = s.load_common(path)
    record, session = s.unpack(s.read_json(path/"record.json"), s.read_json(path/"session.json"), common)
    proof = verify_record(record, session, common, inv)
    p.need(len(b.canonical(proof))+4 <= 262144, "VERIFICATION_LIMIT")
    s.prior.save(path/"verification.json", proof)
    return proof
