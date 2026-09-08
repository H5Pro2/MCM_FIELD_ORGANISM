"""Single preregistered neutral logic qualification; no sealed payload access."""
import ast
import json
import subprocess
import sys
from tools import _s2ns_private_source_binding as io

RUN_ID = "s2ns-two-view-qualification-20260908-01"
TEST = "tests/test_s2ns_private_two_view.py"
OWN = ("tools/_s2ns_private_two_view.py", "tools/_s2ns_private_direct.py",
       "tools/_s2ns_private_evaluation.py", TEST, "reports/s2ns/qualify_two_view_once.py",
       "reports/s2ns/S2NS_ZWEI_SICHTEN_QUALIFIKATIONSBINDUNG.md")
HISTORICAL = ("tools/_s2nq_private_mask_scan.py", "tools/_s2nq_private_direct.py",
    "tools/_s2ne_private_auditory_transfer.py", "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tests/test_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "mcm_field_organism/_ppb1_reference.py",
    "reports/s2ns/s2ns-source-preseal-20260908-01/execution-plan.json",
    "reports/s2ns/s2ns-source-preseal-20260908-01/evaluation-plan.json",
    "reports/s2ns/s2ns-source-preseal-20260908-01/seal.json",
    "reports/s2ns/s2ns-source-preseal-20260908-01/verification.json")


def watched():
    return {**io.watched(), **{p:io.filehash(io.ROOT/p) for p in OWN+HISTORICAL}}


def main():
    out = io.ROOT/"reports/s2ns"/RUN_ID
    out.mkdir(exist_ok=False)
    before = watched()
    inventory = []
    forbidden = {"analyze", "project_auditory_half_v1", "advance_s2jv_atomic", "preseal_once",
                 "pcm_bytes", "rgb", "run_main_once", "materialize", "consume_once"}
    for path in OWN:
        if not path.endswith(".py"):
            continue
        tree = ast.parse((io.ROOT/path).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                name = getattr(node.func,"attr",getattr(node.func,"id",None))
                io.require(name not in forbidden,"FORBIDDEN_QUALIFICATION_CALL")
            if path == TEST and isinstance(node,ast.FunctionDef) and node.name.startswith("test_"):
                inventory.append(node.name)
    io.require(len(inventory) == len(set(inventory)) == 24 and io.MAIN_GATE is False,"QUALIFICATION_BINDING_INVALID")
    command = [sys.executable,"-m","unittest","tests.test_s2ns_private_two_view","-v","-f"]
    io.publish(out/"preregistration.json",dict(run_id=RUN_ID,command=command,cwd=str(io.ROOT),
        expected_tests=24,test_ids=["tests.test_s2ns_private_two_view.TwoViewTests."+n for n in sorted(inventory)],
        hashes_before=before,environment=io.environment(),test_calls=1,retry=False,
        limits=dict(execution_scans=192,execution_rows=3840,execution_band_differences=28800,
            verification_scans=96,verification_rows=1920,verification_band_differences=28800,
            execution_equality_comparisons=4320,verification_equality_comparisons=4320,historical_scans=1,
            scan_bytes=32768,result_bytes=49152,shared_bytes=32768,state_bytes=98304,total_bytes=4194304,
            ns_payloads=0,formation_calls=0,receptor_calls=0,nj_calls=0,field_calls=0,runtime_calls=0),
        boundary="Synthetic native states and generation/endpoint evidence only; no verified real formation-chain construction."),65536)
    import os
    env = {**os.environ,"S2NS_TWO_VIEW_QUAL_DIR":str(out)}
    process = subprocess.run(command,cwd=io.ROOT,env=env,capture_output=True,check=False)
    for name,data in (("stdout.txt",process.stdout),("stderr.txt",process.stderr)):
        with (out/name).open("xb") as handle:
            handle.write(data)
    after = watched()
    transcript = (process.stdout+process.stderr).decode("utf-8",errors="replace")
    metrics = [json.loads(line.removeprefix("NS_TWO_VIEW_METRICS ")) for line in transcript.splitlines()
               if line.startswith("NS_TWO_VIEW_METRICS ")]
    passed = process.returncode == 0 and "Ran 24 tests" in transcript and transcript.rstrip().endswith("OK") and before == after and len(metrics) == 1
    result = io.sealed(dict(run_id=RUN_ID,status="S2NS_TWO_VIEW_LOGIC_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=process.returncode,expected_tests=24,passed_tests=24 if passed else None,test_calls=1,
        hashes_before=before,hashes_after=after,metrics=metrics,
        stdout_sha256=io.filehash(out/"stdout.txt"),stderr_sha256=io.filehash(out/"stderr.txt"),
        main_gate_after=False,main_history_calls=0,ns_payloads=0,retry=False),"result_digest")
    io.publish(out/"result.json",result,65536)
    print(json.dumps({k:result[k] for k in ("run_id","status","exit_code","passed_tests","result_digest")}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
