"""One preregistered neutral run-connection qualification, never a main run."""
import ast
import json
import os
import subprocess
import sys

from tools import _s2ns_private_run as run

RUN_ID = run.QUAL_ID
TEST = "tests/test_s2ns_private_run_binding.py"


def main():
    out = run.ROOT/"reports/s2ns"/RUN_ID
    out.mkdir(exist_ok=False)
    before = run.code_hashes()
    logic = run.logic_qualification()
    tree = ast.parse((run.ROOT/TEST).read_text(encoding="utf-8"))
    names = sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    run.s.require(len(names) == len(set(names)) == 20 and run.MAIN_GATE is False,"QUALIFICATION_INVENTORY_INVALID")
    command = [sys.executable,"-m","unittest","tests.test_s2ns_private_run_binding","-v","-f"]
    limits = dict(memory_calls=16,receptor_calls=2,nj_calls=22,visual_calls=1,ns_payloads=0,
        execution_scans=16,verification_scans=8,execution_terms=7680,verification_terms=3840,
        formation_checks=40,max_full_record_bytes=4194304,worst_schema_bytes=run.MAX_ENVELOPE_BYTES)
    run.io.atomic_write(out/"preregistration.json",dict(run_id=RUN_ID,command=command,cwd=str(run.ROOT),
        test_calls=1,expected_tests=20,test_ids=["tests.test_s2ns_private_run_binding.RunBindingTests."+n for n in names],
        hashes_before=before,logic_qualification_digest=logic,environment=run.b.environment(),
        limits=limits,section_bytes=run.SECTION_BYTES,max_full_envelope_bytes=run.MAX_ENVELOPE_BYTES,
        main_limits=run.LIMITS,read_only_limits=run.VERIFY_LIMITS,retry=False,ns_payloads_allowed=False),65536)
    process = subprocess.run(command,cwd=run.ROOT,env={**os.environ,"S2NS_RUN_QUAL_DIR":str(out)},capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as handle:
            handle.write(data)
    after = run.code_hashes()
    transcript = (process.stdout+process.stderr).decode("utf-8",errors="replace")
    metrics = [json.loads(line.removeprefix("NS_RUN_METRICS ")) for line in transcript.splitlines() if line.startswith("NS_RUN_METRICS ")]
    passed = (process.returncode == 0 and "Ran 20 tests" in transcript and transcript.rstrip().endswith("OK")
        and before == after and len(metrics) == 1 and all(type(v) is int and 0 <= v <= limits[k] for k,v in metrics[0].items()))
    result = run.io.sealed(dict(run_id=RUN_ID,status="S2NS_RUN_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=process.returncode,test_calls=1,expected_tests=20,passed_tests=20 if passed else None,
        logic_qualification_digest=logic,hashes_before=before,hashes_after=after,metrics=metrics,
        stdout_sha256=run.io.filehash(out/"stdout.txt"),stderr_sha256=run.io.filehash(out/"stderr.txt"),
        main_gate_after=run.MAIN_GATE,ns_payloads=0,retry=False),"result_digest")
    run.io.atomic_write(out/"result.json",result,65536)
    print(json.dumps({k:result[k] for k in ("run_id","status","exit_code","passed_tests","result_digest")}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
