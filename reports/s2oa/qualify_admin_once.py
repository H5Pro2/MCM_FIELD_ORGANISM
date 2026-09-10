"""One preregistered neutral administrative qualification, no payload calls."""
import ast
import json
import subprocess
import sys
from tools import _s2oa_private_administrative_binding as b


def main():
    out = b.QUAL_DIR
    out.mkdir(exist_ok=False)
    before = b.watched()
    tree = ast.parse((b.ROOT/"tests/test_s2oa_private_administrative_binding.py").read_text(encoding="utf-8"))
    names = sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(names) == len(set(names)) == 20,"TEST_INVENTORY_INVALID")
    command = [sys.executable,"-m","unittest","tests.test_s2oa_private_administrative_binding","-v"]
    pr = dict(run_id=b.QUAL_ID,test_ids=names,expected_tests=20,unittest_calls=1,command=command,
              hashes=before,limits=b.LIMITS,reservations=b.RESERVES,retry=False,
              python=sys.version,interpreter_sha256=b.filehash(b.Path(sys.executable)),
              oa_payload_calls=0,receptor_calls=0,nj_calls=0,main_gate=False,
              real_data_reads_in_tests=False,source_and_system_import_block=True)
    b.publish(out/"preregistration.json",pr)
    proc = subprocess.run(command,cwd=b.ROOT,capture_output=True,check=False)
    for name,raw in (("stdout.txt",proc.stdout),("stderr.txt",proc.stderr)):
        with (out/name).open("xb") as f:
            f.write(raw)
    after = b.watched()
    transcript = (proc.stdout+proc.stderr).decode("utf-8",errors="replace")
    passed = proc.returncode == 0 and "Ran 20 tests" in transcript and transcript.rstrip().endswith("OK") and before == after
    result = b.sealed(dict(run_id=b.QUAL_ID,status="S2OA_ADMIN_QUALIFIED" if passed else "NOT_QUALIFIED",
        passed_tests=20 if passed else None,expected_tests=20,exit_code=proc.returncode,unittest_calls=1,
        hashes_before=before,hashes_after=after,preregistration_sha256=b.filehash(out/"preregistration.json"),
        stdout_sha256=b.filehash(out/"stdout.txt"),stderr_sha256=b.filehash(out/"stderr.txt"),
        payload_generation_calls=0,receptor_calls=0,nj_calls=0,main_gate_after=False),"result_digest")
    b.ledger({"preregistration":len(b.canonical(pr)),"result":len(b.canonical(result)),
              "stdout":len(proc.stdout),"stderr":len(proc.stderr)}, {})
    b.publish(out/"result.json",result)
    print(json.dumps({k:result[k] for k in ("run_id","status","passed_tests","result_digest")}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
