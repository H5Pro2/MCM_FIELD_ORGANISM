"""Single neutral NF source-guard qualification; no corpus execution."""

import ast
import json
import os
from pathlib import Path
import subprocess
import sys

from tools import _s2nf_private_source_binding as binding

ROOT = binding.ROOT
QUALIFICATION_ID = "s2nf-run-binding-qualification-20260906-02"
OUT = ROOT / "reports/s2nf" / QUALIFICATION_ID
PREVIOUS = ROOT / "reports/s2nf/s2nf-run-binding-qualification-20260906-01"
MODULE = "tests.test_s2nf_private_run"
TEST = "tests/test_s2nf_private_run.py"
VERIFIER = "tools/_s2nf_private_run_verification.py"
CALLER = "reports/s2nf/qualify_source_guard_once.py"
CHANGED = {VERIFIER, TEST}


def main():
    binding.require(Path.cwd().resolve() == ROOT, "WORKSPACE_INVALID")
    OUT.mkdir(exist_ok=False)
    previous = json.loads((PREVIOUS / "result.json").read_bytes())
    binding.require(previous["status"] == "NOT_QUALIFIED", "HISTORICAL_STATUS_INVALID")
    binding.require(all(binding.filehash(ROOT / p) == h for p, h in previous["hashes_after"].items()
                        if p not in CHANGED), "PROTECTED_SOURCE_CHANGED")
    code_paths = ("tools/_s2nf_private_run_sources.py", "tools/_s2nf_private_run.py", VERIFIER,
                  "tools/_s2nf_private_run_evaluation.py", TEST, CALLER)
    trees = {p: ast.parse((ROOT / p).read_text(encoding="utf-8")) for p in code_paths}
    methods = [n.name for n in ast.walk(trees[TEST]) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    binding.require(len(methods) == len(set(methods)) == 24, "TEST_INVENTORY_INVALID")
    binding.require(all(any(n.startswith(prefix) for n in methods) for prefix in
                        ("test_06a_", "test_06b_", "test_06c_", "test_06d_")), "INDEPENDENT_CONTROLS_MISSING")
    gate = [ast.literal_eval(n.value) for n in trees[code_paths[1]].body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "MAIN_GATE" for t in n.targets)]
    binding.require(gate == [False], "MAIN_GATE_NOT_CLOSED")
    for path in (VERIFIER, code_paths[3], TEST):
        calls = {getattr(n.func, "attr", getattr(n.func, "id", "")) for n in ast.walk(trees[path]) if isinstance(n, ast.Call)}
        forbidden = {"analyze", "pcm_payload", "generate_digest", "chirp_functions", "_visual_image"}
        if path != TEST:
            forbidden |= {"advance_s2jv_atomic", "retrieve", "direct_retrieve", "run_main_once"}
        binding.require(not calls & forbidden, "EXECUTION_BOUNDARY_INVALID")
    paths = set(binding.watched()) | set(previous["hashes_after"]) | set(code_paths)
    paths |= {p.relative_to(ROOT).as_posix() for p in PREVIOUS.iterdir() if p.is_file()}
    before = {p: binding.filehash(ROOT / p) for p in sorted(paths)}
    command = [sys.executable, "-m", "unittest", MODULE, "-v"]
    binding.publish(OUT / "preregistration.json", dict(qualification_id=QUALIFICATION_ID,
        command=command, cwd=str(ROOT), test_ids=[MODULE + ".RunQualification." + n for n in sorted(methods)],
        expected_tests=24, unittest_call_limit=1, retry=False, source_hashes_before=before,
        python=sys.version, interpreter_sha256=binding.filehash(Path(sys.executable)),
        allowed_source_changes=sorted(CHANGED), protected_previous_qualification=PREVIOUS.name,
        neutral_limits=dict(formations=2, events_per_recording=6, arm_attempts_max=31,
            nf_source_generations=0, receptor_calls=0, main_history_calls=0, field_calls=0, runtime_calls=0),
        future_main_limits=dict(formations=3, cues=10, events=13, arms=40, slot_visits=800,
            band_differences=19200, equality_comparisons=1920, retrieval_comparisons=21120,
            recording_bytes=4194304, arm_bytes_exclusive=32768),
        main_gate=False, static_preflight=dict(unique_tests=True, syntax=True, verifier_without_execution=True)))
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "S2NF_QUALIFICATION_ARTIFACTS": str(OUT)}
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, check=False)
    for name, data in (("stdout.txt", result.stdout), ("stderr.txt", result.stderr)):
        with (OUT / name).open("xb") as handle:
            handle.write(data)
    after = {p: binding.filehash(ROOT / p) for p in sorted(paths)}
    stdout, stderr = result.stdout.decode("utf-8"), result.stderr.decode("utf-8")
    lines = [line.split("=", 1)[1] for line in stdout.splitlines() if line.startswith("S2NF_NEUTRAL_METRICS=")]
    metrics = json.loads(lines[0]) if len(lines) == 1 else None
    passed = (result.returncode == 0 and "Ran 24 tests" in stderr and stderr.rstrip().endswith("OK")
        and before == after and metrics is not None and metrics["main_gate"] is False
        and metrics["technical_status"] == metrics["verification_status"] == "RECORDING_COMPLETE")
    report = binding.sealed(dict(qualification_id=QUALIFICATION_ID,
        status="S2NF_RUN_BINDING_QUALIFIED" if passed else "NOT_QUALIFIED", exit_code=result.returncode,
        unittest_calls=1, tests=24, hashes_before=before, hashes_after=after,
        evidence_hashes={p.name: binding.filehash(p) for p in OUT.iterdir() if p.is_file()},
        metrics=metrics, main_gate=False), "result_digest")
    binding.publish(OUT / "result.json", report)
    print(json.dumps({k: report[k] for k in ("qualification_id", "status", "exit_code", "result_digest", "metrics")}))
    print(stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
