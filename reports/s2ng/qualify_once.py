"""One prebounded neutral NG qualification. Never execute the MT corpus."""

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
ID = "s2ng-private-runtime-composition-qualification-20260906-01"
OUT = ROOT/"reports/s2ng"/ID
TEST = "tests/test_s2ng_private_runtime_comparison.py"
MODULE = "tests.test_s2ng_private_runtime_comparison"
PRODUCTS = ("tools/_s2ng_private_runtime_comparison.py", "tools/_s2ng_private_comparison_verification.py",
            "tools/_s2ng_private_comparison_evaluation.py")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(name, value):
    data = json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("ascii")
    with (OUT/name).open("xb") as handle:
        handle.write(data)


def main():
    if Path.cwd().resolve() != ROOT:
        raise ValueError("WORKSPACE_INVALID")
    OUT.mkdir(exist_ok=False)
    paths = (*PRODUCTS, TEST, "reports/s2ng/qualify_once.py")
    trees = {p: ast.parse((ROOT/p).read_text(encoding="utf-8")) for p in paths}
    tests = sorted(n.name for n in ast.walk(trees[TEST]) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    if len(tests) != 22 or len(set(tests)) != 22:
        raise ValueError("TEST_INVENTORY_INVALID")
    gate = [ast.literal_eval(n.value) for n in trees[PRODUCTS[0]].body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "MAIN_GATE" for t in n.targets)]
    if gate != [False]:
        raise ValueError("MAIN_GATE_INVALID")
    for p in (*PRODUCTS, TEST):
        calls = {getattr(n.func, "attr", getattr(n.func, "id", "")) for n in ast.walk(trees[p]) if isinstance(n, ast.Call)}
        forbidden = {"analyze", "pcm_payload", "_materialize_events", "run_main_once"}
        if p in PRODUCTS[1:]:
            forbidden |= {"process_once", "advance_s2jv_atomic", "retrieve", "direct_retrieve", "advance_neutral_fast_shared_field_transient"}
        if calls & forbidden:
            raise ValueError("EXECUTION_BOUNDARY_INVALID")
    from tools import _s2ng_private_runtime_comparison as run
    watched = set(run.SOURCE_PATHS) | set(paths) | {"reports/s2ng/KOMPOSITIONSBINDUNG.md"}
    watched |= {p.relative_to(ROOT).as_posix() for p in (ROOT/"reports/s2nf").rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    before = {p: sha(ROOT/p) for p in sorted(watched)}
    command = [sys.executable, "-m", "unittest", MODULE, "-v"]
    types = ("COMPLETE_AV_PERCEPTION",)*20+("PARTIAL_AUDITORY_CUE",)*4+("PARTIAL_VISUAL_CUE",)*4
    write("preregistration.json", dict(qualification_id=ID, expected_tests=22, unittest_call_limit=1, retry=False,
        test_ids=[MODULE+".CompositionQualification."+n for n in tests], command=command, cwd=str(ROOT),
        python=sys.version, interpreter_sha256=sha(Path(sys.executable)), source_hashes_before=before,
        static_codecheck=dict(syntax=True, unique_inventory=True, main_gate=False, excluded_calls_absent=True),
        neutral_limits=dict(source_generations=0, receptor_calls=0, main_history_calls=0,
            formations=4, successful_runtime_events=12, closed_runtime_rejection_attempts=2,
            field_contacts=2208, auditory_scan_receipts=14, visual_scan_receipts=4, failed_scan_attempts=4,
            whole_record_verification_calls=11, formation_l1_limit=14208,
            successful_scan_value_comparisons_max=10592), future_limits=run.budget(types)))
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "S2NG_QUALIFICATION_ARTIFACTS": str(OUT)}
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, check=False)
    for name, data in (("stdout.txt", result.stdout), ("stderr.txt", result.stderr)):
        with (OUT/name).open("xb") as handle:
            handle.write(data)
    after = {p: sha(ROOT/p) for p in sorted(watched)}
    stdout, stderr = result.stdout.decode("utf-8"), result.stderr.decode("utf-8")
    lines = [s.split("=", 1)[1] for s in stdout.splitlines() if s.startswith("S2NG_NEUTRAL_METRICS=")]
    metrics = json.loads(lines[0]) if len(lines) == 1 else None
    passed = result.returncode == 0 and "Ran 22 tests" in stderr and stderr.rstrip().endswith("OK") and before == after
    passed = passed and metrics is not None and metrics["proof"]["status"] == "RECORDING_COMPLETE" and not run.MAIN_GATE
    report = dict(qualification_id=ID, status="S2NG_COMPOSITION_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=result.returncode, unittest_calls=1, expected_tests=22, hashes_before=before, hashes_after=after,
        hashes_unchanged=before == after, evidence_hashes={p.name: sha(p) for p in OUT.iterdir() if p.is_file()},
        metrics=metrics, main_gate=run.MAIN_GATE)
    report["result_digest"] = run.digest(report)
    write("result.json", report)
    print(json.dumps({k: report[k] for k in ("qualification_id", "status", "exit_code", "hashes_unchanged", "result_digest", "metrics")}))
    print(stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
