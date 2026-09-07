"""Authorized S2-NO call only; no retry, receptor preflight or implementation changes."""

import json
from pathlib import Path
import sys

from tools import _s2no_private_half_materialization as run
from tools import _s2no_private_half_verification as verify

RUN_ID = "s2no-half-runtime-20260907-01"
OUT = run.ROOT/"reports/s2no"/RUN_ID
REGISTRATION = run.ROOT/"reports/s2no"/(RUN_ID+"-preregistration.json")


def gates():
    return dict(NO=run.MAIN_GATE, NG=run.ng.MAIN_GATE, NN=run.nn.MAIN_GATE,
                NH=run.nh.MAIN_GATE, NL=run.nn.profile.MAIN_GATE, SOURCE=run.source.MAIN_GATE)


def main():
    run.require(not OUT.exists() and not REGISTRATION.exists(), "RUN_ID_ALREADY_USED")
    run.require(not any(gates().values()), "GATE_ALREADY_OPEN")
    bound = run.load_execution()
    config = run.nn.profile.build_config()
    hashes = run.watched()
    qualification = json.loads((run.ROOT/"reports/s2no"/run.QUAL_ID/"result.json").read_bytes())
    run.require(qualification["status"] == "S2NO_CONNECTION_QUALIFIED"
                and qualification["hashes_after"] == hashes, "QUALIFICATION_CHANGED")
    run.ng.ne.atomic_write(REGISTRATION, dict(run_id=RUN_ID, sources=hashes,
        execution_digest=bound.payload()["execution_digest"], evaluation_digest=run.nh.EVALUATION_DIGEST,
        profile=run.profile_binding(config), gates_before=gates(),
        caller_sha256=run.source.filehash(Path(__file__)), interpreter_sha256=run.source.filehash(Path(sys.executable)),
        main_calls=1, verification_calls=1, evaluation_calls_if_valid=1, retry=False,
        materialization=dict(audio_windows=24,audio_hops=240,audio_snapshots=231,nj_projections=24,visual_frames=24),
        limits=run.ng.budget(tuple(e["event_type"] for e in bound.payload()["events"]))))
    phase = "MAIN"
    calls = dict(main=0,verification=0,evaluation=0)
    proof = result = evaluation = None
    failure = None
    try:
        run.MAIN_GATE = True
        calls["main"] += 1
        result = run.run_main_once(RUN_ID,OUT)
        phase = "VERIFICATION"
        calls["verification"] += 1
        proof = verify.verify_once(OUT/"recording.json",bound,config)
        if result["status"] == proof["status"] == "RECORDING_COMPLETE" and proof["evidence_valid"] and proof["file_unchanged"]:
            phase = "EVALUATION"
            # Remove only the outer file-verification fields; keep the original proof unchanged.
            inner = {k:v for k,v in proof.items() if k not in
                     ("file_sha256","file_unchanged","verification_calls","file_verification_digest")}
            root = run.nh.load_evaluation()
            calls["evaluation"] += 1
            evaluation = verify.evaluate(result,inner,bound,root,config)
            run.ng.ne.atomic_write(OUT/"evaluation.json",evaluation)
        phase = "CLOSE"
    except Exception as error:
        failure = dict(phase=phase,error_class=type(error).__name__,code=getattr(error,"code","CALLER_TECHNICAL_ERROR"))
    finally:
        run.MAIN_GATE = run.ng.MAIN_GATE = run.nn.MAIN_GATE = False
        run.nh.MAIN_GATE = run.nn.profile.MAIN_GATE = run.source.MAIN_GATE = False
    summary = run.sealed(dict(run_id=RUN_ID,calls=calls,gates_after=gates(),
        sources_unchanged=run.watched()==hashes, failure=failure,
        recording_status=None if result is None else result["status"],
        record_digest=None if result is None else result["record_digest"],
        verification_status=None if proof is None else proof["status"],
        evidence_valid=None if proof is None else proof["evidence_valid"],
        evaluation_digest=None if evaluation is None else evaluation["evaluation_digest"],
        partially_examined_corpus=True, semantic_equivalence_to_historical=False,
        offline_numeric_reconstruction=False),"completion_digest")
    if OUT.exists():
        run.ng.ne.atomic_write(OUT/"completion.json",summary)
    print(json.dumps(summary,sort_keys=True))
    return 0 if failure is None and proof is not None and proof["evidence_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
