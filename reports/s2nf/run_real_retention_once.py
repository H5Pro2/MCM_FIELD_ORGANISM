"""Archival caller for the authorized single NF run; no rule changes."""

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "s2nf-real-retention-under-competition-20260906-01"
BASE = ROOT / "reports/s2nf"
TARGET = BASE / RUN_ID
PREREG = BASE / (RUN_ID + "-preregistration.json")
OUTCOME = BASE / (RUN_ID + "-outcome.json")
QUALIFICATION = BASE / "s2nf-run-binding-qualification-20260906-02/result.json"
QUALIFICATION_SHA256 = "9384d58824fd42b32662586eb289ad96d9e93830302b4af11c49b7fce56c2980"


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def write(path, value):
    with path.open("xb") as handle:
        handle.write((json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())


def main():
    if Path.cwd().resolve() != ROOT or any(p.exists() for p in (TARGET, PREREG, OUTCOME)):
        raise RuntimeError("one-shot target already used or workspace differs")
    before, run = {}, None
    phase = "QUALIFIED_BINDINGS"
    calls = dict(main=0, verification=0, evaluation=0, tests=0, receptor_preflights=0)
    result = dict(run_id=RUN_ID, status="NOT_EVALUABLE", calls=calls)
    try:
        if sha(QUALIFICATION) != QUALIFICATION_SHA256:
            raise RuntimeError("qualification binding differs")
        qualified = json.loads(QUALIFICATION.read_bytes())
        protected = qualified["hashes_after"]
        if qualified["status"] != "S2NF_RUN_BINDING_QUALIFIED" or any(sha(ROOT / p) != h for p, h in protected.items()):
            raise RuntimeError("qualified source binding differs")
        for name, expected in qualified["evidence_hashes"].items():
            if sha(QUALIFICATION.parent / name) != expected:
                raise RuntimeError("qualification evidence differs")
        from tools import _s2nf_private_run as run
        from tools import _s2nf_private_run_verification as verification
        from tools import _s2nf_private_run_evaluation as evaluation
        if run.MAIN_GATE is not False or run.ne.MAIN_GATE is not False or run.ne.arms.MAIN_GATE is not False:
            raise RuntimeError("gate was not closed")
        execution = run.sources.load_plan()
        if execution["generator_identity"] != run.sources.binding.identity():
            raise RuntimeError("generator or interpreter binding differs")
        config = run.ne.make_config()
        plan = [asdict(e) for e in run.sources.events_from_plan(execution)]
        paths = set(protected) | set(run.sources.source_hashes()) | {
            Path(__file__).relative_to(ROOT).as_posix()}
        paths |= {p.relative_to(ROOT).as_posix() for p in QUALIFICATION.parent.iterdir() if p.is_file()}
        before = {p: sha(ROOT / p) for p in sorted(paths)}
        write(PREREG, dict(run_id=RUN_ID, output_directory=str(TARGET), output_directory_existed=False,
            git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            command=[sys.executable, "-B", "-m", "reports.s2nf.run_real_retention_once"],
            python=sys.version, interpreter_sha256=sha(Path(sys.executable)),
            qualification_sha256=QUALIFICATION_SHA256, config_digest=config.config_digest,
            execution_digest=execution["execution_digest"], plan=plan, plan_digest=run.digest(plan),
            source_hashes_before=before, main_gate_before=False,
            limits=dict(histories=2, formations=3, cues=10, events=13, arms=40, audio_analyses=13,
                visual_analyses=3, receptor_values=1488, slot_visits=800, band_differences=19200,
                equality_comparisons=1920, retrieval_comparisons=21120, verification_comparisons=21120,
                formation_l1_limit=10656, recording_bytes=4194304, arm_bytes_exclusive=32768),
            call_limits=dict(main=1, verification=1, evaluation_if_verified=1, tests=0, receptor_preflights=0),
            retry=False))
        phase = "MAIN"
        try:
            run.MAIN_GATE = True
            calls["main"] += 1
            path = run.run_main_once(run_id=RUN_ID)
        finally:
            run.MAIN_GATE = False
        record = json.loads(path.read_bytes())
        result.update(recording_status=record["status"], recording_digest=record["record_digest"],
            recording_sha256=sha(path), recording_bytes=path.stat().st_size, counters=record["counts"],
            attempts=record["attempts"], execution_failure=record["failure"])
        phase = "VERIFICATION"
        calls["verification"] += 1
        proof_path = verification.verify_main_once(path)
        proof = json.loads(proof_path.read_bytes())
        result.update(verification_status=proof["status"], verification_sha256=sha(proof_path),
            recording_unchanged=sha(path) == result["recording_sha256"])
        if record["status"] == proof["status"] == "RECORDING_COMPLETE":
            phase = "EVALUATION"
            calls["evaluation"] += 1
            evaluated_path = evaluation.evaluate_main_once(path)
            assessed = json.loads(evaluated_path.read_bytes())
            result.update(status=assessed["status"], evaluation_sha256=sha(evaluated_path),
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
            historical_gates_after=None if run is None else [run.ne.MAIN_GATE, run.ne.arms.MAIN_GATE])
        if not result["source_hashes_unchanged"]:
            result["status"] = "NOT_EVALUABLE"
        write(OUTCOME, result)
    print(json.dumps({k: v for k, v in result.items() if k != "source_hashes_after"}, indent=2))
    return 1 if result["status"] == "NOT_EVALUABLE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
