"""One neutral qualification, bounded lossless package, no real caller run."""
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from tools import _s2oc_private_caller_session as s

b=s.b
PROBE=b.ROOT/"reports/s2oc/package-probe-bound"
OB_NAMES=("preregistration.json","result.json","stdout.txt","stderr.txt","metrics.json","state-sizes.json","final-balance.json")


def save(path,value):
    b.r.ng.ne.atomic_write(path,value,4194304)


def external_binding():
    names=(*OB_NAMES,"code-inventory.json")
    return dict(root=b.QUAL_DIR.relative_to(b.ROOT).as_posix(),names=names,
        sizes=[(b.QUAL_DIR/n).stat().st_size for n in names],
        result_sha256=hashlib.sha256((b.QUAL_DIR/"result.json").read_bytes()).hexdigest(),
        inventory_sha256=hashlib.sha256((b.QUAL_DIR/"code-inventory.json").read_bytes()).hexdigest())


def native_ledger(maximums,metadata):
    return dict(kind="EXPANDED_NATIVE_ITEM_BOUNDS",maximums=maximums,record_metadata=metadata,
        limits=b.LIMITS,external=external_binding(),
        boundary="Physical accounting in package.json; original logical files in index.json. OB result binds its unchanged dependent files.")


def test_result(out,inventory,metrics,code,passed,calls=1):
    return b.sealed(dict(run_id=s.QUAL_ID,status=("QUALIFIED" if passed else "NOT_QUALIFIED") if calls else "ENVELOPE_SHAPE_ONLY",
        test_calls=calls,expected_tests=29,passed_tests=29 if passed and calls else None,exit_code=code,
        hashes_unchanged=True,source_digest=b.digest(inventory),session_sources_digest=b.digest(inventory["session"]),metrics=metrics,
        files={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ("preregistration.json","stdout.txt","stderr.txt","metrics.json") if (out/n).exists()},
        gates=False),"result_digest")


def receipt(measured,status,old_meta,old_sources):
    size=0
    for _ in range(10):
        counts=measured["stored"]
        qualification=counts["qualification"]+size
        metadata=counts["metadata"]+old_meta+max(4096,qualification)+512
        shared=counts["sources"]+old_sources+sum(counts[k] for k in ("nj","formations","generations"))
        total=measured["stored_total"]+size+old_meta+old_sources+512+max(0,4096-qualification)
        violations=[]
        if qualification>4096:violations.append("QUALIFICATION_LIMIT")
        if metadata>65536:violations.append("METADATA_LIMIT")
        if counts["metadata"]>57344:violations.append("METADATA_RESERVE_LIMIT")
        if counts["sources"]>65536:violations.append("SOURCE_RESERVE_LIMIT")
        if shared>262144:violations.append("SHARED_LIMIT")
        if counts["sources"]+old_sources>174080:violations.append("SOURCES_LIMIT")
        if counts["verification"]>262144:violations.append("VERIFICATION_LIMIT")
        if total>4194304:violations.append("TOTAL_LIMIT")
        result=dict(version=s.package.VERSION,sha256=measured["sha256"],status="NOT_QUALIFIED" if violations else status,
            stored=[counts[k] for k in s.package.CLASSES],expanded=[measured["expanded"][k] for k in s.package.CLASSES],
            external=[old_meta,old_sources],physical=[measured["stored_total"],size],
            required=[metadata,shared,total],qualification_bytes=qualification,report_reserve=512,
            unpack=[measured["decompressed_bytes"],measured["maximum_member"],measured["index_expanded"],s.package.UNPACK_MEMORY_LIMIT],
            restored=True,violations=violations)
        n=len(b.canonical(result))
        if n==size:return result
        size=n
    raise RuntimeError("RECEIPT_SIZE_UNSTABLE")


def main():
    out=s.QUAL_DIR
    if out.exists():raise RuntimeError("QUALIFICATION_ID_USED")
    inventory=dict(ob=b.code_inventory(),session=s.sources())
    names=sorted(n.name for n in ast.walk(ast.parse((b.ROOT/s.OWN[1]).read_text(encoding="utf-8")))
        if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    if len(names)!=29 or len(set(names))!=29:raise RuntimeError("TEST_INVENTORY_INVALID")
    old=s.ob_qualification_bytes(); old_sources=(b.QUAL_DIR/"code-inventory.json").stat().st_size
    probe=json.loads((PROBE/"probe.json").read_bytes())
    if probe["code_sha256"]!=hashlib.sha256((b.ROOT/"tools/_s2oc_private_evidence_package.py").read_bytes()).hexdigest():
        raise RuntimeError("PROBE_CODE_CHANGED")
    if probe["sha256"]!=hashlib.sha256((PROBE/"evidence.zip").read_bytes()).hexdigest():raise RuntimeError("PROBE_CHANGED")
    checked=receipt(probe,"PREPARED",old,old_sources)
    if checked["violations"]:raise RuntimeError(json.dumps(checked))
    prereg=dict(run_id=s.QUAL_ID,tests=29,test_inventory_digest=b.digest(names),test_calls=1,retry=False,
        source_digest=b.digest(inventory),session_sources_digest=b.digest(inventory["session"]),
        expected=dict(audio=13,nj=13,visual=13,batch_calls=1,opened=12,verifications=13,gates=False),
        package=s.package.VERSION,probe_sha256=probe["sha256"],report_reserve=512,qualification_reserve=4096,
        stored_metadata_reserve=57344,stored_sources_reserve=65536,total_limit=4194304,
        expanded_limit=s.package.MAX_EXPANDED,unpack_memory_limit=s.package.UNPACK_MEMORY_LIMIT)
    preparation=b.ROOT/"reports/s2oc/package-current-envelope"
    preparation.mkdir(exist_ok=False)
    with tempfile.TemporaryDirectory(prefix="oc-envelope-",dir=b.ROOT/"reports/s2oc") as temp:
        sample=b.Path(temp)
        prior=b.ROOT/"reports/s2oc/s2oc-session-qualification-20260910-01"
        for file in prior.rglob("*"):
            if file.is_file() and file.relative_to(prior).as_posix() not in (
                "BEFUND.md","source-inventory.json","preregistration.json","metrics.json","result.json","final-balance.json"):
                target=sample/file.relative_to(prior);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(file,target)
        save(sample/"source-inventory.json",inventory);save(sample/"preregistration.json",prereg)
        save(sample/"metrics.json",prereg["expected"])
        save(sample/"result.json",test_result(sample,inventory,prereg["expected"],1,False,0))
        save(sample/"final-balance.json",native_ledger(dict(states=98304,inputs=16384,steps=16384,scans=32767,
            nj=1024,formations=1536,generations=1536),77940))
        sample_names=[p.relative_to(sample).as_posix() for p in sample.rglob("*") if p.is_file()]
        s.package.create_package(sample,preparation/"evidence.zip",sample_names)
        measured=s.package.verify_package(preparation/"evidence.zip",sample)
    checked=receipt(measured,"ENVELOPE_SHAPE_ONLY",old,old_sources)
    save(preparation/"package.json",checked)
    if checked["violations"]:
        print(json.dumps(dict(phase="PRECONDITION_BLOCKED",test_calls=0,package=checked)),flush=True)
        return 2
    out.mkdir()
    save(out/"source-inventory.json",inventory);save(out/"preregistration.json",prereg)
    print(json.dumps(dict(phase="PRE_TEST",bound_source_bytes=len(b.canonical(inventory)),full_error_probe=checked)),flush=True)
    env=dict(os.environ,S2OC_QUAL_DIR=str(out),S2OC_OB_CODE=b.digest(inventory["ob"]))
    process=subprocess.run([sys.executable,"-m","unittest","tests.test_s2oc_private_caller_session"],
        cwd=b.ROOT,env=env,capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as f:f.write(data)
    after=dict(ob=b.code_inventory(),session=s.sources())
    metrics=json.loads((out/"metrics.json").read_bytes()) if (out/"metrics.json").exists() else None
    log=(process.stdout+process.stderr).decode("utf-8",errors="replace")
    passed=process.returncode==0 and "Ran 29 tests" in log and log.rstrip().endswith("OK") and after==inventory and metrics==prereg["expected"]
    q=test_result(out,inventory,metrics,process.returncode,passed)
    q=b.sealed({**{k:v for k,v in q.items() if k!="result_digest"},"hashes_unchanged":after==inventory},"result_digest")
    save(out/"result.json",q)
    maximums={}; original_metadata=0
    for path in sorted(out.glob("*/record.json")):
        value=json.loads(path.read_bytes()); core=value["execution"]
        if core is None:original_metadata+=path.stat().st_size;continue
        sizes=b.core_sizes(core)
        original_metadata+=path.stat().st_size-sum(sum(ns) for ns in sizes["items"].values())
        for k,ns in sizes["items"].items():maximums[k]=max([maximums.get(k,0),*ns])
    save(out/"final-balance.json",native_ledger(maximums,original_metadata))
    raw_names=[p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()]
    try:
        s.package.create_package(out,out/"evidence.zip",raw_names)
        measured=s.package.verify_package(out/"evidence.zip",out)
        stamp=receipt(measured,q["status"],old,old_sources)
        save(out/"package.json",stamp)
    except Exception as exc:
        # Keep every original and the incomplete archive; never trim a failure log.
        save(out/"package-failure.json",dict(status="NOT_QUALIFIED",phase="PACKAGING",error_class=type(exc).__name__,
            error=str(exc),test_calls=1,gates=False))
        raise
    if not stamp["violations"]:
        # Only this new output directory, after independent byte-for-byte recovery.
        root=out.resolve()
        for name in raw_names:
            path=(out/name).resolve()
            if not path.is_relative_to(root):raise RuntimeError("CLEANUP_PATH_INVALID")
            path.unlink()
        for folder in sorted((p for p in out.iterdir() if p.is_dir()),reverse=True):folder.rmdir()
    else:
        print(json.dumps(dict(retained_original_bytes=sum((out/n).stat().st_size for n in raw_names))),flush=True)
    print(json.dumps(dict(status=stamp["status"],test_calls=1,metrics=metrics,result_digest=q["result_digest"],package=stamp)),flush=True)
    return 0 if stamp["status"]=="QUALIFIED" else 1


if __name__=="__main__":raise SystemExit(main())
