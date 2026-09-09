"""One neutral qualification before any real NU PCM generation."""
import ast
import json
import subprocess
import sys
from tools import _s2nu_private_source_binding as b


def main():
    out = b.QUAL_DIR
    out.mkdir(exist_ok=False)
    before = b.watched()
    tree = ast.parse((b.ROOT/"tests/test_s2nu_private_source_binding.py").read_text(encoding="utf-8"))
    names = sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    b.require(len(names)==len(set(names))==16,"TEST_INVENTORY_INVALID")
    command = [sys.executable,"-m","unittest","tests.test_s2nu_private_source_binding","-v","-f"]
    b.publish(out/"preregistration.json",dict(run_id=b.QUAL_ID,command=command,cwd=str(b.ROOT),
        test_ids=["tests.test_s2nu_private_source_binding.SourceTests."+n for n in names],
        expected_tests=16,unittest_calls=1,retry=False,hashes_before=before,environment=b.environment(),
        limits=dict(nu_payloads=0,receptor_calls=0,nj_calls=0,differences=0,order_evaluations=0,system_calls=0,
            neutral_generated_samples=18,neutral_generated_bytes=72,max_live_neutral_bytes=12,
            sin_calls=512,metadata_digest_checks=32768),future_limits=b.budgets()),65536)
    process = subprocess.run(command,cwd=b.ROOT,capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as handle:
            handle.write(data)
    after = b.watched()
    transcript = (process.stdout+process.stderr).decode("utf-8",errors="replace")
    passed = process.returncode==0 and "Ran 16 tests" in transcript and transcript.rstrip().endswith("OK") and before==after
    result = b.sealed(dict(run_id=b.QUAL_ID,status="S2NU_SOURCE_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED",
        expected_tests=16,passed_tests=16 if passed else None,unittest_calls=1,exit_code=process.returncode,
        hashes_before=before,hashes_after=after,nu_payloads_generated=0,receptor_calls=0,nj_calls=0,difference_calls=0,
        order_evaluations=0,system_calls=0,main_gate_after=b.MAIN_GATE,
        stdout_sha256=b.filehash(out/"stdout.txt"),stderr_sha256=b.filehash(out/"stderr.txt")),"result_digest")
    b.publish(out/"result.json",result,65536)
    print(json.dumps({k:result[k] for k in ("run_id","status","passed_tests","exit_code","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
