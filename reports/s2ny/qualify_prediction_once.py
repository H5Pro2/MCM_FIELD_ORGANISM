"""One preregistered neutral NY qualification; no sealed NY processing."""
import ast
import json
import subprocess
import sys
from tools import _s2ny_private_prediction_run as run

p,b=run.p,run.b


def main():
    out=run.QUAL_DIR
    out.mkdir(exist_ok=False)
    before=run.watched()
    tree=ast.parse((b.ROOT/"tests/test_s2ny_private_prediction.py").read_text(encoding="utf-8"))
    names=sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith("test_"))
    p.require(len(names)==len(set(names))==30,"TEST_INVENTORY_INVALID")
    p.require(run.MAIN_GATE is False and b.MAIN_GATE is False and run.nw.MAIN_GATE is False
        and run.nw.nv.MAIN_GATE is False,"GATE_INVALID")
    command=[sys.executable,"-m","unittest","tests.test_s2ny_private_prediction","-v","-f"]
    b.publish(out/"preregistration.json",dict(run_id=run.QUAL_ID,command=command,cwd=str(b.ROOT),
        test_ids=["tests.test_s2ny_private_prediction.PredictionQualification."+n for n in names],
        expected_tests=30,unittest_calls=1,retry=False,hashes_before=before,environment=b.environment(),
        work_limits=p.limits(),verification_limits=p.verification_limits(),
        output_limits=dict(total=2097152,frozen_payload=4096,binding=65536,verification=262144,evaluation=262144),
        neutral_suite_limits=dict(real_ny_payloads=0,real_ny_analyses=0,real_ny_runs=0,
            complete_synthetic_executions=2,failed_synthetic_executions=1,additional_prefix_streams=24,
            actual_neutral_analyses=5,actual_neutral_nj=5,neutral_pcm_windows_generated=5,
            neutral_pcm_bytes=96000,max_live_pcm_bytes=19200,
            prediction_subtractions=65536,prediction_multiplications=65536,prediction_additions=65536,
            local_differences=32768,local_products=32768,local_additions=32768,local_divisions=256,
            error_terms=131072,offline_halvings=32768,offline_prediction_subtractions=131072,
            offline_prediction_multiplications=131072,offline_prediction_additions=131072,
            offline_local_differences=65536,offline_local_products=65536,offline_local_additions=65536,
            offline_error_terms=196608,offline_mae_sums=4096,offline_gain_checks=4096,
            successful_evaluations=3,strict_condition_evaluations=60,memory_calls=0,field_calls=0,runtime_calls=0),
        real_ny_execution_authorized=False),65536)
    process=subprocess.run(command,cwd=b.ROOT,capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as handle:
            handle.write(data)
    after=run.watched()
    transcript=(process.stdout+process.stderr).decode("utf-8",errors="replace")
    passed=process.returncode==0 and "Ran 30 tests" in transcript and transcript.rstrip().endswith("OK") and before==after
    result=b.sealed(dict(run_id=run.QUAL_ID,status="S2NY_PREDICTION_QUALIFIED" if passed else "NOT_QUALIFIED",
        expected_tests=30,passed_tests=30 if passed else None,unittest_calls=1,exit_code=process.returncode,
        hashes_before=before,hashes_after=after,ny_payloads_generated=0,real_ny_runs=0,
        actual_neutral_analyses=5 if passed else None,actual_neutral_nj=5 if passed else None,
        memory_calls=0,field_calls=0,runtime_calls=0,main_gate_after=run.MAIN_GATE,source_gate_after=b.MAIN_GATE,
        historical_nw_gate_after=run.nw.MAIN_GATE,historical_nv_gate_after=run.nw.nv.MAIN_GATE,
        stdout_sha256=b.filehash(out/"stdout.txt"),stderr_sha256=b.filehash(out/"stderr.txt"),
        neutral_envelope_sha256=b.filehash(out/"neutral-envelope.json") if (out/"neutral-envelope.json").exists() else None),"result_digest")
    b.publish(out/"result.json",result,65536)
    print(json.dumps({k:result[k] for k in ("run_id","status","passed_tests","exit_code","result_digest")}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
