"""Exactly one preregistered neutral runtime qualification."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
from tools import _s2oa_private_runtime_binding as r

OWN=("tools/_s2oa_private_runtime_binding.py","tools/_s2oa_private_runtime_verification.py",
     "tests/test_s2oa_private_runtime_binding.py","reports/s2oa/qualify_runtime_once.py",
     "reports/s2oa/RUNTIME_QUALIFIKATIONSBINDUNG.md")


def watched():
    paths=set(OWN)|set(r.admin.OWN)|{p for p,_ in r.ng.sources()}|{p for p,_ in r.nn.sources()}
    paths|={"tools/_s2nq_private_verification.py","tools/_s2nl_private_rank_verification.py",
            "tools/_s2jw_profiled_memory_coordinator.py","tools/_s2jw_profiled_memory_ledger.py",
            "mcm_field_organism/_tspm1_private.py","mcm_field_organism/_ppb1_reference.py"}
    return {p:r.admin.filehash(r.admin.ROOT/p) for p in sorted(paths)}


def main():
    out=r.admin.ROOT/"reports/s2oa"/r.QUAL_ID;out.mkdir(exist_ok=False)
    before=watched()
    tree=ast.parse((r.admin.ROOT/OWN[2]).read_text(encoding="utf-8"))
    names=sorted(x.name for x in ast.walk(tree) if isinstance(x,ast.FunctionDef) and x.name.startswith("test_"))
    r.require(len(names)==len(set(names))==20,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2oa_private_runtime_binding","-v"]
    pr=dict(run_id=r.QUAL_ID,test_ids=names,test_calls=1,retry=False,command=command,hashes=before,
        python=sys.version,limits=r.admin.LIMITS,reservations=r.admin.RESERVES,verification_limits=r.WORK_LIMITS,
        qualification_budget=dict(runtime_events=25,formation_attempts=19,nj=21,receptor=0,payloads=0),main_gate=False)
    r.admin.publish(out/"preregistration.json",pr)
    env=dict(os.environ,S2OA_RUNTIME_QUAL_DIR=str(out))
    p=subprocess.run(command,cwd=r.admin.ROOT,env=env,capture_output=True,check=False)
    for name,raw in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f:f.write(raw)
    after=watched();log=(p.stdout+p.stderr).decode("utf-8",errors="replace")
    passed=p.returncode==0 and "Ran 20 tests" in log and log.rstrip().endswith("OK") and before==after
    metrics=json.loads((out/"metrics.json").read_bytes()) if (out/"metrics.json").exists() else None
    passed=passed and metrics==dict(nj=21,events=25,formation_attempts=19,main_calls=0,receptor_calls=0)
    result=r.sealed(dict(run_id=r.QUAL_ID,status="S2OA_RUNTIME_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=p.returncode,test_calls=1,expected_tests=20,passed_tests=20 if passed else None,
        hashes_before_digest=r.digest(before),hashes_after_digest=r.digest(after),hashes_unchanged=before==after,
        preregistration_sha256=r.admin.filehash(out/"preregistration.json"),
        stderr_sha256=r.admin.filehash(out/"stderr.txt"),stdout_sha256=r.admin.filehash(out/"stdout.txt"),
        metrics=metrics,main_gate_after=False),"result_digest")
    if passed:
        proof=json.loads((out/"s2oa-neutral-continuous-proof.json").read_bytes())
        extra=sum((out/n).stat().st_size for n in ("preregistration.json","stderr.txt","stdout.txt","metrics.json"))+len(r.canonical(result))
        meta=25438+proof["sizes"]["metadata_runtime_bytes"]+extra
        proof_bytes=sum(x.stat().st_size for x in out.glob("*-proof.json"))
        total=sum(x.stat().st_size for x in out.iterdir() if x.is_file())+len(r.canonical(result))+25438+162321
        if meta>65536 or proof_bytes>262144 or total>4194304:
            result=r.sealed({**{k:v for k,v in result.items() if k!="result_digest"},"status":"NOT_QUALIFIED",
                "failure":"QUALIFICATION_ENVELOPE_LIMIT","metadata_bytes":meta,"proof_bytes":proof_bytes,"total_bytes":total},"result_digest")
            passed=False
        else:
            result=r.sealed({**{k:v for k,v in result.items() if k!="result_digest"},
                "qualification_envelope":dict(metadata_bytes_upper_bound=meta+256,proof_bytes=proof_bytes,
                                           total_bytes_upper_bound=total+256)},"result_digest")
            r.require(meta+256<=65536 and total+256<=4194304,"QUALIFICATION_ENVELOPE_LIMIT")
    r.admin.publish(out/"result.json",result)
    print(json.dumps({k:result[k] for k in ("run_id","status","exit_code","passed_tests","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":raise SystemExit(main())
