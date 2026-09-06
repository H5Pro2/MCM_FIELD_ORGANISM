"""One complete neutral requalification after the local NG exception mapping."""

import ast
import json
import os
from pathlib import Path
import subprocess
import sys

from reports.s2ng import qualify_once as previous_caller

ROOT = previous_caller.ROOT
ID = "s2ng-private-runtime-composition-qualification-20260906-02"
OUT = ROOT/"reports/s2ng"/ID
PREVIOUS = ROOT/"reports/s2ng/s2ng-private-runtime-composition-qualification-20260906-01"
TEST, MODULE, PRODUCTS = previous_caller.TEST, previous_caller.MODULE, previous_caller.PRODUCTS
CALLER = "reports/s2ng/qualify_state_binding_once.py"
CHANGED = {PRODUCTS[1], TEST}
sha = previous_caller.sha


def write(name, value):
    data = json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("ascii")
    with (OUT/name).open("xb") as handle:
        handle.write(data)


def main():
    if Path.cwd().resolve() != ROOT:
        raise ValueError("WORKSPACE_INVALID")
    OUT.mkdir(exist_ok=False)
    previous = json.loads((PREVIOUS/"result.json").read_bytes())
    preregistered = json.loads((PREVIOUS/"preregistration.json").read_bytes())
    if previous["status"] != "NOT_QUALIFIED" or any(sha(ROOT/p) != h for p, h in previous["hashes_after"].items() if p not in CHANGED):
        raise ValueError("PROTECTED_SOURCE_CHANGED")
    paths = (*PRODUCTS, TEST, CALLER)
    trees = {p: ast.parse((ROOT/p).read_text(encoding="utf-8")) for p in paths}
    tests = sorted(n.name for n in ast.walk(trees[TEST]) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    ids = [MODULE+".CompositionQualification."+n for n in tests]
    if len(tests) != 23 or len(set(tests)) != 23 or ids[:22] != preregistered["test_ids"]:
        raise ValueError("TEST_INVENTORY_INVALID")
    tree = trees[PRODUCTS[1]]
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_verify_record")
    guard = [n for n in function.body if isinstance(n, ast.Try) and any(
        isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == "decode_state"
        for statement in n.body for c in ast.walk(statement))]
    if len(guard) != 1 or len(guard[0].handlers) != 1 or ast.unparse(guard[0].handlers[0].type) != "run.memory.S2JWCoordinatorError":
        raise ValueError("LOCAL_TYPED_GUARD_INVALID")
    handler = guard[0].handlers[0]
    if len(handler.body) != 1 or not isinstance(handler.body[0], ast.Raise) or ast.unparse(handler.body[0].cause) != handler.name:
        raise ValueError("EXPLICIT_EXCEPTION_CHAIN_MISSING")
    gate = [ast.literal_eval(n.value) for n in trees[PRODUCTS[0]].body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "MAIN_GATE" for t in n.targets)]
    if gate != [False]:
        raise ValueError("MAIN_GATE_INVALID")
    from tools import _s2ng_private_runtime_comparison as run
    watched = set(previous["hashes_after"]) | set(run.SOURCE_PATHS) | set(paths)
    watched |= {p.relative_to(ROOT).as_posix() for p in PREVIOUS.iterdir() if p.is_file()}
    before = {p: sha(ROOT/p) for p in sorted(watched)}
    command = [sys.executable, "-m", "unittest", MODULE, "-v"]
    limits = {**preregistered["neutral_limits"], "whole_record_verification_calls": 14}
    write("preregistration.json", dict(qualification_id=ID, expected_tests=23, unittest_call_limit=1, retry=False,
        test_ids=ids, command=command, cwd=str(ROOT), python=sys.version,
        interpreter_sha256=sha(Path(sys.executable)), source_hashes_before=before,
        allowed_source_changes=sorted(CHANGED), protected_previous_qualification=PREVIOUS.name,
        neutral_limits=limits, future_limits=preregistered["future_limits"],
        added_checks="valid state; explicit coordinator cause and reason; unchanged NG error",
        static_codecheck=dict(syntax=True, unchanged_22_test_ids=True, local_typed_guard=True,
                              explicit_exception_chain=True, protected_sources_unchanged=True, main_gate=False)))
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "S2NG_QUALIFICATION_ARTIFACTS": str(OUT)}
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, check=False)
    for name, data in (("stdout.txt", result.stdout), ("stderr.txt", result.stderr)):
        with (OUT/name).open("xb") as handle:
            handle.write(data)
    after = {p: sha(ROOT/p) for p in sorted(watched)}
    stdout, stderr = result.stdout.decode("utf-8"), result.stderr.decode("utf-8")
    lines = [s.split("=", 1)[1] for s in stdout.splitlines() if s.startswith("S2NG_NEUTRAL_METRICS=")]
    metrics = json.loads(lines[0]) if len(lines) == 1 else None
    passed = result.returncode == 0 and "Ran 23 tests" in stderr and stderr.rstrip().endswith("OK") and before == after
    passed = passed and metrics is not None and metrics["proof"]["status"] == "RECORDING_COMPLETE" and not run.MAIN_GATE
    passed = passed and metrics.get("state_binding_regression", {}).get("explicit_chain") is True
    report = dict(qualification_id=ID, status="S2NG_COMPOSITION_QUALIFIED" if passed else "NOT_QUALIFIED",
        exit_code=result.returncode, unittest_calls=1, expected_tests=23, hashes_before=before, hashes_after=after,
        hashes_unchanged=before == after, evidence_hashes={p.name: sha(p) for p in OUT.iterdir() if p.is_file()},
        metrics=metrics, main_gate=run.MAIN_GATE)
    report["result_digest"] = run.digest(report)
    write("result.json", report)
    print(json.dumps({k: report[k] for k in ("qualification_id", "status", "exit_code", "hashes_unchanged", "result_digest", "metrics")}))
    print(stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
