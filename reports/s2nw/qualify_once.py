"""Single neutral NW source qualification, bound before starting unittest."""
import ast
import json
import subprocess
import sys
from tools import _s2nw_private_source_binding as b


def main():
    out = b.QUAL_DIR
    out.mkdir(exist_ok=False)
    before = b.watched()
    tree = ast.parse((b.ROOT/"tests/test_s2nw_private_source_binding.py").read_text(encoding="utf-8"))
    names = sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(names)==len(set(names))==20,"TEST_INVENTORY_INVALID")
    command = [sys.executable,"-m","unittest","tests.test_s2nw_private_source_binding","-v","-f"]
    b.publish(out/"preregistration.json",dict(run_id=b.QUAL_ID,command=command,cwd=str(b.ROOT),
        test_ids=["tests.test_s2nw_private_source_binding.SourceTests."+n for n in names],expected_tests=20,
        unittest_calls=1,retry=False,hashes_before=before,environment=b.environment(),
        limits=dict(nw_payloads=0,receptor_calls=0,nj_calls=0,predictions=0,learning_updates=0,error_calculations=0,system_calls=0,
            neutral_generated_samples=6,neutral_generated_bytes=24,max_live_neutral_bytes=12,
            sin_calls=64,metadata_digest_checks=32768),future_limits=b.budgets()),65536)
    process = subprocess.run(command,cwd=b.ROOT,capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as handle:
            handle.write(data)
    after = b.watched()
    transcript = (process.stdout+process.stderr).decode("utf-8",errors="replace")
    passed = process.returncode==0 and "Ran 20 tests" in transcript and transcript.rstrip().endswith("OK") and before==after
    result = b.sealed(dict(run_id=b.QUAL_ID,status="S2NW_SOURCE_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
        expected_tests=20,passed_tests=20 if passed else None,unittest_calls=1,exit_code=process.returncode,
        hashes_before=before,hashes_after=after,nw_payloads_generated=0,receptor_calls=0,nj_calls=0,
        prediction_calls=0,learning_calls=0,error_calls=0,system_calls=0,main_gate_after=b.MAIN_GATE,
        stdout_sha256=b.filehash(out/"stdout.txt"),stderr_sha256=b.filehash(out/"stderr.txt")),"result_digest")
    b.publish(out/"result.json",result,65536)
    print(json.dumps({k:result[k] for k in ("run_id","status","passed_tests","exit_code","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
