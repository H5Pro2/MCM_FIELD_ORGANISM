"""One preregistered neutral session qualification; no real input execution."""
import ast
import hashlib
import json
import os
import subprocess
import sys
from tools import _s2oc_private_caller_session as s

b = s.b


def save(path, value):
    b.r.ng.ne.atomic_write(path, value, 4194304)


def close_budget(out, result, inventory_bytes, old_qualification_bytes):
    columns = ("record.json", "session.json", "session-sources.json", "verification.json", "session-verification.json", "verification.claim")
    rows = []
    metadata = prefix_steps = 0
    parts = dict(nj=0, formations=0, generations=0)
    proof_bytes = source_bytes = 0
    for folder in sorted(p for p in out.iterdir() if p.is_dir()):
        sizes = [(folder/n).stat().st_size if (folder/n).exists() else 0 for n in columns]
        rows.append([folder.name, *sizes])
        actual = {p.name for p in folder.iterdir() if p.is_file()}
        if actual-set(columns): raise RuntimeError("UNACCOUNTED_RUN_FILE")
        if sizes[0]:
            record = json.loads((folder/"record.json").read_bytes())
            core = record["execution"]
            c = None if core is None else b.core_sizes(core)
            metadata += sizes[0]-(0 if c is None else sum(sum(xs) for xs in c["items"].values()))
            if c is not None:
                for k in parts: parts[k] += sum(c["items"][k])
        if sizes[1]:
            binding = json.loads((folder/"session.json").read_bytes())
            prefix = sum(len(b.canonical(x)) for x in binding["failed_prefix_steps"])
            prefix_steps += prefix; metadata += sizes[1]-prefix
        source_bytes += sizes[2]
        proof_bytes += sum(sizes[3:])
    base_files = {n: (out/n).stat().st_size for n in ("preregistration.json", "stdout.txt", "stderr.txt", "metrics.json") if (out/n).exists()}
    raw_total = sum(sum(row[1:]) for row in rows)+inventory_bytes
    base_q = sum(base_files.values()); rn = ln = 0
    result["ledger_sha256"] = "0"*64
    summary = {}
    for _ in range(12):
        q = base_q+rn+ln
        totals = dict(metadata=metadata+old_qualification_bytes+4096+512,
            shared=inventory_bytes+source_bytes+sum(parts.values()), verification=proof_bytes,
            total=raw_total+old_qualification_bytes+4096+512)
        violations = [k.upper()+"_LIMIT" for k,n in totals.items() if n > b.LIMITS[k]]
        if q > 4096: violations.append("QUALIFICATION_RESERVE_LIMIT")
        if metadata > 57344: violations.append("RUNTIME_SESSION_METADATA_LIMIT")
        if inventory_bytes+source_bytes > 65536: violations.append("QUALIFICATION_SOURCE_RESERVE_LIMIT")
        if violations: result["status"] = "NOT_QUALIFIED"
        summary = dict(columns=columns, runs=rows, qualification_files=base_files, closure=[rn,ln],
            runtime_session_metadata=metadata, retained_prefix_step_bytes=prefix_steps, auxiliary=parts,
            inventory_bytes=inventory_bytes, session_source_bytes=source_bytes,
            ob_qualification_bytes=old_qualification_bytes, qualification_bytes=q, qualification_reserve=4096,
            report_reserve=512, totals_with_reserves=totals, violations=violations)
        result["qualification_bytes"] = q
        result = b.sealed({k:v for k,v in result.items() if k != "result_digest"}, "result_digest")
        nr,nl = len(b.canonical(result)),len(b.canonical(summary))
        if (rn,ln)==(nr,nl): break
        rn,ln=nr,nl
    else: raise RuntimeError("QUALIFICATION_LEDGER_UNSTABLE")
    result = b.sealed({**{k:v for k,v in result.items() if k != "result_digest"},
        "ledger_sha256":hashlib.sha256(b.canonical(summary)).hexdigest()}, "result_digest")
    return result, summary


def main():
    out = s.QUAL_DIR; out.mkdir(exist_ok=False)
    inventory = dict(ob=b.code_inventory(), session=s.sources())
    names = sorted(n.name for n in ast.walk(ast.parse((b.ROOT/s.OWN[1]).read_text(encoding="utf-8")))
                   if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    if len(names) != len(set(names)) or len(names) != 24: raise RuntimeError("TEST_INVENTORY_INVALID")
    old = s.ob_qualification_bytes()
    pre = dict(states=16*98304, inputs=16*16384, steps=16*16384, scans=12*32767,
        sources=65536, nj=13*1024, formations=10*1536, generations=10*1536,
        metadata=57344+old+4096+512, verification=262144)
    total = sum(pre.values()); shared=sum(pre[k] for k in ("sources","nj","formations","generations"))
    pr = dict(run_id=s.QUAL_ID, tests=24, inventory_digest=b.digest(names), test_calls=1, retry=False,
        source_digest=b.digest(inventory), session_sources_digest=b.digest(inventory["session"]),
        limits=pre, total=total, shared=shared, expected=dict(audio=13,nj=13,visual=13,batch_calls=1,opened=12,verifications=13,gates=False))
    save(out/"source-inventory.json", inventory); save(out/"preregistration.json", pr)
    print(json.dumps(dict(phase="PRE_TEST", contributions=pre,total=total,shared=shared)),flush=True)
    if total>4194304 or shared>262144 or pre["metadata"]>65536 or len(b.canonical(pr))>1024:
        raise RuntimeError("PRE_TEST_BUDGET_INVALID")
    env=dict(os.environ,S2OC_QUAL_DIR=str(out),S2OC_OB_CODE=b.digest(inventory["ob"]))
    p=subprocess.run([sys.executable,"-m","unittest","tests.test_s2oc_private_caller_session"],cwd=b.ROOT,env=env,capture_output=True,check=False)
    for name,data in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f:f.write(data)
    after=dict(ob=b.code_inventory(),session=s.sources())
    metrics=json.loads((out/"metrics.json").read_bytes()) if (out/"metrics.json").exists() else None
    log=(p.stdout+p.stderr).decode("utf-8",errors="replace")
    passed=p.returncode==0 and "Ran 24 tests" in log and log.rstrip().endswith("OK") and after==inventory and metrics==pr["expected"]
    result=dict(run_id=s.QUAL_ID,status="QUALIFIED" if passed else "NOT_QUALIFIED",test_calls=1,
        expected_tests=24,passed_tests=24 if passed else None,exit_code=p.returncode,hashes_unchanged=after==inventory,
        session_sources_digest=b.digest(inventory["session"]),source_digest=b.digest(inventory),metrics=metrics,
        files={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ("preregistration.json","stdout.txt","stderr.txt","metrics.json") if (out/n).exists()},gates=False)
    result,ledger=close_budget(out,result,len(b.canonical(inventory)),old)
    save(out/"final-balance.json",ledger);save(out/"result.json",result)
    print(json.dumps(dict(status=result["status"],exit_code=p.returncode,metrics=metrics,qualification_bytes=ledger["qualification_bytes"],
        balance=ledger["totals_with_reserves"],violations=ledger["violations"],result_digest=result["result_digest"])))
    return 0 if result["status"]=="QUALIFIED" else 1


if __name__ == "__main__":raise SystemExit(main())
