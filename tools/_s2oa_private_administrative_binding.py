"""OA v2 administrative references only; no source/system imports or execution."""
import hashlib
import json
import os
from pathlib import Path
from reports.s2nd.seal_inventory import canonical, digest, filehash

ROOT = Path(__file__).resolve().parents[1]
MAIN_GATE = False
QUAL_ID = "s2oa-admin-binding-qualification-20260910-01"
RUN_ID = "s2oa-administrative-binding-20260910-01"
QUAL_DIR = ROOT / "reports/s2oa" / QUAL_ID
DOC = "reports/s2oa/ADMINISTRATIVE_BUDGETBINDUNG.md"
OWN = (DOC, "tools/_s2oa_private_administrative_binding.py",
       "tools/_s2oa_private_administrative_verification.py",
       "tests/test_s2oa_private_administrative_binding.py", "reports/s2oa/qualify_admin_once.py",
       "reports/s2oa/bind_admin_once.py", "reports/s2nd/seal_inventory.py")
PRE = "reports/s2oa/s2oa-source-preseal-20260909-01/"
OLD_QUAL = "reports/s2oa/s2oa-source-binding-qualification-20260909-01/result.json"
ARCHIVE = {
    "execution": (PRE + "execution-plan.json", "bef171eb24a692bc10f44ad22edb1214ea3ccf462420143789624c409ca51ca1"),
    "evaluation": (PRE + "evaluation-plan.json", "745b734b7f979539bb20a8a261fb2c082dbef7d2b42374c08a1edb05c7a95502"),
    "preregistration": (PRE + "preregistration.json", "f86986b5a235100acc63f10f18c17221ca77b27b2405f2aa355ab9bb57600dae"),
    "seal": (PRE + "seal.json", "5bfdb2e706b3607f49687ea20a14709f90af291f6b299d0d1056d51e1c96d50c"),
    "verification": (PRE + "verification.json", "8fcbcb7be044f6cd6b8faf7863d2f4d550a02a5e7f463a4c3a1041272baeee4a"),
    "qualification": (OLD_QUAL, "0a2cd30c6c19018306e74f711b5a2a382140724deaaaf2829c5616ad2e6b80c2"),
}
LIMITS = dict(metadata=65536, sources=174080, nj=22528, formations=30720,
              generations=30720, shared=262144, total=4194304, verification=262144)
RESERVES = dict(nj=22528, formations=30720, generations=30720)
FUTURE_ITEMS = dict(nj=(22,1024), formations=(20,1536), generations=(20,1536))
# Existing OA limits, including the strict scan upper bound.
OTHER_RESERVED = 21*98304 + 56*16384 + 16*32767
QUAL_FILES = ("preregistration.json", "result.json", "stdout.txt", "stderr.txt")


class S2OAAdminError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2OAAdminError(code)


def sealed(value, key="digest"):
    return {**value, key: digest(value)}


def check_root(value, key):
    require(type(value) is dict and value.get(key) == digest({k:v for k,v in value.items() if k != key}), "ROOT_INVALID")


def publish(path, value, limit=65536):
    data = canonical(value)
    require(len(data) <= limit, "FILE_LIMIT_EXCEEDED")
    # Exclusive final creation, matching the existing private evidence publisher.
    with Path(path).open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    return hashlib.sha256(data).hexdigest()


def watched():
    require(filehash(ROOT/"reports/s2nd/seal_inventory.py") ==
            "9f72d2a9fc9676235cf69b23ea690d25f0a782222c54393ecf5b44107f0ce91c", "SERIALIZER_CHANGED")
    return {p:filehash(ROOT/p) for p in OWN}


def read_archive():
    blobs = {}
    for alias, (path, sha) in ARCHIVE.items():
        raw = (ROOT/path).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "ARCHIVE_HASH_INVALID")
        blobs[alias] = raw
    validate_archive(blobs)
    return blobs


def validate_archive(blobs):
    require(set(blobs) == set(ARCHIVE), "ARCHIVE_CLOSURE_INVALID")
    d = {k:json.loads(v) for k,v in blobs.items()}
    ex, ev, pr, z, v, q = (d[k] for k in ARCHIVE)
    for obj, key in ((ex,"execution_digest"),(ev,"evaluation_digest"),(z,"seal_digest"),
                     (v,"verification_digest"),(q,"result_digest")):
        check_root(obj,key)
    require(z["status"] == "S2OA_SOURCES_PRESEALED" and v["status"] == "S2OA_PRESEAL_BINDINGS_VALID"
            and q["status"] == "S2OA_SOURCE_BINDING_QUALIFIED" and q["passed_tests"] == 18, "HISTORY_STATUS_INVALID")
    require(ex["execution_digest"] == ev["execution_digest"] == z["execution_digest"] == v["execution_digest"]
            and ev["evaluation_digest"] == z["evaluation_digest"] == v["evaluation_digest"]
            and z["seal_digest"] == v["seal_digest"], "HISTORY_ROOT_INVALID")
    for alias in ("execution", "evaluation", "preregistration", "seal"):
        name = Path(ARCHIVE[alias][0]).name
        require(v["file_hashes_before"][name] == v["file_hashes_after"][name]
                == hashlib.sha256(blobs[alias]).hexdigest(), "HISTORY_FILE_INVALID")
    require(pr["qualification_sha256"] == hashlib.sha256(blobs["qualification"]).hexdigest(), "HISTORY_QUAL_INVALID")
    require(ex["source_hashes"] == pr["hashes"] == z["hashes_before"] == z["hashes_after"]
            == q["hashes_before"] == q["hashes_after"], "HISTORY_CODE_INVALID")
    require(pr["events"] == ex["events"] and pr["profiles"] == ex["profiles"]
            and pr["environment"] == ex["environment"] and pr["generators"] == ex["generators"], "HISTORY_CONTENT_INVALID")
    require(len(ex["sources"]) == len(pr["specs"]) == 48 and len(ex["events"]) == 28, "HISTORY_COUNT_INVALID")
    for s, spec in zip(ex["sources"],pr["specs"],strict=True):
        check_root(s,"source_digest")
        require({k:v for k,v in s.items() if k not in ("source_digest","payload_sha256")} == spec, "SOURCE_CONTENT_INVALID")
        require(digest(s["recipe"]) == s["recipe_digest"], "RECIPE_INVALID")
    return d


def reference(artifact, member, value, index=None):
    return dict(artifact=artifact, member=member, index=index, value_digest=digest(value))


def compact(blobs):
    d = {k:json.loads(v) for k,v in blobs.items()}
    ex, ev = d["execution"], d["evaluation"]
    execution = dict(schema="s2oa.admin-execution.v2", historical_execution_digest=ex["execution_digest"],
        source_refs=[dict(source_id=s["source_id"],event_id=s["event_id"],
            ref=reference("execution","sources",s,i)) for i,s in enumerate(ex["sources"])],
        event_refs=[dict(event_id=e["event_id"],ref=reference("execution","events",e,i)) for i,e in enumerate(ex["events"])],
        bindings={k:reference("execution",k,ex[k]) for k in
                  ("profiles","environment","generators","source_hashes","contract_sha256")},
        limits=LIMITS, functional_gate=False, sources_regenerated=False)
    evaluation = dict(schema="s2oa.admin-evaluation.v2", execution_digest=digest(execution),
        original=reference("evaluation",None,ev), predictions_changed=False)
    return execution, evaluation


def ledger(metadata_sizes, source_sizes, reservations=None, other_total=0):
    reservations = RESERVES if reservations is None else reservations
    require(set(reservations) == set(RESERVES), "RESERVE_CLASS_INVALID")
    require(all(type(n) is int and n >= 0 for n in
                [*metadata_sizes.values(),*source_sizes.values(),*reservations.values(),other_total]), "BYTE_COUNT_INVALID")
    for sizes, name in ((metadata_sizes,"metadata"),(source_sizes,"sources")):
        require(all(n <= LIMITS[name] for n in sizes.values()), name.upper()+"_ITEM_LIMIT")
        require(sum(sizes.values()) <= LIMITS[name], name.upper()+"_TOTAL_LIMIT")
    for key, size in reservations.items():
        require(size <= LIMITS[key], key.upper()+"_RESERVE_LIMIT")
    shared = sum(source_sizes.values()) + sum(reservations.values())
    require(shared <= LIMITS["shared"], "SHARED_LIMIT")
    total = sum(metadata_sizes.values()) + shared + other_total
    require(total <= LIMITS["total"], "TOTAL_LIMIT")
    return dict(metadata_bytes=sum(metadata_sizes.values()), source_bytes=sum(source_sizes.values()),
                reservations=reservations, shared_reserved_bytes=shared,
                shared_remaining_bytes=LIMITS["shared"]-shared,
                metadata_remaining_bytes=LIMITS["metadata"]-sum(metadata_sizes.values()),
                total_reserved_bytes=total, total_remaining_bytes=LIMITS["total"]-total)


def shared_total_check(actual_sizes):
    require(all(type(n) is int and n >= 0 for n in actual_sizes), "BYTE_COUNT_INVALID")
    require(sum(actual_sizes) <= LIMITS["shared"], "SHARED_LIMIT")


def reserve_items(category, sizes):
    require(category in FUTURE_ITEMS, "RESERVE_CLASS_INVALID")
    count, cap = FUTURE_ITEMS[category]
    require(len(sizes) <= count, "RESERVE_COUNT_LIMIT")
    require(all(type(n) is int and 0 <= n <= cap for n in sizes), "RESERVE_ITEM_LIMIT")
    require(sum(sizes) <= RESERVES[category], "RESERVE_TOTAL_LIMIT")


def qualification():
    files = {n:(QUAL_DIR/n).read_bytes() for n in QUAL_FILES}
    q = json.loads(files["result.json"]); check_root(q,"result_digest")
    pr = json.loads(files["preregistration.json"])
    require(q["status"] == "S2OA_ADMIN_QUALIFIED" and q["passed_tests"] == 20 and q["exit_code"] == 0
            and q["unittest_calls"] == 1 and q["hashes_before"] == q["hashes_after"] == watched()
            and pr["hashes"] == watched() and pr["limits"] == LIMITS, "QUALIFICATION_INVALID")
    require(q["preregistration_sha256"] == hashlib.sha256(files["preregistration.json"]).hexdigest()
            and q["stdout_sha256"] == hashlib.sha256(files["stdout.txt"]).hexdigest()
            and q["stderr_sha256"] == hashlib.sha256(files["stderr.txt"]).hexdigest(), "QUALIFICATION_FILES_INVALID")
    return files


def bind_once():
    out = ROOT/"reports/s2oa"/RUN_ID
    out.mkdir(exist_ok=False)
    phase = "QUALIFICATION"
    try:
        qfiles = qualification(); before = watched()
        phase = "HISTORICAL_BINDINGS"
        blobs = read_archive()
        ex = json.loads(blobs["execution"])
        for path, sha in ex["source_hashes"].items():
            require(filehash(ROOT/path) == sha, "HISTORICAL_CODE_CHANGED")
        refs = {k:dict(path=p,sha256=h,bytes=len(blobs[k])) for k,(p,h) in ARCHIVE.items()}
        qrefs = {n:dict(path=str((QUAL_DIR/n).relative_to(ROOT)).replace("\\","/"),
                       sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)) for n,raw in qfiles.items()}
        phase = "ADMINISTRATIVE_BINDING"
        pr = dict(schema="s2oa.admin-preregistration.v2",run_id=RUN_ID,limits=LIMITS,reservations=RESERVES,
                  archives=refs,qualification=qrefs,code_hashes=before,retry=False,main_gate=False)
        publish(out/"preregistration.json",pr)
        newex, newev = compact(blobs)
        result = sealed(dict(schema="s2oa.administrative-binding.v2",run_id=RUN_ID,
            status="ADMINISTRATIVE_BINDING_COMPLETE",execution=newex,evaluation=newev,
            preregistration_sha256=filehash(out/"preregistration.json"),numeric_reseal=False,
            historical_budget_deviation_preserved=True,payload_generation_calls=0,receptor_calls=0,
            nj_calls=0,memory_calls=0,field_calls=0,runtime_calls=0,main_gate_after=False),"binding_digest")
        metadata = {**{f"qualification/{n}":len(raw) for n,raw in qfiles.items()},
                    "preregistration.json":len(canonical(pr)),"binding.json":len(canonical(result))}
        ledger(metadata,{k:len(v) for k,v in blobs.items()},other_total=OTHER_RESERVED)
        require(watched() == before and all(filehash(ROOT/p) == h for p,h in ARCHIVE.values()), "BINDINGS_CHANGED")
        publish(out/"binding.json",result)
        return out
    except Exception as exc:
        publish(out/"failure.json",sealed(dict(run_id=RUN_ID,status="NOT_EVALUABLE",phase=phase,
            error_class=type(exc).__name__,code=getattr(exc,"code","ADMINISTRATIVE_IO_ERROR"),
            payload_generation_calls=0,main_gate_after=False),"failure_digest"))
        raise
