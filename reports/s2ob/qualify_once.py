"""Prebind and execute exactly one neutral qualification, never a caller main run."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tools import _s2ob_private_caller_binding as b


def save(path,value):
    b.r.ng.ne.atomic_write(path,value,b.LIMITS["total"])


def main():
    out=b.QUAL_DIR
    out.mkdir(exist_ok=False)
    inventory=b.code_inventory(); code=b.digest(inventory)
    tree=ast.parse((b.ROOT/b.OWN[2]).read_text(encoding="utf-8"))
    names=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(names)==len(set(names))==24,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2ob_private_caller_binding"]
    pr=dict(run_id=b.QUAL_ID,code_digest=code,test_inventory_digest=b.digest(names),tests=24,
        command=command,test_calls=1,retry=False,limits=b.LIMITS,reserved=b.RESERVED,
        qualification_limits=dict(events=17,formations=13,audio=15,nj=15,visual=15,runs=5,verifications=10),
        main_gate=False)
    save(out/"code-inventory.json",inventory)
    # Named tests are bound in the source inventory; no duplicated verbose list in metadata.
    save(out/"preregistration.json",pr)
    preflight=dict(source_inventory_bytes=len(b.canonical(inventory)),metadata_reserved_bytes=4096,
        report_reserved_bytes=512,verification_reserved_bytes=262144,
        shared_future_reserved_bytes=len(b.canonical(inventory))+22528+30720+30720)
    print(json.dumps(dict(phase="PRE_TEST",balance=preflight)),flush=True)
    b.require(preflight["source_inventory_bytes"]<=174080 and preflight["shared_future_reserved_bytes"]<=262144
        and len(b.canonical(pr))<=1536,"PRE_TEST_ENVELOPE_LIMIT")
    env=dict(os.environ,S2OB_QUAL_DIR=str(out),S2OB_CODE_DIGEST=code)
    p=subprocess.run(command,cwd=b.ROOT,env=env,capture_output=True,check=False)
    for name,data in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f:f.write(data)
    after=b.code_inventory()
    log=(p.stdout+p.stderr).decode("utf-8",errors="replace")
    metrics=json.loads((out/"metrics.json").read_bytes()) if (out/"metrics.json").exists() else None
    passed=p.returncode==0 and "Ran 24 tests" in log and log.rstrip().endswith("OK") and after==inventory
    passed=passed and metrics==dict(audio=15,nj=15,visual=15,run_calls=5,verification_calls=10,main_gate=False,records=5)
    filehash=lambda name:hashlib.sha256((out/name).read_bytes()).hexdigest()
    result=dict(run_id=b.QUAL_ID,status="QUALIFIED" if passed else "NOT_QUALIFIED",test_calls=1,
        expected_tests=24,passed_tests=24 if passed else None,exit_code=p.returncode,code_digest=code,
        hashes_unchanged=after==inventory,hashes_after_digest=b.digest(after),metrics=metrics,
        files={n:filehash(n) for n in ("preregistration.json","stdout.txt","stderr.txt")},main_gate=False)
    files={p.relative_to(out).as_posix():p.stat().st_size for p in out.rglob("*") if p.is_file()}
    core_metadata=0;aux=dict(nj=0,formations=0,generations=0);proof_bytes=0
    for path in out.rglob("record.json"):
        value=json.loads(path.read_bytes()); core=value.get("execution")
        core_size=0 if core is None else len(b.canonical(core))
        if core is not None:
            sizes=b.core_sizes(core);core_metadata+=sizes["metadata_runtime_bytes"]
            for k in aux:aux[k]+=sum(sizes["items"][k])
        core_metadata+=len(b.canonical(value))-core_size
    proof_bytes=sum(n for name,n in files.items() if name.endswith("verification.json"))
    summary=dict(files=files,metadata_runtime_bytes=core_metadata,auxiliary_bytes=aux,
        source_inventory_bytes=files["code-inventory.json"],proof_bytes=proof_bytes,
        reserves=dict(qualification=4096,report=512))
    # Fixed closure allowance includes result + final ledger, never a new appended reserve.
    metadata=core_metadata+4096+512
    shared=files["code-inventory.json"]+sum(aux.values())
    other_files=sum(n for name,n in files.items() if name not in ("preregistration.json","stdout.txt","stderr.txt","metrics.json"))
    total=other_files+4096+512
    summary["totals_with_reserves"]=dict(metadata=metadata,shared=shared,total=total,verification=proof_bytes)
    summary["violations"]=[k for k,n in summary["totals_with_reserves"].items() if n>b.LIMITS[k]]
    # Actual bookkeeping must itself fit the unchanged reserve.
    booked=sum(files.get(n,0) for n in ("preregistration.json","stdout.txt","stderr.txt","metrics.json"))
    result["envelope"]=summary["totals_with_reserves"]
    result=b.sealed(result,"result_digest")
    booked+=len(b.canonical(result))+len(b.canonical(summary))
    summary["qualification_actual_bytes_upper_bound"]=booked+128
    if summary["violations"] or booked+128>4096:
        passed=False
        result=b.sealed({**{k:v for k,v in result.items() if k!="result_digest"},"status":"NOT_QUALIFIED",
            "failure":"QUALIFICATION_ENVELOPE_LIMIT"},"result_digest")
    save(out/"final-balance.json",summary)
    save(out/"result.json",result)
    print(json.dumps(dict(run_id=b.QUAL_ID,status=result["status"],exit_code=p.returncode,
                         metrics=metrics,balance=summary["totals_with_reserves"],result_digest=result["result_digest"])))
    return 0 if passed else 1


if __name__=="__main__":raise SystemExit(main())
