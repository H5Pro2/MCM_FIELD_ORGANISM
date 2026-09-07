"""One bounded neutral NO qualification, using the existing report-local pattern."""

import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys

from tools import _s2no_private_half_materialization as run

ROOT = run.ROOT
OUT = ROOT/"reports/s2no"/run.QUAL_ID
TEST = "tests/test_s2no_private_half_materialization.py"
GATES = ("tools/_s2no_private_half_materialization.py", "tools/_s2nn_private_half_runtime_binding.py",
         "tools/_s2ng_private_runtime_comparison.py", "tools/_s2nh_private_runtime_binding.py",
         "tools/_s2nl_private_half_profile_binding.py")


def gates():
    for p in GATES:
        tree = ast.parse((ROOT/p).read_text(encoding="utf-8"))
        values = [ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id=="MAIN_GATE" for t in n.targets)]
        if values != [False]:
            raise ValueError("GATE_NOT_FALSE")
    return dict.fromkeys(GATES,False)


def publish(name,value):
    run.ng.ne.atomic_write(OUT/name,value)


def main():
    OUT.mkdir(exist_ok=False)
    inventory = sorted(n.name for n in ast.walk(ast.parse((ROOT/TEST).read_text(encoding="utf-8")))
        if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    if len(inventory)!=20 or len(set(inventory))!=20:
        raise ValueError("INVENTORY_INVALID")
    before, gate_before = run.watched(), gates()
    command = [sys.executable,"-B","-m","unittest","tests.test_s2no_private_half_materialization","-v","-f"]
    publish("preregistration.json",dict(qualification_id=run.QUAL_ID,command=command,cwd=str(ROOT),
        test_inventory=inventory,expected_tests=20,hashes_before=before,gates=gate_before,
        python=dict(version=sys.version,build=platform.python_build(),executable=sys.executable,
            executable_sha256=run.source.filehash(Path(sys.executable))),unittest_calls=1,retry=False,
        budgets=dict(runtime_events=16,formation_attempts=6,field_contacts=3456,scan_records=16,
            scan_value_limit=10624,formation_l1_limit=21312,audio_windows=4,audio_hops=40,
            audio_snapshots=31,nj_projections=4,visual_frames=4,nh_payloads=0,
            max_record_bytes=4194304,max_envelope_bytes=32768,timeout_seconds=180)))
    try:
        p = subprocess.run(command,cwd=ROOT,env=dict(os.environ,S2NO_QUAL_DIR=str(OUT)),
                           capture_output=True,check=False,timeout=180)
        code,stdout,stderr = p.returncode,p.stdout,p.stderr
    except subprocess.TimeoutExpired as error:
        code,stdout,stderr = 124,error.stdout or b"",error.stderr or b""
    for name,data in (("stdout.txt",stdout),("stderr.txt",stderr)):
        with (OUT/name).open("xb") as f: f.write(data)
    after = run.watched()
    metrics_path = OUT/"metrics.json"
    metrics = json.loads(metrics_path.read_bytes()) if metrics_path.exists() else None
    log = (stdout+stderr).decode("utf-8",errors="replace")
    ran = re.search(r"Ran (\d+) tests?",log)
    expected = dict(nh_payloads=0,main_calls=0,runtime_events=16,formation_attempts=6,field_contacts=3456,
        nj_projections=4,audio_windows=4,audio_hops=40,audio_snapshots=31,visual_frames=4)
    ok = code==0 and ran is not None and int(ran[1])==20 and log.rstrip().endswith("OK")
    ok = ok and before==after and gates()==gate_before and metrics is not None
    ok = ok and all(metrics.get(k)==v for k,v in expected.items()) and metrics.get("max_capacity_envelope_bytes",32769)<=32768
    result = dict(qualification_id=run.QUAL_ID,status="S2NO_CONNECTION_QUALIFIED" if ok else "NOT_QUALIFIED",
        exit_code=code,tests_run=int(ran[1]) if ran else None,expected_tests=20,unittest_calls=1,retry=False,
        hashes_before=before,hashes_after=after,gates_after=gates(),metrics=metrics,
        artifacts={p.name:dict(sha256=run.source.filehash(p),bytes=p.stat().st_size) for p in OUT.iterdir() if p.is_file()},
        nh_materialized=False,old_nh_reopened=False,universal_float_equivalence=False)
    result = run.sealed(result,"result_digest")
    publish("result.json",result)
    print(json.dumps({k:result[k] for k in ("qualification_id","status","exit_code","tests_run","metrics","result_digest")}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
