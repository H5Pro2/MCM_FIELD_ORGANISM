"""Authorized single NQ invocation; no tests, pre-materialization or retry."""
import json
import sys

from tools import _s2nq_private_run as run
from tools import _s2nq_private_verification as verifier
from tools import _s2nq_private_evaluation as evaluator

RUN_ID="s2nq-real-mask-memory-transfer-20260908-01"
PARENT=run.ROOT/"reports/s2nq"
QUAL=PARENT/"s2nq-variation-evaluation-qualification-20260908-01/result.json"
QUAL_DIGEST="a7c9e4895ff09867dbbbb6367962238914af50de4e9656fefe8db3232be45525"


def main():
    target=PARENT/RUN_ID
    authorization=PARENT/(RUN_ID+".authorization.json")
    completion=PARENT/(RUN_ID+".completion.json")
    run.s.require(not target.exists() and not authorization.exists() and not completion.exists(),"RUN_ID_USED")
    run.s.require(run.MAIN_GATE is False,"GATE_ALREADY_OPEN")
    q=json.loads(QUAL.read_bytes())
    run.s.require(q["result_digest"]==QUAL_DIGEST==run.s.digest({k:v for k,v in q.items() if k!="result_digest"})
        and q["status"]=="S2NQ_VARIATION_EVALUATION_QUALIFIED"
        and q["hashes_before"]==q["hashes_after"],"QUALIFICATION_INVALID")
    hashes=run.code_hashes()
    run.s.require(all(q["hashes_after"][p]==h for p,h in hashes.items()),"QUALIFIED_CODE_CHANGED")
    binding=run.io.sealed(dict(run_id=RUN_ID,source_commit="7945a4c",output_directory=str(target),
        command=[sys.executable,"-m","reports.s2nq.run_transfer_once"],python_version=sys.version,
        python_sha256=run.io.filehash(sys.executable),invocation_sha256=run.io.filehash(__file__),
        qualification_digest=QUAL_DIGEST,qualification_sha256=run.io.filehash(QUAL),code_hashes=hashes,
        plan_digest=run.s.digest([run.asdict(e) for e in run.sources.EVENTS]),
        execution_limits=run.LIMITS,verification_limits=run.VERIFY_LIMITS,
        main_calls=1,verification_calls=1,evaluation_calls_max=1,retry=False,gate_before=False),"authorization_digest")
    run.io.atomic_write(authorization,binding,65536)
    calls=dict(main=0,verification=0,evaluation=0)
    phase="MAIN"
    outcome=dict(recording_status=None,verification_status=None,evaluation_status=None,failure=None)
    try:
        run.MAIN_GATE=True
        try:
            calls["main"]+=1
            path=run.run_main_once(run_id=RUN_ID)
        finally:
            run.MAIN_GATE=False
        recording=json.loads(path.read_bytes())
        outcome["recording_status"]=recording["status"]
        phase="VERIFICATION"
        config=run.s.profile.build_config()
        catalog=run.sources.load_catalog()
        calls["verification"]+=1
        proof_path=verifier.verify_file_once(path,events=run.sources.EVENTS,catalog=catalog,config=config)
        proof=json.loads(proof_path.read_bytes())
        outcome["verification_status"]=proof["status"]
        if recording["status"]==proof["status"]=="RECORDING_COMPLETE" and proof["file_unchanged"]:
            phase="EVALUATION"
            calls["evaluation"]+=1
            result=evaluator.evaluate_file_once(path)
            outcome["evaluation_status"]=result["status"]
    except Exception as exc:
        outcome["failure"]=dict(phase=phase,error_class=type(exc).__name__,
            code=exc.code if isinstance(exc,run.s.S2NQError) else "TECHNICAL_EXECUTION_ERROR")
    finally:
        run.MAIN_GATE=False
    after=run.code_hashes()
    done=run.io.sealed(dict(run_id=RUN_ID,authorization_digest=binding["authorization_digest"],
        calls=calls,**outcome,gate_after=run.MAIN_GATE,qualified_code_unchanged=after==hashes,
        files={name:run.io.filehash(target/name) for name in ("recording.json","verification.json","evaluation.json")
               if (target/name).is_file()}),"completion_digest")
    run.io.atomic_write(completion,done,65536)
    print(json.dumps(done,sort_keys=True))
    return 0 if outcome["evaluation_status"]=="EVALUATED" and outcome["failure"] is None and after==hashes else 1


if __name__=="__main__":
    raise SystemExit(main())
