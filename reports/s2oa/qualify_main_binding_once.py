"""One bounded neutral qualification of the new OA main connection."""
import ast
import json
import os
import subprocess
import sys
from tools import _s2oa_private_main_binding as b


def main():
    out=b.ROOT/"reports/s2oa"/b.QUAL_ID;out.mkdir(exist_ok=False)
    before=b.watched()
    tree=ast.parse((b.ROOT/b.OWN[2]).read_text(encoding="utf-8"))
    tests=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(tests)==len(set(tests))==14,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2oa_private_main_binding","-v"]
    pr=dict(run_id=b.QUAL_ID,hashes=before,tests=tests,test_calls=1,retry=False,command=command,python=sys.version,
        limits=b.r.admin.LIMITS,reserves=b.r.admin.RESERVES,verification_limits=b.r.WORK_LIMITS,
        neutral_budget=dict(audio=22,visual=26,nj=22,events=31,formation_attempts=21,oa_payloads=0),main_gate=False)
    b.r.admin.publish(out/"preregistration.json",pr)
    p=subprocess.run(command,cwd=b.ROOT,env=dict(os.environ,S2OA_MAIN_QUAL_DIR=str(out)),capture_output=True,check=False)
    for name,data in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f:f.write(data)
    after=b.watched();log=(p.stdout+p.stderr).decode(errors="replace")
    passed=p.returncode==0 and "Ran 14 tests" in log and log.rstrip().endswith("OK") and before==after
    metrics=json.loads((out/"metrics.json").read_bytes()) if (out/"metrics.json").exists() else None
    result=b.sealed(dict(run_id=b.QUAL_ID,status="S2OA_MAIN_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=p.returncode,test_calls=1,passed_tests=14 if passed else None,expected_tests=14,
        hashes_before_digest=b.digest(before),hashes_after_digest=b.digest(after),hashes_unchanged=before==after,
        preregistration_sha256=b.r.admin.filehash(out/"preregistration.json"),
        stdout_sha256=b.r.admin.filehash(out/"stdout.txt"),stderr_sha256=b.r.admin.filehash(out/"stderr.txt"),
        metrics=metrics,main_gate_after=False),"result_digest")
    if passed:
        proof=json.loads((out/"reports/s2oa/s2oa-continuous-runtime-20260910-01/verification.json").read_bytes())
        raw=json.loads((out/"reports/s2oa/s2oa-continuous-runtime-20260910-01/record.json").read_bytes())
        # Preregistration is already charged in the neutral administrative provenance.
        extra=sum((out/n).stat().st_size for n in ("stdout.txt","stderr.txt","metrics.json"))+len(b.canonical(result))+512
        meta=proof["sizes"]["balance"]["metadata_bytes"]+extra
        total=sum(p.stat().st_size for p in out.rglob("*") if p.is_file())+raw["bindings"]["source_bytes"]-raw["bindings"].get("neutral_extra_source_bytes",0)+raw["bindings"]["metadata_bytes"]-(out/"preregistration.json").stat().st_size+len(b.canonical(result))+512
        proofbytes=sum(p.stat().st_size for p in out.rglob("*.json") if p.name=="verification.json" or p.name.endswith("-proof.json"))+raw["bindings"]["prior_verification_bytes"]
        if meta>65536 or total>4194304 or proofbytes>262144:
            passed=False
        result=b.sealed({**{k:v for k,v in result.items() if k!="result_digest"},
            "status":"S2OA_MAIN_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
            "qualification_envelope":dict(metadata_bytes_upper_bound=meta,total_bytes_upper_bound=total,
                                           verification_bytes=proofbytes)},"result_digest")
    b.r.admin.publish(out/"result.json",result)
    print(json.dumps({k:result[k] for k in ("run_id","status","exit_code","passed_tests","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":raise SystemExit(main())
