"""One consolidated neutral qualification with a complete pre-test budget."""
import ast
import hashlib
import json
import os
import subprocess
import sys
from tools import _s2ob_private_caller_binding as b

QUAL_PARTS=dict(preregistration=1024,result=1280,ledger=1152,logs=256,metrics=128,state_sizes=256)
WORK=dict(events=23,formations=16,audio=19,nj=19,visual=20,runs=7,verifications=18)


def save(path,value):
    b.r.ng.ne.atomic_write(path,value,b.LIMITS["total"])


def closure(out,result,inventory_size):
    files={p.relative_to(out).as_posix():p.stat().st_size for p in out.rglob("*") if p.is_file()}
    meta=0; aux=dict(nj=0,formations=0,generations=0); proof=0
    for path in out.rglob("record.json"):
        value=json.loads(path.read_bytes());core=value.get("execution")
        size=len(b.canonical(value))
        if core is not None:
            c=b.core_sizes(core);meta+=size-c["record_bytes"]+c["metadata_runtime_bytes"]
            for k in aux:aux[k]+=sum(c["items"][k])
        else:meta+=size
    proof=sum(n for p,n in files.items() if p.endswith("verification.json") or p.endswith("verification.claim"))
    booked_names=("preregistration.json","stdout.txt","stderr.txt","metrics.json","state-sizes.json")
    base=sum(files.get(n,0) for n in booked_names)
    result["balance_sha256"]="0"*64
    rn=ln=0
    summary={}
    for _ in range(12):
        q=base+rn+ln
        totals=dict(metadata=meta+q+512,shared=inventory_size+sum(aux.values()),
                    total=sum(files.values())+rn+ln+512,verification=proof)
        violations=[k.upper()+"_LIMIT" for k,n in totals.items() if n>b.LIMITS[k]]
        if q>4096:violations.append("QUALIFICATION_RESERVE_LIMIT")
        if violations:
            result["status"]="NOT_QUALIFIED";result["failure"]="QUALIFICATION_ENVELOPE_LIMIT"
        summary=dict(files=files,closure_files=dict(result=rn,ledger=ln),
            metadata_runtime=meta,auxiliary=aux,qualification_actual=q,qualification_reserved=4096,
            report_reserved=512,totals_with_report_reserve=totals,violations=violations)
        result=b.sealed({k:v for k,v in result.items() if k!="result_digest"},"result_digest")
        new_rn,new_ln=len(b.canonical(result)),len(b.canonical(summary))
        if (rn,ln)==(new_rn,new_ln):break
        rn,ln=new_rn,new_ln
    else:raise b.S2OBError("CLOSURE_ACCOUNTING_UNSTABLE")
    result=b.sealed({**{k:v for k,v in result.items() if k!="result_digest"},
        "balance_sha256":hashlib.sha256(b.canonical(summary)).hexdigest()},"result_digest")
    b.require(len(b.canonical(result))==rn and len(b.canonical(summary))==ln,"CLOSURE_ACCOUNTING_INVALID")
    return result,summary


def main():
    out=b.QUAL_DIR;out.mkdir(exist_ok=False)
    inventory=b.code_inventory();code=b.digest(inventory)
    tree=ast.parse((b.ROOT/b.OWN[2]).read_text(encoding="utf-8"))
    names=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(names)==len(set(names))==30,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2ob_private_caller_binding"]
    source_size=len(b.canonical(inventory))
    # Serialized vector bytes are fixed; no compression rate assumption.
    state_bound=59392+27*16+32768+256
    pre=dict(state_wire_bound=state_bound,states=21*98304,inputs=23*16384,steps=23*16384,
        scans=13*32767,runtime_metadata=60000,qualification=4096,report=512,
        sources=source_size,nj=19*1024,formations=16*1536,generations=16*1536,verification=262144)
    total=sum(v for k,v in pre.items() if k!="state_wire_bound")
    shared=source_size+pre["nj"]+pre["formations"]+pre["generations"]
    pr=dict(run_id=b.QUAL_ID,code_digest=code,test_inventory_digest=b.digest(names),tests=30,
        test_calls=1,retry=False,qualification_limits=WORK,qualification_parts=QUAL_PARTS,
        preflight=pre,preflight_total=total,preflight_shared=shared,main_gate=False)
    save(out/"code-inventory.json",inventory);save(out/"preregistration.json",pr)
    print(json.dumps(dict(phase="PRE_TEST",balance=pre,total=total,shared=shared)),flush=True)
    b.require(sum(QUAL_PARTS.values())==4096 and len(b.canonical(pr))<=QUAL_PARTS["preregistration"]
        and state_bound<=98304 and pre["runtime_metadata"]+4096+512<=65536
        and source_size<=174080 and shared<=262144 and total<=4194304,"PRE_TEST_ENVELOPE_LIMIT")
    env=dict(os.environ,S2OB_QUAL_DIR=str(out),S2OB_CODE_DIGEST=code)
    p=subprocess.run(command,cwd=b.ROOT,env=env,capture_output=True,check=False)
    for name,data in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f:f.write(data)
    after=b.code_inventory();log=(p.stdout+p.stderr).decode("utf-8",errors="replace")
    metrics=json.loads((out/"metrics.json").read_bytes()) if (out/"metrics.json").exists() else None
    expected=dict(audio=19,nj=19,visual=20,run_calls=7,verification_calls=18,main_gate=False,records=7)
    passed=p.returncode==0 and "Ran 30 tests" in log and log.rstrip().endswith("OK") and after==inventory and metrics==expected
    tracked=[n for n in ("preregistration.json","stdout.txt","stderr.txt","metrics.json","state-sizes.json") if (out/n).exists()]
    result=dict(run_id=b.QUAL_ID,status="QUALIFIED" if passed else "NOT_QUALIFIED",test_calls=1,
        expected_tests=30,passed_tests=30 if passed else None,exit_code=p.returncode,code_digest=code,
        hashes_unchanged=after==inventory,hashes_after_digest=b.digest(after),metrics=metrics,
        files={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in tracked},main_gate=False)
    result,summary=closure(out,result,source_size)
    save(out/"final-balance.json",summary);save(out/"result.json",result)
    print(json.dumps(dict(run_id=b.QUAL_ID,status=result["status"],exit_code=p.returncode,
        metrics=metrics,balance=summary["totals_with_report_reserve"],qualification_bytes=summary["qualification_actual"],
        result_digest=result["result_digest"])))
    return 0 if result["status"]=="QUALIFIED" else 1


if __name__=="__main__":raise SystemExit(main())
