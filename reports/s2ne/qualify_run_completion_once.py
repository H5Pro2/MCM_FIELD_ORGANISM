"""One preregistered qualification of the added bounded execution boundary."""

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
QUALIFICATION_ID = "s2ne-run-completion-qualification-20260906-01"
OUT = ROOT / "reports/s2ne" / QUALIFICATION_ID
TEST = "tests/test_s2ne_private_run_completion.py"
MODULE = "tests.test_s2ne_private_run_completion"
NEW = (
    "tools/_s2ne_private_run.py",
    "tools/_s2ne_private_run_verification.py",
    "tools/_s2ne_private_run_evaluation.py",
    TEST,
    "reports/s2ne/qualify_run_completion_once.py",
)
PRIOR = ROOT / "reports/s2ne/s2ne-private-memory-transfer-qualification-20260906-01"


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def write(name, value):
    with (OUT / name).open("xb") as handle:
        handle.write((json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8"))


def main():
    if Path.cwd().resolve() != ROOT or OUT.exists():
        raise RuntimeError("qualification root unavailable")
    OUT.mkdir()
    previous = json.loads((PRIOR / "result.json").read_bytes())
    protected = previous["hashes_after"]
    trees = {p: ast.parse((ROOT / p).read_text(encoding="utf-8-sig")) for p in NEW}
    methods = [n.name for n in ast.walk(trees[TEST]) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    gates = [n.value for n in trees[NEW[0]].body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "MAIN_GATE" for t in n.targets)]
    rows = [ast.literal_eval(n.value) for n in trees[NEW[0]].body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "_ROWS" for t in n.targets)]
    if (len(methods) != 12 or len(set(methods)) != 12 or len(gates) != 1
            or ast.literal_eval(gates[0]) is not False or len(rows) != 1
            or len(rows[0]) != 33 or sum(r[2] is not None for r in rows[0]) != 20
            or any(sha(ROOT / p) != h for p, h in protected.items())):
        write("preflight-error.json", dict(status="NOT_QUALIFIED", phase="STATIC_PREFLIGHT"))
        return 2
    forbidden = {"advance_s2jv_atomic", "retrieve", "direct_retrieve", "analyze", "run_main_once"}
    calls = {n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id if isinstance(n.func, ast.Name) else ""
             for n in ast.walk(trees[NEW[1]]) if isinstance(n, ast.Call)}
    if calls & forbidden:
        raise RuntimeError("verification contains prohibited execution")
    paths = sorted(set(protected) | set(NEW) | {p.relative_to(ROOT).as_posix() for p in PRIOR.iterdir() if p.is_file()})
    before = {p: sha(ROOT / p) for p in paths}
    command = [sys.executable, "-m", "unittest", MODULE, "-v"]
    write("preregistration.json", dict(
        qualification_id=QUALIFICATION_ID, command=command, cwd=str(ROOT),
        python=sys.version, interpreter_sha256=sha(Path(sys.executable)),
        test_ids=[MODULE + ".CompletionQualification." + m for m in sorted(methods)],
        test_count=12, unittest_call_limit=1, retry=False, old_18_tests_repeated=False,
        hashes_before=before, main_gate=False,
        neutral_limits=dict(formations=2, arm_calls=16, receptor_calls=0, field_calls=0,
                            runtime_calls=0, main_history_calls=0, events_per_neutral_recording=5),
        main_limits=dict(formations=20, cues=13, arms=52, slot_visits=1040,
                         band_differences=24960, equality_comparisons=2496,
                         retrieval_comparisons=27456, verification_comparisons=27456,
                         recording_bytes=4194304, arm_bytes_exclusive=32768),
        static_preflight=dict(syntax=True, unique_test_ids=True, literal_33_event_plan=True,
                              protected_hashes_unchanged=True, verifier_without_execution=True)))
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "S2NE_QUALIFICATION_ARTIFACTS": str(OUT)}
    completed = subprocess.run(command, cwd=ROOT, env=env, capture_output=True)
    (OUT / "stdout.txt").write_bytes(completed.stdout)
    (OUT / "stderr.txt").write_bytes(completed.stderr)
    after = {p: sha(ROOT / p) for p in paths}
    stdout, stderr = completed.stdout.decode("utf-8"), completed.stderr.decode("utf-8")
    lines = [line.split("=", 1)[1] for line in stdout.splitlines() if line.startswith("S2NE_COMPLETION_METRICS=")]
    metrics = json.loads(lines[0]) if len(lines) == 1 else None
    passed = (completed.returncode == 0 and "Ran 12 tests" in stderr and stderr.rstrip().endswith("OK")
              and before == after and metrics is not None and metrics["main_gate"] is False
              and metrics["technical_status"] == metrics["verification_status"] == "RECORDING_COMPLETE")
    evidence = {p.name: sha(p) for p in OUT.iterdir() if p.is_file()}
    result = dict(qualification_id=QUALIFICATION_ID,
                  status="S2NE_RUN_COMPLETION_QUALIFIED" if passed else "NOT_QUALIFIED",
                  exit_code=completed.returncode, test_count=12, unittest_calls=1, retry=False,
                  hashes_unchanged=before == after, hashes_after=after, evidence_hashes=evidence,
                  main_gate=False, neutral_metrics=metrics, old_18_tests_repeated=False)
    write("result.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("hashes_after", "evidence_hashes")}, indent=2))
    print(stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
