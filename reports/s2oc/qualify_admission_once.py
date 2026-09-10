"""One targeted qualification of admission and actual CALLER boundary."""
import ast
import hashlib
import json
import os
import subprocess
import sys
from tools import _s2oc_private_session_admission as s

b = s.b


def balance(out):
    files = {p.relative_to(out).as_posix(): p.stat().st_size for p in out.rglob("*") if p.is_file()}
    data = 0
    shared_native = dict(nj=0, formations=0, generations=0)
    maxima = {}
    for path in out.glob("*/record.json"):
        record = json.loads(path.read_bytes())
        core = record["execution"]
        if core is not None:
            sizes = b.core_sizes(core)
            data += sum(sum(ns) for ns in sizes["items"].values())
            for k, ns in sizes["items"].items():
                maxima[k] = max([maxima.get(k, 0), *ns])
            for k in shared_native:
                shared_native[k] += sum(sizes["items"][k])
        else:
            binding = json.loads((path.parent/"session.json").read_bytes())
            data += sum(len(b.canonical(x)) for x in binding["failed_prefix_steps"])
    source_bytes = files.get("admission/inventory.json", 0)
    proof_bytes = sum(n for p, n in files.items() if p.endswith(("verification.json", "verification.claim")))
    qualification_names = ("preregistration.json", "stdout.txt", "stderr.txt", "metrics.json", "result.json", "final-balance.json")
    qbytes = sum(files.get(n, 0) for n in qualification_names)
    physical = sum(files.values())
    report = files.get("BEFUND.md", 0)
    metadata = physical-data-source_bytes-proof_bytes+max(0,4096-qbytes)+max(0,512-report)
    totals = dict(metadata=metadata, sources=source_bytes, verification=proof_bytes,
        **shared_native, shared=source_bytes+sum(shared_native.values()),
        total=physical+max(0,4096-qbytes)+max(0,512-report))
    return dict(files=files, physical=physical, qualification_bytes=qbytes, native_maxima=maxima,
        totals=totals, violations=[k.upper()+"_LIMIT" for k,v in totals.items() if v>b.LIMITS[k]]
        + (["QUALIFICATION_LIMIT"] if qbytes>4096 else []) + (["REPORT_LIMIT"] if report>512 else []))


def main():
    out = b.ROOT/"reports/s2oc"/s.QUAL_ID
    if out.exists():
        raise RuntimeError("QUALIFICATION_ID_USED")
    names = sorted(n.name for n in ast.walk(ast.parse((b.ROOT/s.OWN[1]).read_text(encoding="utf-8")))
                   if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    if len(names) != 16:
        raise RuntimeError("TEST_INVENTORY_INVALID")
    inv = s.inventory()
    out.mkdir()
    # All source/test/caller files already exist and are hashed before archive issuance.
    pin = s.create_admission(out/"admission")
    source_size = (out/"admission/inventory.json").stat().st_size
    admission_size = (out/"admission/admission.json").stat().st_size
    native = dict(states=2*2*98304, inputs=2*2*16384, steps=2*2*16384,
        scans=2*2*32767, nj=2*2*1024, formations=2*1536, generations=2*1536)
    bound = dict(metadata=65536, sources=source_size, verification=262144,
        nj=native["nj"], formations=native["formations"], generations=native["generations"],
        shared=source_size+native["nj"]+native["formations"]+native["generations"],
        total=sum(native.values())+65536+source_size+262144)
    pr = dict(run_id=s.QUAL_ID, tests=16, test_inventory_digest=b.digest(names), source_digest=b.digest(inv), test_calls=1, retry=False,
        admission_sha256=pin, native=native, bound=bound, admission_bytes=admission_size,
        qualification_reserve=4096, report_reserve=512,
        expected=dict(audio=3,nj=3,visual=2,sessions=2,verifications=2,gates=False))
    future_names = ["admission/admission.json", "admission/inventory.json", "preregistration.json",
        "stdout.txt", "stderr.txt", "metrics.json", "result.json", "final-balance.json",
        "caller-budget.json", "failure-budget.json"]
    future_names += [folder+"/"+name for folder in ("caller","failure")
                     for name in ("record.json","session.json","verification.json","verification.claim")]
    ledger_shape = dict(files={n:4194304 for n in future_names},physical=4194304,qualification_bytes=4096,
        native_maxima={k:v for k,v in native.items()},totals={k:4194304 for k in b.LIMITS},
        violations=[k.upper()+"_LIMIT" for k in b.LIMITS]+["QUALIFICATION_LIMIT","REPORT_LIMIT"])
    result_shape = b.sealed(dict(run_id=s.QUAL_ID,status="NOT_QUALIFIED",test_calls=1,expected_tests=16,
        passed_tests=None,exit_code=1,hashes_unchanged=False,source_digest="0"*64,admission_sha256=pin,
        metrics=pr["expected"],gates=False,files={n:"0"*64 for n in
        ("preregistration.json","stdout.txt","stderr.txt","metrics.json")}),"result_digest")
    for _ in range(8):
        log_capacity = 4096-len(b.canonical(pr))-len(b.canonical(pr["expected"]))-len(b.canonical(result_shape))-len(b.canonical(ledger_shape))
        if pr.get("log_capacity") == log_capacity:
            break
        pr["log_capacity"] = log_capacity
    else:
        raise RuntimeError("PREREG_SIZE_UNSTABLE")
    s.save(out/"preregistration.json", pr)
    violations = [k for k,v in bound.items() if v>b.LIMITS[k]]
    if violations or admission_size+len(b.canonical(pr))+4096+512>65536 or log_capacity <= 0:
        print(json.dumps(dict(status="PRECONDITION_BLOCKED",test_calls=0,bound=bound,violations=violations)))
        return 2
    print(json.dumps(dict(phase="PRE_TEST",tests=16,bound=bound,source_digest=b.digest(inv),admission_sha256=pin,
        qualification_log_capacity=log_capacity,full_failure_logs_retained=True)),flush=True)
    env = dict(os.environ, OC_ADMISSION_OUT=str(out), OC_ADMISSION_ROOT=str(out/"admission"), OC_ADMISSION_PIN=pin)
    proc = subprocess.run([sys.executable,"-m","unittest","tests.test_s2oc_private_session_admission"],
        cwd=b.ROOT,env=env,capture_output=True,check=False)
    for name, raw in (("stdout.txt",proc.stdout),("stderr.txt",proc.stderr)):
        with (out/name).open("xb") as f:f.write(raw)
    metrics = json.loads((out/"metrics.json").read_bytes()) if (out/"metrics.json").exists() else None
    unchanged = inv==s.inventory()
    log = (proc.stdout+proc.stderr).decode("utf-8",errors="replace")
    passed = proc.returncode==0 and "Ran 16 tests" in log and log.rstrip().endswith("OK") and unchanged and metrics==pr["expected"]
    result = b.sealed(dict(run_id=s.QUAL_ID,status="QUALIFIED" if passed else "NOT_QUALIFIED",test_calls=1,
        expected_tests=16,passed_tests=16 if passed else None,exit_code=proc.returncode,hashes_unchanged=unchanged,
        source_digest=b.digest(inv),admission_sha256=pin,metrics=metrics,gates=False,
        files={n:s.raw_hash((out/n).read_bytes()) for n in ("preregistration.json","stdout.txt","stderr.txt","metrics.json") if (out/n).exists()}),"result_digest")
    s.save(out/"result.json",result)
    # Iteratively account for the final ledger's own bytes, without rewriting any evidence.
    final_path=out/"final-balance.json"
    estimate=0
    for _ in range(12):
        measured=balance(out)
        measured["files"]["final-balance.json"]=estimate
        current=final_path.stat().st_size if final_path.exists() else 0
        delta=estimate-current
        measured["physical"]+=delta
        measured["qualification_bytes"]+=delta
        for key in ("metadata","total"):
            # Qualification bytes up to 4096 consume their existing reserve.
            measured["totals"][key]+=max(0,measured["qualification_bytes"]-4096)-max(0,measured["qualification_bytes"]-delta-4096)
        measured["violations"]=[k.upper()+"_LIMIT" for k,v in measured["totals"].items() if v>b.LIMITS[k]]
        if measured["qualification_bytes"]>4096:measured["violations"].append("QUALIFICATION_LIMIT")
        n=len(b.canonical(measured))
        if n==estimate:
            s.save(final_path,measured)
            break
        estimate=n
    else:
        raise RuntimeError("BALANCE_SIZE_UNSTABLE")
    print(json.dumps(dict(status=result["status"] if not measured["violations"] else "NOT_QUALIFIED",
        metrics=metrics,balance=measured,result_digest=result["result_digest"])),flush=True)
    return 0 if passed and not measured["violations"] else 1


if __name__=="__main__":
    raise SystemExit(main())
