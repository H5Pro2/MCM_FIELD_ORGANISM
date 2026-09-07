"""One authorized NH call; no source, runtime, rule or evaluator modifications."""

import json
from pathlib import Path
import sys

from tools import _s2nh_private_runtime_binding as run
from tools import _s2nh_private_runtime_verification as verify

ID = "s2nh-runtime-comparison-20260907-01"
OUT = run.ROOT / "reports/s2nh" / ID


def main():
    run.require(Path.cwd().resolve()==run.ROOT and not OUT.exists(),"WORKSPACE_OR_OUTPUT_INVALID")
    run.require(not run.MAIN_GATE and not run.ng.MAIN_GATE,"GATE_ALREADY_OPEN")
    before=run.watched()
    caller_sha=run.source.filehash(Path(__file__))
    bound=run.load_execution()
    config=run.ng.ne.make_config()
    record=proof=functional=None
    phase="MAIN_CALL"
    failure=None
    try:
        run.MAIN_GATE=True
        try:
            record=run.run_main_once(ID,OUT)
        finally:
            run.MAIN_GATE=False
            run.ng.MAIN_GATE=False
        phase="READ_ONLY_VERIFICATION"
        proof=verify.verify_once(OUT/"recording.json",bound,config)
        if record["status"]==proof["status"]=="RECORDING_COMPLETE" and proof["evidence_valid"] and proof["file_unchanged"]:
            phase="EVALUATION"
            # The file receipt wraps the qualified verification payload, not its digest domain.
            file_fields={"result_file_sha256","file_unchanged","verification_calls","file_verification_digest"}
            inner_proof={k:v for k,v in proof.items() if k not in file_fields}
            functional=verify.evaluate(record,inner_proof,bound,run.load_evaluation(),config)
            run.ng.ne.atomic_write(OUT/"evaluation.json",functional)
    except Exception as error:
        failure=dict(phase=phase,error_class=type(error).__name__,code=getattr(error,"code","CALL_BOUNDARY_ERROR"))
    finally:
        run.MAIN_GATE=False
        run.ng.MAIN_GATE=False
    after=run.watched()
    report=run.source.sealed(dict(run_id=ID,main_calls=1,
        status="NOT_EVALUABLE" if failure is not None or proof is None else proof["status"],
        main_gate_after=run.MAIN_GATE,ng_gate_after=run.ng.MAIN_GATE,
        caller_sha256_before=caller_sha,caller_sha256_after=run.source.filehash(Path(__file__)),
        source_hashes_unchanged=before==after,python=sys.version,failure=failure,
        record_digest=None if record is None else record["record_digest"],
        file_verification_digest=None if proof is None else proof["file_verification_digest"],
        evaluation_digest=None if functional is None else functional["evaluation_digest"]),"call_digest")
    run.ng.ne.atomic_write(OUT/"call.json",report)
    print(json.dumps(report,sort_keys=True))
    return 0 if functional is not None and failure is None and before==after else 1


if __name__=="__main__":
    raise SystemExit(main())
