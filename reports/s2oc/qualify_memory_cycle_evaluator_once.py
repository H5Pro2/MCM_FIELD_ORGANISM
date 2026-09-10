"""One synthetic evaluator qualification; no caller data or system execution."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "reports/s2oc/memory-cycle-input-binding"
QUAL = ROOT / "reports/s2oc/s2oc-admission-qualification-20260910-01"
ID = "s2oc-memory-cycle-evaluation-qualification-20260910-01"
OUT = ROOT / "reports/s2oc" / ID
CODE = ("tools/_s2oc_memory_cycle_evaluation.py", "tests/test_s2oc_memory_cycle_evaluation.py",
        "reports/s2oc/qualify_memory_cycle_evaluator_once.py", "tools/_s2ob_private_state_evidence.py")
PINS = ("0def09b14294d806d68f37187001c67f827161e87d2510707946867b72abe145",
        "0bc2d62aa5b50cba15a136642478506ad537ccd2d85889af38e3b643a15f792c")


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("ascii")


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def reference(path):
    return [path.relative_to(ROOT).as_posix(), path.stat().st_size,
            hashlib.sha256(path.read_bytes()).hexdigest()]


def seal(x, key):
    return {**x, key: digest(x)}


def write(name, x):
    with (OUT / name).open("xb") as stream:
        stream.write(canonical(x))


def main():
    if OUT.exists():
        raise RuntimeError("QUALIFICATION_ID_USED")
    code = [reference(ROOT / p) for p in CODE]
    if [r[2] for r in code[:2]] != list(PINS) or code[0][1] != 5313:
        raise RuntimeError("PREPARED_CODE_CHANGED")
    tests = sorted(n.name for n in ast.walk(ast.parse((ROOT / CODE[1]).read_text()))
                   if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    if len(tests) != 15:
        raise RuntimeError("TEST_INVENTORY_CHANGED")
    budget = json.loads((INPUT / "budget.json").read_bytes())
    # All existing input bindings are counted once, including their short report.
    meta = [reference(p) for p in sorted(INPUT.iterdir()) if p.is_file()]
    meta += [reference(QUAL / "admission/admission.json"), reference(QUAL / "result.json")]
    source = [reference(ROOT / x["path"]) for x in budget["source_class_contributions"]] + code
    preparation = reference(ROOT / "reports/s2oc/memory-cycle-evaluation-preparation/syntax-preparation.txt")
    if len({x[0] for x in source + meta}) != len(source + meta):
        raise RuntimeError("DUPLICATE_REFERENCE")
    meta_bytes = sum(x[1] for x in meta)
    source_bytes = sum(x[1] for x in source)
    caps = dict(addendum=1400, result=1200, preregistration=4608, log=8192, balance=4096, report=512)
    future_meta = dict(existing=meta_bytes, addendum=caps["addendum"], qualification=caps["result"],
        runtime_session_error=24104, evaluation=3000, dispatch=768, final_balance=1536, final_report=512)
    native = budget["native_caps"]
    future = dict(metadata=sum(future_meta.values()), sources=source_bytes,
        shared=source_bytes+sum(native[k] for k in ("nj", "formations", "generations")),
        total=sum(native.values())+source_bytes+sum(future_meta.values())+262144)
    qmeta = meta_bytes + sum(caps.values()) + preparation[1]
    qtotal = qmeta + source_bytes
    addendum = seal(dict(version="s2oc.memory-cycle-evaluator.v1", qualification_id=ID,
        historical_budget_digest=budget["budget_digest"], code=code,
        test_inventory_digest=digest(tests), code_reserve_before=4096, code_reserve_now=5313,
        future_metadata=future_meta, future_totals=future, main_authorized=False), "addendum_digest")
    prereg = seal(dict(run_id=ID, tests=tests, references=meta+source, reserves=caps,
        syntax_preparation=preparation, prior_test_calls=0,
        qualification_metadata_max=qmeta, qualification_total_max=qtotal,
        addendum_digest=addendum["addendum_digest"], test_calls=1, retry=False,
        command=[sys.executable, "-m", "unittest", "-v", "tests.test_s2oc_memory_cycle_evaluation"],
        boundary="Synthetic assessment inputs only. No native technical verifier is rerun; proof digests are neutral fixtures, not simulated memory validity. No real source reads or system calls.",
        archive="This preregistration, full log, balance and qualification report are counted here. Future active dependencies are all code references, unchanged input bindings, admission, its result, new addendum and new result. The new result pins archived log/preregistration without requiring their replay."), "preregistration_digest")
    violations = []
    for k, limit in (("metadata", 65536), ("sources", 174080), ("shared", 262144), ("total", 4194304)):
        if future[k] > limit:
            violations.append(["future_"+k, future[k], limit])
    if qmeta > 65536 or qtotal > 4194304:
        violations.append(["qualification", qmeta, qtotal])
    for name, value in (("addendum", addendum), ("preregistration", prereg)):
        if len(canonical(value)) > caps[name]:
            violations.append([name, len(canonical(value)), caps[name]])
    print(json.dumps(dict(phase="PRE_TEST", test_calls=0, future=future,
        qualification_metadata=qmeta, qualification_total=qtotal,
        addendum_bytes=len(canonical(addendum)), preregistration_bytes=len(canonical(prereg)),
        contributions=dict(metadata=meta, sources=source), violations=violations)), flush=True)
    if violations:
        return 2
    OUT.mkdir()
    write("addendum.json", addendum)
    write("preregistration.json", prereg)
    proc = subprocess.run([sys.executable, "-m", "unittest", "-v", "tests.test_s2oc_memory_cycle_evaluation"],
        cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, check=False)
    log = proc.stdout + proc.stderr
    with (OUT / "full-log.txt").open("xb") as stream:
        stream.write(log)
    unchanged = code == [reference(ROOT / p) for p in CODE] and all(reference(ROOT / p) == [p, n, h] for p, n, h in meta+source)
    text = log.decode("utf-8", errors="replace")
    passed = proc.returncode == 0 and "Ran 15 tests" in text and text.rstrip().endswith("OK") and unchanged and len(log) <= caps["log"]
    result = seal(dict(run_id=ID, status="QUALIFIED" if passed else "NOT_QUALIFIED", test_calls=1,
        expected_tests=15, passed_tests=15 if passed else None, exit_code=proc.returncode,
        code_digest=digest(code), test_inventory_digest=digest(tests), hashes_unchanged=unchanged,
        addendum_digest=addendum["addendum_digest"], log_sha256=hashlib.sha256(log).hexdigest(),
        preregistration_digest=prereg["preregistration_digest"], gates=False,
        boundary="Assessment only; no source, receptor, memory, field or runtime execution."), "result_digest")
    write("result.json", result)
    files = [reference(p) for p in sorted(OUT.iterdir())]
    measured_meta = meta_bytes + sum(x[1] for x in files) + preparation[1]
    ledger = dict(files=files, references=meta+source+[preparation], actual_metadata_before_balance_report=measured_meta,
        source_bytes=source_bytes, remaining_balance_report=caps["balance"]+caps["report"],
        metadata_with_reserves=qmeta, total_with_reserves=qtotal, future=future,
        violations=[] if len(canonical(result)) <= caps["result"] and len(log) <= caps["log"] else ["QUALIFICATION_ARTIFACT_LIMIT"],
        full_log_retained=True, test_calls=1)
    if len(canonical(ledger)) > caps["balance"]:
        ledger["violations"].append("BALANCE_LIMIT")
    write("final-balance.json", ledger)
    print(json.dumps(dict(status=result["status"], exit_code=proc.returncode,
        result_bytes=len(canonical(result)), log_bytes=len(log), ledger_bytes=len(canonical(ledger)),
        hashes_unchanged=unchanged, violations=ledger["violations"])), flush=True)
    return 0 if passed and not ledger["violations"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
