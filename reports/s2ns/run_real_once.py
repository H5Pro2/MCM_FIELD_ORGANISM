"""Authorized single NS main call, one offline verification, then evaluation."""
import json
from pathlib import Path

from tools import _s2ns_private_run as run
from tools import _s2ns_private_run_verification as verification
from tools import _s2ns_private_run_evaluation as evaluation

RUN_ID = "s2ns-real-two-view-memory-20260908-01"


def main():
    parent = run.ROOT/"reports/s2ns"
    target = parent/RUN_ID
    run.s.require(not target.exists(),"RUN_DIRECTORY_ALREADY_EXISTS")
    run.s.require(not any((run.MAIN_GATE,run.s.MAIN_GATE,run.b.MAIN_GATE,run.s.profile.MAIN_GATE)),"GATE_NOT_CLOSED")
    before = run.code_hashes()
    source_files = {name:run.io.filehash(run.src.SEAL_DIR/name) for name in
        ("execution-plan.json","evaluation-plan.json","seal.json","verification.json")}
    qualifications = {name:run.io.filehash(parent/name/"result.json") for name in
        ("s2ns-two-view-qualification-20260908-01",run.QUAL_ID)}
    prereg = run.io.sealed(dict(run_id=RUN_ID,output_directory=str(target),
        caller_sha256=run.io.filehash(Path(__file__)),code_hashes=before,
        source_files=source_files,qualification_files=qualifications,
        main_calls=1,verification_calls=1,evaluation_calls_max=1,retry=False,
        limits=run.LIMITS,verification_limits=run.VERIFY_LIMITS,
        index_binding=run.src.SCHEMA,raw_payloads_persisted=False,
        field_runtime_hypothesis_application=False),"preregistration_digest")
    run.io.atomic_write(parent/(RUN_ID+".preregistration.json"),prereg,65536)
    phase = "MAIN"
    calls = dict(main=0,verification=0,evaluation=0)
    status,failure = "NOT_EVALUABLE",None
    try:
        run.MAIN_GATE = True
        calls["main"] += 1
        try:
            path = run.run_main_once(run_id=RUN_ID)
        finally:
            run.MAIN_GATE = False
        record = json.loads(path.read_bytes())
        phase = "VERIFICATION"
        # Metadata only. The verifier never regenerates payloads or memory.
        plan = json.loads((run.src.SEAL_DIR/"execution-plan.json").read_bytes())
        calls["verification"] += 1
        proof_path = verification.verify_file_once(path,plan=plan,config=run.s.profile.build_config())
        proof = json.loads(proof_path.read_bytes())
        if record["status"] == proof["status"] == "RECORDING_COMPLETE" and proof["evaluation_allowed"]:
            phase = "EVALUATION"
            evaluation_plan = json.loads((run.src.SEAL_DIR/"evaluation-plan.json").read_bytes())
            calls["evaluation"] += 1
            evaluation.evaluate_file_once(path,plan=plan,evaluation_plan=evaluation_plan)
            status = "TECHNICALLY_COMPLETE_FUNCTION_EVALUATED"
        else:
            failure = dict(record_status=record["status"],record_failure=record.get("failure"),
                verification_status=proof["status"],verification_code=proof.get("code"))
    except Exception as exc:
        failure = dict(phase=phase,error_class=type(exc).__name__,code=getattr(exc,"code","TECHNICAL_EXECUTION_ERROR"))
    finally:
        run.MAIN_GATE = run.s.MAIN_GATE = run.b.MAIN_GATE = run.s.profile.MAIN_GATE = False
    after = run.code_hashes()
    files_after = {name:run.io.filehash(run.src.SEAL_DIR/name) for name in source_files}
    run.s.require(before == after and source_files == files_after,"SOURCE_FILES_CHANGED")
    result = run.io.sealed(dict(run_id=RUN_ID,status=status,calls=calls,failure=failure,
        preregistration_digest=prereg["preregistration_digest"],code_before=before,code_after=after,
        historical_source_files_before=source_files,historical_source_files_after=files_after,
        files={p.name:dict(sha256=run.io.filehash(p),bytes=p.stat().st_size) for p in
            (target/"recording.json",target/"verification.json",target/"evaluation.json") if p.exists()},
        gates_after=dict(main=run.MAIN_GATE,logic=run.s.MAIN_GATE,sources=run.b.MAIN_GATE,profile=run.s.profile.MAIN_GATE),
        retry=False),"execution_digest")
    run.io.atomic_write(parent/(RUN_ID+".execution.json"),result,65536)
    print(json.dumps({k:result[k] for k in ("run_id","status","calls","failure","files","gates_after","execution_digest")}))
    return 0 if status == "TECHNICALLY_COMPLETE_FUNCTION_EVALUATED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
