"""One focused neutral OA identifier qualification, never a main run."""
import ast
import json
import os
import subprocess
import sys
from tools import _s2oa_private_main_binding as b


def main():
    ids=b.ids;out=b.ROOT/"reports/s2oa"/ids.QUAL_ID;out.mkdir(exist_ok=False)
    before=b.watched();keys=set(ids.OLD_HASHES)|set(ids.OWN)
    delta={k:before[k] for k in sorted(keys)}
    base=b.ROOT/"reports/s2oa"/b.QUAL_ID/"preregistration.json"
    previous=json.loads(base.read_bytes())["hashes"]
    tests=sorted(n.name for n in ast.walk(ast.parse((b.ROOT/ids.OWN[1]).read_text()))
        if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(tests)==len(set(tests))==ids.TEST_COUNT,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2oa_private_event_ids"]
    pr=dict(run_id=ids.QUAL_ID,base_sha256=b.r.admin.filehash(base),replaced_hashes=ids.OLD_HASHES,
        hashes=delta,full_hashes_digest=b.digest(before),tests=tests,test_calls=1,retry=False,command=command,
        python=sys.version,budgets=dict(id_rows=28,neutral_lm_inputs=1,id_validation_sweeps=128,
            payloads=0,receptors=0,nj=0,runtimes=0,main_calls=0,id_bytes=ids.MAX_BYTES,
            qualification_bytes=ids.QUAL_BYTES,metadata=65536,shared=262144,total=4194304),main_gate=False)
    b.validate_id_qualification_manifest(pr,previous,before)
    b.r.admin.publish(out/"preregistration.json",pr)
    p=subprocess.run(command,cwd=b.ROOT,env=dict(os.environ,S2OA_ID_QUAL_DIR=str(out)),capture_output=True,check=False)
    for name,data in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f:f.write(data)
    after=b.watched();log=(p.stdout+p.stderr).decode(errors="replace")
    passed=p.returncode==0 and "Ran 14 tests" in log and log.rstrip().endswith("OK") and before==after
    metrics=out/"metrics.json"
    result=b.sealed(dict(run_id=ids.QUAL_ID,status="S2OA_EVENT_IDS_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=p.returncode,test_calls=1,passed_tests=ids.TEST_COUNT if passed else None,expected_tests=ids.TEST_COUNT,
        hashes_before_digest=b.digest(delta),hashes_after_digest=b.digest({k:after[k] for k in sorted(keys)}),
        hashes_unchanged=before==after,full_hashes_digest=b.digest(after),
        preregistration_sha256=b.r.admin.filehash(out/"preregistration.json"),
        stdout_sha256=b.r.admin.filehash(out/"stdout.txt"),stderr_sha256=b.r.admin.filehash(out/"stderr.txt"),
        metrics_sha256=b.r.admin.filehash(metrics) if metrics.exists() else None,main_gate_after=False),"result_digest")
    size=sum(f.stat().st_size for f in out.iterdir() if f.is_file())+len(b.canonical(result))
    if size>ids.QUAL_BYTES:
        passed=False
        result=b.sealed({**{k:v for k,v in result.items() if k!="result_digest"},"status":"NOT_QUALIFIED"},"result_digest")
    b.r.admin.publish(out/"result.json",result)
    print(json.dumps(dict(run_id=ids.QUAL_ID,status=result["status"],exit_code=p.returncode,
        qualification_bytes=size,result_digest=result["result_digest"])))
    return 0 if passed else 1


if __name__=="__main__":raise SystemExit(main())
