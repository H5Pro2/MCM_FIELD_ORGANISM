"""Archival caller for the expressly authorized single S2-NE transfer."""

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "s2ne-real-auditory-transfer-20260906-01"
BASE = ROOT / "reports/s2ne"
TARGET = BASE / RUN_ID
PREREG = BASE / (RUN_ID + "-preregistration.json")
OUTCOME = BASE / (RUN_ID + "-outcome.json")
QUALIFICATION = BASE / "s2ne-run-completion-qualification-20260906-01/result.json"
QUALIFICATION_SHA256 = "1a5d795b50e94d2290724e8d0de9e3f9daa94beb4cf55e76a4505e20bfba85e2"


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def write(path, value):
    with path.open("xb") as handle:
        handle.write((json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())


def main():
    if Path.cwd().resolve() != ROOT or TARGET.exists() or PREREG.exists() or OUTCOME.exists():
        raise RuntimeError("one-shot target already used or workspace differs")
    before = {}
    phase = "QUALIFIED_BINDINGS"
    counts = dict(main=0, verification=0, evaluation=0, tests=0, receptor_preflights=0)
    run = None
    result = dict(run_id=RUN_ID, status="NOT_EVALUABLE", calls=counts)
    try:
        if sha(QUALIFICATION) != QUALIFICATION_SHA256:
            raise RuntimeError("qualification binding differs")
        qualification = json.loads(QUALIFICATION.read_bytes())
        protected = qualification["hashes_after"]
        if any(sha(ROOT / p) != h for p, h in protected.items()):
            raise RuntimeError("qualified source binding differs")
        from tools import _s2ne_private_run as run
        from tools import _s2ne_private_run_verification as verification
        from tools import _s2ne_private_run_evaluation as evaluation
        if run.MAIN_GATE is not False or run.arms.MAIN_GATE is not False:
            raise RuntimeError("gate was not closed")
        catalog = run.load_catalog()
        config = run.make_config()
        paths = set(protected) | set(run.source_hashes()) | {
            QUALIFICATION.relative_to(ROOT).as_posix(), Path(__file__).relative_to(ROOT).as_posix()}
        before = {p: sha(ROOT / p) for p in sorted(paths)}
        plan = [asdict(e) for e in run.EVENTS]
        write(PREREG, dict(
            run_id=RUN_ID, output_directory=str(TARGET), output_directory_existed=False,
            git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            command=[sys.executable, "-B", "-m", "reports.s2ne.run_real_transfer_once"],
            python=sys.version, interpreter_sha256=sha(Path(sys.executable)),
            qualification_sha256=QUALIFICATION_SHA256, config_digest=config.config_digest,
            catalog_digest=run.digest(catalog), plan=plan, plan_digest=run.digest(plan),
            source_hashes_before=before, main_gate_before=False,
            limits=dict(formations=20, cues=13, arms=52, slot_visits=1040,
                        band_differences=24960, equality_comparisons=2496,
                        retrieval_comparisons=27456, verification_comparisons=27456,
                        formation_l1_limit=71040, recording_bytes=4194304),
            call_limits=dict(main=1, verification=1, evaluation_if_verified=1,
                             tests=0, receptor_preflights=0), retry=False))
        phase = "MAIN"
        try:
            run.MAIN_GATE = True
            counts["main"] += 1
            recording_path = run.run_main_once(run_id=RUN_ID)
        finally:
            run.MAIN_GATE = False
        recording = json.loads(recording_path.read_bytes())
        result.update(recording_status=recording["status"], recording_digest=recording["record_digest"],
                      recording_sha256=sha(recording_path), recording_bytes=recording_path.stat().st_size,
                      counters=recording["counts"], attempts=recording["attempts"],
                      execution_failure=recording["failure"])
        phase = "VERIFICATION"
        counts["verification"] += 1
        verification_path = verification.verify_main_once(recording_path)
        proof = json.loads(verification_path.read_bytes())
        result.update(verification_status=proof["status"], verification_sha256=sha(verification_path),
                      recording_unchanged=sha(recording_path) == result["recording_sha256"])
        if recording["status"] == proof["status"] == "RECORDING_COMPLETE":
            phase = "EVALUATION"
            counts["evaluation"] += 1
            evaluation_path = evaluation.evaluate_main_once(recording_path, verification_path)
            assessed = json.loads(evaluation_path.read_bytes())
            result.update(status=assessed["status"], evaluation_sha256=sha(evaluation_path),
                          evaluation_digest=assessed["evaluation_digest"])
        else:
            result["evaluation_status"] = "NOT_PERFORMED"
    except Exception as error:
        result["caller_failure"] = dict(phase=phase, error_class=type(error).__name__,
                                        code=getattr(error, "code", "CALLER_BINDING_OR_EXECUTION_ERROR"))
    finally:
        if run is not None:
            run.MAIN_GATE = False
        after = {p: sha(ROOT / p) if (ROOT / p).is_file() else None for p in before}
        result.update(source_hashes_after=after, source_hashes_unchanged=bool(before) and before == after,
                      main_gate_after=False if run is None else run.MAIN_GATE,
                      qualified_arm_gate_after=None if run is None else run.arms.MAIN_GATE)
        if not result["source_hashes_unchanged"]:
            result["status"] = "NOT_EVALUABLE"
        write(OUTCOME, result)
    print(json.dumps({k: v for k, v in result.items() if k != "source_hashes_after"}, indent=2))
    return 0 if result["status"] in ("CONFIRMED", "FALSIFIED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
