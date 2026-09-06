"""Single neutral test process with source hashes and no NH materialization."""

import ast
import json
import os
from pathlib import Path
import subprocess
import sys
from tools import _s2nh_private_runtime_binding as b


def main():
    out=b.ROOT/"reports/s2nh"/b.QUAL_ID
    out.mkdir(exist_ok=False)
    before=b.watched()
    tree=ast.parse((b.ROOT/"tests/test_s2nh_private_runtime_binding.py").read_text(encoding="utf-8"))
    names=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(names)==len(set(names))==20,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-B","-m","unittest","tests.test_s2nh_private_runtime_binding","-v"]
    b.source.publish(out/"preregistration.json",dict(qualification_id=b.QUAL_ID,expected_tests=20,test_inventory=names,
        command=command,cwd=str(b.ROOT),hashes_before=before,python=sys.version,
        interpreter_sha256=b.source.filehash(Path(sys.executable)),unittest_calls=1,retry=False,
        nh_payload_generations=0,main_calls=0,main_gate=False,
        neutral_limits=dict(pcm_generations=5,rgb_generations=7,audio_windows=4,audio_hops=40,
            hearing_snapshots=31,visual_analyses=4,events_per_arm=6,formations_total=4,field_contacts=2688,scan_receipts=16),
        recording_bytes=b.ng.MAX_BYTES,extra_envelope_bytes=b.MAX_ENVELOPE_BYTES))
    env={**os.environ,"S2NH_QUALIFICATION_ARTIFACTS":str(out)}
    process=subprocess.run(command,cwd=b.ROOT,capture_output=True,check=False,env=env)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as f:
            f.write(data)
    after=b.watched()
    log=(process.stdout+process.stderr).decode("utf-8",errors="replace")
    ok=process.returncode==0 and "Ran 20 tests" in log and log.rstrip().endswith("OK") and before==after
    result=b.source.sealed(dict(qualification_id=b.QUAL_ID,status="S2NH_RUNTIME_BINDING_QUALIFIED" if ok else "NOT_QUALIFIED",
        exit_code=process.returncode,unittest_calls=1,expected_tests=20,passed_tests=20 if ok else None,
        hashes_before=before,hashes_after=after,nh_payload_generations=0,main_calls=0,main_gate=False,
        stdout_sha256=b.source.filehash(out/"stdout.txt"),stderr_sha256=b.source.filehash(out/"stderr.txt")),"result_digest")
    b.source.publish(out/"result.json",result)
    print(json.dumps({k:result[k] for k in ("qualification_id","status","exit_code","passed_tests","result_digest")}))
    return 0 if ok else 1


if __name__=="__main__":
    raise SystemExit(main())
