"""Structural bounds and independent native verification for shared OC evidence."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

from tools import _s2oc_shared_binding as shared

b, budget = shared.b, shared.budget
CAPS = dict(states=98304, inputs=16384, steps=16384, scans=32767,
            nj=1024, formations=1536, generations=1536)


def snapshot_shape(common):
    return dict(runtime_id=common["manifest"]["run_id"], status="CLOSED",
        stream_state_digest="0"*64, field_state_digest="0"*64, memory_state_digest="0"*64,
        next_ordinal=29, processed_event_count=28, field_attempt_count=28,
        memory_formation_attempt_count=20, scan_attempt_count=16, max_event_count=28,
        config_digest="0"*64, snapshot_digest="0"*64, schema=b.r.ng.runtime.S2MR_SCHEMA)


def synthetic_forms(common, n):
    """Only administrative shape and contract-sized opaque native bodies.

    Digests have fixed width; counters use the largest allowed digit width.
    This is not a semantically valid memory history and is never verified as one.
    """
    m = common["manifest"]
    events = m["events"][:n]
    atom = lambda size: "x"*(size-2)
    forms = sum(e["kind"] == b.AV for e in events)
    cues = n-forms
    rows = [dict(step=atom(CAPS["steps"]-9),
        formation=atom(CAPS["formations"]) if e["kind"] == b.AV else None,
        generations=atom(CAPS["generations"]) if e["kind"] == b.AV else None) for e in events]
    core = b.sealed(dict(schema=b.SCHEMA, status="RECORDING_COMPLETE", run_id=m["run_id"],
        config_digest=common["rule_binding"]["config_digest"], runtime_config=common["runtime_config"],
        binding=shared.expanded_rule(common), initial=dict(snapshot=snapshot_shape(common), memory="0"*64,
            field=dict(phase="x"*16, field_component_digest="0"*64, last_end_tick=9999999999,
                       step_count=28, state_digest="0"*64)), final=snapshot_shape(common),
        inputs=[atom(CAPS["inputs"]) for _ in events], rows=rows,
        states={f"{i:064x}":atom(CAPS["states"]) for i in range(forms+1)},
        scans=[atom(CAPS["scans"]) for _ in range(cues*2)],
        source_receipts=[dict(nj=atom(CAPS["nj"]-7)) if e["kind"] != b.V else
            dict(nj=None, rgb_digest="0"*64, source_digest="0"*64) for e in events],
        failure=None, main_gate=False), "record_digest")
    record = b.sealed(dict(schema=b.SCHEMA, mode="NEUTRAL", run_id=m["run_id"], manifest=m,
        code_digest=m["code_digest"], references=[list(x) for x in shared.references(common)],
        status="RECORDING_COMPLETE", counts=dict(payloads=56,audio=22,nj=22,visual=28,materialized_events=28),
        execution=core, failure=None, evaluation=None, main_gate=False,
        input_reads=dict(common["read_plan"], actual_read_bytes=999999999, read_operations=56)), "record_digest")
    session = b.sealed(dict(schema=shared.prior.old.SCHEMA, run_id=m["run_id"], manifest_digest=m["manifest_digest"],
        session_sources_digest="0"*64, record_digest=record["record_digest"], status=record["status"],
        returned_results=[dict(ordinal=i,sha256="0"*64,byte_count=16384) for i in range(1,n+1)],
        active_qualification=common["qualification"], failed_prefix_steps=[],
        result_encoding="canonical JSON bytes of execution.rows[ordinal-1].step; no mutable references",
        main_gate=False), "session_digest")
    failure = deepcopy(record)
    failure.update(execution=None, status="NOT_EVALUABLE", failure=dict(phase="SERIALIZATION",ordinal=28,
        source_id="x"*80, completed_events=28, code="x"*128, error_class="x"*128,
        last_snapshot_digest="0"*64, final=snapshot_shape(common), balance="x"*budget.ERROR_LIMIT))
    failure = b.sealed({k:v for k,v in failure.items() if k != "record_digest"}, "record_digest")
    fs = deepcopy(session)
    fs.update(status="NOT_EVALUABLE",record_digest=failure["record_digest"],
        failed_prefix_steps=[atom(16384) for _ in events])
    fs = b.sealed({k:v for k,v in fs.items() if k != "session_digest"}, "session_digest")
    return (record, session), (failure, fs)


def preflight(common):
    from tools._s2oc_bound_session import ATTACHMENTS
    m = b.decode_manifest(common["manifest"])
    rows = []
    failure_diagnostic = None
    for n in range(len(m.events)+1):
        success, failure = synthetic_forms(common, n)
        values = {name: shared.ledger(*pair, common, attachments=ATTACHMENTS)
                  for name, pair in (("success",success),("failure",failure))}
        if failure_diagnostic is None and any(v["violations"] for v in values.values()):
            failure_diagnostic = budget.diagnostic(values,"BINDINGS",min(n+1,len(m.events)),n)
        rows.append(dict(completed=n, **{name:value["totals"] for name,value in values.items()}))
    violations = [dict(completed=row["completed"], alternative=name, kind=k, total=v, limit=b.LIMITS[k])
        for row in rows for name in ("success","failure") for k,v in row[name].items() if v>b.LIMITS[k]]
    return dict(common_sha256=shared.sha(b.canonical(common)), positions=rows, violations=violations,
        failure_diagnostic=failure_diagnostic,
        basis="Fixed administrative grammar, manifest-specific strings, maximum native item sizes/counts; no memory execution.")


def verify_record(record, session, common, inv):
    before = b.digest(record)
    manifest = shared.validate_common(common, inv)
    count = shared.prior.old.verify_binding(session, record, inv)
    b.check_root(record, "record_digest")
    shared.need(set(record)=={"schema","mode","run_id","manifest","code_digest","references","status",
                "counts","execution","failure","evaluation","main_gate","input_reads","record_digest"}
        and record["schema"]==b.SCHEMA and record["run_id"]==manifest.run_id
        and record["mode"] in ("NEUTRAL","CALLER")
        and record["manifest"] == common["manifest"] and record["code_digest"] == manifest.code_digest
        and record["main_gate"] is False and record["evaluation"] is None
        and b.canonical(record["references"]) == b.canonical(shared.references(common)), "RECORD_BINDING_INVALID")
    reads = record["input_reads"]
    shared.need(set(reads) == {"input_stock_bytes","planned_read_bytes","actual_read_bytes","read_operations"}
        and all(type(v) is int and v>=0 for v in reads.values())
        and all(reads[k]==v for k,v in common["read_plan"].items()), "READ_BINDING_INVALID")
    expected = b.validate_manifest(manifest)
    shared.need(reads["actual_read_bytes"] <= reads["planned_read_bytes"]+1
                and reads["read_operations"] <= expected["payloads"], "READ_LIMIT")
    core = record["execution"]
    if core is None:
        f = record["failure"]
        shared.need(record["status"] == "NOT_EVALUABLE" and f["phase"] in b.PHASES
            and type(f["completed_events"]) is int and count <= f["completed_events"] <= expected["events"]
            and (f["ordinal"] is None or type(f["ordinal"]) is int and 1<=f["ordinal"]<=expected["events"])
            and type(f["code"]) is str, "FAILURE_INVALID")
        if f["final"] is not None:
            b.check_root(f["final"],"snapshot_digest")
            shared.need(f["final"]["status"] == "CLOSED" and f["last_snapshot_digest"] == f["final"]["snapshot_digest"]
                and f["final"]["processed_event_count"]==f["completed_events"], "FAILURE_PROGRESS_INVALID")
        else:
            shared.need(f["completed_events"]==0 and f["last_snapshot_digest"] is None, "FAILURE_PROGRESS_INVALID")
        proof = b.sealed(dict(status="NOT_EVALUABLE", evaluation_allowed=False, record_digest=record["record_digest"],
            boundary="Failure/progress evidence only, no functional partial evaluation."), "verification_digest")
    else:
        config=b.r.nn.profile.build_config()
        shared.need(len(core["inputs"])==len(core["source_receipts"])==len(core["rows"]), "EVENT_COMPLETENESS_INVALID")
        for spec,p,src in zip(manifest.events,core["inputs"],core["source_receipts"]):
            shared.need((p["event"]["event_id"],p["event"]["ordinal"],p["event"]["event_type"]) ==
                (spec.event_id,spec.ordinal,spec.kind) and src["rgb_digest"] == (None if spec.rgb is None else spec.rgb.sha256)
                and (None if src["nj"] is None else src["nj"]["pcm_digest"]) ==
                (None if spec.pcm is None else spec.pcm.sha256), "EVENT_SOURCE_INVALID")
        native=shared.prior.old.verifier.verify_core(core,config,manifest)
        complete=record["status"]=="RECORDING_COMPLETE"
        shared.need(record["status"]==core["status"] and record["failure"]==core["failure"], "STATUS_INVALID")
        if complete:
            shared.need(count==len(core["rows"])==expected["events"] and native["field_contacts"]==expected["contacts"]
                and native["scan_receipts"]==expected["scans"] and len(native["transitions"])==expected["formations"]
                and record["counts"]=={k:expected[k] for k in ("payloads","audio","nj","visual")}
                    | {"materialized_events":expected["events"]}
                and reads["actual_read_bytes"]==reads["planned_read_bytes"]
                and reads["read_operations"]==expected["payloads"], "COUNTS_INVALID")
        proof=b.sealed(dict(status=record["status"], record_digest=record["record_digest"], core=native,
            evaluation_allowed=complete, read_only=True), "verification_digest")
    shared.need(b.digest(record)==before, "VERIFICATION_MUTATED")
    return b.sealed(dict(version=shared.VERSION, core=proof, returned_results=count, read_only=True,
        common_sha256=shared.sha(b.canonical(common)), session_digest=session["session_digest"],
        evaluation_allowed=proof["evaluation_allowed"]), "verification_digest")


def verify_once(directory, inv, *, qualified=True):
    path=Path(directory)
    with (path/"verification.claim").open("xb") as f:
        f.write(b"once")
    common=shared.load_common(path)
    shared.validate_common(common, inv, qualified=qualified)
    wr,ws=shared.read_json(path/"record.json"),shared.read_json(path/"session.json")
    record,session=shared.unpack(wr,ws,common)
    result=verify_record(record,session,common,inv)
    from tools._s2oc_bound_session import ATTACHMENTS
    size=len(b.canonical(result))+4
    actual=shared.ledger(record,session,common,attachments=ATTACHMENTS,proof_bytes=size)
    shared.need(not actual["violations"], "VERIFICATION_PACKAGE_LIMIT")
    shared.need(wr==shared.read_json(path/"record.json") and ws==shared.read_json(path/"session.json")
                and common==shared.load_common(path), "EVIDENCE_CHANGED")
    shared.prior.save(path/"verification.json",result)
    return result,actual
