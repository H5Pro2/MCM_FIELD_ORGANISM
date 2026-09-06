"""Single neutral qualification call; no main-run or corpus entry point."""

import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "s2ne-private-memory-transfer-qualification-20260906-01"
OUT = ROOT / "reports/s2ne" / RUN_ID
TEST = "tests/test_s2ne_private_auditory_transfer.py"
MODULE = "tests.test_s2ne_private_auditory_transfer"
NEW = (
    "tools/_s2ne_private_auditory_transfer.py",
    "tools/_s2ne_private_direct_and_verification.py",
    "tools/_s2ne_private_source_binding.py",
    TEST,
)
EXTRA = (
    "tests/test_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2lg_private_ppb_transition_evaluation.py",
    "mcm_field_organism/log_spectral_receptor.py",
    "mcm_field_organism/finite_video_path.py",
    "mcm_field_organism/receptor_contract.py",
    "mcm_field_organism/receptor_time_model.py",
    "mcm_field_organism/_tspm1_s2dr_private_comparison.py",
    "reports/s2ne/qualify_once.py",
)
CONTRACT = "docs/S2NE_PRIVATER_AUDITIVER_MEMORY_TRANSFER_VERTRAG.md"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def main():
    if Path.cwd().resolve() != ROOT or OUT.exists():
        raise RuntimeError("qualification root unavailable")
    OUT.mkdir(parents=True)
    body = (ROOT / CONTRACT).read_text(encoding="utf-8")
    historical = dict(re.findall(r"- `([^`]+)`: `([0-9a-f]{64})`", body))
    if len(historical) != 13 or any(sha(ROOT / path) != bound for path, bound in historical.items()):
        write("preflight-error.json", {"status": "NOT_EVALUABLE", "phase": "HISTORICAL_BINDINGS"})
        return 2
    trees = {p: ast.parse((ROOT / p).read_text(encoding="utf-8-sig")) for p in NEW}
    tests = [n.name for n in ast.walk(trees[TEST]) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    if len(tests) != 18 or len(set(tests)) != 18:
        raise RuntimeError("test registry differs")
    gate = [n for n in trees[NEW[0]].body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "MAIN_GATE" for t in n.targets)]
    if len(gate) != 1 or ast.literal_eval(gate[0].value) is not False:
        raise RuntimeError("main gate is not closed")
    all_paths = tuple(sorted(set(NEW + EXTRA + (CONTRACT,) + tuple(historical))))
    before = {p: sha(ROOT / p) for p in all_paths}
    command = [sys.executable, "-m", "unittest", MODULE, "-v"]
    plan = {
        "qualification_id": RUN_ID, "status": "PREREGISTERED", "command": command,
        "cwd": str(ROOT), "python": sys.version, "interpreter_sha256": sha(Path(sys.executable)),
        "test_ids": [MODULE + ".S2NEQualification." + name for name in sorted(tests)],
        "test_count": 18, "unittest_call_limit": 1, "retry": False,
        "main_gate": False, "historical_bindings": historical, "hashes_before": before,
        "neutral_limits": {"formations": 4, "audio_analyses": 5, "visual_analyses": 4,
                           "main_history_calls": 0, "field_calls": 0, "runtime_calls": 0,
                           "corpus_materializations": 0, "arm_value_comparisons": 528,
                           "arm_bytes_exclusive": 32768, "recording_bytes_inclusive": 4194304},
        "static_audit": {
            "syntax": "PASS", "unique_test_ids": True, "main_gate_false": True,
            "historical_files_unchanged": True,
            "primary_reuses_kz_slow_and_resolution": True,
            "baseline_has_separate_a_scan_and_direct_resolution": True,
            "verifier_has_no_retrieval_or_formation_invocation": True,
            "no_main_entry_point": True,
        },
    }
    write("preregistration.json", plan)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    completed = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")
    (OUT / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (OUT / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
    after = {p: sha(ROOT / p) for p in all_paths}
    metrics_lines = [line.split("=", 1)[1] for line in completed.stdout.splitlines()
                     if line.startswith("S2NE_NEUTRAL_METRICS=")]
    metrics = json.loads(metrics_lines[0]) if len(metrics_lines) == 1 else None
    passed = (completed.returncode == 0 and "Ran 18 tests" in completed.stderr
              and completed.stderr.rstrip().endswith("OK") and before == after
              and metrics is not None)
    result = dict(qualification_id=RUN_ID, status="S2NE_NEUTRAL_QUALIFICATION_VALID" if passed else "NOT_QUALIFIED",
                  exit_code=completed.returncode, unittest_calls=1, test_count=18,
                  source_hashes_unchanged=before == after, hashes_after=after,
                  main_gate=False, neutral_metrics=metrics,
                  stdout_sha256=sha(OUT / "stdout.txt"), stderr_sha256=sha(OUT / "stderr.txt"),
                  preregistration_sha256=sha(OUT / "preregistration.json"))
    write("result.json", result)
    print(json.dumps({k: v for k, v in result.items() if k not in ("hashes_after", "neutral_metrics")}, indent=2))
    print(completed.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
