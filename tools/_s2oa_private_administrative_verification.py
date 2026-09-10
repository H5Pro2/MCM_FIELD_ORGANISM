"""Independent OA administrative reference/byte verification; no generators."""
import hashlib
import json
from tools import _s2oa_private_administrative_binding as b


def sha(value):
    raw = json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def resolve(ref, archive, artifact, member, index):
    b.require(type(ref) is dict and set(ref) == {"artifact","member","index","value_digest"}, "REFERENCE_FORM_INVALID")
    b.require((ref["artifact"],ref["member"],ref["index"]) == (artifact,member,index), "REFERENCE_TARGET_INVALID")
    b.require(artifact in archive, "REFERENCE_MISSING")
    value = archive[artifact] if member is None else archive[artifact].get(member)
    b.require(value is not None, "REFERENCE_MISSING")
    if index is not None:
        b.require(type(index) is int and type(value) is list and 0 <= index < len(value), "REFERENCE_INDEX_INVALID")
        value = value[index]
    b.require(sha(value) == ref["value_digest"], "REFERENCE_DIGEST_INVALID")
    return value


def verify_references(ex, ev, blobs):
    b.require(set(blobs) == set(b.ARCHIVE), "ARCHIVE_CLOSURE_INVALID")
    originals = {k:json.loads(v) for k,v in blobs.items()}
    original = originals["execution"]
    b.require(set(ex) == {"schema","historical_execution_digest","source_refs","event_refs","bindings",
                          "limits","functional_gate","sources_regenerated"}, "EXECUTION_FORM_INVALID")
    b.require(ex["schema"] == "s2oa.admin-execution.v2" and ex["limits"] == b.LIMITS
              and ex["functional_gate"] is False and ex["sources_regenerated"] is False, "SCOPE_INVALID")
    b.require(ex["historical_execution_digest"] == original["execution_digest"], "HISTORICAL_ROOT_INVALID")
    b.require(type(ex["source_refs"]) is list and len(ex["source_refs"]) == len(original["sources"]) == 48
              and type(ex["event_refs"]) is list and len(ex["event_refs"]) == len(original["events"]) == 28, "REFERENCE_COUNT_INVALID")
    for i,row in enumerate(ex["source_refs"]):
        b.require(type(row) is dict and set(row) == {"source_id","event_id","ref"}, "SOURCE_REFERENCE_INVALID")
        s = resolve(row["ref"],originals,"execution","sources",i)
        b.require(row["source_id"] == s["source_id"] and row["event_id"] == s["event_id"], "SOURCE_ID_INVALID")
    for i,row in enumerate(ex["event_refs"]):
        b.require(type(row) is dict and set(row) == {"event_id","ref"}, "EVENT_REFERENCE_INVALID")
        e = resolve(row["ref"],originals,"execution","events",i)
        b.require(row["event_id"] == e["event_id"], "EVENT_ID_INVALID")
    members = {"profiles","environment","generators","source_hashes","contract_sha256"}
    b.require(type(ex["bindings"]) is dict and set(ex["bindings"]) == members, "BINDING_MEMBERS_INVALID")
    for k in members:
        resolve(ex["bindings"][k],originals,"execution",k,None)
    b.require(set(ev) == {"schema","execution_digest","original","predictions_changed"}
              and ev["schema"] == "s2oa.admin-evaluation.v2" and ev["predictions_changed"] is False
              and ev["execution_digest"] == sha(ex), "EVALUATION_BINDING_INVALID")
    resolve(ev["original"],originals,"evaluation",None,None)


def check_archive_manifest(manifest, blobs):
    b.require(set(manifest) == set(blobs) == set(b.ARCHIVE), "ARCHIVE_CLOSURE_INVALID")
    for alias, (path, expected) in b.ARCHIVE.items():
        row = manifest[alias]
        b.require(row == dict(path=path,sha256=expected,bytes=len(blobs[alias]))
                  and hashlib.sha256(blobs[alias]).hexdigest() == expected, "ARCHIVE_HASH_INVALID")


def check_totals(metadata, sources, reservations, other=0):
    # Independent byte accounting, no primary ledger or serialized size claims.
    b.require(set(reservations) == {"nj","formations","generations"}, "RESERVE_CLASS_INVALID")
    b.require(all(type(n) is int and n >= 0 for n in [*metadata.values(),*sources.values(),*reservations.values(),other]), "BYTE_COUNT_INVALID")
    for sizes, cap, name in ((metadata,65536,"METADATA"),(sources,174080,"SOURCES")):
        b.require(all(n <= cap for n in sizes.values()), name+"_ITEM_LIMIT")
        b.require(sum(sizes.values()) <= cap, name+"_TOTAL_LIMIT")
    for name,cap in (("nj",22528),("formations",30720),("generations",30720)):
        b.require(reservations[name] <= cap, name.upper()+"_RESERVE_LIMIT")
    shared = sum(sources.values()) + sum(reservations.values())
    b.require(shared <= 262144, "SHARED_LIMIT")
    total = sum(metadata.values()) + shared + other
    b.require(total <= 4194304, "TOTAL_LIMIT")
    return dict(metadata_bytes=sum(metadata.values()),source_bytes=sum(sources.values()),reservations=reservations,
        shared_reserved_bytes=shared,shared_remaining_bytes=262144-shared,
        metadata_remaining_bytes=65536-sum(metadata.values()),total_reserved_bytes=total,total_remaining_bytes=4194304-total)


def verify_once(out):
    b.require(out.name == b.RUN_ID, "RUN_ID_INVALID")
    with (out/"verification.claim").open("xb") as f:
        f.write(b.canonical(dict(verification_calls=1)))
    phase = "ADMINISTRATIVE_READ"
    try:
        paths = {"preregistration.json":out/"preregistration.json","binding.json":out/"binding.json"}
        before = {n:b.filehash(p) for n,p in paths.items()}
        pr = json.loads(paths["preregistration.json"].read_bytes())
        result = json.loads(paths["binding.json"].read_bytes())
        b.require(result.get("binding_digest") == sha({k:v for k,v in result.items() if k != "binding_digest"}), "ROOT_INVALID")
        b.require(result["status"] == "ADMINISTRATIVE_BINDING_COMPLETE" and result["run_id"] == pr["run_id"] == b.RUN_ID
                  and result["preregistration_sha256"] == before["preregistration.json"], "TOTAL_BINDING_INVALID")
        b.require(pr["code_hashes"] == b.watched() and pr["limits"] == b.LIMITS
                  and pr["reservations"] == b.RESERVES and pr["main_gate"] is False, "CONFIGURATION_INVALID")
        for k in ("payload_generation_calls","receptor_calls","nj_calls","memory_calls","field_calls","runtime_calls"):
            b.require(type(result[k]) is int and result[k] == 0, "EXECUTION_FORBIDDEN")
        b.require(result["main_gate_after"] is False and result["numeric_reseal"] is False
                  and result["historical_budget_deviation_preserved"] is True and b.MAIN_GATE is False, "SCOPE_INVALID")
        phase = "REFERENCE_CLOSURE"
        blobs = {alias:(b.ROOT/path).read_bytes() for alias,(path,_) in b.ARCHIVE.items()}
        check_archive_manifest(pr["archives"],blobs)
        verify_references(result["execution"],result["evaluation"],blobs)
        original = json.loads(blobs["execution"])
        for path,expected in original["source_hashes"].items():
            b.require(b.filehash(b.ROOT/path) == expected, "HISTORICAL_CODE_CHANGED")
        qraw = {n:(b.QUAL_DIR/n).read_bytes() for n in b.QUAL_FILES}
        b.require(set(pr["qualification"]) == set(qraw), "QUALIFICATION_INVALID")
        for n,raw in qraw.items():
            b.require(pr["qualification"][n] == dict(path=str((b.QUAL_DIR/n).relative_to(b.ROOT)).replace("\\","/"),
                sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)), "QUALIFICATION_INVALID")
        q = json.loads(qraw["result.json"])
        b.require(q["result_digest"] == sha({k:v for k,v in q.items() if k != "result_digest"})
                  and q["status"] == "S2OA_ADMIN_QUALIFIED" and q["passed_tests"] == 20
                  and q["hashes_before"] == q["hashes_after"] == b.watched(), "QUALIFICATION_INVALID")
        phase = "BYTE_ACCOUNTING"
        metadata = {**{n:p.stat().st_size for n,p in paths.items()},**{"qualification/"+n:len(v) for n,v in qraw.items()}}
        sources = {k:len(v) for k,v in blobs.items()}
        balance = check_totals(metadata,sources,pr["reservations"],21*98304+56*16384+16*32767)
        after = {n:b.filehash(p) for n,p in paths.items()}
        b.require(before == after and all(b.filehash(b.ROOT/p) == h for p,h in b.ARCHIVE.values()), "BINDINGS_CHANGED")
        proof = b.sealed(dict(run_id=b.RUN_ID,status="ADMINISTRATIVE_BINDINGS_VALID",verification_calls=1,
            binding_digest=result["binding_digest"],metadata_items=metadata,source_items=sources,balance=balance,
            future_state_input_step_scan_reserve_bytes=21*98304+56*16384+16*32767,
            hashes_before=before,hashes_after=after,read_only=True,payload_generation_calls=0,
            numeric_reseal=False,functional_qualification=False,main_gate_after=False,
            limitation="Exact archived bytes, full referenced values and budgets checked; no payload or functional validation."),"verification_digest")
        b.require(len(b.canonical(proof))+(out/"verification.claim").stat().st_size <= 262144, "VERIFICATION_LIMIT")
        b.publish(out/"verification.json",proof,262144)
        return proof
    except Exception as exc:
        b.publish(out/"verification-failure.json",b.sealed(dict(run_id=b.RUN_ID,status="NOT_EVALUABLE",phase=phase,
            code=getattr(exc,"code","ADMINISTRATIVE_IO_ERROR"),error_class=type(exc).__name__,main_gate_after=False),"failure_digest"))
        raise
