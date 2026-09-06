"""One bounded neutral qualification, never the NH source payloads."""

import ast
import json
import subprocess
import sys
from tools import _s2nh_private_source_binding as b


def main():
    out=b.ROOT/"reports/s2nh"/b.QUAL_ID
    out.mkdir(exist_ok=False)
    before=b.watched()
    tree=ast.parse((b.ROOT/"tests/test_s2nh_private_source_binding.py").read_text(encoding="utf-8"))
    names=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(names)==len(set(names))==18,"TEST_INVENTORY_INVALID")
    command=[sys.executable,"-B","-m","unittest","tests.test_s2nh_private_source_binding","-v"]
    b.publish(out/"preregistration.json",dict(qualification_id=b.QUAL_ID,expected_tests=18,
        test_inventory=names,command=command,cwd=str(b.ROOT),hashes_before=before,generator=b.identity(),
        unittest_calls=1,retry=False,nh_payload_generations=0,receptor_calls=0,
        neutral_payload_limits=dict(pcm=1,rgb=2),main_gate=False))
    p=subprocess.run(command,cwd=b.ROOT,capture_output=True,check=False)
    for name,data in (("stdout.txt",p.stdout),("stderr.txt",p.stderr)):
        with (out/name).open("xb") as f: f.write(data)
    after=b.watched()
    log=(p.stdout+p.stderr).decode("utf-8",errors="replace")
    ok=p.returncode==0 and "Ran 18 tests" in log and log.rstrip().endswith("OK") and before==after
    result=b.sealed(dict(qualification_id=b.QUAL_ID,status="S2NH_SOURCE_BINDING_QUALIFIED" if ok else "NOT_QUALIFIED",
        exit_code=p.returncode,unittest_calls=1,expected_tests=18,passed_tests=18 if ok else None,
        hashes_before=before,hashes_after=after,nh_payload_generations=0,receptor_calls=0,main_gate=False,
        stdout_sha256=b.filehash(out/"stdout.txt"),stderr_sha256=b.filehash(out/"stderr.txt")),"result_digest")
    b.publish(out/"result.json",result)
    print(json.dumps({k:result[k] for k in ("qualification_id","status","exit_code","passed_tests","result_digest")}))
    return 0 if ok else 1


if __name__=="__main__":
    raise SystemExit(main())
