"""One neutral qualification; no source generation or NR main entry."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tools import _s2np_private_source_binding as io

ROOT=io.ROOT
RUN_ID="s2nr-runtime-binding-qualification-20260908-01"
OWN=("tools/_s2nr_private_runtime_types.py","tools/_s2nr_private_runtime_binding.py",
    "tools/_s2nr_private_runtime_verification.py","tools/_s2mr_private_minimal_mcm_runtime.py",
    "tests/test_s2nr_private_runtime_binding.py","reports/s2nr/qualify_runtime_once.py",
    "reports/s2nr/RUNTIME_QUALIFIKATIONSBINDUNG.md")


def hashes():
    from tools import _s2nr_private_runtime_binding as run
    paths=set(OWN)|{p for p,h in run.sources()}
    paths.update(str(p.relative_to(ROOT)).replace("\\","/") for p in
        (ROOT/"reports/s2nr/s2nr-source-preseal-20260908-01").glob("*.*"))
    paths.add("docs/S2NR_PRIVATER_RUNTIME_ANBINDUNGSPLAN_VERTEILTE_AUDIOBANDSICHT.md")
    return {p:io.filehash(ROOT/p) for p in sorted(paths)}


def main():
    out=ROOT/"reports/s2nr"/RUN_ID
    out.mkdir(exist_ok=False)
    before=hashes()
    tree=ast.parse((ROOT/"tests/test_s2nr_private_runtime_binding.py").read_text(encoding="utf-8"))
    names=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    io.require(len(names)==len(set(names))==16,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2nr_private_runtime_binding","-v","-f"]
    io.publish(out/"preregistration.json",dict(run_id=RUN_ID,test_ids=names,expected_tests=16,
        command=command,cwd=str(ROOT),unittest_calls=1,retry=False,hashes_before=before,
        environment=io.environment(),nr_payload_calls=0,receptor_calls=0,runtime_events_limit=14,
        formations_limit=8,field_contacts_limit=2784,nj_limit=3,verification_calls_limit=8,
        recording_byte_limit=4194304))
    env={**os.environ,"S2NR_QUAL_DIR":str(out)}
    p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,check=False)
    for name,data in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f:
            f.write(data)
    after=hashes()
    transcript=(p.stdout+p.stderr).decode("utf-8",errors="replace")
    metrics=json.loads((out/"metrics.json").read_bytes()) if (out/"metrics.json").exists() else None
    passed=p.returncode==0 and "Ran 16 tests" in transcript and transcript.rstrip().endswith("OK") and before==after
    if metrics is not None:
        passed=passed and all(metrics[k]<=v for k,v in dict(runtime_events=14,formations=8,field_contacts=2784,
            scans=8,verification_calls=8,nj_projections=3,nr_payload_calls=0,receptor_calls=0).items())
    else:
        passed=False
    result=io.sealed(dict(run_id=RUN_ID,status="S2NR_RUNTIME_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=p.returncode,expected_tests=16,passed_tests=16 if passed else None,unittest_calls=1,
        hashes_before=before,hashes_after=after,metrics=metrics,main_gate_after=False,
        stderr_sha256=io.filehash(out/"stderr.txt"),stdout_sha256=io.filehash(out/"stdout.txt")),"result_digest")
    io.publish(out/"result.json",result)
    print(json.dumps({k:result[k] for k in ("run_id","status","exit_code","passed_tests","result_digest","metrics")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
