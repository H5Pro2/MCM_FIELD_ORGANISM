"""One focused qualification of new NR execution boundaries, never the corpus."""
import ast
import json
import os
import subprocess
import sys
from tools import _s2nr_private_run as run


def main():
    out=run.ROOT/"reports/s2nr"/run.QUAL_ID
    out.mkdir(exist_ok=False)
    before=run.watched()
    path=run.ROOT/"tests/test_s2nr_private_run.py"
    tree=ast.parse(path.read_text(encoding="utf-8"))
    names=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    run.require(len(names)==len(set(names))==12,"TEST_INVENTORY_INVALID")
    for p in run.OWN:
        if p.endswith(".py"):
            ast.parse((run.ROOT/p).read_text(encoding="utf-8"))
    command=[sys.executable,"-m","unittest","tests.test_s2nr_private_run","-v","-f"]
    budgets=dict(neutral_pcm_generations=6,neutral_rgb_generations=3,audio_hops=40,audio_snapshots=31,
        nj_projections=4,visual_analyses=2,runtime_events=8,formations=4,field_contacts=1536,scans=8,
        total_verifications=12,nr_payloads=0)
    run.source.publish(out/"preregistration.json",dict(run_id=run.QUAL_ID,tests=names,expected_tests=12,
        command=command,cwd=str(run.ROOT),unittest_calls=1,retry=False,hashes_before=before,
        environment=run.source.environment(),budgets=budgets,extra_verification=run.EXTRA_VERIFICATION_BUDGET,
        main_gate=False))
    p=subprocess.run(command,cwd=run.ROOT,env={**os.environ,"S2NR_MAIN_QUAL_DIR":str(out)},capture_output=True,check=False)
    for name,data in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f:
            f.write(data)
    after=run.watched()
    metrics=json.loads((out/"metrics.json").read_bytes()) if (out/"metrics.json").exists() else None
    text=(p.stdout+p.stderr).decode("utf-8",errors="replace")
    passed=p.returncode==0 and "Ran 12 tests" in text and text.rstrip().endswith("OK") and before==after
    passed=passed and metrics is not None and all(metrics[k]<=limit for k,limit in budgets.items())
    result=run.sealed(dict(run_id=run.QUAL_ID,status="S2NR_MAIN_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=p.returncode,passed_tests=12 if passed else None,expected_tests=12,unittest_calls=1,
        hashes_before=before,hashes_after=after,metrics=metrics,main_gate_after=False,
        stderr_sha256=run.source.filehash(out/"stderr.txt"),stdout_sha256=run.source.filehash(out/"stdout.txt")),"result_digest")
    run.source.publish(out/"result.json",result)
    print(json.dumps({k:result[k] for k in ("run_id","status","exit_code","passed_tests","metrics","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
