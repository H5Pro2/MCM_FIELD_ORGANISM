"""Administrative preparation only: read archived JSON, hash code, count bytes.

No unittest, source generator, receptor, memory, field or runtime imports.
No qualification result is created. No saved functional history is replayed.
"""
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys

from tools import _s2oa_private_active_connection as a

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/"reports/s2oa"
ADMIN = "reports/s2oa/s2oa-administrative-binding-20260910-01/"
SHAPE = ("reports/s2oa/s2oa-main-binding-qualification-20260910-01/"
         "reports/s2oa/s2oa-continuous-runtime-20260910-01/record.json")


def read(path):
    return json.loads((ROOT/path).read_bytes())


def main():
    out = ROOT/a.DIRECTORY
    refresh = sys.argv[1:] == ["--refresh-preparation"]
    if refresh and ((out/"qualification.json").exists()
                    or read(a.DIRECTORY+"/balance.json")["status"]!="PREPARED_NOT_QUALIFIED"):
        raise ValueError("Only an unqualified administrative preparation can be refreshed")
    if not refresh and ((out/"manifest.json").exists() or (out/"balance.json").exists()):
        raise FileExistsError("Prepared artifacts already exist; no overwrite")
    admin = read(ADMIN+"preregistration.json")
    # Path inventory inheritance is not test-credit inheritance. Current hashes
    # are stored in full; none of these old qualification roots is needed later.
    paths = set()
    for directory in ("s2oa-main-binding-qualification-20260910-01",
                      "s2oa-event-id-qualification-20260910-01",
                      "s2oa-compact-reference-qualification-20260910-01"):
        paths.update(read("reports/s2oa/"+directory+"/preregistration.json")["hashes"])
    paths.update(a.OWN)
    hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}
    metadata_paths = [ADMIN+"binding.json", ADMIN+"preregistration.json"]
    metadata_paths += [ref["path"] for ref in admin["qualification"].values()]
    metadata_paths += [a.INVENTORY]
    source_refs = list(admin["archives"].values())
    for ref in source_refs:
        if a.file_reference(ROOT, ref["path"]) != ref:
            raise ValueError("Historical source reference changed")
    for ref in admin["qualification"].values():
        if a.file_reference(ROOT, ref["path"]) != ref:
            raise ValueError("Historical administrative qualification changed")
    manifest = dict(schema=a.SCHEMA, main_gate=False,
        qualification_policy="one fresh current administrative qualification; no delta accumulation",
        qualification_scope="administrative connector only, no claim of new full functional qualification",
        metadata_dependencies=[a.file_reference(ROOT,p) for p in sorted(metadata_paths)],
        source_dependencies=source_refs,
        verification_dependencies=[a.file_reference(ROOT,ADMIN+"verification.json")],
        code_hashes=hashes, inventory_sha256=hashes[a.INVENTORY],
        limits=a.LIMITS, qualification_reserved_bytes=a.QUALIFICATION_BYTES,
        report_reserved_bytes=a.REPORT_BYTES)
    manifest["manifest_digest"] = a.digest(manifest)
    mbytes = a.canonical(manifest)
    manifest_ref = dict(path=a.MANIFEST,sha256=hashlib.sha256(mbytes).hexdigest(),bytes=len(mbytes))
    ex = read(admin["archives"]["execution"]["path"])
    proof = read(ADMIN+"verification.json")
    binding = read(ADMIN+"binding.json")
    ev = read(admin["archives"]["evaluation"]["path"])
    mapping = dict(schema="s2oa.event-id-binding.v1", execution_digest=ex["execution_digest"],
        columns=["ordinal","plan_id","technical_id"],
        rows=[[n,"e%02d"%n,"s2oa-event-e%02d"%n] for n in range(1,29)])
    mapping["id_binding_digest"] = a.digest(mapping)
    p = dict(execution_digest=ex["execution_digest"], evaluation_digest=ev["evaluation_digest"],
        admin_binding_digest=binding["binding_digest"], admin_verification_digest=proof["verification_digest"],
        admin_files={n:dict(path=ADMIN+n,sha256=a.file_reference(ROOT,ADMIN+n)["sha256"])
                     for n in ("binding.json","preregistration.json","verification.json")},
        qualifications=dict(active_manifest=manifest_ref,
            current=dict(path=a.OUTCOME,sha256="0"*64,bytes=a.QUALIFICATION_BYTES)),
        code_digest=a.digest(hashes), event_ids=mapping,
        metadata_items={**{ref["path"]:ref["bytes"] for ref in manifest["metadata_dependencies"]},
                        a.MANIFEST:len(mbytes),"qualification_reserved":a.QUALIFICATION_BYTES},
        source_items={ref["path"]:ref["bytes"] for ref in source_refs},
        metadata_bytes=sum(ref["bytes"] for ref in manifest["metadata_dependencies"])+len(mbytes)+a.QUALIFICATION_BYTES,
        source_bytes=sum(ref["bytes"] for ref in source_refs),
        prior_verification_bytes=manifest["verification_dependencies"][0]["bytes"])
    old = read(SHAPE)
    original_core = deepcopy(old["execution"])
    counts = Counter()
    ids = Counter()
    pattern = re.compile(r"neutral-oa-(0[1-9]|1[0-9]|2[0-8])(?![0-9])")

    def replace(value):
        if isinstance(value, str):
            for hit in pattern.finditer(value):
                counts[value[hit.end():] or "event"] += 1
                ids[hit.group(1)] += 1
            return pattern.sub(lambda m:"s2oa-event-e"+m.group(1),value)
        if isinstance(value,list):return [replace(x) for x in value]
        if isinstance(value,dict):return {replace(k):replace(v) for k,v in value.items()}
        return value

    core = replace(original_core)
    shape = dict(schema="s2oa.bound-main.v4",mode="OA",run_id=old["run_id"],
        status=old["status"],bindings=p,counts=old["counts"],execution=core,
        failure=None,evaluation=None,main_gate=False,record_digest="0"*64)
    measured = a.inspect_envelope(shape)
    reserved = a.measure(measured["metadata"],measured["sources"],a.RESERVES,
                         21*98304+56*16384+16*32767+2*262144+len(b"once"))
    actual_with_reserves = a.measure(measured["metadata"],measured["sources"],a.RESERVES,
                                    measured["other_total"]+2*262144+len(b"once"))
    # Proof/evaluation include existing administrative verification, not extra
    # capacity on top. The main report is already in metadata at full reserve.
    total_actual_shape = measured["balance"]["total_reserved_bytes"]+2*262144+len(b"once")
    report = dict(status="PREPARED_NOT_QUALIFIED", test_calls=0, functional_calls=0,
        manifest_sha256=manifest_ref["sha256"], source_shape=a.file_reference(ROOT,SHAPE),
        shape_only=True, digests_not_revalidated=True, functional_values_not_executed=True,
        identifier_widths=dict(old=13,new=14,owner=20,consume=22),
        replaced_occurrences=dict(counts), per_event_occurrences=dict(ids),
        core_before_bytes=len(a.canonical(original_core)),core_after_bytes=len(a.canonical(core)),
        event_id_table_bytes=len(a.canonical(mapping)),actual_shape=measured,
        simultaneous_local_maxima_not_jointly_admissible=reserved,
        concrete_shape_with_additional_and_completion_reserves=actual_with_reserves,
        shape_with_full_completion_caps=total_actual_shape,
        completion_caps=dict(verification_including_admin=262144,evaluation=262144,claim=4),
        code_files=len(hashes),main_gate=False)
    # Publish the entire measurement even when limits fail. Never an early
    # ledger rejection that erases the amount or its components.
    for name,data in (("manifest.json",mbytes),("balance.json",a.canonical(report))):
        with (out/name).open("wb" if refresh else "xb") as handle:handle.write(data)
    print(json.dumps(dict(status=report["status"],metadata=measured["balance"]["metadata_bytes"],
        shared_reserved=reserved["balance"]["shared_reserved_bytes"],
        concrete_total_reserved=actual_with_reserves["balance"]["total_reserved_bytes"],
        simultaneous_local_maxima=reserved["balance"]["total_reserved_bytes"],
        concrete_violations=measured["violations"]+actual_with_reserves["violations"],
        maxima_violations=reserved["violations"],
        replaced_occurrences=sum(counts.values())),sort_keys=True))


if __name__ == "__main__":
    main()
