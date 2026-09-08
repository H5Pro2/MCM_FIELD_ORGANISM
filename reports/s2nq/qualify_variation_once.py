"""One focused evaluator qualification; synthetic evidence, no main execution."""
import ast
import json
import subprocess
import sys

from tools import _s2nq_private_run as run

RUN_ID="s2nq-variation-evaluation-qualification-20260908-01"
TEST="tests/test_s2nq_private_variation_evaluation.py"
OWN=(TEST,"reports/s2nq/qualify_variation_once.py",
     "reports/s2nq/S2NQ_VARIATIONSAUSWERTUNG_QUALIFIKATIONSBINDUNG.md")
HISTORICAL=("tests/test_s2nq_private_transfer.py","reports/s2nq/qualify_once.py",
    "reports/s2nq/S2NQ_NEUTRALE_QUALIFIKATIONSBINDUNG.md",
    "reports/s2nq/s2nq-mask-transfer-qualification-20260908-01/result.json",
    "reports/s2nq/s2nq-mask-transfer-qualification-20260908-01/BEFUND.md")


def hashes():
    return {**run.code_hashes(),**{p:run.io.filehash(run.ROOT/p) for p in OWN+HISTORICAL}}


def main():
    out=run.ROOT/"reports/s2nq"/RUN_ID
    out.mkdir(exist_ok=False)
    before=hashes()
    tests=sorted(n.name for n in ast.walk(ast.parse((run.ROOT/TEST).read_text(encoding="utf-8")))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    run.s.require(len(tests)==len(set(tests))==8 and not run.MAIN_GATE,"QUALIFICATION_BINDING_INVALID")
    for p in OWN+("tools/_s2nq_private_evaluation.py",):
        if p.endswith(".py"):
            ast.parse((run.ROOT/p).read_text(encoding="utf-8"))
    command=[sys.executable,"-m","unittest","tests.test_s2nq_private_variation_evaluation","-v","-f"]
    prereg=dict(run_id=RUN_ID,command=command,cwd=str(run.ROOT),python_version=sys.version,
        python_executable=sys.executable,python_sha256=run.io.filehash(sys.executable),
        test_ids=["tests.test_s2nq_private_variation_evaluation.VariationTests."+n for n in tests],
        expected_tests=8,test_calls=1,retry=False,hashes_before=before,main_gate=False,
        neutral_limits=dict(evaluator_calls=16,synthetic_formation_references=64,synthetic_cue_cases=24,
            reference_components_per_view=96,views=2,output_bytes=run.MAX_BYTES,
            scan_calls=0,formation_calls=0,receptor_calls=0,nj_projection_calls=0,np_payloads=0),
        evidence_scope="synthetic evaluator shapes only; no technical verification or actual memory history")
    run.io.atomic_write(out/"preregistration.json",prereg,65536)
    process=subprocess.run(command,cwd=run.ROOT,capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as handle:
            handle.write(data)
    after=hashes()
    transcript=(process.stdout+process.stderr).decode("utf-8",errors="replace")
    metrics=[json.loads(line.removeprefix("NQ_VARIATION_METRICS ")) for line in transcript.splitlines()
             if line.startswith("NQ_VARIATION_METRICS ")]
    passed=(process.returncode==0 and "Ran 8 tests" in transcript and transcript.rstrip().endswith("OK")
            and before==after and len(metrics)==1 and not run.MAIN_GATE)
    if metrics:
        m=metrics[0]
        passed=passed and m["evaluations"]==14 and 0<m["maximum_output_bytes"]<=run.MAX_BYTES
    result=run.io.sealed(dict(run_id=RUN_ID,
        status="S2NQ_VARIATION_EVALUATION_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=process.returncode,expected_tests=8,passed_tests=8 if passed else None,test_calls=1,
        hashes_before=before,hashes_after=after,metrics=metrics,
        stdout_sha256=run.io.filehash(out/"stdout.txt"),stderr_sha256=run.io.filehash(out/"stderr.txt"),
        main_gate_after=run.MAIN_GATE,scan_calls=0,formation_calls=0,receptor_calls=0,
        nj_projection_calls=0,np_payloads=0,main_history_calls=0),"result_digest")
    run.io.atomic_write(out/"result.json",result,65536)
    print(json.dumps({k:result[k] for k in ("run_id","status","exit_code","passed_tests","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
