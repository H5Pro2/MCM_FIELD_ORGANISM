"""One preregistered neutral call; no main NQ source access."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys

from tools import _s2nq_private_run as run

RUN_ID="s2nq-mask-transfer-qualification-20260908-01"
TEST="tests/test_s2nq_private_transfer.py"
OWN=(TEST,"reports/s2nq/qualify_once.py","reports/s2nq/S2NQ_NEUTRALE_QUALIFIKATIONSBINDUNG.md")
PRIOR=("reports/s2np/s2np-source-preseal-20260907-01/execution-plan.json",
       "reports/s2np/s2np-source-preseal-20260907-01/evaluation-plan.json",
       "reports/s2np/s2np-source-preseal-20260907-01/seal.json",
       "reports/s2np/s2np-receptor-nj-materialization-20260907-01/result.json",
       "reports/s2np/s2np-coverage-corpus-comparison-20260907-01/recording.json")


def hashes():
    return {**run.code_hashes(),**{p:run.io.filehash(run.ROOT/p) for p in OWN+PRIOR}}


def main():
    out=run.ROOT/"reports/s2nq"/RUN_ID
    out.mkdir(exist_ok=False)
    before=hashes()
    tests=sorted(n.name for n in ast.walk(ast.parse((run.ROOT/TEST).read_text(encoding="utf-8")))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    run.s.require(len(tests)==len(set(tests))==24,"TEST_INVENTORY_INVALID")
    for p in before:
        if p.endswith(".py"):
            ast.parse((run.ROOT/p).read_text(encoding="utf-8"))
    command=[sys.executable,"-m","unittest","tests.test_s2nq_private_transfer","-v","-f"]
    prereg=dict(run_id=RUN_ID,command=command,cwd=str(run.ROOT),python_version=sys.version,
        python_executable=sys.executable,python_sha256=run.io.filehash(sys.executable),
        test_ids=["tests.test_s2nq_private_transfer.TransferTests."+n for n in tests],expected_tests=24,
        test_calls=1,retry=False,hashes_before=before,main_gate=False,
        neutral_limits=dict(formations=4,nj_calls=6,receptor_calls=0,np_payloads=0,
            scan_calls=256,scan_comparisons=135168,verification_comparisons=135168,historical_scan_calls=4),
        main_execution_limits=run.LIMITS,separate_main_verification_limits=run.VERIFY_LIMITS,
        np_access="file hashes only; no parsing or comparing NP values")
    run.io.atomic_write(out/"preregistration.json",prereg,65536)
    env={**os.environ,"S2NQ_QUAL_DIR":str(out)}
    process=subprocess.run(command,cwd=run.ROOT,env=env,capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as handle:
            handle.write(data)
    after=hashes()
    transcript=(process.stdout+process.stderr).decode("utf-8",errors="replace")
    metrics=[json.loads(line.removeprefix("NQ_NEUTRAL_METRICS ")) for line in transcript.splitlines()
             if line.startswith("NQ_NEUTRAL_METRICS ")]
    passed=(process.returncode==0 and "Ran 24 tests" in transcript and transcript.rstrip().endswith("OK")
            and before==after and len(metrics)==1)
    if metrics:
        m=metrics[0]
        passed=passed and m["neutral_formations"]==4 and m["nj_calls"]==6 and m["scan_calls"]<=256 and m["scan_comparisons"]<=135168
        passed=passed and m["verification_comparisons"]<=135168 and m["historical_scan_calls"]==4
        passed=passed and 0<m["maximum_arm_bytes"]<=32768 and 0<m["maximum_serialization_bytes"]<=run.MAX_BYTES
    result=run.io.sealed(dict(run_id=RUN_ID,status="S2NQ_NEUTRAL_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=process.returncode,expected_tests=24,passed_tests=24 if passed else None,test_calls=1,
        hashes_before=before,hashes_after=after,metrics=metrics,
        stdout_sha256=run.io.filehash(out/"stdout.txt"),stderr_sha256=run.io.filehash(out/"stderr.txt"),
        main_gate_after=run.MAIN_GATE,receptor_calls=0,np_payloads=0,main_history_calls=0),"result_digest")
    run.io.atomic_write(out/"result.json",result,65536)
    print(json.dumps({k:result[k] for k in ("run_id","status","exit_code","passed_tests","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
