"""One bounded neutral qualification; never loads the NT materialization."""
import ast
import json
import subprocess
import sys
from tools import _s2nt_private_comparison_run as run

c,b = run.c,run.b


def main():
    out = run.QUAL_DIR
    out.mkdir(exist_ok=False)
    before = run.watched()
    tree = ast.parse((b.ROOT/"tests/test_s2nt_private_comparison.py").read_text(encoding="utf-8"))
    names = sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    c.require(len(names) == len(set(names)) == 18,"TEST_INVENTORY_INVALID")
    c.require(run.MAIN_GATE is False and b.MAIN_GATE is False,"GATE_INVALID")
    command = [sys.executable,"-m","unittest","tests.test_s2nt_private_comparison","-v","-f"]
    b.publish(out/"preregistration.json",dict(run_id=run.QUAL_ID,command=command,cwd=str(b.ROOT),
        test_ids=["tests.test_s2nt_private_comparison.ComparisonQualification."+n for n in names],
        expected_tests=18,unittest_calls=1,retry=False,hashes_before=before,environment=b.environment(),
        real_nt_vector_reads_limit=0,nt_payloads_limit=0,receptor_calls_limit=0,nj_calls_limit=0,system_calls_limit=0,
        comparison_limits=c.LIMITS,max_output_bytes=c.MAX_OUTPUT_BYTES,max_verification_bytes=c.MAX_VERIFICATION_BYTES,
        neutral_suite_limits=dict(complete_comparisons=4,extra_single_pairs=2,verification_attempts=9,
            successful_evaluations=4,direct_order_checks=3,band_differences=9696,primary_equalities=9696,
            offline_halvings=6048,offline_terms=21600,offline_equalities=21600,offline_sums=450,order_checks=99)),65536)
    process = subprocess.run(command,cwd=b.ROOT,capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as handle:
            handle.write(data)
    after = run.watched()
    transcript = (process.stdout+process.stderr).decode("utf-8",errors="replace")
    passed = process.returncode == 0 and "Ran 18 tests" in transcript and transcript.rstrip().endswith("OK") and before == after
    result = b.sealed(dict(run_id=run.QUAL_ID,status="S2NT_COMPARISON_QUALIFIED" if passed else "NOT_QUALIFIED",
        expected_tests=18,passed_tests=18 if passed else None,unittest_calls=1,exit_code=process.returncode,
        hashes_before=before,hashes_after=after,real_nt_vectors_read=0,nt_payloads_generated=0,
        receptor_calls=0,nj_calls=0,system_calls=0,real_nt_comparisons=0,
        main_gate_after=run.MAIN_GATE,source_gate_after=b.MAIN_GATE,retry=False,
        stdout_sha256=b.filehash(out/"stdout.txt"),stderr_sha256=b.filehash(out/"stderr.txt")),"result_digest")
    b.publish(out/"result.json",result,65536)
    print(json.dumps({k:result[k] for k in ("run_id","status","passed_tests","exit_code","result_digest")}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
